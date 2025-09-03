from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.recommendation_seed_object import RecommendationSeedObject
    from ..models.track_object import TrackObject


T = TypeVar("T", bound="RecommendationsObject")


@_attrs_define
class RecommendationsObject:
    """
    Attributes:
        seeds (list['RecommendationSeedObject']): An array of recommendation seed objects.
        tracks (list['TrackObject']): An array of track object (simplified) ordered according to the parameters
            supplied.
    """

    seeds: list["RecommendationSeedObject"]
    tracks: list["TrackObject"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        seeds = []
        for seeds_item_data in self.seeds:
            seeds_item = seeds_item_data.to_dict()
            seeds.append(seeds_item)

        tracks = []
        for tracks_item_data in self.tracks:
            tracks_item = tracks_item_data.to_dict()
            tracks.append(tracks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "seeds": seeds,
                "tracks": tracks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recommendation_seed_object import RecommendationSeedObject
        from ..models.track_object import TrackObject

        d = dict(src_dict)
        seeds = []
        _seeds = d.pop("seeds")
        for seeds_item_data in _seeds:
            seeds_item = RecommendationSeedObject.from_dict(seeds_item_data)

            seeds.append(seeds_item)

        tracks = []
        _tracks = d.pop("tracks")
        for tracks_item_data in _tracks:
            tracks_item = TrackObject.from_dict(tracks_item_data)

            tracks.append(tracks_item)

        recommendations_object = cls(
            seeds=seeds,
            tracks=tracks,
        )

        recommendations_object.additional_properties = d
        return recommendations_object

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
