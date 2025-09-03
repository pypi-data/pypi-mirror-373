import json
import pandas as pd
import hashlib
from ..Types import (
    VARCHAR,
    STR,
    TEXT,
    INT,
    BIGINT,
    MAX_VARCHAR_LENGTH,
    SUPER,
    S3,
    REDSHIFT,
    JSON,
    JSONB,
    UUID,
    target_type_is_numeric,
)


class AdapterSourceTarget:
    def __init__(self, struct):
        self.struct = struct

    def order_by_cdc(self, op, df):
        if op == "U":
            if "cdc_datetime" not in df.columns:
                return df
            else:
                if df['cdc_datetime'].isnull().any():
                    return df
                else:
                    df = df.sort_values('cdc_datetime', ascending=True)
                    return df
        else:
            return df

    def convert_types(self, df):
        for c in self.struct.columns:
            case_target_type = {
                VARCHAR: STR,
                TEXT: STR,
                INT: pd.Int64Dtype(),
                BIGINT: pd.Int64Dtype(),
            }

            if c["target_type"] in case_target_type.keys():
                if c["source_name"] not in df.columns:
                    pass
                else:
                    df[c["source_name"]] = df[c["source_name"]].astype(
                        case_target_type[c["target_type"]]
                    )
                    if case_target_type[c["target_type"]] == STR:
                        df[c["source_name"]].replace("None", "", inplace=True)
        return df

    def __transform_super_redshift(self, df, struct_column):
        def decode_json(x):
            try:
                return json.loads(x)
            except Exception as e:
                return {"redshift_error": "Field is too long to be saved"}

        df[struct_column["source_name"]] = df[struct_column["source_name"]].apply(
            json.dumps
        )
        df[struct_column["source_name"]] = df[struct_column["source_name"]].str[
            :MAX_VARCHAR_LENGTH
        ]
        df[struct_column["source_name"]] = df[struct_column["source_name"]].apply(
            decode_json
        )
        df[struct_column["source_name"]] = df[struct_column["source_name"]].apply(
            json.dumps
        )

        return df

    def transform_data(self, df, target_save=REDSHIFT):
        if target_save == REDSHIFT:
            for c in self.struct.columns:
                if c["is_active"] is False:
                    df[c["source_name"]] = ""
                else:
                    if c["target_type"] == SUPER:
                        df = self.__transform_super_redshift(df, c)
        elif target_save == S3:
            for c in self.struct.columns:
                if c["source_type"] == JSON or c["source_type"] == JSONB:
                    df[c["source_name"]] = df[c["source_name"]].apply(json.dumps)
                if c["source_type"] == UUID:
                    df[c["source_name"]] = df[c["source_name"]].astype(str)
        return df

    def equalize_number_columns(self, df):
        df_columns = df.columns.tolist()
        struct_columns = [c["source_name"] for c in self.struct.columns]

        for dfc in df_columns:
            if dfc not in struct_columns and dfc != "Op":
                df = df.drop(columns=[dfc])

        for sc in struct_columns:
            if sc not in df_columns:

                def find_target_type(sc):
                    for c in self.struct.columns:
                        if c["source_name"] == sc:
                            return c["target_type"]

                target_type = find_target_type(sc)

                if target_type == VARCHAR or target_type == TEXT:
                    df[sc] = ""
                elif target_type_is_numeric(target_type):
                    df[sc] = None
                else:
                    df[sc] = None

        df = df[struct_columns]

        return df
