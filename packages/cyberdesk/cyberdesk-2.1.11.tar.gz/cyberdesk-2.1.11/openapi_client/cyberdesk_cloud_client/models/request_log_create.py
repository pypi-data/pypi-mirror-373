from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestLogCreate")


@_attrs_define
class RequestLogCreate:
    """Schema for creating a request log

    Attributes:
        request_id (str):
        method (str):
        path (str):
        machine_id (UUID):
        status_code (Union[None, Unset, int]):
        request_size_bytes (Union[None, Unset, int]):
        response_size_bytes (Union[None, Unset, int]):
        duration_ms (Union[None, Unset, int]):
        error_message (Union[None, Unset, str]):
    """

    request_id: str
    method: str
    path: str
    machine_id: UUID
    status_code: Union[None, Unset, int] = UNSET
    request_size_bytes: Union[None, Unset, int] = UNSET
    response_size_bytes: Union[None, Unset, int] = UNSET
    duration_ms: Union[None, Unset, int] = UNSET
    error_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        method = self.method

        path = self.path

        machine_id = str(self.machine_id)

        status_code: Union[None, Unset, int]
        if isinstance(self.status_code, Unset):
            status_code = UNSET
        else:
            status_code = self.status_code

        request_size_bytes: Union[None, Unset, int]
        if isinstance(self.request_size_bytes, Unset):
            request_size_bytes = UNSET
        else:
            request_size_bytes = self.request_size_bytes

        response_size_bytes: Union[None, Unset, int]
        if isinstance(self.response_size_bytes, Unset):
            response_size_bytes = UNSET
        else:
            response_size_bytes = self.response_size_bytes

        duration_ms: Union[None, Unset, int]
        if isinstance(self.duration_ms, Unset):
            duration_ms = UNSET
        else:
            duration_ms = self.duration_ms

        error_message: Union[None, Unset, str]
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "request_id": request_id,
                "method": method,
                "path": path,
                "machine_id": machine_id,
            }
        )
        if status_code is not UNSET:
            field_dict["status_code"] = status_code
        if request_size_bytes is not UNSET:
            field_dict["request_size_bytes"] = request_size_bytes
        if response_size_bytes is not UNSET:
            field_dict["response_size_bytes"] = response_size_bytes
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = d.pop("request_id")

        method = d.pop("method")

        path = d.pop("path")

        machine_id = UUID(d.pop("machine_id"))

        def _parse_status_code(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        status_code = _parse_status_code(d.pop("status_code", UNSET))

        def _parse_request_size_bytes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        request_size_bytes = _parse_request_size_bytes(d.pop("request_size_bytes", UNSET))

        def _parse_response_size_bytes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        response_size_bytes = _parse_response_size_bytes(d.pop("response_size_bytes", UNSET))

        def _parse_duration_ms(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        duration_ms = _parse_duration_ms(d.pop("duration_ms", UNSET))

        def _parse_error_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        request_log_create = cls(
            request_id=request_id,
            method=method,
            path=path,
            machine_id=machine_id,
            status_code=status_code,
            request_size_bytes=request_size_bytes,
            response_size_bytes=response_size_bytes,
            duration_ms=duration_ms,
            error_message=error_message,
        )

        request_log_create.additional_properties = d
        return request_log_create

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
