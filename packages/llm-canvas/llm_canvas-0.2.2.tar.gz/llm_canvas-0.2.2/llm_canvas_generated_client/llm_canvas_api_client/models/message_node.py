from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dimension import Dimension
    from ..models.message import Message
    from ..models.message_node_meta import MessageNodeMeta
    from ..models.position import Position


T = TypeVar("T", bound="MessageNode")


@_attrs_define
class MessageNode:
    """Node in the canvas conversation graph.

    Attributes:
        id (str):
        message (Message): Message structure for canvas conversations.
        child_ids (list[str]):
        parent_id (Union[Unset, str]):
        meta (Union[Unset, MessageNodeMeta]):
        position (Union[Unset, Position]): Position information for a message node.
        dimension (Union[Unset, Dimension]): Dimension information for a message node.
    """

    id: str
    message: "Message"
    child_ids: list[str]
    parent_id: Union[Unset, str] = UNSET
    meta: Union[Unset, "MessageNodeMeta"] = UNSET
    position: Union[Unset, "Position"] = UNSET
    dimension: Union[Unset, "Dimension"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        message = self.message.to_dict()

        child_ids = self.child_ids

        parent_id = self.parent_id

        meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()

        position: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()

        dimension: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.dimension, Unset):
            dimension = self.dimension.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "message": message,
                "child_ids": child_ids,
            }
        )
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if meta is not UNSET:
            field_dict["meta"] = meta
        if position is not UNSET:
            field_dict["position"] = position
        if dimension is not UNSET:
            field_dict["dimension"] = dimension

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dimension import Dimension
        from ..models.message import Message
        from ..models.message_node_meta import MessageNodeMeta
        from ..models.position import Position

        d = dict(src_dict)
        id = d.pop("id")

        message = Message.from_dict(d.pop("message"))

        child_ids = cast(list[str], d.pop("child_ids"))

        parent_id = d.pop("parent_id", UNSET)

        _meta = d.pop("meta", UNSET)
        meta: Union[Unset, MessageNodeMeta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = MessageNodeMeta.from_dict(_meta)

        _position = d.pop("position", UNSET)
        position: Union[Unset, Position]
        if isinstance(_position, Unset):
            position = UNSET
        else:
            position = Position.from_dict(_position)

        _dimension = d.pop("dimension", UNSET)
        dimension: Union[Unset, Dimension]
        if isinstance(_dimension, Unset):
            dimension = UNSET
        else:
            dimension = Dimension.from_dict(_dimension)

        message_node = cls(
            id=id,
            message=message,
            child_ids=child_ids,
            parent_id=parent_id,
            meta=meta,
            position=position,
            dimension=dimension,
        )

        message_node.additional_properties = d
        return message_node

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
