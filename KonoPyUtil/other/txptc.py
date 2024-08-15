from datetime import datetime
from io import StringIO

import pandas as pd
import requests

from ..dbutils import get_engine, data_query, command_query, write_dataframe


URL = "https://www.powertochoose.org/en-us/Plan/ExportToCsv"


def _clean_headers(df):
    newcols = list(df)
    newcols = [s.replace("[", "") for s in newcols]
    newcols = [s.replace("]", "") for s in newcols]
    return newcols


def _drop_last_record(df):
    df = df[df["idKey"] != "END OF FILE"]
    return df


def _get_latest_file(utc_now):
    # download new file
    r = requests.get(URL, verify=False)
    s = str(r.content, "utf-8")
    data = StringIO(s)
    df = pd.read_csv(data)
    df.columns = _clean_headers(df)
    df = _drop_last_record(df)
    df["utc_download_timestamp"] = utc_now
    df["utc_start"] = utc_now
    df["utc_finish"] = pd.NaT
    return df


def _sunset_old_plans(current_idkeys, utc_now, engine):
    idkeys = ",".join(str(x) for x in current_idkeys)
    select_query = f"""SELECT "idKey" FROM txptc
WHERE "utc_finish" IS NULL
AND "idKey" NOT IN ({idkeys});"""
    df = data_query(select_query)
    update_query = f"""UPDATE txptc SET utc_finish='{utc_now}' WHERE "idKey" IN (
SELECT "idKey" from txptc
WHERE "utc_finish" IS NULL
AND "idKey" NOT IN ({idkeys})
);"""
    command_query(update_query, engine)
    return df


def _get_all_plans(engine):
    query = f"""SELECT "idKey" FROM txptc"""
    return data_query(query, engine)


def get_txptc_plans(verbose=0, tablename=None):
    utc_now = datetime.utcnow()
    df_website = _get_latest_file(utc_now)
    if verbose > 1:
        print(f"Downloaded {len(df_website)} plans from the TX PTC website.")
    engine = get_engine()
    df_db = _get_all_plans(engine)
    df_new = df_website[~df_website["idKey"].astype("int").isin(df_db["idKey"])]
    website_idkeys = list(df_website["idKey"])
    df_sunset = _sunset_old_plans(website_idkeys, utc_now, engine)
    if verbose > 1:
        print(f"Deactivated {len(df_sunset)} plans that are no longer active.")

    if len(df_new):
        if verbose > 1:
            print(f"Uploading {len(df_new)} new plans to the database.")
        if tablename is None:
            tablename = "txptc"
        write_dataframe(df_new, tablename=tablename, engine=engine)
    else:
        if verbose > 1:
            print("No new plans.")

    engine.dispose()
