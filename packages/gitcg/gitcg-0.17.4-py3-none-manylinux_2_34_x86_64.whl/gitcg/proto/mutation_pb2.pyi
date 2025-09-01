import enums_pb2 as _enums_pb2
import state_pb2 as _state_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CardArea(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CARD_AREA_HAND: _ClassVar[CardArea]
    CARD_AREA_PILE: _ClassVar[CardArea]

class TransferCardReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSFER_CARD_REASON_UNSPECIFIED: _ClassVar[TransferCardReason]
    TRANSFER_CARD_REASON_SWITCH: _ClassVar[TransferCardReason]
    TRANSFER_CARD_REASON_DRAW: _ClassVar[TransferCardReason]
    TRANSFER_CARD_REASON_UNDRAW: _ClassVar[TransferCardReason]
    TRANSFER_CARD_REASON_STEAL: _ClassVar[TransferCardReason]
    TRANSFER_CARD_REASON_SWAP: _ClassVar[TransferCardReason]

class SwitchActiveFromAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SWITCH_ACTIVE_FROM_ACTION_NONE: _ClassVar[SwitchActiveFromAction]
    SWITCH_ACTIVE_FROM_ACTION_SLOW: _ClassVar[SwitchActiveFromAction]
    SWITCH_ACTIVE_FROM_ACTION_FAST: _ClassVar[SwitchActiveFromAction]

class RemoveCardReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REMOVE_CARD_REASON_UNSPECIFIED: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_PLAY: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_ELEMENTAL_TUNING: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_HANDS_OVERFLOW: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_DISPOSED: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_PLAY_NO_EFFECT: _ClassVar[RemoveCardReason]
    REMOVE_CARD_REASON_ON_DRAW_TRIGGERED: _ClassVar[RemoveCardReason]

class EntityArea(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTITY_AREA_UNSPECIFIED: _ClassVar[EntityArea]
    ENTITY_AREA_CHARACTER: _ClassVar[EntityArea]
    ENTITY_AREA_COMBAT_STATUS: _ClassVar[EntityArea]
    ENTITY_AREA_SUMMON: _ClassVar[EntityArea]
    ENTITY_AREA_SUPPORT: _ClassVar[EntityArea]

class ModifyDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODIFY_DIRECTION_UNSPECIFIED: _ClassVar[ModifyDirection]
    MODIFY_DIRECTION_INCREASE: _ClassVar[ModifyDirection]
    MODIFY_DIRECTION_DECREASE: _ClassVar[ModifyDirection]

class ResetDiceReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESET_DICE_REASON_UNSPECIFIED: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_ROLL: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_CONSUME: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_ELEMENTAL_TUNING: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_GENERATE: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_CONVERT: _ClassVar[ResetDiceReason]
    RESET_DICE_REASON_ABSORB: _ClassVar[ResetDiceReason]

class HealKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEAL_KIND_NOT_A_HEAL: _ClassVar[HealKind]
    HEAL_KIND_COMMON: _ClassVar[HealKind]
    HEAL_KIND_IMMUNE_DEFEATED: _ClassVar[HealKind]
    HEAL_KIND_REVIVE: _ClassVar[HealKind]
    HEAL_KIND_INCREASE_MAX_HEALTH: _ClassVar[HealKind]
    HEAL_KIND_DISTRIBUTION: _ClassVar[HealKind]

class SkillType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SKILL_TYPE_TRIGGERED: _ClassVar[SkillType]
    SKILL_TYPE_CHARACTER_PASSIVE: _ClassVar[SkillType]
    SKILL_TYPE_NORMAL: _ClassVar[SkillType]
    SKILL_TYPE_ELEMENTAL: _ClassVar[SkillType]
    SKILL_TYPE_BURST: _ClassVar[SkillType]
    SKILL_TYPE_TECHNIQUE: _ClassVar[SkillType]

class PlayerFlag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYER_FLAG_UNSPECIFIED: _ClassVar[PlayerFlag]
    PLAYER_FLAG_DECLARED_END: _ClassVar[PlayerFlag]
    PLAYER_FLAG_LEGEND_USED: _ClassVar[PlayerFlag]
CARD_AREA_HAND: CardArea
CARD_AREA_PILE: CardArea
TRANSFER_CARD_REASON_UNSPECIFIED: TransferCardReason
TRANSFER_CARD_REASON_SWITCH: TransferCardReason
TRANSFER_CARD_REASON_DRAW: TransferCardReason
TRANSFER_CARD_REASON_UNDRAW: TransferCardReason
TRANSFER_CARD_REASON_STEAL: TransferCardReason
TRANSFER_CARD_REASON_SWAP: TransferCardReason
SWITCH_ACTIVE_FROM_ACTION_NONE: SwitchActiveFromAction
SWITCH_ACTIVE_FROM_ACTION_SLOW: SwitchActiveFromAction
SWITCH_ACTIVE_FROM_ACTION_FAST: SwitchActiveFromAction
REMOVE_CARD_REASON_UNSPECIFIED: RemoveCardReason
REMOVE_CARD_REASON_PLAY: RemoveCardReason
REMOVE_CARD_REASON_ELEMENTAL_TUNING: RemoveCardReason
REMOVE_CARD_REASON_HANDS_OVERFLOW: RemoveCardReason
REMOVE_CARD_REASON_DISPOSED: RemoveCardReason
REMOVE_CARD_REASON_PLAY_NO_EFFECT: RemoveCardReason
REMOVE_CARD_REASON_ON_DRAW_TRIGGERED: RemoveCardReason
ENTITY_AREA_UNSPECIFIED: EntityArea
ENTITY_AREA_CHARACTER: EntityArea
ENTITY_AREA_COMBAT_STATUS: EntityArea
ENTITY_AREA_SUMMON: EntityArea
ENTITY_AREA_SUPPORT: EntityArea
MODIFY_DIRECTION_UNSPECIFIED: ModifyDirection
MODIFY_DIRECTION_INCREASE: ModifyDirection
MODIFY_DIRECTION_DECREASE: ModifyDirection
RESET_DICE_REASON_UNSPECIFIED: ResetDiceReason
RESET_DICE_REASON_ROLL: ResetDiceReason
RESET_DICE_REASON_CONSUME: ResetDiceReason
RESET_DICE_REASON_ELEMENTAL_TUNING: ResetDiceReason
RESET_DICE_REASON_GENERATE: ResetDiceReason
RESET_DICE_REASON_CONVERT: ResetDiceReason
RESET_DICE_REASON_ABSORB: ResetDiceReason
HEAL_KIND_NOT_A_HEAL: HealKind
HEAL_KIND_COMMON: HealKind
HEAL_KIND_IMMUNE_DEFEATED: HealKind
HEAL_KIND_REVIVE: HealKind
HEAL_KIND_INCREASE_MAX_HEALTH: HealKind
HEAL_KIND_DISTRIBUTION: HealKind
SKILL_TYPE_TRIGGERED: SkillType
SKILL_TYPE_CHARACTER_PASSIVE: SkillType
SKILL_TYPE_NORMAL: SkillType
SKILL_TYPE_ELEMENTAL: SkillType
SKILL_TYPE_BURST: SkillType
SKILL_TYPE_TECHNIQUE: SkillType
PLAYER_FLAG_UNSPECIFIED: PlayerFlag
PLAYER_FLAG_DECLARED_END: PlayerFlag
PLAYER_FLAG_LEGEND_USED: PlayerFlag

class ExposedMutation(_message.Message):
    __slots__ = ("change_phase", "step_round", "switch_turn", "set_winner", "transfer_card", "switch_active", "remove_card", "create_card", "create_character", "create_entity", "remove_entity", "modify_entity_var", "transform_definition", "reset_dice", "damage", "apply_aura", "skill_used", "player_status_change", "swap_character_position", "set_player_flag", "reroll_done", "switch_hands_done", "choose_active_done", "select_card_done", "handle_event")
    CHANGE_PHASE_FIELD_NUMBER: _ClassVar[int]
    STEP_ROUND_FIELD_NUMBER: _ClassVar[int]
    SWITCH_TURN_FIELD_NUMBER: _ClassVar[int]
    SET_WINNER_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_CARD_FIELD_NUMBER: _ClassVar[int]
    SWITCH_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    REMOVE_CARD_FIELD_NUMBER: _ClassVar[int]
    CREATE_CARD_FIELD_NUMBER: _ClassVar[int]
    CREATE_CHARACTER_FIELD_NUMBER: _ClassVar[int]
    CREATE_ENTITY_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ENTITY_FIELD_NUMBER: _ClassVar[int]
    MODIFY_ENTITY_VAR_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    RESET_DICE_FIELD_NUMBER: _ClassVar[int]
    DAMAGE_FIELD_NUMBER: _ClassVar[int]
    APPLY_AURA_FIELD_NUMBER: _ClassVar[int]
    SKILL_USED_FIELD_NUMBER: _ClassVar[int]
    PLAYER_STATUS_CHANGE_FIELD_NUMBER: _ClassVar[int]
    SWAP_CHARACTER_POSITION_FIELD_NUMBER: _ClassVar[int]
    SET_PLAYER_FLAG_FIELD_NUMBER: _ClassVar[int]
    REROLL_DONE_FIELD_NUMBER: _ClassVar[int]
    SWITCH_HANDS_DONE_FIELD_NUMBER: _ClassVar[int]
    CHOOSE_ACTIVE_DONE_FIELD_NUMBER: _ClassVar[int]
    SELECT_CARD_DONE_FIELD_NUMBER: _ClassVar[int]
    HANDLE_EVENT_FIELD_NUMBER: _ClassVar[int]
    change_phase: ChangePhaseEM
    step_round: StepRoundEM
    switch_turn: SwitchTurnEM
    set_winner: SetWinnerEM
    transfer_card: TransferCardEM
    switch_active: SwitchActiveEM
    remove_card: RemoveCardEM
    create_card: CreateCardEM
    create_character: CreateCharacterEM
    create_entity: CreateEntityEM
    remove_entity: RemoveEntityEM
    modify_entity_var: ModifyEntityVarEM
    transform_definition: TransformDefinitionEM
    reset_dice: ResetDiceEM
    damage: DamageEM
    apply_aura: ApplyAuraEM
    skill_used: SkillUsedEM
    player_status_change: PlayerStatusChangeEM
    swap_character_position: SwapCharacterPositionEM
    set_player_flag: SetPlayerFlagEM
    reroll_done: RerollDoneEM
    switch_hands_done: SwitchHandsDoneEM
    choose_active_done: ChooseActiveDoneEM
    select_card_done: SelectCardDoneEM
    handle_event: HandleEventEM
    def __init__(self, change_phase: _Optional[_Union[ChangePhaseEM, _Mapping]] = ..., step_round: _Optional[_Union[StepRoundEM, _Mapping]] = ..., switch_turn: _Optional[_Union[SwitchTurnEM, _Mapping]] = ..., set_winner: _Optional[_Union[SetWinnerEM, _Mapping]] = ..., transfer_card: _Optional[_Union[TransferCardEM, _Mapping]] = ..., switch_active: _Optional[_Union[SwitchActiveEM, _Mapping]] = ..., remove_card: _Optional[_Union[RemoveCardEM, _Mapping]] = ..., create_card: _Optional[_Union[CreateCardEM, _Mapping]] = ..., create_character: _Optional[_Union[CreateCharacterEM, _Mapping]] = ..., create_entity: _Optional[_Union[CreateEntityEM, _Mapping]] = ..., remove_entity: _Optional[_Union[RemoveEntityEM, _Mapping]] = ..., modify_entity_var: _Optional[_Union[ModifyEntityVarEM, _Mapping]] = ..., transform_definition: _Optional[_Union[TransformDefinitionEM, _Mapping]] = ..., reset_dice: _Optional[_Union[ResetDiceEM, _Mapping]] = ..., damage: _Optional[_Union[DamageEM, _Mapping]] = ..., apply_aura: _Optional[_Union[ApplyAuraEM, _Mapping]] = ..., skill_used: _Optional[_Union[SkillUsedEM, _Mapping]] = ..., player_status_change: _Optional[_Union[PlayerStatusChangeEM, _Mapping]] = ..., swap_character_position: _Optional[_Union[SwapCharacterPositionEM, _Mapping]] = ..., set_player_flag: _Optional[_Union[SetPlayerFlagEM, _Mapping]] = ..., reroll_done: _Optional[_Union[RerollDoneEM, _Mapping]] = ..., switch_hands_done: _Optional[_Union[SwitchHandsDoneEM, _Mapping]] = ..., choose_active_done: _Optional[_Union[ChooseActiveDoneEM, _Mapping]] = ..., select_card_done: _Optional[_Union[SelectCardDoneEM, _Mapping]] = ..., handle_event: _Optional[_Union[HandleEventEM, _Mapping]] = ...) -> None: ...

class ChangePhaseEM(_message.Message):
    __slots__ = ("new_phase",)
    NEW_PHASE_FIELD_NUMBER: _ClassVar[int]
    new_phase: _state_pb2.PhaseType
    def __init__(self, new_phase: _Optional[_Union[_state_pb2.PhaseType, str]] = ...) -> None: ...

class StepRoundEM(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SwitchTurnEM(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetWinnerEM(_message.Message):
    __slots__ = ("winner",)
    WINNER_FIELD_NUMBER: _ClassVar[int]
    winner: int
    def __init__(self, winner: _Optional[int] = ...) -> None: ...

class TransferCardEM(_message.Message):
    __slots__ = ("who", "to", "transfer_to_opp", "target_index", "card", "reason")
    WHO_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    TRANSFER_TO_OPP_FIELD_NUMBER: _ClassVar[int]
    TARGET_INDEX_FIELD_NUMBER: _ClassVar[int]
    CARD_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    who: int
    to: CardArea
    transfer_to_opp: bool
    target_index: int
    card: _state_pb2.CardState
    reason: TransferCardReason
    def __init__(self, who: _Optional[int] = ..., to: _Optional[_Union[CardArea, str]] = ..., transfer_to_opp: bool = ..., target_index: _Optional[int] = ..., card: _Optional[_Union[_state_pb2.CardState, _Mapping]] = ..., reason: _Optional[_Union[TransferCardReason, str]] = ..., **kwargs) -> None: ...

class SwitchActiveEM(_message.Message):
    __slots__ = ("who", "character_id", "character_definition_id", "via_skill_definition_id", "from_action")
    WHO_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    VIA_SKILL_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_ACTION_FIELD_NUMBER: _ClassVar[int]
    who: int
    character_id: int
    character_definition_id: int
    via_skill_definition_id: int
    from_action: SwitchActiveFromAction
    def __init__(self, who: _Optional[int] = ..., character_id: _Optional[int] = ..., character_definition_id: _Optional[int] = ..., via_skill_definition_id: _Optional[int] = ..., from_action: _Optional[_Union[SwitchActiveFromAction, str]] = ...) -> None: ...

class RemoveCardEM(_message.Message):
    __slots__ = ("who", "reason", "card")
    WHO_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CARD_FIELD_NUMBER: _ClassVar[int]
    who: int
    reason: RemoveCardReason
    card: _state_pb2.CardState
    def __init__(self, who: _Optional[int] = ..., reason: _Optional[_Union[RemoveCardReason, str]] = ..., card: _Optional[_Union[_state_pb2.CardState, _Mapping]] = ..., **kwargs) -> None: ...

class CreateCardEM(_message.Message):
    __slots__ = ("who", "to", "target_index", "card")
    WHO_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    TARGET_INDEX_FIELD_NUMBER: _ClassVar[int]
    CARD_FIELD_NUMBER: _ClassVar[int]
    who: int
    to: CardArea
    target_index: int
    card: _state_pb2.CardState
    def __init__(self, who: _Optional[int] = ..., to: _Optional[_Union[CardArea, str]] = ..., target_index: _Optional[int] = ..., card: _Optional[_Union[_state_pb2.CardState, _Mapping]] = ...) -> None: ...

class CreateCharacterEM(_message.Message):
    __slots__ = ("who", "character")
    WHO_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    who: int
    character: _state_pb2.CharacterState
    def __init__(self, who: _Optional[int] = ..., character: _Optional[_Union[_state_pb2.CharacterState, _Mapping]] = ...) -> None: ...

class CreateEntityEM(_message.Message):
    __slots__ = ("who", "where", "entity", "master_character_id")
    WHO_FIELD_NUMBER: _ClassVar[int]
    WHERE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    MASTER_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    who: int
    where: EntityArea
    entity: _state_pb2.EntityState
    master_character_id: int
    def __init__(self, who: _Optional[int] = ..., where: _Optional[_Union[EntityArea, str]] = ..., entity: _Optional[_Union[_state_pb2.EntityState, _Mapping]] = ..., master_character_id: _Optional[int] = ...) -> None: ...

class RemoveEntityEM(_message.Message):
    __slots__ = ("entity",)
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    entity: _state_pb2.EntityState
    def __init__(self, entity: _Optional[_Union[_state_pb2.EntityState, _Mapping]] = ...) -> None: ...

class ModifyEntityVarEM(_message.Message):
    __slots__ = ("entity_id", "entity_definition_id", "variable_name", "variable_value", "direction")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    entity_definition_id: int
    variable_name: str
    variable_value: int
    direction: ModifyDirection
    def __init__(self, entity_id: _Optional[int] = ..., entity_definition_id: _Optional[int] = ..., variable_name: _Optional[str] = ..., variable_value: _Optional[int] = ..., direction: _Optional[_Union[ModifyDirection, str]] = ...) -> None: ...

class TransformDefinitionEM(_message.Message):
    __slots__ = ("entity_id", "new_entity_definition_id")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_ENTITY_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    new_entity_definition_id: int
    def __init__(self, entity_id: _Optional[int] = ..., new_entity_definition_id: _Optional[int] = ...) -> None: ...

class ResetDiceEM(_message.Message):
    __slots__ = ("who", "dice", "reason", "conversion_target_hint")
    WHO_FIELD_NUMBER: _ClassVar[int]
    DICE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_TARGET_HINT_FIELD_NUMBER: _ClassVar[int]
    who: int
    dice: _containers.RepeatedScalarFieldContainer[_enums_pb2.DiceType]
    reason: ResetDiceReason
    conversion_target_hint: _enums_pb2.DiceType
    def __init__(self, who: _Optional[int] = ..., dice: _Optional[_Iterable[_Union[_enums_pb2.DiceType, str]]] = ..., reason: _Optional[_Union[ResetDiceReason, str]] = ..., conversion_target_hint: _Optional[_Union[_enums_pb2.DiceType, str]] = ...) -> None: ...

class DamageEM(_message.Message):
    __slots__ = ("damage_type", "value", "target_id", "target_definition_id", "source_id", "source_definition_id", "is_skill_main_damage", "reaction_type", "cause_defeated", "old_aura", "new_aura", "old_health", "new_health", "heal_kind")
    DAMAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    IS_SKILL_MAIN_DAMAGE_FIELD_NUMBER: _ClassVar[int]
    REACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CAUSE_DEFEATED_FIELD_NUMBER: _ClassVar[int]
    OLD_AURA_FIELD_NUMBER: _ClassVar[int]
    NEW_AURA_FIELD_NUMBER: _ClassVar[int]
    OLD_HEALTH_FIELD_NUMBER: _ClassVar[int]
    NEW_HEALTH_FIELD_NUMBER: _ClassVar[int]
    HEAL_KIND_FIELD_NUMBER: _ClassVar[int]
    damage_type: _enums_pb2.DamageType
    value: int
    target_id: int
    target_definition_id: int
    source_id: int
    source_definition_id: int
    is_skill_main_damage: bool
    reaction_type: _enums_pb2.ReactionType
    cause_defeated: bool
    old_aura: _enums_pb2.AuraType
    new_aura: _enums_pb2.AuraType
    old_health: int
    new_health: int
    heal_kind: HealKind
    def __init__(self, damage_type: _Optional[_Union[_enums_pb2.DamageType, str]] = ..., value: _Optional[int] = ..., target_id: _Optional[int] = ..., target_definition_id: _Optional[int] = ..., source_id: _Optional[int] = ..., source_definition_id: _Optional[int] = ..., is_skill_main_damage: bool = ..., reaction_type: _Optional[_Union[_enums_pb2.ReactionType, str]] = ..., cause_defeated: bool = ..., old_aura: _Optional[_Union[_enums_pb2.AuraType, str]] = ..., new_aura: _Optional[_Union[_enums_pb2.AuraType, str]] = ..., old_health: _Optional[int] = ..., new_health: _Optional[int] = ..., heal_kind: _Optional[_Union[HealKind, str]] = ...) -> None: ...

class ApplyAuraEM(_message.Message):
    __slots__ = ("element_type", "target_id", "target_definition_id", "reaction_type", "old_aura", "new_aura")
    ELEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    REACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    OLD_AURA_FIELD_NUMBER: _ClassVar[int]
    NEW_AURA_FIELD_NUMBER: _ClassVar[int]
    element_type: _enums_pb2.DamageType
    target_id: int
    target_definition_id: int
    reaction_type: _enums_pb2.ReactionType
    old_aura: _enums_pb2.AuraType
    new_aura: _enums_pb2.AuraType
    def __init__(self, element_type: _Optional[_Union[_enums_pb2.DamageType, str]] = ..., target_id: _Optional[int] = ..., target_definition_id: _Optional[int] = ..., reaction_type: _Optional[_Union[_enums_pb2.ReactionType, str]] = ..., old_aura: _Optional[_Union[_enums_pb2.AuraType, str]] = ..., new_aura: _Optional[_Union[_enums_pb2.AuraType, str]] = ...) -> None: ...

class SkillUsedEM(_message.Message):
    __slots__ = ("caller_id", "caller_definition_id", "skill_definition_id", "skill_type", "who", "triggered_on")
    CALLER_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_TYPE_FIELD_NUMBER: _ClassVar[int]
    WHO_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_ON_FIELD_NUMBER: _ClassVar[int]
    caller_id: int
    caller_definition_id: int
    skill_definition_id: int
    skill_type: SkillType
    who: int
    triggered_on: str
    def __init__(self, caller_id: _Optional[int] = ..., caller_definition_id: _Optional[int] = ..., skill_definition_id: _Optional[int] = ..., skill_type: _Optional[_Union[SkillType, str]] = ..., who: _Optional[int] = ..., triggered_on: _Optional[str] = ...) -> None: ...

class PlayerStatusChangeEM(_message.Message):
    __slots__ = ("who", "status")
    WHO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    who: int
    status: _state_pb2.PlayerStatus
    def __init__(self, who: _Optional[int] = ..., status: _Optional[_Union[_state_pb2.PlayerStatus, str]] = ...) -> None: ...

class SwapCharacterPositionEM(_message.Message):
    __slots__ = ("who", "character_0_id", "character_0_definition_id", "character_1_id", "character_1_definition_id")
    WHO_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_0_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_0_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_1_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_1_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    who: int
    character_0_id: int
    character_0_definition_id: int
    character_1_id: int
    character_1_definition_id: int
    def __init__(self, who: _Optional[int] = ..., character_0_id: _Optional[int] = ..., character_0_definition_id: _Optional[int] = ..., character_1_id: _Optional[int] = ..., character_1_definition_id: _Optional[int] = ...) -> None: ...

class SetPlayerFlagEM(_message.Message):
    __slots__ = ("who", "flag_name", "flag_value")
    WHO_FIELD_NUMBER: _ClassVar[int]
    FLAG_NAME_FIELD_NUMBER: _ClassVar[int]
    FLAG_VALUE_FIELD_NUMBER: _ClassVar[int]
    who: int
    flag_name: PlayerFlag
    flag_value: bool
    def __init__(self, who: _Optional[int] = ..., flag_name: _Optional[_Union[PlayerFlag, str]] = ..., flag_value: bool = ...) -> None: ...

class RerollDoneEM(_message.Message):
    __slots__ = ("who", "count")
    WHO_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    who: int
    count: int
    def __init__(self, who: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class ChooseActiveDoneEM(_message.Message):
    __slots__ = ("who", "character_id", "character_definition_id")
    WHO_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    who: int
    character_id: int
    character_definition_id: int
    def __init__(self, who: _Optional[int] = ..., character_id: _Optional[int] = ..., character_definition_id: _Optional[int] = ...) -> None: ...

class SwitchHandsDoneEM(_message.Message):
    __slots__ = ("who", "count")
    WHO_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    who: int
    count: int
    def __init__(self, who: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class SelectCardDoneEM(_message.Message):
    __slots__ = ("who", "selected_definition_id")
    WHO_FIELD_NUMBER: _ClassVar[int]
    SELECTED_DEFINITION_ID_FIELD_NUMBER: _ClassVar[int]
    who: int
    selected_definition_id: int
    def __init__(self, who: _Optional[int] = ..., selected_definition_id: _Optional[int] = ...) -> None: ...

class HandleEventEM(_message.Message):
    __slots__ = ("is_close", "event_name")
    IS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    EVENT_NAME_FIELD_NUMBER: _ClassVar[int]
    is_close: bool
    event_name: str
    def __init__(self, is_close: bool = ..., event_name: _Optional[str] = ...) -> None: ...
