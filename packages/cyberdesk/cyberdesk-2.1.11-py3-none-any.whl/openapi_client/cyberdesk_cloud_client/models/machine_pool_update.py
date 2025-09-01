from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MachinePoolUpdate")


@_attrs_define
class MachinePoolUpdate:
    """Schema for updating a machine's pool assignments

    Attributes:
        pool_ids (list[UUID]): List of pool IDs to assign the machine to
    """

    pool_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pool_ids = []
        for pool_ids_item_data in self.pool_ids:
            pool_ids_item = str(pool_ids_item_data)
            pool_ids.append(pool_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pool_ids": pool_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pool_ids = []
        _pool_ids = d.pop("pool_ids")
        for pool_ids_item_data in _pool_ids:
            pool_ids_item = UUID(pool_ids_item_data)

            pool_ids.append(pool_ids_item)

        machine_pool_update = cls(
            pool_ids=pool_ids,
        )

        machine_pool_update.additional_properties = d
        return machine_pool_update

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
