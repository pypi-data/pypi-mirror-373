import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.machine_status import MachineStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pool_response import PoolResponse


T = TypeVar("T", bound="MachineResponse")


@_attrs_define
class MachineResponse:
    """Machine response schema

    Attributes:
        fingerprint (str):
        id (UUID):
        unkey_key_id (str):
        status (MachineStatus):
        is_available (bool):
        created_at (datetime.datetime):
        last_seen (datetime.datetime):
        name (Union[None, Unset, str]):
        version (Union[None, Unset, str]):
        hostname (Union[None, Unset, str]):
        os_info (Union[None, Unset, str]):
        user_id (Union[None, UUID, Unset]):
        organization_id (Union[None, Unset, str]):
        reserved_session_id (Union[None, UUID, Unset]):
        linked_keepalive_machine_id (Union[None, UUID, Unset]):
        pools (Union[None, Unset, list['PoolResponse']]):
    """

    fingerprint: str
    id: UUID
    unkey_key_id: str
    status: MachineStatus
    is_available: bool
    created_at: datetime.datetime
    last_seen: datetime.datetime
    name: Union[None, Unset, str] = UNSET
    version: Union[None, Unset, str] = UNSET
    hostname: Union[None, Unset, str] = UNSET
    os_info: Union[None, Unset, str] = UNSET
    user_id: Union[None, UUID, Unset] = UNSET
    organization_id: Union[None, Unset, str] = UNSET
    reserved_session_id: Union[None, UUID, Unset] = UNSET
    linked_keepalive_machine_id: Union[None, UUID, Unset] = UNSET
    pools: Union[None, Unset, list["PoolResponse"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fingerprint = self.fingerprint

        id = str(self.id)

        unkey_key_id = self.unkey_key_id

        status = self.status.value

        is_available = self.is_available

        created_at = self.created_at.isoformat()

        last_seen = self.last_seen.isoformat()

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

        user_id: Union[None, Unset, str]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        elif isinstance(self.user_id, UUID):
            user_id = str(self.user_id)
        else:
            user_id = self.user_id

        organization_id: Union[None, Unset, str]
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        reserved_session_id: Union[None, Unset, str]
        if isinstance(self.reserved_session_id, Unset):
            reserved_session_id = UNSET
        elif isinstance(self.reserved_session_id, UUID):
            reserved_session_id = str(self.reserved_session_id)
        else:
            reserved_session_id = self.reserved_session_id

        linked_keepalive_machine_id: Union[None, Unset, str]
        if isinstance(self.linked_keepalive_machine_id, Unset):
            linked_keepalive_machine_id = UNSET
        elif isinstance(self.linked_keepalive_machine_id, UUID):
            linked_keepalive_machine_id = str(self.linked_keepalive_machine_id)
        else:
            linked_keepalive_machine_id = self.linked_keepalive_machine_id

        pools: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.pools, Unset):
            pools = UNSET
        elif isinstance(self.pools, list):
            pools = []
            for pools_type_0_item_data in self.pools:
                pools_type_0_item = pools_type_0_item_data.to_dict()
                pools.append(pools_type_0_item)

        else:
            pools = self.pools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fingerprint": fingerprint,
                "id": id,
                "unkey_key_id": unkey_key_id,
                "status": status,
                "is_available": is_available,
                "created_at": created_at,
                "last_seen": last_seen,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if os_info is not UNSET:
            field_dict["os_info"] = os_info
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if reserved_session_id is not UNSET:
            field_dict["reserved_session_id"] = reserved_session_id
        if linked_keepalive_machine_id is not UNSET:
            field_dict["linked_keepalive_machine_id"] = linked_keepalive_machine_id
        if pools is not UNSET:
            field_dict["pools"] = pools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pool_response import PoolResponse

        d = dict(src_dict)
        fingerprint = d.pop("fingerprint")

        id = UUID(d.pop("id"))

        unkey_key_id = d.pop("unkey_key_id")

        status = MachineStatus(d.pop("status"))

        is_available = d.pop("is_available")

        created_at = isoparse(d.pop("created_at"))

        last_seen = isoparse(d.pop("last_seen"))

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

        def _parse_user_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                user_id_type_0 = UUID(data)

                return user_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        def _parse_organization_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

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

        def _parse_linked_keepalive_machine_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                linked_keepalive_machine_id_type_0 = UUID(data)

                return linked_keepalive_machine_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        linked_keepalive_machine_id = _parse_linked_keepalive_machine_id(d.pop("linked_keepalive_machine_id", UNSET))

        def _parse_pools(data: object) -> Union[None, Unset, list["PoolResponse"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                pools_type_0 = []
                _pools_type_0 = data
                for pools_type_0_item_data in _pools_type_0:
                    pools_type_0_item = PoolResponse.from_dict(pools_type_0_item_data)

                    pools_type_0.append(pools_type_0_item)

                return pools_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PoolResponse"]], data)

        pools = _parse_pools(d.pop("pools", UNSET))

        machine_response = cls(
            fingerprint=fingerprint,
            id=id,
            unkey_key_id=unkey_key_id,
            status=status,
            is_available=is_available,
            created_at=created_at,
            last_seen=last_seen,
            name=name,
            version=version,
            hostname=hostname,
            os_info=os_info,
            user_id=user_id,
            organization_id=organization_id,
            reserved_session_id=reserved_session_id,
            linked_keepalive_machine_id=linked_keepalive_machine_id,
            pools=pools,
        )

        machine_response.additional_properties = d
        return machine_response

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
