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

from uuid import uuid4,                                     \
                 UUID
from abc import ABC,                                        \
                abstractmethod
from typing import Any
from datetime import datetime

from galaxy.utils.base import Component,                    \
                              Configurable
from galaxy.service.service import LogService,              \
                                   LogAsyncService
from galaxy.data.model.cmd import CommandRequest
from galaxy.data.protobuf import cmd_pb2,                   \
                                 uuid_pb2
from galaxy.perfo.decorator import timed


class Interpreter(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create_commands(self, cmd_line: str) -> list[Any]:
        raise NotImplementedError("Should implement create_commands()")


class CmdInterpreter(Interpreter):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CmdInterpreter, self).__init__()

    @timed
    def create_commands(self, cmd_line: str) -> list[CommandRequest]:
        cmd_reqs = []
        cmds = cmd_line.split(";")
        for cmd in [cmd.strip() for cmd in cmds]:
            cmd_req = CommandRequest(uuid4())
            cmd_req.cmd_name = cmd[:cmd.find("(")]
            arg_line = cmd[cmd.find("(") + 1:cmd.find(")")]
            if len(arg_line) > 0:
                args = arg_line.split(",")
                for arg in [arg.strip() for arg in args]:
                    if arg.startswith("\"") and arg.endswith("\"") and len(arg) > 1:
                        cmd_req.cmd_args.append(arg[1:-1])
                    else:
                        cmd_req.cmd_args.append(arg)

            cmd_req.req_by = UUID(self.conf["app_id"])
            cmd_req.req_date = datetime.now().astimezone()
            cmd_reqs.append(cmd_req)
        return cmd_reqs


class CmdProtobufInterpreter(Interpreter):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CmdProtobufInterpreter, self).__init__()

    @timed
    def create_commands(self, cmd_line: str) -> list[cmd_pb2.CommandRequest]:
        cmd_reqs = []
        cmds = cmd_line.split(";")
        for cmd in [cmd.strip() for cmd in cmds]:
            cmd_id = uuid_pb2.UUID()
            cmd_id.value = uuid4().bytes

            cmd_req = cmd_pb2.CommandRequest()
            cmd_req.id.CopyFrom(cmd_id)
            cmd_req.cmd_name = cmd[:cmd.find("(")] if cmd.find("(") >= 0 else cmd
            if cmd.find("(") >= 0:
                arg_line = cmd[cmd.find("(") + 1:cmd.find(")")]
                if len(arg_line) > 0:
                    args = arg_line.split(",")
                    for arg in [arg.strip() for arg in args]:
                        if arg.startswith("\"") and arg.endswith("\"") and len(arg) > 1:
                            cmd_req.cmd_args.append(arg[1:-1])
                        else:
                            cmd_req.cmd_args.append(arg)

            req_by_id = uuid_pb2.UUID()
            req_by_id.value = UUID(self.conf["app_id"]).bytes

            cmd_req.req_by.CopyFrom(req_by_id)
            cmd_req.req_date = datetime.now().isoformat()
            cmd_reqs.append(cmd_req)
        return cmd_reqs


class JupyterInterpreter(object):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(JupyterInterpreter, self).__init__()
