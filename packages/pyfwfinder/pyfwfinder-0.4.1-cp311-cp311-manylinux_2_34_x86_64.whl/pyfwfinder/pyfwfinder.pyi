from collections.abc import Sequence
import enum
from typing import overload


DEFCON2024Badge: DeviceType = DeviceType.DEFCON2024Badge

DEFCON2025FwBadge: DeviceType = DeviceType.DEFCON2025FwBadge

class DeviceType(enum.Enum):
    Unknown = 0

    FreeWili = 1

    DEFCON2024Badge = 2

    DEFCON2025FwBadge = 3

    Winky = 5

    UF2 = 4

ESP32: USBDeviceType = USBDeviceType.ESP32

FTDI: USBDeviceType = USBDeviceType.FTDI

FreeWili: DeviceType = DeviceType.FreeWili

class FreeWiliDevice:
    def __str__(self) -> str: ...

    def __eq__(self, arg: FreeWiliDevice, /) -> bool: ...

    @property
    def device_type(self) -> DeviceType: ...

    @property
    def name(self) -> str: ...

    @property
    def serial(self) -> str: ...

    @property
    def unique_id(self) -> int: ...

    @property
    def standalone(self) -> bool: ...

    @property
    def usb_devices(self) -> list[USBDevice]: ...

    @overload
    def get_usb_devices(self) -> list[USBDevice]: ...

    @overload
    def get_usb_devices(self, arg: USBDeviceType, /) -> list[USBDevice]: ...

    @overload
    def get_usb_devices(self, arg: Sequence[USBDeviceType], /) -> list[USBDevice]: ...

    def get_main_usb_device(self) -> USBDevice: ...

    def get_display_usb_device(self) -> USBDevice: ...

    def get_fpga_usb_device(self) -> USBDevice: ...

    def get_hub_usb_device(self) -> USBDevice: ...

Hub: USBDeviceType = USBDeviceType.Hub

MassStorage: USBDeviceType = USBDeviceType.MassStorage

Other: USBDeviceType = USBDeviceType.Other

Serial: USBDeviceType = USBDeviceType.Serial

SerialDisplay: USBDeviceType = USBDeviceType.SerialDisplay

SerialMain: USBDeviceType = USBDeviceType.SerialMain

UF2: DeviceType = DeviceType.UF2

class USBDevice:
    def __init__(self) -> None: ...

    def __str__(self) -> str: ...

    def __eq__(self, arg: USBDevice, /) -> bool: ...

    @property
    def kind(self) -> USBDeviceType: ...

    @property
    def vid(self) -> int: ...

    @property
    def pid(self) -> int: ...

    @property
    def name(self) -> str: ...

    @property
    def serial(self) -> str: ...

    @property
    def location(self) -> int: ...

    @property
    def port_chain(self) -> list[int]: ...

    @property
    def paths(self) -> list[str] | None: ...

    @property
    def port(self) -> str | None: ...

class USBDeviceType(enum.Enum):
    Hub = 0

    Serial = 1

    SerialMain = 2

    SerialDisplay = 3

    MassStorage = 4

    ESP32 = 5

    FTDI = 6

    Other = 7

Unknown: DeviceType = DeviceType.Unknown

Winky: DeviceType = DeviceType.Winky

def find_all() -> list[FreeWiliDevice]: ...

def get_device_type_name(arg: DeviceType, /) -> str: ...

def get_usb_device_type_name(arg: USBDeviceType, /) -> str: ...
