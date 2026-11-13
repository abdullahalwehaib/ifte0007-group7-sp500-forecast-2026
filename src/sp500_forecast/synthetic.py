"""Fixed-seed artificial prices; no genuine prices or fitted real-data values."""
import csv
import math
import random
from datetime import date
from pathlib import Path

from . import SYNTHETIC_NOTICE
from .calendar import sessions_between
from .engine import Price

SEED=2026111207


def synthetic_prices(seed=SEED):
    rng=random.Random(seed)
    level=1000.0
    rows=[]
    for i,session in enumerate(sessions_between(date(2020,1,1),date(2026,11,12))):
        # Artificial regimes exercise volatility and reversal without importing
        # observations, coefficients or residuals from the real research.
        drift=0.00016+0.00010*math.sin(i/103.0)
        volatility=0.0065+0.003*float(300<=i<480 or 1150<=i<1300)
        level*=math.exp(drift+rng.gauss(0,volatility))
        rows.append(Price(session,round(level,2)))
    return rows


def write_synthetic_csv(path, prices=None):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    rows=synthetic_prices() if prices is None else prices
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['observation_date','SP500','data_status'])
        writer.writeheader()
        for row in rows:
            writer.writerow({'observation_date':str(row.session),'SP500':f'{row.close:.2f}',
                             'data_status':SYNTHETIC_NOTICE})
    return path

