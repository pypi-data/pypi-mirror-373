from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiPrice
from ocpi_pydantic.v221.enum import OcpiAuthMethodEnum, OcpiConnectorFormatEnum, OcpiConnectorTypeEnum, OcpiCdrDimensionTypeEnum, OcpiPowerTypeEnum, OcpiTokenTypeEnum
from ocpi_pydantic.v221.locations import OcpiGeoLocation
from ocpi_pydantic.v221.tariffs import OcpiTariff



class OcpiCdrToken(BaseModel):
    '''
    OCPI 10.4.5. CdrToken class
    '''

    country_code: str = Field(min_length=2, max_length=2, description="ISO-3166 alpha-2 country code of the MSP that 'owns' this Token.")
    party_id: str = Field(min_length=3, max_length=3, description="ID of the eMSP that 'owns' this Token (following the ISO-15118 standard).", )
    uid: str = Field(
        max_length=36,
        description='''
        Unique ID by which this Token can be identified.
        This is the field used by the CPO’s system (RFID reader on the Charge Point) to
        identify this token.
        Currently, in most cases: `type=RFID`, this is the RFID hidden ID as read by the
        RFID reader, but that is not a requirement.
        If this is a `type=APP_USER` Token, it will be a unique, by the eMSP, generated
        ID.
        ''',
    )
    type: OcpiTokenTypeEnum = Field(description='Type of the token')
    contract_id: str = Field(
        max_length=36,
        description='''
        Uniquely identifies the EV driver contract token within the eMSP’s platform (and
        suboperator platforms). Recommended to follow the specification for eMA ID
        from "eMI3 standard version V1.0" (http://emi3group.com/documents-links/)
        "Part 2: business objects."
        ''',
    )



class OcpiCdrDimension(BaseModel):
    '''
    OCPI 10.4.2. CdrDimension class
    '''
    type: OcpiCdrDimensionTypeEnum = Field(description='Type of CDR dimension.')
    volume: float = Field(description='Volume of the dimension consumed, measured according to the dimension type.')



class OcpiCdrLocation(BaseModel):
    '''
    OCPI 10.4.4. CdrLocation class

    The CdrLocation class contains only the relevant information from the Location object that is needed in a CDR.
    '''
    id: str = Field(
        max_length=36,
        description='''
        Uniquely identifies the location within the CPO’s platform (and suboperator
        platforms). This field can never be changed, modified or renamed.
        ''',
    )
    name: Annotated[str | None, Field(max_length=255, description='Display name of the location.')] = None
    address: str = Field(min_length=1, max_length=45, description='Street/block name and house number if available.')
    city: str = Field(min_length=1, max_length=45, description='City or town.')
    postal_code: Annotated[str | None, Field(
        max_length=10,
        description='''
        Postal code of the location, may only be omitted when the location has no postal
        code. In some countries, charging locations at highways don’t have postal codes.
        ''',
    )] = None
    state: Annotated[str | None, Field(max_length=20, description='State only to be used when relevant.')] = None
    country: str = Field(max_length=3, description='ISO 3166-1 alpha-3 code for the country of this location.')
    coordinates: OcpiGeoLocation = Field(description='Coordinates of the location.')
    evse_uid : str = Field(
        max_length=36,
        description='''
        Uniquely identifies the EVSE within the CPO’s platform (and suboperator
        platforms). For example a database unique ID or the actual _EVSE ID_. This field
        can never be changed, modified or renamed. This is the _technical_ identification
        of the EVSE, not to be used as _human_ readable identification, use the field:
        `evse_id` for that. Allowed to be set to: `#NA` when this CDR is created for a
        reservation that never resulted in a charging session.
        ''',
    )
    evse_id: str = Field(
        max_length=48,
        description='''
        Compliant with the following specification for EVSE ID from "eMI3 standard
        version V1.0" (http://emi3group.com/documents-links/) "Part 2: business
        objects.". Allowed to be set to: `#NA` when this CDR is created for a reservation
        that never resulted in a charging session.
        ''',
    )
    connector_id: str = Field(
        max_length=36,
        description='''
        Identifier of the connector within the EVSE. Allowed to be set to: `#NA` when this
        CDR is created for a reservation that never resulted in a charging session.
        ''',
    )
    connector_standard: OcpiConnectorTypeEnum = Field(
        description='''
        The standard of the installed connector. When this CDR is created for a
        reservation that never resulted in a charging session, this field can be set to any
        value and should be ignored by the Receiver.
        ''',
    )
    connector_format: OcpiConnectorFormatEnum = Field(
        description='''
        The format (socket/cable) of the installed connector. When this CDR is created
        for a reservation that never resulted in a charging session, this field can be set
        to any value and should be ignored by the Receiver.
        ''',
    )
    connector_power_type: OcpiPowerTypeEnum = Field(
        description='''
        When this CDR is created for a reservation that never resulted in a charging
        session, this field can be set to any value and should be ignored by the
        Receiver.
        '''
    )




class OcpiChargingPeriod(BaseModel):
    '''
    OCPI 10.4.6. ChargingPeriod class

    A Charging Period consists of a start timestamp and a list of possible values that influence this period, for example: amount of energy charged this period, maximum current during this period etc.
    '''
    start_date_time: AwareDatetime = Field(
        description='''
        Start timestamp of the charging period. A period ends when the next period
        starts. The last period ends when the session ends.
        ''',
    )
    dimensions: list[OcpiCdrDimension] = Field(description='List of relevant values for this charging period.')
    tariff_id: Annotated[str | None, Field(
        max_length=36,
        description='''
        Unique identifier of the Tariff that is relevant for this Charging Period. If not
        provided, no Tariff is relevant during this period.
        ''',
    )] = None



class OcpiSignedValue(BaseModel):
    '''
    OCPI 10.4.8. SignedValue class

    This class contains the signed and the plain/unsigned data. By decoding the data, the receiver can check if the content has not
    been altered.
    '''
    nature: str = Field(
        max_length=32,
        description='''
        Nature of the value, in other words, the event this value belongs to.
        Possible values at moment of writing:
        - Start (value at the start of the Session)
        - End (signed value at the end of the Session)
        - Intermediate (signed values take during the Session, after Start, before End)
        Others might be added later.
        ''',
    )
    plain_data: str = Field(
        max_length=512,
        description='''
        The un-encoded string of data. The format of the content depends on the
        EncodingMethod field.
        ''',
    )
    signed_data : str = Field(
        max_length=5000,
        description='''
        Blob of signed data, base64 encoded. The format of the content depends on the
        EncodingMethod field.
        ''',
    )



class OcpiSignedData(BaseModel):
    '''
    OCPI 10.4.7. SignedData class
    
    This class contains all the information of the signed data. Which encoding method is used, if needed, the public key and a list of
    signed values.

    NOTE: For the German Eichrecht, different solutions are used, all have (somewhat) different encodings. Below the table
    with known implementations and the contact information for more information.
    '''
    encoding_method: str = Field(
        max_length=36,
        description='''
        The name of the encoding used in the SignedData field. This is the
        name given to the encoding by a company or group of companies. See
        note below.
        ''',
    )
    encoding_method_version: Annotated[int | None, Field(description='Version of the EncodingMethod (when applicable)')] = None
    public_key: Annotated[int | None, Field(max_length=512, description='Public key used to sign the data, base64 encoded.')] = None
    signed_values: list[OcpiSignedValue] = Field(description='One or more signed values.')
    url: Annotated[str | None, Field(
        max_length=512,
        description='''
        URL that can be shown to an EV driver. This URL gives the EV driver
        the possibility to check the signed data from a charging session.
        ''',
    )] = None



class OcpiCdr(BaseModel):
    '''
    OCPI 10.3.1. CDR Object

    The CDR object describes the charging session and its costs, how these costs are composed, etc.

    The CDR object is different from the Session object. The Session object is dynamic as it reflects the current state of the charging
    session. The information is meant to be viewed by the driver while the charging session is ongoing.

    The CDR on the other hand can be thought of as _sealed_, preserving the information valid at the moment in time the underlying
    session was started. This is a requirement of the main use case for CDRs, namely invoicing. If e.g. a street is renamed the day after
    a session took place, the driver should be presented with the name valid at the time the session was started. This guarantees that
    the CDR will be recognized as correct by the driver and is not going to be contested.

    The CDR object shall always contain information like Location, EVSE, Tariffs and Token as they were at the start of the charging
    session.

    **ChargingPeriod**: A CPO SHALL at least start (and add) a ChargingPeriod every moment/event that has relevance for the total
    costs of a CDR. During a charging session, different parameters change all the time, like the amount of energy used, or the time of
    day. These changes can result in another Tariff Element of the Tariff becoming active. When another Tariff Element becomes active,
    the CPO SHALL add a new Charging Period with at least all the relevant information for the change to the other Tariff Element. The
    CPO is allowed to add more in-between Charging Periods to a CDR though. Examples of additional Charging Periods:
    
    - When an energy based Tariff changes in price after 17:00. The CPO SHALL start a new Charging Period at 17:00, which
    contains at least the energy in kWh consumed until 17:00.

    - When the price of a Tariff is higher when the EV is charging faster than 32A, a new Charging Period SHALL be added the
    moment the charging power goes over 32A. This may be a moment that is calculated by the CPO, as the Charge Point
    might not send the information to the CPO, but it can be interpolated by the CPO using the metering information before and
    after that moment.

    **step_size**: When calculating the cost of a charging session, `step_size` SHALL only be taken into account once per session for
    the TariffDimensionType `ENERGY` and once for `PARKING_TIME` and `TIME` combined.

    `step_size` is not taken into account when switching time based paying for charging to paying for parking (charging has stopped
    but EV still connected).

    Example: `step_size` for both charging (`TIME`) and parking is 5 minutes. After 21 minutes of charging, the EV is full but remains
    connected for 7 more minutes. The cost of charging will be calculated based on 21 minutes (not 25). The cost of parking will be
    calculated based on 10 minutes (`step_size` is 5).

    `step_size` is not taken into account when switching from (for example) one `ENERGY` based tariff element to another. This is also
    true when switch from one (`TIME`) based tariff element to another (`TIME`) based tariff element, and one `PARKING_TIME` tariff
    element to another `PARKING_TIME` based tariff element.

    Example: when charging is more expensive after 17:00. The `step_size` of the tariff before 17:00 will not be used when charging
    starts before 17:00 and ends after 17:00. Only the `step_size` of the tariff (PriceComponent) after 17:00 is taken into account, for
    the total of the same amount for the session.

    The `step_size` for the PriceComponent that is used to calculate the cost of such a 'last' ChargingPeriod SHALL be used. If the
    `step_size` differs for the different TariffElements, the `step_size` of the last relevant PriceComponent is used.

    The `step_size` is not taken into account when switching between two Tariffs
    
    Example: A driver selects a different Charging Preference `profile_type` during an ongoing charging session, the different profile
    might have a different tariff.

    The `step_size` uses the total amount of a certain unit used during a session, not only the last ChargingPeriod. In other words,
    when charging tariff per kWh of time differs during a session, the total amount of kWh of time is used in calculations with
    `step_size`.

    Example: Charging cost 0.20 euro/Wh before 17:00 and 0.27 euro/Wh after 17:00 both have a `step_size` of 500 Wh. If a driver
    charges 4.3 kWh before 17:00 and 1.1 kWh after 17:00, a total of 5.4 kWh is charged. The `step_size` rounds this up to 5.5 kWh
    total. It does NOT round the energy used after 17:00 to 1.5 kWh.

    Example: Charging cost 5 euro/hour before 17:00 and 7 euro/hour after 17:00 both have a `step_size` of 10 minutes. If a driver
    charges 6 minutes before 17:00 and 22 minutes after 17:00: a total of 28 minutes charging. The `step_size` rounds this up to 30
    minutes total, so 24 minutes after 17:00 will be billed. It does NOT round the minutes after 17:00 to 30 minutes, which would have
    made a total of 36 minutes.

    In the cases that `TIME` and `PARKING_TIME` Tariff Elements are both used, `step_size` is only taken into account for the total
    parking duration.

    Example: Charging cost 1.00 euro/hour, parking 2.00 euro/hour both have a `step_size` of 10 minutes. If a driver charges 21
    minutes, and keeps his EV connected while it is full for another 16 minutes. The `step_size` rounds the parking duration up to 20
    minutes, making it a total of 41 minutes. Note that the charging duration is not rounded up, as it is followed by another time base
    period.

    NOTE: The actual charging duration (energy being transferred between EVSE and EV) of a charging session can be
    calculated: `total_charging_time` = `total_time` - `total_parking_time`.

    NOTE: Having both a `credit` and a `credit_reference_id` might seem redundant. But it is seen as an advantage as
    a boolean flag used in queries is much faster than simple string comparison of references.

    NOTE: Different `authorization_reference` values might happen when for example a ReserveNow had a different
    `authorization_reference` then the value returned by a real-time authorization.

    NOTE: When no `start_date_time` and/or `end_date_time` is known to the CPO, normally the CPO cannot send the
    CDR. If the MSP and CPO both agree that they accept CDRs that miss either or both the `start_date_time`
    and `end_date_time`, and local legislation allows billing of sessions where `start_date_time` and/or
    `end_date_time` are missing. Then, and only then, the CPO could send a CDR where the `start_date_time`
    and/or `end_date_time` are set to: "1970-1-1T00:00:00Z.
    '''
    country_code: str = Field(min_length=2, max_length=2, description="""ISO-3166 alpha-2 country code of the MSP that 'owns' this CDR.""")
    party_id: str = Field(
        min_length=3, max_length=3, description="""
        ID of the eMSP that 'owns' this CDR (following the ISO-15118
        standard).
        """,
    )
    id: str = Field(
        max_length=39,
        description='''
        Uniquely identifies the CDR, the ID SHALL be unique per
        country_code/party_id combination. This field is longer than
        the usual 36 characters to allow for credit CDRs to have something
        appended to the original ID. Normal (non-credit) CDRs SHALL only
        have an ID with a maximum length of 36.
        ''',
    )
    start_date_time: AwareDatetime = Field(
        description='''
        Start timestamp of the charging session, or in-case of a reservation
        (before the start of a session) the start of the reservation.
        ''',
    )
    end_date_time: AwareDatetime = Field(
        description='''
        The timestamp when the session was completed/finished, charging
        might have finished before the session ends, for example: EV is full,
        but parking cost also has to be paid.
        ''',
    )
    session_id: Annotated[str | None, Field(
        max_length=36,
        description='''
        Unique ID of the Session for which this CDR is sent. Is only allowed
        to be omitted when the CPO has not implemented the Sessions
        module or this CDR is the result of a reservation that never became
        a charging session, thus no OCPI Session.
        ''',
    )] = None
    cdr_token: OcpiCdrToken = Field(
        description='''
        Token used to start this charging session, including all the relevant
        information to identify the unique token.
        ''',
    )
    auth_method: OcpiAuthMethodEnum = Field(
        description='''
        Method used for authentication. Multiple
        AuthMethods are possible during
        a charging sessions, for example when the session was started
        with a reservation: ReserveNow: `COMMAND`. When the driver arrives
        and starts charging using a Token that is whitelisted: `WHITELIST`.
        The last method SHALL be used in the CDR.
        '''
    )
    authorization_reference: Annotated[str | None, Field(
        max_length=36,
        description='''
        Reference to the authorization given by the eMSP. When the eMSP
        provided an `authorization_reference` in either: real-time
        authorization, StartSession or ReserveNow this field SHALL
        contain the same value. When different
        `authorization_reference` values have been given by the
        eMSP that are relevant to this Session, the last given value SHALL
        be used here.
        ''',
    )] = None
    cdr_location: OcpiCdrLocation = Field(
        description='''
        Location where the charging session took place, including only the
        relevant EVSE and Connector.
        ''',
    )
    meter_id: Annotated[str | None, Field(max_length=255, description='Identification of the Meter inside the Charge Point.')] = None
    currency: str = Field(max_length=3, description='Currency of the CDR in ISO 4217 Code.')
    tariffs: Annotated[list[OcpiTariff], Field(
        description='''
        List of relevant Tariff Elements, see: Tariff. When relevant, a _Free of
        Charge_ tariff should also be in this list, and point to a defined _Free
        of Charge_ Tariff.
        ''',
    )] = []
    charging_periods: list[OcpiChargingPeriod] = Field(
        description='''
        List of Charging Periods that make up this charging session. A
        session consists of 1 or more periods, where each period has a
        different relevant Tariff.
        ''',
    )
    signed_data: Annotated[OcpiSignedData | None, Field(description='Signed data that belongs to this charging Session.')] = None
    total_cost: OcpiPrice = Field(
        description='''
        Total sum of all the costs of this transaction in the specified
        currency.
        ''',
    )
    total_fixed_cost: Annotated[OcpiPrice | None, Field(
        description='''
        Total sum of all the fixed costs in the specified currency, except
        fixed price components of parking and reservation. The cost not
        depending on amount of time/energy used etc. Can contain costs
        like a start tariff.
        ''',
    )] = None
    total_energy: float = Field(description='Total energy charged, in kWh.')
    total_energy_cost: Annotated[OcpiPrice | None, Field(
        description='''
        Total sum of all the cost of all the energy used, in the specified
        currency.
        ''',
    )] = None
    total_time: float = Field(description='Total duration of the charging session (including the duration of charging and not charging), in hours.')
    total_time_cost: Annotated[OcpiPrice | None, Field(
        description='''
        Total sum of all the cost related to duration of charging during this
        transaction, in the specified currency.
        ''',
    )] = None
    total_parking_time: Annotated[float | None, Field(
        description='''
        Total duration of the charging session where the EV was not
        charging (no energy was transferred between EVSE and EV), in
        hours.
        ''',
    )] = None
    total_parking_cost: Annotated[OcpiPrice | None, Field(
        description='''
        Total sum of all the cost related to parking of this transaction,
        including fixed price components, in the specified currency.
        ''',
    )] = None
    total_reservation_cost: Annotated[OcpiPrice | None, Field(
        description='''
        Total sum of all the cost related to a reservation of a Charge Point,
        including fixed price components, in the specified currency.
        ''',
    )] = None
    remark: Annotated[str | None, Field(
        max_length=255,
        description='''
        Optional remark, can be used to provide additional human readable
        information to the CDR, for example: reason why a transaction was
        stopped.
        ''',
    )] = None
    invoice_reference_id: Annotated[str | None, Field(
        max_length=255,
        description='''
        This field can be used to reference an invoice, that will later be send
        for this CDR. Making it easier to link a CDR to a given invoice.
        Maybe even group CDRs that will be on the same invoice.
        ''',
    )] = None
    credit: Annotated[bool | None, Field(
        description='''
        When set to `true`, this is a Credit CDR, and the field
        `credit_reference_id` needs to be set as well.
        ''',
    )] = None
    credit_reference_id: Annotated[str | None, Field(
        max_length=39,
        description='''
        Is required to be set for a Credit CDR. This SHALL contain the `id`
        of the CDR for which this is a Credit CDR.
        ''',
    )] = None
    home_charging_compensation: Annotated[bool | None, Field(
        description='''
        When set to `true`, this CDR is for a charging session using the
        home charger of the EV Driver for which the energy cost needs to
        be financial compensated to the EV Driver.
        ''',
    )] = None
    last_updated: AwareDatetime = Field(description='Timestamp when this CDR was last updated (or created).')


    _example: ClassVar[dict] = {
        "country_code": "BE",
        "party_id": "BEC",
        "id": "12345",
        "start_date_time": "2015-06-29T21:39:09Z",
        "end_date_time": "2015-06-29T23:37:32Z",
        "cdr_token": {"uid": "012345678", "type": "RFID", "contract_id": "DE8ACC12E46L89"},
        "auth_method": "WHITELIST",
        "cdr_location": {
            "id": "LOC1",
            "name": "Gent Zuid",
            "address": "F.Rooseveltlaan 3A",
            "city": "Gent",
            "postal_code": "9000",
            "country": "BEL",
            "coordinates": {"latitude": "3.729944", "longitude": "51.047599"},
            "evse_uid": "3256",
            "evse_id": "BE*BEC*E041503003",
            "connector_id": "1",
            "connector_standard": "IEC_62196_T2",
            "connector_format": "SOCKET",
            "connector_power_type": "AC_1_PHASE"
        },
        "currency": "EUR",
        "tariffs": [{
            "country_code": "BE",
            "party_id": "BEC",
            "id": "12",
            "currency": "EUR",
            "elements": [{
                "price_components": [{"type": "TIME", "price": 2.00, "vat": 10.0, "step_size": 300}]
            }],
            "last_updated": "2015-02-02T14:15:01Z"
        }],
        "charging_periods": [{
            "start_date_time": "2015-06-29T21:39:09Z",
            "dimensions": [{"type": "TIME", "volume": 1.973}],
            "tariff_id": "12"
        }],
        "total_cost": {"excl_vat": 4.00, "incl_vat": 4.40},
        "total_energy": 15.342,
        "total_time": 1.973,
        "total_time_cost": {"excl_vat": 4.00, "incl_vat": 4.40},
        "last_updated": "2015-06-29T22:01:13Z"
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiCdrResponse(OcpiBaseResponse):
    data: OcpiCdr = ...

    _examples: ClassVar[dict] = [{
        'data': OcpiCdr._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiCdrListResponse(OcpiBaseResponse):
    data: list[OcpiCdr] = []

    _examples: ClassVar[dict] = [{
        'data': [OcpiCdr._example], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})
