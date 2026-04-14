from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from core.extractor import apply_local_shift, extract_points


def _make_fake_dataset(band_data: np.ndarray, pixel_size: float = 1.0,
                       origin_x: float = 500.0, origin_y: float = 504.0):
    """Build a MagicMock rasterio dataset for a small raster."""
    ds = MagicMock()

    transform = MagicMock()
    transform.a = pixel_size
    transform.c = origin_x
    transform.e = -pixel_size
    transform.f = origin_y
    ds.transform = transform

    ds.read.return_value = band_data
    ds.__enter__ = MagicMock(return_value=ds)
    ds.__exit__ = MagicMock(return_value=False)
    return ds


class TestExtractPoints:
    @patch("core.extractor.rasterio.open")
    def test_returns_correct_shape_and_coordinates(self, mock_open):
        band = np.array(
            [[10.0, 20.0, 30.0, 40.0],
             [11.0, 21.0, 31.0, 41.0],
             [12.0, 22.0, 32.0, 42.0],
             [13.0, 23.0, 33.0, 43.0]],
            dtype=np.float32,
        )
        ds = _make_fake_dataset(band, pixel_size=1.0, origin_x=500.0, origin_y=504.0)
        mock_open.return_value = ds

        pts = extract_points("fake.tif", nodata_value=-9999.0)

        # 4x4 grid with no nodata -> 16 points, 3 columns
        assert pts.shape == (16, 3)

        # First pixel (row=0, col=0): x = 500 + (0+0.5)*1 = 500.5
        #                              y = 504 + (0+0.5)*(-1) = 503.5
        #                              z = 10.0
        assert pts[0, 0] == pytest.approx(500.5)
        assert pts[0, 1] == pytest.approx(503.5)
        assert pts[0, 2] == pytest.approx(10.0)

    @patch("core.extractor.rasterio.open")
    def test_filters_nodata(self, mock_open):
        band = np.array(
            [[10.0, -9999.0],
             [-9999.0, 40.0]],
            dtype=np.float32,
        )
        ds = _make_fake_dataset(band)
        mock_open.return_value = ds

        pts = extract_points("fake.tif", nodata_value=-9999.0)

        assert pts.shape == (2, 3)
        assert pts[0, 2] == pytest.approx(10.0)
        assert pts[1, 2] == pytest.approx(40.0)

    @patch("core.extractor.rasterio.open")
    def test_decimation_reduces_point_count(self, mock_open):
        band = np.array(
            [[10.0, 20.0, 30.0, 40.0],
             [11.0, 21.0, 31.0, 41.0],
             [12.0, 22.0, 32.0, 42.0],
             [13.0, 23.0, 33.0, 43.0]],
            dtype=np.float32,
        )
        ds = _make_fake_dataset(band)
        mock_open.return_value = ds

        pts = extract_points("fake.tif", nodata_value=-9999.0, decimation=2)

        # 4x4 with decimation=2 -> 2x2 = 4 points
        assert pts.shape == (4, 3)


class TestApplyLocalShift:
    def test_subtracts_min_xy_preserves_z(self):
        pts = np.array(
            [[100.0, 200.0, 5.0],
             [102.0, 203.0, 8.0],
             [101.0, 201.0, 6.0]],
            dtype=np.float64,
        )

        shifted, (sx, sy) = apply_local_shift(pts)

        assert sx == pytest.approx(100.0)
        assert sy == pytest.approx(200.0)

        assert shifted[0, 0] == pytest.approx(0.0)
        assert shifted[0, 1] == pytest.approx(0.0)
        assert shifted[1, 0] == pytest.approx(2.0)
        assert shifted[1, 1] == pytest.approx(3.0)

        # Z unchanged
        np.testing.assert_array_almost_equal(shifted[:, 2], pts[:, 2])

    def test_does_not_mutate_original(self):
        pts = np.array([[10.0, 20.0, 1.0]], dtype=np.float64)
        original_x = pts[0, 0]

        apply_local_shift(pts)

        assert pts[0, 0] == pytest.approx(original_x)
