from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_status import RunStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_update_input_values_type_0 import RunUpdateInputValuesType0
    from ..models.run_update_output_data_type_0 import RunUpdateOutputDataType0
    from ..models.run_update_run_message_history_type_0_item import RunUpdateRunMessageHistoryType0Item


T = TypeVar("T", bound="RunUpdate")


@_attrs_define
class RunUpdate:
    """Schema for updating a run

    Attributes:
        status (Union[None, RunStatus, Unset]):
        error (Union[None, Unset, list[str]]):
        output_data (Union['RunUpdateOutputDataType0', None, Unset]):
        output_attachment_ids (Union[None, Unset, list[str]]):
        run_message_history (Union[None, Unset, list['RunUpdateRunMessageHistoryType0Item']]):
        input_values (Union['RunUpdateInputValuesType0', None, Unset]):
    """

    status: Union[None, RunStatus, Unset] = UNSET
    error: Union[None, Unset, list[str]] = UNSET
    output_data: Union["RunUpdateOutputDataType0", None, Unset] = UNSET
    output_attachment_ids: Union[None, Unset, list[str]] = UNSET
    run_message_history: Union[None, Unset, list["RunUpdateRunMessageHistoryType0Item"]] = UNSET
    input_values: Union["RunUpdateInputValuesType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_update_input_values_type_0 import RunUpdateInputValuesType0
        from ..models.run_update_output_data_type_0 import RunUpdateOutputDataType0

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, RunStatus):
            status = self.status.value
        else:
            status = self.status

        error: Union[None, Unset, list[str]]
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, list):
            error = self.error

        else:
            error = self.error

        output_data: Union[None, Unset, dict[str, Any]]
        if isinstance(self.output_data, Unset):
            output_data = UNSET
        elif isinstance(self.output_data, RunUpdateOutputDataType0):
            output_data = self.output_data.to_dict()
        else:
            output_data = self.output_data

        output_attachment_ids: Union[None, Unset, list[str]]
        if isinstance(self.output_attachment_ids, Unset):
            output_attachment_ids = UNSET
        elif isinstance(self.output_attachment_ids, list):
            output_attachment_ids = self.output_attachment_ids

        else:
            output_attachment_ids = self.output_attachment_ids

        run_message_history: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.run_message_history, Unset):
            run_message_history = UNSET
        elif isinstance(self.run_message_history, list):
            run_message_history = []
            for run_message_history_type_0_item_data in self.run_message_history:
                run_message_history_type_0_item = run_message_history_type_0_item_data.to_dict()
                run_message_history.append(run_message_history_type_0_item)

        else:
            run_message_history = self.run_message_history

        input_values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.input_values, Unset):
            input_values = UNSET
        elif isinstance(self.input_values, RunUpdateInputValuesType0):
            input_values = self.input_values.to_dict()
        else:
            input_values = self.input_values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if error is not UNSET:
            field_dict["error"] = error
        if output_data is not UNSET:
            field_dict["output_data"] = output_data
        if output_attachment_ids is not UNSET:
            field_dict["output_attachment_ids"] = output_attachment_ids
        if run_message_history is not UNSET:
            field_dict["run_message_history"] = run_message_history
        if input_values is not UNSET:
            field_dict["input_values"] = input_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_update_input_values_type_0 import RunUpdateInputValuesType0
        from ..models.run_update_output_data_type_0 import RunUpdateOutputDataType0
        from ..models.run_update_run_message_history_type_0_item import RunUpdateRunMessageHistoryType0Item

        d = dict(src_dict)

        def _parse_status(data: object) -> Union[None, RunStatus, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = RunStatus(data)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RunStatus, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_error(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                error_type_0 = cast(list[str], data)

                return error_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_output_data(data: object) -> Union["RunUpdateOutputDataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_data_type_0 = RunUpdateOutputDataType0.from_dict(data)

                return output_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunUpdateOutputDataType0", None, Unset], data)

        output_data = _parse_output_data(d.pop("output_data", UNSET))

        def _parse_output_attachment_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                output_attachment_ids_type_0 = cast(list[str], data)

                return output_attachment_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        output_attachment_ids = _parse_output_attachment_ids(d.pop("output_attachment_ids", UNSET))

        def _parse_run_message_history(data: object) -> Union[None, Unset, list["RunUpdateRunMessageHistoryType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                run_message_history_type_0 = []
                _run_message_history_type_0 = data
                for run_message_history_type_0_item_data in _run_message_history_type_0:
                    run_message_history_type_0_item = RunUpdateRunMessageHistoryType0Item.from_dict(
                        run_message_history_type_0_item_data
                    )

                    run_message_history_type_0.append(run_message_history_type_0_item)

                return run_message_history_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["RunUpdateRunMessageHistoryType0Item"]], data)

        run_message_history = _parse_run_message_history(d.pop("run_message_history", UNSET))

        def _parse_input_values(data: object) -> Union["RunUpdateInputValuesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_values_type_0 = RunUpdateInputValuesType0.from_dict(data)

                return input_values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunUpdateInputValuesType0", None, Unset], data)

        input_values = _parse_input_values(d.pop("input_values", UNSET))

        run_update = cls(
            status=status,
            error=error,
            output_data=output_data,
            output_attachment_ids=output_attachment_ids,
            run_message_history=run_message_history,
            input_values=input_values,
        )

        run_update.additional_properties = d
        return run_update

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
