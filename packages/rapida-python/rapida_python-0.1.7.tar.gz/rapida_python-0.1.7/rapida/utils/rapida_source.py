#  Copyright (c) 2024. Rapida
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#  Author: Prashant <prashant@rapida.ai>

from enum import Enum
import logging

from rapida.clients.protos import common_pb2


class RapidaSource(Enum):
    """
    Rapida Source
    """

    WEB_PLUGIN = "web-plugin"
    DEBUGGER = "debugger"
    SDK = "sdk"
    PHONE_CALL = "phone-call"
    WHATSAPP = "whatsapp"

    MAPPING = {
        WEB_PLUGIN: common_pb2.Source.WEB_PLUGIN,
        DEBUGGER: common_pb2.Source.DEBUGGER,
        SDK: common_pb2.Source.SDK,
        PHONE_CALL: common_pb2.Source.PHONE_CALL,
        WHATSAPP: common_pb2.Source.WHATSAPP,
    }

    def get(self) -> str:
        return str(self.value)

    def source(self) -> common_pb2.Source:
        mapping = {
            RapidaSource.WEB_PLUGIN: common_pb2.Source.WEB_PLUGIN,
            RapidaSource.DEBUGGER: common_pb2.Source.DEBUGGER,
            RapidaSource.SDK: common_pb2.Source.SDK,
            RapidaSource.PHONE_CALL: common_pb2.Source.PHONE_CALL,
            RapidaSource.WHATSAPP: common_pb2.Source.WHATSAPP,
        }
        return mapping.get(self)

    @staticmethod
    def from_str(label: str):
        source_map = {
            "web-plugin": RapidaSource.WEB_PLUGIN,
            "debugger": RapidaSource.DEBUGGER,
            "sdk": RapidaSource.SDK,
            "phone-call": RapidaSource.PHONE_CALL,
            "whatsapp": RapidaSource.WHATSAPP,
        }

        result = source_map.get(label.lower(), RapidaSource.WEB_PLUGIN)
        if result == RapidaSource.WEB_PLUGIN and label.lower() != "web-plugin":
            logging.warning(
                f"{label} is not supported. Supported sources are: "
                "'web-plugin', 'debugger', 'sdk', 'phone-call', 'whatsapp'."
            )
        return result
