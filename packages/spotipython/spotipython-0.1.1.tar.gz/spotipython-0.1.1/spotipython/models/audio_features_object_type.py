from enum import Enum


class AudioFeaturesObjectType(str, Enum):
    AUDIO_FEATURES = "audio_features"

    def __str__(self) -> str:
        return str(self.value)
