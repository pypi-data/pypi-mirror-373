import argparse
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

def options():
    parser = argparse.ArgumentParser(description='scx')
    parser.add_argument('--times', type=str, default='202411100000,202411101000') 
    parser.add_argument('--pac', type=str, default='100000')
    parser.add_argument('--tag', type=str, default='100000')
    parser.add_argument('--isDebug',action='store_true',default=False)
    config= parser.parse_args()
    print(config)
    config.times = config.times.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]
    return config
if __name__ == '__main__':
    cfg = options()
    sCST = cfg.times[0]
    eCST = cfg.times[-1]
    timeList = pd.date_range(sCST, eCST + relativedelta(hours=24), freq="1h", inclusive="left")
    print()

    