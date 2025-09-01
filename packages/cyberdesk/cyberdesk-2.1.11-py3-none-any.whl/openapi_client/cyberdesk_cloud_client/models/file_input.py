from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileInput")


@_attrs_define
class FileInput:
    """File input for run creation

    Attributes:
        filename (str):
        content (str): Base64 encoded file content
        target_path (Union[None, Unset, str]): Optional path on machine, defaults to ~/CyberdeskTransfers/
        cleanup_imports_after_run (Union[Unset, bool]): Delete from machine after run completes Default: False.
    """

    filename: str
    content: str
    target_path: Union[None, Unset, str] = UNSET
    cleanup_imports_after_run: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        content = self.content

        target_path: Union[None, Unset, str]
        if isinstance(self.target_path, Unset):
            target_path = UNSET
        else:
            target_path = self.target_path

        cleanup_imports_after_run = self.cleanup_imports_after_run

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filename": filename,
                "content": content,
            }
        )
        if target_path is not UNSET:
            field_dict["target_path"] = target_path
        if cleanup_imports_after_run is not UNSET:
            field_dict["cleanup_imports_after_run"] = cleanup_imports_after_run

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        content = d.pop("content")

        def _parse_target_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target_path = _parse_target_path(d.pop("target_path", UNSET))

        cleanup_imports_after_run = d.pop("cleanup_imports_after_run", UNSET)

        file_input = cls(
            filename=filename,
            content=content,
            target_path=target_path,
            cleanup_imports_after_run=cleanup_imports_after_run,
        )

        file_input.additional_properties = d
        return file_input

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
