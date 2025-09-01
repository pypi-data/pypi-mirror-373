"""
pandas DataFrame utility functions for data analysis and manipulation.

This module provides utilities for:
- Converting data types within DataFrames
- Analyzing column structures across multiple DataFrames
- Finding and extracting rows/columns with missing or empty data
- Data quality validation and exploration
"""

import pandas as pd
from typing import List, Tuple, Dict, Any, Optional, Union


def convert_list_to_tuple_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert list values to tuples in DataFrame object columns.
    
    Preserves None values and other data types unchanged.
    Only processes columns with object dtype that contain list values.
    
    Args:
        df (pd.DataFrame): Input DataFrame to process
        
    Returns:
        pd.DataFrame: DataFrame with list values converted to tuples
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [[1, 2], [3, 4]], 'col2': ['a', 'b']})
        >>> result = convert_list_to_tuple_in_df(df)
        >>> print(result['col1'].iloc[0])
        (1, 2)
    """
    df_copy = df.copy()
    
    for col in df_copy.columns:
        if df_copy[col].dtype == "object" and df_copy[col].map(type).eq(list).any():
            df_copy[col] = df_copy[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)
    
    return df_copy


def show_col_names(dfs: List[pd.DataFrame], print_result: bool = False) -> Tuple[Dict[str, List[str]], pd.DataFrame]:
    """
    Compare column names across multiple DataFrames.
    
    Creates a comprehensive view of all columns present in the input DataFrames,
    showing which columns exist in each DataFrame.
    
    Args:
        dfs (List[pd.DataFrame]): List of DataFrames to compare
        print_result (bool, optional): Whether to print the comparison table. Defaults to False.
        
    Returns:
        Tuple[Dict[str, List[str]], pd.DataFrame]: 
            - Dictionary mapping DataFrame names to column lists
            - Comparison DataFrame showing column presence across DataFrames
            
    Example:
        >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> df2 = pd.DataFrame({'B': [5, 6], 'C': [7, 8]})
        >>> col_dict, comparison_df = show_col_names([df1, df2])
    """
    # Create dictionary mapping each DataFrame to its column list
    all_df = {f'df_{idx + 1}': df.columns.to_list() for (idx, df) in enumerate(dfs)}
    
    # Get all unique column names across all DataFrames
    all_cols = list(set(col for df_cols in all_df.values() for col in df_cols))
    all_cols = sorted(all_cols)
    
    # Create comparison dictionary
    df_cols = {'All': all_cols}
    df_cols.update({
        df_name: [col if col in df_columns else '' for col in all_cols] 
        for (df_name, df_columns) in all_df.items()
    })
    
    # Convert to DataFrame for easy viewing
    df_check = pd.DataFrame(data=df_cols)
    
    if print_result:
        print(df_check)
    
    return (df_cols, df_check)


def show_all_na(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract rows and columns that contain NA values.
    
    Returns a subset of the original DataFrame containing only:
    - Rows that have at least one NA value
    - Columns that have at least one NA value
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        
    Returns:
        pd.DataFrame: Subset containing only rows and columns with NA values
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> df = pd.DataFrame({'A': [1, np.nan], 'B': [3, 4], 'C': [np.nan, 6]})
        >>> na_subset = show_all_na(df)
    """
    # Find rows with any NA values
    df_rows_na = df[df.isna().any(axis='columns')]
    
    # Find columns with any NA values
    df_cols_na = df.columns[df.isna().any()].to_list()
    
    # Return intersection: rows with NA values, showing only columns with NA values
    df_na = df_rows_na[df_cols_na]
    
    return df_na


def show_all_na_or_empty_rows(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Find rows containing NA values or empty strings.
    
    Identifies rows that have NA values or empty strings ('') in any column,
    with option to exclude specific columns from the check.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        exclude_cols (Optional[List[str]], optional): Columns to exclude from NA/empty check. 
            Defaults to None.
            
    Returns:
        pd.DataFrame: Rows containing NA values or empty strings, with all original columns
        
    Example:
        >>> df = pd.DataFrame({'A': [1, ''], 'B': [3, 4], 'C': ['x', 'y']})
        >>> problem_rows = show_all_na_or_empty_rows(df, exclude_cols=['C'])
    """
    if exclude_cols is None:
        exclude_cols = []
    
    # Select columns to check (excluding specified columns)
    cols_to_check = [col for col in df.columns if col not in exclude_cols]
    df_check = df[cols_to_check]
    
    # Create mask for rows with NA values or empty strings
    mask_row = df_check.isna().any(axis=1) | (df_check == '').any(axis=1)
    
    # Return complete rows that match the criteria
    df_na_rows = df[mask_row]
    
    return df_na_rows


def show_all_na_or_empty_columns(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Find columns containing NA values or empty strings.
    
    Identifies columns that have NA values or empty strings ('') in any row,
    with option to exclude specific columns from the check.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        exclude_cols (Optional[List[str]], optional): Columns to exclude from NA/empty check. 
            Defaults to None.
            
    Returns:
        pd.DataFrame: All rows, but only columns that contain NA values or empty strings
        
    Example:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': ['', 'x'], 'C': ['y', 'z']})
        >>> problem_cols = show_all_na_or_empty_columns(df, exclude_cols=['C'])
    """
    if exclude_cols is None:
        exclude_cols = []
    
    # Select columns to check (excluding specified columns)
    cols_to_check = [col for col in df.columns if col not in exclude_cols]
    
    # Create mask for columns with NA values or empty strings
    mask_col = df[cols_to_check].isna().any(axis=0) | (df[cols_to_check] == '').any(axis=0)
    
    # Return all rows but only problematic columns
    df_na_cols = df.loc[:, mask_col.index[mask_col]]
    
    return df_na_cols