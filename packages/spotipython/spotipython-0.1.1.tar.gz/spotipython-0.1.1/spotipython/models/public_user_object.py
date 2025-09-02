from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.public_user_object_type import PublicUserObjectType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject
    from ..models.followers_object import FollowersObject
    from ..models.image_object import ImageObject


T = TypeVar("T", bound="PublicUserObject")


@_attrs_define
class PublicUserObject:
    """
    Attributes:
        display_name (Union[None, Unset, str]): The name displayed on the user's profile. `null` if not available.
        external_urls (Union[Unset, ExternalUrlObject]):
        followers (Union[Unset, FollowersObject]):
        href (Union[Unset, str]): A link to the Web API endpoint for this user.
        id (Union[Unset, str]): The [Spotify user ID](/documentation/web-api/concepts/spotify-uris-ids) for this user.
        images (Union[Unset, list['ImageObject']]): The user's profile image.
        type_ (Union[Unset, PublicUserObjectType]): The object type.
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for this user.
    """

    display_name: Union[None, Unset, str] = UNSET
    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    followers: Union[Unset, "FollowersObject"] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    images: Union[Unset, list["ImageObject"]] = UNSET
    type_: Union[Unset, PublicUserObjectType] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        followers: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.followers, Unset):
            followers = self.followers.to_dict()

        href = self.href

        id = self.id

        images: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item = images_item_data.to_dict()
                images.append(images_item)

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if followers is not UNSET:
            field_dict["followers"] = followers
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if images is not UNSET:
            field_dict["images"] = images
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject
        from ..models.followers_object import FollowersObject
        from ..models.image_object import ImageObject

        d = dict(src_dict)

        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        _followers = d.pop("followers", UNSET)
        followers: Union[Unset, FollowersObject]
        if isinstance(_followers, Unset):
            followers = UNSET
        else:
            followers = FollowersObject.from_dict(_followers)

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        images = []
        _images = d.pop("images", UNSET)
        for images_item_data in _images or []:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, PublicUserObjectType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PublicUserObjectType(_type_)

        uri = d.pop("uri", UNSET)

        public_user_object = cls(
            display_name=display_name,
            external_urls=external_urls,
            followers=followers,
            href=href,
            id=id,
            images=images,
            type_=type_,
            uri=uri,
        )

        public_user_object.additional_properties = d
        return public_user_object

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
