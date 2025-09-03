from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from typing import Generic, Literal, Optional, TypeVar, Union, overload
from uuid import UUID
from maleo.enums.expiration import Expiration
from maleo.enums.token import TokenType
from maleo.enums.privilege import Level
from maleo.types.base.datetime import OptionalDatetime
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import ListOfStrings, OptionalListOfStrings, OptionalString
from maleo.types.base.uuid import OptionalUUID


SystemRoleT = TypeVar(
    "SystemRoleT", Union[ListOfStrings, Literal["user"]], ListOfStrings, Literal["user"]
)
OrganizationIdT = TypeVar("OrganizationIdT", OptionalInteger, None, int)
OrganizationUuidT = TypeVar("OrganizationUuidT", OptionalUUID, None, UUID)
OrganizationKeyT = TypeVar("OrganizationKeyT", OptionalString, None, str)
OrganizationTypeT = TypeVar("OrganizationTypeT", OptionalString, None, str)
UserOrganizationRoleT = TypeVar(
    "UserOrganizationRoleT", OptionalListOfStrings, None, ListOfStrings
)


class GenericCredentialPayload(
    BaseModel,
    Generic[
        SystemRoleT,
        OrganizationIdT,
        OrganizationUuidT,
        OrganizationKeyT,
        OrganizationTypeT,
        UserOrganizationRoleT,
    ],
):
    iss: OptionalString = Field(None, description="Token's issuer")
    sub: str = Field(..., description="Token's subject")
    sr: SystemRoleT = Field(..., description="System role")
    u_i: int = Field(..., description="user's id")
    u_uu: UUID = Field(..., description="user's uuid")
    u_u: str = Field(..., description="user's username")
    u_e: str = Field(..., description="user's email")
    u_ut: str = Field(..., description="user's type")
    o_i: OrganizationIdT = Field(..., description="Organization's id")
    o_uu: OrganizationUuidT = Field(..., description="Organization's uuid")
    o_k: OrganizationKeyT = Field(..., description="Organization's key")
    o_ot: OrganizationTypeT = Field(..., description="Organization's type")
    uor: UserOrganizationRoleT = Field(..., description="User Organization Role")

    @classmethod
    def new_credential(
        cls,
        iss: OptionalString = None,
        *,
        sub: str,
        sr: SystemRoleT,
        u_i: int,
        u_uu: UUID,
        u_u: str,
        u_e: str,
        u_ut: str,
        o_i: OrganizationIdT,
        o_uu: OrganizationUuidT,
        o_k: OrganizationKeyT,
        o_ot: OrganizationTypeT,
        uor: UserOrganizationRoleT,
    ) -> "GenericCredentialPayload[SystemRoleT, OrganizationIdT, OrganizationUuidT, OrganizationKeyT, OrganizationTypeT, UserOrganizationRoleT]":
        """Create a credential payload with the provided values."""
        return cls(
            iss=iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )


CredentialPayloadT = TypeVar(
    "CredentialPayloadT",
    bound=GenericCredentialPayload[
        Union[ListOfStrings, Literal["user"]],
        OptionalInteger,
        OptionalUUID,
        OptionalString,
        OptionalString,
        OptionalListOfStrings,
    ],
)


class GeneralCredentialPayload(
    GenericCredentialPayload[
        Union[ListOfStrings, Literal["user"]],
        OptionalInteger,
        OptionalUUID,
        OptionalString,
        OptionalString,
        OptionalListOfStrings,
    ]
):
    sr: Union[ListOfStrings, Literal["user"]] = Field(..., description="System role")
    o_i: OptionalInteger = Field(None, description="Organization's id")
    o_uu: OptionalUUID = Field(None, description="Organization's uuid")
    o_k: OptionalString = Field(None, description="Organization's key")
    o_ot: OptionalString = Field(None, description="Organization's type")
    uor: OptionalListOfStrings = Field(None, description="User Organization Role")

    @classmethod
    def new_credential(
        cls,
        iss: OptionalString = None,
        *,
        sub: str,
        sr: Union[ListOfStrings, Literal["user"]],
        u_i: int,
        u_uu: UUID,
        u_u: str,
        u_e: str,
        u_ut: str,
        o_i: OptionalInteger = None,
        o_uu: OptionalUUID = None,
        o_k: OptionalString = None,
        o_ot: OptionalString = None,
        uor: OptionalListOfStrings = None,
    ) -> "GeneralCredentialPayload":
        """Create a credential payload with the provided values."""
        return cls(
            iss=iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )


class BasicCredentialPayload(
    GenericCredentialPayload[
        Literal["user"],
        int,
        UUID,
        str,
        str,
        ListOfStrings,
    ]
):
    sr: Literal["user"] = "user"
    o_i: int = Field(..., description="Organization's id")
    o_uu: UUID = Field(..., description="Organization's uuid")
    o_k: str = Field(..., description="Organization's key")
    o_ot: str = Field(..., description="Organization's type")
    uor: ListOfStrings = Field(..., description="User Organization Role")

    @classmethod
    def new_credential(
        cls,
        iss: OptionalString = None,
        *,
        sub: str,
        sr: Literal["user"] = "user",
        u_i: int,
        u_uu: UUID,
        u_u: str,
        u_e: str,
        u_ut: str,
        o_i: int,
        o_uu: UUID,
        o_k: str,
        o_ot: str,
        uor: ListOfStrings,
    ) -> "BasicCredentialPayload":
        return cls(
            iss=iss,
            sub=sub,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )


class PrivilegedCredentialPayload(
    GenericCredentialPayload[
        ListOfStrings,
        None,
        None,
        None,
        None,
        None,
    ]
):
    sr: ListOfStrings = Field(..., min_length=1, description="System role")
    o_i: None = None
    o_uu: None = None
    o_k: None = None
    o_ot: None = None
    uor: None = None

    @classmethod
    def new_credential(
        cls,
        iss: OptionalString = None,
        *,
        sub: str,
        sr: ListOfStrings,
        u_i: int,
        u_uu: UUID,
        u_u: str,
        u_e: str,
        u_ut: str,
        o_i: None = None,
        o_uu: None = None,
        o_k: None = None,
        o_ot: None = None,
        uor: None = None,
    ) -> "PrivilegedCredentialPayload":
        return cls(
            iss=iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
        )


@overload
def generate_credential_payload(
    privilege: Literal[None] = None,
    iss: OptionalString = None,
    *,
    sub: str,
    sr: SystemRoleT,
    u_i: int,
    u_uu: UUID,
    u_u: str,
    u_e: str,
    u_ut: str,
    o_i: OrganizationIdT = None,
    o_uu: OrganizationUuidT = None,
    o_k: OrganizationKeyT = None,
    o_ot: OrganizationTypeT = None,
    uor: UserOrganizationRoleT = None,
) -> GenericCredentialPayload[
    SystemRoleT,
    OrganizationIdT,
    OrganizationUuidT,
    OrganizationKeyT,
    OrganizationTypeT,
    UserOrganizationRoleT,
]: ...
@overload
def generate_credential_payload(
    privilege: Literal[Level.GENERAL],
    iss: OptionalString = None,
    *,
    sub: str,
    sr: Union[ListOfStrings, Literal["user"]],
    u_i: int,
    u_uu: UUID,
    u_u: str,
    u_e: str,
    u_ut: str,
    o_i: OptionalInteger = None,
    o_uu: OptionalUUID = None,
    o_k: OptionalString = None,
    o_ot: OptionalString = None,
    uor: OptionalListOfStrings = None,
) -> GeneralCredentialPayload: ...
@overload
def generate_credential_payload(
    privilege: Literal[Level.BASIC],
    iss: OptionalString = None,
    *,
    sub: str,
    sr: Literal["user"],
    u_i: int,
    u_uu: UUID,
    u_u: str,
    u_e: str,
    u_ut: str,
    o_i: int,
    o_uu: UUID,
    o_k: str,
    o_ot: str,
    uor: ListOfStrings,
) -> BasicCredentialPayload: ...
@overload
def generate_credential_payload(
    privilege: Literal[Level.PRIVILEGED],
    iss: OptionalString = None,
    *,
    sub: str,
    sr: ListOfStrings,
    u_i: int,
    u_uu: UUID,
    u_u: str,
    u_e: str,
    u_ut: str,
) -> PrivilegedCredentialPayload: ...
def generate_credential_payload(
    privilege: Optional[Level] = None,
    iss: OptionalString = None,
    *,
    sub: str,
    sr: SystemRoleT,
    u_i: int,
    u_uu: UUID,
    u_u: str,
    u_e: str,
    u_ut: str,
    o_i: OrganizationIdT = None,
    o_uu: OrganizationUuidT = None,
    o_k: OrganizationKeyT = None,
    o_ot: OrganizationTypeT = None,
    uor: UserOrganizationRoleT = None,
) -> Union[
    GenericCredentialPayload[
        SystemRoleT,
        OrganizationIdT,
        OrganizationUuidT,
        OrganizationKeyT,
        OrganizationTypeT,
        UserOrganizationRoleT,
    ],
    GeneralCredentialPayload,
    BasicCredentialPayload,
    PrivilegedCredentialPayload,
]:
    if privilege is None:
        return GenericCredentialPayload[
            SystemRoleT,
            OrganizationIdT,
            OrganizationUuidT,
            OrganizationKeyT,
            OrganizationTypeT,
            UserOrganizationRoleT,
        ].new_credential(
            iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )

    if privilege is Level.GENERAL:
        return GeneralCredentialPayload.new_credential(
            iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )
    elif privilege is Level.BASIC:
        if isinstance(sr, list) or sr != "user":
            raise ValueError("System roles is not 'user'")
        if not isinstance(o_i, int):
            raise TypeError(f"Invalid type of Organization's ID: {type(o_i)}")
        if not isinstance(o_uu, UUID):
            raise TypeError(f"Invalid type of Organization's UUID: {type(o_uu)}")
        if not isinstance(o_k, int):
            raise TypeError(f"Invalid type of Organization's Key: {type(o_k)}")
        if not isinstance(o_ot, int):
            raise TypeError(f"Invalid type of Organization's Type: {type(o_ot)}")
        if not isinstance(uor, list):
            raise TypeError(f"Invalid type of User's Organization Role: {type(uor)}")
        return BasicCredentialPayload.new_credential(
            iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
            o_i=o_i,
            o_uu=o_uu,
            o_k=o_k,
            o_ot=o_ot,
            uor=uor,
        )
    elif privilege is Level.PRIVILEGED:
        if not isinstance(sr, list):
            raise ValueError("System roles is not a list")
        return PrivilegedCredentialPayload.new_credential(
            iss,
            sub=sub,
            sr=sr,
            u_i=u_i,
            u_uu=u_uu,
            u_u=u_u,
            u_e=u_e,
            u_ut=u_ut,
        )


class TimestampPayload(BaseModel):
    iat_dt: datetime = Field(..., description="Issued at (datetime)")
    iat: int = Field(..., description="Issued at (integer)")
    exp_dt: datetime = Field(..., description="Expired at (datetime)")
    exp: int = Field(..., description="Expired at (integer)")

    @classmethod
    def new_timestamp(
        cls, iat_dt: OptionalDatetime = None, exp_in: Expiration = Expiration.EXP_15MN
    ) -> "TimestampPayload":
        if iat_dt is None:
            iat_dt = datetime.now(tz=timezone.utc)
        exp_dt = iat_dt + timedelta(seconds=exp_in.value)
        return cls(
            iat_dt=iat_dt,
            iat=int(iat_dt.timestamp()),
            exp_dt=exp_dt,
            exp=int(exp_dt.timestamp()),
        )


class GenericPayload(
    TimestampPayload,
    GenericCredentialPayload[
        SystemRoleT,
        OrganizationIdT,
        OrganizationUuidT,
        OrganizationKeyT,
        OrganizationTypeT,
        UserOrganizationRoleT,
    ],
    Generic[
        SystemRoleT,
        OrganizationIdT,
        OrganizationUuidT,
        OrganizationKeyT,
        OrganizationTypeT,
        UserOrganizationRoleT,
    ],
):
    pass


PayloadT = TypeVar("PayloadT", bound=GenericPayload)


class GeneralPayload(
    GenericPayload[
        Union[ListOfStrings, Literal["user"]],
        OptionalInteger,
        OptionalUUID,
        OptionalString,
        OptionalString,
        OptionalListOfStrings,
    ]
):
    pass


class BasicPayload(
    GenericPayload[
        Literal["user"],
        int,
        UUID,
        str,
        str,
        ListOfStrings,
    ]
):
    pass


class PrivilegedPayload(
    GenericPayload[
        ListOfStrings,
        None,
        None,
        None,
        None,
        None,
    ]
):
    pass


class GenericAuthenticationToken(BaseModel, Generic[PayloadT]):
    type: TokenType = Field(..., description="Token's type")
    payload: PayloadT = Field(..., description="Token's payload")


class GeneralAuthenticationToken(GenericAuthenticationToken[GeneralPayload]):
    pass


class BasicAuthenticationToken(GenericAuthenticationToken[BasicPayload]):
    pass


class PrivilegedAuthenticationToken(GenericAuthenticationToken[PrivilegedPayload]):
    pass
