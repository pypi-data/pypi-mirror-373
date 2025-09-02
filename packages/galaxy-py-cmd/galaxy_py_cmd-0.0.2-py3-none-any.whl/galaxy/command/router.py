#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC,                                    \
                abstractmethod
from collections import OrderedDict
from typing import Any
from importlib import import_module
import sys

from galaxy.utils.base import Component,                \
                              Configurable
from galaxy.service.log import LogService,              \
                               LogAsyncService
from galaxy.command.cmd import Command,                 \
                               AsyncCommand
from galaxy.data.protobuf import cmd_pb2,               \
                                 net_pb2
from galaxy.perfo.decorator import timed,               \
                                   async_timed


class Router(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | None = None
        self.routes: dict[str, Command] | None = None

    def _load(self) -> None:
        super(Router, self)._load()
        [cmd._load() for cmd in self.routes.values()]

    @abstractmethod
    def route(self, data: Any, from_: bytes | None = None) -> Any:
        raise NotImplementedError("Should implement route()")


class ProtobufRouter(Router):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProtobufRouter, self).__init__()

    @timed
    def route(self, payloads: Any, from_: bytes | None = None) -> Any:
        if "route" in self.conf:
            for module_and_class, route_name in self.conf["route"].items():
                parts = module_and_class.split(".")
                module_name = ".".join(parts[:-1])
                class_name = parts[-1]
                if module_name == "":
                    cls = eval(class_name)
                else:
                    import_module(module_name)
                    cls = getattr(sys.modules[module_name], class_name)
                if payloads[0].Is(cls.DESCRIPTOR):
                    cmd = self.routes[route_name]
                    cmd.execute(payloads)


class AsyncRouter(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogAsyncService | None = None
        self.routes: dict[str, AsyncCommand] = OrderedDict({})

    def _load(self) -> None:
        super(AsyncRouter, self)._load()
        [cmd._load() for cmd in self.routes.values()]

    @abstractmethod
    async def route(self, data: Any, from_: bytes | None = None) -> Any:
        raise NotImplementedError("Should implement route()")


class ProtobufAsyncRouter(AsyncRouter):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProtobufAsyncRouter, self).__init__()

    @async_timed
    async def route(self, payloads: list, from_: bytes | None = None) -> Any:
        if "route" in self.conf:
            for module_and_class, route_name in self.conf["route"].items():
                parts = module_and_class.split(".")
                module_name = ".".join(parts[:-1])
                class_name = parts[-1]
                if module_name == "":
                    cls = eval(class_name)
                else:
                    import_module(module_name)
                    cls = getattr(sys.modules[module_name], class_name)
                if payloads[0].Is(cls.DESCRIPTOR):
                    cmd = self.routes[route_name]
                    await cmd.execute(payloads)


class ProtobufCmdAsyncRouter(AsyncRouter):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProtobufCmdAsyncRouter, self).__init__()

    @async_timed
    async def route(self, message: net_pb2.Message, from_: list[bytes] | None = None) -> Any:
        cmd_reqs = []
        for p in message.payload:
            cmd_req = cmd_pb2.CommandRequest()
            cmd_req.ParseFromString(p.value)
            cmd_reqs.append(cmd_req)
        if "route" in self.conf:
            for cmd_req in cmd_reqs:
                if cmd_req.cmd_name in self.conf["route"]:
                    cmd = self.conf["route"][cmd_req.cmd_name]
                    await self.routes[cmd].execute(args=cmd_req.cmd_args,
                                                   message=message,
                                                   cmd_req=cmd_req,
                                                   from_=from_)
                else:
                    await self.routes["not_supported"].execute(args=cmd_req.cmd_args,
                                                               message=message,
                                                               cmd_req=cmd_req,
                                                               from_=from_)
