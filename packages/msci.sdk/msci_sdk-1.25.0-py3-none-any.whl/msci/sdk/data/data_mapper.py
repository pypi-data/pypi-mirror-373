from enum import Enum
import pandas as pd


class Datatypes(Enum):
    SECURITY_ID = "SEC_ID"
    BARRA_ID = "BARRA_ID"
    SEDOL = "SEDOL"
    ISIN = "ISIN"
    CUSIP = "CUSIP"
    RIC = "RIC"
    MIC = "MIC"
    ISSUER_ID = "ISSUER_ID"



def get_mapping_data(connection, input_identifier: Datatypes, output_identifier:Datatypes, input_list:tuple ,as_of_date:str):
    date = pd.to_datetime(as_of_date)
    query = f"select {input_identifier.value} , {output_identifier.value}, VERSION_START_DATE, VERSION_END_DATE from MSCI_DATASETS_ISHARE.DT.EQUITY_CHARACTERISTICS_HOC where {input_identifier.value} in {input_list} and TO_TIMESTAMP_NTZ('{date}') >= VERSION_START_DATE AND TO_TIMESTAMP_NTZ('{date}') < VERSION_END_DATE;"
    df = pd.read_sql(query, connection)
    return df
