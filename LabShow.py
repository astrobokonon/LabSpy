import time
import pytz
import numpy as np
import datetime as dt
import sqlite3 as sql

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


#offset-naive datetime
UNIX_EPOCH_naive = dt.datetime(1970, 1, 1, 0, 0) 
#offset-aware datetime
UNIX_EPOCH_offset_aware = dt.datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc) 

UNIX_EPOCH = UNIX_EPOCH_naive
TS_MULT_us = 1e6



def searchDB(dbname, intval=-12, intkind='hours'):
    conn = sql.connect(dbname)
    cursor = conn.cursor()
    # Can't figure out how to avoid this
    interval = "%f %s" % (intval, intkind)
    cursor.execute(
                   """
                   SELECT RPITimestamp, Temperature, Humidity, CRCCheck
                   FROM LabEnvironment 
                   WHERE DATETIME(RPITimestamp) > DATETIME('now', ?)
                   """, 
                   [interval])

    rvals = cursor.fetchall()
    times = np.array(zip(*rvals)[0])
    times = dtvals(times)

    temps = np.array(zip(*rvals)[1])
    humis = np.array(zip(*rvals)[2])

    conn.close()
    return times, temps, humis


def dtvals(arry):
    fmt = "%Y-%m-%d %H:%M:%S.%f"
    dts = [dt.datetime.strptime(item, fmt) for item in arry]

    return dts


def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return(int((dt.datetime.utcnow() - epoch).total_seconds()*ts_mult))


def int2dt(ts, ts_mult=TS_MULT_us):
    return(dt.datetime.utcfromtimestamp(float(ts)/ts_mult))


def dt2int(dt, ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    delta = dt - epoch
    return(int(delta.total_seconds()*ts_mult))


def td2int(td, ts_mult=TS_MULT_us):
    return(int(td.total_seconds()*ts_mult))


def int2td(ts, ts_mult=TS_MULT_us):
    return(dt.timedelta(seconds=float(ts)/ts_mult))


def main():
    times, temps, humis = searchDB('./CourtyardPalmdale.db')
    
    plt.plot(times, temps, color='red', label="Temperature")
    plt.plot(times, humis, color='blue', label="Humidity")
    plt.legend()
    plt.savefig("./storedsofar.png")
    plt.close()


if __name__ == '__main__':
    main()
