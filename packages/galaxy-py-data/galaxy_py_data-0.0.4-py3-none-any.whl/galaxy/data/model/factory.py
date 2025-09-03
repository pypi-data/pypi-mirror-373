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

from datetime import datetime
from google.protobuf import any_pb2
from uuid import uuid4

from galaxy.data.model.net import Message
from galaxy.data.model.cmd import CommandRequest,       \
                                  CommandResponse
from galaxy.utils.type import Id
from galaxy.data.protobuf import net_pb2,               \
                                 cmd_pb2,               \
                                 uuid_pb2


class MessageFactory(object):
    """
    classdocs
    """

    @staticmethod
    def create_msg(payload: list, create_by: Id) -> Message:
        msg = Message(uuid4())
        msg.create_date = datetime.now().astimezone()
        msg.create_by = create_by
        msg.payload = payload
        return msg

    @staticmethod
    def update_msg_before_sending(msg: Message, send_by: Id) -> Message:
        msg.send_date = datetime.now().astimezone()
        msg.send_by = send_by
        return msg


class MessageProtobufFactory(object):
    """
    classdocs
    """

    @staticmethod
    def create_msg(payload: list, create_by: Id) -> net_pb2.Message:
        msg = net_pb2.Message()

        msg_id = uuid_pb2.UUID()
        msg_id.value = uuid4().bytes

        create_by_id = uuid_pb2.UUID()
        create_by_id.value = create_by.bytes

        msg.id.CopyFrom(msg_id)
        msg.create_date = datetime.now().isoformat()
        msg.create_by.CopyFrom(create_by_id)

        for p in payload:
            any_payload = any_pb2.Any()
            any_payload.Pack(p)
            msg.payload.append(any_payload)
        return msg

    @staticmethod
    def update_msg_before_sending(msg: Message, send_by: Id) -> Message:
        send_by_id = uuid_pb2.UUID()
        send_by_id.value = send_by.bytes

        msg.send_date = datetime.now().isoformat()
        msg.send_by.CopyFrom(send_by_id)
        return msg


class CmdResponseFactory(object):
    """
    classdocs
    """

    @staticmethod
    def create_response(result: list,
                        cmd_req: CommandRequest,
                        rep_by: Id,
                        code: int,
                        msg: str) -> CommandResponse:
        cmd_resp = CommandResponse(uuid4())
        cmd_resp.req_id = cmd_req.id
        cmd_resp.rep_date = datetime.now().astimezone()
        cmd_resp.rep_by = rep_by
        cmd_resp.code = code
        cmd_resp.msg = msg
        cmd_resp.result = result
        return cmd_resp


class CmdResponseProtobufFactory(object):
    """
    classdocs
    """

    @staticmethod
    def create_response(result: list,
                        cmd_req: cmd_pb2.CommandRequest,
                        rep_by: Id,
                        code: int,
                        msg: str) -> cmd_pb2.CommandResponse:
        resp_id = uuid_pb2.UUID()
        resp_id.value = uuid4().bytes

        cmd_resp = cmd_pb2.CommandResponse()
        cmd_resp.id.CopyFrom(resp_id)
        cmd_resp.req_id.CopyFrom(cmd_req.id)
        cmd_resp.rep_date = datetime.now().isoformat()

        rep_by_id = uuid_pb2.UUID()
        rep_by_id.value = rep_by.bytes
        cmd_resp.rep_by.CopyFrom(rep_by_id)

        cmd_resp.code = code
        cmd_resp.msg = msg

        for res in result:
            any_res = any_pb2.Any()
            any_res.Pack(res)
            cmd_resp.result.append(any_res)
        return cmd_resp
