import enums_pb2 as _enums_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PhaseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PHASE_TYPE_INIT_HANDS: _ClassVar[PhaseType]
    PHASE_TYPE_INIT_ACTIVES: _ClassVar[PhaseType]
    PHASE_TYPE_ROLL: _ClassVar[PhaseType]
    PHASE_TYPE_ACTION: _ClassVar[PhaseType]
    PHASE_TYPE_END: _ClassVar[PhaseType]
    PHASE_TYPE_GAME_END: _ClassVar[PhaseType]

class PlayerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYER_STATUS_UNSPECIFIED: _ClassVar[PlayerStatus]
    PLAYER_STATUS_CHOOSING_ACTIVE: _ClassVar[PlayerStatus]
    PLAYER_STATUS_SWITCHING_HANDS: _ClassVar[PlayerStatus]
    PLAYER_STATUS_REROLLING: _ClassVar[PlayerStatus]
    PLAYER_STATUS_ACTING: _ClassVar[PlayerStatus]
    PLAYER_STATUS_SELECTING_CARDS: _ClassVar[PlayerStatus]

class EquipmentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUIPMENT_TYPE_OTHER: _ClassVar[EquipmentType]
    EQUIPMENT_TYPE_WEAPON: _ClassVar[EquipmentType]
    EQUIPMENT_TYPE_ARTIFACT: _ClassVar[EquipmentType]
    EQUIPMENT_TYPE_TECHNIQUE: _ClassVar[EquipmentType]
PHASE_TYPE_INIT_HANDS: PhaseType
PHASE_TYPE_INIT_ACTIVES: PhaseType
PHASE_TYPE_ROLL: PhaseType
PHASE_TYPE_ACTION: PhaseType
PHASE_TYPE_END: PhaseType
PHASE_TYPE_GAME_END: PhaseType
PLAYER_STATUS_UNSPECIFIED: PlayerStatus
PLAYER_STATUS_CHOOSING_ACTIVE: PlayerStatus
PLAYER_STATUS_SWITCHING_HANDS: PlayerStatus
PLAYER_STATUS_REROLLING: PlayerStatus
PLAYER_STATUS_ACTING: PlayerStatus
PLAYER_STATUS_SELECTING_CARDS: PlayerStatus
EQUIPMENT_TYPE_OTHER: EquipmentType
EQUIPMENT_TYPE_WEAPON: EquipmentType
EQUIPMENT_TYPE_ARTIFACT: EquipmentType
EQUIPMENT_TYPE_TECHNIQUE: EquipmentType

class State(_message.Message):
    __slots__ = ("phase", "round_number", "current_turn", "winner", "player")
    PHASE_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TURN_FIELD_NUMBER: _ClassVar[int]
    WINNER_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    phase: PhaseType
    round_number: int
    current_turn: int
    winner: int
    player: _containers.RepeatedCompositeFieldContainer[PlayerState]
    def __init__(self, phase: _Optional[_Union[PhaseType, str]] = ..., round_number: _Optional[int] = ..., current_turn: _Optional[int] = ..., winner: _Optional[int] = ..., player: _Optional[_Iterable[_Union[PlayerState, _Mapping]]] = ...) -> None: ...

class PlayerState(_message.Message):
    __slots__ = ("active_character_id", "character", "combat_status", "summon", "support", "dice", "pile_card", "hand_card", "status", "declared_end", "legend_used", "initiative_skill")
    ACTIVE_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    COMBAT_STATUS_FIELD_NUMBER: _ClassVar[int]
    SUMMON_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    DICE_FIELD_NUMBER: _ClassVar[int]
    PILE_CARD_FIELD_NUMBER: _ClassVar[int]
    HAND_CARD_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DECLARED_END_FIELD_NUMBER: _ClassVar[int]
    LEGEND_USED_FIELD_NUMBER: _ClassVar[int]
    INITIATIVE_SKILL_FIELD_NUMBER: _ClassVar[int]
    active_character_id: int
    character: _containers.RepeatedCompositeFieldContainer[CharacterState]
    combat_status: _containers.RepeatedCompositeFieldContainer[EntityState]
    summon: _containers.RepeatedCompositeFieldContainer[EntityState]
    support: _containers.RepeatedCompositeFieldContainer[EntityState]
    dice: _containers.RepeatedScalarFieldContainer[_enums_pb2.DiceType]
    pile_card: _containers.RepeatedCompositeFieldContainer[CardState]
    hand_card: _containers.RepeatedCompositeFieldContainer[CardState]
    status: PlayerStatus
    declared_end: bool
    legend_used: bool
    initiative_skill: _containers.RepeatedCompositeFieldContainer[SkillInfo]
    def __init__(self, active_character_id: _Optional[int] = ..., character: _Optional[_Iterable[_Union[CharacterState, _Mapping]]] = ..., combat_status: _Optional[_Iterable[_Union[EntityState, _Mapping]]] = ..., summon: _Optional[_Iterable[_Union[EntityState, _Mapping]]] = ..., support: _Optional[_Iterable[_Union[EntityState, _Mapping]]] = ..., dice: _Optional[_Iterable[_Union[_enums_pb2.DiceType, str]]] = ..., pile_card: _Optional[_Iterable[_Union[CardState, _Mapping]]] = ..., hand_card: _Optional[_Iterable[_Union[CardState, _Mapping]]] = ..., status: _Optional[_Union[PlayerStatus, str]] = ..., declared_end: bool = ..., legend_used: bool = ..., initiative_skill: _Optional[_Iterable[_Union[SkillInfo, _Mapping]]] = ...) -> None: ...

class CharacterState(_message.Message):
    __slots__ = ("id", "definition_id", "entity", "defeated", "health", "max_health", "energy", "max_energy", "aura", "tags", "special_energy_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    DEFEATED_FIELD_NUMBER: _ClassVar[int]
    HEALTH_FIELD_NUMBER: _ClassVar[int]
    MAX_HEALTH_FIELD_NUMBER: _ClassVar[int]
    ENERGY_FIELD_NUMBER: _ClassVar[int]
    MAX_ENERGY_FIELD_NUMBER: _ClassVar[int]
    AURA_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_ENERGY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    definition_id: int
    entity: _containers.RepeatedCompositeFieldContainer[EntityState]
    defeated: bool
    health: int
    max_health: int
    energy: int
    max_energy: int
    aura: _enums_pb2.AuraType
    tags: int
    special_energy_name: str
    def __init__(self, id: _Optional[int] = ..., definition_id: _Optional[int] = ..., entity: _Optional[_Iterable[_Union[EntityState, _Mapping]]] = ..., defeated: bool = ..., health: _Optional[int] = ..., max_health: _Optional[int] = ..., energy: _Optional[int] = ..., max_energy: _Optional[int] = ..., aura: _Optional[_Union[_enums_pb2.AuraType, str]] = ..., tags: _Optional[int] = ..., special_energy_name: _Optional[str] = ...) -> None: ...

class EntityState(_message.Message):
    __slots__ = ("id", "definition_id", "description_dictionary", "variable_name", "variable_value", "hint_text", "hint_icon", "has_usage_per_round", "equipment")
    class DescriptionDictionaryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_DICTIONARY_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    HINT_TEXT_FIELD_NUMBER: _ClassVar[int]
    HINT_ICON_FIELD_NUMBER: _ClassVar[int]
    HAS_USAGE_PER_ROUND_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    definition_id: int
    description_dictionary: _containers.ScalarMap[str, str]
    variable_name: str
    variable_value: int
    hint_text: str
    hint_icon: int
    has_usage_per_round: bool
    equipment: EquipmentType
    def __init__(self, id: _Optional[int] = ..., definition_id: _Optional[int] = ..., description_dictionary: _Optional[_Mapping[str, str]] = ..., variable_name: _Optional[str] = ..., variable_value: _Optional[int] = ..., hint_text: _Optional[str] = ..., hint_icon: _Optional[int] = ..., has_usage_per_round: bool = ..., equipment: _Optional[_Union[EquipmentType, str]] = ...) -> None: ...

class CardState(_message.Message):
    __slots__ = ("id", "definition_id", "description_dictionary", "definition_cost", "tags")
    class DescriptionDictionaryEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_DICTIONARY_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_COST_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    id: int
    definition_id: int
    description_dictionary: _containers.ScalarMap[str, str]
    definition_cost: _containers.RepeatedCompositeFieldContainer[_enums_pb2.DiceRequirement]
    tags: int
    def __init__(self, id: _Optional[int] = ..., definition_id: _Optional[int] = ..., description_dictionary: _Optional[_Mapping[str, str]] = ..., definition_cost: _Optional[_Iterable[_Union[_enums_pb2.DiceRequirement, _Mapping]]] = ..., tags: _Optional[int] = ...) -> None: ...

class SkillInfo(_message.Message):
    __slots__ = ("definition_id", "definition_cost")
    DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_COST_FIELD_NUMBER: _ClassVar[int]
    definition_id: int
    definition_cost: _containers.RepeatedCompositeFieldContainer[_enums_pb2.DiceRequirement]
    def __init__(self, definition_id: _Optional[int] = ..., definition_cost: _Optional[_Iterable[_Union[_enums_pb2.DiceRequirement, _Mapping]]] = ...) -> None: ...
