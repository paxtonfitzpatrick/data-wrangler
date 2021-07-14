#!/usr/bin/env python

"""Tests for `datawrangler` package (format module)."""

import datawrangler as dw
import numpy as np
import pandas as pd

from dataloader import resources, data_file, img_file, text_file, data


def test_is_dataframe():
    assert dw.zoo.is_dataframe(data)
    assert dw.zoo.is_dataframe(pd.DataFrame(np.zeros([10, 3])))
    assert not dw.zoo.is_dataframe(img_file)
    assert not dw.zoo.is_dataframe(text_file)


def test_dataframe_like():
    assert dw.zoo.dataframe_like(data)
    assert not dw.zoo.dataframe_like(img_file)


def test_wrangle_dataframe():
    assert dw.zoo.is_dataframe(dw.zoo.wrangle_dataframe(data))

    df = dw.zoo.wrangle_dataframe(data)
    assert df.index.name == 'ByTwos'
    assert np.all(df['FirstDim'] == np.arange(1, 8))
    assert np.all(df['SecondDim'] == np.arange(2, 16, 2))
    assert np.all(df['ThirdDim'] == np.arange(3, 24, 3))
    assert np.all(df['FourthDim'] == np.arange(4, 32, 4))
    assert np.all(df['FifthDim'] == np.arange(5, 40, 5))


def test_is_array():
    assert dw.zoo.is_array(data.values)
    assert not dw.zoo.is_array(img_file)
    assert not dw.zoo.is_array(text_file)


def test_wrangle_array():
    df = dw.zoo.wrangle_array(data.values)
    assert dw.zoo.is_dataframe(df)
    assert df.shape == (7, 5)


def test_get_image():
    img = dw.zoo.image.get_image(img_file)
    assert img is not None
    assert img.shape == (1400, 1920, 3)
    assert np.max(img) == 248
    assert np.min(img) == 12
    assert np.isclose(np.mean(img), 152.193)


def test_is_image():
    assert dw.zoo.is_image(img_file)


def test_wrangle_image():
    df = dw.zoo.wrangle_image(img_file)
    assert df.shape == (1400, 5760)
    assert dw.zoo.is_dataframe(df)
    assert np.max(df.values) == 248
    assert np.min(df.values) == 12
    assert np.isclose(np.mean(df.values), 152.193)


def test_load_text():
    text = dw.io.load(text_file).split('\n')
    assert text[0] == 'O give me a home where the buffaloes roam'
    assert text[-1] == 'And the skies are not cloudy all day'


def test_is_text():
    assert dw.zoo.is_text(text_file)
    assert not dw.zoo.is_text(img_file)
    assert not dw.zoo.is_text(data_file)


def test_get_corpus():
    # test sotus corpus (small)
    sotus = dw.zoo.text.get_corpus('sotus')
    assert sotus[0].split('\n')[0] == 'Mr. Speaker, Mr. President, and distinguished Members of the House and ' \
                                      'Senate, honored guests, and fellow citizens:'
    assert sotus[0].split('\n')[-1] == 'Thank you. God bless you, and God bless America.'
    assert sotus[-1].split('\n')[0] == "Thank you very much. Mr. Speaker, Mr. Vice President, Members of Congress, " \
                                       "the First Lady of the United States, and citizens of America: Tonight, " \
                                       "as we mark the conclusion of our celebration of Black History Month, " \
                                       "we are reminded of our Nation's path towards civil rights and the work that " \
                                       "still remains to be done. Recent threats targeting Jewish community centers " \
                                       "and vandalism of Jewish cemeteries, as well as last week's shooting in " \
                                       "Kansas City, remind us that while we may be a nation divided on policies, " \
                                       "we are a country that stands united in condemning hate and evil in all of " \
                                       "its very ugly forms."
    assert sotus[-1].split('\n')[-1] == ''
    assert len(sotus) == 29

    # test small hugging face corpus: cbt/raw
    cbt = dw.zoo.text.get_corpus('cbt', 'raw')
    assert cbt[0][:100] == 'CHAPTER I. -LCB- Chapter heading picture : p1.jpg -RCB- How the Fairies were not Invited ' \
                           'to Court . '
    assert cbt[0][-104:] == "occasionally Rosalind would say , `` I do believe , my dear , that you are really as " \
                            "clever as ever ! ''"
    assert len(cbt[0]) == 98440
    assert len(cbt[100]) == 417432
    assert len(cbt) == 108


def test_wrangle_text_sklearn():
    text = dw.io.load(text_file).split('\n')

    # scikit-learn CountVectorizer
    text_kwargs = {'model': 'CountVectorizer'}
    cv = dw.wrangle(text, text_kwargs=text_kwargs)
    assert cv.shape == (24, 1220)
    assert dw.util.btwn(cv, 0, 1)

    # check text split into two documents
    i = 10
    cv2 = dw.wrangle([text[:i], text[i:]], text_kwargs=text_kwargs)
    assert np.allclose(cv[:i], cv2[0])
    assert np.allclose(cv[i:], cv2[1])

    # scikit-learn CountVectorizer + LatentDirichletAllocation
    text_kwargs = {'model': ['CountVectorizer', 'LatentDirichletAllocation']}
    lda = dw.wrangle(text, text_kwargs=text_kwargs)
    assert lda.shape == (24, 50)
    assert dw.util.btwn(lda, 0, 1)
    assert np.allclose(lda.sum(axis=1), 1)

    # scikit-learn TfidfVectorizer + NMF
    text_kwargs = {'model': ['TfidfVectorizer', {'model': 'NMF', 'args': [], 'kwargs': {'n_components': 25}}]}
    nmf = dw.wrangle(text, text_kwargs=text_kwargs)
    assert nmf.shape == (24, 25)
    assert dw.util.btwn(nmf, 0, 1)


def test_wrangle_text_hugging_face():
    text = dw.io.load(text_file).split('\n')
    words = [s.split() for s in text]

    glove_kwargs = {'model': {'model': 'WordEmbeddings', 'args': ['glove'], 'kwargs': {}}}
    glove_embeddings = dw.wrangle(words, text_kwargs=glove_kwargs)
    assert len(glove_embeddings) == 24
    assert all([a == b for a, b in zip([g.shape[0] for g in glove_embeddings], [len(w) for w in words])])
    assert all(g.shape[1] == 100 for g in glove_embeddings)
    assert np.allclose([g.values.mean() for g in glove_embeddings],
                       [-0.0025757, -0.0095522, -0.0250349, -0.0261115, +0.0083214, -0.0095522,
                        -0.0250349, -0.0261115, -0.0162621, -0.0142552, -0.0116034, -0.0279718,
                        +0.0083214, -0.0095522, -0.0250349, -0.0261115, -0.0308725, -0.0095388,
                        -0.0167642, -0.0208202, +0.0083214, -0.0095522, -0.0250349, -0.0261115])

    gpt2_kwargs = {'model': {'model': 'TransformerDocumentEmbeddings', 'args': ['gpt2'], 'kwargs': {}}}
    gpt2_embeddings = dw.wrangle(text, text_kwargs=gpt2_kwargs)
    assert gpt2_embeddings.shape == (24, 768)
    assert np.isclose(gpt2_embeddings.mean(axis=0).mean(axis=0), 0.399877)

    bert_kwargs = {'model': {'model': 'SentenceTransformerDocumentEmbeddings', 'args': ['bert-base-nli-mean-tokens'],
                             'kwargs': {}}}
    bert_embeddings = dw.wrangle(text, text_kwargs=bert_kwargs)
    assert bert_embeddings.shape == (24, 768)
    assert np.isclose(bert_embeddings.mean(axis=0).mean(axis=0), -0.018518)


def test_is_null():
    assert dw.zoo.is_null(None)
    assert dw.zoo.is_null('')
    assert dw.zoo.is_null([])
    assert dw.zoo.is_null([[]])
    assert dw.zoo.is_null([[], [[], [], [[], []]]])
    assert not dw.zoo.is_null([1, 2, 3, 4, 5])
    assert not dw.zoo.is_null('this should not be null')
    assert not dw.zoo.is_null([[], 'neither should', [['this'], []]])


def test_wrangle_null():
    df = dw.wrangle(None)
    assert dw.zoo.is_dataframe(df)
    assert len(df) == 0


# TODO:
#   x wrangle text with various models and corpora
#   x other text functions
#   x is_null
#   x wrangle_null
#   - decorators
#   - io
#   - ppca
#   - interpolation
#   - helper functions
#   - divide tests into separate files:
#      - one per datatype
#      - one per additional function beyond datatype-specific formatting
#   - depth
