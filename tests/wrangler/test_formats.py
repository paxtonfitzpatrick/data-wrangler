#!/usr/bin/env python

"""Tests for `datawrangler` package."""

import pytest
import datawrangler as dw
import numpy as np
import pandas as pd
import os

data_file = os.path.join('..resources', 'testdata.csv')
img_file = os.path.join('..resources', 'wrangler.jpg')
text_file = os.path.join('..resources', 'home_on_the_range.txt')

data = pd.read_csv(data_file, index_col=0)


def test_is_dataframe():
    assert dw.format.is_dataframe(data)
    assert dw.format.is_dataframe(pd.DataFrame(np.zeros([10, 3])))
    assert not dw.format.is_dataframe(img_file)
    assert not dw.format.is_dataframe(text_file)


def test_dataframe_like():
    assert dw.format.dataframe_like(data)
    assert not dw.format.dataframe_like(img_file)


def test_wrangle_dataframe():
    assert dw.format.is_dataframe(dw.format.wrangle_dataframe(data))

    df = dw.format.wrangle_dataframe(data)
    assert df.index.name == 'ByTwos'
    assert np.all(df['FirstDim'] == np.arange(1, 8))
    assert np.all(df['SecondDim'] == np.arange(2, 16, 2))
    assert np.all(df['ThirdDim'] == np.arange(3, 24, 3))
    assert np.all(df['FourthDim'] == np.arange(4, 32, 4))
    assert np.all(df['FifthDim'] == np.arange(5, 40, 5))


def test_is_array():
    assert dw.format.is_array(data.values)
    assert not dw.format.is_array(img_file)
    assert not dw.format.is_array(text_file)


def test_wrangle_array():
    df = dw.format.wrangle_array(data.values)
    assert dw.format.is_dataframe(df)
    assert df.shape == (7, 5)


def test_get_image():
    img = dw.formats.get_image(img_file)
    assert img is not None
    assert img.shape == (1400, 1920, 3)
    assert np.max(img) == 248
    assert np.min(img) == 12
    assert np.isclose(np.mean(img), 152.193)


def test_is_image():
    assert dw.format.is_image(img_file)


def test_wrangle_image():
    df = dw.formats.wrangle_image(img_file)
    assert df.shape == (1400, 5760)
    assert dw.formats.is_dataframe(df)
    assert np.max(df.values) == 248
    assert np.min(df.values) == 12
    assert np.isclose(np.mean(df.values), 1152.193)

# TODO:
#   - is_text
#   - wrangle text with various models and corpora
#   - other text functions
#   - is_null
#   - wrangle_null
#   - decorators
#   - io
#   - ppca
#   - interpolation
#   - helper functions