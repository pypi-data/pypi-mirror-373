from __future__ import annotations

from typing import Union, Callable
from dataclasses import dataclass, field

from amulet.nbt import (
    NamedTag,
    ListTag,
    CompoundTag,
)

from amulet.core.block import Block
from amulet.core.block_entity import BlockEntity
from amulet.core.entity import Entity
from ._typing import NBTTagT, NBTPath


@dataclass(frozen=True)
class SrcDataExtra:
    absolute_coordinates: tuple[int, int, int]
    get_block_callback: Callable[
        [tuple[int, int, int]], tuple[Block, BlockEntity | None]
    ]


@dataclass(frozen=True)
class SrcData:
    block: Block | None
    nbt: NamedTag | None
    extra: SrcDataExtra | None


@dataclass
class StateData:
    relative_location: tuple[int, int, int] = (0, 0, 0)
    # nbt_path is only set when within walk_input_nbt
    nbt_path: tuple[str, type[ListTag] | type[CompoundTag], NBTPath] | None = None


@dataclass
class DstData:
    cls: type[Block] | type[Entity] | None = None
    resource_id: tuple[str, str] | None = None
    properties: dict[str, Block.PropertyValue] = field(default_factory=dict)
    nbt: list[
        tuple[
            str,
            type[ListTag] | type[CompoundTag],
            NBTPath,
            Union[str, int],
            NBTTagT,
        ]
    ] = field(default_factory=list)
    extra_needed: bool = False
    cacheable: bool = True
