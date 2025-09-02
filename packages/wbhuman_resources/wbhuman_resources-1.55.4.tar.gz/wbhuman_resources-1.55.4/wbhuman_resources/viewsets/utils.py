from datetime import date, timedelta
from typing import Tuple

import pandas as pd


def current_week_range(val_date: date = None) -> Tuple[date, date]:
    if not val_date:
        val_date = date.today()
    return [val_date - timedelta(days=val_date.weekday()), val_date + timedelta(days=6 - val_date.weekday())]


def current_day_range(val_date: date = None) -> Tuple[date, date]:
    if not val_date:
        val_date = date.today()
    return [val_date, val_date + timedelta(days=1)]


def current_month_range(val_date: date = None) -> Tuple[date, date]:
    if not val_date:
        val_date = date.today()
    return [(val_date - pd.tseries.offsets.MonthEnd(1)).date(), (val_date + pd.tseries.offsets.MonthEnd(0)).date()]


def current_year_range(val_date: date = None) -> Tuple[date, date]:
    if not val_date:
        val_date = date.today()
    return [(val_date - pd.tseries.offsets.YearBegin(1)).date(), (val_date + pd.tseries.offsets.YearEnd(0)).date()]
