import os
import pytest
import pandas as pd

from src.enc4ppm.complex_index_encoder import ComplexIndexEncoder
from src.enc4ppm.constants import LabelingType, CategoricalEncoding, PrefixStrategy
from tests.data.dummy_log_info import *

PREFIX_LENGTH = 5

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
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case001',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': 0,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        # Case002
        {
            CASE_ID_KEY: 'Case002',
            'Customer': 'CustomerB',

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Contact Supplier',
        },
        {
            CASE_ID_KEY: 'Case002',
            'Customer': 'CustomerB',

            'event_1': 'Receive Order',
            'event_2': 'Contact Supplier',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': -20,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case002',
            'Customer': 'CustomerB',

            'event_1': 'Receive Order',
            'event_2': 'Contact Supplier',
            'event_3': 'Ship',
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': -20,
            'Amount_3': 0,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        # Case003
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': 0,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': 'Receive Payment',
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': 0,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Order Returned',
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': 'Receive Payment',
            'event_4': 'Order Returned',
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': 0,
            'Amount_3': 300,
            'Amount_4': 0,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Issue Refund',
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            'Customer': 'CustomerC',

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            'Customer': 'CustomerC',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': 0,
            'Amount_2': 0,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
    ]


@pytest.fixture
def gt_encoded_log_onehot():
    return [
        # Case001
        {
            'CaseID': 'Case001',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case001',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        # Case002
        {
            'CaseID': 'Case002',

            'Customer_CustomerA': False,
            'Customer_CustomerB': True,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Contact Supplier',
        },
        {
            'CaseID': 'Case002',

            'Customer_CustomerA': False,
            'Customer_CustomerB': True,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': True,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': -20,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case002',

            'Customer_CustomerA': False,
            'Customer_CustomerB': True,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': True,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': True,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': False,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': -20,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        # Case003
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': True,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': False,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Order Returned',
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_CustomerC': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': True,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': False,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': True,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': False,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Issue Refund',
        },
        # Case004
        {
            'CaseID': 'Case004',

            'Customer_CustomerA': False,
            'Customer_CustomerB': False,
            'Customer_CustomerC': True,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case004',

            'Customer_CustomerA': False,
            'Customer_CustomerB': False,
            'Customer_CustomerC': True,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_Order Returned': False,
            'event_1_Issue Refund': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_Order Returned': False,
            'event_2_Issue Refund': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_Order Returned': False,
            'event_3_Issue Refund': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_Order Returned': False,
            'event_4_Issue Refund': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_Order Returned': False,
            'event_5_Issue Refund': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

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
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': 'Receive Payment',
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': UNKNOWN_VAL,
        },
        {
            CASE_ID_KEY: 'Case003',
            'Customer': 'CustomerA',

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': 'Receive Payment',
            'event_4': UNKNOWN_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': UNKNOWN_VAL,
        },
        # Case004
        {
            CASE_ID_KEY: 'Case004',
            'Customer': UNKNOWN_VAL,

            'event_1': 'Receive Order',
            'event_2': PADDING_CAT_VAL,
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            CASE_ID_KEY: 'Case004',
            'Customer': UNKNOWN_VAL,

            'event_1': 'Receive Order',
            'event_2': 'Ship',
            'event_3': PADDING_CAT_VAL,
            'event_4': PADDING_CAT_VAL,
            'event_5': PADDING_CAT_VAL,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
    ]


@pytest.fixture
def gt_encoded_log_onehot_unknown_values():
    # Supposing Case001+Case002 are training log and Case003+Case004 are test log
        return [
        # Case003
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': True,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': False,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': UNKNOWN_VAL,
        },
        {
            'CaseID': 'Case003',

            'Customer_CustomerA': True,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': False,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': True,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': False,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': True,
            'event_4_PADDING': False,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': 300,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': UNKNOWN_VAL,
        },
        # Case004
        {
            'CaseID': 'Case004',

            'Customer_CustomerA': False,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': True,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': False,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': True,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Ship',
        },
        {
            'CaseID': 'Case004',

            'Customer_CustomerA': False,
            'Customer_CustomerB': False,
            'Customer_UNKNOWN': True,

            'event_1_Receive Order': True,
            'event_1_Ship': False,
            'event_1_Receive Payment': False,
            'event_1_Contact Supplier': False,
            'event_1_UNKNOWN': False,
            'event_1_PADDING': False,

            'event_2_Receive Order': False,
            'event_2_Ship': True,
            'event_2_Receive Payment': False,
            'event_2_Contact Supplier': False,
            'event_2_UNKNOWN': False,
            'event_2_PADDING': False,

            'event_3_Receive Order': False,
            'event_3_Ship': False,
            'event_3_Receive Payment': False,
            'event_3_Contact Supplier': False,
            'event_3_UNKNOWN': False,
            'event_3_PADDING': True,

            'event_4_Receive Order': False,
            'event_4_Ship': False,
            'event_4_Receive Payment': False,
            'event_4_Contact Supplier': False,
            'event_4_UNKNOWN': False,
            'event_4_PADDING': True,

            'event_5_Receive Order': False,
            'event_5_Ship': False,
            'event_5_Receive Payment': False,
            'event_5_Contact Supplier': False,
            'event_5_UNKNOWN': False,
            'event_5_PADDING': True,

            'Amount_1': PADDING_NUM_VAL,
            'Amount_2': PADDING_NUM_VAL,
            'Amount_3': PADDING_NUM_VAL,
            'Amount_4': PADDING_NUM_VAL,
            'Amount_5': PADDING_NUM_VAL,

            'label': 'Receive Payment',
        },
    ]


def test_complex_index_encoder(log, gt_encoded_log):
    complex_index_encoder = ComplexIndexEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        prefix_length=PREFIX_LENGTH,
        prefix_strategy=PrefixStrategy.UP_TO_SPECIFIED,
        attributes=['Customer', 'Amount'],
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = complex_index_encoder.encode(log)

    assert len(gt_encoded_log) == len(encoded_log)
    assert len(gt_encoded_log[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log)):
        assert gt_encoded_log[i] == encoded_log[i]


def test_complex_index_encoder_onehot(log, gt_encoded_log_onehot):
    complex_index_encoder = ComplexIndexEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        prefix_length=PREFIX_LENGTH,
        prefix_strategy=PrefixStrategy.UP_TO_SPECIFIED,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.ONE_HOT,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )
    encoded_log = complex_index_encoder.encode(log)

    assert len(gt_encoded_log_onehot) == len(encoded_log)
    assert len(gt_encoded_log_onehot[0]) == len(encoded_log.columns)

    encoded_log = encoded_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_onehot)):
        assert gt_encoded_log_onehot[i] == encoded_log[i]


def test_complex_index_encoder_unknown_values(log, gt_encoded_log_unknown_values):
    complex_index_encoder = ComplexIndexEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        prefix_length=PREFIX_LENGTH,
        prefix_strategy=PrefixStrategy.UP_TO_SPECIFIED,
        attributes=['Customer', 'Amount'],
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )

    train_log = log[log[CASE_ID_KEY].isin(['Case001', 'Case002'])].copy()
    test_log = log[log[CASE_ID_KEY].isin(['Case003', 'Case004'])].copy()

    _ = complex_index_encoder.encode(train_log, freeze=True)
    encoded_test_log = complex_index_encoder.encode(test_log)

    assert len(gt_encoded_log_unknown_values) == len(encoded_test_log)
    assert len(gt_encoded_log_unknown_values[0]) == len(encoded_test_log.columns)

    encoded_test_log = encoded_test_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_unknown_values)):
        assert gt_encoded_log_unknown_values[i] == encoded_test_log[i]


def test_complex_index_encoder_onehot_unknown_values(log, gt_encoded_log_onehot_unknown_values):
    complex_index_encoder = ComplexIndexEncoder(
        labeling_type=LabelingType.NEXT_ACTIVITY,
        prefix_length=PREFIX_LENGTH,
        prefix_strategy=PrefixStrategy.UP_TO_SPECIFIED,
        attributes=['Customer', 'Amount'],
        categorical_encoding=CategoricalEncoding.ONE_HOT,
        timestamp_format=TIMESTAMP_FORMAT,
        case_id_key=CASE_ID_KEY,
        activity_key=ACTIVITY_KEY,
        timestamp_key=TIMESTAMP_KEY,
    )

    train_log = log[log[CASE_ID_KEY].isin(['Case001', 'Case002'])].copy()
    test_log = log[log[CASE_ID_KEY].isin(['Case003', 'Case004'])].copy()

    _ = complex_index_encoder.encode(train_log, freeze=True)
    encoded_test_log = complex_index_encoder.encode(test_log)

    assert len(gt_encoded_log_onehot_unknown_values) == len(encoded_test_log)
    assert len(gt_encoded_log_onehot_unknown_values[0]) == len(encoded_test_log.columns)

    encoded_test_log = encoded_test_log.to_dict(orient='records')
    for i in range(len(gt_encoded_log_onehot_unknown_values)):
        assert gt_encoded_log_onehot_unknown_values[i] == encoded_test_log[i]
