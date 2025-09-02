from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExternalIdObject")


@_attrs_define
class ExternalIdObject:
    """
    Attributes:
        ean (Union[Unset, str]): [International Article
            Number](http://en.wikipedia.org/wiki/International_Article_Number_%28EAN%29)
        isrc (Union[Unset, str]): [International Standard Recording
            Code](http://en.wikipedia.org/wiki/International_Standard_Recording_Code)
        upc (Union[Unset, str]): [Universal Product Code](http://en.wikipedia.org/wiki/Universal_Product_Code)
    """

    ean: Union[Unset, str] = UNSET
    isrc: Union[Unset, str] = UNSET
    upc: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ean = self.ean

        isrc = self.isrc

        upc = self.upc

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ean is not UNSET:
            field_dict["ean"] = ean
        if isrc is not UNSET:
            field_dict["isrc"] = isrc
        if upc is not UNSET:
            field_dict["upc"] = upc

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ean = d.pop("ean", UNSET)

        isrc = d.pop("isrc", UNSET)

        upc = d.pop("upc", UNSET)

        external_id_object = cls(
            ean=ean,
            isrc=isrc,
            upc=upc,
        )

        external_id_object.additional_properties = d
        return external_id_object

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
