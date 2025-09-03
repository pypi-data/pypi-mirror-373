from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UnfollowArtistsUsersBody")


@_attrs_define
class UnfollowArtistsUsersBody:
    """
    Attributes:
        ids (Union[Unset, list[str]]): A JSON array of the artist or user [Spotify IDs](/documentation/web-
            api/concepts/spotify-uris-ids). For example: `{ids:["74ASZWbe4lXaubB36ztrGX", "08td7MxkoHQkXnWAYD8d6Q"]}`. A
            maximum of 50 IDs can be sent in one request. _**Note**: if the `ids` parameter is present in the query string,
            any IDs listed here in the body will be ignored._
    """

    ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.ids, Unset):
            ids = self.ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ids is not UNSET:
            field_dict["ids"] = ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ids = cast(list[str], d.pop("ids", UNSET))

        unfollow_artists_users_body = cls(
            ids=ids,
        )

        unfollow_artists_users_body.additional_properties = d
        return unfollow_artists_users_body

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
