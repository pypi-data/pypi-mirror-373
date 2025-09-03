import datetime
from decimal import Decimal
from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl, ValidationInfo, field_validator

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiDisplayText, OcpiPrice
from ocpi_pydantic.v221.enum import OcpiDayOfWeekEnum, OcpiReservationRestrictionTypeEnum, OcpiTariffDimensionTypeEnum, OcpiTariffTypeEnum
from ocpi_pydantic.v221.locations.location import OcpiEnergyMix



class OcpiPriceComponent(BaseModel):
    '''
    OCPI 11.4.2. PriceComponent class

    NOTE: `step_size`: depends on the type and every type (except FLAT) defines a step_size multiplier, which is the
    size of every *step* for that type in the given unit.

    For example: `PARKING_TIME` has the `step_size` multiplier: *1 second*, which means that the step_size of a
    `PriceComponent` is multiplied by *1 second*. Thus a `step_size = 300` means `300 seconds` (`5 minutes`).
    This means that when someone parked for 8 minutes they will be billed for 10 minutes. The parking time will be
    simply rounded up to the next larger chunk of `step_size` (i.e. blocks of `300 seconds` in this example).

    Another example: `ENERGY` has the `step_size` multiplied: *1 Wh*, which means that the `step_size` of a
    `PriceComponent` is multiplied by *1 Wh*. Thus a `step_size = 1` with a `price = 0.25` will result in a cost
    calculation that uses the charged Wh as precision.  
    If someone charges their EV with 115.2 Wh, then they are billed for 116 Wh, resulting in total cost of 0.029 euro.
    When `step_size = 25`, then the same amount would be billed for 101 to 125 Wh: 0.031 euro.
    When `step_size = 500`, then the same amount will be billed for 1 to 500 Wh: 0.125 euro.

    NOTE: For more information about how `step_size` impacts the calculation of the cost of charging see: CDR object
    description

    NOTE: Take into account that using `step_size` can be confusing for customers/drivers. There may be local or national
    regulations that define max `step_size`. E.g. in The Netherlands telecom companies are required to at least
    offer one subscription which is paid per second. To prevent confusion by the customer, we recommend to keep
    the step_size as small as possible and mention them clearly in your offering.
    '''
    type: OcpiTariffDimensionTypeEnum = Field(description='Type of tariff dimension.')
    price: Decimal = Field(description='Price per unit (excl. VAT) for this tariff dimension.')
    vat: Annotated[float | None, Field(
        description='''
        Applicable VAT percentage for this tariff dimension. If omitted, no VAT
        is applicable. Not providing a VAT is different from 0% VAT, which would
        be a value of 0.0 here.
        ''',
    )] = None
    step_size: int = Field(
        description='''
        Minimum amount to be billed. This unit will be billed in this step_size
        blocks. Amounts that are less then this step_size are rounded up to
        the given step_size. For example: if type is TIME and step_size
        has a value of 300, then time will be billed in blocks of 5 minutes. If 6
        minutes were used, 10 minutes (2 blocks of step_size) will be billed.
        ''',
    )



class OcpiTariffRestrictions(BaseModel):
    '''
    OCPI 11.4.6. TariffRestrictions class

    These restrictions are not for the entire Charging Session. They only describe if and when a TariffElement becomes active or
    inactive during a Charging Session.

    When more than one restriction is set, they are to be threaded as a logical AND. So all need to be valid before this tariff is active.
    '''
    start_time: Annotated[str | None, Field(
        min_length=5,
        max_length=5,
        description='''
        Start time of day in local time, the time zone is defined in the `time_zone` field of
        the Location, for example 13:30, valid from this time of the day. Must be in 24h
        format with leading zeros. Hour/Minute separator: ":" Regex: `([0-1][0-
        9]|2[0-3]):[0-5][0-9]`
        ''',
    )] = None
    end_time: Annotated[str | None, Field(
        min_length=5,
        max_length=5,
        description='''
        End time of day in local time, the time zone is defined in the `time_zone` field of
        the Location, for example 19:45, valid until this time of the day. Same syntax as
        `start_time`. If end_time < start_time then the period wraps around to the next
        day. To stop at end of the day use: 00:00.
        ''',
    )] = None
    start_date: Annotated[str | None, Field(
        min_length=10,
        max_length=10,
        description='''
        Start date in local time, the time zone is defined in the `time_zone` field of the
        Location, for example: 2015-12-24, valid from this day (inclusive). Regex:
        `([12][0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])`
        ''',
    )] = None
    end_date: Annotated[str | None, Field(
        min_length=10,
        max_length=10,
        description='''
        End date in local time, the time zone is defined in the `time_zone` field of the
        Location, for example: 2015-12-27, valid until this day (exclusive). Same syntax
        as `start_date`.
        ''',
    )] = None
    min_kwh: Annotated[float | None, Field(
        description='''
        Minimum consumed energy in kWh, for example 20, valid from this amount of
        energy (inclusive) being used.
        ''',
    )] = None
    max_kwh: Annotated[float | None, Field(
        description='''
        Maximum consumed energy in kWh, for example 50, valid until this amount of
        energy (exclusive) being used.
        ''',
    )] = None
    min_current: Annotated[float | None, Field(
        description='''
        Sum of the minimum current (in Amperes) over all phases, for example 5. When
        the EV is charging with more than, or equal to, the defined amount of current,
        this TariffElement is/becomes active. If the charging current is or becomes lower,
        this TariffElement is not or no longer valid and becomes inactive. This describes
        NOT the minimum current over the entire Charging Session. This restriction can
        make a TariffElement become active when the charging current is above the
        defined value, but the TariffElement MUST no longer be active when the
        charging current drops below the defined value.
        ''',
    )] = None
    max_current: Annotated[float | None, Field(
        description='''
        Sum of the maximum current (in Amperes) over all phases, for example 20.
        When the EV is charging with less than the defined amount of current, this
        TariffElement becomes/is active. If the charging current is or becomes higher,
        this TariffElement is not or no longer valid and becomes inactive. This describes
        NOT the maximum current over the entire Charging Session. This restriction can
        make a TariffElement become active when the charging current is below this
        value, but the TariffElement MUST no longer be active when the charging
        current raises above the defined value.
        ''',
    )] = None
    min_power: Annotated[float | None, Field(
        description='''
        Minimum power in kW, for example 5. When the EV is charging with more than,
        or equal to, the defined amount of power, this TariffElement is/becomes active. If
        the charging power is or becomes lower, this TariffElement is not or no longer
        valid and becomes inactive. This describes NOT the minimum power over the
        entire Charging Session. This restriction can make a TariffElement become
        active when the charging power is above this value, but the TariffElement MUST
        no longer be active when the charging power drops below the defined value.
        ''',
    )] = None
    max_power: Annotated[float | None, Field(
        description='''
        Maximum power in kW, for example 20. When the EV is charging with less than
        the defined amount of power, this TariffElement becomes/is active. If the
        charging power is or becomes higher, this TariffElement is not or no longer valid
        and becomes inactive. This describes NOT the maximum power over the entire
        Charging Session. This restriction can make a TariffElement become active
        when the charging power is below this value, but the TariffElement MUST no
        longer be active when the charging power raises above the defined value.
        ''',
    )] = None
    min_duration: Annotated[int | None, Field(
        description='''
        Minimum duration in seconds the Charging Session MUST last (inclusive).
        When the duration of a Charging Session is longer than the defined value, this
        TariffElement is or becomes active. Before that moment, this TariffElement is not
        yet active.
        ''',
    )] = None
    max_duration: Annotated[int | None, Field(
        description='''
        Maximum duration in seconds the Charging Session MUST last (exclusive).
        When the duration of a Charging Session is shorter than the defined value, this
        TariffElement is or becomes active. After that moment, this TariffElement is no
        longer active.
        ''',
    )] = None
    day_of_week: Annotated[list[OcpiDayOfWeekEnum], Field(description='Which day(s) of the week this TariffElement is active.')] = []
    reservation: Annotated[OcpiReservationRestrictionTypeEnum | None, Field(
        description='''
        When this field is present, the TariffElement describes reservation costs. A
        reservation starts when the reservation is made, and ends when the driver
        starts charging on the reserved EVSE/Location, or when the reservation
        expires. A reservation can only have: FLAT and TIME TariffDimensions, where
        `TIME` is for the duration of the reservation.
        ''',
    )] = None


    @field_validator('end_date', mode='after')
    @classmethod
    def validate_end_date(cls, value: str | None, info: ValidationInfo):
        start_date: str | None = info.data.get('start_date')
        if start_date and value:
            s_date = datetime.date(*map(int, start_date.split('-')))
            e_date = datetime.date(*map(int, value.split('-')))
            if s_date > e_date: raise ValueError('end_date must be after start_date')
        return value

    @field_validator('max_kwh', mode='after')
    @classmethod
    def validate_max_kwh(cls, value: float | None, info: ValidationInfo):
        min_kwh: float | None = info.data.get('min_kwh')
        if min_kwh and value:
            if min_kwh > value: raise ValueError('max_kwh must be larger than min_kwh')
        return value

    @field_validator('max_current', mode='after')
    @classmethod
    def validate_max_current(cls, value: float | None, info: ValidationInfo):
        min_current: float | None = info.data.get('min_kwh')
        if min_current and value:
            if min_current > value: raise ValueError('max_current must be larger than min_current')
        return value

    @field_validator('max_power', mode='after')
    @classmethod
    def validate_max_power(cls, value: float | None, info: ValidationInfo):
        min_power: float | None = info.data.get('min_kwh')
        if min_power and value:
            if min_power > value: raise ValueError('max_power must be larger than min_power')
        return value

    @field_validator('max_duration', mode='after')
    @classmethod
    def validate_max_duration(cls, value: int | None, info: ValidationInfo):
        min_duration: int | None = info.data.get('min_kwh')
        if min_duration and value:
            if min_duration > value: raise ValueError('max_duration must be larger than min_duration')
        return value



class OcpiTariffElement(BaseModel):
    '''
    OCPI 11.4.4. TariffElement class
    '''
    price_components: list[OcpiPriceComponent] = Field(description='List of price components that describe the pricing of a tariff.')
    restrictions: Annotated[OcpiTariffRestrictions | None, Field(description='Restrictions that describe the applicability of a tariff.')] = None



class OcpiTariff(BaseModel):
    '''
    OCPI 11.3.1. Tariff Object

    A Tariff object consists of a list of one or more Tariff Elements, which can be used to create complex Tariff structures.

    When the list of Tariff Elements contains more than one Element with the same Tariff Dimension (ENERGY/FLAT/TIME etc.), than
    the first Tariff Element with that Dimension in the list with matching Tariff Restrictions will be used. Only one Tariff per Element type
    can be active at any point in time, but multiple Tariff Types can be active at once. IE you can have an ENERGY element and TIME
    element active at the same time, but only the first valid element of each.

    When no Tariff Element with a specific Dimension is found for which the Restrictions match, and there is no Tariff Element in the list
    with the given Dimension without Restrictions, there will be no costs for that Tariff Dimension.

    It is advised to always add a "default" Tariff Element per Dimension (ENERGY/FLAT/TIME etc.). This can be achieved by adding a
    Tariff Element without Restrictions after all other occurrences of the same Dimension in the list of Tariff Elements (the order is
    important). Such a Tariff Element will act as fallback when no other Tariff Element of a specific Dimension matches the relevant
    parameters (Restrictions).

    To define a "Free of Charge" tariff in OCPI, a Tariff with `type = FLAT` and `price = 0.00` has to be provided. See: Free of Charge
    Tariff example

    NOTE: `min_price`: As the VAT might be built up of different parts, there might be situations where minimum cost
    including VAT is reached earlier or later than the minimum cost excluding VAT. So as a rule, they both apply: -
    The total cost of a Charging Session excluding VAT can never be lower than the `min_price` excluding VAT. -
    The total cost of a Charging Session including VAT can never be lower than the `min_price` including VAT.

    NOTE: `max_price`: As the VAT might be built up of different parts, there might be situations where maximum cost
    including VAT is reached earlier or later than the maximum cost excluding VAT. So as a rule, they both apply: -
    The total cost of a Charging Session excluding VAT can never be higher than the `max_price` excluding VAT. -
    The total cost of a Charging Session including VAT can never be higher than the `max_price` including VAT.

    NOTE: `start_date_time` and `end_date_time`: When the Tariff of a Charge Point (Location) is changed during an
    ongoing charging session, it is common to not switch the Tariff until the ongoing session is finished. But this is
    NOT a requirement of OCPI, it is even possible with OCPI. Changing tariffs during an ongoing session is in many
    countries not allowed by consumer legislation. When charging at a Charge Point, a driver accepts the tariff which
    is valid when they start their charging session. If the Tariff of the Charge Point would change during the charging
    session, the driver might get billed something they didn't agree to when starting the session.

    NOTE: The fields: `tariff_alt_text` and `tariff_alt_url` may be used separately, or in combination with each
    other or even combined with the structured tariff elements. When a Tariff contains both the tariff_alt_text
    and elements fields, the tariff_alt_text SHALL only contain additional tariff information in human-
    readable text, not the price information that is also available via the elements field. Reason for this: the eMSP
    might have additional fees they want to include in communication with their customer.
    '''
    country_code: str = Field(min_length=2, max_length=2, description="""ISO-3166 alpha-2 country code of the CPO that 'owns' this Tariff.""")
    party_id: str = Field(
        min_length=3, max_length=3, description="""
        ID of the CPO that 'owns' this Traiff (following the ISO-15118
        standard).
        """,
    )
    id: str = Field(
        max_length=36,
        description='''
        Uniquely identifies the tariff within the CPO’s platform (and suboperator
        platforms).
        ''',
    )
    currency: str = Field(max_length=3, description='ISO-4217 code of the currency of this tariff.')
    type: Annotated[OcpiTariffTypeEnum | None, Field(
        description='''
        Defines the type of the tariff. This allows for distinction in case of given Charging
        Preferences. When omitted, this tariff is valid for all sessions.
        ''',
    )] = None
    tariff_alt_text: Annotated[list[OcpiDisplayText], Field(description='List of multi-language alternative tariff info texts.')] = []
    tariff_alt_url: Annotated[HttpUrl | None, Field(
        description='''
        URL to a web page that contains an explanation of the tariff information in
        human readable form.
        ''',
    )] = None
    min_price: Annotated[OcpiPrice | None, Field(
        description='''
        When this field is set, a Charging Session with this tariff will at least cost this
        amount. This is different from a `FLAT` fee (Start Tariff, Transaction Fee), as a
        `FLAT` fee is a fixed amount that has to be paid for any Charging Session. A
        minimum price indicates that when the cost of a Charging Session is lower than
        this amount, the cost of the Session will be equal to this amount. (Also see note
        below)
        ''',
    )] = None
    max_price: Annotated[OcpiPrice | None, Field(
        description='''
        When this field is set, a Charging Session with this tariff will NOT cost more than
        this amount. (See note below)
        ''',
    )] = None
    elements: list[OcpiTariffElement] = Field(description='List of Tariff Elements.')
    start_date_time: Annotated[AwareDatetime | None, Field(
        description='''
        The time when this tariff becomes active, in UTC, `time_zone` field of the
        Location can be used to convert to local time. Typically used for a new tariff that
        is already given with the location, before it becomes active. (See note below)
        ''',
    )] = None
    end_date_time: Annotated[AwareDatetime | None, Field(
        description='''
        The time after which this tariff is no longer valid, in UTC, `time_zone` field if the
        Location can be used to convert to local time. Typically used when this tariff is
        going to be replaced with a different tariff in the near future. (See note below)
        ''',
    )] = None
    energy_mix: Annotated[OcpiEnergyMix | None, Field(description='Details on the energy supplied with this tariff.')] = None
    last_updated: AwareDatetime = Field(description='Timestamp when this Tariff was last updated (or created).')


    @field_validator('end_date_time', mode='after')
    @classmethod
    def validate_end_date_time(cls, value: AwareDatetime | None, info: ValidationInfo):
        start_date_time: AwareDatetime | None = info.data.get('start_date_time')
        if start_date_time and value:
            if start_date_time > value: raise ValueError('end_date_time must be after start_date_time')
        return value
    

    @field_validator('tariff_alt_url', mode='before')
    @classmethod
    def validate_tariff_alt_url(cls, value: str | None, info: ValidationInfo):
        if not value: return None
        else: return value

    
    @field_validator('type', mode='before')
    @classmethod
    def validate_type(cls, value: str | None, info: ValidationInfo):
        if not value: return None
        else: return value


    @field_validator('max_price', mode='after')
    @classmethod
    def validate_max_price(cls, value: OcpiPrice | None, info: ValidationInfo):
        if not value: return value
        min_price: OcpiPrice | None = info.data.get('min_price')
        if not min_price: return value
        if value.excl_vat < min_price.excl_vat: raise ValueError('max_price should larger than min_price')
        if value.incl_vat < min_price.incl_vat: raise ValueError('max_price should larger than min_price')


    _examples: ClassVar[list[dict]] = [
        # OCPI 11.3.1.1. Examples
        { # Simple Tariff example 0.25 euro per kWh
            "country_code": "DE",
            "party_id": "ALL",
            "id": "16",
            "currency": "EUR",
            "elements": [{"price_components": [{
                "type": "ENERGY",
                "price": 0.25,
                "vat": 10.0,
                "step_size": 1,
            }]}],
            "last_updated": "2018-12-17T11:16:55Z",
        },
        { # Tariff example 0.25 euro per kWh + start fee
            "country_code": "DE",
            "party_id": "ALL",
            "id": "17",
            "currency": "EUR",
            "elements": [{"price_components": [
                {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}
            ]}],
            "last_updated": "2018-12-17T11:36:01Z"
        },
        { # Tariff example 0.25 euro per kWh + minimum price
            "country_code": "DE",
            "party_id": "ALL",
            "id": "20",
            "currency": "EUR",
            "min_price": {"excl_vat": 0.50, "incl_vat": 0.55},
            "elements": [{"price_components": [{"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}]}],
            "last_updated": "2018-12-17T16:45:21Z"
        },
        { # Tariff example 0.25 euro per kWh + parking fee + start fee
            "country_code": "DE",
            "party_id": "ALL",
            "id": "18",
            "currency": "EUR",
            "elements": [{"price_components": [
                {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1},
                {"type": "PARKING_TIME", "price": 2.00, "vat": 20.0, "step_size": 900}
            ]}],
            "last_updated": "2018-12-17T11:44:10Z"
        },
        { # Tariff example 0.25 euro per kWh + start fee + max price + tariff end date
            "country_code": "DE",
            "party_id": "ALL",
            "id": "16",
            "currency": "EUR",
            "max_price": {"excl_vat": 10.00, "incl_vat": 11.00},
            "elements": [{"price_components": [
                {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}
            ]}],
            "end_date_time": "2019-06-30T23:59:59Z",
            "last_updated": "2018-12-17T17:15:01Z"
        },
        {
            "country_code": "DE",
            "party_id": "ALL",
            "id": "12",
            "currency": "EUR",
            "elements": [{"price_components": [{"type": "TIME", "price": 2.00, "vat": 10.0, "step_size": 60}]}],
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # Simple Tariff example 3 euro per hour, 5 euro per hour parking
            "country_code": "DE",
            "party_id": "ALL",
            "id": "21",
            "currency": "EUR",
            "elements": [{"price_components": [
                {"type": "TIME", "price": 3.00, "vat": 10.0, "step_size": 60},
                {"type": "PARKING_TIME", "price": 5.00, "vat": 20.0, "step_size": 300}
            ]}],
            "last_updated": "2018-12-17T17:00:43Z"
        },
        { # Ad-Hoc simple Tariff example with multiple languages
            "country_code": "DE",
            "party_id": "ALL",
            "id": "12",
            "currency": "EUR",
            "type": "AD_HOC_PAYMENT",
            "tariff_alt_text": [
                {"language": "en", "text": "2.00 euro p/hour including VAT."},
                {"language": "nl", "text": "2.00 euro p/uur inclusief BTW."}
            ],
            "elements": [{"price_components": [{"type": "TIME", "price": 1.90, "vat": 5.2, "step_size": 300}]}],
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # Ad-Hoc Tariff example not possible with OCPI
            "country_code": "DE",
            "party_id": "ALL",
            "id": "19",
            "currency": "EUR",
            "type": "AD_HOC_PAYMENT",
            "tariff_alt_text": [
                {"language": "en", "text": "2.00 euro p/hour, start tariff debit card: 0.25 euro, credit card: 0.50 euro including VAT."},
                {"language": "nl", "text": "2.00 euro p/uur, starttarief bankpas: 0,25 euro, creditkaart: 0,50 euro inclusief BTW."}
            ],
            "elements": [{"price_components": [
                {"type": "FLAT", "price": 0.40, "vat": 25.0, "step_size": 1},
                {"type": "TIME", "price": 1.90, "vat": 5.2, "step_size": 300}
            ]}],
            "last_updated": "2018-12-29T15:55:58Z"
        },
        { # Simple Tariff example with alternative URL
            "country_code": "DE",
            "party_id": "ALL",
            "id": "13",
            "currency": "EUR",
            "type": "PROFILE_CHEAP",
            "tariff_alt_url": "https://company.com/tariffs/13",
            "elements": [{"price_components": [
                {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 100}
            ]}],
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # Complex Tariff example
            "country_code": "DE",
            "party_id": "ALL",
            "id": "14",
            "currency": "EUR",
            "type": "REGULAR",
            "tariff_alt_url": "https://company.com/tariffs/14",
            "elements": [
                {"price_components": [{"type": "FLAT", "price": 2.50, "vat": 15.0, "step_size": 1}]},
                {
                    "price_components": [{"type": "TIME", "price": 1.00, "vat": 20.0, "step_size": 900}],
                    "restrictions": {"max_current": 32.00}
                },
                {
                    "price_components": [{"type": "TIME", "price": 2.00, "vat": 20.0, "step_size": 600}],
                    "restrictions": {"min_current": 32.00, "day_of_week": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]}
                },
                {
                    "price_components": [{"type": "TIME", "price": 1.25, "vat": 20.0, "step_size": 600}],
                    "restrictions": { "min_current": 32.00, "day_of_week": ["SATURDAY", "SUNDAY"]}
                },
                {
                    "price_components": [{"type": "PARKING_TIME", "price": 5.00, "vat": 10.0, "step_size": 300}],
                    "restrictions": {"start_time": "09:00", "end_time": "18:00", "day_of_week": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]}
                },
                {
                    "price_components": [{"type": "PARKING_TIME", "price": 6.00, "vat": 10.0, "step_size": 300}],
                    "restrictions": {"start_time": "10:00", "end_time": "17:00", "day_of_week": ["SATURDAY"]}
                }
            ],
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # Free of Charge Tariff example
            "country_code": "DE",
            "party_id": "ALL",
            "id": "15",
            "currency": "EUR",
            "elements": [{"price_components": [{"type": "FLAT", "price": 0.00, "step_size": 0}]}],
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # First hour free energy example
            "country_code": "DE",
            "party_id": "ALL",
            "id": "52",
            "currency": "EUR",
            "elements": [
                {
                    "price_components": [{"type": "PARKING_TIME", "price": 0.0, "step_size": 60}],
                    "restrictions": {"min_duration": 0, "max_duration": 3600}
                },
                {
                    "price_components": [{"type": "PARKING_TIME", "price": 2.0, "step_size": 60}],
                    "restrictions": {"min_duration": 3600, "max_duration": 10800}
                },
                {
                    "price_components": [{"type": "PARKING_TIME", "price": 3.0, "step_size": 60}],
                    "restrictions": {"min_duration": 10800}
                },
                {
                    "price_components": [{"type": "ENERGY", "price": 0.0, "step_size": 1}],
                    "restrictions": {"max_kwh": 1.0}
                },
                {
                    "price_components": [{"type": "ENERGY", "price": 0.2, "step_size": 1}],
                    "restrictions": {"min_kwh": 1.0}
                }
            ],
            "last_updated": "2018-12-29T15:55:58Z"
        },
        { # Tariff example with reservation price
            "country_code": "DE",
            "party_id": "ALL",
            "id": "20",
            "currency": "EUR",
            "elements": [
                {
                    "price_components": [{"type": "TIME", "price": 5.00, "vat": 20.0, "step_size": 60}],
                    "restrictions": {"reservation": "RESERVATION"}
                },
                {"price_components": [
                    {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                    {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}]
                }
            ],
            "last_updated": "2019-02-03T17:00:11Z"
        },
        { # Tariff example with reservation price and fee
            "country_code": "DE",
            "party_id": "ALL",
            "id": "20",
            "currency": "EUR",
            "elements": [
                {
                    "price_components": [
                        {"type": "FLAT", "price": 2.00, "vat": 20.0, "step_size": 1},
                        {"type": "TIME", "price": 5.00, "vat": 20.0, "step_size": 300}
                    ],
                    "restrictions": {"reservation": "RESERVATION"}
                },
                {"price_components": [
                    {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                    {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}
                ]}
            ],
            "last_updated": "2019-02-03T17:00:11Z"
        },
        { # Tariff example with reservation price and expire fee
            "country_code": "DE",
            "party_id": "ALL",
            "id": "20",
            "currency": "EUR",
            "elements": [
                {
                    "price_components": [{"type": "FLAT", "price": 4.00, "vat": 20.0, "step_size": 1}],
                    "restrictions": {"reservation": "RESERVATION_EXPIRES"}
                },
                {
                    "price_components": [{"type": "TIME", "price": 2.00, "vat": 20.0, "step_size": 600}],
                    "restrictions": {"reservation": "RESERVATION"}
                },
                {"price_components": [
                    {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                    {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}
                ]}
            ],
            "last_updated": "2019-02-03T17:00:11Z"
        },
        { # Tariff example with reservation time and expire time
            "country_code": "DE",
            "party_id": "ALL",
            "id": "20",
            "currency": "EUR",
            "elements": [
                {
                    "price_components": [{"type": "TIME", "price": 6.00, "vat": 20.0, "step_size": 600}],
                    "restrictions": {"reservation": "RESERVATION_EXPIRES"}
                },
                {
                    "price_components": [{"type": "TIME", "price": 3.00, "vat": 20.0, "step_size": 600}],
                    "restrictions": {"reservation": "RESERVATION"}
                },
                {
                    "price_components": [
                        {"type": "FLAT", "price": 0.50, "vat": 20.0, "step_size": 1},
                        {"type": "ENERGY", "price": 0.25, "vat": 10.0, "step_size": 1}
                    ]
                }
            ],
            "last_updated": "2019-02-03T17:00:11Z"
        },

        # OCPI 11.4.2.1. Example Tariff
        {
            "country_code": "DE",
            "party_id": "ALL",
            "id": "22",
            "currency": "EUR",

            "elements": [
                {
                    "price_components": [
                        {"type": "TIME", "price": 1.20, "step_size": 1800},
                        {"type": "PARKING_TIME", "price": 1.00, "step_size": 900}
                    ],
                    "restrictions" : {"start_time" : "00:00", "end_time" : "17:00"}
                },
                {
                    "price_components": [
                        {"type": "TIME", "price": 2.40, "step_size": 900},
                        {"type": "PARKING_TIME", "price": 1.00, "step_size": 900},
                    ],
                    "restrictions" : {"start_time" : "17:00", "end_time" : "20:00"}
                },
                {
                    "price_components": [{"type": "TIME", "price": 2.40, "step_size": 900}],
                    "restrictions" : {"start_time" : "20:00", "end_time" : "00:00"}
                }
            ],
            "last_updated": "2018-12-18T17:07:11Z"
        },

        # OCPI 11.4.6.1. Example: Tariff with max_power Tariff Restrictions
        {
            "country_code": "DE",
            "party_id": "ALL",
            "id": "1",
            "currency": "EUR",
            "type": "REGULAR",
            "elements": [
                {
                    "price_components": [{"type": "ENERGY", "price": 0.20, "vat": 20.0, "step_size": 1}],
                    "restrictions": {"max_power": 16.00}
                },
                {
                "price_components": [{"type": "ENERGY", "price": 0.35, "vat": 20.0, "step_size": 1}],
                "restrictions": {"max_power": 32.00}
                },
                {"price_components": [{"type": "ENERGY", "price": 0.50, "vat": 20.0, "step_size": 1}]}
            ],
            "last_updated": "2018-12-05T12:01:09Z"
        },
        
        # OCPI 11.4.6.2. Example: Tariff with max_duration Tariff Restrictions
        {
            "country_code": "DE",
            "party_id": "ALL",
            "id": "2",
            "currency": "EUR",
            "type": "REGULAR",
            "elements": [
                {
                    "price_components": [{"type": "ENERGY", "price": 0.00, "vat": 20.0, "step_size": 1}],
                    "restrictions": {"max_duration": 1800}
                },
                {
                    "price_components": [{"type": "ENERGY", "price": 0.25, "vat": 20.0, "step_size": 1}],
                    "restrictions": {"max_duration": 3600}
                },
                {"price_components": [{"type": "ENERGY", "price": 0.40, "vat": 20.0, "step_size": 1}]}
            ],
            "last_updated": "2018-12-05T13:12:44Z"
        }
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiTariffResponse(OcpiBaseResponse):
    data: OcpiTariff = ...

    _examples: ClassVar[dict] = [{
        'data': OcpiTariff._examples[0], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiTariffListResponse(OcpiBaseResponse):
    data: list[OcpiTariff] = []

    _examples: ClassVar[dict] = [{
        'data': [OcpiTariff._examples[0]], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})
