from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiDisplayText
from ocpi_pydantic.v221.enum import OcpiAllowedTypeEnum, OcpiProfileTypeEnum, OcpiTokenTypeEnum, OcpiWhitelistTypeEnum



class OcpiEnergyContract(BaseModel):
    '''
    OCPI 12.4.2. EnergyContract class

    Information about a energy contract that belongs to a Token so a driver could use his/her own energy contract when charging at a
    Charge Point.
    '''

    supplier_name: str = Field(description='Name of the energy supplier for this token.', max_length=64)
    contract_id: Annotated[str | None, Field(description='Contract ID at the energy supplier, that belongs to the owner of this token.')] = None



class OcpiToken(BaseModel):
    '''
    OCPI 12.3.2. Token Object

    - `uid`:
        Unique ID by which this Token, combined with the Token type, can be identified.
        This is the field used by CPO system (RFID reader on the Charge Point) to
        identify this token.
        Currently, in most cases: type=RFID, this is the RFID hidden ID as read by the
        RFID reader, but that is not a requirement.
        If this is a `APP_USER` or `AD_HOC_USER` Token, it will be a uniquely, by the eMSP,
        generated ID.
        This field is named `uid` instead of `id` to prevent confusion with: `contract_id`.
    - `contract_id`:
        Uniquely identifies the EV Driver contract token within the eMSP’s platform (and
        suboperator platforms). Recommended to follow the specification for eMA ID
        from "eMI3 standard version V1.0" (http://emi3group.com/documents-links/)
        "Part 2: business objects."
    - `group_id`:
        This ID groups a couple of tokens. This can be used to make two or more
        tokens work as one, so that a session can be started with one token and
        stopped with another, handy when a card and key-fob are given to the EV-driver.
        Beware that OCPP 1.5/1.6 only support group_ids (it is called parentId in OCPP
        1.5/1.6) with a maximum length of 20.
    - `language`:
        Language Code ISO 639-1. This optional field indicates the Token owner’s
        preferred interface language. If the language is not provided or not supported
        then the CPO is free to choose its own language.
    - `default_profile_type`:
        he default Charging Preference. When this is provided, and a charging session
        is started on an Charge Point that support Preference base Smart Charging and
        support this ProfileType, the Charge Point can start using this ProfileType,
        without this having to be set via: Set Charging Preferences.
    - `energy_contract`:
        When the Charge Point supports using your own energy supplier/contract at a
        Charge Point, information about the energy supplier/contract is needed so the
        CPO knows which energy supplier to use.
        NOTE: In a lot of countries it is currently not allowed/possible to use a drivers
        own energy supplier/contract at a Charge Point.

    The combination of _uid_ and _type_ should be unique for every token within the eMSP’s system.

    NOTE: OCPP supports group_id (or ParentID as it is called in OCPP 1.5/1.6) OCPP 1.5/1.6 only support group ID’s with
    maximum length of string(20), case insensitive. As long as EV-driver can be expected to charge at an OCPP
    1.5/1.6 Charge Point, it is adviced to not used a group_id longer then 20.
    '''

    country_code: str = Field(description="ISO-3166 alpha-2 country code of the MSP that 'owns' this Token.", min_length=2, max_length=2)
    party_id: str = Field(description="ID of the eMSP that 'owns' this Token (following the ISO-15118 standard).", min_length=3, max_length=3)
    uid: str = Field(description='Unique ID by which this Token, combined with the Token type, can be identified.', max_length=36)
    type: OcpiTokenTypeEnum = Field(description='Type of the token')
    contract_id: str = Field(description='Uniquely identifies the EV Driver contract token within the eMSP’s platform (and suboperator platforms).', max_length=36)
    visual_number: Annotated[str | None, Field(description='Visual readable number/identification as printed on the Token (RFID card), might be equal to the contract_id.', max_length=64)] = None
    issuer: str = Field(description='Issuing company, most of the times the name of the company printed on the token (RFID card), not necessarily the eMSP.', max_length=64)
    group_id: Annotated[str | None, Field(description='This ID groups a couple of tokens.')] = None
    valid: bool = Field(description='Is this Token valid')
    whitelist: OcpiWhitelistTypeEnum = Field(description='Indicates what type of white-listing is allowed.')
    language: Annotated[str | None, Field(description='Language Code ISO 639-1.', min_length=2, max_length=2)] = None
    default_profile_type: Annotated[OcpiProfileTypeEnum | None, Field(description='The default Charging Preference.')] = None
    energy_contract: Annotated[OcpiEnergyContract | None, Field(description='When the Charge Point supports using your own energy supplier/contract at a Charge Point, information about the energy supplier/contract is needed so the CPO knows which energy supplier to use.')] = None
    last_updated: AwareDatetime = Field(description='Timestamp when this Token was last updated (or created).')

    _examples: ClassVar[list[dict]] = [
        { # A new Token
            "country_code": "NL",
            "party_id": "TNM",
            "uid": "012345678",
            "type": "RFID",
            "contract_id": "NL8ACC12E46L89",
            "visual_number": "DF000-2001-8999-1",
            "issuer": "TheNewMotion",
            "group_id": "DF000-2001-8999",
            "valid": True,
            "whitelist": "ALWAYS",
            "last_updated": "2015-06-29T22:39:09Z"
        },
        { # Simple APP_USER example
            "country_code": "DE",
            "party_id": "TNM",
            "uid": "bdf21bce-fc97-11e8-8eb2-f2801f1b9fd1",
            "type": "APP_USER",
            "contract_id": "DE8ACC12E46L89",
            "issuer": "TheNewMotion",
            "valid": True,
            "whitelist": "ALLOWED",
            "last_updated": "2018-12-10T17:16:15Z"
        },
        { # Full RFID example
            "country_code": "DE",
            "party_id": "TNM",
            "uid": "12345678905880",
            "type": "RFID",
            "contract_id": "DE8ACC12E46L89",
            "visual_number": "DF000-2001-8999-1",
            "issuer": "TheNewMotion",
            "group_id": "DF000-2001-8999",
            "valid": True,
            "whitelist": "ALLOWED",
            "language": "it",
            "default_profile_type": "GREEN",
            "energy_contract": {"supplier_name": "Greenpeace Energy eG", "contract_id": "0123456789"},
            "last_updated": "2018-12-10T17:25:10Z"
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiTokenResponse(OcpiBaseResponse):
    data: OcpiToken = ...

    _examples: ClassVar[dict] = [{'data': OcpiToken._examples[0], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z'}]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiTokenListResponse(OcpiBaseResponse):
    data: list[OcpiToken] = ...

    _examples: ClassVar[dict] = [{'data': [OcpiToken._examples[0]], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z'}]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiLocationReferences(BaseModel):
    '''
    OCPI 12.4.3. LocationReferences class

    References to location details.
    '''

    location_id: str = Field(description='Unique identifier for the location.', max_length=36)
    evse_uids: Annotated[list[str], Field(description='Unique identifiers for EVSEs within the CPO’s platform for the EVSE within the given location.', max_length=36)] = []



class OcpiAuthorizationInfo(BaseModel):
    '''
    OCPI 12.3.1. AuthorizationInfo Object

    - `location`:
        Optional reference to the location if it was included in the request, and if
        the EV driver is allowed to charge at that location. Only the EVSEs the
        EV driver is allowed to charge at are returned.
    - `authorization_reference`:
        Reference to the authorization given by the eMSP, when given, this
        reference will be provided in the relevant Session and/or CDR.
    '''

    allowed: OcpiAllowedTypeEnum = Field(description='Status of the Token, and whether charging is allowed at the optionally given location')
    token: OcpiToken = Field(description='The complete Token object for which this authorization was requested.')
    location: Annotated[OcpiLocationReferences | None, Field(description='Optional reference to the location if it was included in the request, and if the EV driver is allowed to charge at that location.')] = None
    authorization_reference: Annotated[str | None, Field(description='Reference to the authorization given by the eMSP')] = None
    info: Annotated[OcpiDisplayText | None, Field(description='')] = None

    _example: ClassVar[dict] = {
        'allowed': OcpiAllowedTypeEnum.ALLOWED,
        'token': OcpiToken._examples[0],
        'location': None,
        'authorization_reference': None,
        'info': None,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiAuthorizationInfoResponse(OcpiBaseResponse):
    data: OcpiAuthorizationInfo = ...

    _examples: ClassVar[dict] = [{
        'data': OcpiAuthorizationInfo._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})