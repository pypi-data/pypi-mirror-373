import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.attachment_type import AttachmentType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RunAttachmentResponse")


@_attrs_define
class RunAttachmentResponse:
    """Run attachment response schema

    Attributes:
        filename (str):
        content_type (str):
        attachment_type (AttachmentType):
        id (UUID):
        run_id (UUID):
        size_bytes (int):
        storage_path (str):
        created_at (datetime.datetime):
        target_path (Union[None, Unset, str]):
        cleanup_imports_after_run (Union[Unset, bool]):  Default: False.
        user_id (Union[None, UUID, Unset]):
        organization_id (Union[None, Unset, str]):
        expires_at (Union[None, Unset, datetime.datetime]):
    """

    filename: str
    content_type: str
    attachment_type: AttachmentType
    id: UUID
    run_id: UUID
    size_bytes: int
    storage_path: str
    created_at: datetime.datetime
    target_path: Union[None, Unset, str] = UNSET
    cleanup_imports_after_run: Union[Unset, bool] = False
    user_id: Union[None, UUID, Unset] = UNSET
    organization_id: Union[None, Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        content_type = self.content_type

        attachment_type = self.attachment_type.value

        id = str(self.id)

        run_id = str(self.run_id)

        size_bytes = self.size_bytes

        storage_path = self.storage_path

        created_at = self.created_at.isoformat()

        target_path: Union[None, Unset, str]
        if isinstance(self.target_path, Unset):
            target_path = UNSET
        else:
            target_path = self.target_path

        cleanup_imports_after_run = self.cleanup_imports_after_run

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
                "filename": filename,
                "content_type": content_type,
                "attachment_type": attachment_type,
                "id": id,
                "run_id": run_id,
                "size_bytes": size_bytes,
                "storage_path": storage_path,
                "created_at": created_at,
            }
        )
        if target_path is not UNSET:
            field_dict["target_path"] = target_path
        if cleanup_imports_after_run is not UNSET:
            field_dict["cleanup_imports_after_run"] = cleanup_imports_after_run
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        content_type = d.pop("content_type")

        attachment_type = AttachmentType(d.pop("attachment_type"))

        id = UUID(d.pop("id"))

        run_id = UUID(d.pop("run_id"))

        size_bytes = d.pop("size_bytes")

        storage_path = d.pop("storage_path")

        created_at = isoparse(d.pop("created_at"))

        def _parse_target_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target_path = _parse_target_path(d.pop("target_path", UNSET))

        cleanup_imports_after_run = d.pop("cleanup_imports_after_run", UNSET)

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

        run_attachment_response = cls(
            filename=filename,
            content_type=content_type,
            attachment_type=attachment_type,
            id=id,
            run_id=run_id,
            size_bytes=size_bytes,
            storage_path=storage_path,
            created_at=created_at,
            target_path=target_path,
            cleanup_imports_after_run=cleanup_imports_after_run,
            user_id=user_id,
            organization_id=organization_id,
            expires_at=expires_at,
        )

        run_attachment_response.additional_properties = d
        return run_attachment_response

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
