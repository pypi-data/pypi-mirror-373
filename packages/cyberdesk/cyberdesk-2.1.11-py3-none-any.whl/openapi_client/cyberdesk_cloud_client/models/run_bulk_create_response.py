from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_response import RunResponse


T = TypeVar("T", bound="RunBulkCreateResponse")


@_attrs_define
class RunBulkCreateResponse:
    """Response for bulk run creation

    Attributes:
        created_runs (list['RunResponse']):
        failed_count (Union[Unset, int]):  Default: 0.
        errors (Union[Unset, list[str]]):
    """

    created_runs: list["RunResponse"]
    failed_count: Union[Unset, int] = 0
    errors: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_runs = []
        for created_runs_item_data in self.created_runs:
            created_runs_item = created_runs_item_data.to_dict()
            created_runs.append(created_runs_item)

        failed_count = self.failed_count

        errors: Union[Unset, list[str]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_runs": created_runs,
            }
        )
        if failed_count is not UNSET:
            field_dict["failed_count"] = failed_count
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_response import RunResponse

        d = dict(src_dict)
        created_runs = []
        _created_runs = d.pop("created_runs")
        for created_runs_item_data in _created_runs:
            created_runs_item = RunResponse.from_dict(created_runs_item_data)

            created_runs.append(created_runs_item)

        failed_count = d.pop("failed_count", UNSET)

        errors = cast(list[str], d.pop("errors", UNSET))

        run_bulk_create_response = cls(
            created_runs=created_runs,
            failed_count=failed_count,
            errors=errors,
        )

        run_bulk_create_response.additional_properties = d
        return run_bulk_create_response

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
