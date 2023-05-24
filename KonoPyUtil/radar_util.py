import pandas as pd
import ipaddress
from uuid import uuid4
from .credentials import set_credentials
from .dbutils import get_engine, data_query, write_dataframe
from radar import RadarClient
from datetime import datetime


def _validate_ip_address(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def geocode_ip(ip_address, use_cache=True):
    if not _validate_ip_address(ip_address):
        return {
            "Success": "False",
            "Message": "Improperly Formatted IP Address",
        }

    if use_cache:
        query = f"""SELECT * FROM ip_geocode WHERE "ip_address" = '{ip_address}' ORDER BY upload_dt_utc DESC LIMIT 1"""
        df = data_query(query=query)
        if len(df):
            return_dict = dict(df.iloc[0])
            return_dict["Success"] = "True"
            return return_dict
    radar_key = set_credentials(env_var_name="RADAR_CREDENTIALS")["KEY"]
    radar = RadarClient(radar_key)
    r = radar.geocode.ip(ip=ip_address)
    try:
        df = pd.DataFrame(r.to_dict()).loc[["coordinates"]]
    except ValueError:
        return {
            "Success": "False",
            "Message": "Can't locate IP Address",
        }
    df = df.drop(columns=["geometry"])
    df["upload_dt_utc"] = datetime.utcnow()
    df["uuid"] = uuid4()
    df["ip_address"] = ip_address
    write_dataframe(df=df, tablename="ip_geocode", if_exists="append")
    return_dict = dict(df.iloc[0])
    return_dict["Success"] = "True"
    return return_dict
