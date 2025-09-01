#!/usr/bin/env python3
#
# nanokontrol_config - Configurator for Korg nanoKONTROL Studio
# Copyright (C) 2025 - Frans Fürst
#
# nanokontrol_config is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# nanokontrol_config is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details at
#  <http://www.gnu.org/licenses/>.
#
# Anyway this project is not free for commercial machine learning. If you're
# using any content of this repository to train any sort of machine learned
# model (e.g. LLMs), you agree to make the whole model trained with this
# repository and all data needed to train (i.e. reproduce) the model publicly
# and freely available (i.e. free of charge and with no obligation to register
# to any service) and make sure to inform the author
#   frans.fuerst@protonmail.com via email how to get and use that model and any
# sources needed to train it.

"""The nanokontrol-config CLI interface"""

import logging
import sys
from argparse import ArgumentParser
from argparse import Namespace as Args
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path

import mido

from nanokontrol_config.nanokontrol_studio import (
    Configuration,
    DeviceConnection,
    from_yaml,
    to_yaml,
)


def fn_info(args: Args) -> None:
    for port_name in mido.get_input_names():
        print(port_name)
    print()
    for port_name in mido.get_output_names():
        print(port_name)
    print()
    for port_name in mido.get_ioport_names():
        print(port_name)
    print()


def fn_watch(args: Args) -> None:
    with DeviceConnection(args.port) as connection:
        connection.watch_messages()


def fn_export_config(args: Args) -> None:
    with DeviceConnection(args.port) as connection:
        current_config = Configuration(
            global_config=connection.read_global_config(),
            scene_config=tuple(
                connection.read_scene_config(i) for i in range(5)
            ),
        )
        # current_config.global_config.dump()
        for i in range(1):
            current_config.scene_config[i].dump()
    if args.output.name == "-":
        sys.stdout.write(to_yaml(current_config))
    else:
        with args.output.open("w") as output_file:
            output_file.write(to_yaml(current_config))


def fn_set_config(args: Args) -> None:
    with args.input.open() as input_file:
        c = from_yaml(input_file)
    with DeviceConnection(args.port) as connection:
        connection.write_global_config(c.global_config)
        for i in range(5):
            connection.write_scene_config(i, c.scene_config[i])


def fn_patch_config(args: Args) -> None:
    raise NotImplementedError("sorry, not yet")


def parse_args(argv: Sequence[str] | None = None) -> Args:
    parser = ArgumentParser(__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--port", "-p", type=str, default="nanoKONTROL Studio")

    parser.set_defaults(func=lambda *_: parser.print_usage())
    subparsers = parser.add_subparsers(
        help="available commands", metavar="CMD"
    )

    parser_info = subparsers.add_parser("help")
    parser_info.set_defaults(func=lambda *_: parser.print_help())

    parser_export = subparsers.add_parser("export-config", aliases=["e"])
    parser_export.set_defaults(func=fn_export_config)
    parser_export.add_argument(
        "--output", "-o", type=Path, default="nanoKontrol_Studio-config.yaml"
    )

    parser_set = subparsers.add_parser("set-config", aliases=["s"])
    parser_set.set_defaults(func=fn_set_config)
    parser_set.add_argument(
        "--input", "-i", type=Path, default="nanoKontrol_Studio-config.yaml"
    )

    parser_patch = subparsers.add_parser("patch-config", aliases=["p"])
    parser_patch.set_defaults(func=fn_patch_config)

    parser_watch = subparsers.add_parser("watch", aliases=["w"])
    parser_watch.set_defaults(func=fn_watch)

    parser_info = subparsers.add_parser("info", aliases=["i"])
    parser_info.set_defaults(func=fn_info)

    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        format=f"%(levelname)-7s %(asctime)s.%(msecs)03d %(name)-12s│ %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    with suppress(KeyboardInterrupt):
        args.func(args)


if __name__ == "__main__":
    main()
