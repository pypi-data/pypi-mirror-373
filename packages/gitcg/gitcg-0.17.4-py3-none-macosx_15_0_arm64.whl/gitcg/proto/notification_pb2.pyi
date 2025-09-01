import state_pb2 as _state_pb2
import mutation_pb2 as _mutation_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Notification(_message.Message):
    __slots__ = ("state", "mutation")
    STATE_FIELD_NUMBER: _ClassVar[int]
    MUTATION_FIELD_NUMBER: _ClassVar[int]
    state: _state_pb2.State
    mutation: _containers.RepeatedCompositeFieldContainer[_mutation_pb2.ExposedMutation]
    def __init__(self, state: _Optional[_Union[_state_pb2.State, _Mapping]] = ..., mutation: _Optional[_Iterable[_Union[_mutation_pb2.ExposedMutation, _Mapping]]] = ...) -> None: ...
