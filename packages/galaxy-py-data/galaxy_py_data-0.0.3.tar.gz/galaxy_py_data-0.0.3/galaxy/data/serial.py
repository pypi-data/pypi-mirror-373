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

from abc import ABC,                                \
                abstractmethod
from typing import Any
import msgpack
import pickle

from galaxy.utils.base import Component
from galaxy.data.protobuf.net_pb2 import Message


class Serializer(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(Serializer, self).__init__()

    @abstractmethod
    def serialize(self, data: Any) -> Any:
        raise NotImplementedError("Should implement serialize()")

    @abstractmethod
    def deserialize(self, data: Any) -> Any:
        raise NotImplementedError("Should implement deserialize()")


class NoSerializer(Serializer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(NoSerializer, self).__init__()

    def serialize(self, data: Any) -> bytes:
        return data

    def deserialize(self, data: Any) -> Any:
        if isinstance(data, list):
            if len(data) == 1:
                return data[0]
        return data


class PickleSerializer(Serializer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(PickleSerializer, self).__init__()

    def serialize(self, data: Any) -> bytes:
        return pickle.dumps(data)

    def deserialize(self, data: Any) -> Any:
        if isinstance(data, list):
            if len(data) == 1:
                return pickle.load(data[0])
            return [pickle.load(d) for d in data]
        return pickle.load(data)


class MsgPackSerializer(Serializer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MsgPackSerializer, self).__init__()

    def serialize(self, data: Any) -> bytes:
        return msgpack.packb(data)

    def deserialize(self, data: Any) -> Any:
        if isinstance(data, list):
            if len(data) == 1:
                return msgpack.unpackb(data[0])
            return [msgpack.unpackb(d) for d in data]
        return msgpack.unpackb(data)


class ProtobufSerializer(Serializer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ProtobufSerializer, self).__init__()

    def serialize(self, data: Any) -> bytes:
        return data.SerializeToString()

    @abstractmethod
    def deserialize(self, data: Any) -> Any:
        raise NotImplementedError("Should implement deserialize()")


class MessageProtobufSerializer(ProtobufSerializer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MessageProtobufSerializer, self).__init__()

    def deserialize(self, data: Any) -> Message:
        if isinstance(data, list):
            if len(data) == 1:
                res = Message()
                res.ParseFromString(data[0])
                return res
            res = []
            for d in data:
                msg = Message()
                res.append(msg.ParseFromString(d))
            return res
        res = Message()
        res.ParseFromString(data)
        return res
