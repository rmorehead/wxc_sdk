"""
Common date types and APIs
"""
from datetime import datetime
from typing import Optional, Any

from pydantic import Field, root_validator, validator

from ..base import ApiModel, webex_id_to_uuid
from ..base import SafeEnum as Enum

__all__ = ['UserType', 'UserBase', 'RingPattern', 'AlternateNumber', 'Greeting', 'UserNumber', 'PersonPlaceAgent',
           'MonitoredMember', 'CallParkExtension', 'AuthCode', 'RouteType', 'DialPatternValidate', 'DialPatternStatus',
           'RouteIdentity', 'Customer', 'IdOnly', 'IdAndName', 'PatternAction', 'NumberState', 'ValidationStatus',
           'ValidateExtensionStatusState', 'ValidateExtensionStatus', 'ValidateExtensionsResponse',
           'ValidatePhoneNumberStatusState', 'ValidatePhoneNumberStatus', 'ValidatePhoneNumbersResponse', 'StorageType',
           'VoicemailMessageStorage', 'VoicemailEnabled', 'VoicemailNotifications', 'VoicemailFax',
           'VoicemailTransferToNumber', 'VoicemailCopyOfMessage', 'AudioCodecPriority', 'AtaDtmfMode', 'AtaDtmfMethod',
           'VlanSetting', 'AtaCustomization', 'DeviceCustomizations', 'DeviceCustomization',
           'CommonDeviceCustomization', 'BacklightTimer', 'Background', 'BackgroundSelection', 'DisplayNameSelection',
           'LoggingLevel', 'DisplayCallqueueAgentSoftkey', 'AcdCustomization', 'LineKeyLabelSelection',
           'LineKeyLedPattern', 'PhoneLanguage', 'EnabledAndValue', 'WifiNetwork', 'MppCustomization',
           'PrimaryOrShared',
           'MediaFileType', 'AnnAudioFile', 'WifiCustomization', 'RoomType', 'LinkRelation', 'AnnouncementLevel',
           'UsbPortsObject', 'WifiAuthenticationMethod', 'DirectoryMethod', 'CallHistoryMethod', 'MppVlanDevice',
           'VolumeSettings', 'CallForwardExpandedSoftKey', 'HttpProxy', 'HttpProxyMode', 'BluetoothMode',
           'BluetoothSetting', 'NoiseCancellation', 'SoftKeyLayout', 'SoftKeyMenu', 'PskObject', 'BackgroundImageColor',
           'BacklightTimer68XX78XX', 'DectCustomization']


class IdOnly(ApiModel):
    id: str


class IdAndName(IdOnly):
    name: str


class LinkRelation(ApiModel):
    #: Link relation describing how the target resource is related to the current context (conforming with RFC5998).
    rel: Optional[str]
    #: Target resource URI (conforming with RFC5998).
    href: Optional[str]
    #: Target resource method (conforming with RFC5998).
    method: Optional[str]


class RoomType(str, Enum):
    #: 1:1 room.
    direct = 'direct'
    #: Group room.
    group = 'group'


class UserType(str, Enum):
    people = 'PEOPLE'
    place = 'PLACE'
    virtual_line = 'VIRTUAL_LINE'


class UserBase(ApiModel):
    first_name: Optional[str]
    last_name: Optional[str]
    user_type: Optional[UserType] = Field(alias='type')


class RingPattern(str, Enum):
    """
    Ring Pattern
    """
    #: Normal incoming ring pattern.
    normal = 'NORMAL'
    #: Incoming ring pattern of two long rings.
    long_long = 'LONG_LONG'
    #: Incoming ring pattern of two short rings, followed by a short ring.
    short_short_long = 'SHORT_SHORT_LONG'
    #: Incoming ring pattern of a short ring, followed by a long ring, followed by a short ring.
    short_long_short = 'SHORT_LONG_SHORT'


class AlternateNumber(ApiModel):
    """
    Hunt group or call queue alternate number
    """
    #: Alternate phone number for the hunt group or call queue
    phone_number: Optional[str]
    #: Ring pattern for when this alternate number is called. Only available when distinctiveRing is enabled for the
    #: hunt group.
    ring_pattern: Optional[RingPattern]
    #: Flag: phone_number is a toll free number
    toll_free_number: Optional[bool]


class Greeting(str, Enum):
    """
    DEFAULT indicates that a system default message will be placed when incoming calls are intercepted.
    """
    #: A custom will be placed when incoming calls are intercepted.
    custom = 'CUSTOM'
    #: A System default message will be placed when incoming calls are intercepted.
    default = 'DEFAULT'


class UserNumber(ApiModel):
    """
    phone number of the person or workspace.
    """
    #: Phone number of person or workspace. Either phoneNumber or extension is mandatory
    external: Optional[str]
    #: Extension of person or workspace. Either phoneNumber or extension is mandatory.
    extension: Optional[str]
    #: Flag to indicate primary phone.
    primary: Optional[bool]


class PersonPlaceAgent(UserBase):
    """
    Agent (person or place)
    """
    #: ID of person or workspace.
    agent_id: str = Field(alias='id')
    #: Display name of person or workspace.
    display_name: Optional[str]
    #: Email of the person or workspace.
    email: Optional[str]
    #: List of phone numbers of the person or workspace.
    numbers: Optional[list[UserNumber]]
    location: Optional[IdAndName]


class MonitoredMember(ApiModel):
    """
    a monitored user or place
    """
    #: The identifier of the monitored person.
    member_id: Optional[str] = Field(alias='id')
    #: The last name of the monitored person or place.
    last_name: Optional[str]
    #: The first name of the monitored person or place.
    first_name: Optional[str]
    #: The display name of the monitored person or place.
    display_name: Optional[str]
    #: Indicates whether type is PEOPLE or PLACE.
    member_type: Optional[UserType] = Field(alias='type')
    #: The email address of the monitored person or place.
    email: Optional[str]
    #: The list of phone numbers of the monitored person or place.
    numbers: Optional[list[UserNumber]]

    @property
    def ci_member_id(self) -> Optional[str]:
        return self.member_id and webex_id_to_uuid(self.member_id)


class CallParkExtension(ApiModel):
    #: The identifier of the call park extension.
    cpe_id: Optional[str] = Field(alias='id')
    #: The name to describe the call park extension.
    name: Optional[str]
    #: The extension number for this call park extension.
    extension: Optional[str]
    #: The location name where the call park extension is.
    location_name: Optional[str]
    #: The location ID for the location.
    location_id: Optional[str]

    @root_validator(pre=True)
    def fix_location_name(cls, values):
        """

        :meta private:
        :param values:
        :return:
        """
        location = values.pop('location', None)
        if location is not None:
            values['location_name'] = location
        return values

    @property
    def ci_cpe_id(self) -> Optional[str]:
        """
        call park extension ID as UUID
        """
        return self.cpe_id and webex_id_to_uuid(self.cpe_id)


class AuthCode(ApiModel):
    """
    authorization code and description.
    """
    #: Indicates an authorization code.
    code: str
    #: Indicates the description of the authorization code.
    description: str


class RouteType(str, Enum):
    #: Route group must include at least one trunk with a maximum of 10 trunks per route group.
    route_group = 'ROUTE_GROUP'
    # Connection between Webex Calling and the premises.
    trunk = 'TRUNK'


class DialPatternStatus(str, Enum):
    """
    validation status.
    """
    #: invalid pattern
    invalid = 'INVALID'
    #: duplicate pattern
    duplicate = 'DUPLICATE'
    #: duplicate in input
    duplicate_in_list = 'DUPLICATE_IN_LIST'


class DialPatternValidate(ApiModel):
    #: input dial pattern that is being validate
    dial_pattern: str
    #: validation status.
    pattern_status: DialPatternStatus
    #: failure details.
    message: str


class RouteIdentity(ApiModel):
    route_id: str = Field(alias='id')
    name: Optional[str]
    route_type: RouteType = Field(alias='type')


class Customer(ApiModel):
    """
    Customer information.
    """
    #: ID of the customer/organization.
    customer_id: str = Field(alias='id')
    #: Name of the customer/organization.
    name: str


class PatternAction(str, Enum):
    #: add action, when adding a new dial pattern
    add = 'ADD'
    #: delete action, when deleting an existing dial pattern
    delete = 'DELETE'


class NumberState(str, Enum):
    active = 'ACTIVE'
    inactive = 'INACTIVE'


class ValidationStatus(str, Enum):
    ok = 'OK'
    errors = 'ERRORS'


class ValidateExtensionStatusState(str, Enum):
    valid = 'VALID'
    duplicate = 'DUPLICATE'
    duplicate_in_list = 'DUPLICATE_IN_LIST'
    invalid = 'INVALID'


class ValidateExtensionStatus(ApiModel):
    #: Indicates the extension id for which the status is about .
    extension: str
    #: Indicate the status for the given extension id .
    state: ValidateExtensionStatusState
    #: Error Code .
    error_code: Optional[int]
    message: Optional[str]

    @property
    def ok(self):
        return self.state == ValidateExtensionStatusState.valid


class ValidateExtensionsResponse(ApiModel):
    status: ValidationStatus
    extension_status: Optional[list[ValidateExtensionStatus]]

    @property
    def ok(self) -> bool:
        return self.status == ValidationStatus.ok


class ValidatePhoneNumberStatusState(str, Enum):
    #: This means the phone number is available.
    available = 'Available'
    #: This means it's a duplicate phone number.
    duplicate = 'Duplicate'
    #: This means it's a duplicate phone number in the list.
    duplicate_in_list = 'Duplicate In List'
    #: The phone number is invalid.
    invalid = 'Invalid'
    #: This phone number is unavailable and cannot be used.
    unavailable = 'Unavailable'


class ValidatePhoneNumberStatus(ApiModel):
    #: Phone number that need to be validated.
    phone_number: str
    #: This indicates the state of the number.
    state: ValidatePhoneNumberStatusState
    #: This indicated whether it's a toll-free number
    toll_free_number: bool
    #: This field has the details if error if the number is unavailable.
    detail: list[str] = Field(default_factory=list)

    @property
    def ok(self):
        return self.state == ValidatePhoneNumberStatusState.available


class ValidatePhoneNumbersResponse(ApiModel):
    #: This indicates the status of the numbers.
    status: ValidationStatus
    #: This is an array of number objects with number details.
    phone_numbers: Optional[list[ValidatePhoneNumberStatus]]

    @property
    def ok(self) -> bool:
        return self.status == ValidationStatus.ok


class StorageType(str, Enum):
    """
    Designates which type of voicemail message storage is used.
    """
    #: For message access via phone or the Calling User Portal.
    internal = 'INTERNAL'
    #: For sending all messages to the person's email.
    external = 'EXTERNAL'


class VoicemailMessageStorage(ApiModel):
    """
    Settings for message storage
    """
    #: When true desktop phone will indicate there are new voicemails.
    mwi_enabled: Optional[bool]
    #: Designates which type of voicemail message storage is used.
    storage_type: Optional[StorageType]
    #: External email address to which the new voicemail audio will be sent. A value for this field must be provided
    # in the request if a storageType of EXTERNAL is given in the request.
    external_email: Optional[str]


class VoicemailEnabled(ApiModel):
    enabled: bool


class VoicemailNotifications(VoicemailEnabled):
    """
    Settings for notifications when there are any new voicemails.
    """
    #: Email address to which the notification will be sent. For text messages, use an email to text message gateway
    #: like 2025551212@txt.att.net.
    destination: Optional[str]


class VoicemailFax(VoicemailEnabled):
    """
    Fax message settings
    """
    #: Designates optional extension for fax.
    extension: Optional[str]
    #: Designates phone number for fax. A value for this field must be provided in the request if faxMessage enabled
    #: field is given as true in the request.
    phone_number: Optional[str]


class VoicemailTransferToNumber(VoicemailEnabled):
    """
    Settings for voicemail caller to transfer to a different number by pressing zero (0).
    """
    #: Number voicemail caller will be transferred to when they press zero (0).
    destination: Optional[str]


class VoicemailCopyOfMessage(VoicemailEnabled):
    """
    Settings for sending a copy of new voicemail message audio via email.
    """
    #: Email address to which the new voicemail audio will be sent.
    email_id: Optional[str]


class AudioCodecPriority(ApiModel):
    """
    Choose up to three predefined codec priority options available for your region.
    """
    #: Indicates the selection of an Audio Code Priority Object.
    selection: str
    #: Indicates the primary Audio Codec.
    primary: Optional[str]
    #: Indicates the secondary Audio Codec.
    secondary: Optional[str]
    #: Indicates the tertiary Audio Codec.
    tertiary: Optional[str]


class AtaDtmfMode(str, Enum):
    """
    DTMF Detection Tx Mode selection for Cisco ATA devices.
    """
    #: It means a) DTMF digit requires an extra hold time after detection and b) DTMF level threshold is raised to
    #: -20 dBm.
    strict = 'STRICT'
    #: It means normal threshold mode.
    normal = 'NORMAL'


class AtaDtmfMethod(str, Enum):
    """
    Method for transmitting DTMF signals to the far end.
    """
    #: Sends DTMF by using the audio path.
    inband = 'INBAND'
    #: Audio video transport. Sends DTMF as AVT events.
    avt = 'AVT'
    auto = 'AUTO'


class VlanSetting(ApiModel):
    #: Denotes whether the VLAN object is enabled
    enabled: bool
    #: The value of the VLAN Object
    value: int
    #: Indicates the PC port value of a VLAN object for an MPP object
    pc_port: Optional[int]


class CommonDeviceCustomization(ApiModel):
    #: Choose up to three predefined codec priority options available for your region.
    audio_codec_priority: AudioCodecPriority
    #: Enable/disable Cisco Discovery Protocol for local devices.
    cdp_enabled: bool
    #: Enable/disable Link Layer Discovery Protocol for local devices.
    lldp_enabled: bool
    #: Enable/disable quality of service tagging of packets from the local device to the Webex Calling platform.
    qos_enabled: bool
    #: Specify a numeric Virtual LAN ID for devices.
    vlan: VlanSetting
    #: Enable/disable automatic nightly configuration resync of the device.
    nightly_resync_enabled: Optional[bool]


class AtaCustomization(CommonDeviceCustomization):
    """
    settings that are applicable to ATA devices.
    """
    #: DTMF Detection Tx Mode selection for Cisco ATA devices.
    ata_dtmf_mode: AtaDtmfMode
    #: Method for transmitting DTMF signals to the far end.
    ata_dtmf_method: AtaDtmfMethod
    snmp: dict
    #: Enable/disable user level web access to the local device.
    web_access_enabled: bool


class DectCustomization(CommonDeviceCustomization):
    #: Enable/disable user level web access to the local device.
    web_access_enabled: bool


class BacklightTimer(str, Enum):
    one_min = 'ONE_MIN'
    five_min = 'FIVE_MIN'
    thirty_min = 'THIRTY_MIN'
    always_on = 'ALWAYS_ON'


class BacklightTimer68XX78XX(str, Enum):
    #: Keep the phone's backlight always on.
    always_on = 'ALWAYS_ON'
    #: Set the phone's backlight to be on for ten seconds.
    ten_sec = 'TEN_SEC'
    #: Set the phone's backlight to be on for twenty seconds.
    twenty_sec = 'TWENTY_SEC'
    #: Set the phone's backlight to be on for thirty seconds.
    thirty_sec = 'THIRTY_SEC'
    #: Keep the phone's backlight off.
    off = 'OFF'


class BacklightTimer(str, Enum):
    one_min = 'ONE_MIN'
    five_min = 'FIVE_MIN'
    thirty_min = 'THIRTY_MIN'
    always_on = 'ALWAYS_ON'


class Background(str, Enum):
    #: Indicates that there will be no background image set for the devices.
    no_background = 'NONE'
    #: Indicates that dark blue background image will be set for the devices.
    dark_blue = 'DARK_BLUE'
    #: Indicates that Cisco themed dark blue background image will be set for the devices.
    cisco_dark_blue = 'CISCO_DARK_BLUE'
    #: Indicates that Cisco webex dark blue background image will be set for the devices.
    webex_dark_blue = 'WEBEX_DARK_BLUE'
    #: Indicates that a custom background image will be set for the devices.
    custom_background = 'CUSTOM_BACKGROUND'


class BackgroundSelection(ApiModel):
    """
    Background selection for MPP devices
    """
    image: Background
    custom_url: Optional[str]


class DisplayNameSelection(str, Enum):
    #: Indicates that devices will display the person’s phone number, or if a person doesn’t have a phone number, the
    #: location number will be displayed.
    person_number = 'PERSON_NUMBER'
    #: Indicates that devices will display the name in first name then last name format.
    person_first_then_last_name = 'PERSON_FIRST_THEN_LAST_NAME'
    #: Indicates that devices will display the name in last name then first name format.
    person_last_then_first_name = 'PERSON_LAST_THEN_FIRST_NAME'


class LoggingLevel(str, Enum):
    #: Enables standard logging.
    standard = 'STANDARD'
    #: Enables detailed debugging logging.
    debugging = 'DEBUGGING'


class DisplayCallqueueAgentSoftkey(str, Enum):
    """
    Chooses the location of the Call Queue Agent Login/Logout softkey on Multi-Platform Phones.
    """
    front_page = 'FRONT_PAGE'
    last_page = 'LAST_PAGE'


class AcdCustomization(ApiModel):
    #: Indicates whether the ACD object is enabled.
    enabled: bool
    #: Indicates the call queue agent soft key value of an ACD object.
    display_callqueue_agent_softkeys: str


class LineKeyLabelSelection(str, Enum):
    """
    Line key labels define the format of what’s shown next to line keys.
    """
    #: This will display the person extension, or if a person doesn’t have an extension, the person’s first name will
    #: be displayed.
    person_extension = 'PERSON_EXTENSION'
    #: Indicates that devices will display the name in first name then last name format.
    person_first_then_last_name = 'PERSON_FIRST_THEN_LAST_NAME'
    #: Indicates that devices will display the name in last name then first name format.
    person_last_then_first_name = 'PERSON_LAST_THEN_FIRST_NAME'


class LineKeyLedPattern(str, Enum):
    default = 'DEFAULT'
    preset_1 = 'PRESET_1'


class PhoneLanguage(str, Enum):
    #: Indicates a person's announcement language.
    person = 'PERSON_LANGUAGE'
    arabic = 'ARABIC'
    bulgarian = 'BULGARIAN'
    catalan = 'CATALAN'
    chinese_simplified = 'CHINESE_SIMPLIFIED'
    chinese_traditional = 'CHINESE_TRADITIONAL'
    croatian = 'CROATIAN'
    czech = 'CZECH'
    danish = 'DANISH'
    dutch = 'DUTCH'
    english_united_states = 'ENGLISH_UNITED_STATES'
    english_united_kingdom = 'ENGLISH_UNITED_KINGDOM'
    finnish = 'FINNISH'
    french_canada = 'FRENCH_CANADA'
    french_france = 'FRENCH_FRANCE'
    german = 'GERMAN'
    greek = 'GREEK'
    hebrew = 'HEBREW'
    hungarian = 'HUNGARIAN'
    italian = 'ITALIAN'
    japanese = 'JAPANESE'
    korean = 'KOREAN'
    norwegian = 'NORWEGIAN'
    polish = 'POLISH'
    portuguese_portugal = 'PORTUGUESE_PORTUGAL'
    russian = 'RUSSIAN'
    spanish_colombia = 'SPANISH_COLOMBIA'
    spanish_spain = 'SPANISH_SPAIN'
    slovak = 'SLOVAK'
    swedish = 'SWEDISH'
    slovenian = 'SLOVENIAN'
    turkish = 'TURKISH'
    ukraine = 'UKRAINE'


class EnabledAndValue(ApiModel):
    enabled: bool
    value: int


class WifiNetwork(ApiModel):
    """
    Specify the Wi-Fi SSID and password for wireless-enabled MPP phones.
    """
    #: Indicates whether the wifi network is enabled.
    enabled: bool
    #: Authentication method of wifi network.
    authentication_method: str
    #: SSID name of the wifi network.
    ssid_name: Optional[str]
    #: User ID of the wifi network.
    user_id: Optional[str]


class UsbPortsObject(ApiModel):
    #: New Control to Enable/Disable the side USB port.
    enabled: Optional[bool]
    #: Enable/disable use of the side USB port on the MPP device. Enabled by default.
    side_usb_enabled: Optional[bool]
    #: Enable/disable use of the rear USB port on the MPP device.
    rear_usb_enabled: Optional[bool]


class MppVlanDevice(EnabledAndValue):
    #: Indicates the PC port value of a VLAN object for an MPP object.
    pc_port: Optional[int]


class WifiAuthenticationMethod(str, Enum):
    #: No authentication.
    none = 'NONE'
    #: Extensible Authentication Protocol-Flexible Authentication via Secure Tunneling. Requires username and 
    # password authentication.
    eap_fast = 'EAP_FAST'
    #: Protected Extensible Authentication Protocol - Generic Token Card. Requires username and password authentication.
    peap_gtc = 'PEAP_GTC'
    #: Protected Extensible Authentication Protocol - Microsoft Challenge Handshake Authentication Protocol version 
    # 2. Requires username and password authentication.
    peap_mschapv2 = 'PEAP_MSCHAPV2'
    #: Pre-Shared Key. Requires shared passphrase for authentication.
    psk = 'PSK'
    #: Wired Equivalent Privacy. Requires encryption key for authentication.
    wep = 'WEP'


class CallHistoryMethod(str, Enum):
    #: Set call history to use the unified call history from all of the end user's devices.
    unified = 'WEBEX_UNIFIED_CALL_HISTORY'
    #: Set call history to use local device information only.
    local = 'LOCAL_CALL_HISTORY'


class DirectoryMethod(str, Enum):
    #: Set directory services to use standard XSI query method from the device.
    xsi_directory = 'XSI_DIRECTORY'
    #: Set directory services to use the Webex Enterprise directory.
    webex_directory = 'WEBEX_DIRECTORY'


class VolumeSettings(ApiModel):
    #: Specify a ringer volume level through a numeric value between 0 and 15.
    ringer_volume: Optional[int]
    #: Specify a speaker volume level through a numeric value between 0 and 15.
    speaker_volume: Optional[int]
    #: Specify a handset volume level through a numeric value between 0 and 15.
    handset_volume: Optional[int]
    #: Specify a headset volume level through a numeric value between 0 and 15.
    headset_volume: Optional[int]
    #: Enable/disable the wireless headset hookswitch control.
    e_hook_enabled: Optional[bool]
    #: Enable/disable to preserve the existing values on the phone and not the values defined for the device settings.
    allow_end_user_override_enabled: Optional[bool]


class CallForwardExpandedSoftKey(str, Enum):
    #: Set the default call forward expanded soft key behavior to single option.
    only_the_call_forward_all = 'ONLY_THE_CALL_FORWARD_ALL'
    #: Set the default call forward expanded soft key behavior to multiple menu option.
    all_call_forwards = 'ALL_CALL_FORWARDS'


class HttpProxyMode(str, Enum):
    off = 'OFF'
    auto = 'AUTO'
    manual = 'MANUAL'


class HttpProxy(ApiModel):
    #: Mode of the HTTP proxy.
    mode: Optional[HttpProxyMode]
    #: Enable/disable auto discovery of the URL.
    auto_discovery_enabled: Optional[bool]
    #: Specify the host URL if the HTTP mode is set to MANUAL.
    host: Optional[str]
    #: Specify the port if the HTTP mode is set to MANUAL.
    port: Optional[str]
    #: Specify PAC URL if auto discovery is disabled.
    pack_url: Optional[str]
    #: Enable/disable authentication settings.
    auth_settings_enabled: Optional[bool]
    #: Specify a username if authentication settings are enabled.
    username: Optional[str]
    #: Specify a password if authentication settings are enabled.
    password: Optional[str]


class BluetoothMode(str, Enum):
    phone = 'PHONE'
    hands_free = 'HANDS_FREE'
    both = 'BOTH'


class BluetoothSetting(ApiModel):
    #: Enable/disable Bluetooth.
    enabled: Optional[bool]
    #: Select a Bluetooth mode.
    mode: Optional[BluetoothMode]


class NoiseCancellation(ApiModel):
    #: Enable/disable the Noise Cancellation.
    enabled: Optional[bool]
    #: Enable/disable to preserve the existing values on the phone and not the value defined for the device setting.
    allow_end_user_override_enabled: Optional[bool]


class SoftKeyMenu(ApiModel):
    #: Specify the idle key list.
    idle_key_list: Optional[str]
    #: Specify the off hook key list.
    off_hook_key_list: Optional[str]
    #: Specify the dialing input key list.
    dialing_input_key_list: Optional[str]
    #: Specify the progressing key list.
    progressing_key_list: Optional[str]
    #: Specify the connected key list.
    connected_key_list: Optional[str]
    #: Specify the connected video key list.
    connected_video_key_list: Optional[str]
    #: Start the transfer key list.
    start_transfer_key_list: Optional[str]
    #: Start the conference key list.
    start_conference_key_list: Optional[str]
    #: Specify the conferencing key list.
    conferencing_key_list: Optional[str]
    #: Specify the releasing key list.
    releasing_key_list: Optional[str]
    #: Specify the hold key list.
    hold_key_list: Optional[str]
    #: Specify the ringing key list.
    ringing_key_list: Optional[str]
    #: Specify the shared active key list.
    shared_active_key_list: Optional[str]
    #: Specify the shared held key list.
    shared_held_key_list: Optional[str]


class PskObject(ApiModel):
    #: Specify PSK1.
    psk1: Optional[str]
    #: Specify PSK2.
    psk2: Optional[str]
    #: Specify PSK3.
    psk3: Optional[str]
    #: Specify PSK4.
    psk4: Optional[str]
    #: Specify PSK5.
    psk5: Optional[str]
    #: Specify PSK6.
    psk6: Optional[str]
    #: Specify PSK7.
    psk7: Optional[str]
    #: Specify PSK8.
    psk8: Optional[str]
    #: Specify PSK9.
    psk9: Optional[str]
    #: Specify PSK10.
    psk10: Optional[str]
    #: Specify PSK11.
    psk11: Optional[str]
    #: Specify PSK12.
    psk12: Optional[str]
    #: Specify PSK13.
    psk13: Optional[str]
    #: Specify PSK14.
    psk14: Optional[str]
    #: Specify PSK15.
    psk15: Optional[str]
    #: Specify PSK16.
    psk16: Optional[str]


class SoftKeyLayout(ApiModel):
    #: Customize SoftKey menu settings.
    soft_key_menu: Optional[SoftKeyMenu]
    #: Customize PSK.
    psk: Optional[PskObject]
    #: Default SoftKey menu settings.
    soft_key_menu_defaults: Optional[SoftKeyMenu]
    #: Default PSK.
    psk_defaults: Optional[PskObject]


class BackgroundImageColor(str, Enum):
    #: Indicates that dark cyan background image will be set for the devices.
    cyan_dark = 'CYAN_DARK'
    #: Indicates the dark purple background image will be set for the devices.
    purple_dark = 'PURPLE_DARK'
    #: Indicates the dark blue background image will be set for the devices.
    blue_dark = 'BLUE_DARK'
    #: Indicates the dark violet background image will be set for the devices.
    violet_dark = 'VIOLET_DARK'
    #: Indicates the light blue background image will be set for the devices.
    blue_light = 'BLUE_LIGHT'
    #: Indicates the light violet background image will be set for the devices.
    violet_light = 'VIOLET_LIGHT'


class MppCustomization(CommonDeviceCustomization):
    """
    settings that are applicable to MPP devices.
    """
    #: Indicates whether PNAC of MPP object is enabled or not
    pnac_enabled: bool
    #: Choose the length of time (in minutes) for the phone’s backlight to remain on.
    backlight_timer: BacklightTimer
    #: Holds the background object of MPP Object.
    background: BackgroundSelection
    #: The display name that appears on the phone screen.
    display_name_format: DisplayNameSelection
    #: Choose the desired logging level for an MPP devices
    default_logging_level: LoggingLevel
    #: Enable/disable Do-Not-Disturb capabilities for Multi-Platform Phones.
    dnd_services_enabled: bool
    #: Chooses the location of the Call Queue Agent Login/Logout softkey on Multi-Platform Phones.
    display_callqueue_agent_softkeys: Optional[DisplayCallqueueAgentSoftkey]
    #: Choose the duration (in hours) of Hoteling guest login.
    hoteling_guest_association_timer: Optional[int]
    #: Holds the Acd object value.
    acd: AcdCustomization
    #: Indicates the short inter digit timer value.
    short_interdigit_timer: int
    #: Indicates the long inter digit timer value.
    long_interdigit_timer: int
    #: Line key labels define the format of what’s shown next to line keys.
    line_key_label_format: LineKeyLabelSelection
    #: LED patterns define lighting schemes for the line keys on the MPP devices. Note – This parameter is not
    #: supported on the MPP 8875
    line_key_led_pattern: LineKeyLedPattern = Field(alias='lineKeyLEDPattern')
    #: Enable/disable user-level access to the web interface of Multi-Platform Phones.
    mpp_user_web_access_enabled: bool
    #: Select up to 10 Multicast Group URLs (each with a unique Listening Port).
    multicast: Optional[list[str]]
    #: Specify the amount of time (in seconds) that a phone can remain off-hook.
    off_hook_timer: int
    #: Select the language for your MPP phone. Setting this overrides the default language setting in place for your
    #: provisioned location.
    phone_language: PhoneLanguage
    #: Enable/disable the Power-Over-Ethernet mode for Multi-Platform Phones.
    poe_mode: str
    #: Specify the amount of inactive time needed (in seconds) before the phone’s screen saver activates.
    screen_timeout: EnabledAndValue
    #: Enable/disable the use of the USB ports on Multi-Platform phones.
    usb_ports_enabled: Optional[bool]
    #: By default the Side USB port is enabled to support KEMs and other peripheral devices. Use the option to disable
    #: use of this port.
    usb_ports: Optional[UsbPortsObject]
    #: Specify a numeric Virtual LAN ID for devices.
    vlan: Optional[MppVlanDevice]
    #: Specify the Wi-Fi SSID and password for wireless-enabled MPP phones.
    wifi_network: Optional[WifiNetwork]
    #: Specify the call history information to use. Only applies to user devices.
    call_history: Optional[CallHistoryMethod]
    #: Specify the directory services to use.
    contacts: Optional[DirectoryMethod]
    #: Enable/disable the availability of the webex meetings functionality from the phone.
    webex_meetings_enabled: Optional[bool]
    #: Specify all volume level values on the phone.
    volume_settings: Optional[VolumeSettings]
    #: Specify the call forward expanded soft key behavior.
    cf_expanded_soft_key: Optional[CallForwardExpandedSoftKey]
    #: Specify HTTP Proxy values.
    http_proxy: Optional[HttpProxy]
    #: Enable/disable the visibility of the bluetooth menu on the MPP device.
    bluetooth: Optional[BluetoothSetting]
    #: Enable/disable the use of the PC passthrough ethernet port on supported phone models.
    pass_through_port_enabled: Optional[bool]
    #: Enable/disable the ability for an end user to set a local password on the phone to restrict local access to the
    #: device.
    user_password_override_enabled: Optional[bool]
    #: Enable/disable the default screen behavior when inbound calls are received.
    active_call_focus_enabled: Optional[bool]
    #: Enable/disable peer firmware sharing.
    peer_firmware_enabled: Optional[bool]
    #: Enable/disable local noise cancellation on active calls from the device.
    noise_cancellation: Optional[NoiseCancellation]
    #: Enable/disable visibility of the Accessibility Voice Feedback menu on the MPP device.
    voice_feedback_accessibility_enabled: Optional[bool]
    #: Enable/disable availability of dial assist feature on the phone.
    dial_assist_enabled: Optional[bool]
    #: Specify the number of calls per unique line appearance on the phone.
    calls_per_line: Optional[int]
    #: Enable/disable the visual indication of missed calls.
    missed_call_notification_enabled: Optional[bool]
    #: Specify the softkey layout per phone menu state.
    soft_key_layout: Optional[SoftKeyLayout]
    #: Specify the image option for the MPP 8875 phone background.
    background_image8875: Optional[BackgroundImageColor]
    #: Specify the use of the backlight feature on 6800 nad 7800 series devices.
    backlight_timer_68xx78xx: Optional[BacklightTimer68XX78XX] = Field(alias='backlightTimer68XX78XX')

    # !!
    # #: Specify the Wi-Fi SSID and password for wireless-enabled MPP phones.
    # wifi_network: Optional[WifiNetwork]
    # migration_url: Optional[str]


class WifiCustomization(ApiModel):
    # TODO: implement as soon as properly documented on developer.webex.com

    #: Choose up to three predefined codec priority options available for your region.
    audio_codec_priority: AudioCodecPriority
    ldap: Any
    web_access: Any


class DeviceCustomizations(ApiModel):
    """
    Customization object of the device settings.

    At the device level only one of ata, dect, and mpp is set. At location and org level all three
    customizations are set.
    """
    ata: Optional[AtaCustomization]
    dect: Optional[DectCustomization]
    mpp: Optional[MppCustomization]
    wifi: Optional[WifiCustomization]


class DeviceCustomization(ApiModel):
    """
    Device customization
    """

    @validator('last_update_time', pre=True)
    def update_time(cls, v):
        """

        :meta private:
        """
        if not v:
            return v
        try:
            v = datetime.fromtimestamp(v / 1000)
        finally:
            pass
        return v

    #: customization object of the device settings.
    customizations: DeviceCustomizations
    #: Indicates if customization is allowed at repective (location or device) level.
    #: If true - customized at this level.
    #: If false - not customized, using higher level config (location or org).
    #: Only present in location and device level customization response
    custom_enabled: Optional[bool]
    #: Indicates the progress of the device update. Not present at device level
    update_in_progress: Optional[bool]
    #: Indicates the device count. Not present at device level
    device_count: Optional[int]
    #: Indicates the last updated time.
    last_update_time: Optional[datetime]


class PrimaryOrShared(str, Enum):
    #: This indicates a Primary line for the member
    primary = 'PRIMARY'
    #: This indicates a Shared line for the member. Shared line appearance allows users to receive and place calls to
    #: and from another user's extension, using their device.
    shared = 'SHARED_CALL_APPEARANCE'
    mobility = 'MOBILITY'


class MediaFileType(str, Enum):
    """
    Media Type of the audio file.
    """
    #: WMA File Extension.
    wma = 'WMA'
    #: WAV File Extension.
    wav = 'WAV'
    #: 3GP File Extension.
    three_gp = '3GP'


class AnnouncementLevel(Enum):
    #: Specifies this audio file is configured across organisation.
    organization = 'ORGANIZATION'
    #: Specifies this audio file is configured across location.
    location = 'LOCATION'
    #: Specifies this audio file is configured on instance level.
    entity = 'ENTITY'


class AnnAudioFile(ApiModel):
    """
    Announcement Audio Files
    """
    #: A unique identifier for the announcement. name, mediaFileType, level are mandatory if id is not provided for
    #: uploading an announcement.
    id: Optional[str]
    #: Name of the file.
    file_name: Optional[str]
    #: Media Type of the audio file.
    media_file_type: Optional[MediaFileType]
    #: Audio announcement file type location.
    level: Optional[AnnouncementLevel]
