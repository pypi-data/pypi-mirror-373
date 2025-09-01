from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MachinePoolAssignment")


@_attrs_define
class MachinePoolAssignment:
    """Schema for assigning machines to pools

    Attributes:
        machine_ids (list[UUID]): List of machine IDs to assign to the pool
    """

    machine_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        machine_ids = []
        for machine_ids_item_data in self.machine_ids:
            machine_ids_item = str(machine_ids_item_data)
            machine_ids.append(machine_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "machine_ids": machine_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        machine_ids = []
        _machine_ids = d.pop("machine_ids")
        for machine_ids_item_data in _machine_ids:
            machine_ids_item = UUID(machine_ids_item_data)

            machine_ids.append(machine_ids_item)

        machine_pool_assignment = cls(
            machine_ids=machine_ids,
        )

        machine_pool_assignment.additional_properties = d
        return machine_pool_assignment

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
