from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectionCreate")


@_attrs_define
class ConnectionCreate:
    """Schema for creating a connection

    Attributes:
        websocket_id (str):
        machine_id (UUID):
        ip_address (Union[None, Unset, str]):
        user_agent (Union[None, Unset, str]):
    """

    websocket_id: str
    machine_id: UUID
    ip_address: Union[None, Unset, str] = UNSET
    user_agent: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        websocket_id = self.websocket_id

        machine_id = str(self.machine_id)

        ip_address: Union[None, Unset, str]
        if isinstance(self.ip_address, Unset):
            ip_address = UNSET
        else:
            ip_address = self.ip_address

        user_agent: Union[None, Unset, str]
        if isinstance(self.user_agent, Unset):
            user_agent = UNSET
        else:
            user_agent = self.user_agent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "websocket_id": websocket_id,
                "machine_id": machine_id,
            }
        )
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if user_agent is not UNSET:
            field_dict["user_agent"] = user_agent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        websocket_id = d.pop("websocket_id")

        machine_id = UUID(d.pop("machine_id"))

        def _parse_ip_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ip_address = _parse_ip_address(d.pop("ip_address", UNSET))

        def _parse_user_agent(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_agent = _parse_user_agent(d.pop("user_agent", UNSET))

        connection_create = cls(
            websocket_id=websocket_id,
            machine_id=machine_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        connection_create.additional_properties = d
        return connection_create

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
