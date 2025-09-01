from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.trajectory_update_trajectory_data_type_0_item import TrajectoryUpdateTrajectoryDataType0Item


T = TypeVar("T", bound="TrajectoryUpdate")


@_attrs_define
class TrajectoryUpdate:
    """Schema for updating a trajectory

    Attributes:
        name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        trajectory_data (Union[None, Unset, list['TrajectoryUpdateTrajectoryDataType0Item']]):
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    trajectory_data: Union[None, Unset, list["TrajectoryUpdateTrajectoryDataType0Item"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        trajectory_data: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.trajectory_data, Unset):
            trajectory_data = UNSET
        elif isinstance(self.trajectory_data, list):
            trajectory_data = []
            for trajectory_data_type_0_item_data in self.trajectory_data:
                trajectory_data_type_0_item = trajectory_data_type_0_item_data.to_dict()
                trajectory_data.append(trajectory_data_type_0_item)

        else:
            trajectory_data = self.trajectory_data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if trajectory_data is not UNSET:
            field_dict["trajectory_data"] = trajectory_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trajectory_update_trajectory_data_type_0_item import TrajectoryUpdateTrajectoryDataType0Item

        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_trajectory_data(data: object) -> Union[None, Unset, list["TrajectoryUpdateTrajectoryDataType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                trajectory_data_type_0 = []
                _trajectory_data_type_0 = data
                for trajectory_data_type_0_item_data in _trajectory_data_type_0:
                    trajectory_data_type_0_item = TrajectoryUpdateTrajectoryDataType0Item.from_dict(
                        trajectory_data_type_0_item_data
                    )

                    trajectory_data_type_0.append(trajectory_data_type_0_item)

                return trajectory_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TrajectoryUpdateTrajectoryDataType0Item"]], data)

        trajectory_data = _parse_trajectory_data(d.pop("trajectory_data", UNSET))

        trajectory_update = cls(
            name=name,
            description=description,
            trajectory_data=trajectory_data,
        )

        trajectory_update.additional_properties = d
        return trajectory_update

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
