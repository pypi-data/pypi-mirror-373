"""Stems for organizing files into separate dsps repeats."""

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspStemName
from dkist_processing_cryonirsp.parsers.scan_step import MapScanStepStemBase


class MapScanFlower(MapScanStepStemBase):
    """Flower for computing and assigning map scan numbers."""

    def __init__(self):
        super().__init__(stem_name=CryonirspStemName.map_scan.value)

    def getter(self, key: str) -> int:
        """Compute the map scan number for a single frame.

        The frame implies a SingleScanStep. That object is then compared to the sorted list of objects for a single
        (raster_step, meas_num, modstate, sub_repeat) tuple. The location within that sorted list is the map scan number.
        """
        return self.get_map_scan_for_key(key)


class NumMapScansBud(MapScanStepStemBase):
    """
    Bud for determining the total number of dsps repeats.

    Also checks that all scan steps have the same number of dsps repeats.
    """

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.num_map_scans.value)

    def getter(self, key: str) -> int:
        """
        Compute the total number of dsps repeats.

        The number of map_scans for every scan step are calculated and if a map_scan is incomplete,
        it will not be included.
        Assumes the incomplete map_scan is always the last one due to summit abort or cancellation.
        """
        return self.number_of_complete_map_scans
