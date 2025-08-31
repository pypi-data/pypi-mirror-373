#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ['mido', 'python-rtmidi', 'pydantic', 'pyyaml']
# ///

"""Korg nanoKONTROL Studio specific implementation"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from contextlib import ExitStack
from enum import StrEnum, auto
from itertools import batched
from types import FrameType, ModuleType, TracebackType
from typing import Optional, TextIO, Type

import mido
import yaml
from pydantic import BaseModel, ConfigDict, model_validator

Values = dict[str, str | bytes]
LOG = logging.getLogger("knks")

EXTRA_KEYS = (
    "play",
    "stop",
    "record",
    "fast_backward",
    "fast_forward",
    "cycle",
    "begin",
    "marker_set",
    "marker_left",
    "marker_right",
    "track_left",
    "track_right",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GlobalConfig(StrictModel):
    global_midi_channel: int = 0  # raw, i.e. 0..15
    controller_mode: int = 0  # 0 = assignable, 1=cubase..
    battery_type: int = 0  # 0=Alkalline, 1=NiMH
    name: str = "nanoKontrol Studio"
    scene_button_as_scrub: int = 0

    usb_auto_led_off: int = 3
    usb_led_brightness: int = 3
    usb_led_illumination: int = 1

    bat_auto_power_safe: int = 2  # disable, 30min, 2=1h, 2h, 4h
    bat_auto_led_off: int = 1
    bat_led_brightness: int = 2
    bat_led_illumination: int = 1

    @classmethod
    def from_raw(cls, data: bytes) -> "GlobalConfig":
        """
        Extract global config data from an unpacked byte sequence of size 126
        """
        assert len(data) == 126  # should be 128
        return cls(
            global_midi_channel=data[0],
            controller_mode=data[1],
            battery_type=data[2],
            scene_button_as_scrub=data[3],
            name=data[8:33]
            .decode(encoding="ascii", errors="ignore")
            .replace("\0", "")
            .strip(),
            usb_auto_led_off=data[65],
            usb_led_brightness=data[66],
            usb_led_illumination=data[67],
            bat_auto_power_safe=data[72],
            bat_auto_led_off=data[73],
            bat_led_brightness=data[74],
            bat_led_illumination=data[75],
        )

    def serialize(self) -> bytes:
        result = bytearray(b"\xff" * 126)
        result[0] = self.global_midi_channel
        result[1] = self.controller_mode
        result[2] = self.battery_type
        result[3] = self.scene_button_as_scrub
        result[8:33] = self.name.encode(encoding="ascii").ljust(25, b"\0")
        result[64] = 0  # ?? (maybe usb_auto_power_safe)
        result[65] = self.usb_auto_led_off
        result[66] = self.usb_led_brightness
        result[67] = self.usb_led_illumination

        result[72] = self.bat_auto_power_safe
        result[73] = self.bat_auto_led_off
        result[74] = self.bat_led_brightness
        result[75] = self.bat_led_illumination

        result[80] = 0  # ??
        result[81] = 0  # ??
        return bytes(result)

    def dump(self) -> None:
        print(f"Name: '{self.name}'")
        print(f" midi: '{self.global_midi_channel + 1}'")
        # controller_mode: int = 0  # 0 = assignable, 1=cubase..
        # battery_type: int = 0  # 0=Alkalline, 1=NiMH
        # scene_button_as_scrub: int = 0

        # usb_auto_led_off: int = 3
        # usb_led_brightness: int = 3
        # usb_led_illumination: int = 1

        # bat_auto_power_safe: int = 2  # disable, 30min, 2=1h, 2h, 4h
        # bat_auto_led_off: int = 1
        # bat_led_brightness: int = 2
        # bat_led_illumination: int = 1


class Scalar(StrictModel):
    midi_channel: int
    disabled: int = 0
    midi_cc: int
    lower_value: int = 0
    upper_value: int = 127

    @classmethod
    def default(cls, index: int) -> "Scalar":
        return cls(
            midi_channel=1 + index,
            midi_cc=13 + index,
        )

    @classmethod
    def from_raw(cls, data: bytes) -> "Scalar":
        return cls(
            midi_channel=data[0] + 1,
            disabled=data[1],
            midi_cc=data[2],
            lower_value=data[3],
            upper_value=data[4],
        )

    def serialize(self) -> bytes:
        return bytes(
            (
                self.midi_channel - 1,
                0,
                self.midi_cc,
                self.lower_value,
                self.upper_value,
            )
        )

    def param_str(self) -> str:
        return f"(c={self.midi_channel:>2} cc={self.midi_cc:>3} l={self.lower_value:>2} u={self.upper_value:>3})"


class Button(StrictModel):
    midi_channel: int
    assign_type: int = 0  # 0: ControlChange
    cc_note_value: int
    off_value: int = 0
    on_value: int = 127
    behavior: int = 0  # 0: momentary, 1: toggle

    @classmethod
    def default(cls, index: int) -> "Button":
        return cls(
            midi_channel=1,
            cc_note_value=0,
        )

    @classmethod
    def from_raw(cls, data: bytes) -> "Button":
        """ """
        return cls(
            midi_channel=data[0] + 1,
            assign_type=data[1],
            cc_note_value=data[2],
            off_value=data[3],
            on_value=data[4],
            behavior=data[5],
        )

    def serialize(self) -> bytes:
        return bytes(
            (
                self.midi_channel - 1,
                self.assign_type,
                self.cc_note_value,
                self.off_value,
                self.on_value,
                self.behavior,
            )
        )

    def param_str(self) -> str:
        return (
            f"(c:{self.midi_channel:>2}"
            f" {'nt' if self.assign_type else 'cc'}:{self.cc_note_value:>3}"
            f" b:{self.off_value:>2}-{self.on_value:>3}"
            f" {'t' if self.behavior else 'm'})"
        )


class JogWheel(StrictModel):
    midi_channel: int
    wheel_type: int = 0
    acceleration: int = 0
    sign_mag_cc: int = 82
    inc_dec_cw_cc: int = 83
    inc_dec_ccw_cc: int = 85
    continuous_cc: int = 86
    min_val: int = 0
    max_val: int = 127
    """
    512-010-?|513-002-?|514-000-?|515-087-W|516-088-X|517-089-Y|518-090-Z|519-007-?|
    520-120-x|521-255-■|522-255-■|523-255-■|524-255-■|525-255-■|526-255-■|527-255-■|
    """

    @classmethod
    def default(cls) -> "JogWheel":
        return cls(midi_channel=1)

    @classmethod
    def from_raw(cls, data: Sequence[int]) -> "JogWheel":
        return cls(
            midi_channel=data[0] + 1,
            wheel_type=data[1],
            acceleration=data[2],
            sign_mag_cc=data[3],
            inc_dec_cw_cc=data[4],
            inc_dec_ccw_cc=data[5],
            continuous_cc=data[6],
            min_val=data[7],
            max_val=data[8],
        )

    def serialize(self) -> bytes:
        return bytes(
            (
                self.midi_channel - 1,
                self.wheel_type,
                self.acceleration,
                self.sign_mag_cc,
                self.inc_dec_cw_cc,
                self.inc_dec_ccw_cc,
                self.continuous_cc,
                self.min_val,
                self.max_val,
            )
        )


class SceneConfig(StrictModel):
    name: str  # "Scene <N>"
    # LED mode
    jog_wheel: JogWheel = JogWheel.default()

    knob: tuple[Scalar, ...] = tuple(Scalar.default(i) for i in range(8))
    slider: tuple[Scalar, ...] = tuple(Scalar.default(i) for i in range(8))
    mute: tuple[Button, ...] = tuple(Button.default(i) for i in range(8))
    solo: tuple[Button, ...] = tuple(Button.default(i) for i in range(8))
    rec: tuple[Button, ...] = tuple(Button.default(i) for i in range(8))
    select: tuple[Button, ...] = tuple(Button.default(i) for i in range(8))

    extra: tuple[Button, ...] = tuple(Button.default(i) for i in range(12))

    @classmethod
    def default(cls, scene_number: int) -> "SceneConfig":
        return cls(
            name=f"Scene {scene_number + 1}",
        )

    @classmethod
    def from_raw(cls, data: bytes) -> "SceneConfig":
        return cls(
            name=data[0:16]
            .decode(encoding="ascii", errors="ignore")
            .replace("\0", "")
            .strip(),
            knob=tuple(
                Scalar.from_raw(data[(2 + i) * 8 : (2 + i + 1) * 8])
                for i in range(8)
            ),
            slider=tuple(
                Scalar.from_raw(data[(10 + i) * 8 : (10 + i + 1) * 8])
                for i in range(8)
            ),
            solo=tuple(
                Button.from_raw(data[(18 + i) * 8 : (18 + i + 1) * 8])
                for i in range(8)
            ),
            mute=tuple(
                Button.from_raw(data[(26 + i) * 8 : (26 + i + 1) * 8])
                for i in range(8)
            ),
            rec=tuple(
                Button.from_raw(data[(34 + i) * 8 : (34 + i + 1) * 8])
                for i in range(8)
            ),
            select=tuple(
                Button.from_raw(data[(42 + i) * 8 : (42 + i + 1) * 8])
                for i in range(8)
            ),
            extra=tuple(
                Button.from_raw(data[(50 + i) * 8 : (50 + i + 1) * 8])
                for i in range(12)
            ),
            jog_wheel=JogWheel.from_raw(data[64 * 8 : 64 * 8 + 9]),
        )

    def serialize(self) -> bytes:
        def round_up(x: int) -> int:
            return ((x + 8 - 1) // 8) * 8

        return b"".join(
            b.ljust(round_up(len(b)), b"\xff")
            for a in (
                (self.name.encode(encoding="ascii").ljust(13, b"\x00"),),
                map(Scalar.serialize, self.knob),
                map(Scalar.serialize, self.slider),
                map(Button.serialize, self.solo),
                map(Button.serialize, self.mute),
                map(Button.serialize, self.rec),
                map(Button.serialize, self.select),
                map(Button.serialize, self.extra),
                (b"".ljust(2 * 8, b"\xff"),),
                (self.jog_wheel.serialize(),),
                (b"".ljust(4 * 8, b"\xff"),),
            )
            for b in a
        )

    def dump(self) -> None:
        print(f"Name: '{self.name}'")
        for i in range(8):
            print(
                f"Col {i + 1}: Kn: {self.knob[i].param_str()}"
                f" Sl: {self.slider[i].param_str()}"
                f" Mu: {self.mute[i].param_str()}"
                f" So: {self.solo[i].param_str()}"
                f" Re: {self.rec[i].param_str()}"
                f" Se: {self.select[i].param_str()}"
            )
        for r in range(3):
            print(
                " ".join(
                    f"{self.extra[r * 4 + c].param_str()}" for c in range(4)
                )
            )


class Configuration(StrictModel):
    global_config: GlobalConfig = GlobalConfig()
    scene_config: tuple[SceneConfig, ...] = tuple(
        SceneConfig.default(i) for i in range(5)
    )


def to_yaml(configuration: Configuration) -> str:
    """
    >>> len(to_yaml(Configuration())) > 10
    True
    """

    def config_representer(
        dumper: yaml.Dumper, data: Configuration
    ) -> yaml.Node:
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            {
                "global": data.global_config,
                **{
                    f"scene{i + 1}": sc
                    for i, sc in enumerate(data.scene_config)
                },
            },
        )

    def global_config_representer(
        dumper: yaml.Dumper, data: GlobalConfig
    ) -> yaml.Node:
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            data.model_dump(),
        )

    def scene_representer(dumper: yaml.Dumper, data: SceneConfig) -> yaml.Node:
        return dumper.represent_mapping(
            "tag:yaml.org,2002:map",
            {
                "name": data.name,
                "jog_wheel": data.jog_wheel.model_dump(),
                "buttons": {
                    k: data.extra[i] for i, k in enumerate(EXTRA_KEYS)
                },
                **{
                    f"block{i + 1}": {
                        "mute": data.mute[i],
                        "solo": data.solo[i],
                        "rec": data.rec[i],
                        "select": data.select[i],
                        "knob": data.knob[i],
                        "slider": data.slider[i],
                    }
                    for i in range(8)
                },
            },
        )

    def shortmap_representer(
        dumper: yaml.Dumper, data: Button | Scalar
    ) -> yaml.Node:
        return dumper.represent_data(str(data))

    yaml.add_representer(Configuration, config_representer)
    yaml.add_representer(GlobalConfig, global_config_representer)
    yaml.add_representer(SceneConfig, scene_representer)
    yaml.add_representer(Button, shortmap_representer)
    yaml.add_representer(Scalar, shortmap_representer)

    return yaml.dump(configuration, sort_keys=False)


def from_yaml(yaml_stream: TextIO) -> Configuration:
    def dict_from(string: str) -> Values:
        return {k: v for e in string.split(" ") for k, v in (e.split("="),)}

    raw_data = yaml.load(yaml_stream, Loader=yaml.Loader)

    return Configuration(
        global_config=raw_data["global"],
        scene_config=tuple(
            SceneConfig(
                name=raw_scene["name"],
                jog_wheel=raw_scene["jog_wheel"],
                knob=tuple(
                    Scalar.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["knob"])
                    )
                    for j in range(8)
                ),
                slider=tuple(
                    Scalar.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["slider"])
                    )
                    for j in range(8)
                ),
                mute=tuple(
                    Button.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["mute"])
                    )
                    for j in range(8)
                ),
                solo=tuple(
                    Button.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["solo"])
                    )
                    for j in range(8)
                ),
                rec=tuple(
                    Button.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["rec"])
                    )
                    for j in range(8)
                ),
                select=tuple(
                    Button.model_validate(
                        dict_from(raw_scene[f"block{j + 1}"]["select"])
                    )
                    for j in range(8)
                ),
                extra=tuple(
                    Button.model_validate(dict_from(raw_scene["buttons"][key]))
                    for key in EXTRA_KEYS
                ),
            )
            for i in range(5)
            for raw_scene in (raw_data[f"scene{i + 1}"],)
        ),
    )


class SysexMessage(ABC):
    class Type(StrEnum):
        SEARCH_DEVICE = auto()
        DEVICE_INQUIRY_REQUEST = auto()
        DEVICE_INQUIRY_REPLY = auto()
        REQUEST_CURRENT_SCENE_CONFIG = auto()
        REQUEST_SAVE_SCENE_CONFIG = auto()
        DATA_WRITE_COMPLETED = auto()
        DATA_LOAD_COMPLETED = auto()
        SET_SCENE_NUMBER = auto()
        REQUEST_GLOBAL_CONFIG = auto()
        SCENE_CONFIG = auto()
        GLOBAL_CONFIG = auto()
        REQUEST_MODE = auto()
        MODE = auto()

    @classmethod
    def from_raw(cls, raw_data: bytes) -> "SysexMessage":
        # print(" ".join(f"{b:02X}" for b in raw_data[:16]))
        raw_bytes = bytes(raw_data)
        if raw_bytes == DeviceInquiryRequestMessage.serialized():
            return DeviceInquiryRequestMessage()

        if raw_bytes[:2] == b"\x42\x50":
            return SearchDeviceMessage()

        if raw_bytes[0] == 0x7E:
            assert (raw_bytes[1] >> 4) == 0
            assert len(raw_bytes) == 13
            return DeviceInquiryReplyMessage(raw_bytes)

        assert raw_bytes[0] == 0x42

        return NanoKontrolSysexMessage.from_raw(raw_bytes)

    @property
    @abstractmethod
    def type(self) -> Type: ...

    @abstractmethod
    def serialized(self) -> bytes: ...

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__repr__()


class SearchDeviceMessage(SysexMessage):
    @staticmethod
    def serialized() -> bytes:
        return b"\x42\x50\x00\xff"

    @property
    def type(self) -> SysexMessage.Type:
        return self.Type.SEARCH_DEVICE

    def __repr__(self) -> str:
        return f"{self.type:<28} |"


class DeviceInquiryRequestMessage(SysexMessage):
    @staticmethod
    def serialized() -> bytes:
        return b"\x7e\x7f\x06\x01"

    @property
    def type(self) -> SysexMessage.Type:
        return self.Type.DEVICE_INQUIRY_REQUEST

    def __repr__(self) -> str:
        return f"{self.type:<28} |"


class DeviceInquiryReplyMessage(SysexMessage):
    raw_data: bytes

    @property
    def type(self) -> SysexMessage.Type:
        return self.Type.DEVICE_INQUIRY_REPLY

    def __init__(self, raw_data: bytes) -> None:
        self.raw_data = raw_data

    def midi_channel(self) -> int:
        """0..15 => 1..16"""
        return self.raw_data[1] % 16

    def serialized(self) -> bytes:
        return self.raw_data

    def __repr__(self) -> str:
        # 7E 02 06 02 42 37 01 00 00 05 00 01 00
        # 42 50 01 01 04 37 01 00 00 05 00 01 00

        return (
            f"{self.type:<28} |"
            f" midi={self.midi_channel() + 1:02}"
            f" device={self.raw_data[4]:02X}-{self.raw_data[5]:02X}"
            f" version={self.raw_data[11]}.{self.raw_data[9]:02}"
        )


class NanoKontrolSysexMessage(SysexMessage, StrictModel):
    manufacturer: int = 0x42
    project_id: int = 0x37
    midi_channel: int
    payload: bytes

    @classmethod
    def create(
        cls,
        type: SysexMessage.Type,
        midi_channel: int,
        scene_number: None | int = None,
        unpacked: None | bytes = None,
        **kwargs: int,
    ) -> "NanoKontrolSysexMessage":
        def payload_from(
            msg_type: SysexMessage.Type,
            scene_number: None | int = None,
            unpacked: None | bytes = None,
        ) -> bytes:
            if msg_type == cls.Type.REQUEST_CURRENT_SCENE_CONFIG:
                return b"\x10"
            if msg_type == cls.Type.REQUEST_SAVE_SCENE_CONFIG:
                if scene_number is None or scene_number not in range(5):
                    raise RuntimeError("Need scene_number=0..4")
                return bytes([0x11, scene_number])
            if msg_type == cls.Type.SET_SCENE_NUMBER:
                if scene_number is None or scene_number not in range(5):
                    raise RuntimeError("Need scene_number=0..4")
                return bytes([0x14, scene_number])
            if msg_type == cls.Type.REQUEST_GLOBAL_CONFIG:
                return b"\x0e"
            """
            if self.payload[0] == 0x21:
                assert len(self.payload) == 1
                return self.Type.DATA_WRITE_COMPLETED
            if self.payload[0] == 0x23:
                assert len(self.payload) == 1
                return self.Type.DATA_LOAD_COMPLETED
            """
            if msg_type == cls.Type.SCENE_CONFIG:
                if not unpacked:
                    raise RuntimeError("Need unpacked bytes")
                return b"\x40" + cls.pack_7b(unpacked)
            if msg_type == cls.Type.GLOBAL_CONFIG:
                if not unpacked:
                    raise RuntimeError("Need unpacked bytes")
                return b"\x51" + cls.pack_7b(unpacked) + b"\x03\x7f\x7f"
            raise RuntimeError(f"Unknown message type {type}")

        return cls(
            payload=payload_from(
                msg_type=type, scene_number=scene_number, unpacked=unpacked
            ),
            midi_channel=midi_channel,
            **{
                key: value
                for key, value in kwargs.items()
                if key not in {"scene_number", "unpacked"}
            },
        )

    @classmethod
    def from_raw(cls, data: bytes) -> "NanoKontrolSysexMessage":
        payload_size = (data[7] << 14) + (data[6] << 7) + data[5]
        assert payload_size + 8 == len(data), (
            f"payload size {payload_size} does not match actual size {len(data) - 8}"
        )
        return cls(
            manufacturer=data[0],
            project_id=data[4],
            midi_channel=data[1] % 16,
            payload=data[8:],
        )

    @property
    def type(self) -> SysexMessage.Type:
        if self.payload[0] == 0x10:
            assert len(self.payload) == 1
            return self.Type.REQUEST_CURRENT_SCENE_CONFIG
        if self.payload[0] == 0x11:
            assert len(self.payload) == 2  # 1 + scene_number
            return self.Type.REQUEST_SAVE_SCENE_CONFIG
        if self.payload[0] == 0x12:
            assert len(self.payload) == 1
            return self.Type.REQUEST_MODE
        if self.payload[0] == 0x14:
            assert len(self.payload) == 2  # 1 + scene_number
            return self.Type.SET_SCENE_NUMBER
        if self.payload[0] == 0x0E:
            assert len(self.payload) == 1
            return self.Type.REQUEST_GLOBAL_CONFIG
        if self.payload[0] == 0x21:
            assert len(self.payload) == 1
            return self.Type.DATA_WRITE_COMPLETED
        if self.payload[0] == 0x23:
            assert len(self.payload) == 1
            return self.Type.DATA_LOAD_COMPLETED
        if self.payload[0] == 0x40:
            assert len(self.payload) == 641  # 1 + 8 x 80
            return self.Type.SCENE_CONFIG
        if self.payload[0] == 0x42:
            assert len(self.payload) == 2
            return self.Type.MODE
        if self.payload[0] == 0x51:
            assert len(self.payload) == 148  # 17 * 8 + 3
            return self.Type.GLOBAL_CONFIG
        raise RuntimeError(f"Unknown message type 0x{self.payload[0]:2X}")

    @property
    def scene_number(self) -> int:
        assert self.type in {
            self.Type.SET_SCENE_NUMBER,
            self.Type.REQUEST_SAVE_SCENE_CONFIG,
        }
        return self.payload[1] + 1

    @property
    def unpacked(self) -> bytes:
        assert self.type in {self.Type.SCENE_CONFIG, self.Type.GLOBAL_CONFIG}
        temp_effective_length = (
            len(self.payload) - 3
            if self.type == self.Type.GLOBAL_CONFIG
            else len(self.payload)
        )
        return self.unpack_7b(self.payload[1:temp_effective_length])

    def serialized(self) -> bytes:
        return (
            bytes(
                (
                    self.manufacturer,
                    0x40 + self.midi_channel,
                    0,
                    1,
                    self.project_id,
                    len(self.payload) % 128,
                    (len(self.payload) // 128) % 128,
                    0,
                )
            )
            + self.payload
        )

    def __repr__(self) -> str:
        return (
            f"{self.type:<28}"
            f" | device={self.manufacturer:02X}-{self.project_id:02X}"
            f" midi={self.midi_channel} payload={len(self.payload)}"
        )

    @staticmethod
    def unpack_7b(data: bytes) -> bytes:
        assert len(data) % 8 == 0, f"len:={len(data)}%8!==0"
        return bytes(
            c | b
            for c, b in zip(
                (c for i, c in enumerate(data) if i % 8 != 0),
                (
                    int(b) << 7
                    for i, c in enumerate(data)
                    if i % 8 == 0
                    for b in f"{c:07b}"[::-1]
                ),
            )
        )

    @staticmethod
    def pack_7b(data: bytes) -> bytes:
        def pack_msb(values: Sequence[int]) -> Sequence[int]:
            result = [0]
            for i, v in enumerate(values):
                result[0] |= ((v >> 7) & 1) << i
                result.append(v % 128)
            return result

        assert len(data) % 7 == 0
        result: list[int] = []
        for chunk in batched(data, 7):
            result.extend(pack_msb(chunk))
        return bytes(result)

    @staticmethod
    def formatted(enumerated: Iterable[tuple[int, int]]) -> str:
        return "".join(
            f"{i:03}-{c:03}-{(chr(c) if 32 <= c < 127 else '■' if c == 255 else '?')}|"
            for i, c in enumerated
        )

    def dump(self) -> None:
        if self.type == self.Type.SCENE_CONFIG:
            for chunk in batched(enumerate(self.unpacked), 8):
                print(self.formatted(chunk))
        else:
            for chunk in batched(enumerate(self.unpacked), 9):
                print(self.formatted(chunk))


class DeviceConnection:
    def __init__(self, midi_port_name: str) -> None:
        self.midi_port_name = midi_port_name
        self.midi_in: None | mido.Input = None
        self.midi_out: None | mido.Output = None
        self._stack = ExitStack()

    def __enter__(self) -> "DeviceConnection":
        for io_port_name in mido.get_ioport_names():
            if self.midi_port_name not in io_port_name:
                continue
            LOG.info("using %s", io_port_name)
            self.midi_in = self._stack.enter_context(
                mido.open_input(io_port_name)
            )
            self.midi_out = self._stack.enter_context(
                mido.open_output(io_port_name)
            )
            mido.ports.set_sleep_time(seconds=0.03)
            return self
        raise RuntimeError(
            f"No device with name '{self.midi_port_name}' found among {mido.get_ioport_names()}"
        )

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None | bool:
        return self._stack.__exit__(exc_type, exc_val, exc_tb)

    def get_reply(
        self, data_or_message: str | Sequence[int] | SysexMessage
    ) -> Sequence[SysexMessage]:
        if not self.midi_out:
            raise RuntimeError("No midi_out device defined")
        assert isinstance(data_or_message, SysexMessage), data_or_message
        parsed_request = (
            data_or_message
            if isinstance(data_or_message, SysexMessage)
            else SysexMessage.from_raw(
                bytes.fromhex(data_or_message)
                if isinstance(data_or_message, str)
                else bytes(data_or_message)
            )
        )
        LOG.info("> %s", parsed_request)
        self.midi_out.send(
            mido.Message("sysex", data=parsed_request.serialized())
        )
        while not (messages := self.receive_messages()):
            # LOG.debug("retry receive")
            continue
        return messages

    def receive_messages(self) -> Sequence[SysexMessage]:
        if not self.midi_in:
            raise RuntimeError("No midi_in device defined")
        mido.ports.sleep()
        reply = []
        while msg := self.midi_in.receive(block=False):
            if msg.type != "sysex":
                continue
            parsed = SysexMessage.from_raw(bytes(msg.data))
            # dump_formatted(msg.data)
            LOG.info("< %s", parsed)
            reply.append(parsed)

        return reply

    def watch_messages(self) -> GlobalConfig:
        while True:
            self.receive_messages()

    def read_global_config(self) -> GlobalConfig:
        reply = self.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        midi_channel = reply[-1].midi_channel()

        # no idea what this is, maybe "mode request"
        # reply = self.get_reply(
        #    NanoKontrolSysexMessage(midi_channel=midi_channel, payload=[0x12])
        # )
        # >c:p 42 42 00 01 37 01 00 00 12 F7
        # c:p 42 42 00 01 37 02 00 00 42 00 F7

        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.REQUEST_GLOBAL_CONFIG,
                midi_channel=midi_channel,
            )
        )
        assert isinstance(reply[0], NanoKontrolSysexMessage)
        assert reply[0].type == NanoKontrolSysexMessage.Type.GLOBAL_CONFIG, (
            reply[0].type
        )
        return GlobalConfig.from_raw(reply[0].unpacked)

    def read_scene_config(self, scene_nr: int) -> SceneConfig:
        reply = self.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        midi_channel = reply[-1].midi_channel()

        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.SET_SCENE_NUMBER,
                midi_channel=midi_channel,
                scene_number=scene_nr,
            )
        )

        reply = self.get_reply(DeviceInquiryRequestMessage())

        # request 'current scene data dump'
        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.REQUEST_CURRENT_SCENE_CONFIG,
                midi_channel=midi_channel,
                scene_number=scene_nr,
            )
        )
        assert isinstance(reply[0], NanoKontrolSysexMessage)
        assert reply[0].type == NanoKontrolSysexMessage.Type.SCENE_CONFIG

        scene_config_message = reply[0]
        scene_config_message.dump()

        reply = self.get_reply(DeviceInquiryRequestMessage())
        return SceneConfig.from_raw(scene_config_message.unpacked)

    def write_global_config(self, global_config: GlobalConfig) -> None:
        global_config.dump()

        reply = self.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        midi_channel = reply[-1].midi_channel()

        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.GLOBAL_CONFIG,
                midi_channel=midi_channel,
                unpacked=global_config.serialize(),
            )
        )
        assert any(
            r.type == NanoKontrolSysexMessage.Type.DATA_LOAD_COMPLETED
            for r in reply
        )

    def write_scene_config(
        self, scene_nr: int, scene_config: SceneConfig
    ) -> None:
        scene_config.dump()

        reply = self.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        midi_channel = reply[-1].midi_channel()

        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.SCENE_CONFIG,
                midi_channel=midi_channel,
                unpacked=scene_config.serialize(),
            )
        )
        assert len(reply) == 1
        assert isinstance(reply[0], NanoKontrolSysexMessage)
        assert any(
            r.type == SysexMessage.Type.DATA_LOAD_COMPLETED for r in reply
        )

        reply = self.get_reply(DeviceInquiryRequestMessage())
        assert len(reply) == 1
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)

        reply = self.get_reply(
            NanoKontrolSysexMessage.create(
                type=SysexMessage.Type.REQUEST_SAVE_SCENE_CONFIG,
                midi_channel=midi_channel,
                scene_number=scene_nr,
            )
        )
        assert isinstance(reply[0], NanoKontrolSysexMessage)
        assert len(reply) == 1
        assert any(
            r.type == SysexMessage.Type.DATA_WRITE_COMPLETED for r in reply
        )
