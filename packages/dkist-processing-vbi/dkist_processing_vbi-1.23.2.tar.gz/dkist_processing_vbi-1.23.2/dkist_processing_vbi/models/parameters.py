"""VBI calibration pipeline parameters."""

from dkist_processing_common.models.parameters import ParameterBase


class VbiParameters(ParameterBase):
    """VBI calibration pipeline parameters."""

    @property
    def movie_intensity_clipping_percentile(self) -> float:
        """Percentile to clip the movie intensity at."""
        return self._find_most_recent_past_value("vbi_movie_intensity_clipping_percentile")
