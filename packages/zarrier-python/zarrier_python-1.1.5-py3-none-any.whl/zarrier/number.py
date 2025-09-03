import typing
import collections


def addx(a, b):
    return [(ia + ib) for ia, ib in zip(a, b)]


def minusx(a, b):
    return roundx([(ia - ib) for ia, ib in zip(a, b)])


def absx(a):
    return [abs(ia) for ia in a]


def roundx(a, n=3):
    return [round(ia, n) for ia in a]
