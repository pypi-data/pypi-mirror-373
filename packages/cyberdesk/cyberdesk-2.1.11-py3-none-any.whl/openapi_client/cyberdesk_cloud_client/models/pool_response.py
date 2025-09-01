import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PoolResponse")


@_attrs_define
class PoolResponse:
    """Pool response schema

    Attributes:
        name (str):
        id (UUID):
        organization_id (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        description (Union[None, Unset, str]):
        machine_count (Union[None, Unset, int]): Number of machines in this pool Default: 0.
    """

    name: str
    id: UUID
    organization_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    machine_count: Union[None, Unset, int] = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id = str(self.id)

        organization_id = self.organization_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        machine_count: Union[None, Unset, int]
        if isinstance(self.machine_count, Unset):
            machine_count = UNSET
        else:
            machine_count = self.machine_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "id": id,
                "organization_id": organization_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if machine_count is not UNSET:
            field_dict["machine_count"] = machine_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        id = UUID(d.pop("id"))

        organization_id = d.pop("organization_id")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_machine_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        machine_count = _parse_machine_count(d.pop("machine_count", UNSET))

        pool_response = cls(
            name=name,
            id=id,
            organization_id=organization_id,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            machine_count=machine_count,
        )

        pool_response.additional_properties = d
        return pool_response

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
