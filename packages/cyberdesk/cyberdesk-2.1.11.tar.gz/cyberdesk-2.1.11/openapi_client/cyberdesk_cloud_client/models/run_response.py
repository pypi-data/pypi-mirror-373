import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.run_status import RunStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_response_input_values_type_0 import RunResponseInputValuesType0
    from ..models.run_response_output_data_type_0 import RunResponseOutputDataType0
    from ..models.run_response_run_message_history_type_0_item import RunResponseRunMessageHistoryType0Item
    from ..models.run_response_sensitive_input_aliases_type_0 import RunResponseSensitiveInputAliasesType0


T = TypeVar("T", bound="RunResponse")


@_attrs_define
class RunResponse:
    """Run response schema

    Attributes:
        workflow_id (UUID):
        machine_id (Union[None, UUID]):
        id (UUID):
        status (RunStatus):
        error (Union[None, list[str]]):
        output_data (Union['RunResponseOutputDataType0', None]):
        input_attachment_ids (Union[None, list[str]]):
        output_attachment_ids (Union[None, list[str]]):
        run_message_history (Union[None, list['RunResponseRunMessageHistoryType0Item']]):
        input_values (Union['RunResponseInputValuesType0', None]):
        created_at (datetime.datetime):
        user_id (Union[None, UUID, Unset]):
        organization_id (Union[None, Unset, str]):
        pool_ids (Union[None, Unset, list[UUID]]):
        sensitive_input_aliases (Union['RunResponseSensitiveInputAliasesType0', None, Unset]):
        session_id (Union[None, UUID, Unset]):
        session_alias (Union[None, Unset, str]):
        release_session_after (Union[None, Unset, bool]):
    """

    workflow_id: UUID
    machine_id: Union[None, UUID]
    id: UUID
    status: RunStatus
    error: Union[None, list[str]]
    output_data: Union["RunResponseOutputDataType0", None]
    input_attachment_ids: Union[None, list[str]]
    output_attachment_ids: Union[None, list[str]]
    run_message_history: Union[None, list["RunResponseRunMessageHistoryType0Item"]]
    input_values: Union["RunResponseInputValuesType0", None]
    created_at: datetime.datetime
    user_id: Union[None, UUID, Unset] = UNSET
    organization_id: Union[None, Unset, str] = UNSET
    pool_ids: Union[None, Unset, list[UUID]] = UNSET
    sensitive_input_aliases: Union["RunResponseSensitiveInputAliasesType0", None, Unset] = UNSET
    session_id: Union[None, UUID, Unset] = UNSET
    session_alias: Union[None, Unset, str] = UNSET
    release_session_after: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_response_input_values_type_0 import RunResponseInputValuesType0
        from ..models.run_response_output_data_type_0 import RunResponseOutputDataType0
        from ..models.run_response_sensitive_input_aliases_type_0 import RunResponseSensitiveInputAliasesType0

        workflow_id = str(self.workflow_id)

        machine_id: Union[None, str]
        if isinstance(self.machine_id, UUID):
            machine_id = str(self.machine_id)
        else:
            machine_id = self.machine_id

        id = str(self.id)

        status = self.status.value

        error: Union[None, list[str]]
        if isinstance(self.error, list):
            error = self.error

        else:
            error = self.error

        output_data: Union[None, dict[str, Any]]
        if isinstance(self.output_data, RunResponseOutputDataType0):
            output_data = self.output_data.to_dict()
        else:
            output_data = self.output_data

        input_attachment_ids: Union[None, list[str]]
        if isinstance(self.input_attachment_ids, list):
            input_attachment_ids = self.input_attachment_ids

        else:
            input_attachment_ids = self.input_attachment_ids

        output_attachment_ids: Union[None, list[str]]
        if isinstance(self.output_attachment_ids, list):
            output_attachment_ids = self.output_attachment_ids

        else:
            output_attachment_ids = self.output_attachment_ids

        run_message_history: Union[None, list[dict[str, Any]]]
        if isinstance(self.run_message_history, list):
            run_message_history = []
            for run_message_history_type_0_item_data in self.run_message_history:
                run_message_history_type_0_item = run_message_history_type_0_item_data.to_dict()
                run_message_history.append(run_message_history_type_0_item)

        else:
            run_message_history = self.run_message_history

        input_values: Union[None, dict[str, Any]]
        if isinstance(self.input_values, RunResponseInputValuesType0):
            input_values = self.input_values.to_dict()
        else:
            input_values = self.input_values

        created_at = self.created_at.isoformat()

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

        sensitive_input_aliases: Union[None, Unset, dict[str, Any]]
        if isinstance(self.sensitive_input_aliases, Unset):
            sensitive_input_aliases = UNSET
        elif isinstance(self.sensitive_input_aliases, RunResponseSensitiveInputAliasesType0):
            sensitive_input_aliases = self.sensitive_input_aliases.to_dict()
        else:
            sensitive_input_aliases = self.sensitive_input_aliases

        session_id: Union[None, Unset, str]
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        elif isinstance(self.session_id, UUID):
            session_id = str(self.session_id)
        else:
            session_id = self.session_id

        session_alias: Union[None, Unset, str]
        if isinstance(self.session_alias, Unset):
            session_alias = UNSET
        else:
            session_alias = self.session_alias

        release_session_after: Union[None, Unset, bool]
        if isinstance(self.release_session_after, Unset):
            release_session_after = UNSET
        else:
            release_session_after = self.release_session_after

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
                "machine_id": machine_id,
                "id": id,
                "status": status,
                "error": error,
                "output_data": output_data,
                "input_attachment_ids": input_attachment_ids,
                "output_attachment_ids": output_attachment_ids,
                "run_message_history": run_message_history,
                "input_values": input_values,
                "created_at": created_at,
            }
        )
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if pool_ids is not UNSET:
            field_dict["pool_ids"] = pool_ids
        if sensitive_input_aliases is not UNSET:
            field_dict["sensitive_input_aliases"] = sensitive_input_aliases
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if session_alias is not UNSET:
            field_dict["session_alias"] = session_alias
        if release_session_after is not UNSET:
            field_dict["release_session_after"] = release_session_after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_response_input_values_type_0 import RunResponseInputValuesType0
        from ..models.run_response_output_data_type_0 import RunResponseOutputDataType0
        from ..models.run_response_run_message_history_type_0_item import RunResponseRunMessageHistoryType0Item
        from ..models.run_response_sensitive_input_aliases_type_0 import RunResponseSensitiveInputAliasesType0

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        def _parse_machine_id(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                machine_id_type_0 = UUID(data)

                return machine_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        machine_id = _parse_machine_id(d.pop("machine_id"))

        id = UUID(d.pop("id"))

        status = RunStatus(d.pop("status"))

        def _parse_error(data: object) -> Union[None, list[str]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                error_type_0 = cast(list[str], data)

                return error_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[str]], data)

        error = _parse_error(d.pop("error"))

        def _parse_output_data(data: object) -> Union["RunResponseOutputDataType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_data_type_0 = RunResponseOutputDataType0.from_dict(data)

                return output_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunResponseOutputDataType0", None], data)

        output_data = _parse_output_data(d.pop("output_data"))

        def _parse_input_attachment_ids(data: object) -> Union[None, list[str]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                input_attachment_ids_type_0 = cast(list[str], data)

                return input_attachment_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[str]], data)

        input_attachment_ids = _parse_input_attachment_ids(d.pop("input_attachment_ids"))

        def _parse_output_attachment_ids(data: object) -> Union[None, list[str]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                output_attachment_ids_type_0 = cast(list[str], data)

                return output_attachment_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[str]], data)

        output_attachment_ids = _parse_output_attachment_ids(d.pop("output_attachment_ids"))

        def _parse_run_message_history(data: object) -> Union[None, list["RunResponseRunMessageHistoryType0Item"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                run_message_history_type_0 = []
                _run_message_history_type_0 = data
                for run_message_history_type_0_item_data in _run_message_history_type_0:
                    run_message_history_type_0_item = RunResponseRunMessageHistoryType0Item.from_dict(
                        run_message_history_type_0_item_data
                    )

                    run_message_history_type_0.append(run_message_history_type_0_item)

                return run_message_history_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list["RunResponseRunMessageHistoryType0Item"]], data)

        run_message_history = _parse_run_message_history(d.pop("run_message_history"))

        def _parse_input_values(data: object) -> Union["RunResponseInputValuesType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_values_type_0 = RunResponseInputValuesType0.from_dict(data)

                return input_values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunResponseInputValuesType0", None], data)

        input_values = _parse_input_values(d.pop("input_values"))

        created_at = isoparse(d.pop("created_at"))

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

        def _parse_sensitive_input_aliases(data: object) -> Union["RunResponseSensitiveInputAliasesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sensitive_input_aliases_type_0 = RunResponseSensitiveInputAliasesType0.from_dict(data)

                return sensitive_input_aliases_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RunResponseSensitiveInputAliasesType0", None, Unset], data)

        sensitive_input_aliases = _parse_sensitive_input_aliases(d.pop("sensitive_input_aliases", UNSET))

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

        def _parse_session_alias(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        session_alias = _parse_session_alias(d.pop("session_alias", UNSET))

        def _parse_release_session_after(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        release_session_after = _parse_release_session_after(d.pop("release_session_after", UNSET))

        run_response = cls(
            workflow_id=workflow_id,
            machine_id=machine_id,
            id=id,
            status=status,
            error=error,
            output_data=output_data,
            input_attachment_ids=input_attachment_ids,
            output_attachment_ids=output_attachment_ids,
            run_message_history=run_message_history,
            input_values=input_values,
            created_at=created_at,
            user_id=user_id,
            organization_id=organization_id,
            pool_ids=pool_ids,
            sensitive_input_aliases=sensitive_input_aliases,
            session_id=session_id,
            session_alias=session_alias,
            release_session_after=release_session_after,
        )

        run_response.additional_properties = d
        return run_response

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
