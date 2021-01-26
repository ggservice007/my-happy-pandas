"""
Data IO api
"""

# flake8: noqa

from my_happy_pandas.io.clipboards import read_clipboard
from my_happy_pandas.io.excel import ExcelFile, ExcelWriter, read_excel
from my_happy_pandas.io.feather_format import read_feather
from my_happy_pandas.io.gbq import read_gbq
from my_happy_pandas.io.html import read_html
from my_happy_pandas.io.json import read_json
from my_happy_pandas.io.orc import read_orc
from my_happy_pandas.io.parquet import read_parquet
from my_happy_pandas.io.parsers import read_csv, read_fwf, read_table
from my_happy_pandas.io.pickle import read_pickle, to_pickle
from my_happy_pandas.io.pytables import HDFStore, read_hdf
from my_happy_pandas.io.sas import read_sas
from my_happy_pandas.io.spss import read_spss
from my_happy_pandas.io.sql import read_sql, read_sql_query, read_sql_table
from my_happy_pandas.io.stata import read_stata
