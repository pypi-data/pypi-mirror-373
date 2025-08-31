# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-07-17 22:32:37
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base methods.
"""


from reykit.rbase import Base


__all__ = (
    'WebBase',
    'API'
)


class WebBase(Base):
    """
    Web base type.
    """


class API(WebBase):
    """
    External API type.
    """
