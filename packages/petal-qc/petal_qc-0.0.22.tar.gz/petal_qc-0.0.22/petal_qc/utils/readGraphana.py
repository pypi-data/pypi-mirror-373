#!/usr/bin/env python3
"""Class to access graphana data."""

import datetime
from dateutil.parser import parse
import influxdb
import numpy as np


class ReadGraphana(object):
    """Connect to the GraphanaDB"""

    def __init__(self, host="silab15.ific.uv.es", port=8086):
        """Connect to Graphan server

        Args:
            host (str, optional): The IP of the server.
            port (int, optional): The port to the server.
        """
        self.client = influxdb.InfluxDBClient(host=host, port=port,
                                 username="matlab", password="matlab",
                                 database="clean_room",
                                 timeout=2)

    def get_temperature(self, the_time, window=10):
        """REturns the temperature

        Args:
            teh_time: the time to query the DB.
            window: the time window, in minutes, around the given time.
        """
        if not isinstance(the_time, datetime.datetime):
            the_time = parse(the_time)

        wnd = int(window/2.0+0.5)
        td = datetime.timedelta(minutes=wnd)
        t1 = the_time - td
        t2 = the_time + td

        measure="Temp"
        setup="MARTA_APP|MARTA_tt06"
        query = "select location,value from {measure} where (location =~ /.*{location}*/ and time>'{t1}' and time < '{t2}') group by \"location\"".format(
            measure=measure,
            location=setup,
            t1=t1.astimezone(datetime.timezone.utc).isoformat(),
            t2=t2.astimezone(datetime.timezone.utc).isoformat()
        )

        ss = self.client.query(query)
        nitems = 0
        for s in ss:

            nitems += len(s)

        if nitems==0:
            raise ValueError(("No data found"))

        T = []
        X = []
        for s in ss:
            for v in s:
                T.append(v['value'])
                X.append(v['time'])

        return X, T
