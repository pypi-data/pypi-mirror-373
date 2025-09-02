"""Type classes used by the ldap module"""

from datetime import date, datetime
from enum import Enum
from typing import (
    Annotated,
    Callable,
    ClassVar,
    Generic,
    Literal,
    Type,
    TypeVar,
    cast,
    overload,
)

from ldap3 import SUBTREE
from ldap3.utils.conv import escape_filter_chars
from pydantic import AliasPath, BaseModel, BeforeValidator, Field

from .connection import LDAPConnection
from .pydantic_validators import (
    active_to_bool,
    group_dn_to_name,
    string_to_date,
    to_str,
)


class SearchBase(str, Enum):
    """ldap search base"""

    USERS = "ou=users,dc=tu-dresden,dc=de"
    STRUCTURES = "ou=structures,dc=tu-dresden,dc=de"
    FACILITY = "ou=facilities,dc=tu-dresden,dc=de"


class LdapUserBase(BaseModel):
    """basic model for an LDAP user"""

    uid: Annotated[
        str,
        Field(
            validation_alias=AliasPath("uid", 0),
            serialization_alias="uid",
        ),
    ]


class LdapUserBulk(LdapUserBase):
    """model for the LDAP user search to get full names"""

    last_name: Annotated[
        str,
        Field(
            validation_alias=AliasPath("sn", 0),
            serialization_alias="sn",
        ),
    ]

    first_name: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("givenName", 0),
            serialization_alias="givenName",
        ),
    ] = None


class Gender(str, Enum):
    """gender of a User"""

    UNKNOWN = "0"
    MALE = "1"
    FEMALE = "2"
    DIVERSE = "3"
    NOT_SPECIFIED = "9"


class LdapUser(LdapUserBulk):
    """ldap user"""

    cn: Annotated[
        str,
        Field(
            validation_alias=AliasPath("cn", 0),
            serialization_alias="cn",
        ),
    ]
    job_title_de: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("title;lang-de", 0),
            serialization_alias="title;lang-de",
        ),
    ] = None
    job_title_en: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("title;lang-en", 0),
            serialization_alias="title;lang-en",
        ),
    ] = None
    personal_title: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("personalTitle", 0),
            serialization_alias="personalTitle",
        ),
    ] = None
    displayName: Annotated[
        str,
        Field(
            validation_alias=AliasPath("displayName", 0),
            serialization_alias="displayName",
        ),
    ]
    zihGender: Annotated[
        Gender | None,
        BeforeValidator(to_str),
        Field(
            validation_alias=AliasPath("zihGender", 0),
            serialization_alias="zihGender",
        ),
    ] = None
    email: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("mail", 0),
            serialization_alias="mail",
        ),
    ] = None
    edu_person_principal_name: Annotated[
        str,
        Field(
            validation_alias=AliasPath("eduPersonPrincipalName", 0),
            serialization_alias="eduPersonPrincipalName",
        ),
    ]
    affiliations: Annotated[
        list[str],
        Field(alias="eduPersonScopedAffiliation"),
    ]
    zihState: Annotated[
        bool,
        BeforeValidator(active_to_bool),
        Field(
            validation_alias=AliasPath("zihState", 0),
            serialization_alias="zihState",
        ),
    ]
    zihStateLastChanged: Annotated[
        datetime,
        Field(
            validation_alias=AliasPath("zihStateLastChanged", 0),
            serialization_alias="zihStateLastChanged",
        ),
    ]
    eduPersonPrimaryOrgUnitDN: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("eduPersonPrimaryOrgUnitDN", 0),
            serialization_alias="eduPersonPrimaryOrgUnitDN",
        ),
    ] = None
    eduPersonOrgUnitDN: list[str]
    o: Annotated[
        str,
        Field(
            validation_alias=AliasPath("o", 0),
            serialization_alias="o",
        ),
    ]
    ou: list[str]
    groupmemberOf: list[str]
    idm_groups: Annotated[
        list[str],
        BeforeValidator(group_dn_to_name),
        Field(alias="zihGroupmemberOf"),
    ]
    proxyAddresses: list[str]
    zihProxyAddresses: list[str]
    zihAcademicDegree: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("zihAcademicDegree", 0),
            serialization_alias="zihAcademicDegree",
        ),
    ] = None


ModelT = TypeVar("ModelT", bound=LdapUserBase)


class LdapUserManager:
    """ldap user manager"""

    def __init__(self, connection: LDAPConnection) -> None:
        self.connection = connection

    # you can't use default parameters for a TypeVar, so we have to use this
    # beautiful @overload construct found below
    # https://github.com/python/mypy/issues/3737
    # thank you mypy
    # since 2017...
    @overload
    def get(self, uid: str, *, get_inactive: bool = False) -> LdapUser: ...

    @overload
    def get(
        self,
        uid: str,
        attributes_model: type[ModelT],
        *,
        get_inactive: bool = False,
    ) -> ModelT: ...

    def get(  # type: ignore
        self,
        uid: str,
        attributes_model: type[LdapUserBase] = LdapUser,
        *,
        get_inactive: bool = False,
    ):
        """get LdapUser via uid"""
        escaped_uid = escape_filter_chars(uid)
        state_filter = "" if get_inactive else "(zihState=active)"
        filter_term = (
            f"(&(objectClass=zihAccount){state_filter}(uid={escaped_uid}))"
        )
        ldap_user = self.connection.get(
            filter_term, SearchBase.USERS.value, attributes_model
        )
        return ldap_user

    @overload
    def filter(
        self, search_term: str, *, get_inactive: bool = False
    ) -> list[LdapUser]: ...

    @overload
    def filter(
        self,
        search_term: str,
        attributes_model: type[ModelT],
        *,
        get_inactive: bool = False,
    ) -> list[ModelT]: ...

    def filter(  # type: ignore
        self,
        search_term,
        attributes_model=LdapUser,
        *,
        get_inactive: bool = False,
    ):
        """get ldap users via python ldap3 search term"""
        state_filter = "" if get_inactive else "(zihState=active)"
        filter_term = f"(&(objectClass=zihAccount){state_filter}{search_term})"
        return self.connection.filter(
            filter_term, SearchBase.USERS.value, attributes_model
        )

    @overload
    def get_bulk(
        self, uids: set[str], *, get_inactive: bool = False
    ) -> dict[str, LdapUserBulk]: ...

    @overload
    def get_bulk(
        self,
        uids: set[str],
        attributes_model: type[ModelT],
        *,
        get_inactive: bool = False,
    ) -> dict[str, ModelT]: ...

    def get_bulk(  # type: ignore
        self,
        uids,
        attributes_model=LdapUserBulk,
        *,
        get_inactive: bool = False,
    ):
        """get ldap users via bulk query"""
        uid_chunks = [
            list(uids)[i : i + 500] for i in range(0, len(uids), 500)
        ]
        ldap_users = []
        for uid_chunk in uid_chunks:
            uid_filter = "".join(
                f"(uid={escape_filter_chars(uid)})" for uid in uid_chunk
            )
            state_filter = "" if get_inactive else "(zihState=active)"
            filter_term = (
                f"(&(objectClass=zihAccount){state_filter}(|{uid_filter}))"
            )
            ldap_users.extend(
                self.connection.filter(
                    filter_term,
                    SearchBase.USERS.value,
                    attributes_model,
                )
            )
        return {user.uid: user for user in ldap_users}


class LdapOrgUnitBase(BaseModel):
    """base ldap orgunit"""

    dn: str
    ou: Annotated[
        str,
        Field(
            validation_alias=AliasPath("ou", 0),
            serialization_alias="ou",
        ),
    ]

    _get_language: ClassVar[Callable[[], Literal["de", "en"]]] = lambda: "de"

    @classmethod
    def set_get_language(
        cls,
        get_language: Callable[[], Literal["de", "en"]],
    ) -> None:
        cls._get_language = get_language

    def get_language(self) -> Literal["de", "en"]:
        return self.__class__._get_language()


class LdapOrgUnit(LdapOrgUnitBase):
    """ldap orgunit"""

    zihCostCenter: Annotated[
        str,
        Field(
            validation_alias=AliasPath("zihCostCenter", 0),
            serialization_alias="zihCostCenter",
        ),
    ]
    zihExpiryDate: Annotated[
        date | None,
        BeforeValidator(string_to_date),
        Field(
            validation_alias=AliasPath("zihExpiryDate", 0),
            serialization_alias="zihExpiryDate",
        ),
    ] = None
    zihStartDate: Annotated[
        date | None,
        BeforeValidator(string_to_date),
        Field(
            validation_alias=AliasPath("zihStartDate", 0),
            serialization_alias="zihStartDate",
        ),
    ] = None
    zihState: Annotated[
        Literal["false", "true", "deleted"] | None,
        Field(
            validation_alias=AliasPath("zihState", 0),
            serialization_alias="zihState",
        ),
    ] = None
    zihSupervisorOfStructureDN: list[str] | None = None
    zihOrganisationName: Annotated[
        str,
        Field(
            validation_alias=AliasPath("zihOrganisationName", 0),
            serialization_alias="zihOrganisationName",
        ),
    ]
    zihOrganisationNameDeLong: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("zihOrganisationNameDeLong", 0),
            serialization_alias="zihOrganisationNameDeLong",
        ),
    ] = None
    zihOrganisationNameEnLong: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("zihOrganisationNameEnLong", 0),
            serialization_alias="zihOrganisationNameEnLong",
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("description", 0),
            serialization_alias="description",
        ),
    ] = None

    @property
    def translated_name(self) -> str:
        """Get translated organisation name if existent"""
        name = self.zihOrganisationName
        if self.zihOrganisationNameDeLong:
            name = self.zihOrganisationNameDeLong
        if self.get_language() == "en" and self.zihOrganisationNameEnLong:
            name = self.zihOrganisationNameEnLong
        return name


OrgUnitModelT = TypeVar("OrgUnitModelT", bound=LdapOrgUnitBase)


class LdapOrgUnitManager:
    """ldap OrgUnit manager"""

    def __init__(self, connection: LDAPConnection) -> None:
        self.connection = connection

    @overload
    def get(self, ou_of_orgunit: str) -> LdapOrgUnit: ...

    @overload
    def get(
        self,
        ou_of_orgunit: str,
        attributes_model: type[OrgUnitModelT],
    ) -> OrgUnitModelT: ...

    def get(self, ou_of_orgunit, attributes_model=LdapOrgUnit):  # type: ignore
        """get LdapOrgUnit via ou"""
        escaped_ou_of_orgunit = escape_filter_chars(ou_of_orgunit)
        org_unit = self.connection.get(
            f"(ou={escaped_ou_of_orgunit})",
            SearchBase.STRUCTURES.value,
            attributes_model,
            SUBTREE,
        )
        return org_unit

    @overload
    def filter(self, search_term: str) -> list[LdapOrgUnit]: ...

    @overload
    def filter(
        self,
        search_term: str,
        attributes_model: type[OrgUnitModelT],
    ) -> list[OrgUnitModelT]: ...

    def filter(self, searchterm, attributes_model=LdapOrgUnit):  # type: ignore
        """get ldap OrgUnit via python ldap3 searchterm"""
        return self.connection.filter(
            searchterm,
            SearchBase.STRUCTURES.value,
            attributes_model,
            SUBTREE,
        )


FacilityType = Literal[
    "Institution", "Macro", "Micro", "Building", "Floor", "Room"
]
LdapFacilityUnitT = TypeVar("LdapFacilityUnitT", bound="LdapFacilityUnit")


class LdapFacilityUnitManager(Generic[LdapFacilityUnitT]):
    """ldap FacilityUnit manager"""

    def __init__(
        self, facility_type: FacilityType, connection: LDAPConnection
    ) -> None:
        self.connection = connection
        self.facility_type = facility_type

    @property
    def facility_model(self) -> Type["LdapFacilityUnit"]:
        """return facility model"""
        facility_models: dict[FacilityType, Type[LdapFacilityUnit]] = {
            "Institution": LdapFacilityInstitution,
            "Macro": LdapFacilityMacroLocation,
            "Micro": LdapFacilityMicroLocation,
            "Building": LdapFacilityBuilding,
            "Floor": LdapFacilityFloor,
            "Room": LdapFacilityRoom,
        }
        return facility_models[self.facility_type]

    def get(self, facility_id: str) -> LdapFacilityUnitT:
        """get LdapFacilityUnit via facility_id"""
        escaped_facility_id = escape_filter_chars(facility_id)
        facility = self.connection.get(
            f"(&(zihFacilityID={escaped_facility_id})(zihFacilityType={self.facility_type}))",
            SearchBase.FACILITY.value,
            self.facility_model,
            SUBTREE,
        )
        return cast(LdapFacilityUnitT, facility)

    def filter(self, filterterm: str) -> list[LdapFacilityUnitT]:
        """get ldap LdapFacilityUnit via python ldap3 search term"""
        return cast(
            list[LdapFacilityUnitT],
            self.connection.filter(
                f"(&{filterterm} (zihFacilityType={self.facility_type}))",
                SearchBase.FACILITY.value,
                self.facility_model,
                SUBTREE,
            ),
        )

    def all(self) -> list[LdapFacilityUnitT]:
        """get all ldap LdapFacilityUnit via of this type"""
        return cast(
            list[LdapFacilityUnitT],
            self.connection.filter(
                f"(zihFacilityType={self.facility_type})",
                SearchBase.FACILITY.value,
                self.facility_model,
                SUBTREE,
            ),
        )


class LdapFacilityUnit(BaseModel):
    """Base class for all facility unites"""

    zihFacilityID: Annotated[
        str,
        Field(
            validation_alias=AliasPath("zihFacilityID", 0),
            serialization_alias="zihFacilityID",
        ),
    ]
    zihFacilityType: Annotated[
        FacilityType,
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]
    zihFacilityName: Annotated[
        str,
        Field(
            validation_alias=AliasPath("zihFacilityName", 0),
            serialization_alias="zihFacilityName",
        ),
    ]
    zihStateLastChanged: Annotated[
        datetime,
        Field(
            validation_alias=AliasPath("zihStateLastChanged", 0),
            serialization_alias="zihStateLastChanged",
        ),
    ]


class LdapFacilityInstitution(LdapFacilityUnit):
    """ldap facility unit of a institution"""

    object_list: ClassVar[list["LdapFacilityInstitution"]] = []

    zihFacilityType: Annotated[
        Literal["Institution"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]


def newLdapFacilityInstitutionManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityInstitution"]:
    return LdapFacilityUnitManager(
        facility_type="Institution", connection=connection
    )


class LdapFacilityMacroLocation(LdapFacilityUnit):
    """ldap facility unit of a macrolocation"""

    zihFacilityType: Annotated[
        Literal["Macro"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]


def newLdapFacilityMacroLocationManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityMacroLocation"]:
    return LdapFacilityUnitManager(
        facility_type="Macro", connection=connection
    )


class LdapFacilityMicroLocation(LdapFacilityUnit):
    """ldap facility unit of a microlocation"""

    zihFacilityType: Annotated[
        Literal["Micro"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]


def newLdapFacilityMicroLocationManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityMicroLocation"]:
    return LdapFacilityUnitManager(
        facility_type="Micro", connection=connection
    )


class LdapFacilityBuilding(LdapFacilityUnit):
    """ldap facility unit of a building"""

    zihFacilityType: Annotated[
        Literal["Building"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]
    zihFacilityShortName: Annotated[
        str | None,
        Field(
            validation_alias=AliasPath("zihFacilityShortName", 0),
            serialization_alias="zihFacilityShortName",
        ),
    ] = None


def newLdapFacilityBuildingManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityBuilding"]:
    return LdapFacilityUnitManager(
        facility_type="Building", connection=connection
    )


class LdapFacilityFloor(LdapFacilityUnit):
    """ldap facility unit of a floor"""

    zihFacilityType: Annotated[
        Literal["Floor"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]


def newLdapFacilityFloorManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityFloor"]:
    return LdapFacilityUnitManager(
        facility_type="Floor", connection=connection
    )


class LdapFacilityRoom(LdapFacilityUnit):
    """ldap facility unit of a room"""

    zihFacilityType: Annotated[
        Literal["Room"],
        Field(
            validation_alias=AliasPath("zihFacilityType", 0),
            serialization_alias="zihFacilityType",
        ),
    ]
    zihFacilityRoomTypeID: Annotated[
        str,
        Field(validation_alias=AliasPath("zihFacilityRoomTypeID", 0)),
    ]


def newLdapFacilityRoomManager(
    connection: LDAPConnection,
) -> LdapFacilityUnitManager["LdapFacilityRoom"]:
    return LdapFacilityUnitManager(facility_type="Room", connection=connection)
