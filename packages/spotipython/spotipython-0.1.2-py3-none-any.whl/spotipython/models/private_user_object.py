from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.explicit_content_settings_object import ExplicitContentSettingsObject
    from ..models.external_url_object import ExternalUrlObject
    from ..models.followers_object import FollowersObject
    from ..models.image_object import ImageObject


T = TypeVar("T", bound="PrivateUserObject")


@_attrs_define
class PrivateUserObject:
    """
    Attributes:
        country (Union[Unset, str]): The country of the user, as set in the user's account profile. An [ISO 3166-1
            alpha-2 country code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). _This field is only available when the
            current user has granted access to the [user-read-private](/documentation/web-api/concepts/scopes/#list-of-
            scopes) scope._
        display_name (Union[Unset, str]): The name displayed on the user's profile. `null` if not available.
        email (Union[Unset, str]): The user's email address, as entered by the user when creating their account.
            _**Important!** This email address is unverified; there is no proof that it actually belongs to the user._ _This
            field is only available when the current user has granted access to the [user-read-email](/documentation/web-
            api/concepts/scopes/#list-of-scopes) scope._
        explicit_content (Union[Unset, ExplicitContentSettingsObject]):
        external_urls (Union[Unset, ExternalUrlObject]):
        followers (Union[Unset, FollowersObject]):
        href (Union[Unset, str]): A link to the Web API endpoint for this user.
        id (Union[Unset, str]): The [Spotify user ID](/documentation/web-api/concepts/spotify-uris-ids) for the user.
        images (Union[Unset, list['ImageObject']]): The user's profile image.
        product (Union[Unset, str]): The user's Spotify subscription level: "premium", "free", etc. (The subscription
            level "open" can be considered the same as "free".) _This field is only available when the current user has
            granted access to the [user-read-private](/documentation/web-api/concepts/scopes/#list-of-scopes) scope._
        type_ (Union[Unset, str]): The object type: "user"
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the user.
    """

    country: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    explicit_content: Union[Unset, "ExplicitContentSettingsObject"] = UNSET
    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    followers: Union[Unset, "FollowersObject"] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    images: Union[Unset, list["ImageObject"]] = UNSET
    product: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        country = self.country

        display_name = self.display_name

        email = self.email

        explicit_content: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.explicit_content, Unset):
            explicit_content = self.explicit_content.to_dict()

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

        product = self.product

        type_ = self.type_

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if country is not UNSET:
            field_dict["country"] = country
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if email is not UNSET:
            field_dict["email"] = email
        if explicit_content is not UNSET:
            field_dict["explicit_content"] = explicit_content
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
        if product is not UNSET:
            field_dict["product"] = product
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.explicit_content_settings_object import ExplicitContentSettingsObject
        from ..models.external_url_object import ExternalUrlObject
        from ..models.followers_object import FollowersObject
        from ..models.image_object import ImageObject

        d = dict(src_dict)
        country = d.pop("country", UNSET)

        display_name = d.pop("display_name", UNSET)

        email = d.pop("email", UNSET)

        _explicit_content = d.pop("explicit_content", UNSET)
        explicit_content: Union[Unset, ExplicitContentSettingsObject]
        if isinstance(_explicit_content, Unset):
            explicit_content = UNSET
        else:
            explicit_content = ExplicitContentSettingsObject.from_dict(_explicit_content)

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

        product = d.pop("product", UNSET)

        type_ = d.pop("type", UNSET)

        uri = d.pop("uri", UNSET)

        private_user_object = cls(
            country=country,
            display_name=display_name,
            email=email,
            explicit_content=explicit_content,
            external_urls=external_urls,
            followers=followers,
            href=href,
            id=id,
            images=images,
            product=product,
            type_=type_,
            uri=uri,
        )

        private_user_object.additional_properties = d
        return private_user_object

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
