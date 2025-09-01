import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.connection_status import ConnectionStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectionResponse")


@_attrs_define
class ConnectionResponse:
    """Connection response schema

    Attributes:
        websocket_id (str):
        id (UUID):
        machine_id (UUID):
        connected_at (datetime.datetime):
        disconnected_at (Union[None, datetime.datetime]):
        last_ping (datetime.datetime):
        status (ConnectionStatus):
        ip_address (Union[None, Unset, str]):
        user_agent (Union[None, Unset, str]):
    """

    websocket_id: str
    id: UUID
    machine_id: UUID
    connected_at: datetime.datetime
    disconnected_at: Union[None, datetime.datetime]
    last_ping: datetime.datetime
    status: ConnectionStatus
    ip_address: Union[None, Unset, str] = UNSET
    user_agent: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        websocket_id = self.websocket_id

        id = str(self.id)

        machine_id = str(self.machine_id)

        connected_at = self.connected_at.isoformat()

        disconnected_at: Union[None, str]
        if isinstance(self.disconnected_at, datetime.datetime):
            disconnected_at = self.disconnected_at.isoformat()
        else:
            disconnected_at = self.disconnected_at

        last_ping = self.last_ping.isoformat()

        status = self.status.value

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
                "id": id,
                "machine_id": machine_id,
                "connected_at": connected_at,
                "disconnected_at": disconnected_at,
                "last_ping": last_ping,
                "status": status,
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

        id = UUID(d.pop("id"))

        machine_id = UUID(d.pop("machine_id"))

        connected_at = isoparse(d.pop("connected_at"))

        def _parse_disconnected_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                disconnected_at_type_0 = isoparse(data)

                return disconnected_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        disconnected_at = _parse_disconnected_at(d.pop("disconnected_at"))

        last_ping = isoparse(d.pop("last_ping"))

        status = ConnectionStatus(d.pop("status"))

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

        connection_response = cls(
            websocket_id=websocket_id,
            id=id,
            machine_id=machine_id,
            connected_at=connected_at,
            disconnected_at=disconnected_at,
            last_ping=last_ping,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        connection_response.additional_properties = d
        return connection_response

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
