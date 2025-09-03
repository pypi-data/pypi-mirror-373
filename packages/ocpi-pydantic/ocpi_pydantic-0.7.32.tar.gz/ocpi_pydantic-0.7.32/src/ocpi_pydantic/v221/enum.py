from enum import Enum, IntEnum



class OcpiStatusCodeEnum(IntEnum):
    '''
    OCPI 5. Status codes
    '''
    # 5.1. 1xxx: Success
    SUCCESS = 1000 # Generic success code
    
    # 5.2. 2xxx: Client errors
    # Errors detected by the server in the message sent by a client where the client did something wrong.
    CLIENT_ERROR = 2000 # Generic client error
    INVALID_OR_MISSING_PARAMETERS = 2001 # Invalid or missing parameters , for example: missing `last_updated` field in a PATCH request.
    NOT_ENOUGH_INFORMATION = 2002 # Not enough information, for example: Authorization request with too little information.
    UNKNOWN_LOCATION = 2003 # Unknown Location, for example: Command: START_SESSION with unknown location.
    UNKNOWN_TOKEN = 2004 # Unknown Token, for example: 'real-time' authorization of an unknown Token.

    # 5.3. 3xxx: Server errors
    # Error during processing of the OCPI payload in the server. The message was syntactically correct but could not be processed by
    # the server.
    SERVER_ERROR = 3000 # Generic server error
    UNABLE_TO_USE_THE_CLIENTS_API = 3001 # Unable to use the client’s API. For example during the credentials registration: When the initializing party requests data from the other party during the open POST call to its credentials endpoint. If one of the GETs can not be processed, the party should return this error in the POST response.
    UNSUPPORTED_VERSION = 3002 # Unsupported version
    NO_MATCHING_ENDPOINTS_OR_EXPECTED_ENDPOINTS_MISSING_BETWEEN_PARTIES = 3003 # No matching endpoints or expected endpoints missing between parties. Used during the registration process if the two parties do not have any mutual modules or endpoints available, or the minimal implementation expected by the other party is not been met.

    # 5.4. 4xxx: Hub errors
    # When a server encounters an error, client side error (2xxx) or server side error (3xxx), it sends the status code to the Hub. The Hub
    #SHALL then forward this error to the client which sent the request (when the request was not a Broadcast Push).
    # For errors that a Hub encounters while routing messages, the following OCPI status codes shall be used.
    HUB_ERROR = 4000 # Generic error
    UNKNOWN_RECEIVER = 4001 # Unknown receiver (TO address is unknown)
    TIMEOUT_ON_FORWARDED_REQUEST = 4002 # Timeout on forwarded request (message is forwarded, but request times out)
    CONNECTION_PROBLEM = 4003 # Connection problem (receiving party is not connected)



class OcpiPartyRoleEnum(str, Enum):
    '''
    OCPI 16.5.1 Role enum & OCPI 2.2

    - CPO: Charging Point Operator. Operates a network of Charge Points.
    - eMSP: e-Mobility Service Provider. Gives EV drivers access to charging services.
    - Hub: Can connect one or more CPOs to one or more eMSPs.
    - NAP: National Access Point. Provides a national database with all (public) charging locations. Information can be sent and retrieved from the NAP. This makes it different from a typical NSP.
    - NSP: Navigation Service Provider. Provides EV drivers with location information of Charge Points. Usually only interested in Location information.
    - Roaming Hub: See: Hub.
    - SCSP: Smart Charging Service Provider. Provides Smart Charging service to other parties. Might use a lot of different inputs to calculate Smart Charging Profiles.
    '''
    CPO = 'CPO'
    EMSP = 'EMSP'
    HUB = 'HUB'



class OcpiVersionNumberEnum(str, Enum):
    'List of known versions.'
    v221 = '2.2.1'
    v220 = '2.2'
    v211 = '2.1.1'



class OcpiModuleIdEnum(str, Enum):
    '''
    The Module identifiers for each endpoint are described in the beginning of each Module chapter.
    '''
    cdrs = 'cdrs'
    chargingprofiles = 'chargingprofiles'
    commands = 'commands'
    credentials = 'credentials' # Required for all implementations. The role field has no function for this module.
    hubclientinfo = 'hubclientinfo'
    locations = 'locations'
    sessions = 'sessions'
    tariffs = 'tariffs'
    tokens = 'tokens'
    # versions = 'versions'



class OcpiInterfaceRoleEnum(str, Enum):
    '''
    - SENDER: Sender Interface implementation. Interface implemented by the owner of data, so the Receiver can Pull information from the data Sender/owner.
    - RECEIVER: Receiver Interface implementation. Interface implemented by the receiver of data, so the Sender/owner can Push information to the Receiver.
    '''
    SENDER = 'SENDER'
    RECEIVER = 'RECEIVER'



class OcpiCapabilityEnum(str, Enum):
    '''
    OCPI 8.4.3. Capability enum

    The capabilities of an EVSE.

    When a Charge Point supports ad-hoc payments with a payment terminal, please use a combination of the following values to
    explain the possibilities of the terminal: CHIP_CARD_SUPPORT, CONTACTLESS_CARD_SUPPORT, CREDIT_CARD_PAYABLE,
    DEBIT_CARD_PAYABLE, PED_TERMINAL.

    There are Charge Points in the field that do not yet support OCPP 2.x. If these Charge Points have multiple connectors per EVSE,
    the CPO needs to know which connector to start when receiving a StartSession for the given EVSE. If this is the case, the CPO
    should set the `START_SESSION_CONNECTOR_REQUIRED` capability on the given EVSE.
    '''
    CHARGING_PROFILE_CAPABLE = 'CHARGING_PROFILE_CAPABLE' # The EVSE supports charging profiles.
    CHARGING_PREFERENCES_CAPABLE = 'CHARGING_PREFERENCES_CAPABLE' # The EVSE supports charging profiles.
    CHIP_CARD_SUPPORT = 'CHIP_CARD_SUPPORT' # EVSE has a payment terminal that supports chip cards.
    CONTACTLESS_CARD_SUPPORT = 'CONTACTLESS_CARD_SUPPORT' # EVSE has a payment terminal that supports contactless cards.
    CREDIT_CARD_PAYABLE = 'CREDIT_CARD_PAYABLE' # EVSE has a payment terminal that makes it possible to pay for charging using a credit card.
    DEBIT_CARD_PAYABLE = 'DEBIT_CARD_PAYABLE' # EVSE has a payment terminal that makes it possible to pay for charging using a debit card.
    PED_TERMINAL = 'PED_TERMINAL' # EVSE has a payment terminal with a pin-code entry device.
    REMOTE_START_STOP_CAPABLE = 'REMOTE_START_STOP_CAPABLE' # The EVSE can remotely be started/stopped.
    RESERVABLE = 'RESERVABLE' # The EVSE can be reserved.
    RFID_READER = 'RFID_READER' # Charging at this EVSE can be authorized with an RFID token.
    START_SESSION_CONNECTOR_REQUIRED = 'START_SESSION_CONNECTOR_REQUIRED' # When a StartSession is sent to this EVSE, the MSP is required to add the optional connector_id field in the StartSession object.
    TOKEN_GROUP_CAPABLE = 'TOKEN_GROUP_CAPABLE' # This EVSE supports token groups, two or more tokens work as one, so that a session can be started with one token and stopped with another (handy when a card and key-fob are given to the EV-driver).
    UNLOCK_CAPABLE = 'UNLOCK_CAPABLE' # Connectors have mechanical lock that can be requested by the eMSP to be unlocked.



class OcpiConnectorFormatEnum(str, Enum):
    '''
    OCPI 8.4.4. ConnectorFormat enum
    '''
    SOCKET = 'SOCKET' # The connector is a socket; the EV user needs to bring a fitting plug.
    CABLE = 'CABLE' # The connector is an attached cable; the EV users car needs to have a fitting inlet.



class OcpiConnectorTypeEnum(str, Enum):
    '''
    OCPI 8.4.5. ConnectorType enum
    '''
    CHADEMO = 'CHADEMO' # The connector type is CHAdeMO, DC
    CHAOJI = 'CHAOJI' # The ChaoJi connector.
    DOMESTIC_A = 'DOMESTIC_A' # Standard/Domestic household, type "A", NEMA 1-15, 2 pins
    DOMESTIC_B = 'DOMESTIC_B' # Standard/Domestic household, type "B", NEMA 5-15, 3 pins
    DOMESTIC_C = 'DOMESTIC_C' # Standard/Domestic household, type "C", CEE 7/17, 2 pins
    DOMESTIC_D = 'DOMESTIC_D' # Standard/Domestic household, type "D", 3 pin
    DOMESTIC_E = 'DOMESTIC_E' # Standard/Domestic household, type "E", CEE 7/5 3 pins
    DOMESTIC_F = 'DOMESTIC_F' # Standard/Domestic household, type "F", CEE 7/4, Schuko, 3 pins
    DOMESTIC_G = 'DOMESTIC_G' # Standard/Domestic household, type "G", BS 1363, Commonwealth, 3 pins
    DOMESTIC_H = 'DOMESTIC_H' # Standard/Domestic household, type "H", SI-32, 3 pins
    DOMESTIC_I = 'DOMESTIC_I' # Standard/Domestic household, type "I", AS 3112, 3 pins
    DOMESTIC_J = 'DOMESTIC_J' # Standard/Domestic household, type "J", SEV 1011, 3 pins
    DOMESTIC_K = 'DOMESTIC_K' # Standard/Domestic household, type "K", DS 60884-2-D1, 3 pins
    DOMESTIC_L = 'DOMESTIC_L' # Standard/Domestic household, type "L", CEI 23-16-VII, 3 pins
    DOMESTIC_M = 'DOMESTIC_M' # Standard/Domestic household, type "M", BS 546, 3 pins
    DOMESTIC_N = 'DOMESTIC_N' # Standard/Domestic household, type "N", NBR 14136, 3 pins
    DOMESTIC_O = 'DOMESTIC_O' # Standard/Domestic household, type "O", TIS 166-2549, 3 pins
    GBT_AC = 'GBT_AC' # Guobiao GB/T 20234.2 AC socket/connector
    GBT_DC = 'GBT_DC' # Guobiao GB/T 20234.3 DC connector
    IEC_60309_2_single_16 = 'IEC_60309_2_single_16' # IEC 60309-2 Industrial Connector single phase 16 amperes (usually blue)
    IEC_60309_2_three_16 = 'IEC_60309_2_three_16' # IEC 60309-2 Industrial Connector three phases 16 amperes (usually red)
    IEC_60309_2_three_32 = 'IEC_60309_2_three_32' # IEC 60309-2 Industrial Connector three phases 32 amperes (usually red)
    IEC_60309_2_three_64 = 'IEC_60309_2_three_64' # IEC 60309-2 Industrial Connector three phases 64 amperes (usually red)
    IEC_62196_T1 = 'IEC_62196_T1' # IEC 62196 Type 1 "SAE J1772"
    IEC_62196_T1_COMBO = 'IEC_62196_T1_COMBO' # Combo Type 1 based, DC
    IEC_62196_T2 = 'IEC_62196_T2' # IEC 62196 Type 2 "Mennekes"
    IEC_62196_T2_COMBO = 'IEC_62196_T2_COMBO' # Combo Type 2 based, DC
    IEC_62196_T3A = 'IEC_62196_T3A' # IEC 62196 Type 3A
    IEC_62196_T3C = 'IEC_62196_T3C' # IEC 62196 Type 3C "Scame"
    NEMA_5_20 = 'NEMA_5_20' # NEMA 5-20, 3 pins
    NEMA_6_30 = 'NEMA_6_30' # NEMA 6-30, 3 pins
    NEMA_6_50 = 'NEMA_6_50' # NEMA 6-50, 3 pins
    NEMA_10_30 = 'NEMA_10_30' # NEMA 10-30, 3 pins
    NEMA_10_50 = 'NEMA_10_50' # NEMA 10-50, 3 pins
    NEMA_14_30 = 'NEMA_14_30' # NEMA 14-30, 3 pins, rating of 30 A
    NEMA_14_50 = 'NEMA_14_50' # NEMA 14-50, 3 pins, rating of 50 A
    PANTOGRAPH_BOTTOM_UP = 'PANTOGRAPH_BOTTOM_UP' # On-board Bottom-up-Pantograph typically for bus charging
    PANTOGRAPH_TOP_DOWN = 'PANTOGRAPH_TOP_DOWN' # Off-board Top-down-Pantograph typically for bus charging
    TESLA_R = 'TESLA_R' # Tesla Connector "Roadster"-type (round, 4 pin)
    TESLA_S = 'TESLA_S' # Tesla Connector "Model-S"-type (oval, 5 pin)



class OcpiEnergySourceCategoryEnum(str, Enum):
    '''
    OCPI 8.4.8. EnergySourceCategory enum
    '''
    NUCLEAR = 'NUCLEAR'
    GENERAL_FOSSIL = 'GENERAL_FOSSIL'
    COAL = 'COAL'
    GAS = 'GAS'
    GENERAL_GREEN = 'GENERAL_GREEN'
    SOLAR = 'SOLAR'
    WIND = 'WIND'
    WATER = 'WATER'



class OcpiEnvironmentalImpactCategoryEnum(str, Enum):
    '''
    OCPI 8.4.10. EnvironmentalImpactCategory enum
    '''
    NUCLEAR_WASTE = 'NUCLEAR_WASTE' # Produced nuclear waste in grams per kilowatthour.
    CARBON_DIOXIDE = 'CARBON_DIOXIDE' # Exhausted carbon dioxide in grams per kilowatthour.



class OcpiFacilityEnum(str, Enum):
    '''
    OCPI 8.4.12. Facility enum
    '''
    HOTEL = 'HOTEL'
    RESTAURANT = 'RESTAURANT'
    CAFE = 'CAFE'
    MALL = 'MALL'
    SUPERMARKET = 'SUPERMARKET'
    SPORT = 'SPORT'
    RECREATION_AREA = 'RECREATION_AREA'
    NATURE = 'NATURE'
    MUSEUM = 'MUSEUM'
    BIKE_SHARING = 'BIKE_SHARING'
    BUS_STOP = 'BUS_STOP'
    TAXI_STAND = 'TAXI_STAND'
    TRAM_STOP = 'TRAM_STOP'
    METRO_STATION = 'METRO_STATION'
    TRAIN_STATION = 'TRAIN_STATION'
    AIRPORT = 'AIRPORT'
    PARKING_LOT = 'PARKING_LOT'
    CARPOOL_PARKING = 'CARPOOL_PARKING'
    FUEL_STATION = 'FUEL_STATION'
    WIFI = 'WIFI'



class OcpiImageCategoryEnum(str, Enum):
    CHARGER = 'CHARGER'
    ENTRANCE = 'ENTRANCE'
    LOCATION = 'LOCATION'
    NETWORK = 'NETWORK'
    OPERATOR = 'OPERATOR'
    OTHER = 'OTHER'
    OWNER = 'OWNER'



class OcpiParkingRestrictionEnum(str, Enum):
    '''
    OCPI 8.4.17. ParkingRestriction enum
    '''
    EV_ONLY = 'EV_ONLY' # Reserved parking spot for electric vehicles.
    PLUGGED = 'PLUGGED' # Parking is only allowed while plugged in (charging).
    DISABLED = 'DISABLED' # Reserved parking spot for disabled people with valid ID.
    CUSTOMERS = 'CUSTOMERS' # Parking spot for customers/guests only, for example in case of a hotel or shop.
    MOTORCYCLES = 'MOTORCYCLES' # Parking spot only suitable for (electric) motorcycles or scooters.



class OcpiParkingTypeEnum(str, Enum):
    '''
    OCPI 8.4.18. ParkingType enum
    '''
    ALONG_MOTORWAY  = 'ALONG_MOTORWAY' # Location on a parking facility/rest area along a motorway, freeway, interstate, highway etc.
    PARKING_GARAGE = 'PARKING_GARAGE' # Multistorey car park.
    PARKING_LOT = 'PARKING_LOT' # A cleared area that is intended for parking vehicles, i.e. at super markets, bars, etc.
    ON_DRIVEWAY = 'ON_DRIVEWAY' # Location is on the driveway of a house/building.
    ON_STREET = 'ON_STREET' # Parking in public space along a street.
    UNDERGROUND_GARAGE = 'UNDERGROUND_GARAGE' # Multistorey car park, mainly underground.



class OcpiPowerTypeEnum(str, Enum):
    '''
    OCPI 8.4.19. PowerType enum
    '''
    AC_1_PHASE = 'AC_1_PHASE' # AC single phase.
    AC_2_PHASE = 'AC_2_PHASE' # AC two phases, only two of the three available phases connected.
    AC_2_PHASE_SPLIT = 'AC_2_PHASE_SPLIT' # AC two phases using split phase system.
    AC_3_PHASE = 'AC_3_PHASE' # AC three phases.
    DC = 'DC' # Direct Current.



class OcpiStatusEnum(str, Enum):
    '''
    OCPI 8.4.22. Status enum
    '''
    AVAILABLE = 'AVAILABLE' # The EVSE/Connector is able to start a new charging session.
    BLOCKED = 'BLOCKED' # The EVSE/Connector is not accessible because of a physical barrier, i.e. a car.
    CHARGING = 'CHARGING' # The EVSE/Connector is in use.
    INOPERATIVE = 'INOPERATIVE' # The EVSE/Connector is not yet active, or temporarily not available for use, but not broken or defect.
    OUTOFORDER = 'OUTOFORDER' # The EVSE/Connector is currently out of order, some part/components may be broken/defect.
    PLANNED = 'PLANNED' # The EVSE/Connector is planned, will be operating soon.
    REMOVED = 'REMOVED' # The EVSE/Connector was discontinued/removed.
    RESERVED = 'RESERVED' # The EVSE/Connector is reserved for a particular EV driver and is unavailable for other drivers.
    UNKNOWN = 'UNKNOWN' # No status information available (also used when offline).



class OcpiChargingPreferencesResponseEnum(str, Enum):
    '''
    OCPI 9.4.1. ChargingPreferencesResponse enum

    Different smart charging profile types.

    If a PUT with `ChargingPreferences` is received for an EVSE that does not have the capability
    `CHARGING_PREFERENCES_CAPABLE`, the receiver should respond with an HTTP status of 404 and an OCPI status code of 2001 in
    the OCPI response object.
    '''
    ACCEPTED = 'ACCEPTED' # Charging Preferences accepted, EVSE will try to accomplish them, although this is no guarantee that they will be fulfilled.
    DEPARTURE_REQUIRED = 'DEPARTURE_REQUIRED' # CPO requires `departure_time` to be able to perform Charging Preference based Smart Charging.
    ENERGY_NEED_REQUIRED = 'ENERGY_NEED_REQUIRED' # CPO requires `energy_need` to be able to perform Charging Preference based Smart Charging.
    NOT_POSSIBLE = 'NOT_POSSIBLE' # Charging Preferences contain a demand that the EVSE knows it cannot fulfill.
    PROFILE_TYPE_NOT_SUPPORTED = 'PROFILE_TYPE_NOT_SUPPORTED' # `profile_type` contains a value that is not supported by the EVSE.



class OcpiProfileTypeEnum(str, Enum):
    '''
    OCPI 9.4.2. ProfileType enum

    Different smart charging profile types.
    '''
    CHEAP = 'CHEAP ' # Driver wants to use the cheapest charging profile possible.
    FAST = 'FAST' # Driver wants his EV charged as quickly as possible and is willing to pay a premium for this, if needed.
    GREEN = 'GREEN' # Driver wants his EV charged with as much regenerative (green) energy as possible.
    REGULAR = 'REGULAR' # Driver does not have special preferences.



class OcpiSessionStatusEnum(str, Enum):
    '''
    OCPI 9.4.3. SessionStatus enum

    Defines the state of a session.
    '''
    ACTIVE = 'ACTIVE' # The session has been accepted and is active. All pre-conditions were met: Communication between EV and EVSE (for example: cable plugged in correctly), EV or driver is authorized. EV is being charged, or can be charged. Energy is, or is not, being transfered.
    COMPLETED = 'COMPLETED' # The session has been finished successfully. No more modifications will be made to the Session object using this state.
    INVALID = 'INVALID' # The Session object using this state is declared invalid and will not be billed.
    PENDING = 'PENDING' # The session is pending, it has not yet started. Not all pre-conditions are met. This is the initial state. The session might never become an _active_ session.
    RESERVATION = 'RESERVATION' # The session is started due to a reservation, charging has not yet started. The session might never become an _active_ session.



class OcpiAuthMethodEnum(str, Enum):
    '''
    OCPI 10.4.1. AuthMethod enum
    '''
    AUTH_REQUEST = 'AUTH_REQUEST' # Authentication request has been sent to the eMSP.
    COMMAND = 'COMMAND' # Command like StartSession or ReserveNow used to start the Session, the Token provided in the Command was used as authorization.
    WHITELIST = 'WHITELIST' # Whitelist used for authentication, no request to the eMSP has been performed.



class OcpiCdrDimensionTypeEnum(str, Enum):
    '''
    OCPI 10.4.3. CdrDimensionType enum

    This enumeration contains allowed values for CdrDimensions, which are used to define dimensions of ChargingPeriods in both
    `CDRs` and `Sessions`. Some of these values are not useful for `CDRs`, and SHALL therefor only be used in `Sessions`, these are
    marked in the column: Session Only

    NOTE: OCPI makes it possible to provide SoC in the Session object. This information can be useful to show the current
    State of Charge to an EV driver during charging. Implementers should be aware that SoC is only available at
    some DC Chargers. Which is currently a small amount of the total amount of Charge Points. Of these DC
    Chargers, only a small percentage currently provides SoC via OCPP to the CPO. Then there is also the question
    if SoC is allowed to be provided to third-parties as it can be seen as privacy-sensitive information. So if an
    implementer wants to show SoC in, for example an App, care should be taken, to make the App work without
    SoC, as this will probably not always be available.
    '''
    CURRENT = 'CURRENT' # Session Only # Average charging current during this ChargingPeriod: defined in A (Ampere). When negative, the current is flowing from the EV to the grid.
    ENERGY = 'ENERGY' # Total amount of energy (dis-)charged during this ChargingPeriod: defined in kWh. When negative, more energy was feed into the grid then charged into the EV. Default step_size 1.
    ENERGY_EXPORT = 'ENERGY_EXPORT' # Session Only # Total amount of energy feed back into the grid: defined in kWh.
    ENERGY_IMPORT = 'ENERGY_IMPORT' # Session Only # Total amount of energy charged, defined in kWh.
    MAX_CURRENT = 'MAX_CURRENT' # Sum of the maximum current over all phases, reached during this ChargingPeriod: defined in A (Ampere)
    MIN_CURRENT = 'MIN_CURRENT' # Sum of the minimum current over all phases, reached during this ChargingPeriod, when negative, current has flowed from the EV to the grid. Defined in A (Ampere).
    MAX_POWER = 'MAX_POWER' # Maximum power reached during this ChargingPeriod: defined in kW (Kilowatt).
    MIN_POWER = 'MIN_POWER' # Minimum power reached during this ChargingPeriod: defined in kW (Kilowatt), when negative, the power has flowed from the EV to the grid.
    PARKING_TIME = 'PARKING_TIME' # Time during this ChargingPeriod not charging: defined in hours, default step_size multiplier is 1 second.
    POWER = 'POWER' # Session Only # Average power during this ChargingPeriod: defined in kW (Kilowatt). When negative, the power is flowing from the EV to the grid.
    RESERVATION_TIME = 'RESERVATION_TIME' # Time during this ChargingPeriod Charge Point has been reserved and not yet been in use for this customer: defined in hours, default step_size multiplier is 1 second.
    STATE_OF_CHARGE = 'STATE_OF_CHARGE' # Session Only # Current state of charge of the EV, in percentage, values allowed: 0 to 100. See note below.
    TIME = 'TIME' # Time charging during this ChargingPeriod: defined in hours, default step_size multiplier is 1 second.



class OcpiDayOfWeekEnum(str, Enum):
    '''
    OCPI 11.4.1. DayOfWeek enum
    '''
    MONDAY = 'MONDAY' # Monday
    TUESDAY = 'TUESDAY' # Tuesday
    WEDNESDAY = 'WEDNESDAY' # Wednesday
    THURSDAY = 'THURSDAY' # Thursday
    FRIDAY = 'FRIDAY' # Friday
    SATURDAY = 'SATURDAY' # Saturday
    SUNDAY = 'SUNDAY' # Sunday



class OcpiReservationRestrictionTypeEnum(str, Enum):
    '''
    OCPI 11.4.3. ReservationRestrictionType enum

    NOTE: When a Tariff has both, `RESERVATION` and `RESERVATION_EXPIRES` TariffElements, where both TariffElements
    have a TIME PriceComponent, then the time based cost of an expired reservation will be calculated based on the
    `RESERVATION_EXPIRES` TariffElement.
    '''
    RESERVATION = 'RESERVATION' # Used in TariffElements to describe costs for a reservation.
    RESERVATION_EXPIRES = 'RESERVATION_EXPIRES' # Used in TariffElements to describe costs for a reservation that expires (i.e. driver does not start a charging session before expiry_date of the reservation).


class OcpiTariffDimensionTypeEnum(str, Enum):
    '''
    OCPI 11.4.5. TariffDimensionType enum
    '''
    ENERGY = 'ENERGY' # Defined in kWh, `step_size` multiplier: 1 Wh
    FLAT = 'FLAT' # Flat fee without unit for `step_size`
    PARKING_TIME = 'PARKING_TIME' # Time not charging: defined in hours, `step_size` multiplier: 1 second
    TIME = 'TIME' # Time charging: defined in hours, `step_size` multiplier: 1 second Can also be used in combination with a RESERVATION restriction to describe the price of the reservation time.



class OcpiTariffTypeEnum(str, Enum):
    '''
    OCPI 11.4.7. TariffType enum
    '''
    AD_HOC_PAYMENT = 'AD_HOC_PAYMENT' # Used to describe that a Tariff is valid when ad-hoc payment is used at the Charge Point (for example: Debit or Credit card payment terminal).
    PROFILE_CHEAP = 'PROFILE_CHEAP' # Used to describe that a Tariff is valid when Charging Preference: CHEAP is set for the session.
    PROFILE_FAST = 'PROFILE_FAST' # Used to describe that a Tariff is valid when Charging Preference: FAST is set for the session.
    PROFILE_GREEN = 'PROFILE_GREEN' # Used to describe that a Tariff is valid when Charging Preference: GREEN is set for the session.
    REGULAR = 'REGULAR' # Used to describe that a Tariff is valid when using an RFID, without any Charging Preference, or when Charging Preference: REGULAR is set for the session.



class OcpiAllowedTypeEnum(str, Enum):
    '''
    OCPI 12.4.1. AllowedType enum
    '''
    ALLOWED = 'ALLOWED' # This Token is allowed to charge (at this location).
    BLOCKED = 'BLOCKED' # This Token is blocked.
    EXPIRED = 'EXPIRED' # This Token has expired.
    NO_CREDIT = 'NO_CREDIT' # This Token belongs to an account that has not enough credits to charge (at the given location).
    NOT_ALLOWED = 'NOT_ALLOWED' # Token is valid, but is not allowed to charge at the given location.



class OcpiTokenTypeEnum(str, Enum):
    '''
    OCPI 12.4.4. TokenType enum

    NOTE: The eMSP is RECOMMENDED to push Tokens with type: `AD_HOC_USER` or `APP_USER` with `whitelist` set to
    `NEVER`. Whitelists are very useful for RFID type Tokens, but the `AD_HOC_USER`/`APP_USER` Tokens are used to
    start Sessions from an App etc. so whitelisting them has no advantages.
    '''
    AD_HOC_USER = 'AD_HOC_USER' # One time use Token ID generated by a server (or App.)
    APP_USER = 'APP_USER' # Token ID generated by a server (or App.) to identify a user of an App.
    OTHER = 'OTHER' # Other type of token
    RFID = 'RFID' # RFID



class OcpiWhitelistTypeEnum(str, Enum):
    '''
    OCPI 12.4.5. WhitelistType enum

    Defines when authorization of a Token by the CPO is allowed.

    The validity of a Token has no influence on this. If a Token is: `valid = false`, when the `whitelist` field requires real-time
    authorization, the CPO SHALL do a real-time authorization, the state of the Token might have changed.
    '''
    ALWAYS = 'ALWAYS' # Token always has to be whitelisted, realtime authorization is not possible/allowed. CPO shall always allow any use of this Token.
    ALLOWED = 'ALLOWED' # It is allowed to whitelist the token, realtime authorization is also allowed. The CPO may choose which version of authorization to use.
    ALLOWED_OFFLINE = 'ALLOWED_OFFLINE' # In normal situations realtime authorization shall be used. But when the CPO cannot get a response from the eMSP (communication between CPO and eMSP is offline), the CPO shall allow this Token to be used.
    NEVER = 'NEVER' # Whitelisting is forbidden, only realtime authorization is allowed. CPO shall always send a realtime authorization for any use of this Token to the eMSP.



class OcpiCommandResponseTypeEnum(str, Enum):
    '''
    OCPI 13.4.1. CommandResponseType enum

    Response to the command request from the eMSP to the CPO.
    '''
    NOT_SUPPORTED = 'NOT_SUPPORTED' # The requested command is not supported by this CPO, Charge Point, EVSE etc.
    REJECTED = 'REJECTED' # Command request rejected by the CPO. (Session might not be from a customer of the eMSP that send this request)
    ACCEPTED = 'ACCEPTED' # Command request accepted by the CPO.
    UNKNOWN_SESSION = 'UNKNOWN_SESSION' # The Session in the requested command is not known by this CPO.



class OcpiCommandResultTypeEnum(str, Enum):
    '''
    OCPI 13.4.2. CommandResultType enum

    Result of the command that was send to the Charge Point.
    '''
    ACCEPTED = 'ACCEPTED' # Command request accepted by the CPO.
    CANCELED_RESERVATION = 'CANCELED_RESERVATION' # The Reservation has been canceled by the CPO.
    EVSE_OCCUPIED = 'EVSE_OCCUPIED' # EVSE is currently occupied, another session is ongoing. Cannot start a new session
    EVSE_INOPERATIVE = 'EVSE_INOPERATIVE' # EVSE is currently inoperative or faulted.
    FAILED = 'FAILED' # Execution of the command failed at the Charge Point.
    NOT_SUPPORTED = 'NOT_SUPPORTED' # The requested command is not supported by this Charge Point, EVSE etc.
    REJECTED = 'REJECTED' # Command request rejected by the Charge Point.
    TIMEOUT= 'TIMEOUT' # Command request timeout, no response received from the Charge Point in a reasonable time.
    UNKNOWN_RESERVATION = 'UNKNOWN_RESERVATION' # The Reservation in the requested command is not known by this Charge Point.



class OcpiCommandTypeEnum(str, Enum):
    '''
    OCPI 13.4.3. CommandType enum

    **The command UNLOCK_CONNECTOR may only be used by an operator or the eMSP. This command SHALL never be allowed
    to be sent directly by the EV-Driver. The UNLOCK_CONNECTOR is intended to be used in the rare situation that the connector
    is not unlocked successfully after a transaction is stopped. The mechanical unlock of the lock mechanism might get
    stuck, for example: fail when there is tension on the charging cable when the Charge Point tries to unlock the connector.
    In such a situation the EV-Driver can call either the CPO or the eMSP to retry the unlocking.**
    '''
    CANCEL_RESERVATION  = 'CANCEL_RESERVATION ' # Request the Charge Point to cancel a specific reservation.
    RESERVE_NOW = 'RESERVE_NOW' # Request the Charge Point to reserve a (specific) EVSE for a Token for a certain time, starting now.
    START_SESSION = 'START_SESSION' # Request the Charge Point to start a transaction on the given EVSE/Connector.
    STOP_SESSION = 'STOP_SESSION' # Request the Charge Point to stop an ongoing session.
    UNLOCK_CONNECTOR = 'UNLOCK_CONNECTOR' # Request the Charge Point to unlock the connector (if applicable). This functionality is for help desk operators only!
