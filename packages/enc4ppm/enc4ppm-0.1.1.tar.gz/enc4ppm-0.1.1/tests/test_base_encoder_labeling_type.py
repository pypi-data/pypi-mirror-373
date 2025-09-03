import os
import pytest
import pandas as pd

from src.enc4ppm.frequency_encoder import FrequencyEncoder
from src.enc4ppm.constants import LabelingType
from tests.data.dummy_log_info import *

@pytest.fixture
def log():
    log_path = os.path.join(os.path.dirname(__file__), 'data', TEST_LOG_NAME)
    return pd.read_csv(log_path)


@pytest.fixture
def gt_encoded_log_next_activity():
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
def gt_encoded_log_remaining_time():
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
            'label': 50.0,
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
            'label': 42.0,
        },
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 0.0,
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
            'label': 68.5,
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
            'label': 63.0,
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
            'label': 22.5,
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 0,
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
            'label': 191.0,
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
            'label': 187.75,
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
            'label': 172.0,
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
            'label': 28.0,
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 1,
            'Issue Refund': 1,
            'label': 0.0,
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
            'label': 52.0,
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
            'label': 46.0,
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': 0.0,
        },
    ]

@pytest.fixture
def gt_encoded_log_outcome():
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
            'label': False,
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
            'label': False,
        },
        {
            CASE_ID_KEY: 'Case001',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': False,
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
            'label': False,
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
            'label': False,
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
            'label': False,
        },
        {
            CASE_ID_KEY: 'Case002',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 1,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': False,
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
            'label': True,
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
            'label': True,
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
            'label': True,
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
            'label': True,
        },
        {
            CASE_ID_KEY: 'Case003',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 1,
            'Issue Refund': 1,
            'label': True,
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
            'label': False,
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
            'label': False,
        },
        {
            CASE_ID_KEY: 'Case004',
            UNKNOWN_VAL: 0,
            'Receive Order': 1,
            'Ship': 1,
            'Receive Payment': 1,
            'Contact Supplier': 0,
            'Order Returned': 0,
            'Issue Refund': 0,
            'label': False,
        },
    ]


def test_next_activity(log, gt_encoded_log_next_activity):
    frequency_encoder = FrequencyEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log_next_activity) == len(encoded_log)
    assert len(gt_encoded_log_next_activity[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_next_activity)):
        assert gt_encoded_log_next_activity[i] == encoded_log[i]


def test_remaining_time(log, gt_encoded_log_remaining_time):
    frequency_encoder = FrequencyEncoder(
        labeling_type=LabelingType.REMAINING_TIME,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log_remaining_time) == len(encoded_log)
    assert len(gt_encoded_log_remaining_time[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_remaining_time)):
        assert gt_encoded_log_remaining_time[i] == encoded_log[i]


def test_outcome(log, gt_encoded_log_outcome):
    frequency_encoder = FrequencyEncoder(
        labeling_type=LabelingType.OUTCOME,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
        outcome_key='Outcome',
    )
    encoded_log = frequency_encoder.encode(log)

    assert len(gt_encoded_log_outcome) == len(encoded_log)
    assert len(gt_encoded_log_outcome[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_outcome)):
        assert gt_encoded_log_outcome[i] == encoded_log[i]
