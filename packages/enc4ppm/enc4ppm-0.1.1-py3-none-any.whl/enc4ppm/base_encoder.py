import os
import pickle
import pprint
from abc import ABC, abstractmethod
import pandas as pd
from pandas.api.types import is_numeric_dtype

from .constants import LabelingType, CategoricalEncoding, PrefixStrategy

class BaseEncoder(ABC):
    ORIGINAL_INDEX_KEY = 'OriginalIndex'
    EVENT_COL_PREFIX_NAME = 'event'
    LATEST_PAYLOAD_COL_SUFFIX_NAME = 'latest'
    LABEL_KEY = 'label'
    UNKNOWN_VAL = 'UNKNOWN'
    PADDING_CAT_VAL = 'PADDING'
    PADDING_NUM_VAL = 0.0
    
    def __init__(
        self,
        labeling_type: LabelingType = LabelingType.NEXT_ACTIVITY,
        attributes: list[str] | str = [],
        categorical_encoding: CategoricalEncoding = CategoricalEncoding.STRING,
        prefix_length: int = None,
        prefix_strategy: PrefixStrategy = PrefixStrategy.UP_TO_SPECIFIED,
        timestamp_format: str = None,
        case_id_key: str = 'case:concept:name',
        activity_key: str = 'concept:name',
        timestamp_key: str = 'time:timestamp',
        outcome_key: str = 'outcome',
    ) -> None:
        self.labeling_type = labeling_type
        self.attributes = attributes
        self.categorical_encoding = categorical_encoding
        self.prefix_length = prefix_length
        self.prefix_strategy = prefix_strategy
        self.timestamp_format = timestamp_format
        self.case_id_key = case_id_key
        self.activity_key = activity_key
        self.timestamp_key = timestamp_key
        self.outcome_key = outcome_key

        # Instance variables
        self.is_frozen: bool = False
        self.original_df: pd.DataFrame = pd.DataFrame()
        self.log_activities: list[str] = []
        self.log_attributes: dict[str, dict[str, str | list | dict]] = {}


    @abstractmethod
    def _encode(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        The _encode abstract method must be defined by subclasses and must contain the specific encoding logic of the encoder.
        In particular, the _encode implementation must create the necessary columns for the specific encoding + add the ORIGINAL_INDEX_KEY column.
        The _encode method must not filter rows (events), but instead return them all: the BaseEncoder will then _apply_prefix_strategy to filter them.
        """
        pass

    
    def _encode_template(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        The _encode_template method is a template method which performs both common operations shared amongs all encoders and the specific logic of each encoder.
        In particular, common operations are: _preprocess_log, _label_log, _apply_prefix_strategy and _postprocess_log; specific encoding is performed by the _encode method.
        """
        self.original_df = df
        
        self._check_log(df)
        self._check_parameters(df)
        df = self._preprocess_log(df)
        
        if not self.is_frozen:
            self._extract_log_data(df)

        if 'freeze' in kwargs and kwargs['freeze']:
            self.is_frozen = True

        encoded_df = self._encode(df)

        if self.ORIGINAL_INDEX_KEY not in encoded_df.columns:
            raise ValueError(f'You must include {self.ORIGINAL_INDEX_KEY} column when implementing your own custom encoder!')

        encoded_df = self._label_log(encoded_df)
        encoded_df = self._apply_prefix_strategy(encoded_df)
        encoded_df = self._postprocess_log(encoded_df)

        return encoded_df
    

    def _check_log(self, df: pd.DataFrame) -> None:
        """
        Checks and validations on input log.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        
        if df.empty:
            raise ValueError("df cannot be empty")
        
        for col in [self.case_id_key, self.activity_key, self.timestamp_key]:
            if col not in df.columns:
                raise ValueError(f"df must contain column '{col}'")


    def _check_parameters(self, df: pd.DataFrame) -> None:
        """
        Checks and validations on encoder parameters.
        """
        # Labeling type
        if not isinstance(self.labeling_type, LabelingType):
            raise TypeError(f'labeling_type must be a valid LabelingType: {[e.name for e in LabelingType]}')
        
        if self.labeling_type == LabelingType.OUTCOME and (self.outcome_key is None or self.outcome_key not in df.columns):
            raise ValueError("If labeling_type is set to OUTCOME, then you must specify the outcome_key parameter and it must be present in the DataFrame")
        
        # Attributes
        if not isinstance(self.attributes, str) and not isinstance(self.attributes, list):
            raise ValueError(f'attributes must be either a list of strings or the string "all"')

        if isinstance(self.attributes, str) and self.attributes != 'all':
            raise ValueError("Since attributes is set to a string, then it must be set to the value 'all'. Otherwise, set it to a list of strings indicating the attributes you want to consider.")
        
        if isinstance(self.attributes, list):
            for attribute in self.attributes:
                if not isinstance(attribute, str):
                    raise ValueError('Since attributes is a list, it must contain only string elements')
                
                if attribute not in self.original_df.columns:
                    raise ValueError(f"attributes contains value '{attribute}', which cannot be found in the log")
        
        # Prefix length and strategy
        if self.prefix_length is not None and (not isinstance(self.prefix_length, int) or self.prefix_length <= 0):
            raise ValueError(f'prefix_length must be either None or a positive integer ({self.prefix_length} has been provided instead)')
        
        if self.prefix_length is None and self.prefix_strategy == PrefixStrategy.ONLY_SPECIFIED:
            raise ValueError(f'If prefix strategy is set to ONLY_SPECIFIED, then you must specify the prefix_length parameter')
        
        if not isinstance(self.prefix_strategy, PrefixStrategy):
            raise TypeError(f'prefix_strategy must be a valid PrefixStrategy: {[e.name for e in PrefixStrategy]}')


    def _preprocess_log(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Common preprocessing logic shared by all encoders.
        """
        # Cast timestamp column to datetime
        df.loc[:, self.timestamp_key] = pd.to_datetime(df[self.timestamp_key], format=self.timestamp_format)

        # Change null values to UNKNOWN_VAL or 0, based on their type
        fill_dict = {}

        for col in df.select_dtypes(include=['object', 'category']).columns:
            fill_dict[col] = self.UNKNOWN_VAL

        for col in df.select_dtypes(include=['number']).columns:
            fill_dict[col] = 0

        df = df.fillna(fill_dict)

        return df


    def _extract_log_data(self, df: pd.DataFrame) -> None:
        """
        From log data, create necessary variables for later use (e.g: determines prefix length, build activity and attribute vocabs, etc.)
        """
        # Set prefix length
        max_prefix_length_log = df.groupby(self.case_id_key).size().max().item()

        if self.prefix_length is None:
            self.prefix_length = max_prefix_length_log

        # Build activity vocab
        self.log_activities = df[self.activity_key].unique().tolist() + [self.UNKNOWN_VAL] + [self.PADDING_CAT_VAL]

        # Build attribute vocabs
        if self.attributes == 'all':
            self.attributes = [a for a in df.columns.tolist() if a not in [self.case_id_key, self.activity_key, self.timestamp_key]]
            
        for attribute_name in self.attributes:
            attribute_values = df[attribute_name].unique()

            is_numeric = is_numeric_dtype(attribute_values)
            is_static = df.groupby(self.case_id_key)[attribute_name].nunique().eq(1).all()

            attribute_dict = {
                'type': 'numerical' if is_numeric else 'categorical',
                'scope': 'trace' if is_static else 'event',
            }

            if is_numeric_dtype(attribute_values):
                attribute_dict['values'] = {
                    'min': attribute_values.min().item(),
                    'max': attribute_values.max().item(),
                    'mean': attribute_values.mean().item(),
                }
            else:
                attribute_values = attribute_values[attribute_values != self.UNKNOWN_VAL] # remove UNKNOWN_VAL if present, because it'll be added anyway
                attribute_dict['values'] = attribute_values.tolist() + [self.UNKNOWN_VAL] + [self.PADDING_CAT_VAL]
                
            self.log_attributes[attribute_name] = attribute_dict

    
    def _label_log(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Common logic shared by all encoders. The method labels the provided log with the provided LabelingType.
        """
        if self.ORIGINAL_INDEX_KEY not in df.columns:
            raise ValueError(f'You must include {self.ORIGINAL_INDEX_KEY} column into df before calling _label_log')
        
        # Sort by case and timestamp
        df = df.sort_values([self.case_id_key, self.timestamp_key], ascending=[True, True]).reset_index(drop=True)

        if self.labeling_type == LabelingType.NEXT_ACTIVITY:
            # Get the next ORIGINAL_INDEX_KEY per case
            df['next_index'] = df.groupby(self.case_id_key)[self.ORIGINAL_INDEX_KEY].shift(-1)

            # Map next_index to activity in original_df
            df[self.LABEL_KEY] = df['next_index'].map(
                lambda idx: self._get_activity_value(self.original_df.at[idx, self.activity_key]) if pd.notna(idx) else None
            )
            
            # Drop the helper column
            df = df.drop(columns=['next_index'])

        elif self.labeling_type == LabelingType.REMAINING_TIME:
            # Get the last timestamp for each case
            last_timestamp_per_case = df.groupby(self.case_id_key)[self.timestamp_key].transform('max')

            # Compute remaining time in hours
            df[self.LABEL_KEY] = (last_timestamp_per_case - df[self.timestamp_key]).dt.total_seconds() / 60 / 60

        elif self.labeling_type == LabelingType.OUTCOME:
            # Get outcome for each case (from original_df)
            df[self.LABEL_KEY] = df[self.ORIGINAL_INDEX_KEY].map(self.original_df[self.outcome_key])

        return df
    
    
    def _apply_prefix_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Common logic shared by all encoders. The method filters the log with respect to specified prefix_length value.
        """
        # Compute event number in case (starting from 1)
        df = df.sort_values([self.case_id_key, self.timestamp_key], ascending=[True, True]).reset_index(drop=True)
        df['event_num_in_case'] = df.groupby(self.case_id_key).cumcount() + 1

        if self.prefix_strategy == PrefixStrategy.UP_TO_SPECIFIED:
            filtered_df = df[df['event_num_in_case'] <= self.prefix_length]
        elif self.prefix_strategy == PrefixStrategy.ONLY_SPECIFIED:
            filtered_df = df[df['event_num_in_case'] == self.prefix_length]
        else:
            filtered_df = df

        # Drop the helper column
        filtered_df = filtered_df.drop(columns=['event_num_in_case'])

        return filtered_df


    def _postprocess_log(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Common postprocessing logic shared by all encoders. The method restores original ordering and drops unnecessary data.
        """
        # Restore original ordering
        df = df.sort_values(by=self.ORIGINAL_INDEX_KEY).reset_index(drop=True)

        # Drop unnecessary data
        df = df.drop(columns=[self.timestamp_key, self.ORIGINAL_INDEX_KEY])
        df = df.dropna(subset=[self.LABEL_KEY]).reset_index(drop=True)

        return df

    
    def _include_latest_payload(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add latest payload attributes to encoded DataFrame. 
        """
        if self.attributes == [] or self.attributes is None:
            return df
        
        if self.ORIGINAL_INDEX_KEY not in df.columns:
            raise ValueError(f'You must include {self.ORIGINAL_INDEX_KEY} column into df before calling _include_latest_payload')

        # Add latest payload of specified attributes to the dataframe
        for attribute_name in self.attributes:
            attribute_values = []
            
            for _, row in df.iterrows():
                attribute_values.append(
                    self._get_attribute_value(attribute_name, self.original_df.loc[row[self.ORIGINAL_INDEX_KEY], attribute_name])
                )

            df[f'{attribute_name}_{self.LATEST_PAYLOAD_COL_SUFFIX_NAME}'] = attribute_values

        return df

    
    def _get_activity_value(self, activity_value: str) -> str:
        """
        Return specified activity_value if present in self.log_activities, otherwise a string representing unknown activity.
        """
        if activity_value in self.log_activities:
            return activity_value
            
        return self.UNKNOWN_VAL
    

    def _get_attribute_value(self, attribute_name: str, attribute_value: str) -> str:
        """
        Return specified attribute_value if present in self.log_attributes under attribute_name, otherwise a string representing unknown attribute.
        """
        if attribute_name not in self.log_attributes:
            raise ValueError(f'Attribute {attribute_name} not found in log attributes {list(self.log_attributes.keys())}')
        
        # Numerical attribute
        if self.log_attributes[attribute_name]['type'] == 'numerical':
            return attribute_value
        
        # Categorical attribute
        if attribute_value in self.log_attributes[attribute_name]['values']:
            return attribute_value
        
        return self.UNKNOWN_VAL
        
    
    def summary(self) -> None:
        """
        Print a summary of the encoder. Only works if the encoder has been frozen.
        """
        if not self.is_frozen:
            raise RuntimeError("Encoder must be frozen before summarizing.")

        # Print a summary of the encoder's configuration and learned parameters
        print("Encoder Summary:")
        print(f" - Encoder Type: {self.__class__.__name__}")
        print(f" - Labeling Type: {self.labeling_type}")
        print(f" - Categorical Encoding: {self.categorical_encoding}")
        print(f" - Prefix Length: {self.prefix_length}")
        print(f" - Prefix Strategy: {self.prefix_strategy}")
        print(f" - Timestamp Format: {self.timestamp_format}")
        print(f" - Case ID Key: {self.case_id_key}")
        print(f" - Activity Key: {self.activity_key}")
        print(f" - Timestamp Key: {self.timestamp_key}")
        print(f" - Log Activities ({len(self.log_activities)}): {self.log_activities}")
        print(f" - Log Attributes ({len(self.log_attributes)}):")
        pprint.pprint(self.log_attributes)


    def save(self, filepath: str) -> None:
        """
        Save the encoder instance to a pickle file. Only works if the encoder has been frozen.

        Args:
            filepath (str): Path to the pickle file where the encoder will be saved.
        """
        if not self.is_frozen:
            raise RuntimeError("Encoder must be frozen before saving. Call with freeze=True during encoding.")
        
        # Do not save original_df
        self.original_df = None
        
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    
    @classmethod
    def load(cls, filepath: str):
        """
        Load a frozen encoder instance from a pickle file.

        Args:
            filepath (str): Path to the pickle file to load.

        Returns:
            BaseEncoder: The loaded encoder instance.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")
        
        with open(filepath, 'rb') as f:
            encoder = pickle.load(f)
        
        if not isinstance(encoder, cls):
            raise TypeError(f"Loaded object is not an instance of {cls.__name__}")
        
        return encoder
