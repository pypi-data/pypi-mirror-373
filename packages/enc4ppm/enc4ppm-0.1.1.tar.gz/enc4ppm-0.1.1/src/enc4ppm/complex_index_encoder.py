import pandas as pd

from .base_encoder import BaseEncoder
from .constants import LabelingType, CategoricalEncoding, PrefixStrategy
from .helpers import one_hot

class ComplexIndexEncoder(BaseEncoder):
    def __init__(
        self,
        *,
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
        """
        Initialize the ComplexIndexEncoder.

        Args:
            labeling_type: Label type to apply to examples.
            attributes: Which attributes to consider. Can be a list of the attributes to consider or the string 'all' (all attributes found in the log will be encoded).
            categorical_attributes_encoding: How to encode categorical attributes. They can either remain strings (CategoricalEncoding.STRING) or be converted to one-hot vectors splitted across multiple columns (CategoricalEncoding.ONE_HOT).
            prefix_length: Maximum prefix length to consider: longer prefixes will be discarded, shorter prefixes may be discarded depending on prefix_strategy parameter. If not provided, defaults to maximum prefix length found in log. If provided, it must be a non-zero positive int number.
            prefix_strategy: Whether to consider prefix lengths from 1 to prefix_length (PrefixStrategy.UP_TO_SPECIFIED) or only the specified prefix_length (PrefixStrategy.ONLY_SPECIFIED).
            timestamp_format: Format of the timestamps in the log. If not provided, formatting will be inferred from the data.
            case_id_key: Column name for case identifiers.
            activity_key: Column name for activity names.
            timestamp_key: Column name for timestamps.
            outcome_key: Column name for outcome predition.
        """
        super().__init__(
            labeling_type,
            attributes,
            categorical_encoding,
            prefix_length,
            prefix_strategy,
            timestamp_format,
            case_id_key,
            activity_key,
            timestamp_key,
            outcome_key,
        )


    def encode(
        self,
        df: pd.DataFrame,
        *,
        freeze: bool = False,
    ) -> pd.DataFrame:
        """
        Encode the provided DataFrame with complex-index encoding and apply the specified labeling.

        Args:
            df: DataFrame to encode.
            freeze: Freeze encoder with provided parameters. Usually set to True when encoding the train log, False otherwise. Required if you want to later save the encoder to a file.

        Returns:
            The encoded DataFrame.
        """
        return super()._encode_template(df, freeze=freeze)
    

    def _encode(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        grouped = df.groupby(self.case_id_key)

        for case_id, case_events in grouped:
            case_events = case_events.sort_values(self.timestamp_key).reset_index()

            for prefix_length in range(1, len(case_events)+1):
                row = {
                    self.case_id_key: case_id,
                    self.timestamp_key: case_events.loc[prefix_length-1, self.timestamp_key],
                    self.ORIGINAL_INDEX_KEY: case_events.loc[prefix_length-1, 'index'],
                }

                # Add trace attributes
                for attribute_name, attribute in self.log_attributes.items():
                    if attribute['scope'] != 'trace': continue
                    
                    row[attribute_name] = self._get_attribute_value(attribute_name, case_events.loc[prefix_length-1, attribute_name])

                # Add activities
                for i in range(1, self.prefix_length+1):
                    if i <= prefix_length:
                        row[f'{self.EVENT_COL_PREFIX_NAME}_{i}'] = self._get_activity_value(case_events.loc[i-1, self.activity_key])
                    else:
                        row[f'{self.EVENT_COL_PREFIX_NAME}_{i}'] = self.PADDING_CAT_VAL

                # Add event attributes
                for attribute_name, attribute in self.log_attributes.items():
                    if attribute['scope'] != 'event': continue

                    for i in range(1, self.prefix_length+1):
                        if i <= prefix_length:
                            row[f'{attribute_name}_{i}'] = self._get_attribute_value(attribute_name, case_events.loc[i-1, attribute_name])
                        else:
                            if attribute['type'] == 'categorical':
                                row[f'{attribute_name}_{i}'] = self.PADDING_CAT_VAL
                            else:
                                row[f'{attribute_name}_{i}'] = self.PADDING_NUM_VAL
                
                rows.append(row)

        encoded_df = pd.DataFrame(rows)

        # Transform to one-hot if requested
        if self.categorical_encoding == CategoricalEncoding.ONE_HOT:
            categorical_columns = []
            categorical_columns_possible_values = []
            
            # Activity columns
            for i in range(1, self.prefix_length+1):
                categorical_columns.append(f'{self.EVENT_COL_PREFIX_NAME}_{i}')
                categorical_columns_possible_values.append(self.log_activities)

            # Categorical attributes columns
            for attribute_name, attribute in self.log_attributes.items():
                if attribute['type'] == 'categorical':
                    if attribute['scope'] == 'event':
                        for i in range(1, self.prefix_length+1):
                            categorical_columns.append(f'{attribute_name}_{i}')
                            categorical_columns_possible_values.append(attribute['values'])
                    else:
                        # For trace attributes do not consider PADDING value
                        attribute_possible_values = [attribute_value for attribute_value in attribute['values'] if attribute_value != self.PADDING_CAT_VAL]

                        categorical_columns.append(attribute_name)
                        categorical_columns_possible_values.append(attribute_possible_values)

            encoded_df = one_hot(
                encoded_df,
                columns=categorical_columns,
                columns_possible_values=categorical_columns_possible_values,
                unknown_value=self.UNKNOWN_VAL,
            )

        return encoded_df
