from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetAvailableMarketsResponse200")


@_attrs_define
class GetAvailableMarketsResponse200:
    """
    Attributes:
        markets (Union[Unset, list[str]]):  Example: ['CA', 'BR', 'IT'].
    """

    markets: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markets: Union[Unset, list[str]] = UNSET
        if not isinstance(self.markets, Unset):
            markets = self.markets

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if markets is not UNSET:
            field_dict["markets"] = markets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        markets = cast(list[str], d.pop("markets", UNSET))

        get_available_markets_response_200 = cls(
            markets=markets,
        )

        get_available_markets_response_200.additional_properties = d
        return get_available_markets_response_200

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
