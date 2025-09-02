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

from abc import ABC,                                                        \
                abstractmethod
from typing import TYPE_CHECKING
from reactivex import of
from reactivex import operators as ops
from uuid import UUID
import yaml

from galaxy.command.constant import CODE_CMD_SUCCESS,                       \
                                    MSG_CMD_SUCCESSFUL
from galaxy.kernel.loop import AsyncioLoop
from galaxy.utils.base import Component,                                    \
                              Configurable
from galaxy.service.service import ServiceAsyncManager,                     \
                                   LogService,                              \
                                   LogAsyncService
from galaxy.data.protobuf import net_pb2,                                   \
                                 cmd_pb2
from galaxy.net.zmq.zmq import ZmqAsyncClient
from galaxy.net.zmq.zmq import ZmqAsyncServer
from galaxy.data.serial import ProtobufSerializer
from galaxy.data.model.factory import CmdResponseFactory,                   \
                                      CmdResponseProtobufFactory,           \
                                      MessageFactory,                       \
                                      MessageProtobufFactory
from galaxy.error.cmd import CmdInvalidParamError,                          \
                             CmdCommandNotSupportedError,                   \
                             CmdInvalidParamsError,                         \
                             CmdStatusNotSupportedError,                    \
                             CmdStartNotSupportedError,                     \
                             CmdStopNotSupportedError,                      \
                             CmdConnectNotSupportedError,                   \
                             CmdCloseNotSupportedError,                     \
                             CmdPauseNotSupportedError,                     \
                             CmdResumeNotSupportedError
from galaxy.perfo.decorator import timed,                                   \
                                   async_timed

if TYPE_CHECKING:
    from galaxy.app.ioc.ioc import IOCManager
    from galaxy.app.ioc.visitor import Visitor


class Command(Component, Configurable, ABC):
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
        self.ioc: IOCManager | None = None

    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError("Should implement execute()")

    def __repr__(self) -> str:
        return "<Command(id='{}')>".format(self.id)


class AsyncCommand(Component, Configurable, ABC):
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
        self.loop: AsyncioLoop | None = None
        self.ioc: IOCManager | None = None

    @abstractmethod
    async def execute(self, *args, **kwargs) -> None:
        raise NotImplementedError("Should implement execute()")

    @timed
    def send_response(self,
                      cmd_srv: ZmqAsyncServer,
                      code: int,
                      result: list,
                      msg: str,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: list[bytes] | bytes) -> None:
        if isinstance(cmd_srv.serializer, ProtobufSerializer):
            source = of(result).pipe(ops.map(lambda d: CmdResponseProtobufFactory.create_response(d, cmd_req, self.id, code, msg)),
                                     ops.map(lambda d: MessageProtobufFactory.create_msg([d], self.id)),
                                     ops.map(lambda d: MessageProtobufFactory.update_msg_before_sending(d, cmd_srv.id)),
                                     ops.map(lambda d: cmd_srv.serializer.serialize(d)),
                                     ops.map(lambda d: cmd_srv.compressor.compress(d)))
        else:
            source = of(result).pipe(ops.map(lambda d: CmdResponseFactory.create_response(d, cmd_req, self.id, code, msg)),
                                     ops.map(lambda d: MessageFactory.create_msg([d], self.id)),
                                     ops.map(lambda d: MessageFactory.update_msg_before_sending(d, cmd_srv.id)),
                                     ops.map(lambda d: cmd_srv.serializer.serialize(d)),
                                     ops.map(lambda d: cmd_srv.compressor.compress(d)))
        source.subscribe(on_next=lambda d: cmd_srv.send(from_ + [d]))

    @timed
    def forward_cmd(self, message: net_pb2.Message, to_client: ZmqAsyncClient, from_: list[bytes]) -> None:
        source = of(message).pipe(ops.map(lambda d: MessageProtobufFactory.update_msg_before_sending(d, to_client.id)),
                                  ops.map(lambda d: to_client.serializer.serialize(d)),
                                  ops.map(lambda d: to_client.compressor.compress(d)))
        source.subscribe(on_next=lambda d: to_client.send(from_ + [d]))

    def __repr__(self) -> str:
        return "<AsyncCommand(id='{}')>".format(self.id)


class CmdNotSupportedProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CmdNotSupportedProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        ex = CmdCommandNotSupportedError(cmd_req.cmd_name)
        self.send_response(cmd_srv,
                           ex.error_code,
                           [],
                           ex.message,
                           cmd_req,
                           from_)


class GetCompStatusProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GetCompStatusProtobufAsyncCommand, self).__init__()
        self.visitor: Visitor | None = None

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "accept"):
                        obj.accept(self.visitor)
                        r = cmd_pb2.StringResult()
                        r.content = yaml.safe_dump(self.visitor.res,
                                                   sort_keys=False,
                                                   default_flow_style=False,
                                                   indent=2,
                                                   allow_unicode=True)
                        res.append(r)
                    else:
                        ex = CmdStatusNotSupportedError(cmd_req.cmd_name, str(arg), internal=e)
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
        else:
            self.ioc.context.accept(self.visitor)
            r = cmd_pb2.StringResult()
            r.content = yaml.safe_dump(self.visitor.res,
                                       sort_keys=False,
                                       default_flow_style=False,
                                       indent=2,
                                       allow_unicode=True)
            res.append(r)

        if code == CODE_CMD_SUCCESS:
            msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
        self.send_response(cmd_srv,
                           code,
                           res,
                           "\n".join(msgs),
                           cmd_req,
                           from_)


class GetCompProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GetCompProtobufAsyncCommand, self).__init__()
        self.visitor: Visitor | None = None

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        if len(args) > 0:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)
        else:
            self.ioc.context.accept(self.visitor)
            r = cmd_pb2.StringResult()
            ydump = yaml.dump(self.visitor.res,
                              sort_keys=False,
                              default_flow_style=False,
                              indent=2,
                              allow_unicode=True).replace("'", "")
            r.content = "compo:\n{}".format(ydump)
            res = [r]
            self.send_response(cmd_srv,
                               CODE_CMD_SUCCESS,
                               res,
                               MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name),
                               cmd_req,
                               from_)


class GetConfProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GetConfProtobufAsyncCommand, self).__init__()
        self.visitor: Visitor | None = None

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        if len(args) > 0:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)
        else:
            self.ioc.context.accept(self.visitor)
            r = cmd_pb2.StringResult()
            ydump = yaml.dump(self.visitor.res,
                              sort_keys=False,
                              default_flow_style=False,
                              indent=2,
                              allow_unicode=True).replace("'", "")
            r.content = "config:\n{}".format(ydump)
            res = [r]
            self.send_response(cmd_srv,
                               CODE_CMD_SUCCESS,
                               res,
                               MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name),
                               cmd_req,
                               from_)


class StartProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(StartProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "start"):
                        await obj.start()
                    else:
                        ex = CmdStartNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class StopProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(StopProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "stop"):
                        await obj.stop()
                    else:
                        ex = CmdStopNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class RestartProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RestartProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "restart"):
                        await obj.restart()
                    elif hasattr(obj, "start") and hasattr(obj, "stop"):
                        await obj.stop()
                        await obj.start()
                    else:
                        ex = CmdStartNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class ConnectProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ConnectProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "connect"):
                        await obj.connect()
                    else:
                        ex = CmdConnectNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class CloseProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CloseProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "close"):
                        await obj.close()
                    else:
                        ex = CmdCloseNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class ReconnectProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ReconnectProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "reconnect"):
                        await obj.reconnect()
                    elif hasattr(obj, "connect") and hasattr(obj, "close"):
                        await obj.close()
                        await obj.connect()
                    else:
                        ex = CmdConnectNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class PauseProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PauseProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "pause"):
                        await obj.pause()
                    else:
                        ex = CmdPauseNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class ResumeProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ResumeProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "resume"):
                        await obj.resume()
                    else:
                        ex = CmdResumeNotSupportedError(cmd_req.cmd_name, str(arg))
                        msgs.append(ex.message)
                        if first_error:
                            code = ex.error_code
                            first_error = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class UpdateConfProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(UpdateConfProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        pass


class CreateCompProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(CreateCompProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        pass


class RemoveCompProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RemoveCompProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        pass


class EnableCompProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(EnableCompProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    obj.enabled = True
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class DisableCompProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(DisableCompProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        srv_mgr = list(self.ioc.context.get_components_by_type(ServiceAsyncManager).values())[0]
        cmd_srv = srv_mgr.managers["net"].services["kernel"].servers["cmd"]
        code = CODE_CMD_SUCCESS
        first_error = True
        res = []
        msgs = []

        if len(args) > 0:
            for arg in args:
                try:
                    obj = self.ioc.context.get_component(UUID(arg))
                    if hasattr(obj, "stop"):
                        await obj.stop()
                    elif hasattr(obj, "close"):
                        await obj.close()
                    obj.enabled = False
                except ValueError as e:
                    ex = CmdInvalidParamError(cmd_req.cmd_name, str(arg), internal=e)
                    msgs.append(ex.message)
                    if first_error:
                        code = ex.error_code
                        first_error = False
            if code == CODE_CMD_SUCCESS:
                msgs.append(MSG_CMD_SUCCESSFUL.format(cmd_req.cmd_name))
            self.send_response(cmd_srv,
                               code,
                               res,
                               "\n".join(msgs),
                               cmd_req,
                               from_)
        else:
            ex = CmdInvalidParamsError(cmd_req.cmd_name)
            self.send_response(cmd_srv,
                               ex.error_code,
                               [],
                               ex.message,
                               cmd_req,
                               from_)


class ExecuteProtobufAsyncCommand(AsyncCommand):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ExecuteProtobufAsyncCommand, self).__init__()

    @async_timed
    async def execute(self,
                      args: list,
                      message: net_pb2.Message,
                      cmd_req: cmd_pb2.CommandRequest,
                      from_: bytes) -> None:
        pass
