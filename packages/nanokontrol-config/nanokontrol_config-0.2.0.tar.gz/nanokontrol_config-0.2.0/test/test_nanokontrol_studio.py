#!/usr/bin/env python3

""" """

from itertools import batched

import pytest

RAW_GLOBAL_CONFIG_MSG = (
    "42 42 00 01 37 14 01 00"
    "51"
    "70 00 00 01 00 7F 7F 7F"
    "01 7F 6E 6E 6E 6E 4B 4F"
    "00 4E 54 52 4F 4C 20 53"
    "00 74 75 64 69 6F 00 00"
    "40 00 00 00 00 00 00 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "61 7F 00 01 00 00 7F 7F"
    "43 7F 7F 04 00 02 00 7F"
    "67 7F 7F 7F 00 00 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F"
    "03 7F 7F"
)
RAW_SCENE_CONFIG_MSG = (
    "42 42 00 01 37 01 05 00"
    "40"
    "00 53 63 65 6E 65 20 35  40 00 00 00 00 00 00 7F"
    "03 7F 7F 04 00 0F 00 7F  07 7F 7F 7F 04 00 10 00"
    "0E 7F 7F 7F 7F 04 00 11  1C 00 7F 7F 7F 7F 04 00"
    "38 12 00 7F 7F 7F 7F 04  70 00 13 00 7F 7F 7F 7F"
    "60 04 00 14 00 7F 7F 7F  41 7F 04 00 15 00 7F 7F"
    "03 7F 7F 04 00 16 00 7F  07 7F 7F 7F 06 00 04 00"
    "0E 7B 7F 7F 7F 04 00 05  1C 00 7F 7F 7F 7F 04 00"
    "38 06 00 7F 7F 7F 7F 04  70 00 07 00 7F 7F 7F 7F"
    "60 04 00 08 00 7F 7F 7F  41 7F 04 00 0A 00 7F 7F"
    "03 7F 7F 06 00 0E 00 7F  07 7F 7F 7F 06 00 0C 03"
    "0E 7C 7F 7F 7F 04 00 1F  18 00 7F 00 7F 7F 04 00"
    "30 1E 00 7F 00 7F 7F 04  60 00 1F 00 7F 00 7F 7F"
    "40 04 00 21 00 7F 00 7F  01 7F 04 00 22 00 7F 00"
    "03 7F 7F 04 00 23 00 7F  06 00 7F 7F 04 00 24 00"
    "0C 7F 00 7F 7F 04 00 27  18 00 7F 00 7F 7F 04 00"
    "30 17 00 7F 00 7F 7F 04  60 00 16 00 7F 00 7F 7F"
    "40 04 00 17 00 7F 00 7F  01 7F 04 00 18 00 7F 00"
    "03 7F 7F 04 00 19 00 7F  06 00 7F 7F 04 00 1A 00"
    "0C 7F 00 7F 7F 04 00 1B  18 00 7F 00 7F 7F 04 00"
    "30 1E 00 7F 00 7F 7F 04  60 00 28 00 7F 00 7F 7F"
    "40 04 00 27 00 7F 00 7F  01 7F 04 00 28 00 7F 00"
    "03 7F 7F 04 00 29 00 7F  06 00 7F 7F 04 00 2A 00"
    "0C 7F 00 7F 7F 04 00 2B  18 00 7F 00 7F 7F 04 00"
    "30 2C 00 7F 00 7F 7F 04  60 00 2F 00 7F 00 7F 7F"
    "40 04 00 30 00 7F 00 7F  01 7F 04 00 2F 00 7F 00"
    "03 7F 7F 04 00 30 00 7F  06 00 7F 7F 04 00 31 00"
    "0C 7F 00 7F 7F 04 00 32  18 00 7F 00 7F 7F 04 00"
    "30 33 00 7F 00 7F 7F 04  60 00 34 00 7F 00 7F 7F"
    "40 04 00 37 00 7F 00 7F  01 7F 04 00 50 00 7F 00"
    "03 7F 7F 04 00 3F 00 7F  06 00 7F 7F 04 00 51 00"
    "0C 7F 00 7F 7F 04 00 3A  18 00 7F 00 7F 7F 04 00"
    "30 3B 00 7F 00 7F 7F 04  60 00 36 00 7F 00 7F 7F"
    "40 04 00 3E 00 7F 00 7F  01 7F 04 00 37 00 7F 00"
    "03 7F 7F 04 00 38 00 7F  06 00 7F 7F 04 00 39 00"
    "0C 7F 00 7F 7F 04 00 3C  18 00 7F 00 7F 7F 04 00"
    "70 3D 00 7F 00 7F 7F 7F  7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F  01 7F 04 02 01 52 53 55"
    "78 56 00 7F 7F 7F 7F 7F  7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F  7F 7F 7F 7F 7F 7F 7F 7F"
    "7F 7F 7F 7F 7F 7F 7F 7F  7F 7F 7F 7F 7F 7F 7F 7F"
)

from nanokontrol_config.nanokontrol_studio import (
    DeviceConnection,
    DeviceInquiryReplyMessage,
    DeviceInquiryRequestMessage,
    GlobalConfig,
    NanoKontrolSysexMessage,
    SceneConfig,
    SysexMessage,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw_str, properties",
    [
        (
            "7E 7F 06 01",
            {
                "type": SysexMessage.Type.DEVICE_INQUIRY_REQUEST,
            },
        ),
        (
            "7E 02 06 02 42 37 01 00 00 05 00 01 00",
            {"type": SysexMessage.Type.DEVICE_INQUIRY_REPLY},
        ),
        (
            "42 42 00 01 37 01 00 00 10",
            {
                "type": NanoKontrolSysexMessage.Type.REQUEST_CURRENT_SCENE_CONFIG
            },
        ),
        (
            "42 42 00 01 37 02 00 00 11 03",
            {
                "type": NanoKontrolSysexMessage.Type.REQUEST_SAVE_SCENE_CONFIG,
                "scene_number": 4,
            },
        ),
        (
            "42 42 00 01 37 01 00 00 21",
            {
                "type": NanoKontrolSysexMessage.Type.DATA_WRITE_COMPLETED,
            },
        ),
        (
            "42 42 00 01 37 01 00 00 23",
            {
                "type": NanoKontrolSysexMessage.Type.DATA_LOAD_COMPLETED,
            },
        ),
        (
            "42 42 00 01 37 02 00 00 14 00",
            {
                "type": NanoKontrolSysexMessage.Type.SET_SCENE_NUMBER,
                "scene_number": 1,
            },
        ),
        (
            "42 42 00 01 37 01 00 00 0E",
            {
                "type": NanoKontrolSysexMessage.Type.REQUEST_GLOBAL_CONFIG,
            },
        ),
        (
            RAW_GLOBAL_CONFIG_MSG,
            {
                "type": NanoKontrolSysexMessage.Type.GLOBAL_CONFIG,
            },
        ),
        (
            RAW_SCENE_CONFIG_MSG,
            {
                "type": NanoKontrolSysexMessage.Type.SCENE_CONFIG,
            },
        ),
    ],
)
def test_message_from_raw(raw_str: str, properties):
    m = SysexMessage.from_raw(bytes.fromhex(raw_str))
    print()
    print(m)
    for key, value in properties.items():
        assert getattr(m, key) == value, f"{key}=={getattr(m, key) != {value}}"


def test_message_constructors():
    m = SysexMessage.from_raw(bytes.fromhex())
    print()
    print(m)
    print(m)
    """
    for cls, args in (
        (
            DeviceInquiryReplyMessage,
            {
                "raw_data": bytes.fromhex(
                    "7E 02 06 02 42 37 01 00 00 05 00 01 00"
                )
            },
        ),
        (DeviceInquiryRequestMessage, {}),
        (DataLoadCompletedMessage, {"midi_channel": 1}),
        (DataWriteCompletedMessage, {"midi_channel": 1}),
        (SetSceneNumberMessage, {"midi_channel": 1, "scene_number": 5}),
        (RequestGlobalConfigMessage, {"midi_channel": 1}),
        (RequestCurrentSceneConfigMessage, {"midi_channel": 1}),
        (RequestSaveSceneConfigMessage, {"midi_channel": 1, "scene_number": 5}),
        # (SceneConfigMessage, {"midi_channel": 1}),
        # (GlobalConfigMessage, {"midi_channel": 1}),
    ):
        m = cls(**args)
        assert isinstance(m, cls)
        print(f"{m}")
    """


@pytest.mark.unit
def test_messages():
    """
    payload = bytes.fromhex(
        "51 "
        "70 00 00 01 00 7F 7F 7F "
        "01 7F 6E 6E 6E 6E 4B 4F "
        "00 4E 54 52 4F 4C 20 53 "
        "00 74 75 64 69 6F 00 00 "
        "40 00 00 00 00 00 00 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "61 7F 00 01 00 00 7F 7F "
        "43 7F 7F 04 00 02 00 7F "
        "67 7F 7F 7F 00 00 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "7F 7F 7F 7F 7F 7F 7F 7F "
        "03 7F 7F"
    )

    m = GlobalConfigMessage(midi_channel=5, payload=payload)
    repacked = GlobalConfigMessage.pack_7b(m.unpacked)
    assert repacked == payload[1:-3]
    assert SysexMessage.from_raw(m.serialized()) == m
    """


@pytest.mark.unit
def test_config():
    def dump(d):
        for chunk in batched(enumerate(d), 8):
            print(NanoKontrolSysexMessage.formatted(chunk))

    c = SceneConfig.default(0)
    serialized = c.serialize()
    # dump(serialized)
    # print(len(serialized))


def test_global_config_roundtrip():
    with DeviceConnection("nanoKONTROL Studio") as connection:
        reply = connection.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        midi_channel = reply[-1].midi_channel()

        reply = connection.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.REQUEST_GLOBAL_CONFIG,
                midi_channel=midi_channel,
            )
        )
        assert isinstance(reply[0], NanoKontrolSysexMessage)
        assert reply[0].type == NanoKontrolSysexMessage.Type.GLOBAL_CONFIG
        global_config_message = reply[0]

        # global_config_message.dump()
        global_config = GlobalConfig.from_raw(global_config_message.unpacked)
        global_config.dump()
        # print(global_config.serialize())
        new_global_config_message = NanoKontrolSysexMessage.create(
            type=NanoKontrolSysexMessage.Type.GLOBAL_CONFIG,
            midi_channel=midi_channel,
            unpacked=global_config.serialize(),
        )
        # new_global_config_message.dump()
        assert (
            global_config_message.unpacked[36:]
            == global_config.serialize()[36:]
        )
        assert (
            156
            == len(new_global_config_message.serialized())
            == len(global_config_message.serialized())
        )
        # assert new_global_config_message.payload() == global_config_message.payload()
        assert (
            148
            == len(new_global_config_message.payload)
            == len(global_config_message.payload)
        )


@pytest.mark.system
def test_scene_roundtrip():
    with DeviceConnection("nanoKONTROL Studio") as connection:
        reply = connection.get_reply(DeviceInquiryRequestMessage())
        assert isinstance(reply[-1], DeviceInquiryReplyMessage)
        device_inquiry_reply = reply[-1]
        midi_channel = device_inquiry_reply.midi_channel()

        reply = connection.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.SET_SCENE_NUMBER,
                midi_channel=midi_channel,
                scene_number=0,
            )
        )
        assert any(
            r.type == NanoKontrolSysexMessage.Type.DATA_LOAD_COMPLETED
            for r in reply
        )

        reply = connection.get_reply(
            NanoKontrolSysexMessage.create(
                type=NanoKontrolSysexMessage.Type.REQUEST_CURRENT_SCENE_CONFIG,
                midi_channel=midi_channel,
            )
        )
        reply[0].type == SysexMessage.Type.SCENE_CONFIG
        scene_config_message = reply[0]
        scene_config_message.dump()

        scene_config = SceneConfig.from_raw(scene_config_message.unpacked)
        scene_config.dump()

        # reply = connection.get_reply(DeviceInquiryRequestMessage())
        new_scene_config_message = NanoKontrolSysexMessage.create(
            type=NanoKontrolSysexMessage.Type.SCENE_CONFIG,
            midi_channel=midi_channel,
            unpacked=scene_config.serialize(),
        )

        # reply = self.get_reply(
        #    new_scene_data_message
        # )

        # print()
        # new_scene_data_message.dump()
        assert scene_config_message.unpacked == scene_config.serialize()
        assert new_scene_config_message.payload == scene_config_message.payload


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format=f"%(levelname)-7s %(asctime)s.%(msecs)03d %(name)-12s│ %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    # test_messages()
    # test_config()
    # test_global_config_roundtrip()
    test_scene_roundtrip()
