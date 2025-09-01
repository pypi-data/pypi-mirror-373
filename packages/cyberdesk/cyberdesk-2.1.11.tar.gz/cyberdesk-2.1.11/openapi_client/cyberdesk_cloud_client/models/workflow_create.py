from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowCreate")


@_attrs_define
class WorkflowCreate:
    """Schema for creating a workflow

    Attributes:
        main_prompt (str):
        name (Union[None, Unset, str]):
        output_schema (Union[None, Unset, str]): JSON schema for output data transformation
        includes_file_exports (Union[Unset, bool]): Enable AI-based file export detection Default: False.
        is_webhooks_enabled (Union[Unset, bool]): Send webhook on run completion Default: False.
    """

    main_prompt: str
    name: Union[None, Unset, str] = UNSET
    output_schema: Union[None, Unset, str] = UNSET
    includes_file_exports: Union[Unset, bool] = False
    is_webhooks_enabled: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        main_prompt = self.main_prompt

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        output_schema: Union[None, Unset, str]
        if isinstance(self.output_schema, Unset):
            output_schema = UNSET
        else:
            output_schema = self.output_schema

        includes_file_exports = self.includes_file_exports

        is_webhooks_enabled = self.is_webhooks_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "main_prompt": main_prompt,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if output_schema is not UNSET:
            field_dict["output_schema"] = output_schema
        if includes_file_exports is not UNSET:
            field_dict["includes_file_exports"] = includes_file_exports
        if is_webhooks_enabled is not UNSET:
            field_dict["is_webhooks_enabled"] = is_webhooks_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        main_prompt = d.pop("main_prompt")

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_output_schema(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        output_schema = _parse_output_schema(d.pop("output_schema", UNSET))

        includes_file_exports = d.pop("includes_file_exports", UNSET)

        is_webhooks_enabled = d.pop("is_webhooks_enabled", UNSET)

        workflow_create = cls(
            main_prompt=main_prompt,
            name=name,
            output_schema=output_schema,
            includes_file_exports=includes_file_exports,
            is_webhooks_enabled=is_webhooks_enabled,
        )

        workflow_create.additional_properties = d
        return workflow_create

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
