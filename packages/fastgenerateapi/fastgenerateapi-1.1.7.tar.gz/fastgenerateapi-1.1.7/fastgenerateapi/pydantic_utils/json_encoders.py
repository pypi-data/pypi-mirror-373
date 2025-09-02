from datetime import datetime, date, time


def new_datetime_type(name, format_str=""):
    return type(name, (datetime,), dict(format_str=format_str))


def new_date_type(name, format_str=""):
    return type(name, (date,), dict(format_str=format_str))


def new_time_type(name, format_str=""):
    return type(name, (time,), dict(format_str=format_str))


# Common datetime format
DATETIME_FORMAT_COMMON = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_COMMON_CN = "%Y年%m月%d日 %H时%M分%S秒"
DATETIME_NOS_FORMAT = "%Y-%m-%d %H:%M"
DATETIME_NOS_FORMAT_CN = "%Y年%m月%d日 %H时%M分"
DATE_FORMAT_COMMON = "%Y-%m-%d"
DATE_FORMAT_COMMON_CN = "%Y年%m月%d日"
TIME_FORMAT_COMMON = "%H:%M"
TIME_FORMAT_12H_MODE = "%I:%M"
TIME_FORMAT_12H_MODE_WITH_SUFFIX = "%I:%M(%p)"
TIME_FORMAT_TIME_COMMON = "%H:%M:%S"

# Common datetime format
common_format_datetime = new_datetime_type("COMMON_FORMAT_DATETIME", format_str=DATETIME_FORMAT_COMMON)
common_cn_format_datetime = new_datetime_type("COMMON_CN_FORMAT_DATETIME", format_str=DATETIME_FORMAT_COMMON_CN)
nos_format_datetime = new_datetime_type("NOS_FORMAT_DATETIME", format_str=DATETIME_NOS_FORMAT)
nos_cn_format_datetime = new_datetime_type("NOS_CN_FORMAT_DATETIME", format_str=DATETIME_NOS_FORMAT_CN)
common_format_date = new_date_type("COMMON_FORMAT_DATE", format_str=DATE_FORMAT_COMMON)
common_cn_format_date = new_date_type("COMMON_CN_FORMAT_DATE", format_str=DATE_FORMAT_COMMON_CN)
common_format_time = new_time_type("COMMON_FORMAT_TIME", format_str=TIME_FORMAT_COMMON)
h12_mode_format_time = new_time_type("H12_MODE_FORMAT_TIME", format_str=TIME_FORMAT_12H_MODE)
h12_mode_with_suffix_format_time = new_time_type("H12_MODE_WITH_SUFFIX_FORMAT_TIME",
                                                 format_str=TIME_FORMAT_12H_MODE_WITH_SUFFIX)
common_format_with_s_time = new_time_type("COMMON_FORMAT_WITH_S_TIME", format_str=TIME_FORMAT_TIME_COMMON)

JSON_ENCODERS = {
    time: lambda v: v.strftime(TIME_FORMAT_TIME_COMMON),
    date: lambda v: v.strftime(DATE_FORMAT_COMMON),
    # datetime: lambda v: v.strftime(DATETIME_FORMAT_COMMON),
    datetime: lambda v: int(v.timestamp() * 1000),

    # special date type
    common_format_datetime: lambda v: v.strftime(v.format_str),
    common_cn_format_datetime: lambda v: v.strftime(v.format_str),
    nos_format_datetime: lambda v: v.strftime(v.format_str),
    nos_cn_format_datetime: lambda v: v.strftime(v.format_str),
    common_format_date: lambda v: v.strftime(v.format_str),
    common_cn_format_date: lambda v: v.strftime(v.format_str),
    common_format_time: lambda v: v.strftime(v.format_str),
    h12_mode_format_time: lambda v: v.strftime(v.format_str),
    h12_mode_with_suffix_format_time: lambda v: v.strftime(v.format_str),
    common_format_with_s_time: lambda v: v.strftime(v.format_str),

}

