from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_url_object import ExternalUrlObject
    from ..models.image_object import ImageObject
    from ..models.playlist_owner_object import PlaylistOwnerObject
    from ..models.playlist_tracks_ref_object import PlaylistTracksRefObject


T = TypeVar("T", bound="SimplifiedPlaylistObject")


@_attrs_define
class SimplifiedPlaylistObject:
    """
    Attributes:
        collaborative (Union[Unset, bool]): `true` if the owner allows other users to modify the playlist.
        description (Union[Unset, str]): The playlist description. _Only returned for modified, verified playlists,
            otherwise_ `null`.
        external_urls (Union[Unset, ExternalUrlObject]):
        href (Union[Unset, str]): A link to the Web API endpoint providing full details of the playlist.
        id (Union[Unset, str]): The [Spotify ID](/documentation/web-api/concepts/spotify-uris-ids) for the playlist.
        images (Union[Unset, list['ImageObject']]): Images for the playlist. The array may be empty or contain up to
            three images. The images are returned by size in descending order. See [Working with
            Playlists](/documentation/web-api/concepts/playlists). _**Note**: If returned, the source URL for the image
            (`url`) is temporary and will expire in less than a day._
        name (Union[Unset, str]): The name of the playlist.
        owner (Union[Unset, PlaylistOwnerObject]):
        public (Union[Unset, bool]): The playlist's public/private status (if it is added to the user's profile): `true`
            the playlist is public, `false` the playlist is private, `null` the playlist status is not relevant. For more
            about public/private status, see [Working with Playlists](/documentation/web-api/concepts/playlists)
        snapshot_id (Union[Unset, str]): The version identifier for the current playlist. Can be supplied in other
            requests to target a specific playlist version
        tracks (Union[Unset, PlaylistTracksRefObject]):
        type_ (Union[Unset, str]): The object type: "playlist"
        uri (Union[Unset, str]): The [Spotify URI](/documentation/web-api/concepts/spotify-uris-ids) for the playlist.
    """

    collaborative: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    external_urls: Union[Unset, "ExternalUrlObject"] = UNSET
    href: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    images: Union[Unset, list["ImageObject"]] = UNSET
    name: Union[Unset, str] = UNSET
    owner: Union[Unset, "PlaylistOwnerObject"] = UNSET
    public: Union[Unset, bool] = UNSET
    snapshot_id: Union[Unset, str] = UNSET
    tracks: Union[Unset, "PlaylistTracksRefObject"] = UNSET
    type_: Union[Unset, str] = UNSET
    uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collaborative = self.collaborative

        description = self.description

        external_urls: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.external_urls, Unset):
            external_urls = self.external_urls.to_dict()

        href = self.href

        id = self.id

        images: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item = images_item_data.to_dict()
                images.append(images_item)

        name = self.name

        owner: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.owner, Unset):
            owner = self.owner.to_dict()

        public = self.public

        snapshot_id = self.snapshot_id

        tracks: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tracks, Unset):
            tracks = self.tracks.to_dict()

        type_ = self.type_

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if collaborative is not UNSET:
            field_dict["collaborative"] = collaborative
        if description is not UNSET:
            field_dict["description"] = description
        if external_urls is not UNSET:
            field_dict["external_urls"] = external_urls
        if href is not UNSET:
            field_dict["href"] = href
        if id is not UNSET:
            field_dict["id"] = id
        if images is not UNSET:
            field_dict["images"] = images
        if name is not UNSET:
            field_dict["name"] = name
        if owner is not UNSET:
            field_dict["owner"] = owner
        if public is not UNSET:
            field_dict["public"] = public
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id
        if tracks is not UNSET:
            field_dict["tracks"] = tracks
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_url_object import ExternalUrlObject
        from ..models.image_object import ImageObject
        from ..models.playlist_owner_object import PlaylistOwnerObject
        from ..models.playlist_tracks_ref_object import PlaylistTracksRefObject

        d = dict(src_dict)
        collaborative = d.pop("collaborative", UNSET)

        description = d.pop("description", UNSET)

        _external_urls = d.pop("external_urls", UNSET)
        external_urls: Union[Unset, ExternalUrlObject]
        if isinstance(_external_urls, Unset):
            external_urls = UNSET
        else:
            external_urls = ExternalUrlObject.from_dict(_external_urls)

        href = d.pop("href", UNSET)

        id = d.pop("id", UNSET)

        images = []
        _images = d.pop("images", UNSET)
        for images_item_data in _images or []:
            images_item = ImageObject.from_dict(images_item_data)

            images.append(images_item)

        name = d.pop("name", UNSET)

        _owner = d.pop("owner", UNSET)
        owner: Union[Unset, PlaylistOwnerObject]
        if isinstance(_owner, Unset):
            owner = UNSET
        else:
            owner = PlaylistOwnerObject.from_dict(_owner)

        public = d.pop("public", UNSET)

        snapshot_id = d.pop("snapshot_id", UNSET)

        _tracks = d.pop("tracks", UNSET)
        tracks: Union[Unset, PlaylistTracksRefObject]
        if isinstance(_tracks, Unset):
            tracks = UNSET
        else:
            tracks = PlaylistTracksRefObject.from_dict(_tracks)

        type_ = d.pop("type", UNSET)

        uri = d.pop("uri", UNSET)

        simplified_playlist_object = cls(
            collaborative=collaborative,
            description=description,
            external_urls=external_urls,
            href=href,
            id=id,
            images=images,
            name=name,
            owner=owner,
            public=public,
            snapshot_id=snapshot_id,
            tracks=tracks,
            type_=type_,
            uri=uri,
        )

        simplified_playlist_object.additional_properties = d
        return simplified_playlist_object

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
