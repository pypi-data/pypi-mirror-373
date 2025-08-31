from enum import IntEnum


class Expiration(IntEnum):
    EXP_15SC = int(15)
    EXP_30SC = int(30)
    EXP_1MN = int(1 * 60)
    EXP_5MN = int(5 * 60)
    EXP_10MN = int(10 * 60)
    EXP_15MN = int(15 * 60)
    EXP_30MN = int(30 * 60)
    EXP_1HR = int(1 * 60 * 60)
    EXP_6HR = int(6 * 60 * 60)
    EXP_12HR = int(12 * 60 * 60)
    EXP_1DY = int(1 * 24 * 60 * 60)
    EXP_3DY = int(3 * 24 * 60 * 60)
    EXP_1WK = int(1 * 7 * 24 * 60 * 60)
    EXP_2WK = int(2 * 7 * 24 * 60 * 60)
    EXP_1MO = int(1 * 30 * 24 * 60 * 60)
