from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowUpdate")


@_attrs_define
class WorkflowUpdate:
    """Schema for updating a workflow

    Attributes:
        name (Union[None, Unset, str]):
        main_prompt (Union[None, Unset, str]):
        output_schema (Union[None, Unset, str]): JSON schema for output data transformation
        includes_file_exports (Union[None, Unset, bool]): Enable AI-based file export detection
        is_webhooks_enabled (Union[None, Unset, bool]): Send webhook on run completion
    """

    name: Union[None, Unset, str] = UNSET
    main_prompt: Union[None, Unset, str] = UNSET
    output_schema: Union[None, Unset, str] = UNSET
    includes_file_exports: Union[None, Unset, bool] = UNSET
    is_webhooks_enabled: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        main_prompt: Union[None, Unset, str]
        if isinstance(self.main_prompt, Unset):
            main_prompt = UNSET
        else:
            main_prompt = self.main_prompt

        output_schema: Union[None, Unset, str]
        if isinstance(self.output_schema, Unset):
            output_schema = UNSET
        else:
            output_schema = self.output_schema

        includes_file_exports: Union[None, Unset, bool]
        if isinstance(self.includes_file_exports, Unset):
            includes_file_exports = UNSET
        else:
            includes_file_exports = self.includes_file_exports

        is_webhooks_enabled: Union[None, Unset, bool]
        if isinstance(self.is_webhooks_enabled, Unset):
            is_webhooks_enabled = UNSET
        else:
            is_webhooks_enabled = self.is_webhooks_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if main_prompt is not UNSET:
            field_dict["main_prompt"] = main_prompt
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

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_main_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        main_prompt = _parse_main_prompt(d.pop("main_prompt", UNSET))

        def _parse_output_schema(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        output_schema = _parse_output_schema(d.pop("output_schema", UNSET))

        def _parse_includes_file_exports(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        includes_file_exports = _parse_includes_file_exports(d.pop("includes_file_exports", UNSET))

        def _parse_is_webhooks_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_webhooks_enabled = _parse_is_webhooks_enabled(d.pop("is_webhooks_enabled", UNSET))

        workflow_update = cls(
            name=name,
            main_prompt=main_prompt,
            output_schema=output_schema,
            includes_file_exports=includes_file_exports,
            is_webhooks_enabled=is_webhooks_enabled,
        )

        workflow_update.additional_properties = d
        return workflow_update

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
