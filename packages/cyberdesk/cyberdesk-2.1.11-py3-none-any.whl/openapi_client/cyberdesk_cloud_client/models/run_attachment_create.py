import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.attachment_type import AttachmentType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RunAttachmentCreate")


@_attrs_define
class RunAttachmentCreate:
    """Schema for creating a run attachment

    Attributes:
        run_id (UUID):
        filename (str):
        content (str): Base64 encoded file content
        content_type (str):
        attachment_type (AttachmentType):
        target_path (Union[None, Unset, str]):
        cleanup_imports_after_run (Union[Unset, bool]):  Default: False.
        expires_at (Union[None, Unset, datetime.datetime]):
    """

    run_id: UUID
    filename: str
    content: str
    content_type: str
    attachment_type: AttachmentType
    target_path: Union[None, Unset, str] = UNSET
    cleanup_imports_after_run: Union[Unset, bool] = False
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run_id = str(self.run_id)

        filename = self.filename

        content = self.content

        content_type = self.content_type

        attachment_type = self.attachment_type.value

        target_path: Union[None, Unset, str]
        if isinstance(self.target_path, Unset):
            target_path = UNSET
        else:
            target_path = self.target_path

        cleanup_imports_after_run = self.cleanup_imports_after_run

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id": run_id,
                "filename": filename,
                "content": content,
                "content_type": content_type,
                "attachment_type": attachment_type,
            }
        )
        if target_path is not UNSET:
            field_dict["target_path"] = target_path
        if cleanup_imports_after_run is not UNSET:
            field_dict["cleanup_imports_after_run"] = cleanup_imports_after_run
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        run_id = UUID(d.pop("run_id"))

        filename = d.pop("filename")

        content = d.pop("content")

        content_type = d.pop("content_type")

        attachment_type = AttachmentType(d.pop("attachment_type"))

        def _parse_target_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target_path = _parse_target_path(d.pop("target_path", UNSET))

        cleanup_imports_after_run = d.pop("cleanup_imports_after_run", UNSET)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        run_attachment_create = cls(
            run_id=run_id,
            filename=filename,
            content=content,
            content_type=content_type,
            attachment_type=attachment_type,
            target_path=target_path,
            cleanup_imports_after_run=cleanup_imports_after_run,
            expires_at=expires_at,
        )

        run_attachment_create.additional_properties = d
        return run_attachment_create

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
