from collections import OrderedDict, defaultdict
from datetime import datetime

from dateutil import rrule
from django.utils import timezone


def get_number_of_hours_between_dates(
    d1, d2, list_employee_dayoffs, list_public_holidays=False, hours_range=range(0, 23), granularity=12
):
    def convert_days_from_hours(hours, granularity, hours_per_day):
        return int(hours / granularity) * granularity / hours_per_day

    rules = rrule.rruleset()

    byweekday_list = [rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]

    rules.rrule(
        rrule.rrule(
            freq=rrule.HOURLY,
            byweekday=byweekday_list,
            byhour=hours_range,
            dtstart=d1,
            until=d2,
        )
    )
    if list_public_holidays:
        list_employee_dayoffs.extend(list_public_holidays)
    current_tz = timezone.get_current_timezone()
    for holiday in sorted(list_employee_dayoffs):
        s1 = datetime(holiday.year, holiday.month, holiday.day, 0, 0, 0, tzinfo=current_tz)
        s2 = datetime(holiday.year, holiday.month, holiday.day, 23, 59, 59, tzinfo=current_tz)
        rules.exrule(rrule.rrule(rrule.HOURLY, dtstart=s1, until=s2))
    dates = defaultdict(int)
    for r in list(rules):
        dates[r.date()] += 1
    final = OrderedDict()
    for k, v in dates.items():
        final[k] = convert_days_from_hours(v, granularity, len(hours_range))
    return final
