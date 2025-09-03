from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RecommendationSeedObject")


@_attrs_define
class RecommendationSeedObject:
    r"""
    Attributes:
        after_filtering_size (Union[Unset, int]): The number of tracks available after min\_\* and max\_\* filters have
            been applied.
        after_relinking_size (Union[Unset, int]): The number of tracks available after relinking for regional
            availability.
        href (Union[Unset, str]): A link to the full track or artist data for this seed. For tracks this will be a link
            to a Track Object. For artists a link to an Artist Object. For genre seeds, this value will be `null`.
        id (Union[Unset, str]): The id used to select this seed. This will be the same as the string used in the
            `seed_artists`, `seed_tracks` or `seed_genres` parameter.
        initial_pool_size (Union[Unset, int]): The number of recommended tracks available for this seed.
        type_ (Union[Unset, str]): The entity type of this seed. One of `artist`, `track` or `genre`.
    """

    after_filtering_size: Union[Unset, int] = UNSET
    after_relinking_size: Union[Unset, int] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    initial_pool_size: Union[Unset, int] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        after_filtering_size = self.after_filtering_size

        after_relinking_size = self.after_relinking_size

        href = self.href

        id = self.id

        initial_pool_size = self.initial_pool_size

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if after_filtering_size is not UNSET:
            field_dict["afterFilteringSize"] = after_filtering_size
        if after_relinking_size is not UNSET:
            field_dict["afterRelinkingSize"] = after_relinking_size
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if initial_pool_size is not UNSET:
            field_dict["initialPoolSize"] = initial_pool_size
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        after_filtering_size = d.pop("afterFilteringSize", UNSET)

        after_relinking_size = d.pop("afterRelinkingSize", UNSET)

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        initial_pool_size = d.pop("initialPoolSize", UNSET)

        type_ = d.pop("type", UNSET)

        recommendation_seed_object = cls(
            after_filtering_size=after_filtering_size,
            after_relinking_size=after_relinking_size,
            href=href,
            id=id,
            initial_pool_size=initial_pool_size,
            type_=type_,
        )

        recommendation_seed_object.additional_properties = d
        return recommendation_seed_object

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
