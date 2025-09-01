from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet")


@_attrs_define
class FsReadV1ComputerMachineIdFsReadGetResponseFsReadV1ComputerMachineIdFsReadGet:
    """ """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fs_read_v1_computer_machine_id_fs_read_get_response_fs_read_v1_computer_machine_id_fs_read_get = cls()

        fs_read_v1_computer_machine_id_fs_read_get_response_fs_read_v1_computer_machine_id_fs_read_get.additional_properties = d
        return fs_read_v1_computer_machine_id_fs_read_get_response_fs_read_v1_computer_machine_id_fs_read_get

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
