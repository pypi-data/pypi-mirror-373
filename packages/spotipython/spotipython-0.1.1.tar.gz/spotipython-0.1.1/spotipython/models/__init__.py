"""Contains all the data models used in inputs/outputs"""

from .add_to_queue_response_401 import AddToQueueResponse401
from .add_to_queue_response_403 import AddToQueueResponse403
from .add_to_queue_response_429 import AddToQueueResponse429
from .add_tracks_to_playlist_body import AddTracksToPlaylistBody
from .add_tracks_to_playlist_response_201 import AddTracksToPlaylistResponse201
from .add_tracks_to_playlist_response_401 import AddTracksToPlaylistResponse401
from .add_tracks_to_playlist_response_403 import AddTracksToPlaylistResponse403
from .add_tracks_to_playlist_response_429 import AddTracksToPlaylistResponse429
from .album_base import AlbumBase
from .album_base_album_type import AlbumBaseAlbumType
from .album_base_release_date_precision import AlbumBaseReleaseDatePrecision
from .album_base_type import AlbumBaseType
from .album_object import AlbumObject
from .album_restriction_object import AlbumRestrictionObject
from .album_restriction_object_reason import AlbumRestrictionObjectReason
from .artist_discography_album_object import ArtistDiscographyAlbumObject
from .artist_discography_album_object_album_group import ArtistDiscographyAlbumObjectAlbumGroup
from .artist_object import ArtistObject
from .artist_object_type import ArtistObjectType
from .audio_analysis_object import AudioAnalysisObject
from .audio_analysis_object_meta import AudioAnalysisObjectMeta
from .audio_analysis_object_track import AudioAnalysisObjectTrack
from .audio_features_object import AudioFeaturesObject
from .audio_features_object_type import AudioFeaturesObjectType
from .audiobook_base import AudiobookBase
from .audiobook_base_type import AudiobookBaseType
from .audiobook_object import AudiobookObject
from .author_object import AuthorObject
from .category_object import CategoryObject
from .change_playlist_details_body import ChangePlaylistDetailsBody
from .change_playlist_details_response_401 import ChangePlaylistDetailsResponse401
from .change_playlist_details_response_403 import ChangePlaylistDetailsResponse403
from .change_playlist_details_response_429 import ChangePlaylistDetailsResponse429
from .chapter_base import ChapterBase
from .chapter_base_release_date_precision import ChapterBaseReleaseDatePrecision
from .chapter_base_type import ChapterBaseType
from .chapter_object import ChapterObject
from .chapter_restriction_object import ChapterRestrictionObject
from .check_current_user_follows_item_type import CheckCurrentUserFollowsItemType
from .check_current_user_follows_response_401 import CheckCurrentUserFollowsResponse401
from .check_current_user_follows_response_403 import CheckCurrentUserFollowsResponse403
from .check_current_user_follows_response_429 import CheckCurrentUserFollowsResponse429
from .check_if_user_follows_playlist_response_401 import CheckIfUserFollowsPlaylistResponse401
from .check_if_user_follows_playlist_response_403 import CheckIfUserFollowsPlaylistResponse403
from .check_if_user_follows_playlist_response_429 import CheckIfUserFollowsPlaylistResponse429
from .check_users_saved_albums_response_401 import CheckUsersSavedAlbumsResponse401
from .check_users_saved_albums_response_403 import CheckUsersSavedAlbumsResponse403
from .check_users_saved_albums_response_429 import CheckUsersSavedAlbumsResponse429
from .check_users_saved_audiobooks_response_401 import CheckUsersSavedAudiobooksResponse401
from .check_users_saved_audiobooks_response_403 import CheckUsersSavedAudiobooksResponse403
from .check_users_saved_audiobooks_response_429 import CheckUsersSavedAudiobooksResponse429
from .check_users_saved_episodes_response_401 import CheckUsersSavedEpisodesResponse401
from .check_users_saved_episodes_response_403 import CheckUsersSavedEpisodesResponse403
from .check_users_saved_episodes_response_429 import CheckUsersSavedEpisodesResponse429
from .check_users_saved_shows_response_401 import CheckUsersSavedShowsResponse401
from .check_users_saved_shows_response_403 import CheckUsersSavedShowsResponse403
from .check_users_saved_shows_response_429 import CheckUsersSavedShowsResponse429
from .check_users_saved_tracks_response_401 import CheckUsersSavedTracksResponse401
from .check_users_saved_tracks_response_403 import CheckUsersSavedTracksResponse403
from .check_users_saved_tracks_response_429 import CheckUsersSavedTracksResponse429
from .context_object import ContextObject
from .copyright_object import CopyrightObject
from .create_playlist_body import CreatePlaylistBody
from .create_playlist_response_401 import CreatePlaylistResponse401
from .create_playlist_response_403 import CreatePlaylistResponse403
from .create_playlist_response_429 import CreatePlaylistResponse429
from .currently_playing_context_object import CurrentlyPlayingContextObject
from .cursor_object import CursorObject
from .cursor_paging_object import CursorPagingObject
from .cursor_paging_play_history_object import CursorPagingPlayHistoryObject
from .cursor_paging_simplified_artist_object import CursorPagingSimplifiedArtistObject
from .device_object import DeviceObject
from .disallows_object import DisallowsObject
from .episode_base import EpisodeBase
from .episode_base_release_date_precision import EpisodeBaseReleaseDatePrecision
from .episode_base_type import EpisodeBaseType
from .episode_object import EpisodeObject
from .episode_restriction_object import EpisodeRestrictionObject
from .error_object import ErrorObject
from .explicit_content_settings_object import ExplicitContentSettingsObject
from .external_id_object import ExternalIdObject
from .external_url_object import ExternalUrlObject
from .follow_artists_users_body import FollowArtistsUsersBody
from .follow_artists_users_item_type import FollowArtistsUsersItemType
from .follow_artists_users_response_401 import FollowArtistsUsersResponse401
from .follow_artists_users_response_403 import FollowArtistsUsersResponse403
from .follow_artists_users_response_429 import FollowArtistsUsersResponse429
from .follow_playlist_body import FollowPlaylistBody
from .follow_playlist_response_401 import FollowPlaylistResponse401
from .follow_playlist_response_403 import FollowPlaylistResponse403
from .follow_playlist_response_429 import FollowPlaylistResponse429
from .followers_object import FollowersObject
from .get_a_categories_playlists_response_401 import GetACategoriesPlaylistsResponse401
from .get_a_categories_playlists_response_403 import GetACategoriesPlaylistsResponse403
from .get_a_categories_playlists_response_429 import GetACategoriesPlaylistsResponse429
from .get_a_category_response_401 import GetACategoryResponse401
from .get_a_category_response_403 import GetACategoryResponse403
from .get_a_category_response_429 import GetACategoryResponse429
from .get_a_chapter_response_401 import GetAChapterResponse401
from .get_a_chapter_response_403 import GetAChapterResponse403
from .get_a_chapter_response_429 import GetAChapterResponse429
from .get_a_list_of_current_users_playlists_response_401 import GetAListOfCurrentUsersPlaylistsResponse401
from .get_a_list_of_current_users_playlists_response_403 import GetAListOfCurrentUsersPlaylistsResponse403
from .get_a_list_of_current_users_playlists_response_429 import GetAListOfCurrentUsersPlaylistsResponse429
from .get_a_show_response_401 import GetAShowResponse401
from .get_a_show_response_403 import GetAShowResponse403
from .get_a_show_response_429 import GetAShowResponse429
from .get_a_shows_episodes_response_401 import GetAShowsEpisodesResponse401
from .get_a_shows_episodes_response_403 import GetAShowsEpisodesResponse403
from .get_a_shows_episodes_response_429 import GetAShowsEpisodesResponse429
from .get_a_users_available_devices_response_200 import GetAUsersAvailableDevicesResponse200
from .get_a_users_available_devices_response_401 import GetAUsersAvailableDevicesResponse401
from .get_a_users_available_devices_response_403 import GetAUsersAvailableDevicesResponse403
from .get_a_users_available_devices_response_429 import GetAUsersAvailableDevicesResponse429
from .get_an_album_response_401 import GetAnAlbumResponse401
from .get_an_album_response_403 import GetAnAlbumResponse403
from .get_an_album_response_429 import GetAnAlbumResponse429
from .get_an_albums_tracks_response_401 import GetAnAlbumsTracksResponse401
from .get_an_albums_tracks_response_403 import GetAnAlbumsTracksResponse403
from .get_an_albums_tracks_response_429 import GetAnAlbumsTracksResponse429
from .get_an_artist_response_401 import GetAnArtistResponse401
from .get_an_artist_response_403 import GetAnArtistResponse403
from .get_an_artist_response_429 import GetAnArtistResponse429
from .get_an_artists_albums_response_401 import GetAnArtistsAlbumsResponse401
from .get_an_artists_albums_response_403 import GetAnArtistsAlbumsResponse403
from .get_an_artists_albums_response_429 import GetAnArtistsAlbumsResponse429
from .get_an_artists_related_artists_response_200 import GetAnArtistsRelatedArtistsResponse200
from .get_an_artists_related_artists_response_401 import GetAnArtistsRelatedArtistsResponse401
from .get_an_artists_related_artists_response_403 import GetAnArtistsRelatedArtistsResponse403
from .get_an_artists_related_artists_response_429 import GetAnArtistsRelatedArtistsResponse429
from .get_an_artists_top_tracks_response_200 import GetAnArtistsTopTracksResponse200
from .get_an_artists_top_tracks_response_401 import GetAnArtistsTopTracksResponse401
from .get_an_artists_top_tracks_response_403 import GetAnArtistsTopTracksResponse403
from .get_an_artists_top_tracks_response_429 import GetAnArtistsTopTracksResponse429
from .get_an_audiobook_response_400 import GetAnAudiobookResponse400
from .get_an_audiobook_response_401 import GetAnAudiobookResponse401
from .get_an_audiobook_response_403 import GetAnAudiobookResponse403
from .get_an_audiobook_response_404 import GetAnAudiobookResponse404
from .get_an_audiobook_response_429 import GetAnAudiobookResponse429
from .get_an_episode_response_401 import GetAnEpisodeResponse401
from .get_an_episode_response_403 import GetAnEpisodeResponse403
from .get_an_episode_response_429 import GetAnEpisodeResponse429
from .get_audio_analysis_response_401 import GetAudioAnalysisResponse401
from .get_audio_analysis_response_403 import GetAudioAnalysisResponse403
from .get_audio_analysis_response_429 import GetAudioAnalysisResponse429
from .get_audio_features_response_401 import GetAudioFeaturesResponse401
from .get_audio_features_response_403 import GetAudioFeaturesResponse403
from .get_audio_features_response_429 import GetAudioFeaturesResponse429
from .get_audiobook_chapters_response_401 import GetAudiobookChaptersResponse401
from .get_audiobook_chapters_response_403 import GetAudiobookChaptersResponse403
from .get_audiobook_chapters_response_429 import GetAudiobookChaptersResponse429
from .get_available_markets_response_200 import GetAvailableMarketsResponse200
from .get_available_markets_response_401 import GetAvailableMarketsResponse401
from .get_available_markets_response_403 import GetAvailableMarketsResponse403
from .get_available_markets_response_429 import GetAvailableMarketsResponse429
from .get_categories_response_200 import GetCategoriesResponse200
from .get_categories_response_200_categories import GetCategoriesResponse200Categories
from .get_categories_response_401 import GetCategoriesResponse401
from .get_categories_response_403 import GetCategoriesResponse403
from .get_categories_response_429 import GetCategoriesResponse429
from .get_current_users_profile_response_401 import GetCurrentUsersProfileResponse401
from .get_current_users_profile_response_403 import GetCurrentUsersProfileResponse403
from .get_current_users_profile_response_429 import GetCurrentUsersProfileResponse429
from .get_featured_playlists_response_401 import GetFeaturedPlaylistsResponse401
from .get_featured_playlists_response_403 import GetFeaturedPlaylistsResponse403
from .get_featured_playlists_response_429 import GetFeaturedPlaylistsResponse429
from .get_followed_item_type import GetFollowedItemType
from .get_followed_response_200 import GetFollowedResponse200
from .get_followed_response_401 import GetFollowedResponse401
from .get_followed_response_403 import GetFollowedResponse403
from .get_followed_response_429 import GetFollowedResponse429
from .get_information_about_the_users_current_playback_response_401 import (
    GetInformationAboutTheUsersCurrentPlaybackResponse401,
)
from .get_information_about_the_users_current_playback_response_403 import (
    GetInformationAboutTheUsersCurrentPlaybackResponse403,
)
from .get_information_about_the_users_current_playback_response_429 import (
    GetInformationAboutTheUsersCurrentPlaybackResponse429,
)
from .get_list_users_playlists_response_401 import GetListUsersPlaylistsResponse401
from .get_list_users_playlists_response_403 import GetListUsersPlaylistsResponse403
from .get_list_users_playlists_response_429 import GetListUsersPlaylistsResponse429
from .get_multiple_albums_response_200 import GetMultipleAlbumsResponse200
from .get_multiple_albums_response_401 import GetMultipleAlbumsResponse401
from .get_multiple_albums_response_403 import GetMultipleAlbumsResponse403
from .get_multiple_albums_response_429 import GetMultipleAlbumsResponse429
from .get_multiple_artists_response_200 import GetMultipleArtistsResponse200
from .get_multiple_artists_response_401 import GetMultipleArtistsResponse401
from .get_multiple_artists_response_403 import GetMultipleArtistsResponse403
from .get_multiple_artists_response_429 import GetMultipleArtistsResponse429
from .get_multiple_audiobooks_response_200 import GetMultipleAudiobooksResponse200
from .get_multiple_audiobooks_response_401 import GetMultipleAudiobooksResponse401
from .get_multiple_audiobooks_response_403 import GetMultipleAudiobooksResponse403
from .get_multiple_audiobooks_response_429 import GetMultipleAudiobooksResponse429
from .get_multiple_episodes_response_200 import GetMultipleEpisodesResponse200
from .get_multiple_episodes_response_401 import GetMultipleEpisodesResponse401
from .get_multiple_episodes_response_403 import GetMultipleEpisodesResponse403
from .get_multiple_episodes_response_429 import GetMultipleEpisodesResponse429
from .get_multiple_shows_response_200 import GetMultipleShowsResponse200
from .get_multiple_shows_response_401 import GetMultipleShowsResponse401
from .get_multiple_shows_response_403 import GetMultipleShowsResponse403
from .get_multiple_shows_response_429 import GetMultipleShowsResponse429
from .get_new_releases_response_200 import GetNewReleasesResponse200
from .get_new_releases_response_401 import GetNewReleasesResponse401
from .get_new_releases_response_403 import GetNewReleasesResponse403
from .get_new_releases_response_429 import GetNewReleasesResponse429
from .get_playlist_cover_response_401 import GetPlaylistCoverResponse401
from .get_playlist_cover_response_403 import GetPlaylistCoverResponse403
from .get_playlist_cover_response_429 import GetPlaylistCoverResponse429
from .get_playlist_response_401 import GetPlaylistResponse401
from .get_playlist_response_403 import GetPlaylistResponse403
from .get_playlist_response_429 import GetPlaylistResponse429
from .get_playlists_tracks_response_401 import GetPlaylistsTracksResponse401
from .get_playlists_tracks_response_403 import GetPlaylistsTracksResponse403
from .get_playlists_tracks_response_429 import GetPlaylistsTracksResponse429
from .get_queue_response_401 import GetQueueResponse401
from .get_queue_response_403 import GetQueueResponse403
from .get_queue_response_429 import GetQueueResponse429
from .get_recently_played_response_401 import GetRecentlyPlayedResponse401
from .get_recently_played_response_403 import GetRecentlyPlayedResponse403
from .get_recently_played_response_429 import GetRecentlyPlayedResponse429
from .get_recommendation_genres_response_200 import GetRecommendationGenresResponse200
from .get_recommendation_genres_response_401 import GetRecommendationGenresResponse401
from .get_recommendation_genres_response_403 import GetRecommendationGenresResponse403
from .get_recommendation_genres_response_429 import GetRecommendationGenresResponse429
from .get_recommendations_response_401 import GetRecommendationsResponse401
from .get_recommendations_response_403 import GetRecommendationsResponse403
from .get_recommendations_response_429 import GetRecommendationsResponse429
from .get_several_audio_features_response_200 import GetSeveralAudioFeaturesResponse200
from .get_several_audio_features_response_401 import GetSeveralAudioFeaturesResponse401
from .get_several_audio_features_response_403 import GetSeveralAudioFeaturesResponse403
from .get_several_audio_features_response_429 import GetSeveralAudioFeaturesResponse429
from .get_several_chapters_response_200 import GetSeveralChaptersResponse200
from .get_several_chapters_response_401 import GetSeveralChaptersResponse401
from .get_several_chapters_response_403 import GetSeveralChaptersResponse403
from .get_several_chapters_response_429 import GetSeveralChaptersResponse429
from .get_several_tracks_response_200 import GetSeveralTracksResponse200
from .get_several_tracks_response_401 import GetSeveralTracksResponse401
from .get_several_tracks_response_403 import GetSeveralTracksResponse403
from .get_several_tracks_response_429 import GetSeveralTracksResponse429
from .get_the_users_currently_playing_track_response_401 import GetTheUsersCurrentlyPlayingTrackResponse401
from .get_the_users_currently_playing_track_response_403 import GetTheUsersCurrentlyPlayingTrackResponse403
from .get_the_users_currently_playing_track_response_429 import GetTheUsersCurrentlyPlayingTrackResponse429
from .get_track_response_401 import GetTrackResponse401
from .get_track_response_403 import GetTrackResponse403
from .get_track_response_429 import GetTrackResponse429
from .get_users_profile_response_401 import GetUsersProfileResponse401
from .get_users_profile_response_403 import GetUsersProfileResponse403
from .get_users_profile_response_429 import GetUsersProfileResponse429
from .get_users_saved_albums_response_401 import GetUsersSavedAlbumsResponse401
from .get_users_saved_albums_response_403 import GetUsersSavedAlbumsResponse403
from .get_users_saved_albums_response_429 import GetUsersSavedAlbumsResponse429
from .get_users_saved_audiobooks_response_401 import GetUsersSavedAudiobooksResponse401
from .get_users_saved_audiobooks_response_403 import GetUsersSavedAudiobooksResponse403
from .get_users_saved_audiobooks_response_429 import GetUsersSavedAudiobooksResponse429
from .get_users_saved_episodes_response_401 import GetUsersSavedEpisodesResponse401
from .get_users_saved_episodes_response_403 import GetUsersSavedEpisodesResponse403
from .get_users_saved_episodes_response_429 import GetUsersSavedEpisodesResponse429
from .get_users_saved_shows_response_401 import GetUsersSavedShowsResponse401
from .get_users_saved_shows_response_403 import GetUsersSavedShowsResponse403
from .get_users_saved_shows_response_429 import GetUsersSavedShowsResponse429
from .get_users_saved_tracks_response_401 import GetUsersSavedTracksResponse401
from .get_users_saved_tracks_response_403 import GetUsersSavedTracksResponse403
from .get_users_saved_tracks_response_429 import GetUsersSavedTracksResponse429
from .get_users_top_artists_and_tracks_response_200 import GetUsersTopArtistsAndTracksResponse200
from .get_users_top_artists_and_tracks_response_401 import GetUsersTopArtistsAndTracksResponse401
from .get_users_top_artists_and_tracks_response_403 import GetUsersTopArtistsAndTracksResponse403
from .get_users_top_artists_and_tracks_response_429 import GetUsersTopArtistsAndTracksResponse429
from .get_users_top_artists_and_tracks_type import GetUsersTopArtistsAndTracksType
from .image_object import ImageObject
from .linked_track_object import LinkedTrackObject
from .narrator_object import NarratorObject
from .paging_artist_discography_album_object import PagingArtistDiscographyAlbumObject
from .paging_artist_object import PagingArtistObject
from .paging_featured_playlist_object import PagingFeaturedPlaylistObject
from .paging_object import PagingObject
from .paging_playlist_object import PagingPlaylistObject
from .paging_playlist_track_object import PagingPlaylistTrackObject
from .paging_saved_album_object import PagingSavedAlbumObject
from .paging_saved_episode_object import PagingSavedEpisodeObject
from .paging_saved_show_object import PagingSavedShowObject
from .paging_saved_track_object import PagingSavedTrackObject
from .paging_simplified_album_object import PagingSimplifiedAlbumObject
from .paging_simplified_audiobook_object import PagingSimplifiedAudiobookObject
from .paging_simplified_chapter_object import PagingSimplifiedChapterObject
from .paging_simplified_episode_object import PagingSimplifiedEpisodeObject
from .paging_simplified_show_object import PagingSimplifiedShowObject
from .paging_simplified_track_object import PagingSimplifiedTrackObject
from .paging_track_object import PagingTrackObject
from .pause_a_users_playback_response_401 import PauseAUsersPlaybackResponse401
from .pause_a_users_playback_response_403 import PauseAUsersPlaybackResponse403
from .pause_a_users_playback_response_429 import PauseAUsersPlaybackResponse429
from .play_history_object import PlayHistoryObject
from .playlist_object import PlaylistObject
from .playlist_owner_object import PlaylistOwnerObject
from .playlist_track_object import PlaylistTrackObject
from .playlist_tracks_ref_object import PlaylistTracksRefObject
from .playlist_user_object import PlaylistUserObject
from .playlist_user_object_type import PlaylistUserObjectType
from .private_user_object import PrivateUserObject
from .public_user_object import PublicUserObject
from .public_user_object_type import PublicUserObjectType
from .queue_object import QueueObject
from .recommendation_seed_object import RecommendationSeedObject
from .recommendations_object import RecommendationsObject
from .remove_albums_user_body import RemoveAlbumsUserBody
from .remove_albums_user_response_401 import RemoveAlbumsUserResponse401
from .remove_albums_user_response_403 import RemoveAlbumsUserResponse403
from .remove_albums_user_response_429 import RemoveAlbumsUserResponse429
from .remove_audiobooks_user_response_401 import RemoveAudiobooksUserResponse401
from .remove_audiobooks_user_response_403 import RemoveAudiobooksUserResponse403
from .remove_audiobooks_user_response_429 import RemoveAudiobooksUserResponse429
from .remove_episodes_user_body import RemoveEpisodesUserBody
from .remove_episodes_user_response_401 import RemoveEpisodesUserResponse401
from .remove_episodes_user_response_403 import RemoveEpisodesUserResponse403
from .remove_episodes_user_response_429 import RemoveEpisodesUserResponse429
from .remove_shows_user_response_401 import RemoveShowsUserResponse401
from .remove_shows_user_response_403 import RemoveShowsUserResponse403
from .remove_shows_user_response_429 import RemoveShowsUserResponse429
from .remove_tracks_playlist_body import RemoveTracksPlaylistBody
from .remove_tracks_playlist_body_tracks_item import RemoveTracksPlaylistBodyTracksItem
from .remove_tracks_playlist_response_200 import RemoveTracksPlaylistResponse200
from .remove_tracks_playlist_response_401 import RemoveTracksPlaylistResponse401
from .remove_tracks_playlist_response_403 import RemoveTracksPlaylistResponse403
from .remove_tracks_playlist_response_429 import RemoveTracksPlaylistResponse429
from .remove_tracks_user_body import RemoveTracksUserBody
from .remove_tracks_user_response_401 import RemoveTracksUserResponse401
from .remove_tracks_user_response_403 import RemoveTracksUserResponse403
from .remove_tracks_user_response_429 import RemoveTracksUserResponse429
from .reorder_or_replace_playlists_tracks_body import ReorderOrReplacePlaylistsTracksBody
from .reorder_or_replace_playlists_tracks_response_200 import ReorderOrReplacePlaylistsTracksResponse200
from .reorder_or_replace_playlists_tracks_response_401 import ReorderOrReplacePlaylistsTracksResponse401
from .reorder_or_replace_playlists_tracks_response_403 import ReorderOrReplacePlaylistsTracksResponse403
from .reorder_or_replace_playlists_tracks_response_429 import ReorderOrReplacePlaylistsTracksResponse429
from .resume_point_object import ResumePointObject
from .save_albums_user_body import SaveAlbumsUserBody
from .save_albums_user_response_401 import SaveAlbumsUserResponse401
from .save_albums_user_response_403 import SaveAlbumsUserResponse403
from .save_albums_user_response_429 import SaveAlbumsUserResponse429
from .save_audiobooks_user_response_401 import SaveAudiobooksUserResponse401
from .save_audiobooks_user_response_403 import SaveAudiobooksUserResponse403
from .save_audiobooks_user_response_429 import SaveAudiobooksUserResponse429
from .save_episodes_user_body import SaveEpisodesUserBody
from .save_episodes_user_response_401 import SaveEpisodesUserResponse401
from .save_episodes_user_response_403 import SaveEpisodesUserResponse403
from .save_episodes_user_response_429 import SaveEpisodesUserResponse429
from .save_shows_user_response_401 import SaveShowsUserResponse401
from .save_shows_user_response_403 import SaveShowsUserResponse403
from .save_shows_user_response_429 import SaveShowsUserResponse429
from .save_tracks_user_body import SaveTracksUserBody
from .save_tracks_user_body_timestamped_ids_item import SaveTracksUserBodyTimestampedIdsItem
from .save_tracks_user_response_401 import SaveTracksUserResponse401
from .save_tracks_user_response_403 import SaveTracksUserResponse403
from .save_tracks_user_response_429 import SaveTracksUserResponse429
from .saved_album_object import SavedAlbumObject
from .saved_episode_object import SavedEpisodeObject
from .saved_show_object import SavedShowObject
from .saved_track_object import SavedTrackObject
from .search_include_external import SearchIncludeExternal
from .search_response_200 import SearchResponse200
from .search_response_401 import SearchResponse401
from .search_response_403 import SearchResponse403
from .search_response_429 import SearchResponse429
from .search_type_item import SearchTypeItem
from .section_object import SectionObject
from .section_object_mode import SectionObjectMode
from .seek_to_position_in_currently_playing_track_response_401 import SeekToPositionInCurrentlyPlayingTrackResponse401
from .seek_to_position_in_currently_playing_track_response_403 import SeekToPositionInCurrentlyPlayingTrackResponse403
from .seek_to_position_in_currently_playing_track_response_429 import SeekToPositionInCurrentlyPlayingTrackResponse429
from .segment_object import SegmentObject
from .set_repeat_mode_on_users_playback_response_401 import SetRepeatModeOnUsersPlaybackResponse401
from .set_repeat_mode_on_users_playback_response_403 import SetRepeatModeOnUsersPlaybackResponse403
from .set_repeat_mode_on_users_playback_response_429 import SetRepeatModeOnUsersPlaybackResponse429
from .set_volume_for_users_playback_response_401 import SetVolumeForUsersPlaybackResponse401
from .set_volume_for_users_playback_response_403 import SetVolumeForUsersPlaybackResponse403
from .set_volume_for_users_playback_response_429 import SetVolumeForUsersPlaybackResponse429
from .show_base import ShowBase
from .show_base_type import ShowBaseType
from .show_object import ShowObject
from .simplified_album_object import SimplifiedAlbumObject
from .simplified_artist_object import SimplifiedArtistObject
from .simplified_artist_object_type import SimplifiedArtistObjectType
from .simplified_audiobook_object import SimplifiedAudiobookObject
from .simplified_chapter_object import SimplifiedChapterObject
from .simplified_episode_object import SimplifiedEpisodeObject
from .simplified_playlist_object import SimplifiedPlaylistObject
from .simplified_show_object import SimplifiedShowObject
from .simplified_track_object import SimplifiedTrackObject
from .skip_users_playback_to_next_track_response_401 import SkipUsersPlaybackToNextTrackResponse401
from .skip_users_playback_to_next_track_response_403 import SkipUsersPlaybackToNextTrackResponse403
from .skip_users_playback_to_next_track_response_429 import SkipUsersPlaybackToNextTrackResponse429
from .skip_users_playback_to_previous_track_response_401 import SkipUsersPlaybackToPreviousTrackResponse401
from .skip_users_playback_to_previous_track_response_403 import SkipUsersPlaybackToPreviousTrackResponse403
from .skip_users_playback_to_previous_track_response_429 import SkipUsersPlaybackToPreviousTrackResponse429
from .start_a_users_playback_body import StartAUsersPlaybackBody
from .start_a_users_playback_body_offset import StartAUsersPlaybackBodyOffset
from .start_a_users_playback_response_401 import StartAUsersPlaybackResponse401
from .start_a_users_playback_response_403 import StartAUsersPlaybackResponse403
from .start_a_users_playback_response_429 import StartAUsersPlaybackResponse429
from .time_interval_object import TimeIntervalObject
from .toggle_shuffle_for_users_playback_response_401 import ToggleShuffleForUsersPlaybackResponse401
from .toggle_shuffle_for_users_playback_response_403 import ToggleShuffleForUsersPlaybackResponse403
from .toggle_shuffle_for_users_playback_response_429 import ToggleShuffleForUsersPlaybackResponse429
from .track_object import TrackObject
from .track_object_linked_from import TrackObjectLinkedFrom
from .track_object_type import TrackObjectType
from .track_restriction_object import TrackRestrictionObject
from .transfer_a_users_playback_body import TransferAUsersPlaybackBody
from .transfer_a_users_playback_response_401 import TransferAUsersPlaybackResponse401
from .transfer_a_users_playback_response_403 import TransferAUsersPlaybackResponse403
from .transfer_a_users_playback_response_429 import TransferAUsersPlaybackResponse429
from .unfollow_artists_users_body import UnfollowArtistsUsersBody
from .unfollow_artists_users_item_type import UnfollowArtistsUsersItemType
from .unfollow_artists_users_response_401 import UnfollowArtistsUsersResponse401
from .unfollow_artists_users_response_403 import UnfollowArtistsUsersResponse403
from .unfollow_artists_users_response_429 import UnfollowArtistsUsersResponse429
from .unfollow_playlist_response_401 import UnfollowPlaylistResponse401
from .unfollow_playlist_response_403 import UnfollowPlaylistResponse403
from .unfollow_playlist_response_429 import UnfollowPlaylistResponse429
from .upload_custom_playlist_cover_response_401 import UploadCustomPlaylistCoverResponse401
from .upload_custom_playlist_cover_response_403 import UploadCustomPlaylistCoverResponse403
from .upload_custom_playlist_cover_response_429 import UploadCustomPlaylistCoverResponse429

__all__ = (
    "AddToQueueResponse401",
    "AddToQueueResponse403",
    "AddToQueueResponse429",
    "AddTracksToPlaylistBody",
    "AddTracksToPlaylistResponse201",
    "AddTracksToPlaylistResponse401",
    "AddTracksToPlaylistResponse403",
    "AddTracksToPlaylistResponse429",
    "AlbumBase",
    "AlbumBaseAlbumType",
    "AlbumBaseReleaseDatePrecision",
    "AlbumBaseType",
    "AlbumObject",
    "AlbumRestrictionObject",
    "AlbumRestrictionObjectReason",
    "ArtistDiscographyAlbumObject",
    "ArtistDiscographyAlbumObjectAlbumGroup",
    "ArtistObject",
    "ArtistObjectType",
    "AudioAnalysisObject",
    "AudioAnalysisObjectMeta",
    "AudioAnalysisObjectTrack",
    "AudiobookBase",
    "AudiobookBaseType",
    "AudiobookObject",
    "AudioFeaturesObject",
    "AudioFeaturesObjectType",
    "AuthorObject",
    "CategoryObject",
    "ChangePlaylistDetailsBody",
    "ChangePlaylistDetailsResponse401",
    "ChangePlaylistDetailsResponse403",
    "ChangePlaylistDetailsResponse429",
    "ChapterBase",
    "ChapterBaseReleaseDatePrecision",
    "ChapterBaseType",
    "ChapterObject",
    "ChapterRestrictionObject",
    "CheckCurrentUserFollowsItemType",
    "CheckCurrentUserFollowsResponse401",
    "CheckCurrentUserFollowsResponse403",
    "CheckCurrentUserFollowsResponse429",
    "CheckIfUserFollowsPlaylistResponse401",
    "CheckIfUserFollowsPlaylistResponse403",
    "CheckIfUserFollowsPlaylistResponse429",
    "CheckUsersSavedAlbumsResponse401",
    "CheckUsersSavedAlbumsResponse403",
    "CheckUsersSavedAlbumsResponse429",
    "CheckUsersSavedAudiobooksResponse401",
    "CheckUsersSavedAudiobooksResponse403",
    "CheckUsersSavedAudiobooksResponse429",
    "CheckUsersSavedEpisodesResponse401",
    "CheckUsersSavedEpisodesResponse403",
    "CheckUsersSavedEpisodesResponse429",
    "CheckUsersSavedShowsResponse401",
    "CheckUsersSavedShowsResponse403",
    "CheckUsersSavedShowsResponse429",
    "CheckUsersSavedTracksResponse401",
    "CheckUsersSavedTracksResponse403",
    "CheckUsersSavedTracksResponse429",
    "ContextObject",
    "CopyrightObject",
    "CreatePlaylistBody",
    "CreatePlaylistResponse401",
    "CreatePlaylistResponse403",
    "CreatePlaylistResponse429",
    "CurrentlyPlayingContextObject",
    "CursorObject",
    "CursorPagingObject",
    "CursorPagingPlayHistoryObject",
    "CursorPagingSimplifiedArtistObject",
    "DeviceObject",
    "DisallowsObject",
    "EpisodeBase",
    "EpisodeBaseReleaseDatePrecision",
    "EpisodeBaseType",
    "EpisodeObject",
    "EpisodeRestrictionObject",
    "ErrorObject",
    "ExplicitContentSettingsObject",
    "ExternalIdObject",
    "ExternalUrlObject",
    "FollowArtistsUsersBody",
    "FollowArtistsUsersItemType",
    "FollowArtistsUsersResponse401",
    "FollowArtistsUsersResponse403",
    "FollowArtistsUsersResponse429",
    "FollowersObject",
    "FollowPlaylistBody",
    "FollowPlaylistResponse401",
    "FollowPlaylistResponse403",
    "FollowPlaylistResponse429",
    "GetACategoriesPlaylistsResponse401",
    "GetACategoriesPlaylistsResponse403",
    "GetACategoriesPlaylistsResponse429",
    "GetACategoryResponse401",
    "GetACategoryResponse403",
    "GetACategoryResponse429",
    "GetAChapterResponse401",
    "GetAChapterResponse403",
    "GetAChapterResponse429",
    "GetAListOfCurrentUsersPlaylistsResponse401",
    "GetAListOfCurrentUsersPlaylistsResponse403",
    "GetAListOfCurrentUsersPlaylistsResponse429",
    "GetAnAlbumResponse401",
    "GetAnAlbumResponse403",
    "GetAnAlbumResponse429",
    "GetAnAlbumsTracksResponse401",
    "GetAnAlbumsTracksResponse403",
    "GetAnAlbumsTracksResponse429",
    "GetAnArtistResponse401",
    "GetAnArtistResponse403",
    "GetAnArtistResponse429",
    "GetAnArtistsAlbumsResponse401",
    "GetAnArtistsAlbumsResponse403",
    "GetAnArtistsAlbumsResponse429",
    "GetAnArtistsRelatedArtistsResponse200",
    "GetAnArtistsRelatedArtistsResponse401",
    "GetAnArtistsRelatedArtistsResponse403",
    "GetAnArtistsRelatedArtistsResponse429",
    "GetAnArtistsTopTracksResponse200",
    "GetAnArtistsTopTracksResponse401",
    "GetAnArtistsTopTracksResponse403",
    "GetAnArtistsTopTracksResponse429",
    "GetAnAudiobookResponse400",
    "GetAnAudiobookResponse401",
    "GetAnAudiobookResponse403",
    "GetAnAudiobookResponse404",
    "GetAnAudiobookResponse429",
    "GetAnEpisodeResponse401",
    "GetAnEpisodeResponse403",
    "GetAnEpisodeResponse429",
    "GetAShowResponse401",
    "GetAShowResponse403",
    "GetAShowResponse429",
    "GetAShowsEpisodesResponse401",
    "GetAShowsEpisodesResponse403",
    "GetAShowsEpisodesResponse429",
    "GetAudioAnalysisResponse401",
    "GetAudioAnalysisResponse403",
    "GetAudioAnalysisResponse429",
    "GetAudiobookChaptersResponse401",
    "GetAudiobookChaptersResponse403",
    "GetAudiobookChaptersResponse429",
    "GetAudioFeaturesResponse401",
    "GetAudioFeaturesResponse403",
    "GetAudioFeaturesResponse429",
    "GetAUsersAvailableDevicesResponse200",
    "GetAUsersAvailableDevicesResponse401",
    "GetAUsersAvailableDevicesResponse403",
    "GetAUsersAvailableDevicesResponse429",
    "GetAvailableMarketsResponse200",
    "GetAvailableMarketsResponse401",
    "GetAvailableMarketsResponse403",
    "GetAvailableMarketsResponse429",
    "GetCategoriesResponse200",
    "GetCategoriesResponse200Categories",
    "GetCategoriesResponse401",
    "GetCategoriesResponse403",
    "GetCategoriesResponse429",
    "GetCurrentUsersProfileResponse401",
    "GetCurrentUsersProfileResponse403",
    "GetCurrentUsersProfileResponse429",
    "GetFeaturedPlaylistsResponse401",
    "GetFeaturedPlaylistsResponse403",
    "GetFeaturedPlaylistsResponse429",
    "GetFollowedItemType",
    "GetFollowedResponse200",
    "GetFollowedResponse401",
    "GetFollowedResponse403",
    "GetFollowedResponse429",
    "GetInformationAboutTheUsersCurrentPlaybackResponse401",
    "GetInformationAboutTheUsersCurrentPlaybackResponse403",
    "GetInformationAboutTheUsersCurrentPlaybackResponse429",
    "GetListUsersPlaylistsResponse401",
    "GetListUsersPlaylistsResponse403",
    "GetListUsersPlaylistsResponse429",
    "GetMultipleAlbumsResponse200",
    "GetMultipleAlbumsResponse401",
    "GetMultipleAlbumsResponse403",
    "GetMultipleAlbumsResponse429",
    "GetMultipleArtistsResponse200",
    "GetMultipleArtistsResponse401",
    "GetMultipleArtistsResponse403",
    "GetMultipleArtistsResponse429",
    "GetMultipleAudiobooksResponse200",
    "GetMultipleAudiobooksResponse401",
    "GetMultipleAudiobooksResponse403",
    "GetMultipleAudiobooksResponse429",
    "GetMultipleEpisodesResponse200",
    "GetMultipleEpisodesResponse401",
    "GetMultipleEpisodesResponse403",
    "GetMultipleEpisodesResponse429",
    "GetMultipleShowsResponse200",
    "GetMultipleShowsResponse401",
    "GetMultipleShowsResponse403",
    "GetMultipleShowsResponse429",
    "GetNewReleasesResponse200",
    "GetNewReleasesResponse401",
    "GetNewReleasesResponse403",
    "GetNewReleasesResponse429",
    "GetPlaylistCoverResponse401",
    "GetPlaylistCoverResponse403",
    "GetPlaylistCoverResponse429",
    "GetPlaylistResponse401",
    "GetPlaylistResponse403",
    "GetPlaylistResponse429",
    "GetPlaylistsTracksResponse401",
    "GetPlaylistsTracksResponse403",
    "GetPlaylistsTracksResponse429",
    "GetQueueResponse401",
    "GetQueueResponse403",
    "GetQueueResponse429",
    "GetRecentlyPlayedResponse401",
    "GetRecentlyPlayedResponse403",
    "GetRecentlyPlayedResponse429",
    "GetRecommendationGenresResponse200",
    "GetRecommendationGenresResponse401",
    "GetRecommendationGenresResponse403",
    "GetRecommendationGenresResponse429",
    "GetRecommendationsResponse401",
    "GetRecommendationsResponse403",
    "GetRecommendationsResponse429",
    "GetSeveralAudioFeaturesResponse200",
    "GetSeveralAudioFeaturesResponse401",
    "GetSeveralAudioFeaturesResponse403",
    "GetSeveralAudioFeaturesResponse429",
    "GetSeveralChaptersResponse200",
    "GetSeveralChaptersResponse401",
    "GetSeveralChaptersResponse403",
    "GetSeveralChaptersResponse429",
    "GetSeveralTracksResponse200",
    "GetSeveralTracksResponse401",
    "GetSeveralTracksResponse403",
    "GetSeveralTracksResponse429",
    "GetTheUsersCurrentlyPlayingTrackResponse401",
    "GetTheUsersCurrentlyPlayingTrackResponse403",
    "GetTheUsersCurrentlyPlayingTrackResponse429",
    "GetTrackResponse401",
    "GetTrackResponse403",
    "GetTrackResponse429",
    "GetUsersProfileResponse401",
    "GetUsersProfileResponse403",
    "GetUsersProfileResponse429",
    "GetUsersSavedAlbumsResponse401",
    "GetUsersSavedAlbumsResponse403",
    "GetUsersSavedAlbumsResponse429",
    "GetUsersSavedAudiobooksResponse401",
    "GetUsersSavedAudiobooksResponse403",
    "GetUsersSavedAudiobooksResponse429",
    "GetUsersSavedEpisodesResponse401",
    "GetUsersSavedEpisodesResponse403",
    "GetUsersSavedEpisodesResponse429",
    "GetUsersSavedShowsResponse401",
    "GetUsersSavedShowsResponse403",
    "GetUsersSavedShowsResponse429",
    "GetUsersSavedTracksResponse401",
    "GetUsersSavedTracksResponse403",
    "GetUsersSavedTracksResponse429",
    "GetUsersTopArtistsAndTracksResponse200",
    "GetUsersTopArtistsAndTracksResponse401",
    "GetUsersTopArtistsAndTracksResponse403",
    "GetUsersTopArtistsAndTracksResponse429",
    "GetUsersTopArtistsAndTracksType",
    "ImageObject",
    "LinkedTrackObject",
    "NarratorObject",
    "PagingArtistDiscographyAlbumObject",
    "PagingArtistObject",
    "PagingFeaturedPlaylistObject",
    "PagingObject",
    "PagingPlaylistObject",
    "PagingPlaylistTrackObject",
    "PagingSavedAlbumObject",
    "PagingSavedEpisodeObject",
    "PagingSavedShowObject",
    "PagingSavedTrackObject",
    "PagingSimplifiedAlbumObject",
    "PagingSimplifiedAudiobookObject",
    "PagingSimplifiedChapterObject",
    "PagingSimplifiedEpisodeObject",
    "PagingSimplifiedShowObject",
    "PagingSimplifiedTrackObject",
    "PagingTrackObject",
    "PauseAUsersPlaybackResponse401",
    "PauseAUsersPlaybackResponse403",
    "PauseAUsersPlaybackResponse429",
    "PlayHistoryObject",
    "PlaylistObject",
    "PlaylistOwnerObject",
    "PlaylistTrackObject",
    "PlaylistTracksRefObject",
    "PlaylistUserObject",
    "PlaylistUserObjectType",
    "PrivateUserObject",
    "PublicUserObject",
    "PublicUserObjectType",
    "QueueObject",
    "RecommendationSeedObject",
    "RecommendationsObject",
    "RemoveAlbumsUserBody",
    "RemoveAlbumsUserResponse401",
    "RemoveAlbumsUserResponse403",
    "RemoveAlbumsUserResponse429",
    "RemoveAudiobooksUserResponse401",
    "RemoveAudiobooksUserResponse403",
    "RemoveAudiobooksUserResponse429",
    "RemoveEpisodesUserBody",
    "RemoveEpisodesUserResponse401",
    "RemoveEpisodesUserResponse403",
    "RemoveEpisodesUserResponse429",
    "RemoveShowsUserResponse401",
    "RemoveShowsUserResponse403",
    "RemoveShowsUserResponse429",
    "RemoveTracksPlaylistBody",
    "RemoveTracksPlaylistBodyTracksItem",
    "RemoveTracksPlaylistResponse200",
    "RemoveTracksPlaylistResponse401",
    "RemoveTracksPlaylistResponse403",
    "RemoveTracksPlaylistResponse429",
    "RemoveTracksUserBody",
    "RemoveTracksUserResponse401",
    "RemoveTracksUserResponse403",
    "RemoveTracksUserResponse429",
    "ReorderOrReplacePlaylistsTracksBody",
    "ReorderOrReplacePlaylistsTracksResponse200",
    "ReorderOrReplacePlaylistsTracksResponse401",
    "ReorderOrReplacePlaylistsTracksResponse403",
    "ReorderOrReplacePlaylistsTracksResponse429",
    "ResumePointObject",
    "SaveAlbumsUserBody",
    "SaveAlbumsUserResponse401",
    "SaveAlbumsUserResponse403",
    "SaveAlbumsUserResponse429",
    "SaveAudiobooksUserResponse401",
    "SaveAudiobooksUserResponse403",
    "SaveAudiobooksUserResponse429",
    "SavedAlbumObject",
    "SavedEpisodeObject",
    "SavedShowObject",
    "SavedTrackObject",
    "SaveEpisodesUserBody",
    "SaveEpisodesUserResponse401",
    "SaveEpisodesUserResponse403",
    "SaveEpisodesUserResponse429",
    "SaveShowsUserResponse401",
    "SaveShowsUserResponse403",
    "SaveShowsUserResponse429",
    "SaveTracksUserBody",
    "SaveTracksUserBodyTimestampedIdsItem",
    "SaveTracksUserResponse401",
    "SaveTracksUserResponse403",
    "SaveTracksUserResponse429",
    "SearchIncludeExternal",
    "SearchResponse200",
    "SearchResponse401",
    "SearchResponse403",
    "SearchResponse429",
    "SearchTypeItem",
    "SectionObject",
    "SectionObjectMode",
    "SeekToPositionInCurrentlyPlayingTrackResponse401",
    "SeekToPositionInCurrentlyPlayingTrackResponse403",
    "SeekToPositionInCurrentlyPlayingTrackResponse429",
    "SegmentObject",
    "SetRepeatModeOnUsersPlaybackResponse401",
    "SetRepeatModeOnUsersPlaybackResponse403",
    "SetRepeatModeOnUsersPlaybackResponse429",
    "SetVolumeForUsersPlaybackResponse401",
    "SetVolumeForUsersPlaybackResponse403",
    "SetVolumeForUsersPlaybackResponse429",
    "ShowBase",
    "ShowBaseType",
    "ShowObject",
    "SimplifiedAlbumObject",
    "SimplifiedArtistObject",
    "SimplifiedArtistObjectType",
    "SimplifiedAudiobookObject",
    "SimplifiedChapterObject",
    "SimplifiedEpisodeObject",
    "SimplifiedPlaylistObject",
    "SimplifiedShowObject",
    "SimplifiedTrackObject",
    "SkipUsersPlaybackToNextTrackResponse401",
    "SkipUsersPlaybackToNextTrackResponse403",
    "SkipUsersPlaybackToNextTrackResponse429",
    "SkipUsersPlaybackToPreviousTrackResponse401",
    "SkipUsersPlaybackToPreviousTrackResponse403",
    "SkipUsersPlaybackToPreviousTrackResponse429",
    "StartAUsersPlaybackBody",
    "StartAUsersPlaybackBodyOffset",
    "StartAUsersPlaybackResponse401",
    "StartAUsersPlaybackResponse403",
    "StartAUsersPlaybackResponse429",
    "TimeIntervalObject",
    "ToggleShuffleForUsersPlaybackResponse401",
    "ToggleShuffleForUsersPlaybackResponse403",
    "ToggleShuffleForUsersPlaybackResponse429",
    "TrackObject",
    "TrackObjectLinkedFrom",
    "TrackObjectType",
    "TrackRestrictionObject",
    "TransferAUsersPlaybackBody",
    "TransferAUsersPlaybackResponse401",
    "TransferAUsersPlaybackResponse403",
    "TransferAUsersPlaybackResponse429",
    "UnfollowArtistsUsersBody",
    "UnfollowArtistsUsersItemType",
    "UnfollowArtistsUsersResponse401",
    "UnfollowArtistsUsersResponse403",
    "UnfollowArtistsUsersResponse429",
    "UnfollowPlaylistResponse401",
    "UnfollowPlaylistResponse403",
    "UnfollowPlaylistResponse429",
    "UploadCustomPlaylistCoverResponse401",
    "UploadCustomPlaylistCoverResponse403",
    "UploadCustomPlaylistCoverResponse429",
)
