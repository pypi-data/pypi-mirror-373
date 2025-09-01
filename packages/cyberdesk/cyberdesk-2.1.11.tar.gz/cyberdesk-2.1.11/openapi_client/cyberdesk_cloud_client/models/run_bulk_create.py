from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_input import FileInput
    from ..models.run_bulk_create_input_values_type_0 import RunBulkCreateInputValuesType0
    from ..models.run_bulk_create_sensitive_input_values_type_0 import RunBulkCreateSensitiveInputValuesType0


T = TypeVar("T", bound="RunBulkCreate")


@_attrs_define
class RunBulkCreate:
    """Schema for bulk creating runs

    Attributes:
        workflow_id (UUID):
        count (int): Number of runs to create (max 1000)
        machine_id (Union[None, UUID, Unset]): Machine ID. If not provided, an available machine will be automatically
            selected.
        pool_ids (Union[None, Unset, list[UUID]]): Pool IDs to filter available machines. Machine must belong to all of
            these pools (intersection). Ignored when machine_id is provided.
        input_values (Union['RunBulkCreateInputValuesType0', None, Unset]): Input values for workflow variables
        file_inputs (Union[None, Unset, list['FileInput']]): Files to upload to the machine
        sensitive_input_values (Union['RunBulkCreateSensitiveInputValuesType0', None, Unset]): Sensitive input values to
            store in the secure vault per run. Not persisted in our database.
        session_id (Union[None, UUID, Unset]): Join an existing session; overrides machine_id/pool_ids for all runs
        start_session (Union[None, Unset, bool]): Start a new session for these runs; a new UUID will be generated and
            set on all runs. The first run will attempt to reserve a machine. Default: False.
    """

    workflow_id: UUID
    count: int
    machine_id: Union[None, UUID, Unset] = UNSET
    pool_ids: Union[None, Unset, list[UUID]] = UNSET
    input_values: Union["RunBulkCreateInputValuesType0", None, Unset] = UNSET
    file_inputs: Union[None, Unset, list["FileInput"]] = UNSET
    sensitive_input_values: Union["RunBulkCreateSensitiveInputValuesType0", None, Unset] = UNSET
    session_id: Union[None, UUID, Unset] = UNSET
    start_session: Union[None, Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_bulk_create_input_values_type_0 import RunBulkCreateInputValuesType0
        from ..models.run_bulk_create_sensitive_input_values_type_0 import RunBulkCreateSensitiveInputValuesType0

        workflow_id = str(self.workflow_id)

        count = self.count

        machine_id: Union[None, Unset, str]
        if isinstance(self.machine_id, Unset):
            machine_id = UNSET
        elif isinstance(self.machine_id, UUID):
            machine_id = str(self.machine_id)
        else:
            machine_id = self.machine_id

        pool_ids: Union[None, Unset, list[str]]
        if isinstance(self.pool_ids, Unset):
            pool_ids = UNSET
        elif isinstance(self.pool_ids, list):
            pool_ids = []
            for pool_ids_type_0_item_data in self.pool_ids:
                pool_ids_type_0_item = str(pool_ids_type_0_item_data)
                pool_ids.append(pool_ids_type_0_item)

        else:
            pool_ids = self.pool_ids

        input_values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.input_values, Unset):
            input_values = UNSET
        elif isinstance(self.input_values, RunBulkCreateInputValuesType0):
            input_values = self.input_values.to_dict()
        else:
            input_values = self.input_values

        file_inputs: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.file_inputs, Unset):
            file_inputs = UNSET
        elif isinstance(self.file_inputs, list):
            file_inputs = []
            for file_inputs_type_0_item_data in self.file_inputs:
                file_inputs_type_0_item = file_inputs_type_0_item_data.to_dict()
                file_inputs.append(file_inputs_type_0_item)

        else:
            file_inputs = self.file_inputs

        sensitive_input_values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.sensitive_input_values, Unset):
            sensitive_input_values = UNSET
        elif isinstance(self.sensitive_input_values, RunBulkCreateSensitiveInputValuesType0):
            sensitive_input_values = self.sensitive_input_values.to_dict()
        else:
            sensitive_input_values = self.sensitive_input_values

        session_id: Union[None, Unset, str]
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        elif isinstance(self.session_id, UUID):
            session_id = str(self.session_id)
        else:
            session_id = self.session_id

        start_session: Union[None, Unset, bool]
        if isinstance(self.start_session, Unset):
            start_session = UNSET
        else:
            start_session = self.start_session

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
                "count": count,
            }
        )
        if machine_id is not UNSET:
            field_dict["machine_id"] = machine_id
        if pool_ids is not UNSET:
            field_dict["pool_ids"] = pool_ids
        if input_values is not UNSET:
            field_dict["input_values"] = input_values
        if file_inputs is not UNSET:
            field_dict["file_inputs"] = file_inputs
        if sensitive_input_values is not UNSET:
            field_dict["sensitive_input_values"] = sensitive_input_values
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if start_session is not UNSET:
            field_dict["start_session"] = start_session

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_input import FileInput
        from ..models.run_bulk_create_input_values_type_0 import RunBulkCreateInputValuesType0
        from ..models.run_bulk_create_sensitive_input_values_type_0 import RunBulkCreateSensitiveInputValuesType0

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        count = d.pop("count")

        def _parse_machine_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                machine_id_type_0 = UUID(data)

                return machine_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        machine_id = _parse_machine_id(d.pop("machine_id", UNSET))

        def _parse_pool_ids(data: object) -> Union[None, Unset, list[UUID]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                pool_ids_type_0 = []
                _pool_ids_type_0 = data
                for pool_ids_type_0_item_data in _pool_ids_type_0:
                    pool_ids_type_0_item = UUID(pool_ids_type_0_item_data)

                    pool_ids_type_0.append(pool_ids_type_0_item)

                return pool_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[UUID]], data)

        pool_ids = _parse_pool_ids(d.pop("pool_ids", UNSET))

        def _parse_input_values(data: object) -> Union["RunBulkCreateInputValuesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_values_type_0 = RunBulkCreateInputValuesType0.from_dict(data)

                return input_values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunBulkCreateInputValuesType0", None, Unset], data)

        input_values = _parse_input_values(d.pop("input_values", UNSET))

        def _parse_file_inputs(data: object) -> Union[None, Unset, list["FileInput"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                file_inputs_type_0 = []
                _file_inputs_type_0 = data
                for file_inputs_type_0_item_data in _file_inputs_type_0:
                    file_inputs_type_0_item = FileInput.from_dict(file_inputs_type_0_item_data)

                    file_inputs_type_0.append(file_inputs_type_0_item)

                return file_inputs_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["FileInput"]], data)

        file_inputs = _parse_file_inputs(d.pop("file_inputs", UNSET))

        def _parse_sensitive_input_values(data: object) -> Union["RunBulkCreateSensitiveInputValuesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sensitive_input_values_type_0 = RunBulkCreateSensitiveInputValuesType0.from_dict(data)

                return sensitive_input_values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunBulkCreateSensitiveInputValuesType0", None, Unset], data)

        sensitive_input_values = _parse_sensitive_input_values(d.pop("sensitive_input_values", UNSET))

        def _parse_session_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                session_id_type_0 = UUID(data)

                return session_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        session_id = _parse_session_id(d.pop("session_id", UNSET))

        def _parse_start_session(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        start_session = _parse_start_session(d.pop("start_session", UNSET))

        run_bulk_create = cls(
            workflow_id=workflow_id,
            count=count,
            machine_id=machine_id,
            pool_ids=pool_ids,
            input_values=input_values,
            file_inputs=file_inputs,
            sensitive_input_values=sensitive_input_values,
            session_id=session_id,
            start_session=start_session,
        )

        run_bulk_create.additional_properties = d
        return run_bulk_create

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
