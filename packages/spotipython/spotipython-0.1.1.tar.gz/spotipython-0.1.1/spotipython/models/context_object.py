from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject


T = TypeVar("T", bound="ContextObject")


@_attrs_define
class ContextObject:
    """
    Attributes:
        type_ (Union[Unset, str]): The object type, e.g. "artist", "playlist", "album", "show".
        href (Union[Unset, str]): A link to the Web API endpoint providing full details of the track.
        external_urls (Union[Unset, ExternalUrlObject]):
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the context.
    """

    type_: Union[Unset, str] = UNSET
    href: Union[Unset, str] = UNSET
    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        href = self.href

        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if href is not UNSET:
            field_dict["href"] = href
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        href = d.pop("href", UNSET)

        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        uri = d.pop("uri", UNSET)

        context_object = cls(
            type_=type_,
            href=href,
            external_urls=external_urls,
            uri=uri,
        )

        context_object.additional_properties = d
        return context_object

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
