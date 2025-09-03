from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from functools import cached_property
from pydantic import BaseModel, Field, model_validator
from typing import Self
from maleo.types.base.string import OptionalString


class Size(BaseModel):
    size: int = Field(
        2048, ge=2048, le=8192, multiple_of=1024, description="Key's size"
    )


class Password(BaseModel):
    password: str = Field(..., description="Key's password")


class OptionalPassword(BaseModel):
    password: OptionalString = Field(None, description="Key's password")


class Private(OptionalPassword):
    private: str = Field(..., description="Private key in str format.")

    def _validate_private_key(self) -> None:
        """Internal validation logic"""
        if not RSA.import_key(
            extern_key=self.private, passphrase=self.password
        ).has_private():
            raise ValueError(
                "Invalid key type, the private key did not have private inside it"
            )

    @model_validator(mode="after")
    def validate_private(self) -> Self:
        self._validate_private_key()
        return self

    @cached_property
    def private_rsa_key(self) -> RSA.RsaKey:
        self._validate_private_key()
        private = RSA.import_key(extern_key=self.private, passphrase=self.password)
        return private


class Public(BaseModel):
    public: str = Field(..., description="Public key in str format.")

    def _validate_public_key(self) -> None:
        """Internal validation logic"""
        if RSA.import_key(extern_key=self.public).has_private():
            raise ValueError("Invalid key type, the public key had private inside it")

    @model_validator(mode="after")
    def validate_public(self) -> Self:
        self._validate_public_key()
        return self

    @cached_property
    def public_rsa_key(self) -> RSA.RsaKey:
        public = RSA.import_key(extern_key=self.public)
        return public


class Complete(Public, Private):
    @model_validator(mode="after")
    def validate_complete_keys(self) -> Self:
        try:
            # Import private key with password
            private_key = self.private_rsa_key

            # Import public key
            public_key = self.public_rsa_key

            # Validate keys match by comparing public components
            if (
                private_key.publickey().n != public_key.n
                or private_key.publickey().e != public_key.e
            ):
                raise ValueError("Public key does not match the private key")

            # Optional: Test encrypt/decrypt functionality
            test_message = b"validation_test"
            try:
                # Encrypt with public key
                cipher = PKCS1_OAEP.new(public_key)
                encrypted = cipher.encrypt(test_message)

                # Decrypt with private key
                cipher = PKCS1_OAEP.new(private_key)
                decrypted = cipher.decrypt(encrypted)

                if decrypted != test_message:
                    raise ValueError(
                        "Keys do not work together for encryption/decryption"
                    )

            except Exception as e:
                raise ValueError(f"Keys failed encryption/decryption test: {str(e)}")

        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise ValueError(f"Key validation failed: {str(e)}")

        return self
