import sqlalchemy as sa
import pandas as pd
from .credentials import set_credentials
from .exceptions import MissingCredentialsError


def data_query(query, engine=None, **kwargs):
    """
    consumes a select query and returns a dataframe with the results
    :param query: string of query
    :param engine: sql alchemy engine
    :param **kwargs: remaining parameters for pandas.read_sql()
    :return: dataframe of results of query
    """
    close_engine = False
    if engine is None:
        close_engine = True
        engine = get_engine(**kwargs)
    df = pd.read_sql(query, engine)
    if close_engine:
        engine.dispose()
    return df


def command_query(query, engine=None, **kwargs):
    """
    consumes a command query (update, drop, etc)
    :param query: string  of query
    :param engine: sql alchemy engine
    :return: returns result of query execution
    """
    close_engine = False
    if engine is None:
        close_engine = True
        engine = get_engine(**kwargs)
    if close_engine:
        engine.dispose()
    return engine.execute(sa.text(query).execution_options(autocommit=True))


def write_dataframe(df, tablename, engine, if_exists="append", index=False, **kwargs):
    """
    Appends dataframe records to a database. (Creates table if it doesn't exist)
    :param df: dataframe
    :param tablename: table name
    :param engine: engine
    :param if_exists: {‘fail’, ‘replace’, ‘append’}, default ‘append’
    :param **kwargs: remaining parameters for pandas.to_sql()
    :return: True if success, False otherwise
    """

    close_engine = False
    if engine is None:
        close_engine = True
        engine = get_engine(**kwargs)
    try:
        df.to_sql(name=tablename, con=engine, if_exists=if_exists, index=index)
        engine.dispose()
        success = True
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        success = False
    finally:
        if close_engine:
            engine.dispose()
    return success


def get_engine(credentials=None, **kwargs):
    """
    Returns a sqlalchemy engine given appropriate inputs
    :param **kwargs: remaining parameters for sqlalchemy.create_engine()
    """
    if not credentials:
        os_credentials = set_credentials()
        if not os_credentials:
            raise (MissingCredentialsError())
        userid = os_credentials.get("USERID", "db_userid")
        password = os_credentials.get("PASSWORD", "db_password")
        host = os_credentials.get("HOST", "db_host")
        port = int(os_credentials.get("PORT", "0"))
        dbname = os_credentials.get("DBNAME", "db_name")
    cstring = f"postgresql://{userid}:{password}@{host}:{port}/{dbname}"
    return sa.create_engine(cstring, **kwargs)
