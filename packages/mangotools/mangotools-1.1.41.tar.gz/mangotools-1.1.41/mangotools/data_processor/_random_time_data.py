# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import random
from datetime import date, timedelta, datetime

import time
from faker import Faker


class RandomTimeData:
    """ 随机时间类型测试数据 """
    faker = Faker(locale='zh_CN')

    @classmethod
    def time_now_ymdhms(cls, minute=0) -> str:
        """当前年月日时分秒,参数：minute（默认0）"""
        target_time = datetime.now() + timedelta(days=int(minute))
        return target_time.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def time_before_time(cls, days=1):
        """当今日之前的日期,参数：days（默认1）"""
        yesterday = datetime.now() - timedelta(days=int(days))
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        return yesterday_str

    @classmethod
    def time_stamp(cls, minute=1) -> int:
        """几分钟后的时间戳, 参数：minute（默认1）"""
        return int(time.time() + 60 * int(minute)) * 1000

    @classmethod
    def time_now_ymd(cls) -> str:
        """当前年月日"""
        localtime = time.strftime("%Y-%m-%d", time.localtime())
        return localtime

    @classmethod
    def get_time_for_min(cls, minute=1) -> int:
        """获取几分钟后的时间戳 参数：minute（默认1）"""
        return int(time.time() + 60 * int(minute)) * 1000

    @classmethod
    def time_next_minute(cls, minute=1) -> str:
        """几分钟后的年月日时分秒 参数：分钟（默认1）"""
        future_time = datetime.now() + timedelta(minutes=int(minute))
        return future_time.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time_random_year(cls):
        """获取随机年份"""
        return cls.faker.year()

    @classmethod
    def time_random_month(cls):
        """获取随机月份"""
        return cls.faker.month()

    @classmethod
    def time_random_date(cls):
        """获取随机日期"""
        return cls.faker.date()

    @classmethod
    def time_now_int(cls) -> int:
        """获取当前时间戳整形"""
        return int(time.time()) * 1000

    @classmethod
    def time_future_datetime(cls):
        """未来的随机年月日时分秒"""
        return cls.faker.future_datetime()

    @classmethod
    def time_future_date(cls):
        """未来的随机年月日"""
        return cls.faker.future_date()

    @classmethod
    def time_today_date_00(cls):
        """获取今日00:00:00时间"""
        _today = date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def time_today_date_59(cls):
        """获取今日23:59:59时间"""
        _today = date.today().strftime("%Y-%m-%d") + " 23:59:59"
        return str(_today)

    @classmethod
    def time_after_week(cls):
        """获取一周后12点整的时间"""
        _time_after_week = (date.today() + timedelta(days=+6)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week

    @classmethod
    def time_after_month(cls):
        """获取30天后的12点整时间"""
        _time_after_week = (date.today() + timedelta(days=+30)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week

    @classmethod
    def time_day_reduce(cls, types=0) -> int:
        """获取今日日期的数字,参数：types（默认0）"""
        today = datetime.today()
        if types:
            return today.day - int(types)
        else:
            return today.day

    @classmethod
    def time_cron_time(cls, time_parts) -> str:
        """秒级cron表达式,参数：time_parts"""
        seconds = int(time_parts[0])
        minutes = int(time_parts[1])
        hours = int(time_parts[2])
        current_date = datetime.now().date()
        date_obj = datetime(year=current_date.year,
                            month=current_date.month,
                            day=current_date.day,
                            hour=hours,
                            minute=minutes,
                            second=seconds)

        time_str_result = date_obj.strftime("%H:%M:%S")
        return time_str_result

    @classmethod
    def time_next_minute_cron(cls, minutes=1):
        """按周重复的cron表达式,参数：minutes（默认1）"""
        now = datetime.now() + timedelta(minutes=float(minutes))
        second = f"{now.second:02d}"  # 格式化为两位数
        minute = f"{now.minute:02d}"  # 格式化为两位数
        hour = f"{now.hour:02d}"  # 格式化为两位数
        day = "?"  # 日用问号表示不指定
        month = "*"  # 月用星号表示每个月
        weekday = str(date.today().weekday() + 2)
        return f"{second} {minute} {hour} {day} {month} {weekday}"

    @classmethod
    def time_random_year_str(cls):
        """随机年份字符串"""
        return str(cls.faker.year())

    @classmethod
    def time_random_month_str(cls):
        """随机月份字符串（01-12）"""
        return f"{random.randint(1, 12):02d}"

    @classmethod
    def time_random_day_str(cls):
        """随机日字符串（01-31）"""
        return f"{random.randint(1, 31):02d}"

    @classmethod
    def time_random_hour_str(cls):
        """随机小时字符串（00-23）"""
        return f"{random.randint(0, 23):02d}"

    @classmethod
    def time_random_minute_str(cls):
        """随机分钟字符串（00-59）"""
        return f"{random.randint(0, 59):02d}"

    @classmethod
    def time_random_second_str(cls):
        """随机秒字符串（00-59）"""
        return f"{random.randint(0, 59):02d}"

    @classmethod
    def time_random_ym(cls):
        """随机年月字符串（YYYY-MM）"""
        return f"{cls.faker.year()}-{random.randint(1, 12):02d}"

    @classmethod
    def time_random_ymd_str(cls):
        """随机年月日字符串（YYYY-MM-DD）"""
        return cls.faker.date()

    @classmethod
    def time_random_ymdhm_str(cls):
        """随机年月日时分字符串（YYYY-MM-DD HH:MM）"""
        dt = cls.faker.date_time()
        return dt.strftime('%Y-%m-%d %H:%M')

    @classmethod
    def time_random_ymdhms_str(cls):
        """随机年月日时分秒字符串（YYYY-MM-DD HH:MM:SS）"""
        dt = cls.faker.date_time()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time_random_hm_str(cls):
        """随机时分字符串（HH:MM）"""
        return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"

    @classmethod
    def time_random_hms_str(cls):
        """随机时分秒字符串（HH:MM:SS）"""
        return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

    @classmethod
    def time_random_timestamp_s(cls):
        """随机时间戳（秒）"""
        dt = cls.faker.date_time()
        return int(dt.timestamp())

    @classmethod
    def time_random_timestamp_ms(cls):
        """随机时间戳（毫秒）"""
        dt = cls.faker.date_time()
        return int(dt.timestamp() * 1000)

    @classmethod
    def time_random_timestamp_us(cls):
        """随机时间戳（微秒）"""
        dt = cls.faker.date_time()
        return int(dt.timestamp() * 1000000)

    @classmethod
    def time_random_iso8601(cls):
        """随机ISO8601时间字符串"""
        return cls.faker.iso8601()

    @classmethod
    def time_random_rfc3339(cls):
        """随机RFC3339时间字符串"""
        return cls.faker.date_time().isoformat()

    @classmethod
    def time_random_cron(cls):
        """随机cron表达式（分 时 日 月 周）"""
        minute = random.randint(0, 59)
        hour = random.randint(0, 23)
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        week = random.randint(0, 6)
        return f"{minute} {hour} {day} {month} {week}"

    @classmethod
    def time_random_future_ymd(cls):
        """未来随机年月日字符串"""
        return cls.faker.future_date().strftime('%Y-%m-%d')

    @classmethod
    def time_random_past_ymd(cls):
        """过去随机年月日字符串"""
        return cls.faker.past_date().strftime('%Y-%m-%d')

    @classmethod
    def time_random_future_ymdhms(cls):
        """未来随机年月日时分秒字符串"""
        return cls.faker.future_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time_random_past_ymdhms(cls):
        """过去随机年月日时分秒字符串"""
        return cls.faker.past_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def time_random_weekday(cls):
        """随机周几（中文）"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return random.choice(weekdays)

    @classmethod
    def time_random_weekday_num(cls):
        """随机周几（数字1-7）"""
        return random.randint(1, 7)

    @classmethod
    def time_random_quarter(cls):
        """随机季度（Q1-Q4）"""
        return f"Q{random.randint(1, 4)}"

    @classmethod
    def time_random_week(cls):
        """随机周数（1-53）"""
        return random.randint(1, 53)

    @classmethod
    def time_random_time_diff_days(cls):
        """随机天数时间差字符串（如'3天'）"""
        days = random.randint(1, 365)
        return f"{days}天"

    @classmethod
    def time_random_time_diff_hms(cls):
        """随机时分秒时间差字符串（如'12:34:56'）"""
        return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

    @classmethod
    def time_random_12h(cls):
        """随机12小时制时间字符串（hh:MM:SS AM/PM）"""
        dt = cls.faker.date_time()
        return dt.strftime('%I:%M:%S %p')

    @classmethod
    def time_random_24h(cls):
        """随机24小时制时间字符串（HH:MM:SS）"""
        dt = cls.faker.date_time()
        return dt.strftime('%H:%M:%S')

    @classmethod
    def time_random_boundary_1970(cls):
        """1970-01-01 00:00:00"""
        return '1970-01-01 00:00:00'

    @classmethod
    def time_random_boundary_2038(cls):
        """2038-01-19 03:14:07（32位时间戳溢出临界）"""
        return '2038-01-19 03:14:07'

    @classmethod
    def time_random_boundary_9999(cls):
        """9999-12-31 23:59:59"""
        return '9999-12-31 23:59:59'

    @classmethod
    def time_random_leap_year(cls):
        """随机闰年（如2020）"""
        leap_years = [y for y in range(1900, 2101) if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)]
        return str(random.choice(leap_years))

    @classmethod
    def time_random_non_leap_year(cls):
        """随机平年（非闰年）"""
        years = [y for y in range(1900, 2101) if not ((y % 4 == 0 and y % 100 != 0) or (y % 400 == 0))]
        return str(random.choice(years))

    @classmethod
    def time_random_dst_date(cls):
        """随机夏令时日期（如美国）"""
        # 3月第2个周日到11月第1个周日
        year = random.randint(2000, 2030)
        march = datetime(year, 3, 1)
        first_sunday = march + timedelta(days=(6 - march.weekday()) % 7)
        second_sunday = first_sunday + timedelta(days=7)
        return second_sunday.strftime('%Y-%m-%d')

    @classmethod
    def time_random_holiday(cls):
        """随机中国法定节假日日期（字符串）"""
        holidays = ['2023-01-01', '2023-01-22', '2023-04-05', '2023-05-01', '2023-06-22', '2023-10-01']
        return random.choice(holidays)

    @classmethod
    def time_random_workday(cls):
        """随机工作日（周一到周五）"""
        days = ["周一", "周二", "周三", "周四", "周五"]
        return random.choice(days)

    @classmethod
    def time_random_weekend(cls):
        """随机周末（周六或周日）"""
        return random.choice(["周六", "周日"])

    @classmethod
    def time_random_time_range_str(cls):
        """随机时间区间字符串（如'2023-01-01~2023-01-31'）"""
        start = cls.faker.date_this_year()
        end = cls.faker.future_date(end_date='+30d')
        return f"{start}~{end}"

    @classmethod
    def time_random_time_diff_seconds(cls):
        """随机秒数时间差字符串（如'3600秒'）"""
        seconds = random.randint(1, 86400)
        return f"{seconds}秒"

    @classmethod
    def time_random_time_diff_minutes(cls):
        """随机分钟数时间差字符串（如'120分钟'）"""
        minutes = random.randint(1, 1440)
        return f"{minutes}分钟"

    @classmethod
    def time_random_time_diff_hours(cls):
        """随机小时数时间差字符串（如'12小时'）"""
        hours = random.randint(1, 48)
        return f"{hours}小时"

    @classmethod
    def time_random_time_diff_weeks(cls):
        """随机周数时间差字符串（如'3周'）"""
        weeks = random.randint(1, 52)
        return f"{weeks}周"

    @classmethod
    def time_random_time_diff_months(cls):
        """随机月数时间差字符串（如'6个月'）"""
        months = random.randint(1, 12)
        return f"{months}个月"

    @classmethod
    def time_random_time_diff_years(cls):
        """随机年数时间差字符串（如'2年'）"""
        years = random.randint(1, 10)
        return f"{years}年"

    @classmethod
    def time_random_utcnow(cls):
        """当前UTC时间字符串（YYYY-MM-DD HH:MM:SSZ）"""
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    def time_random_utc_offset(cls):
        """随机UTC偏移字符串（如+08:00）"""
        sign = random.choice(['+', '-'])
        hour = random.randint(0, 14)
        minute = random.choice([0, 30, 45])
        return f"{sign}{hour:02d}:{minute:02d}"

    @classmethod
    def time_random_rfc2822(cls):
        """随机RFC2822时间字符串"""
        return cls.faker.date_time().strftime('%a, %d %b %Y %H:%M:%S +0000')

    @classmethod
    def time_random_rfc850(cls):
        """随机RFC850时间字符串"""
        return cls.faker.date_time().strftime('%A, %d-%b-%y %H:%M:%S GMT')

    @classmethod
    def time_random_rfc1123(cls):
        """随机RFC1123时间字符串"""
        return cls.faker.date_time().strftime('%a, %d %b %Y %H:%M:%S GMT')

    @classmethod
    def time_random_rfc1036(cls):
        """随机RFC1036时间字符串"""
        return cls.faker.date_time().strftime('%A, %d-%b-%y %H:%M:%S GMT')

    @classmethod
    def time_random_rfc822(cls):
        """随机RFC822时间字符串"""
        return cls.faker.date_time().strftime('%a, %d %b %y %H:%M:%S +0000')

    @classmethod
    def time_random_rfc3339nano(cls):
        """随机RFC3339纳秒时间字符串"""
        dt = cls.faker.date_time()
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    @classmethod
    def cron_every_minute(cls):
        """每分钟执行一次"""
        return '* * * * *'

    @classmethod
    def cron_every_hour(cls):
        """每小时执行一次"""
        return '0 * * * *'

    @classmethod
    def cron_every_day(cls):
        """每天执行一次（0点）"""
        return '0 0 * * *'

    @classmethod
    def cron_every_week(cls):
        """每周执行一次（周日0点）"""
        return '0 0 * * 0'

    @classmethod
    def cron_every_month(cls):
        """每月执行一次（1号0点）"""
        return '0 0 1 * *'

    @classmethod
    def cron_every_year(cls):
        """每年执行一次（1月1日0点）"""
        return '0 0 1 1 *'

    @classmethod
    def cron_every_workday(cls):
        """每个工作日执行一次（周一到周五0点）"""
        return '0 0 * * 1-5'

    @classmethod
    def cron_every_weekend(cls):
        """每个周末执行一次（周六、周日0点）"""
        return '0 0 * * 6,0'

    @classmethod
    def cron_every_5_minutes(cls):
        """每5分钟执行一次"""
        return '*/5 * * * *'

    @classmethod
    def cron_every_2_hours(cls):
        """每2小时执行一次"""
        return '0 */2 * * *'

    @classmethod
    def cron_every_3_days(cls):
        """每3天执行一次（0点）"""
        return '0 0 */3 * *'

    @classmethod
    def cron_last_day_of_month(cls):
        """每月最后一天执行一次（0点）"""
        return '0 0 L * *'

    @classmethod
    def cron_first_workday_of_month(cls):
        """每月第一个工作日执行一次（0点）"""
        return '0 0 1W * *'

    @classmethod
    def cron_at_3am_every_day(cls):
        """每天3点执行一次"""
        return '0 3 * * *'

    @classmethod
    def cron_at_12_30_every_day(cls):
        """每天12:30执行一次"""
        return '30 12 * * *'

    @classmethod
    def cron_at_random_time_every_day(cls):
        """每天随机时间点执行一次"""
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        return f'{minute} {hour} * * *'

    @classmethod
    def cron_at_random_day_every_month(cls):
        """每月随机一天0点执行一次"""
        day = random.randint(1, 28)
        return f'0 0 {day} * *'

    @classmethod
    def cron_at_random_weekday_every_week(cls):
        """每周随机一天0点执行一次"""
        weekday = random.randint(0, 6)
        return f'0 0 * * {weekday}'

    @classmethod
    def cron_at_midnight(cls):
        """每天0点执行一次"""
        return '0 0 * * *'

    @classmethod
    def cron_at_noon(cls):
        """每天12点执行一次"""
        return '0 12 * * *'

    @classmethod
    def cron_at_23_59(cls):
        """每天23:59执行一次"""
        return '59 23 * * *'

    @classmethod
    def cron_at_0_12_18(cls):
        """每天0点、12点、18点执行"""
        return '0 0,12,18 * * *'

    @classmethod
    def cron_every_hour_on_half(cls):
        """每小时半点执行一次"""
        return '30 * * * *'

    @classmethod
    def cron_at_8_12_18(cls):
        """每天8点、12点、18点执行"""
        return '0 8,12,18 * * *'

    @classmethod
    def cron_on_1_15_last_day(cls):
        """每月1号、15号、最后一天执行（0点）"""
        return '0 0 1,15,L * *'

    @classmethod
    def cron_first_day_of_quarter(cls):
        """每季度第一天0点执行"""
        return '0 0 1 1,4,7,10 *'

    @classmethod
    def cron_first_day_of_year(cls):
        """每年第一天0点执行"""
        return '0 0 1 1 *'
