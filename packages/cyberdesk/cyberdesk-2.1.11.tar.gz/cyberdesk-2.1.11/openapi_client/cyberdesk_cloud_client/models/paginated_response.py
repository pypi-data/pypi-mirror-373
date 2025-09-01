from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PaginatedResponse")


@_attrs_define
class PaginatedResponse:
    """Paginated response wrapper

    Attributes:
        items (list[Any]):
        total (int):
        skip (int):
        limit (int):
    """

    items: list[Any]
    total: int
    skip: int
    limit: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = self.items

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
        d = dict(src_dict)
        items = cast(list[Any], d.pop("items"))

        total = d.pop("total")

        skip = d.pop("skip")

        limit = d.pop("limit")

        paginated_response = cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

        paginated_response.additional_properties = d
        return paginated_response

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
