import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.machine_status import MachineStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="MachineUpdate")


@_attrs_define
class MachineUpdate:
    """Schema for updating a machine

    Attributes:
        name (Union[None, Unset, str]):
        version (Union[None, Unset, str]):
        hostname (Union[None, Unset, str]):
        os_info (Union[None, Unset, str]):
        status (Union[MachineStatus, None, Unset]):
        is_available (Union[None, Unset, bool]):
        last_seen (Union[None, Unset, datetime.datetime]):
        reserved_session_id (Union[None, UUID, Unset]): Set to null to clear reservation; server will cancel
            queued/running session runs and clear
    """

    name: Union[None, Unset, str] = UNSET
    version: Union[None, Unset, str] = UNSET
    hostname: Union[None, Unset, str] = UNSET
    os_info: Union[None, Unset, str] = UNSET
    status: Union[MachineStatus, None, Unset] = UNSET
    is_available: Union[None, Unset, bool] = UNSET
    last_seen: Union[None, Unset, datetime.datetime] = UNSET
    reserved_session_id: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        version: Union[None, Unset, str]
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        hostname: Union[None, Unset, str]
        if isinstance(self.hostname, Unset):
            hostname = UNSET
        else:
            hostname = self.hostname

        os_info: Union[None, Unset, str]
        if isinstance(self.os_info, Unset):
            os_info = UNSET
        else:
            os_info = self.os_info

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, MachineStatus):
            status = self.status.value
        else:
            status = self.status

        is_available: Union[None, Unset, bool]
        if isinstance(self.is_available, Unset):
            is_available = UNSET
        else:
            is_available = self.is_available

        last_seen: Union[None, Unset, str]
        if isinstance(self.last_seen, Unset):
            last_seen = UNSET
        elif isinstance(self.last_seen, datetime.datetime):
            last_seen = self.last_seen.isoformat()
        else:
            last_seen = self.last_seen

        reserved_session_id: Union[None, Unset, str]
        if isinstance(self.reserved_session_id, Unset):
            reserved_session_id = UNSET
        elif isinstance(self.reserved_session_id, UUID):
            reserved_session_id = str(self.reserved_session_id)
        else:
            reserved_session_id = self.reserved_session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if os_info is not UNSET:
            field_dict["os_info"] = os_info
        if status is not UNSET:
            field_dict["status"] = status
        if is_available is not UNSET:
            field_dict["is_available"] = is_available
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if reserved_session_id is not UNSET:
            field_dict["reserved_session_id"] = reserved_session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_hostname(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        hostname = _parse_hostname(d.pop("hostname", UNSET))

        def _parse_os_info(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        os_info = _parse_os_info(d.pop("os_info", UNSET))

        def _parse_status(data: object) -> Union[MachineStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = MachineStatus(data)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[MachineStatus, None, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_is_available(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_available = _parse_is_available(d.pop("is_available", UNSET))

        def _parse_last_seen(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_seen_type_0 = isoparse(data)

                return last_seen_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_seen = _parse_last_seen(d.pop("last_seen", UNSET))

        def _parse_reserved_session_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reserved_session_id_type_0 = UUID(data)

                return reserved_session_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        reserved_session_id = _parse_reserved_session_id(d.pop("reserved_session_id", UNSET))

        machine_update = cls(
            name=name,
            version=version,
            hostname=hostname,
            os_info=os_info,
            status=status,
            is_available=is_available,
            last_seen=last_seen,
            reserved_session_id=reserved_session_id,
        )

        machine_update.additional_properties = d
        return machine_update

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
