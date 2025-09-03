from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.serializable import Serializable
from rudi_node_read.utils.type_dict import (
    check_has_key,
    check_is_dict,
    check_is_dict_or_none,
)
from rudi_node_read.utils.type_string import check_is_string_or_none
from rudi_node_read.utils.typing_utils import check_type, ensure_is_number


def check_is_latitude(latitude: float, alt_err_msg: str | None = None) -> float:
    latitude = ensure_is_number(latitude)
    if not -90 <= latitude <= 90:
        raise ValueError(
            f"{'latitude' if not alt_err_msg else alt_err_msg}"
            f" should be a decimal between -90 and 90, got '{latitude}'"
        )
    return float(latitude)


def check_is_longitude(longitude: float, alt_err_msg: str | None = None) -> float:
    longitude = ensure_is_number(longitude)
    if not -180 <= longitude <= 180:
        raise ValueError(
            f"{'longitude' if not alt_err_msg else alt_err_msg}"
            f" should be a decimal between -180 and 180, got '{longitude}'"
        )
    return float(longitude)


class BoundingBox(Serializable):
    def __init__(
        self,
        south_latitude: float,
        west_longitude: float,
        north_latitude: float,
        east_longitude: float,
    ):
        """
        Coordinates of a bounding box, given as decimal numbers (ISO 6709)
        :param south_latitude: southernmost latitude
        :param west_longitude: westernmost longitude
        :param north_latitude: northernmost latitude
        :param east_longitude: easternmost longitude
        """
        self.south_latitude = check_is_latitude(south_latitude, "southernmost latitude")
        self.north_latitude = check_is_latitude(north_latitude, "northernmost latitude")
        if self.south_latitude > self.north_latitude:
            raise ValueError("southernmost latitude should be lower than northernmost latitude")
        self.west_longitude = check_is_longitude(west_longitude, "westernmost longitude")
        self.east_longitude = check_is_longitude(east_longitude, "easternmost longitude")
        if self.west_longitude > self.east_longitude:
            print(
                f"! BoundingBox warning: westernmost latitude is generally lower than easternmost latitude. Got W: {self.west_longitude} > E: {self.east_longitude}"
            )

    @staticmethod
    def from_json(o: dict):
        check_is_dict(o)
        south_latitude = check_is_latitude(check_has_key(o, "south_latitude"), "southernmost latitude")
        north_latitude = check_is_latitude(check_has_key(o, "north_latitude"), "northernmost latitude")
        west_longitude = check_is_longitude(check_has_key(o, "west_longitude"), "westernmost longitude")
        east_longitude = check_is_longitude(check_has_key(o, "east_longitude"), "easternmost longitude")
        return BoundingBox(
            south_latitude=south_latitude,
            north_latitude=north_latitude,
            west_longitude=west_longitude,
            east_longitude=east_longitude,
        )

    @staticmethod
    def merge_bbox_list(bbox_list: list):
        frst_bbox = bbox_list[0]
        lowest_south = frst_bbox.south_latitude
        highest_north = frst_bbox.north_latitude
        lowest_west = frst_bbox.west_longitude
        highest_east = frst_bbox.east_longitude
        if len(bbox_list) > 1:
            for bbox in bbox_list[1:]:
                lowest_south = min(lowest_south, bbox.south_latitude)
                highest_north = max(highest_north, bbox.north_latitude)
                lowest_west = min(lowest_west, bbox.west_longitude)
                highest_east = max(highest_east, bbox.east_longitude)
        return BoundingBox(
            south_latitude=lowest_south,
            west_longitude=lowest_west,
            north_latitude=highest_north,
            east_longitude=highest_east,
        )


class RudiGeography(Serializable):
    def __init__(
        self,
        bounding_box: BoundingBox,
        geographic_distribution: dict | None = None,
        projection: str | None = None,
    ):
        self.bounding_box = check_type(bounding_box, BoundingBox)
        self.geographic_distribution = check_is_dict_or_none(geographic_distribution)
        self.projection = check_is_string_or_none(projection)

    @staticmethod
    def from_json(o: dict | None):
        if o is None:
            return None
        return RudiGeography(
            bounding_box=BoundingBox.from_json(check_has_key(o, "bounding_box")),
            geographic_distribution=o.get("geographic_distribution"),
            projection=o.get("projection"),
        )


if __name__ == "__main__":  # pragma: no cover
    tests = "geo_tests"
    bb1 = BoundingBox(10, 120, 30, 40)
    bb = BoundingBox.from_json(
        {
            "south_latitude": -10,
            "north_latitude": 24.8,
            "west_longitude": 40.7,
            "east_longitude": 104.8,
        }
    )
    log_d(tests, "BoundingBox", bb)

    geo = {
        "bounding_box": {
            "west_longitude": -1.96327,
            "east_longitude": -1.46558,
            "south_latitude": 47.93192,
            "north_latitude": 48.30684,
        },
        "geographic_distribution": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-1.96327, 47.93192],
                    [-1.46558, 47.93192],
                    [-1.46558, 48.30684],
                    [-1.96327, 48.30684],
                    [-1.96327, 47.93192],
                ]
            ],
            "bbox": [-1.96327, 47.93192, -1.46558, 48.30684],
        },
        "projection": "WGS 84 (EPSG:4326)",
    }
    log_d(tests, "RudiGeography", RudiGeography.from_json(geo))
