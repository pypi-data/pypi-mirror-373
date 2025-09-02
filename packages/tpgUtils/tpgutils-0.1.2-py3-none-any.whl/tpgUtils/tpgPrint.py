#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  report_utilities.py
#
#  Copyright 2023 cswaim <cswaim@jcrl.net>

"""
    Common routines used by the reporting modules

    from src import report_utils as rptu
"""

from datetime import datetime, time

dt = datetime.now()
hd1_template = """ Date: {} {:^50} Time: {}"""
hd2_template = """             {:^50} """

col1_template = """ {}"""
col2_template = """ {}"""

def set_rpt_date(rpt_date: datetime | None = None ) -> None:
    """set the report date"""
    global dt
    if rpt_date is not None:
        dt = rpt_date

def print_header(hd1, hd2=None, col_hd1=None, col_hd2=None, fmt="std", fileobj=None):
    """print report header
        fmt=std will use the template
        fmt=None will just print the hd1, hd2 as passed
        fileobj defaults to sys.stdout
    """
    # set date if not set
    if dt is None:
        set_rpt_date()

    print("", file=fileobj)
    # print report headers
    if fmt == "std":
        print(hd1_template.format(dt.strftime("%y-%m-%d"), hd1, dt.strftime("%H:%M:%S")), file=fileobj)
    else:
        print(f"{hd1}", file=fileobj)
    if hd2 is not None:
        if fmt == "std":
            print(hd2_template.format(hd2), file=fileobj)
        else:
            print(f"{hd2}", file=fileobj)

    # print column headings
    if col_hd1 is not None:
        print(col1_template.format(col_hd1), file=fileobj)
    if col_hd2 is not None:
        print(col2_template.format(col_hd2), file=fileobj)

def print_dtl(line, fileobj=None, newline=True):
    """print detail report line"""
    if newline:
        print(line, file=fileobj)
    else:
        print(line, end="", file=fileobj)

