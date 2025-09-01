"""
时间工具模块使用示例
展示如何使用 time_utils.py 中的各种时间相关函数
"""

from time_utils import TimeUtils, today_date, get_yesterday, get_current_year


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 获取当前时间信息
    print(f"当前日期: {today_date()}")
    print(f"昨天: {get_yesterday()}")
    print(f"当前年份: {get_current_year()}")
    print(f"当前周数: {TimeUtils.get_week_num()}")
    print(f"当前时间段: {TimeUtils.get_period()}")
    print(f"中文星期: {TimeUtils.get_chinese_weekday(today_date())}")


def example_date_ranges():
    """日期范围计算示例"""
    print("\n=== 日期范围计算示例 ===")
    
    # 获取过去7天的日期范围
    start, end = TimeUtils.get_past_7_days_range()
    print(f"过去7天范围: {start} 到 {end}")
    
    # 获取过去7天的日期列表
    dates = TimeUtils.get_past_7_days_list()
    print(f"过去7天列表: {dates}")
    
    # 获取指定日期范围
    date_list = TimeUtils.date_range('2025-01-01', '2025-01-05')
    print(f"2025年1月1-5日: {date_list}")
    
    # 获取上个月范围
    last_month_start, last_month_end = TimeUtils.get_last_month_range()
    print(f"上个月范围: {last_month_start} 到 {last_month_end}")


def example_timestamp_conversion():
    """时间戳转换示例"""
    print("\n=== 时间戳转换示例 ===")
    
    from datetime import datetime
    
    # 获取当前时间戳
    current_ts = int(datetime.now().timestamp() * 1000)
    print(f"当前时间戳: {current_ts}")
    
    # 时间戳转字符串
    time_str = TimeUtils.convert_timestamp_to_str(current_ts)
    print(f"时间戳转字符串: {time_str}")
    
    # 时间戳转日期
    date_str = TimeUtils.convert_timestamp_to_date(current_ts)
    print(f"时间戳转日期: {date_str}")
    
    # 获取指定日期的开始和结束时间戳
    start_ts = TimeUtils.get_start_timestamps('2025-01-01')
    end_ts = TimeUtils.get_end_timestamps('2025-01-01')
    print(f"2025-01-01 开始时间戳: {start_ts}")
    print(f"2025-01-01 结束时间戳: {end_ts}")


def example_date_comparison():
    """日期比较示例"""
    print("\n=== 日期比较示例 ===")
    
    # 判断日期是否大于等于今天
    is_future = TimeUtils.is_date_greater_or_equal('2025-12-31')
    print(f"2025-12-31 是否大于等于今天: {is_future}")
    
    # 判断是否是昨天
    is_yesterday = TimeUtils.is_yesterday_date('2025-01-01')
    print(f"2025-01-01 是否是昨天: {is_yesterday}")
    
    # 判断时间是否在指定月份
    in_month = TimeUtils.is_in_month('2025-01-15', 1)
    print(f"2025-01-15 是否在1月: {in_month}")


def example_date_formatting():
    """日期格式化示例"""
    print("\n=== 日期格式化示例 ===")
    
    # 日期格式转换
    date_with_slash = TimeUtils.date_trans('2025-01-01')
    print(f"2025-01-01 转换为: {date_with_slash}")
    
    # 跨平台格式化
    cross_platform = TimeUtils.format_date_cross_platform('2025-01-01')
    print(f"跨平台格式化: {cross_platform}")
    
    # 时间字符串转日期
    date_only = TimeUtils.convert_datetime_to_date('2025-01-01 12:30:45')
    print(f"时间字符串转日期: {date_only}")


def example_advanced_usage():
    """高级使用示例"""
    print("\n=== 高级使用示例 ===")
    
    # 获取过去第n天的日期
    past_5th_day = TimeUtils.get_past_nth_day(5)
    print(f"过去第5天: {past_5th_day}")
    
    # 获取过去n天的日期列表
    past_10_days = TimeUtils.get_past_n_days_list(10)
    print(f"过去10天列表: {past_10_days}")
    
    # 获取从本月第一天到昨天的日期列表
    month_dates = TimeUtils.get_dates_from_first_of_month_to_yesterday()
    print(f"本月到昨天的日期: {month_dates}")
    
    # 获取上个月的时间范围（字符串格式）
    last_month_start_str, last_month_end_str = TimeUtils.get_last_month_range_time_str()
    print(f"上个月时间范围: {last_month_start_str} 到 {last_month_end_str}")
    
    # 获取上个月的时间范围（时间戳格式）
    last_month_start_ts, last_month_end_ts = TimeUtils.get_last_month_range_time()
    print(f"上个月时间戳范围: {last_month_start_ts} 到 {last_month_end_ts}")


def example_file_time():
    """文件时间相关示例"""
    print("\n=== 文件时间相关示例 ===")
    
    import os
    
    # 创建一个临时文件用于测试
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("test content")
    
    try:
        # 获取文件修改时间
        file_mtime = TimeUtils.get_file_mtime(test_file)
        print(f"文件修改时间: {file_mtime}")
        
        # 获取文件修改时间（datetime对象）
        file_mtime_dt = TimeUtils.get_file_mtime(test_file, to_str=False)
        print(f"文件修改时间(datetime): {file_mtime_dt}")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)


def example_weekday_functions():
    """星期相关函数示例"""
    print("\n=== 星期相关函数示例 ===")
    
    # 获取中文星期
    weekday_cn = TimeUtils.get_chinese_weekday('2025-01-01')
    print(f"2025-01-01 的中文星期: {weekday_cn}")
    
    # 获取简短星期名称
    weekday_short = TimeUtils.get_weekday_name('2025-01-01')
    print(f"2025-01-01 的简短星期: {weekday_short}")
    
    # 获取当前周数
    week_num = TimeUtils.get_week_num()
    print(f"当前是第 {week_num} 周")


def example_period_functions():
    """时间段相关函数示例"""
    print("\n=== 时间段相关函数示例 ===")
    
    # 获取当前时间段（中文）
    period_cn = TimeUtils.get_period()
    print(f"当前时间段(中文): {period_cn}")
    
    # 获取当前时间段（英文）
    period_en = TimeUtils.get_period2()
    print(f"当前时间段(英文): {period_en}")


def example_year_month_functions():
    """年月相关函数示例"""
    print("\n=== 年月相关函数示例 ===")
    
    # 获取当前年份
    current_year = TimeUtils.get_current_year()
    print(f"当前年份: {current_year}")
    
    # 获取当前月份
    current_month = TimeUtils.get_current_month()
    print(f"当前月份: {current_month}")
    
    # 获取上个月
    last_month = TimeUtils.get_last_month()
    print(f"上个月: {last_month}")
    
    # 获取当前年份范围
    year_start, year_end = TimeUtils.get_current_year_range()
    print(f"当前年份范围: {year_start} 到 {year_end}")


def example_relative_dates():
    """相对日期函数示例"""
    print("\n=== 相对日期函数示例 ===")
    
    # 获取昨天
    yesterday = TimeUtils.get_yesterday()
    print(f"昨天: {yesterday}")
    
    # 获取前天
    before_yesterday = TimeUtils.before_yesterday()
    print(f"前天: {before_yesterday}")
    
    # 获取明天
    tomorrow = TimeUtils.tomorrow_date()
    print(f"明天: {tomorrow}")
    
    # 基于指定日期获取昨天
    yesterday_from_date = TimeUtils.get_yesterday('20250101')
    print(f"基于2025-01-01的昨天: {yesterday_from_date}")


if __name__ == "__main__":
    """运行所有示例"""
    print("时间工具模块使用示例")
    print("=" * 50)
    
    example_basic_usage()
    example_date_ranges()
    example_timestamp_conversion()
    example_date_comparison()
    example_date_formatting()
    example_advanced_usage()
    example_file_time()
    example_weekday_functions()
    example_period_functions()
    example_year_month_functions()
    example_relative_dates()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")
