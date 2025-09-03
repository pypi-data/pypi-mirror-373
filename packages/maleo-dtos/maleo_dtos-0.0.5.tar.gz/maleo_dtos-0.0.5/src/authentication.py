from functools import cached_property
from fastapi import Request
from pydantic import BaseModel, Field
from starlette.authentication import AuthCredentials, BaseUser
from starlette.exceptions import HTTPException
from typing import Generic, Literal, Optional, TypeVar
from maleo.types.base.string import SequenceOfStrings, OptionalSequenceOfStrings
from .token import (
    PayloadT,
    GeneralPayload,
    BasicPayload,
    PrivilegedPayload,
    GenericAuthenticationToken,
    GeneralAuthenticationToken,
)


# ----- CREDENTIALS -----
class RequestCredentials(AuthCredentials):
    def __init__(
        self,
        token: Optional[GeneralAuthenticationToken] = None,
        scopes: OptionalSequenceOfStrings = None,
    ) -> None:
        self._token = token
        super().__init__(scopes)

    @property
    def token(self) -> Optional[GeneralAuthenticationToken]:
        return self._token


TokenT = TypeVar("TokenT", bound=Optional[GenericAuthenticationToken])
ScopesT = TypeVar("ScopesT", bound=OptionalSequenceOfStrings)


class GenericCredentials(
    BaseModel,
    Generic[
        TokenT,
        ScopesT,
    ],
):
    token: TokenT = Field(..., description="Token")
    scopes: ScopesT = Field(..., description="Scopes")


CredentialsT = TypeVar("CredentialsT", bound=GenericCredentials)


class OptionalCredentials(
    GenericCredentials[
        Optional[GenericAuthenticationToken[GeneralPayload]], OptionalSequenceOfStrings
    ],
):
    token: Optional[GenericAuthenticationToken[GeneralPayload]] = Field(
        None, description="Token"
    )
    scopes: OptionalSequenceOfStrings = Field(None, description="Scopes")


class MandatoryCredentials(
    GenericCredentials[GenericAuthenticationToken[PayloadT], SequenceOfStrings],
    Generic[PayloadT],
):
    scopes: SequenceOfStrings = Field(..., min_length=1, description="Scopes")


class GeneralCredentials(MandatoryCredentials[GeneralPayload]):
    pass


class BasicCredentials(MandatoryCredentials[BasicPayload]):
    pass


class PrivilegedCredentials(MandatoryCredentials[PrivilegedPayload]):
    pass


# ----- USER -----
class RequestUser(BaseUser):
    def __init__(
        self, authenticated: bool = False, username: str = "", email: str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email


IsAuthenticatedT = TypeVar("IsAuthenticatedT", bound=bool)


class GenericUser(BaseModel, Generic[IsAuthenticatedT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


UserT = TypeVar("UserT", bound=GenericUser)


class GeneralUser(GenericUser[bool]):
    is_authenticated: bool = Field(..., description="Authenticated")


class AuthenticatedUser(GenericUser[Literal[True]]):
    is_authenticated: Literal[True] = True


# ----- AUTHENTICATION -----
class GenericAuthentication(
    BaseModel,
    Generic[CredentialsT, UserT],
):
    credentials: CredentialsT = Field(..., description="Credentials")
    user: UserT = Field(..., description="User")

    @classmethod
    def _validate_request_credentials(cls, request: Request):
        if not isinstance(request.auth, RequestCredentials):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's credentials: '{type(request.auth)}'",
            )

    @classmethod
    def _validate_request_user(cls, request: Request):
        if not isinstance(request.user, RequestUser):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid type of request's user: '{type(request.user)}'",
            )

    @classmethod
    def from_request(
        cls,
        request: Request,
        credentials_type: type[CredentialsT],
        user_type: type[UserT],
    ) -> "GenericAuthentication[CredentialsT, UserT]":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = credentials_type.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = user_type.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unable to validate General Authentication: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(
        cls, credentials_type: type[CredentialsT], user_type: type[UserT]
    ):
        """Create a FastAPI dependency for this authentication."""

        def dependency(
            request: Request,
        ) -> "GenericAuthentication[CredentialsT, UserT]":
            return cls.from_request(request, credentials_type, user_type)

        return dependency


AuthenticationT = TypeVar("AuthenticationT", bound=Optional[GenericAuthentication])


class OptionalAuthentication(
    GenericAuthentication[OptionalCredentials, GeneralUser],
):
    @classmethod
    def from_request(
        cls,
        request: Request,
        credentials_type: type[OptionalCredentials] = OptionalCredentials,
        user_type: type[GeneralUser] = GeneralUser,
    ) -> "OptionalAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = OptionalCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = GeneralUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unable to validate Optional Authentication: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(
        cls,
        credentials_type: type[OptionalCredentials] = OptionalCredentials,
        user_type: type[GeneralUser] = GeneralUser,
    ):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "OptionalAuthentication":
            return cls.from_request(request)

        return dependency


class GeneralAuthentication(
    GenericAuthentication[
        GeneralCredentials,
        AuthenticatedUser,
    ]
):
    @classmethod
    def from_request(
        cls,
        request: Request,
        credentials_type: type[GeneralCredentials] = GeneralCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ) -> "GeneralAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = GeneralCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = AuthenticatedUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unable to validate General Authentication: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(
        cls,
        credentials_type: type[GeneralCredentials] = GeneralCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "GeneralAuthentication":
            return cls.from_request(request)

        return dependency

    @cached_property
    def to_optional(self) -> OptionalAuthentication:
        return OptionalAuthentication.model_validate(self.model_dump())


class BasicAuthentication(
    GenericAuthentication[
        BasicCredentials,
        AuthenticatedUser,
    ]
):
    @classmethod
    def from_request(
        cls,
        request: Request,
        credentials_type: type[BasicCredentials] = BasicCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ) -> "BasicAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = BasicCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = AuthenticatedUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unable to validate Basic Authentication: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(
        cls,
        credentials_type: type[BasicCredentials] = BasicCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "BasicAuthentication":
            return cls.from_request(request)

        return dependency

    @cached_property
    def to_optional(self) -> OptionalAuthentication:
        return OptionalAuthentication.model_validate(self.model_dump())

    @cached_property
    def to_general(self) -> GeneralAuthentication:
        return GeneralAuthentication.model_validate(self.model_dump())


class PrivilegedAuthentication(
    GenericAuthentication[
        PrivilegedCredentials,
        AuthenticatedUser,
    ]
):
    @classmethod
    def from_request(
        cls,
        request: Request,
        credentials_type: type[PrivilegedCredentials] = PrivilegedCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ) -> "PrivilegedAuthentication":
        try:
            # validate credentials
            cls._validate_request_credentials(request=request)
            credentials = PrivilegedCredentials.model_validate(
                request.auth, from_attributes=True
            )

            # validate user
            cls._validate_request_user(request=request)
            user = AuthenticatedUser.model_validate(request.user, from_attributes=True)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Unable to validate Privileged Authentication: '{str(e)}'",
            )

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(
        cls,
        credentials_type: type[PrivilegedCredentials] = PrivilegedCredentials,
        user_type: type[AuthenticatedUser] = AuthenticatedUser,
    ):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "PrivilegedAuthentication":
            return cls.from_request(request)

        return dependency

    @cached_property
    def to_optional(self) -> OptionalAuthentication:
        return OptionalAuthentication.model_validate(self.model_dump())

    @cached_property
    def to_general(self) -> GeneralAuthentication:
        return GeneralAuthentication.model_validate(self.model_dump())


class AuthenticationMixin(BaseModel, Generic[AuthenticationT]):
    authentication: AuthenticationT = Field(
        ...,
        description="Authentication",
    )
