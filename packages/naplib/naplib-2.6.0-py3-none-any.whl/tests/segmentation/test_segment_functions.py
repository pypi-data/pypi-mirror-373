import pytest
import numpy as np

from naplib.segmentation import get_label_change_points
from naplib.segmentation import segment_around_label_transitions
from naplib.segmentation import electrode_lags_fratio
from naplib.segmentation import shift_label_onsets
from naplib import Data

@pytest.fixture(scope='module')
def outstruct():
    labels1 = [np.array([0, 0, 1, 1, 1, 3, 3, 3]), np.array([-1, 2, 2, 0, 0, 0])]
    labels2 = [np.array([1, 2, 3, 4, 5, 6, 7, 8]), np.array([8, 7, 6, 6, 6, 6])]
    x = [np.arange(16,).reshape(-1,2), np.arange(12,).reshape(-1,2)]
    # [array([[ 0,  1],
    #    [ 2,  3],
    #    [ 4,  5],
    #    [ 6,  7],
    #    [ 8,  9],
    #    [10, 11],
    #    [12, 13],
    #    [14, 15]]),
    #  array([[ 0,  1],
    #    [ 2,  3],
    #    [ 4,  5],
    #    [ 6,  7],
    #    [ 8,  9],
    #    [10, 11]])]

    data_tmp = []
    for i in range(2):
        data_tmp.append({'resp': x[i], 'labels1': labels1[i], 'labels2': labels2[i]})
    return Data(data_tmp)

def test_label_change_points_simple():
    arr = np.array([0, 0, 0, 1, 1, 3, 3])
    locs, labels, prior_labels = get_label_change_points(arr)
    assert np.array_equal(locs, np.array([3,5]))
    assert np.array_equal(labels, np.array([1,3]))
    assert np.array_equal(prior_labels, np.array([0,1]))

def test_label_change_points_negatives():
    arr = np.array([100, 100, 100, -1, -1, 2, 2])
    locs, labels, prior_labels = get_label_change_points(arr)
    assert np.array_equal(locs, np.array([3,5]))
    assert np.array_equal(labels, np.array([-1,2]))
    assert np.array_equal(prior_labels, np.array([100,-1]))

def test_label_change_points_list_error():
    arr = [100, 100, 100, -1, -1, 2, 2]
    with pytest.raises(TypeError):
        _ = get_label_change_points(arr)

def test_label_change_points_1elem_array():
    arr = np.array([0])
    locs, labels, prior_labels = get_label_change_points(arr)
    assert np.array_equal(locs, np.array([]))
    assert np.array_equal(labels, np.array([]))
    assert np.array_equal(prior_labels, np.array([]))

def test_label_change_points_2elem_array():
    arr = np.array([-1, 2])
    locs, labels, prior_labels = get_label_change_points(arr)
    print((locs, labels, prior_labels))
    assert np.array_equal(locs, np.array(1))
    assert np.array_equal(labels, np.array(2))
    assert np.array_equal(prior_labels, np.array(-1))


# test segment_around_label_transitions

def test_single_label_segment_transitions_0prechange(outstruct):
    segments, labels, prior_labels = segment_around_label_transitions(
        field=outstruct['resp'],
        labels=outstruct['labels1'],
        prechange_samples=0,
        postchange_samples=2
    )
    expected = np.array([[[ 4,  5],
                          [ 6,  7]],
                         [[10, 11],
                          [12, 13]],
                         [[ 2,  3],
                          [ 4,  5]],
                         [[ 6,  7],
                          [ 8,  9]]])

    assert np.array_equal(segments, expected)
    assert np.array_equal(labels, np.array([1,3,2,0]))
    assert np.array_equal(prior_labels, np.array([0,1,-1,2]))

def test_single_label_segment_transitions_bigprechange(outstruct):
    segments, labels, prior_labels = segment_around_label_transitions(field=outstruct['resp'], labels=outstruct['labels1'],
                                                                      prechange_samples=3,
                                                                      postchange_samples=2)
    expected = np.array([[[ 4,  5],
                          [ 6,  7],
                          [ 8,  9],
                          [10, 11],
                          [12, 13]],
                         [[ 0,  1],
                          [ 2,  3],
                          [ 4,  5],
                          [ 6,  7],
                          [ 8,  9]]])
    assert np.array_equal(segments, expected)
    assert np.array_equal(labels, np.array([3,0]))
    assert np.array_equal(prior_labels, np.array([1,2]))

def test_single_label_segment_transitions_bigpostchange(outstruct):
    segments, labels, prior_labels = segment_around_label_transitions(field=outstruct['resp'], labels=outstruct['labels1'],
                                                                      prechange_samples=0,
                                                                      postchange_samples=6)
    expected = np.array([[[ 4,  5],
                          [ 6,  7],
                          [ 8,  9],
                          [10, 11],
                          [12, 13],
                          [14, 15]]])
    assert np.array_equal(segments, expected)
    assert np.array_equal(labels, np.array([1]))
    assert np.array_equal(prior_labels, np.array([0]))

def test_single_label_segment_transitions_withlags(outstruct):
    segments, labels, prior_labels = segment_around_label_transitions(field=outstruct['resp'], labels=outstruct['labels1'],
                                                                      prechange_samples=3,
                                                                      postchange_samples=1,
                                                                      elec_lag=np.array([1,2]))
    expected = np.array([[[ 6,  9],
                          [ 8, 11],
                          [10, 13],
                          [12, 15]],
                         [[ 2,  5],
                          [ 4,  7],
                          [ 6,  9],
                          [ 8, 11]]])
    assert np.array_equal(segments, expected)
    assert np.array_equal(labels, np.array([3,0]))
    assert np.array_equal(prior_labels, np.array([1,2]))

def test_single_label_segment_transitions_withlags_multiplelabels(outstruct):
    segments, labels, prior_labels = segment_around_label_transitions(field=outstruct['resp'], labels=(outstruct['labels1'], outstruct['labels2']),
                                                                      prechange_samples=3,
                                                                      postchange_samples=1,
                                                                      elec_lag=np.array([1,2]))
    expected = np.array([[[ 6,  9],
                          [ 8, 11],
                          [10, 13],
                          [12, 15]],
                         [[ 2,  5],
                          [ 4,  7],
                          [ 6,  9],
                          [ 8, 11]]])
    labs2_ex = np.array([[3, 4, 5, 6,], [8, 7, 6, 6]])
    assert np.array_equal(segments, expected)
    assert np.array_equal(labels[0], np.array([3,0]))
    assert np.array_equal(labels[1], labs2_ex)
    assert np.array_equal(prior_labels, np.array([1,2]))

def test_electrode_lags_fratio():
    rng = np.random.default_rng(1)
    labs = np.zeros(50,)
    labs[::2] = 1
    data = Data({'resp': [rng.uniform(size=(50,2))], 'lab': [labs]})
    lags, fratios = electrode_lags_fratio(
        data, field='resp', labels='lab', max_lag=3, return_fratios=True
    )
    assert np.allclose(lags, np.array([1,1]))
    assert np.allclose(fratios, np.array([[0.01886274, 0.11040603, 0.03642117],
                                          [0.44325853, 0.8626185,  0.70390361]])
    )

def test_electrode_lags_fratio_no_labels_or_field_passed():
    rng = np.random.default_rng(1)
    labs = np.zeros(50,)
    labs[::2] = 1
    data = Data({'resp': [rng.uniform(size=(50,2))], 'lab': [labs]})

    with pytest.raises(ValueError) as exc:
        _ = electrode_lags_fratio(data, field='resp', max_lag=3)
    assert 'None found in labels' in str(exc)

    with pytest.raises(ValueError) as exc:
        _ = electrode_lags_fratio(data, labels='lab', max_lag=3)
    assert 'None found in field' in str(exc)

## test shift_label_onsets
def test_shift_label_onsets_simple_50(outstruct):
    expected = [np.array([-1, 0, -1, 1, 1, -1, 3, 3]), np.array([-1, -1, 2, -1, 0, 0])]
    new_labels = shift_label_onsets(outstruct, labels='labels1', p=0.5)

    for lab, exp in zip(new_labels, expected):
        assert np.allclose(lab, exp)

def test_shift_label_onsets_simple_99(outstruct):
    expected = [np.array([-1, 0, -1, -1, 1, -1, -1, 3]), np.array([-1, -1, 2, -1, -1, 0])]
    new_labels = shift_label_onsets(outstruct, labels='labels1', p=0.99)

    for lab, exp in zip(new_labels, expected):
        assert np.allclose(lab, exp)

def test_shift_label_onsets_from_list():
    expected = [np.array([-1,-1,-1,-1,-1,3,3,-1,4,4,-1,-1,-1,-1,5,5,5])]
    labels = [np.array([-1,-1,-1,3,3,3,3,4,4,4,-1,-1,5,5,5,5,5])]
    new_labels = shift_label_onsets(labels=labels, p=0.5)

    for lab, exp in zip(new_labels, expected):
        assert np.allclose(lab, exp)

def test_shift_label_onsets_bad_p(outstruct):
    with pytest.raises(ValueError) as exc:
        _ = shift_label_onsets(outstruct, labels='labels1', p=-0.2)
    assert 'p must be in the range [0, 1)' in str(exc)

    with pytest.raises(ValueError) as exc:
        _ = shift_label_onsets(outstruct, labels='labels2', p=1)
    assert 'p must be in the range [0, 1)' in str(exc)

    with pytest.raises(ValueError) as exc:
        _ = shift_label_onsets(outstruct, labels='labels2', p=1.5)
    assert 'p must be in the range [0, 1)' in str(exc)
