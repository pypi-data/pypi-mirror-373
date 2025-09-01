from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiceRequirementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DICE_REQUIREMENT_TYPE_VOID: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_CRYO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_HYDRO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_PYRO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_ELECTRO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_ANEMO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_GEO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_DENDRO: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_ALIGNED: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_ENERGY: _ClassVar[DiceRequirementType]
    DICE_REQUIREMENT_TYPE_LEGEND: _ClassVar[DiceRequirementType]

class DiceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DICE_TYPE_UNSPECIFIED: _ClassVar[DiceType]
    DICE_TYPE_CRYO: _ClassVar[DiceType]
    DICE_TYPE_HYDRO: _ClassVar[DiceType]
    DICE_TYPE_PYRO: _ClassVar[DiceType]
    DICE_TYPE_ELECTRO: _ClassVar[DiceType]
    DICE_TYPE_ANEMO: _ClassVar[DiceType]
    DICE_TYPE_GEO: _ClassVar[DiceType]
    DICE_TYPE_DENDRO: _ClassVar[DiceType]
    DICE_TYPE_OMNI: _ClassVar[DiceType]

class DamageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DAMAGE_TYPE_PHYSICAL: _ClassVar[DamageType]
    DAMAGE_TYPE_CRYO: _ClassVar[DamageType]
    DAMAGE_TYPE_HYDRO: _ClassVar[DamageType]
    DAMAGE_TYPE_PYRO: _ClassVar[DamageType]
    DAMAGE_TYPE_ELECTRO: _ClassVar[DamageType]
    DAMAGE_TYPE_ANEMO: _ClassVar[DamageType]
    DAMAGE_TYPE_GEO: _ClassVar[DamageType]
    DAMAGE_TYPE_DENDRO: _ClassVar[DamageType]
    DAMAGE_TYPE_PIERCING: _ClassVar[DamageType]
    DAMAGE_TYPE_HEAL: _ClassVar[DamageType]

class AuraType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AURA_TYPE_NONE: _ClassVar[AuraType]
    AURA_TYPE_CRYO: _ClassVar[AuraType]
    AURA_TYPE_HYDRO: _ClassVar[AuraType]
    AURA_TYPE_PYRO: _ClassVar[AuraType]
    AURA_TYPE_ELECTRO: _ClassVar[AuraType]
    AURA_TYPE_DENDRO: _ClassVar[AuraType]
    AURA_TYPE_CRYO_DENDRO: _ClassVar[AuraType]

class ReactionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REACTION_TYPE_UNSPECIFIED: _ClassVar[ReactionType]
    REACTION_TYPE_MELT: _ClassVar[ReactionType]
    REACTION_TYPE_VAPORIZE: _ClassVar[ReactionType]
    REACTION_TYPE_OVERLOADED: _ClassVar[ReactionType]
    REACTION_TYPE_SUPERCONDUCT: _ClassVar[ReactionType]
    REACTION_TYPE_ELECTRO_CHARGED: _ClassVar[ReactionType]
    REACTION_TYPE_FROZEN: _ClassVar[ReactionType]
    REACTION_TYPE_SWIRL_CRYO: _ClassVar[ReactionType]
    REACTION_TYPE_SWIRL_HYDRO: _ClassVar[ReactionType]
    REACTION_TYPE_SWIRL_PYRO: _ClassVar[ReactionType]
    REACTION_TYPE_SWIRL_ELECTRO: _ClassVar[ReactionType]
    REACTION_TYPE_CRYSTALLIZE_CRYO: _ClassVar[ReactionType]
    REACTION_TYPE_CRYSTALLIZE_HYDRO: _ClassVar[ReactionType]
    REACTION_TYPE_CRYSTALLIZE_PYRO: _ClassVar[ReactionType]
    REACTION_TYPE_CRYSTALLIZE_ELECTRO: _ClassVar[ReactionType]
    REACTION_TYPE_BURNING: _ClassVar[ReactionType]
    REACTION_TYPE_BLOOM: _ClassVar[ReactionType]
    REACTION_TYPE_QUICKEN: _ClassVar[ReactionType]
DICE_REQUIREMENT_TYPE_VOID: DiceRequirementType
DICE_REQUIREMENT_TYPE_CRYO: DiceRequirementType
DICE_REQUIREMENT_TYPE_HYDRO: DiceRequirementType
DICE_REQUIREMENT_TYPE_PYRO: DiceRequirementType
DICE_REQUIREMENT_TYPE_ELECTRO: DiceRequirementType
DICE_REQUIREMENT_TYPE_ANEMO: DiceRequirementType
DICE_REQUIREMENT_TYPE_GEO: DiceRequirementType
DICE_REQUIREMENT_TYPE_DENDRO: DiceRequirementType
DICE_REQUIREMENT_TYPE_ALIGNED: DiceRequirementType
DICE_REQUIREMENT_TYPE_ENERGY: DiceRequirementType
DICE_REQUIREMENT_TYPE_LEGEND: DiceRequirementType
DICE_TYPE_UNSPECIFIED: DiceType
DICE_TYPE_CRYO: DiceType
DICE_TYPE_HYDRO: DiceType
DICE_TYPE_PYRO: DiceType
DICE_TYPE_ELECTRO: DiceType
DICE_TYPE_ANEMO: DiceType
DICE_TYPE_GEO: DiceType
DICE_TYPE_DENDRO: DiceType
DICE_TYPE_OMNI: DiceType
DAMAGE_TYPE_PHYSICAL: DamageType
DAMAGE_TYPE_CRYO: DamageType
DAMAGE_TYPE_HYDRO: DamageType
DAMAGE_TYPE_PYRO: DamageType
DAMAGE_TYPE_ELECTRO: DamageType
DAMAGE_TYPE_ANEMO: DamageType
DAMAGE_TYPE_GEO: DamageType
DAMAGE_TYPE_DENDRO: DamageType
DAMAGE_TYPE_PIERCING: DamageType
DAMAGE_TYPE_HEAL: DamageType
AURA_TYPE_NONE: AuraType
AURA_TYPE_CRYO: AuraType
AURA_TYPE_HYDRO: AuraType
AURA_TYPE_PYRO: AuraType
AURA_TYPE_ELECTRO: AuraType
AURA_TYPE_DENDRO: AuraType
AURA_TYPE_CRYO_DENDRO: AuraType
REACTION_TYPE_UNSPECIFIED: ReactionType
REACTION_TYPE_MELT: ReactionType
REACTION_TYPE_VAPORIZE: ReactionType
REACTION_TYPE_OVERLOADED: ReactionType
REACTION_TYPE_SUPERCONDUCT: ReactionType
REACTION_TYPE_ELECTRO_CHARGED: ReactionType
REACTION_TYPE_FROZEN: ReactionType
REACTION_TYPE_SWIRL_CRYO: ReactionType
REACTION_TYPE_SWIRL_HYDRO: ReactionType
REACTION_TYPE_SWIRL_PYRO: ReactionType
REACTION_TYPE_SWIRL_ELECTRO: ReactionType
REACTION_TYPE_CRYSTALLIZE_CRYO: ReactionType
REACTION_TYPE_CRYSTALLIZE_HYDRO: ReactionType
REACTION_TYPE_CRYSTALLIZE_PYRO: ReactionType
REACTION_TYPE_CRYSTALLIZE_ELECTRO: ReactionType
REACTION_TYPE_BURNING: ReactionType
REACTION_TYPE_BLOOM: ReactionType
REACTION_TYPE_QUICKEN: ReactionType

class DiceRequirement(_message.Message):
    __slots__ = ("type", "count")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    type: DiceRequirementType
    count: int
    def __init__(self, type: _Optional[_Union[DiceRequirementType, str]] = ..., count: _Optional[int] = ...) -> None: ...
