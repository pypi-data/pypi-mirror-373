import pandas as pd
import numpy as np
from pandas.io.json import json_normalize


class DataFrameUtil:
    @staticmethod
    def convertToDF(dfJSON) -> pd.DataFrame:
        """ Converts the input JSON to a DataFrame. """
        return(json_normalize(dfJSON))


    @staticmethod
    def convertToJSON(df:pd.DataFrame) -> str:
        """ Converts the input DataFrame to JSON. """
        resultJSON = df.to_json(orient='records')
        return(resultJSON)


    @staticmethod
    def csvToDF(path: str, separator:str='\t', skip_rows:int=0) -> pd.DataFrame:
        """ Converts the input CSV to DataFrame. """
        return pd.read_csv(path, skiprows=skip_rows, sep=separator, comment='#')


    @staticmethod
    def convertToDict(df:pd.DataFrame) -> dict:
        """ Converts the input DataFrame to dictionary. """
        tmp_d = dict()
        for index, row in list(df.iterrows()):
            v1 = row.values[0]
            v2 = row.values[1]
            tmp_d[v1] = v2
        return tmp_d


    @staticmethod
    def remove_row(df:pd.DataFrame, id:str, column_name:str="id") -> pd.DataFrame:
        df_list:pd.DataFrame = df.loc[df[column_name] != id]
        return df_list


    @staticmethod
    def get_list(df:pd.DataFrame, order_by:str="row_idx", skip:int=0, num:int=10) -> pd.DataFrame:
        df_list:pd.DataFrame = df.nlargest(num+skip, columns=order_by).tail(num)
        return df_list


    @staticmethod
    def add_row_number(df:pd.DataFrame, column:str="row_idx") -> None:
        df[column] = np.arange(len(df))


    @staticmethod
    def search(df:pd.DataFrame, column:str, name:str, use_case:bool=False) -> pd.DataFrame:
        return df[df[column].str.contains(name, case=use_case, na=False)]


    @staticmethod
    def get_diff(input_a:pd.DataFrame, input_b:pd.DataFrame) -> pd.DataFrame:
#        return pd.concat([input_a, input_b]).drop_duplicates(keep=False)
        return input_a.compare(input_b)
