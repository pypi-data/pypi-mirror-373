from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WorkflowChainResponse")


@_attrs_define
class WorkflowChainResponse:
    """Response for chain creation

    Attributes:
        session_id (UUID):
        run_ids (list[UUID]):
    """

    session_id: UUID
    run_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = str(self.session_id)

        run_ids = []
        for run_ids_item_data in self.run_ids:
            run_ids_item = str(run_ids_item_data)
            run_ids.append(run_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session_id": session_id,
                "run_ids": run_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_id = UUID(d.pop("session_id"))

        run_ids = []
        _run_ids = d.pop("run_ids")
        for run_ids_item_data in _run_ids:
            run_ids_item = UUID(run_ids_item_data)

            run_ids.append(run_ids_item)

        workflow_chain_response = cls(
            session_id=session_id,
            run_ids=run_ids,
        )

        workflow_chain_response.additional_properties = d
        return workflow_chain_response

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
