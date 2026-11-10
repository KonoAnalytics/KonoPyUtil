Release History
===============

2.1.0
----------

- Upgraded dependencies: pandas 3.1.1, SQLAlchemy 2.1.8, environs 15.2.0, psycopg2-binary 2.9.13, ipinfo 5.6.0, requests 2.34.2
- Added openpyxl (required by soccer.schedule_event for reading Excel workbooks)
- Requires Python 3.13 or greater (pandas 3 and SQLAlchemy 2.1 require it)
- set_credentials(): fixed loading of .env values with environs 15
- get_engine(): explicit postgresql+psycopg2 driver (SQLAlchemy 2.1 defaults to psycopg)
- get_engine(): fixed credentials argument being ignored (raised UnboundLocalError)
- get_elo_season(): fixed pandas 3 dtype error


2.0.0 (2024-08-15)
------------------

- get_txptc_plans: better error handling of ipinfo return values
- updated dependency versions, including SQLAlchemy and Pandas


1.0.2 (2024-05-01)
------------------

- geocode_ip(): better error handling of ipinfo return values


1.0.1 (2024-05-01)
------------------

- geocode_ip(): replaced provider Radar with ipinfo


1.0.0 (2022-05-24)
------------------
- Made Available to kono.rest
- Radar: added geocode_ip()


0.0.3 (2022-02-01)
------------------

- Soccer: added validate_elo_df()


0.0.2 (2022-01-30)
------------------

- Soccer: better variable naming convention


0.0.1 (2022-01-29)
------------------

- Soccer: get_elo_season, get_elo_match
- Database: data_query, command_query, write_dataframe, get_engine
- Credentials: set_credentials 
- Datasets: list_datasets, load_dataset. copa_rayados.2021.csv dataset
