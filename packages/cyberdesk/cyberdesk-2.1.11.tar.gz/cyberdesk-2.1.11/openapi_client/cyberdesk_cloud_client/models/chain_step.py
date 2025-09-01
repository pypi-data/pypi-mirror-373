from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chain_step_inputs_type_0 import ChainStepInputsType0


T = TypeVar("T", bound="ChainStep")


@_attrs_define
class ChainStep:
    """One step within a chain

    Attributes:
        workflow_id (UUID):
        session_alias (Union[None, Unset, str]): Alias to persist this step's outputs within the session
        inputs (Union['ChainStepInputsType0', None, Unset]): Step-specific inputs; values must be string or {$ref:
            'alias.outputs.path'}
    """

    workflow_id: UUID
    session_alias: Union[None, Unset, str] = UNSET
    inputs: Union["ChainStepInputsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chain_step_inputs_type_0 import ChainStepInputsType0

        workflow_id = str(self.workflow_id)

        session_alias: Union[None, Unset, str]
        if isinstance(self.session_alias, Unset):
            session_alias = UNSET
        else:
            session_alias = self.session_alias

        inputs: Union[None, Unset, dict[str, Any]]
        if isinstance(self.inputs, Unset):
            inputs = UNSET
        elif isinstance(self.inputs, ChainStepInputsType0):
            inputs = self.inputs.to_dict()
        else:
            inputs = self.inputs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
            }
        )
        if session_alias is not UNSET:
            field_dict["session_alias"] = session_alias
        if inputs is not UNSET:
            field_dict["inputs"] = inputs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chain_step_inputs_type_0 import ChainStepInputsType0

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        def _parse_session_alias(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        session_alias = _parse_session_alias(d.pop("session_alias", UNSET))

        def _parse_inputs(data: object) -> Union["ChainStepInputsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                inputs_type_0 = ChainStepInputsType0.from_dict(data)

                return inputs_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ChainStepInputsType0", None, Unset], data)

        inputs = _parse_inputs(d.pop("inputs", UNSET))

        chain_step = cls(
            workflow_id=workflow_id,
            session_alias=session_alias,
            inputs=inputs,
        )

        chain_step.additional_properties = d
        return chain_step

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
