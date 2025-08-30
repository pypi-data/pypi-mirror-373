#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/04 07:14
# @Author  : Wu_RH
# @FileName: impl_obj.py

from ..utils import tool

from ..abs.board import PositionTag
from ..abs.Mrule import MinesTag, ValueCircle
from ..abs.Rrule import ValueQuess, ValueCross

POSITION_TAG = PositionTag()
MINES_TAG = MinesTag(POSITION_TAG)
VALUE_QUESS = ValueQuess(POSITION_TAG)
VALUE_CIRCLE = ValueCircle(POSITION_TAG)
VALUE_CROSS = ValueCross(POSITION_TAG)

TOTAL = -1


def set_total(total: int):
    global TOTAL
    TOTAL = total


def get_total() -> int:
    return TOTAL


def get_seed():
    return tool.SEED
