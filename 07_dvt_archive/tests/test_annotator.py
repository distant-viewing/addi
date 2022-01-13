import pytest

from os.path import join

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from dvt import imread, SizeAnnotator, AverageAnnotator, ImwriteAnnotator


class TestSizeAnnotator:

    def test_size_annotator(self):
        im = imread(join("test-data", "2017810725.jpg"))
        anno = SizeAnnotator()
        output = anno.annotate(im)

        assert isinstance(output, dict)
        assert len(output) == 1
        assert isinstance(output['size'], DataFrame)
        assert output['size'].shape == (1, 2)
        assert output['size'].height.values[0] == im.shape[0]
        assert output['size'].width.values[0] == im.shape[1]


class TestAverageAnnotator:

    def test_average_annotator(self):
        im = imread(join("test-data", "2017810725.jpg"))
        anno = AverageAnnotator()
        output = anno.annotate(im)

        assert isinstance(output, dict)
        assert len(output) == 1
        assert isinstance(output['average'], DataFrame)
        assert output['average'].shape == (1, 2)
        assert output['average'].saturation.values[0] < 0.001
        assert output['average'].val.values[0] > 125
        assert output['average'].val.values[0] < 126
