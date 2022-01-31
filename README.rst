.. image:: https://konoanalytics.com/static/website/images/Kono-Logo-White-Color-Transparent-Back.svg
    :target: https://konoanalytics.com/


Kono Analytics Python Utilities
===============================
KonoPyUtil is a library of convenience functions, written in Python, for Kono Analytics and anyone else who wants to use it.

You can install this utility library with pip from GitHub.

    $ pip install git+https://github.com/konoanalytics/KonoPyUtil.git


>>> import KonoPyUtil as kpu
>>> kpu.__version__
>>> credentials = kpu.set_credentials('.env')
>>> query = "SELECT * FROM mytable LIMIT 10;"
>>> df = kpu.data_query(query)  # return a dataframe of your query results
