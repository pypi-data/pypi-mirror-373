from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost")


@_attrs_define
class DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost:
    """ """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dummy_test_endpoint_v1_test_post_response_dummy_test_endpoint_v1_test_post = cls()

        dummy_test_endpoint_v1_test_post_response_dummy_test_endpoint_v1_test_post.additional_properties = d
        return dummy_test_endpoint_v1_test_post_response_dummy_test_endpoint_v1_test_post

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
