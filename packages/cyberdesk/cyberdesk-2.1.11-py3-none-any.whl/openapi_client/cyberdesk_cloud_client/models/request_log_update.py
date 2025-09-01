import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestLogUpdate")


@_attrs_define
class RequestLogUpdate:
    """Schema for updating a request log

    Attributes:
        status_code (Union[None, Unset, int]):
        response_size_bytes (Union[None, Unset, int]):
        completed_at (Union[None, Unset, datetime.datetime]):
        duration_ms (Union[None, Unset, int]):
        error_message (Union[None, Unset, str]):
    """

    status_code: Union[None, Unset, int] = UNSET
    response_size_bytes: Union[None, Unset, int] = UNSET
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    duration_ms: Union[None, Unset, int] = UNSET
    error_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_code: Union[None, Unset, int]
        if isinstance(self.status_code, Unset):
            status_code = UNSET
        else:
            status_code = self.status_code

        response_size_bytes: Union[None, Unset, int]
        if isinstance(self.response_size_bytes, Unset):
            response_size_bytes = UNSET
        else:
            response_size_bytes = self.response_size_bytes

        completed_at: Union[None, Unset, str]
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

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
        field_dict.update({})
        if status_code is not UNSET:
            field_dict["status_code"] = status_code
        if response_size_bytes is not UNSET:
            field_dict["response_size_bytes"] = response_size_bytes
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_status_code(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        status_code = _parse_status_code(d.pop("status_code", UNSET))

        def _parse_response_size_bytes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        response_size_bytes = _parse_response_size_bytes(d.pop("response_size_bytes", UNSET))

        def _parse_completed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

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

        request_log_update = cls(
            status_code=status_code,
            response_size_bytes=response_size_bytes,
            completed_at=completed_at,
            duration_ms=duration_ms,
            error_message=error_message,
        )

        request_log_update.additional_properties = d
        return request_log_update

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
