import pandas as pd

from dataframe_helpers.generic import to_array
import warnings

def group_apply(df, group_col, output_col,  func):
    group_col = to_array(group_col)
    output_col = to_array(output_col)
    
#    df2 = df.groupby(group_col).apply(func )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="DataFrameGroupBy.apply operated on the grouping columns",
        )
        df2 = df.groupby(group_col, group_keys=False).apply(func, include_groups=True)

    dummyVariableName = 'internal_dummy_name'
    df3 = df2.reset_index(name=dummyVariableName)
    df3[output_col ] = pd.DataFrame(df3[dummyVariableName].to_list(), columns=output_col )
    df3.drop(dummyVariableName, axis=1, inplace=True)
    return df3
