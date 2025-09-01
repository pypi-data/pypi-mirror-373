from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MouseClickRequest")


@_attrs_define
class MouseClickRequest:
    """
    Attributes:
        x (Union[None, Unset, int]):
        y (Union[None, Unset, int]):
        button (Union[Unset, str]):  Default: 'left'.
        down (Union[None, Unset, bool]): None = full click, True = mouse down, False = mouse up
    """

    x: Union[None, Unset, int] = UNSET
    y: Union[None, Unset, int] = UNSET
    button: Union[Unset, str] = "left"
    down: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        x: Union[None, Unset, int]
        if isinstance(self.x, Unset):
            x = UNSET
        else:
            x = self.x

        y: Union[None, Unset, int]
        if isinstance(self.y, Unset):
            y = UNSET
        else:
            y = self.y

        button = self.button

        down: Union[None, Unset, bool]
        if isinstance(self.down, Unset):
            down = UNSET
        else:
            down = self.down

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if button is not UNSET:
            field_dict["button"] = button
        if down is not UNSET:
            field_dict["down"] = down

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_x(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        x = _parse_x(d.pop("x", UNSET))

        def _parse_y(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        y = _parse_y(d.pop("y", UNSET))

        button = d.pop("button", UNSET)

        def _parse_down(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        down = _parse_down(d.pop("down", UNSET))

        mouse_click_request = cls(
            x=x,
            y=y,
            button=button,
            down=down,
        )

        mouse_click_request.additional_properties = d
        return mouse_click_request

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
