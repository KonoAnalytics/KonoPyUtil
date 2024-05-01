import pandas as pd
import ipaddress
from uuid import uuid4
import ipinfo
from .credentials import set_credentials
from .dbutils import get_engine, data_query, write_dataframe
from .constants import US_STATE_TO_ABBREVIATION
from datetime import datetime


def _validate_ip_address(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def geocode_ip(ip_address, use_cache=True):
    """
    Uses IPInfo
    Account information here: https://ipinfo.io/account/home
    :param ip_address:
    :param use_cache:
    :return:
    """
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
    ipinfo_key = set_credentials(env_var_name="IPINFO_CREDENTIALS")["TOKEN"]
    handler = ipinfo.getHandler(ipinfo_key)
    details = handler.getDetails(ip_address)
    if (details.all).get("bogon"):
        return {
            "Success": "False",
            "Message": "Can't locate IP Address",
        }
    details_dict = details.all
    for k, v in details_dict.items():
        details_dict[k] = [v]
    df = pd.DataFrame.from_dict(details_dict)
    df["upload_dt_utc"] = datetime.utcnow()
    rename_cols = {
        "ip": "ip_address",
        "country": "countryCode",
        "region": "state",
        "postal": "postalCode",
        "country_name": "country",
    }
    df = df.rename(columns=rename_cols)
    df["stateCode"] = df["state"].map(US_STATE_TO_ABBREVIATION)
    df["uuid"] = uuid4()
    df["countryFlag"] = df["country_flag"].iloc[0]["unicode"]  # TODO: figure out how to write this properly to dB
    df["dma"] = None
    df["dmaCode"] = None
    df["layer"] = None
    continent = df["continent"].iloc[0]
    df["continent"] = continent["name"]
    df["continentCode"] = continent["code"]
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    drop_cols = ["country_currency", "loc", "country_flag", "iseu"]
    df = df.drop(columns=drop_cols)
    write_dataframe(df=df, tablename="ip_geocode", if_exists="append")
    return_dict = dict(df.iloc[0])
    return_dict["Success"] = "True"
    return return_dict
