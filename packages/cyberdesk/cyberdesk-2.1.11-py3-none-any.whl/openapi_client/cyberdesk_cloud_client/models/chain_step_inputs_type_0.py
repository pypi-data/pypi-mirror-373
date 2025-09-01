from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ref_value import RefValue


T = TypeVar("T", bound="ChainStepInputsType0")


@_attrs_define
class ChainStepInputsType0:
    """ """

    additional_properties: dict[str, Union["RefValue", str]] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ref_value import RefValue

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, RefValue):
                field_dict[prop_name] = prop.to_dict()
            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ref_value import RefValue

        d = dict(src_dict)
        chain_step_inputs_type_0 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: object) -> Union["RefValue", str]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property_type_1 = RefValue.from_dict(data)

                    return additional_property_type_1
                except:  # noqa: E722
                    pass
                return cast(Union["RefValue", str], data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        chain_step_inputs_type_0.additional_properties = additional_properties
        return chain_step_inputs_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union["RefValue", str]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union["RefValue", str]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
