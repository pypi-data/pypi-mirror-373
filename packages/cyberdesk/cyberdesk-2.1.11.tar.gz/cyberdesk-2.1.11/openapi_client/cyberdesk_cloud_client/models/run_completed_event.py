import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_response import RunResponse


T = TypeVar("T", bound="RunCompletedEvent")


@_attrs_define
class RunCompletedEvent:
    """Payload sent for the run_complete webhook event.

    Attributes:
        run (RunResponse): Run response schema
        event_id (Union[Unset, UUID]): Unique event identifier for idempotency
        event_type (Union[Unset, str]): Event type key Default: 'run_complete'.
        occurred_at (Union[Unset, datetime.datetime]): Time the event occurred (UTC)
    """

    run: "RunResponse"
    event_id: Union[Unset, UUID] = UNSET
    event_type: Union[Unset, str] = "run_complete"
    occurred_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run = self.run.to_dict()

        event_id: Union[Unset, str] = UNSET
        if not isinstance(self.event_id, Unset):
            event_id = str(self.event_id)

        event_type = self.event_type

        occurred_at: Union[Unset, str] = UNSET
        if not isinstance(self.occurred_at, Unset):
            occurred_at = self.occurred_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run": run,
            }
        )
        if event_id is not UNSET:
            field_dict["event_id"] = event_id
        if event_type is not UNSET:
            field_dict["event_type"] = event_type
        if occurred_at is not UNSET:
            field_dict["occurred_at"] = occurred_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_response import RunResponse

        d = dict(src_dict)
        run = RunResponse.from_dict(d.pop("run"))

        _event_id = d.pop("event_id", UNSET)
        event_id: Union[Unset, UUID]
        if isinstance(_event_id, Unset):
            event_id = UNSET
        else:
            event_id = UUID(_event_id)

        event_type = d.pop("event_type", UNSET)

        _occurred_at = d.pop("occurred_at", UNSET)
        occurred_at: Union[Unset, datetime.datetime]
        if isinstance(_occurred_at, Unset):
            occurred_at = UNSET
        else:
            occurred_at = isoparse(_occurred_at)

        run_completed_event = cls(
            run=run,
            event_id=event_id,
            event_type=event_type,
            occurred_at=occurred_at,
        )

        run_completed_event.additional_properties = d
        return run_completed_event

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
