import enums_pb2 as _enums_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchActiveAction(_message.Message):
    __slots__ = ("character_id", "character_definition_id")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    character_definition_id: int
    def __init__(self, character_id: _Optional[int] = ..., character_definition_id: _Optional[int] = ...) -> None: ...

class PlayCardAction(_message.Message):
    __slots__ = ("card_id", "card_definition_id", "target_ids", "will_be_effectless")
    CARD_ID_FIELD_NUMBER: _ClassVar[int]
    CARD_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_IDS_FIELD_NUMBER: _ClassVar[int]
    WILL_BE_EFFECTLESS_FIELD_NUMBER: _ClassVar[int]
    card_id: int
    card_definition_id: int
    target_ids: _containers.RepeatedScalarFieldContainer[int]
    will_be_effectless: bool
    def __init__(self, card_id: _Optional[int] = ..., card_definition_id: _Optional[int] = ..., target_ids: _Optional[_Iterable[int]] = ..., will_be_effectless: bool = ...) -> None: ...

class UseSkillAction(_message.Message):
    __slots__ = ("skill_definition_id", "target_ids", "main_damage_target_id")
    SKILL_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_IDS_FIELD_NUMBER: _ClassVar[int]
    MAIN_DAMAGE_TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    skill_definition_id: int
    target_ids: _containers.RepeatedScalarFieldContainer[int]
    main_damage_target_id: int
    def __init__(self, skill_definition_id: _Optional[int] = ..., target_ids: _Optional[_Iterable[int]] = ..., main_damage_target_id: _Optional[int] = ...) -> None: ...

class ElementalTuningAction(_message.Message):
    __slots__ = ("removed_card_id", "target_dice")
    REMOVED_CARD_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_DICE_FIELD_NUMBER: _ClassVar[int]
    removed_card_id: int
    target_dice: _enums_pb2.DiceType
    def __init__(self, removed_card_id: _Optional[int] = ..., target_dice: _Optional[_Union[_enums_pb2.DiceType, str]] = ...) -> None: ...

class DeclareEndAction(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
