from typing import Any, Callable, Generic, List, Dict, Text, Optional, Tuple, Union, TypeVar, Type
import pandas as pd
import os
import csv
import math
from ewoxcore.utils.dictionary_util import DictionaryUtil

T = TypeVar("T")


class CsvFileUtil:
    @staticmethod
    def split(filename:str, delimiter:str=",", row_limit:int=1000,
              output_filename="output_%s.csv", output_path="", 
              keep_headers=True) -> List[str]:
        files:List[str] = []
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            current_piece:int = 1
            current_out_path:str = os.path.join(
                output_path,
                output_filename % current_piece
            )
            files.append(current_out_path)

            current_out_writer = csv.writer(open(current_out_path, "w"), delimiter=delimiter)
            current_limit:int = row_limit
            if keep_headers:
                headers = reader.next()
                current_out_writer.writerow(headers)
   
            for i, row in enumerate(reader):
                if i + 1 > current_limit:
                    current_piece += 1
                    current_limit = row_limit * current_piece
                    current_out_path:str = os.path.join(
                        output_path,
                        output_filename % current_piece
                    )
                    files.append(current_out_path)

                    current_out_writer = csv.writer(open(current_out_path, "w"), delimiter=delimiter)
                    if keep_headers:
                        current_out_writer.writerow(headers)

                current_out_writer.writerow(row)

            return files


    @staticmethod
    def split_df(df:pd.DataFrame, delimiter:str=",", row_limit:int=1000,
                output_filename:str="output_%s.csv", output_path:str="", headers:List[str]=[], add_num_zeros:int=0) -> None:
        files:List[str] = []
        low:int = 0
        high:int = row_limit
        for i in range(math.ceil(len(df) / row_limit)):
            filename:str = os.path.join(output_path, output_filename % str(i+1).zfill(add_num_zeros))
            files.append(filename)
            df[low:high].to_csv(filename, sep=delimiter, index=False)
            if (len(headers) > 0):
                df.columns = headers

            low = high
            if (high + row_limit < len(df)):
                high += row_limit
            else:
                high = len(df)

        return files


    @staticmethod
    def read_file(filename:str, callback:Callable[[Any], None], chunk_size:int=100000):
        """ Read large data file or improve read performance based on setting chunk size. """
        if (callback is None):
            return

        df_chunks = pd.read_csv(filename, chunksize=chunk_size, low_memory=False)
        for df in df_chunks:
            callback(df)
        

    @staticmethod
    def write_df(df:pd.DataFrame, delimiter:str=",", filename="output.csv") -> None:
        df.to_csv(filename, sep=delimiter, index=False)


    @staticmethod
    def write(items:List[T], filename:str, delimiter:str=",", header:List[str]=[]) -> None:
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=header, delimiter=delimiter)
            writer.writeheader()
            for item in items:
                item_dict = DictionaryUtil.convert(item)
                writer.writerow(item_dict)
