"""Test chromaticity methods."""
from coloraide import Color
from . import util
import pytest
import unittest
from coloraide import util as cutil


class TestChromaticity(util.ColorAssertsPyTest):
    """Test chromaticity conversions."""

    @pytest.mark.parametrize(
        'color,xy',
        [
            ('color(srgb 1 0 0)', (0.64, 0.33)),
            ('color(srgb 0 1 0)', (0.30, 0.60)),
            ('color(srgb 0 0 1)', (0.15, 0.06)),
            ('color(display-p3 1 0 0)', (0.68, 0.32)),
            ('color(display-p3 0 1 0)', (0.265, 0.69)),
            ('color(display-p3 0 0 1)', (0.150, 0.060)),
            ('color(a98-rgb 1 0 0)', (0.64, 0.33)),
            ('color(a98-rgb 0 1 0)', (0.21, 0.71)),
            ('color(a98-rgb 0 0 1)', (0.15, 0.06)),
            ('color(prophoto-rgb 1 0 0)', (0.7347, 0.2653)),
            ('color(prophoto-rgb 0 1 0)', (0.1596, 0.8404)),
            ('color(prophoto-rgb 0 0 1)', (0.0366, 0.0001)),
            ('color(rec2020 1 0 0)', (0.708, 0.292)),
            ('color(rec2020 0 1 0)', (0.17, 0.797)),
            ('color(rec2020 0 0 1)', (0.131, 0.046))
        ]
    )
    def test_xy(self, color, xy):
        """Test `xy` conversions."""

        xy2 = Color(color).xy()
        for v1, v2 in zip(xy, xy2):
            self.assertCompare(v1, v2)

    @pytest.mark.parametrize(
        'color,uv',
        [
            ('color(srgb 1 0 0)', (0.4507, 0.52289)),
            ('color(srgb 0 1 0)', (0.125, 0.5625)),
            ('color(srgb 0 0 1)', (0.17544, 0.15789)),
            ('color(display-p3 1 0 0)', (0.49635, 0.52555)),
            ('color(display-p3 0 1 0)', (0.0986, 0.57767)),
            ('color(display-p3 0 0 1)', (0.17544, 0.15789)),
            ('color(a98-rgb 1 0 0)', (0.4507, 0.52289)),
            ('color(a98-rgb 0 1 0)', (0.07568, 0.57568)),
            ('color(a98-rgb 0 0 1)', (0.17544, 0.15789)),
            ('color(prophoto-rgb 1 0 0)', (0.62339, 0.50649)),
            ('color(prophoto-rgb 0 1 0)', (0.05001, 0.5925)),
            ('color(prophoto-rgb 0 0 1)', (0.05, 0.00031)),
            ('color(rec2020 1 0 0)', (0.5566, 0.51651)),
            ('color(rec2020 0 1 0)', (0.05563, 0.5868)),
            ('color(rec2020 0 0 1)', (0.15927, 0.12584))
        ]
    )
    def test_xy_1976(self, color, uv):
        """Test `uv` 1976 conversions."""

        uv2 = Color(color).uv()
        for v1, v2 in zip(uv, uv2):
            self.assertCompare(v1, v2)

    @pytest.mark.parametrize(
        'color,uv',
        [
            ('color(srgb 1 0 0)', (0.4507, 0.34859)),
            ('color(srgb 0 1 0)', (0.125, 0.375)),
            ('color(srgb 0 0 1)', (0.17544, 0.10526)),
            ('color(display-p3 1 0 0)', (0.49635, 0.35036)),
            ('color(display-p3 0 1 0)', (0.0986, 0.38512)),
            ('color(display-p3 0 0 1)', (0.17544, 0.10526)),
            ('color(a98-rgb 1 0 0)', (0.4507, 0.34859)),
            ('color(a98-rgb 0 1 0)', (0.07568, 0.38378)),
            ('color(a98-rgb 0 0 1)', (0.17544, 0.10526)),
            ('color(prophoto-rgb 1 0 0)', (0.62339, 0.33766)),
            ('color(prophoto-rgb 0 1 0)', (0.05001, 0.395)),
            ('color(prophoto-rgb 0 0 1)', (0.05, 0.0002)),
            ('color(rec2020 1 0 0)', (0.5566, 0.34434)),
            ('color(rec2020 0 1 0)', (0.05563, 0.3912)),
            ('color(rec2020 0 0 1)', (0.15927, 0.08389))
        ]
    )
    def test_xy_1960(self, color, uv):
        """Test `uv` 1960 conversions."""

        uv2 = Color(color).uv('1960')
        for v1, v2 in zip(uv, uv2):
            self.assertCompare(v1, v2)


class TestChromaticitySpecificCases(util.ColorAsserts, unittest.TestCase):
    """Test distance specific cases."""

    def test_xy_luminance(self):
        """Test xy with luminance."""

        xyy = Color('red').split_chromaticity('xy-1931')
        for v1, v2 in zip(xyy, [0.64, 0.33, 0.21264]):
            self.assertCompare(v1, v2)

    def test_uv_1960_luminance(self):
        """Test uv 1960 with luminance."""

        uvy = Color('red').split_chromaticity('uv-1960')
        for v1, v2 in zip(uvy, [0.4507, 0.34859, 0.21264]):
            self.assertCompare(v1, v2)

    def test_uv_1976_luminance(self):
        """Test uv 1976 with luminance."""

        uvy = Color('red').split_chromaticity('uv-1976')
        for v1, v2 in zip(uvy, [0.4507, 0.52289, 0.21264]):
            self.assertCompare(v1, v2)

    def test_new_xy_color(self):
        """Test new xy color."""

        c1 = Color('red')
        xyy = c1.split_chromaticity('xy-1931')
        c2 = Color.chromaticity('srgb', xyy, 'xy-1931')
        self.assertColorEqual(c1, c2)

    def test_new_uv_1960_color(self):
        """Test new uv 1960 color."""

        c1 = Color('red')
        uvy = c1.split_chromaticity('uv-1960')
        c2 = Color.chromaticity('srgb', uvy, 'uv-1960')
        self.assertColorEqual(c1, c2)

    def test_new_uv_1976_color(self):
        """Test new uv 1976 color."""

        c1 = Color('red')
        uvy = c1.split_chromaticity('uv-1976')
        c2 = Color.chromaticity('srgb', uvy, 'uv-1976')
        self.assertColorEqual(c1, c2)

    def test_chromaticity_bad_value(self):
        """Test bad chromaticity input."""

        with self.assertRaises(ValueError):
            Color.chromaticity('srgb', [0, 0], 'bad')

    def test_color_from_2D_chromaticity(self):
        """Test new color from 2D chromaticity."""

        c1 = Color('red')
        xy = c1.xy()
        c2 = Color.chromaticity('srgb', xy, 'xy-1931', scale=True, scale_space='srgb-linear')
        self.assertEqual(c2.to_string(fit=False), 'rgb(255 0 0)')
        [self.assertCompare(v1, v2) for v1, v2 in zip(c2.xy(), xy)]

    def test_uv_1960_to_xy(self):
        """Test `uv` 1960 to `xy`."""

        xy = Color('red').xy()
        uv = Color('red').uv('1960')

        for v1, v2 in zip(xy, cutil.uv_1960_to_xy(uv)):
            self.assertCompare(v1, v2)

    def test_uv_1976_to_xy(self):
        """Test `uv` 1960 to `xy`."""

        xy = Color('red').xy()
        uv = Color('red').uv('1976')

        for v1, v2 in zip(xy, cutil.uv_to_xy(uv)):
            self.assertCompare(v1, v2)

    def test_uv_1960_zero(self):
        """Test a case that should return zero."""

        u, v = cutil.xy_to_uv_1960((7.5, 1))
        self.assertCompare(u, 0)
        self.assertCompare(v, 0)

    def test_uv_1976_xy_zero(self):
        """Test a case that should return zero."""

        x, y = cutil.uv_to_xy((2 / 3, 1))
        self.assertCompare(x, 0)
        self.assertCompare(y, 0)

    def test_uv_1960_xy_zero(self):
        """Test a case that should return zero."""

        x, y = cutil.uv_1960_to_xy((2, 1))
        self.assertCompare(x, 0)
        self.assertCompare(y, 0)

    def test_bad_uv_value(self):
        """Test bad `uv` mode value."""

        with self.assertRaises(ValueError):
            Color('red').uv('bad')

    def test_chromaticity_no_xyz_value(self):
        """Test chromaticity does not accept XYZ values."""

        with self.assertRaises(ValueError):
            Color('red').chromaticity('srgb', [0.33, 0.66], 'xyz')

    def test_split_chromaticity_no_xyz_value(self):
        """Test that split chromaticity does not convert to XYZ."""

        with self.assertRaises(ValueError):
            Color('red').split_chromaticity('xyz')

    def test_convert_xyz_bad_coordinates(self):
        """Test chromaticity conversion with XYZ values."""

        with self.assertRaises(ValueError):
            Color.convert_chromaticity('xyz', 'xy-1931', [0, 0])

        with self.assertRaises(ValueError):
            Color.convert_chromaticity('xyz', 'xy-1931', [0, 0, 0, 0])

    def test_convert_chromaticity_bad_coordinates(self):
        """Test chromaticity conversion with XYZ values."""

        with self.assertRaises(ValueError):
            Color.convert_chromaticity('xy-1931', 'xyz', [0])

        with self.assertRaises(ValueError):
            Color.convert_chromaticity('xy-1931', 'xyz', [0, 0, 0, 0])

    def test_convert_chromaticity_no_convert(self):
        """Test case when no conversion is needed."""

        self.assertEqual(Color.convert_chromaticity('xy-1931', 'xy-1931', [0.33, 0.36, 1.0]), [0.33, 0.36, 1.0])

    def test_convert_chromaticity_no_convert_no_luminance(self):
        """Test case when no conversion is needed and no luminance is provided."""

        self.assertEqual(Color.convert_chromaticity('xy-1931', 'xy-1931', [0.33, 0.36]), [0.33, 0.36, 1.0])
