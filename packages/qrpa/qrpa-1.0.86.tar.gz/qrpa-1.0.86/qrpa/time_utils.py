"""
时间工具模块
提供各种时间相关的工具函数，包括日期获取、格式化、转换、计算等功能
"""

import os
import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Tuple, List, Union


class TimeUtils:
    """时间工具类，提供各种时间相关的静态方法"""

    # ==================== 当前时间获取 ====================

    @staticmethod
    def get_current_date() -> str:
        """获取当前日期，格式为 YYYYMMDD"""
        return datetime.now().strftime('%Y%m%d')

    @staticmethod
    def get_current_datetime() -> str:
        """获取当前日期时间，格式为 YYYYMMDDHHMMSS"""
        return datetime.now().strftime('%Y%m%d%H%M%S')

    @staticmethod
    def current_datetime() -> str:
        """获取当前日期时间，格式为 YYYY-MM-DD HH:MM:SS"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def today_date() -> str:
        """获取今天的日期，格式为 YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def today_date_hour() -> str:
        """获取今天的日期和小时，格式为 YYYY-MM-DD_HH"""
        return datetime.now().strftime('%Y-%m-%d_%H')

    @staticmethod
    def get_current_year() -> int:
        """获取当前年份"""
        return datetime.now().year

    @staticmethod
    def get_current_month() -> int:
        """获取当前月份（1-12）"""
        return datetime.now().month

    @staticmethod
    def get_current_year_range() -> Tuple[str, str]:
        """获取当前年份的开始和结束日期"""
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1).strftime('%Y-%m-%d')
        end_date = datetime(current_year, 12, 31).strftime('%Y-%m-%d')
        return start_date, end_date

    # ==================== 相对日期获取 ====================

    @staticmethod
    def get_yesterday(dt: Optional[str] = None) -> str:
        """
        获取昨天的日期
        
        Args:
            dt: 可选的基础日期，格式为 YYYYMMDD，默认为今天
            
        Returns:
            昨天的日期，格式为 YYYY-MM-DD
        """
        if dt is None:
            dt = datetime.now()
        else:
            dt = datetime.strptime(dt, "%Y%m%d")
        yesterday = dt - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

    @staticmethod
    def before_yesterday() -> str:
        """获取前天的日期"""
        return (datetime.now().date() - timedelta(days=2)).strftime("%Y-%m-%d")

    @staticmethod
    def tomorrow_date() -> str:
        """获取明天的日期"""
        return (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")

    @staticmethod
    def get_last_month() -> int:
        """获取上个月的月份"""
        today = datetime.today()
        last_month = today.month - 1 if today.month > 1 else 12
        return last_month

    # ==================== 日期范围计算 ====================

    @staticmethod
    def get_past_7_days_range(start_from: Optional[str] = None, format_str: str = '%Y-%m-%d') -> Tuple[str, str,]:
        """
        获取过去7天的日期范围（包括结束日，共7天）
        
        Args:
            start_from: 可选的起始参考日期（格式 'YYYY-MM-DD'），默认以今天为起点
            
        Returns:
            (start_date_str, end_date_str) 日期范围元组
            
        Example:
            >>> get_past_7_days_range('2025-07-02')
            ('2025-06-25', '2025-07-01')
        """
        if start_from:
            try:
                base_date = datetime.strptime(start_from, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_from 格式必须是 'YYYY-MM-DD'")
        else:
            base_date = datetime.today()

        end_date = base_date - timedelta(days=1)  # 默认昨天为结束
        start_date = end_date - timedelta(days=6)  # 往前推6天为开始

        return start_date.strftime(format_str), end_date.strftime(format_str)

    @staticmethod
    def get_past_7_days_range_format(start_from: Optional[str] = None, format_str: str = '%Y-%m-%d') -> Tuple[str, str]:
        """
        获取过去7天的日期范围（包括结束日，共7天），支持自定义格式
        
        Args:
            start_from: 可选的起始参考日期（格式 'YYYY-MM-DD'），默认以今天为起点
            format_str: 日期格式字符串
            
        Returns:
            (start_date_str, end_date_str) 日期范围元组
        """
        if start_from:
            try:
                base_date = datetime.strptime(start_from, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_from 格式必须是 'YYYY-MM-DD'")
        else:
            base_date = datetime.today()

        end_date = base_date - timedelta(days=1)  # 默认昨天为结束
        start_date = end_date - timedelta(days=6)  # 往前推6天为开始

        return start_date.strftime(format_str), end_date.strftime(format_str)

    @staticmethod
    def get_past_nth_day(n: int, start_from: Optional[str] = None, format_str: str = '%Y-%m-%d') -> str:
        """
        获取过去第n天的日期
        
        Args:
            n: 获取过去第n天的日期（n=1 表示昨天，n=2 表示前天，以此类推）
            start_from: 可选的起始参考日期（格式 'YYYY-MM-DD'），默认以今天为起点
            
        Returns:
            'YYYY-MM-DD' 格式的日期
            
        Example:
            >>> get_past_nth_day(29, '2025-07-02')
            '2025-06-03'
        """
        if start_from:
            try:
                base_date = datetime.strptime(start_from, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_from 格式必须是 'YYYY-MM-DD'")
        else:
            base_date = datetime.today()

        past_date = base_date - timedelta(days=n)
        return past_date.strftime(format_str)

    @staticmethod
    def get_past_n_days_list(n: int, start_from: Optional[str] = None) -> List[str]:
        """
        获取过去n天的日期列表，从最旧到最近的日期
        
        Args:
            n: 获取过去多少天
            start_from: 可选的起始参考日期（格式 'YYYY-MM-DD'），默认以今天为起点
            
        Returns:
            ['YYYY-MM-DD', ..., 'YYYY-MM-DD']，从旧到新排序
            
        Example:
            >>> get_past_n_days_list(7, '2025-07-02')
            ['2025-07-01', '2025-06-30', '2025-06-29', '2025-06-28', '2025-06-27', '2025-06-26', '2025-06-25']
        """
        if start_from:
            try:
                base_date = datetime.strptime(start_from, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_from 格式必须是 'YYYY-MM-DD'")
        else:
            base_date = datetime.today()

        return [
            (base_date - timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(1, n + 1)
        ]

    @staticmethod
    def get_past_7_days_list(start_from: Optional[str] = None) -> List[str]:
        """
        获取过去7天的日期列表（不包含 start_from 当天），共7天
        
        Args:
            start_from: 可选的起始参考日期（格式 'YYYY-MM-DD'），默认以今天为起点
            
        Returns:
            ['YYYY-MM-DD', ..., 'YYYY-MM-DD']，从旧到新排序
        """
        if start_from:
            try:
                base_date = datetime.strptime(start_from, '%Y-%m-%d')
            except ValueError:
                raise ValueError("start_from 格式必须是 'YYYY-MM-DD'")
        else:
            base_date = datetime.today()

        return [
            (base_date - timedelta(days=i)).strftime('%Y-%m-%d')
            for i in range(1, 8)
        ]

    @staticmethod
    def date_range(start_date: str, end_date: str) -> List[str]:
        """
        生成两个日期之间的日期列表
        
        Args:
            start_date: 开始日期，格式为YYYY-MM-DD
            end_date: 结束日期，格式为YYYY-MM-DD
            
        Returns:
            包含两个日期之间所有日期的列表，日期格式为YYYY-MM-DD
            
        Raises:
            ValueError: 当开始日期大于结束日期时
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start > end:
            raise ValueError("开始日期不能大于结束日期")

        date_list = []
        current_date = start
        while current_date <= end:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        return date_list

    @staticmethod
    def get_dates_from_first_of_month_to_yesterday() -> List[str]:
        """获取从本月第一天到昨天的日期列表"""
        today = datetime.today()
        first_day_of_month = today.replace(day=1)
        yesterday = today - timedelta(days=1)

        date_list = []
        current_date = first_day_of_month

        while current_date <= yesterday:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return date_list

    # ==================== 月份相关 ====================

    @staticmethod
    def get_last_month_range() -> Tuple[str, str]:
        """获取上个月的第一天和最后一天"""
        today = datetime.today()
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1

        first_day = datetime(year, last_month, 1)
        last_day = datetime(year, last_month, calendar.monthrange(year, last_month)[1])

        return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")

    @staticmethod
    def get_last_month_range_time_str() -> Tuple[str, str]:
        """获取上个月第一天和最后一天的时间字符串"""
        today = datetime.today()
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1

        first_day = datetime(year, last_month, 1, 0, 0, 0)
        last_day = datetime(year, last_month, calendar.monthrange(year, last_month)[1], 23, 59, 59)

        start_time_str = first_day.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = last_day.strftime("%Y-%m-%d %H:%M:%S")

        return start_time_str, end_time_str

    @staticmethod
    def get_last_month_range_time() -> Tuple[int, int]:
        """获取上个月第一天和最后一天的毫秒级时间戳"""
        today = datetime.today()
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1

        first_day = datetime(year, last_month, 1, 0, 0, 0)
        last_day = datetime(year, last_month, calendar.monthrange(year, last_month)[1], 23, 59, 59, 0)

        start_timestamp = int(first_day.timestamp() * 1000)
        end_timestamp = int(last_day.timestamp() * 1000)

        return start_timestamp, end_timestamp

    @staticmethod
    def is_in_month(time_str: str, month: int, fmt: str = "%Y-%m-%d") -> bool:
        """
        判断时间字符串是否在指定月份
        
        Args:
            time_str: 时间字符串
            month: 月份（1-12）
            fmt: 时间格式
            
        Returns:
            如果时间在指定月份返回True，否则返回False
        """
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.month == month
        except ValueError:
            return False

    # ==================== 星期相关 ====================

    @staticmethod
    def get_week_num() -> int:
        """获取当前是第几周"""
        today = date.today()
        week_num = today.isocalendar()[1]  # 返回 (year, week_num, weekday)
        return week_num

    @staticmethod
    def get_chinese_weekday(date_str: str) -> str:
        """
        根据输入的日期字符串返回中文星期几
        
        Args:
            date_str: 格式为'YYYY-MM-DD'的日期字符串
            
        Returns:
            中文星期几，如'星期一'
            
        Example:
            >>> get_chinese_weekday('2025-04-15')
            '星期二'
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday_num = date_obj.weekday()
            weekday_cn = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            return weekday_cn[weekday_num]
        except ValueError as e:
            raise ValueError(f"日期格式错误，请输入'YYYY-MM-DD'格式的日期字符串。错误详情: {str(e)}")

    @staticmethod
    def get_weekday_name(date_str: str) -> str:
        """获取中文星期名称（简短格式）"""
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return weekdays[date_obj.weekday()]

    # ==================== 时间段相关 ====================

    @staticmethod
    def get_period() -> str:
        """获取当前时间段（上午/下午/晚上）"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "上午"
        elif 12 <= hour < 18:
            return "下午"
        else:
            return "晚上"

    @staticmethod
    def get_period2() -> str:
        """获取当前时间段（AM/PM）"""
        now = datetime.now()
        period = now.strftime("%p")  # 返回AM或者PM
        return period

    # ==================== 时间戳转换 ====================

    @staticmethod
    def convert_timestamp_to_str(timestamp_ms: Optional[int]) -> str:
        """
        将毫秒时间戳转换为字符串
        
        Args:
            timestamp_ms: 毫秒时间戳
            
        Returns:
            格式化的时间字符串，如果输入为None则返回'-'
        """
        if timestamp_ms is None:
            return '-'
        timestamp_s = int(timestamp_ms) / 1000
        dt = datetime.fromtimestamp(timestamp_s)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def convert_timestamp_to_date(timestamp_ms: Union[int, float]) -> str:
        """
        将毫秒时间戳转换为日期字符串
        
        Args:
            timestamp_ms: 毫秒时间戳
            
        Returns:
            YYYY-MM-DD 格式的日期字符串
        """
        timestamp_s = timestamp_ms / 1000
        dt = datetime.fromtimestamp(timestamp_s)
        return dt.strftime('%Y-%m-%d')

    @staticmethod
    def get_start_timestamps(date_str: str) -> int:
        """
        获取指定日期的开始毫秒时间戳（00:00:00.000）
        
        Args:
            date_str: 格式为"YYYY-MM-DD"的日期字符串
            
        Returns:
            开始毫秒时间戳
        """
        start_of_day = datetime.strptime(date_str, "%Y-%m-%d")
        return int(start_of_day.timestamp() * 1000)

    @staticmethod
    def get_end_timestamps(date_str: str) -> int:
        """
        获取指定日期的结束毫秒时间戳（23:59:59.999）
        
        Args:
            date_str: 格式为"YYYY-MM-DD"的日期字符串
            
        Returns:
            结束毫秒时间戳
        """
        start_of_day = datetime.strptime(date_str, "%Y-%m-%d")
        end_of_day = start_of_day + timedelta(days=1) - timedelta(milliseconds=1)
        return int(end_of_day.timestamp() * 1000)

    # ==================== 日期格式转换 ====================

    @staticmethod
    def convert_datetime_to_date(datetime_str: str) -> str:
        """
        将格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串转换为 'YYYY-MM-DD' 格式的日期字符串
        
        Args:
            datetime_str: 时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            日期字符串，格式为 'YYYY-MM-DD'
            
        Example:
            >>> convert_datetime_to_date("2025-06-27 09:49:16")
            '2025-06-27'
        """
        try:
            dt_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            return dt_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"输入的时间字符串格式错误，需要 'YYYY-MM-DD HH:MM:SS' 格式，但得到: {datetime_str}")
            return datetime_str

    @staticmethod
    def date_trans(d_t: str) -> str:
        """
        无斜杠日期转成有斜杠日期
        
        Args:
            d_t: 格式为 YYYY-MM-DD 的日期字符串
            
        Returns:
            格式为 YYYYMMDD 的日期字符串
        """
        return datetime.strptime(d_t, "%Y-%m-%d").strftime("%Y%m%d")

    @staticmethod
    def format_date_cross_platform(date_str: str) -> str:
        """
        跨平台格式化日期
        
        Args:
            date_str: 格式为 YYYY-MM-DD 的日期字符串
            
        Returns:
            格式化后的日期字符串
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        import platform
        if platform.system() == "Windows":
            return date_obj.strftime("%Y/%#m/%#d")
        else:  # Linux, macOS等
            return date_obj.strftime("%Y/%-m/%-d")

    # ==================== 日期比较和判断 ====================

    @staticmethod
    def is_date_greater_or_equal(date_str: str) -> bool:
        """
        比较指定日期是否大于或等于今天的日期
        
        Args:
            date_str: 格式为YYYY-MM-DD的日期字符串
            
        Returns:
            如果指定日期大于或等于今天返回True，否则返回False
        """
        try:
            year, month, day = map(int, date_str.split('-'))
            input_date = date(year, month, day)
            today = date.today()
            return input_date >= today
        except ValueError:
            print("日期格式不正确，请使用YYYY-MM-DD格式")
            return False

    @staticmethod
    def is_yesterday(create_time_str: str, dt: Optional[str] = None) -> bool:
        """
        判断给定的时间字符串是否是昨天
        
        Args:
            create_time_str: 创建时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
            dt: 日期字符串，格式为 "%Y-%m-%d" 表示某一天，默认为今天
            
        Returns:
            如果 create_time_str 是昨天的日期，返回 True，否则返回 False
        """
        try:
            create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
            if dt is None:
                dt = datetime.now()
            else:
                dt = datetime.strptime(dt, "%Y%m%d")
        except ValueError:
            raise ValueError("时间字符串格式不正确，请使用正确的格式：'%Y-%m-%d %H:%M:%S' 和 '%Y-%m-%d'")

        yesterday = dt - timedelta(days=1)
        return create_time.date() == yesterday.date()

    @staticmethod
    def is_yesterday_date(date_str: str) -> bool:
        """
        判断给定的日期字符串是否是昨天
        
        Args:
            date_str: 日期字符串，格式为 "%Y-%m-%d"
            
        Returns:
            如果 date_str 是昨天的日期，返回 True，否则返回 False
        """
        try:
            create_time = datetime.strptime(date_str, "%Y-%m-%d")
            dt = datetime.now()
        except ValueError:
            raise ValueError("时间字符串格式不正确，请使用正确的格式：'%Y-%m-%d'")

        yesterday = dt - timedelta(days=1)
        return create_time.date() == yesterday.date()

    # ==================== 文件时间相关 ====================

    @staticmethod
    def get_file_mtime(file_path: str, to_str: bool = True, tz_offset: int = 8) -> Union[str, datetime]:
        """
        获取文件的修改时间
        
        Args:
            file_path: 文件路径
            to_str: 是否返回格式化字符串（默认 True）
            tz_offset: 时区偏移（默认东八区 +8）
            
        Returns:
            格式化时间字符串或 datetime 对象
            
        Raises:
            FileNotFoundError: 当文件不存在时
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        mtime = os.path.getmtime(file_path)
        tz = timezone(timedelta(hours=tz_offset))
        mtime_dt = datetime.fromtimestamp(mtime, tz=tz)

        return mtime_dt.strftime('%Y-%m-%d %H:%M:%S') if to_str else mtime_dt


# ==================== 便捷函数 ====================
# 为了保持向后兼容，提供一些便捷函数

def get_current_date() -> str:
    """获取当前日期，格式为 YYYYMMDD"""
    return TimeUtils.get_current_date()


def get_current_datetime() -> str:
    """获取当前日期时间，格式为 YYYYMMDDHHMMSS"""
    return TimeUtils.get_current_datetime()


def current_datetime() -> str:
    """获取当前日期时间，格式为 YYYY-MM-DD HH:MM:SS"""
    return TimeUtils.current_datetime()


def today_date() -> str:
    """获取今天的日期，格式为 YYYY-MM-DD"""
    return TimeUtils.today_date()


def today_date_hour() -> str:
    """获取今天的日期和小时，格式为 YYYY-MM-DD_HH"""
    return TimeUtils.today_date_hour()


def get_yesterday(dt: Optional[str] = None) -> str:
    """获取昨天的日期"""
    return TimeUtils.get_yesterday(dt)


def tomorrow_date() -> str:
    """获取明天的日期"""
    return TimeUtils.tomorrow_date()


def before_yesterday() -> str:
    """获取前天的日期"""
    return TimeUtils.before_yesterday()


def get_current_year() -> int:
    """获取当前年份"""
    return TimeUtils.get_current_year()


def get_current_month() -> int:
    """获取当前月份"""
    return TimeUtils.get_current_month()


def get_last_month() -> int:
    """获取上个月的月份"""
    return TimeUtils.get_last_month()


def get_week_num() -> int:
    """获取当前是第几周"""
    return TimeUtils.get_week_num()


def get_period() -> str:
    """获取当前时间段（上午/下午/晚上）"""
    return TimeUtils.get_period()


def get_period2() -> str:
    """获取当前时间段（AM/PM）"""
    return TimeUtils.get_period2()


def get_chinese_weekday(date_str: str) -> str:
    """根据输入的日期字符串返回中文星期几"""
    return TimeUtils.get_chinese_weekday(date_str)


def get_weekday_name(date_str: str) -> str:
    """获取中文星期名称（简短格式）"""
    return TimeUtils.get_weekday_name(date_str)


def is_in_month(time_str: str, month: int, fmt: str = "%Y-%m-%d") -> bool:
    """判断时间字符串是否在指定月份"""
    return TimeUtils.is_in_month(time_str, month, fmt)


def date_trans(d_t: str) -> str:
    """无斜杠日期转成有斜杠日期"""
    return TimeUtils.date_trans(d_t)


def is_date_greater_or_equal(date_str: str) -> bool:
    """比较指定日期是否大于或等于今天的日期"""
    return TimeUtils.is_date_greater_or_equal(date_str)


def is_yesterday(create_time_str: str, dt: Optional[str] = None) -> bool:
    """判断给定的时间字符串是否是昨天"""
    return TimeUtils.is_yesterday(create_time_str, dt)


def is_yesterday_date(date_str: str) -> bool:
    """判断给定的日期字符串是否是昨天"""
    return TimeUtils.is_yesterday_date(date_str)


def get_file_mtime(file_path: str, to_str: bool = True, tz_offset: int = 8) -> Union[str, datetime]:
    """获取文件的修改时间"""
    return TimeUtils.get_file_mtime(file_path, to_str, tz_offset)


def convert_timestamp_to_str(timestamp_ms: Optional[int]) -> str:
    """将毫秒时间戳转换为字符串"""
    return TimeUtils.convert_timestamp_to_str(timestamp_ms)


def convert_timestamp_to_date(timestamp_ms: Union[int, float]) -> str:
    """将毫秒时间戳转换为日期字符串"""
    return TimeUtils.convert_timestamp_to_date(timestamp_ms)


def convert_datetime_to_date(datetime_str: str) -> str:
    """将格式为 'YYYY-MM-DD HH:MM:SS' 的时间字符串转换为 'YYYY-MM-DD' 格式的日期字符串"""
    return TimeUtils.convert_datetime_to_date(datetime_str)


def get_current_year_range() -> Tuple[str, str]:
    """获取当前年份的开始和结束日期"""
    return TimeUtils.get_current_year_range()


def get_start_timestamps(date_str: str) -> int:
    """获取指定日期的开始毫秒时间戳（00:00:00.000）"""
    return TimeUtils.get_start_timestamps(date_str)


def get_end_timestamps(date_str: str) -> int:
    """获取指定日期的结束毫秒时间戳（23:59:59.999）"""
    return TimeUtils.get_end_timestamps(date_str)


def format_date_cross_platform(date_str: str) -> str:
    """跨平台格式化日期"""
    return TimeUtils.format_date_cross_platform(date_str)


def get_past_7_days_range(start_from: Optional[str] = None) -> Tuple[str, str]:
    """获取过去7天的日期范围（包括结束日，共7天）"""
    return TimeUtils.get_past_7_days_range(start_from)


def get_past_7_days_range_format(start_from: Optional[str] = None, format_str: str = '%Y-%m-%d') -> Tuple[str, str]:
    """获取过去7天的日期范围（包括结束日，共7天），支持自定义格式"""
    return TimeUtils.get_past_7_days_range_format(start_from, format_str)


def get_past_nth_day(n: int, start_from: Optional[str] = None) -> str:
    """获取过去第n天的日期"""
    return TimeUtils.get_past_nth_day(n, start_from)


def get_past_n_days_list(n: int, start_from: Optional[str] = None) -> List[str]:
    """获取过去n天的日期列表，从最旧到最近的日期"""
    return TimeUtils.get_past_n_days_list(n, start_from)


def get_past_7_days_list(start_from: Optional[str] = None) -> List[str]:
    """获取过去7天的日期列表（不包含 start_from 当天），共7天"""
    return TimeUtils.get_past_7_days_list(start_from)


def date_range(start_date: str, end_date: str) -> List[str]:
    """生成两个日期之间的日期列表"""
    return TimeUtils.date_range(start_date, end_date)


def get_dates_from_first_of_month_to_yesterday() -> List[str]:
    """获取从本月第一天到昨天的日期列表"""
    return TimeUtils.get_dates_from_first_of_month_to_yesterday()


def get_last_month_range() -> Tuple[str, str]:
    """获取上个月的第一天和最后一天"""
    return TimeUtils.get_last_month_range()


def get_last_month_range_time_str() -> Tuple[str, str]:
    """获取上个月第一天和最后一天的时间字符串"""
    return TimeUtils.get_last_month_range_time_str()


def get_last_month_range_time() -> Tuple[int, int]:
    """获取上个月第一天和最后一天的毫秒级时间戳"""
    return TimeUtils.get_last_month_range_time()


# 为了向后兼容，保留一些旧函数名
def get_past_7_days_range_old() -> Tuple[str, str]:
    """获取过去7天的日期范围（旧版本）"""
    end_date = datetime.today() - timedelta(days=1)  # 昨天为结束日期
    start_date = end_date - timedelta(days=6)  # 往前推6天为开始日期
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def get_past_7_days_list_old() -> List[str]:
    """获取过去7天的日期列表（旧版本）"""
    today = datetime.today()
    return [
        (today - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(1, 8)
    ]


if __name__ == "__main__":
    # 测试示例
    print(f"当前日期: {today_date()}")
    print(f"昨天: {get_yesterday()}")
    print(f"明天: {tomorrow_date()}")
    print(f"当前年份: {get_current_year()}")
    print(f"当前月份: {get_current_month()}")
    print(f"当前周数: {get_week_num()}")
    print(f"当前时间段: {get_period()}")
    print(f"中文星期: {get_chinese_weekday(today_date())}")

    # 测试日期范围
    start, end = get_past_7_days_range()
    print(f"过去7天范围: {start} 到 {end}")

    # 测试时间戳转换
    current_ts = int(datetime.now().timestamp() * 1000)
    print(f"当前时间戳: {current_ts}")
    print(f"时间戳转字符串: {convert_timestamp_to_str(current_ts)}")
    print(f"时间戳转日期: {convert_timestamp_to_date(current_ts)}")
