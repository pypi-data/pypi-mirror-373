from typing import Any, List, Optional, Dict, Tuple, Text
from datetime import date, time, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dateutil import tz, parser
from ewoxcore.constants.week_day import WeekDay


class DatetimeUtil:
    @staticmethod
    def is_time(input:str) -> bool:
        import time
        try:
            time.strptime(input, '%H:%M')
            return True
        except ValueError:
            return False
   

    @staticmethod
    def is_date(input:str, fuzzy:bool=False) -> bool:
        """
        Return whether the string can be interpreted as a date.

        :param input: str, input to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try: 
            parser.parse(input, fuzzy=fuzzy)
            return True
        except ValueError:
            return False
        except:
            return False


    @staticmethod
    def get_safe_date_string(val:date) -> str:
        try:
            if (val is None):
                return ""
            if (str(val) == "NaT"):
                return ""
            return str(val)
        except Exception as error:
            return ""


    @staticmethod
    def get_date(date_s:str) -> date:
        date_str:str = ""
        try:
            date_d:datetime = parser.parse(date_s, fuzzy=False)
            date_str = date_d.strftime("%Y-%m-%d")
        except Exception as error:
            try:
                date_str = datetime.strptime(date_s, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            except Exception as error:
                try:
                    date_str = datetime.strptime(date_s, '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%d")
                except Exception as error:
                    date_str = datetime.strptime(date_s, '%Y-%m-%d').strftime("%Y-%m-%d")

        tmp_date_d:datetime = datetime.strptime(date_str, '%Y-%m-%d')
        date_d:date = date(tmp_date_d.year, tmp_date_d.month, tmp_date_d.day)

        return date_d


    @staticmethod
    def get_date_time(date_s:str) -> Optional[datetime]:
        date_d:datetime = None
        try:
            date_d = parser.parse(date_s, fuzzy=False)
        except Exception as error:
            return None
        return date_d


    @staticmethod
    def get_utc_isoformat() -> str:        
        utc_date:str = datetime.now(tz=timezone.utc).isoformat() + "Z"
        return utc_date


    @staticmethod
    def get_next_weekday(input:date=date.today()):
        weekday:datetime = input + timedelta(days=1)
        if weekday.isoweekday() in set((6, 7)):
            weekday += timedelta(days=-weekday.isoweekday() + 8)
        return weekday


    @staticmethod
    def get_next_weekend_day(input:date=date.today()):
        if (input.weekday() == 5):
            input += timedelta(days=1)
            return input
        weekend_date = input + timedelta((12 - input.weekday()) % 7)
        return weekend_date


    @staticmethod
    def convert_utc(input:datetime) -> datetime:
        input_utc:datetime = input.astimezone(timezone.utc)
        return input_utc


    @staticmethod
    def get_week_number(input:datetime) -> int:
        week:int = input.isocalendar().week
        return week


    @staticmethod
    def get_week_number(input:date) -> int:
        week:int = input.isocalendar().week
        return week


    @staticmethod
    def get_previous_week_number(input:datetime) -> int:
        week:int = input.isocalendar().week
        week -= 1
        if (week == 0):
            week = 52
        return week


    @staticmethod
    def get_next_day_from_days(week_day:int, days:List[int]) -> int:
        """ Expects a sorted list of days"""
        for day in days:
            if (day > week_day):
                return day

        return -1


    @staticmethod
    def get_end_of_today(delta:int=0) -> datetime:
        end_of_today:datetime = datetime.now() + timedelta(days=delta)
        end_of_today = datetime(
            year=end_of_today.year, month=end_of_today.month, day=end_of_today.day, 
            hour=23, minute=59, second=59)
        return end_of_today


    @staticmethod
    def get_next_time_slot(input:datetime, days:List[int], now:datetime, additional_delta:timedelta=timedelta(minutes=1)) -> datetime:
        if (len(days) == 0):
            return input

        week_days:List[int] = [x if (x != 0) else 8 for x in days]
        week_days.sort()

        days.sort()
        day_chosen:int = -1
        today_idx:int = -1
        now_utc:datetime = DatetimeUtil.convert_utc(now+additional_delta)
        iso_weekday:int = now_utc.isoweekday()
        input_utc:datetime = DatetimeUtil.convert_utc(input)
        for index, day in enumerate(week_days):
            if (day >= input.isoweekday()):
                if (day == 8):
                    if (iso_weekday == 0):
                        today_idx = index
                elif (day == iso_weekday):
                    today_idx = index

                # we add 10 minutes by default to ensure we get a datetime in the future for scheduling.
                if (input_utc > now_utc):
                    day_chosen = day
                    break

        if (day_chosen == -1):
            if ((today_idx > -1) & (len(week_days) > today_idx+1)):
                day_chosen = week_days[today_idx+1]
        
        week_offset:timedelta = None
        if ((day_chosen == -1) & (len(days) == 1)):
            week_offset = timedelta(days=7)
        if (day_chosen == -1):
            day_chosen = DatetimeUtil.get_next_day_from_days(iso_weekday, week_days)

        day_today:int = input.isoweekday()
        if (week_offset is not None):
            input += week_offset
        elif (day_chosen >= day_today):
            input += timedelta(day_chosen - day_today)
        else:
            diff:int = 8 - day_today
            input += timedelta(diff)

        return input


    @staticmethod
    def get_week_dates(today:datetime=datetime.today()) -> List[datetime]:
        weekday:int = today.isoweekday()
        start:datetime = today - timedelta(days=weekday)
        dates:List[datetime] = [start + timedelta(days=i) for i in range(7)]
        return dates


    @staticmethod
    def get_week_dates_as_string(today:datetime=datetime.today()) -> List[str]:
        weekday:int = today.isoweekday()
        start:datetime = today - timedelta(days=weekday)
        dates:List[str] = [str((start + timedelta(days=i)).date()) for i in range(7)]
        return dates


    @staticmethod
    def get_previous_week_range(value:date) -> Tuple[date, date]:
        # Minus 1 day as a calendar week start day is a Sunday.
        weekday:int = value.weekday()
        start_delta:timedelta = timedelta(days=weekday, weeks=1) - timedelta(days=-1)
        if (weekday == int(WeekDay.Sunday)):
            start_delta = timedelta(days=7) 
        start_date:date = value - start_delta
        end_date:date = date(year=start_date.year, month=start_date.month, day=start_date.day)
        end_date = end_date + timedelta(days=6)

        return start_date, end_date


    @staticmethod
    def get_week_range() -> Tuple[date, date]:
        start_date:date = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
        end_date:date = start_date + timedelta(days=6)

        return start_date, end_date


    @staticmethod
    def convert_delta_to_hours(delta:timedelta) -> int:
        total_seconds:float = delta.total_seconds()
        hours = int(total_seconds / 3600)
        return hours

    
    @staticmethod
    def get_iso_string(value:str) -> str:
        dt_iso:str = DatetimeUtil.get_safe_date_string(value)
        if (len(dt_iso) < 19):
            dt_iso += "T00:00:00"
        else:
            dt_iso = dt_iso[:19]
            dt_iso += "Z" if (dt_iso[-1] != "Z") else ""

        return dt_iso


    @staticmethod
    def get_utc_string_or_none(value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        try:
            dt = parser.parse(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)

            dt_iso:str = dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

            return dt_iso
        except Exception:
            return None


if __name__ == "__main__":
    DatetimeUtil.get_week_range()
    input:date = date(year=2023, month=3, day=12)
    from_date, to_date = DatetimeUtil.get_previous_week_range(input)
    print(f"Input: {input}, Start: {from_date}, To: {to_date} ")

    input:date = date(year=2023, month=2, day=25)
    from_date, to_date = DatetimeUtil.get_previous_week_range(input)
    print(f"Input: {input}, Start: {from_date}, To: {to_date} ")

    is_time:bool = DatetimeUtil.is_time("12:23")
    week_dates = DatetimeUtil.get_week_dates_as_string()
    week_dates = DatetimeUtil.get_week_dates()
    week:int = DatetimeUtil.get_week_number(datetime.today())
    required_output:datetime = datetime(2022,4,30, 12,36,0)

    days:List[int] = [1,2,3,4,5]

    time_zone:str = "Europe/Copenhagen"
    time_of_day:int=16
    time_of_day_minute:int=53
    scheduled_at:datetime = datetime.combine(datetime.now(),
                                time(hour=time_of_day, minute=time_of_day_minute, second=0, tzinfo=ZoneInfo(time_zone)))
    next_scheduled_at:datetime = DatetimeUtil.get_next_time_slot(scheduled_at, 
                                                    days, 
                                                    now=datetime.now(), 
                                                    additional_delta=timedelta(seconds=1))

    now_utc:datetime = DatetimeUtil.convert_utc(datetime.now())
    next_scheduled_at_utc:datetime = DatetimeUtil.convert_utc(next_scheduled_at)
#    if (next_scheduled_at <= scheduled_at):
    if (next_scheduled_at_utc <= now_utc):
        print("")

    now:datetime = datetime(2023,2,22, 8,36,0)
    tzinfo = ZoneInfo("Australia/Adelaide")
    time_local = time(hour=8, minute=0, second=0, tzinfo=ZoneInfo("Australia/Adelaide"))
    scheduled_at:datetime = datetime.combine(now, time_local)
#    scheduled_at -= timedelta(days=1)
    print(str(scheduled_at))
    output:datetime = DatetimeUtil.get_next_time_slot(scheduled_at, days, now)
    print(str(output))
    if (output <= scheduled_at):
        output += timedelta(days=1)
    print(str(output))

    now:datetime = datetime(2022,4,29, 14,36,0)
    days:List[int] = [0,1,2,3,4,5,6]
    test_day:datetime = datetime(2022,4,29, 12,36,0)
    output:datetime = DatetimeUtil.get_next_time_slot(test_day, days, now)
    print(str(output))

    res:bool = required_output == output


    days:List[int] = [1, 2, 3, 4, 5] #[1, 2, 0]
    test_day:datetime = datetime(2022,4,3, 12,36,0)
    output:datetime = DatetimeUtil.get_next_time_slot(test_day, days, now)
    print(str(output))

#        scheduled_at:datetime = datetime.combine(self.datetime_provider.now(),
#                                    time(hour=time_of_day, minute=time_of_day_minute, second=0, tzinfo=ZoneInfo(time_zone)))
    time_zone:str = "Europe/Copenhagen"
    time_zone_hosting:str = "Europe/Dublin"
    time_of_day:int = 15
    time_of_day_minute:int = 38

    time_zone:str = "Europe/Kiev"
    tzinfo=ZoneInfo(time_zone_hosting)
    now_hosting:datetime = datetime.now(tzinfo)
    scheduled_at:datetime = datetime.combine(datetime.now(), #now_hosting,
                                    time(hour=time_of_day, minute=time_of_day_minute, second=0, tzinfo=ZoneInfo(time_zone)))
    print(str(now_hosting))
    print(str(scheduled_at))

    scheduled_at_utc:datetime = DatetimeUtil.convert_utc(scheduled_at)
    print(str(scheduled_at_utc))


    tzinfo=tz.gettz(time_zone_hosting)
    now_hosting:datetime = datetime.now(tzinfo)
    scheduled_at:datetime = datetime.combine(now_hosting,
                                    time(hour=time_of_day, minute=time_of_day_minute, second=0, tzinfo=tz.gettz(time_zone)))
    print(str(scheduled_at))
    days:List[int] = [0, 1, 2, 3, 4, 5, 6] #[1, 2, 0]
    output:datetime = DatetimeUtil.get_next_time_slot(scheduled_at, days, additional_delta=timedelta(seconds=1), now=now)
    print(str(output))

    scheduled_at:datetime = datetime.combine(datetime.now(),
                                    time(hour=time_of_day, minute=time_of_day_minute, second=0, tzinfo=tz.gettz(time_zone)))
    days:List[int] = [0, 1, 2, 3, 4, 5, 6] #[1, 2, 0]
    output:datetime = DatetimeUtil.get_next_time_slot(scheduled_at, days, now)
    print(str(scheduled_at))
    print(str(output))


    days:List[int] = [3, 4, 5] #[1, 2, 0]
    test_day:datetime = datetime(2022,3,24,11,15,0)
    output:datetime = DatetimeUtil.get_next_time_slot(test_day, days, now)
    print(str(output))

#    test_day:datetime = datetime(2022,2,22,11,0,0)
#    new_day:datetime = DatetimeUtil.get_next_day(test_day, days)

    next_weekend:datetime = DatetimeUtil.get_next_weekend_day(date(2022, 1, 1))
    print(next_weekend)
    next_weekend:datetime = DatetimeUtil.get_next_weekend_day(date(2022, 1, 2))
    print(next_weekend)
    
    next_weekday:datetime = DatetimeUtil.get_next_weekday(date(2022, 1, 1))
    print(next_weekday)