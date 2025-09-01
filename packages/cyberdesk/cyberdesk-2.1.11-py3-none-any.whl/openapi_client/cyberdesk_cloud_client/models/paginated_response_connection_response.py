from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.connection_response import ConnectionResponse


T = TypeVar("T", bound="PaginatedResponseConnectionResponse")


@_attrs_define
class PaginatedResponseConnectionResponse:
    """
    Attributes:
        items (list['ConnectionResponse']):
        total (int):
        skip (int):
        limit (int):
    """

    items: list["ConnectionResponse"]
    total: int
    skip: int
    limit: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        total = self.total

        skip = self.skip

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connection_response import ConnectionResponse

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = ConnectionResponse.from_dict(items_item_data)

            items.append(items_item)

        total = d.pop("total")

        skip = d.pop("skip")

        limit = d.pop("limit")

        paginated_response_connection_response = cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

        paginated_response_connection_response.additional_properties = d
        return paginated_response_connection_response

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
