import os
import pytest
import pandas as pd

from src.enc4ppm.frequency_encoder import FrequencyEncoder
from src.enc4ppm.constants import LabelingType, CategoricalEncoding
from tests.data.dummy_log_info import *

@pytest.fixture
def log():
    log_path = os.path.join(os.path.dirname(__file__), 'data', TEST_LOG_NAME)
    return pd.read_csv(log_path)

@pytest.fixture
def gt_encoded_log():
    return [
        # Case001
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Receive Payment',
        },
        # Case002
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Contact Supplier',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Receive Payment',
        },
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Order Returned',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 1,
            'Issue Refund': 0,
            'label': 'Issue Refund',
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 'Receive Payment',
        },
    ]

@pytest.fixture
def gt_encoded_log_latest_payload():
    return [
        # Case001
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        # Case002
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerB',
            'Amount_latest': 0,
            'label': 'Contact Supplier',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerB',
            'Amount_latest': -20,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerB',
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 300,
            'label': 'Order Returned',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 1,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Issue Refund',
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerC',
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest': 'CustomerC',
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
    ]


@pytest.fixture
def gt_encoded_log_onehot_latest_payload():
    return [
        # Case001
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        # Case002
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': True,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Contact Supplier',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': True,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': -20,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': True,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
                # Case003
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 300,
            'label': 'Order Returned',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 1,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Issue Refund',
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': True,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': False,
            'Customer_latest_CustomerC': True,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
 
    ]


@pytest.fixture
def gt_encoded_log_unknown_values():
    # Supposing Case001+Case002 are training log and Case003+Case004 are test log
    return [
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'label': UNKNOWN_VAL,
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 1,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'label': UNKNOWN_VAL,
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'label': 'Receive Payment',
        },
    ]


@pytest.fixture
def gt_encoded_log_latest_payload_unknown_values():
    # Supposing Case001+Case002 are training log and Case003+Case004 are test log
    return [
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 300,
            'label': UNKNOWN_VAL,
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 1,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Customer_latest': 'CustomerA',
            'Amount_latest': 0,
            'label': UNKNOWN_VAL,
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest': UNKNOWN_VAL,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest': UNKNOWN_VAL,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
    ]


@pytest.fixture
def gt_encoded_log_onehot_latest_payload_unknown_values():
    # Supposing Case001+Case002 are training log and Case003+Case004 are test log
    return [
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 300,
            'label': UNKNOWN_VAL,
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 1,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': True,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': False,
            'Amount_latest': 0,
            'label': UNKNOWN_VAL,
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 0,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': True,
            'Amount_latest': 0,
            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 0,
            'Contact Supplier': 0,
            'Customer_latest_CustomerA': False,
            'Customer_latest_CustomerB': False,
            'Customer_latest_UNKNOWN': True,
            'Amount_latest': 0,
            'label': 'Receive Payment',
        },
    ]


def test_frequency_encoder(log, gt_encoded_log):
    frequency_encoder = FrequencyEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log) == len(encoded_log)
    assert len(gt_encoded_log[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log)):
        assert gt_encoded_log[i] == encoded_log[i]


def test_frequency_encoder_latest_payload(log, gt_encoded_log_latest_payload):
    frequency_encoder = FrequencyEncoder(
        include_latest_payload=True,
        labeling_type=LabelingType.NEXT_ACTIVITY,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.STRING,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log_latest_payload) == len(encoded_log)
    assert len(gt_encoded_log_latest_payload[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_latest_payload)):
        assert gt_encoded_log_latest_payload[i] == encoded_log[i]


def test_frequency_encoder_onehot_latest_payload(log, gt_encoded_log_onehot_latest_payload):
    frequency_encoder = FrequencyEncoder(
        include_latest_payload=True,
        labeling_type=LabelingType.NEXT_ACTIVITY,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.ONE_HOT,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log_onehot_latest_payload) == len(encoded_log)
    assert len(gt_encoded_log_onehot_latest_payload[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_onehot_latest_payload)):
        assert gt_encoded_log_onehot_latest_payload[i] == encoded_log[i]


def test_frequency_encoder_unknown_values(log, gt_encoded_log_unknown_values):
    frequency_encoder = FrequencyEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    train_log = log[log[CASE_ID_KEY].isin(['Case001', 'Case002'])].copy()
    test_log = log[log[CASE_ID_KEY].isin(['Case003', 'Case004'])].copy()

    _ = frequency_encoder.encode(train_log, freeze=True)
    encoded_test_log = frequency_encoder.encode(test_log)

    assert len(gt_encoded_log_unknown_values) == len(encoded_test_log)
    assert len(gt_encoded_log_unknown_values[0]) == len(encoded_test_log.columns)

    encoded_test_log = encoded_test_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_unknown_values)):
        assert gt_encoded_log_unknown_values[i] == encoded_test_log[i]


def test_frequency_encoder_latest_payload_unknown_values(log, gt_encoded_log_latest_payload_unknown_values):
    frequency_encoder = FrequencyEncoder(
        include_latest_payload=True,
        labeling_type=LabelingType.NEXT_ACTIVITY,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.STRING,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    train_log = log[log[CASE_ID_KEY].isin(['Case001', 'Case002'])].copy()
    test_log = log[log[CASE_ID_KEY].isin(['Case003', 'Case004'])].copy()

    _ = frequency_encoder.encode(train_log, freeze=True)
    encoded_test_log = frequency_encoder.encode(test_log)

    assert len(gt_encoded_log_latest_payload_unknown_values) == len(encoded_test_log)
    assert len(gt_encoded_log_latest_payload_unknown_values[0]) == len(encoded_test_log.columns)

    encoded_test_log = encoded_test_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_latest_payload_unknown_values)):
        assert gt_encoded_log_latest_payload_unknown_values[i] == encoded_test_log[i]


def test_frequency_encoder_onehot_latest_payload_unknown_values(log, gt_encoded_log_onehot_latest_payload_unknown_values):
    frequency_encoder = FrequencyEncoder(
        include_latest_payload=True,
        labeling_type=LabelingType.NEXT_ACTIVITY,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.ONE_HOT,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    train_log = log[log[CASE_ID_KEY].isin(['Case001', 'Case002'])].copy()
    test_log = log[log[CASE_ID_KEY].isin(['Case003', 'Case004'])].copy()

    _ = frequency_encoder.encode(train_log, freeze=True)
    encoded_test_log = frequency_encoder.encode(test_log)

    assert len(gt_encoded_log_onehot_latest_payload_unknown_values) == len(encoded_test_log)
    assert len(gt_encoded_log_onehot_latest_payload_unknown_values[0]) == len(encoded_test_log.columns)

    encoded_test_log = encoded_test_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_onehot_latest_payload_unknown_values)):
        assert gt_encoded_log_onehot_latest_payload_unknown_values[i] == encoded_test_log[i]
