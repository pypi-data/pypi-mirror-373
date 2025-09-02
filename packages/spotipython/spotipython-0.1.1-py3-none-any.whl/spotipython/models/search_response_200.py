from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.paging_artist_object import PagingArtistObject
    from ..models.paging_playlist_object import PagingPlaylistObject
    from ..models.paging_simplified_album_object import PagingSimplifiedAlbumObject
    from ..models.paging_simplified_audiobook_object import PagingSimplifiedAudiobookObject
    from ..models.paging_simplified_episode_object import PagingSimplifiedEpisodeObject
    from ..models.paging_simplified_show_object import PagingSimplifiedShowObject
    from ..models.paging_track_object import PagingTrackObject


T = TypeVar("T", bound="SearchResponse200")


@_attrs_define
class SearchResponse200:
    """
    Attributes:
        tracks (Union[Unset, PagingTrackObject]):
        artists (Union[Unset, PagingArtistObject]):
        albums (Union[Unset, PagingSimplifiedAlbumObject]):
        playlists (Union[Unset, PagingPlaylistObject]):
        shows (Union[Unset, PagingSimplifiedShowObject]):
        episodes (Union[Unset, PagingSimplifiedEpisodeObject]):
        audiobooks (Union[Unset, PagingSimplifiedAudiobookObject]):
    """

    tracks: Union[Unset, "PagingTrackObject"] = UNSET
    artists: Union[Unset, "PagingArtistObject"] = UNSET
    albums: Union[Unset, "PagingSimplifiedAlbumObject"] = UNSET
    playlists: Union[Unset, "PagingPlaylistObject"] = UNSET
    shows: Union[Unset, "PagingSimplifiedShowObject"] = UNSET
    episodes: Union[Unset, "PagingSimplifiedEpisodeObject"] = UNSET
    audiobooks: Union[Unset, "PagingSimplifiedAudiobookObject"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tracks: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tracks, Unset):
            tracks = self.tracks.to_dict()

        artists: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.artists, Unset):
            artists = self.artists.to_dict()

        albums: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.albums, Unset):
            albums = self.albums.to_dict()

        playlists: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.playlists, Unset):
            playlists = self.playlists.to_dict()

        shows: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.shows, Unset):
            shows = self.shows.to_dict()

        episodes: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.episodes, Unset):
            episodes = self.episodes.to_dict()

        audiobooks: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.audiobooks, Unset):
            audiobooks = self.audiobooks.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tracks is not UNSET:
            field_dict["tracks"] = tracks
        if artists is not UNSET:
            field_dict["artists"] = artists
        if albums is not UNSET:
            field_dict["albums"] = albums
        if playlists is not UNSET:
            field_dict["playlists"] = playlists
        if shows is not UNSET:
            field_dict["shows"] = shows
        if episodes is not UNSET:
            field_dict["episodes"] = episodes
        if audiobooks is not UNSET:
            field_dict["audiobooks"] = audiobooks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.paging_artist_object import PagingArtistObject
        from ..models.paging_playlist_object import PagingPlaylistObject
        from ..models.paging_simplified_album_object import PagingSimplifiedAlbumObject
        from ..models.paging_simplified_audiobook_object import PagingSimplifiedAudiobookObject
        from ..models.paging_simplified_episode_object import PagingSimplifiedEpisodeObject
        from ..models.paging_simplified_show_object import PagingSimplifiedShowObject
        from ..models.paging_track_object import PagingTrackObject

        d = dict(src_dict)
        _tracks = d.pop("tracks", UNSET)
        tracks: Union[Unset, PagingTrackObject]
        if isinstance(_tracks, Unset):
            tracks = UNSET
        else:
            tracks = PagingTrackObject.from_dict(_tracks)

        _artists = d.pop("artists", UNSET)
        artists: Union[Unset, PagingArtistObject]
        if isinstance(_artists, Unset):
            artists = UNSET
        else:
            artists = PagingArtistObject.from_dict(_artists)

        _albums = d.pop("albums", UNSET)
        albums: Union[Unset, PagingSimplifiedAlbumObject]
        if isinstance(_albums, Unset):
            albums = UNSET
        else:
            albums = PagingSimplifiedAlbumObject.from_dict(_albums)

        _playlists = d.pop("playlists", UNSET)
        playlists: Union[Unset, PagingPlaylistObject]
        if isinstance(_playlists, Unset):
            playlists = UNSET
        else:
            playlists = PagingPlaylistObject.from_dict(_playlists)

        _shows = d.pop("shows", UNSET)
        shows: Union[Unset, PagingSimplifiedShowObject]
        if isinstance(_shows, Unset):
            shows = UNSET
        else:
            shows = PagingSimplifiedShowObject.from_dict(_shows)

        _episodes = d.pop("episodes", UNSET)
        episodes: Union[Unset, PagingSimplifiedEpisodeObject]
        if isinstance(_episodes, Unset):
            episodes = UNSET
        else:
            episodes = PagingSimplifiedEpisodeObject.from_dict(_episodes)

        _audiobooks = d.pop("audiobooks", UNSET)
        audiobooks: Union[Unset, PagingSimplifiedAudiobookObject]
        if isinstance(_audiobooks, Unset):
            audiobooks = UNSET
        else:
            audiobooks = PagingSimplifiedAudiobookObject.from_dict(_audiobooks)

        search_response_200 = cls(
            tracks=tracks,
            artists=artists,
            albums=albums,
            playlists=playlists,
            shows=shows,
            episodes=episodes,
            audiobooks=audiobooks,
        )

        search_response_200.additional_properties = d
        return search_response_200

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
