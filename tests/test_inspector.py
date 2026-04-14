from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from core.inspector import TileInfo, inspect, validate_defra_format


def _make_fake_dataset(
    band_data: np.ndarray,
    nodata: float = -9999.0,
    crs_epsg: int = 27700,
    pixel_size: float = 1.0,
    origin_x: float = 400000.0,
    origin_y: float = 300004.0,
    dtype: str = "float32",
):
    """Build a MagicMock that behaves like a rasterio dataset."""
    ds = MagicMock()

    crs = MagicMock()
    crs.to_epsg.return_value = crs_epsg
    crs.to_string.return_value = f"EPSG:{crs_epsg}"
    ds.crs = crs

    transform = MagicMock()
    transform.a = pixel_size
    transform.c = origin_x
    transform.e = -pixel_size
    transform.f = origin_y
    ds.transform = transform

    ds.width = band_data.shape[1]
    ds.height = band_data.shape[0]
    ds.nodata = nodata
    ds.dtypes = (dtype,)
    ds.read.return_value = band_data

    # Support context manager
    ds.__enter__ = MagicMock(return_value=ds)
    ds.__exit__ = MagicMock(return_value=False)
    return ds


class TestInspect:
    @patch("core.inspector.rasterio.open")
    def test_returns_correct_tile_info(self, mock_open):
        band = np.array(
            [[1.0, 2.0], [3.0, 4.0]], dtype=np.float32
        )
        ds = _make_fake_dataset(band)
        mock_open.return_value = ds

        info = inspect("fake.tif")

        assert info.path == "fake.tif"
        assert info.crs_epsg == 27700
        assert info.crs_name == "EPSG:27700"
        assert info.pixel_size_m == 1.0
        assert info.width_px == 2
        assert info.height_px == 2
        assert info.width_m == 2.0
        assert info.height_m == 2.0
        assert info.origin_easting == 400000.0
        assert info.origin_northing == 300004.0
        assert info.z_min == pytest.approx(1.0)
        assert info.z_max == pytest.approx(4.0)
        assert info.z_mean == pytest.approx(2.5)
        assert info.nodata_value == -9999.0
        assert info.point_count == 4
        assert info.data_type == "float32"

    @patch("core.inspector.rasterio.open")
    def test_filters_nodata_from_stats(self, mock_open):
        band = np.array(
            [[-9999.0, 2.0], [3.0, -9999.0]], dtype=np.float32
        )
        ds = _make_fake_dataset(band, nodata=-9999.0)
        mock_open.return_value = ds

        info = inspect("fake.tif")

        assert info.point_count == 2
        assert info.z_min == pytest.approx(2.0)
        assert info.z_max == pytest.approx(3.0)
        assert info.z_mean == pytest.approx(2.5)

    @patch("core.inspector.rasterio.open")
    def test_raises_when_all_nodata(self, mock_open):
        band = np.array(
            [[-9999.0, -9999.0], [-9999.0, -9999.0]], dtype=np.float32
        )
        ds = _make_fake_dataset(band, nodata=-9999.0)
        mock_open.return_value = ds

        with pytest.raises(ValueError, match="no valid elevation data"):
            inspect("fake.tif")


class TestValidateDefraFormat:
    def _valid_info(self, **overrides) -> TileInfo:
        defaults = dict(
            path="tile.tif",
            crs_epsg=27700,
            crs_name="EPSG:27700",
            pixel_size_m=1.0,
            width_px=100,
            height_px=100,
            width_m=100.0,
            height_m=100.0,
            origin_easting=400000.0,
            origin_northing=300000.0,
            z_min=0.0,
            z_max=10.0,
            z_mean=5.0,
            nodata_value=-9999.0,
            point_count=10000,
            data_type="float32",
        )
        defaults.update(overrides)
        return TileInfo(**defaults)

    def test_valid_tile_returns_no_warnings(self):
        info = self._valid_info()
        assert validate_defra_format(info) == []

    def test_wrong_crs_warns(self):
        info = self._valid_info(crs_epsg=4326)
        warnings = validate_defra_format(info)
        assert any("EPSG:4326" in w for w in warnings)

    def test_wrong_pixel_size_warns(self):
        info = self._valid_info(pixel_size_m=2.0)
        warnings = validate_defra_format(info)
        assert any("2.0m" in w for w in warnings)

    def test_wrong_data_type_warns(self):
        info = self._valid_info(data_type="int16")
        warnings = validate_defra_format(info)
        assert any("int16" in w for w in warnings)

    def test_accepted_pixel_sizes(self):
        for ps in (0.25, 0.5, 1.0):
            info = self._valid_info(pixel_size_m=ps)
            warnings = validate_defra_format(info)
            assert not any("Pixel size" in w for w in warnings)
