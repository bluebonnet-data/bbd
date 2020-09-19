from pathlib import Path

import shapefile

from bbd import gis

here = Path(__file__).parent


def test_trim_shapefile():
    in_path = here / "shapefiles/co/tl_2019_08_cd116"
    join_on = "GEOID"
    include = [
        "0804",
        "0803",
        "0802",
        "0801",
    ]

    out_path = gis.trim_shapefile(in_path, join_on, include)

    with shapefile.Reader(str(out_path)) as r:

        shape_records = r.shapeRecords()
        assert len(shape_records) == 4

        geoids = [sr.record["GEOID"] for sr in shape_records]
        assert sorted(geoids) == sorted(include)
