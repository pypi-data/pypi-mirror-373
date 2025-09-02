# -*- coding: utf-8 -*-

#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import datetime
import dateutil.parser
import re
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
import os
from holado_core.common.tools.converters.converter import Converter
from enum import Enum
from holado_python.common.enums import ArithmeticOperator
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import math
from decimal import Decimal
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


EPOCH_1970 = datetime.datetime(year=1970, month=1, day=1, tzinfo=datetime.timezone.utc)
EPOCH_JULIAN_CNES = datetime.datetime(year=1950, month=1, day=1, tzinfo=datetime.timezone.utc)
EPOCH_JULIAN_NASA = datetime.datetime(year=1968, month=5, day=24, tzinfo=datetime.timezone.utc)

FORMAT_DATETIME_ISO = '%Y-%m-%dT%H:%M:%S.%fZ'
FORMAT_DATETIME_ISO_SECONDS = '%Y-%m-%dT%H:%M:%SZ'
FORMAT_DATETIME_HUMAN_SECOND = '%Y-%m-%d %H:%M:%S'


class DurationUnit(str, Enum):
    # Nanosecond = "nanosecond"
    Microsecond = "microsecond"
    Millisecond = "millisecond"
    Second = "second"
    Minute = "minute"
    Hour = "hour"
    Day = "day"
    Week = "week"
    Month = "month"
    Year = "year"
    


class DateTime(object):
    
    __is_system_time_in_tai = None
    __is_system_time_expected_in_tai = None
    __utc_to_tai_timedelta = None
    
    def __init__(self):
        pass
    
    @classmethod
    def is_system_time_in_tai(cls):
        """Return if system time is in TAI (International Atomic Time)"""
        if cls.__is_system_time_in_tai is None:
            cls.__is_system_time_in_tai = Converter.to_boolean(os.getenv("HOLADO_SYSTEM_TIME_IS_IN_TAI", False))
        return cls.__is_system_time_in_tai
    
    @classmethod
    def now(cls):
        return datetime.datetime.now()
    
    @classmethod
    def utcnow(cls):
        if cls.is_system_time_in_tai():
            return datetime.datetime.utcnow() - cls.utc_to_tai_timedelta()
        else:
            return datetime.datetime.utcnow()
    
    @classmethod
    def tainow(cls):
        if cls.is_system_time_in_tai():
            return datetime.datetime.utcnow()
        else:
            return datetime.datetime.utcnow() + cls.utc_to_tai_timedelta()
    
    @classmethod
    def utc_to_tai_timedelta(cls):
        """Return the timedelta to add to an UTC datetime to obtain a TAI datetime.
        Note: Currently, only years 2020-2029 are managed"""
        if cls.__utc_to_tai_timedelta is None:
            cls.__utc_to_tai_timedelta = datetime.timedelta(seconds=37)
        return cls.__utc_to_tai_timedelta
    
    @classmethod
    def apply_delta_on_datetime(cls, date:datetime, operator:ArithmeticOperator, duration, duration_unit:DurationUnit) -> datetime:
        args={duration_unit.value+'s':duration}
        if duration_unit in [DurationUnit.Millisecond]:
            delta = timedelta(**args)
        else:
            delta = relativedelta(**args)
        
        if operator == ArithmeticOperator.Subtraction: 
            res = date - delta
        elif operator == ArithmeticOperator.Addition:
            res = date + delta
        else:
            raise TechnicalException(f"Unmanaged operator '{operator.value}'")
        
        return res
    
    ### Conversions to/from str
    
    @classmethod
    def is_str_datetime(cls, dt_str, dt_format=None):
        """Return if a string is a datetime of given format"""
        res = True
        try:
            DateTime.str_2_datetime(dt_str, dt_format)
        except (dateutil.parser._parser.ParserError, ValueError):
            res = False
        return res

    @classmethod
    def str_2_datetime(cls, dt_str, dt_format=None):
        """Convert string to datetime instance"""
        res = None
        if dt_format is None:
            res = dateutil.parser.parse(dt_str)
        else:
            res = datetime.datetime.strptime(dt_str, dt_format)
            # if res.tzinfo is None:
            #     res = res.replace(tzinfo=timezone.utc)
        return res

    @classmethod
    def str_2_timedelta(cls, dur_str):
        """Convert string to timedelta instance"""
        res = None
        dur_regex = re.compile(r"(\d+(?:\.\d*)?) (?:s|sec|seconds)")
        r = dur_regex.match(dur_str)
        if r:
            res = datetime.timedelta(seconds=float(r.group(1)))
        else:
            raise FunctionalException(r"Duration string must match pattern '\d+(\.\d*)? (s|sec|seconds)'")
        return res
    
    @classmethod
    def datetime_2_str(cls, dt_value, dt_format=None):
        res = None
        if dt_format is None:
            res = datetime.datetime.isoformat(dt_value)
        else:
            res = dt_value.strftime(dt_format)
        return res
    
    @classmethod
    def _get_datetime(cls, dt):
        res = None
        if dt is not None:
            if isinstance(dt, datetime.datetime):
                res = dt
            elif isinstance(dt, str):
                res = DateTime.str_2_datetime(dt)
            else:
                raise TechnicalException(f"Datetime can be a datetime, a str containing a datetime, or None")
        return res
    
    @classmethod
    def _get_epoch_datetime(cls, epoch):
        res = None
        if epoch is not None:
            if isinstance(epoch, datetime.datetime):
                res = epoch
            elif isinstance(epoch, str):
                if epoch in ['EPOCH_1970', 'EPOCH_JULIAN_CNES', 'EPOCH_JULIAN_NASA']:
                    res = eval(epoch)
                else:
                    res = DateTime.str_2_datetime(epoch)
            else:
                raise TechnicalException(f"Epoch can be a datetime, a str containing a datetime, a str containing an EPOCH name, or None")
        return res
        
    @classmethod
    def _get_timestamp(cls, ts):
        res = None
        if ts is not None:
            if isinstance(ts, float) or isinstance(ts, int):
                res = ts
            elif isinstance(ts, str) and (Converter.is_float(ts) or Converter.is_integer(ts)):
                res = Converter.to_float(ts)
            else:
                raise TechnicalException(f"Timestamp must be a float|int or a string containing a float|int (obtained type: {Typing.get_object_class_fullname(ts)})")
        return res
    
    
    ### Conversions to/from timestamp
    
    @classmethod
    def datetime_to_timestamp(cls, dt, epoch=None):
        dt = cls._get_datetime(dt)
        epoch = cls._get_epoch_datetime(epoch)
        
        if epoch is None:
            return dt.timestamp()
        else:
            return (dt - epoch).total_seconds()
    
    @classmethod
    def timestamp_to_datetime(cls, ts, epoch=None):
        """
        Convert timestamp to UTC datetime
        """
        ts = cls._get_timestamp(ts)
        epoch = cls._get_epoch_datetime(epoch)
        
        res = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        if epoch is not None:
            res = epoch + (res - EPOCH_1970)
        return res
    
    
    ### Conversions to/from (seconds, nanos)
    
    @classmethod
    def datetime_to_seconds_nanos(cls, dt, epoch=None):
        ts = cls.datetime_to_timestamp(dt, epoch)
        return cls.timestamp_to_seconds_nanos(ts)
    
    @classmethod
    def seconds_nanos_to_datetime(cls, seconds, nanos, epoch=None, round_func=round):
        """
        Convert timestamp to UTC datetime
        @param round_func: defines the rounding method applied to microseconds (default: round ; possible methods: round, math.ceil, math.trunc)
        """
        ts = cls.seconds_nanos_to_timestamp(seconds, nanos, round_func=round_func)
        return cls.timestamp_to_datetime(ts, epoch)
    
    @classmethod
    def timestamp_to_seconds_nanos(cls, ts):
        return round(ts), round(ts * 1e6 % 1e6)
    
    @classmethod
    def seconds_nanos_to_timestamp(cls, seconds, nanos, cast_func=float, round_func=round):
        """
        Convert (seconds, nanos) to timestamp.
        By default, it returns a timestamp as float with nanos rounded to microsecond precision.
        To keep nanosecond precision, set cast_func=None and round_func=None, it will returns a timestamp as decimal.Decimal.
        @param cast_func: Type of the returned value (default: float). If None, no cast is applied, and result is of type decimal.Decimal, usefull to keep nanosecond precision.
        @param round_func: defines the rounding method applied to microseconds (default: round ; possible methods: round, math.ceil, math.trunc). If None, value is not rounded.
        """
        res_dec = Decimal(seconds) + Decimal(nanos) / Decimal(1e9)
        if round_func is not None:
            res_dec = round_func(res_dec * 1000000) / 1000000
        if cast_func is not None:
            return cast_func(res_dec)
        else:
            return res_dec
    
    
    ### Conversions to/from Julian date
    
    @classmethod
    def datetime_to_julian_date(cls, dt, epoch=None):
        if epoch is None:
            return cls.datetime_to_julian_date(dt, epoch=EPOCH_JULIAN_CNES) + 2433282.5
        else:
            td = (dt - epoch)
            return td.days + td.seconds / (3600 * 24)
        
    @classmethod
    def julian_date_to_datetime(cls, jd, epoch=None, precision_nb_digits=6):
        """ Convert a Julian date to a datetime instance
        @param precision_nb_digits Precision of the Julian date (default: 6 = microseconds)
        """
        if epoch is None:
            return cls.julian_date_to_datetime(jd - 2433282.5, epoch=EPOCH_JULIAN_CNES)
        else:
            jd_decimal, jd_days = math.modf(jd)
            jd_seconds = round(jd_decimal * 3600 * 24, precision_nb_digits)
            td = datetime.timedelta(days=round(jd_days), seconds=jd_seconds)
            return epoch + td
        
    @classmethod
    def datetime_utc_to_tai(cls, dt, dt_format=None):
        """ Convert a datetime in UTC to a datetime in TAI
        @param dt Datetime in UTC
        @param dt_format Format to use if 'dt' is a string (can be None for format autodetection)
        """
        dt_src = dt
        if isinstance(dt_src, str):
            dt_src = cls.str_2_datetime(dt_src, dt_format)
        
        return dt_src + DateTime.utc_to_tai_timedelta()
    
    @classmethod
    def datetime_tai_to_utc(cls, dt, dt_format=None):
        """ Convert a datetime in TAI to a datetime in UTC
        @param dt Datetime in TAI
        @param dt_format Format to use if 'dt' is a string (can be None for format autodetection)
        """
        dt_src = dt
        if isinstance(dt_src, str):
            dt_src = cls.str_2_datetime(dt_src, dt_format)
        
        return dt_src - DateTime.utc_to_tai_timedelta()
        
        
        
        
        
        