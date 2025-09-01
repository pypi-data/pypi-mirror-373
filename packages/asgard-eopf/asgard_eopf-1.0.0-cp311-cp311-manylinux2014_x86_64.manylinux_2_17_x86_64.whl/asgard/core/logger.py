#!/usr/bin/env python
# coding: utf8
#
# Copyright 2023 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Utility functions for ASGARD loggers
"""


import logging
from abc import abstractmethod
from math import ceil, log10

import numpy as np

ASGARD_LOGGER_NAME = "asgard"


def initialize(name: str):
    """
    Default initialization of an ASGARD logger

    :param name: Name of the logger to initialize
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # formatter
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

    # console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


# =================


class ListFormatter:  # pylint: disable=too-few-public-methods
    """
    "Namespace" for list formatters
    """

    class Interface:  # pylint: disable=too-few-public-methods
        """
        Interface for all list formatters: they define the :meth:`format` method.
        """

        @abstractmethod
        def format(self, lst, crt_indent, indent) -> list[str]:
            """
            Format the list and returns the list of strings that'll be used by :func:`format_as_tree`.

            :param list lst:        List to format
            :param int  crt_indent: Indent level to use if new lines are required; ignored otherwise
            :param int  indent:     Indent increment when recursing, may be ignored.
            """

    class Typename(Interface):  # pylint: disable=too-few-public-methods
        """
        Specialization that only displays the list typename as well of the typename of the elements (if known)

        A typical output would be:

        .. code-block::

            ndarray[float64]
        """

        def format(self, lst, crt_indent, indent) -> list[str]:
            """
            Return the list typename and the typename of the elements -- if any.

            :param list lst:        List to format
            :param int  crt_indent: **Ignored**
            :param int  indent:     **Ignored**
            """
            elements_typename = lst[0].__class__.__name__ if len(lst) > 0 else "???"
            return [f"{lst.__class__.__name__}[{elements_typename}]"]

    class OneLine(Interface):  # pylint: disable=too-few-public-methods
        """
        Specialization that displays the first list elements.
        Dictionary and List elements will just be stringified
        => it's better to avoid this formatter for these composed types.

        A typical output would be:

        .. code-block::

            [ 8338.0, 8338.000347222222, 8338.000694444445, 8338.001041666666, 8338.00138888889, 8338.001736111111,...]
        """

        def __init__(self, max_list_elements=5):
            """
            Constructor...

            :param int max_list_elements: Maximum number of elements to display. If set to 0, all elements will be
                                          displayed.
            """
            self.__max_list_elements = max_list_elements

        def format(self, lst, crt_indent, indent) -> list[str]:
            """
            Return the first elements.

            :param list lst:        List to format
            :param int  crt_indent: **Ignored**
            :param int  indent:     **Ignored**
            """
            num = self.__max_list_elements if self.__max_list_elements > 0 else len(lst)
            res = ", ".join((f"{v!r}" for v in lst[:num]))
            if num != len(lst):
                res += ", ..."
            return [f"[{res}]"]

    class Expand(Interface):  # pylint: disable=too-few-public-methods
        """
        Specialization that expands the list elements: each element being displayed on a new line. Dictionary and List
        elements will be expanded.

        A typical output would be:

        .. code-block::

            [
                +- [0] -> 8338.0
                +- [1] -> 8338.000347222222
                +- [2] -> 8338.000694444445
                +- [3] -> 8338.001041666666
                +- [4] -> 8338.00138888889
                +- [5] -> 8338.001736111111
                +- ... plus 28796 other elements...
                ]
        """

        def __init__(self, max_list_elements=5):
            """
            Constructor...

            :param int max_list_elements: Maximum number of elements to display. If set to 0, all elements will be
                                          displayed.
            """
            self.__max_list_elements = max_list_elements

        def format(self, lst, crt_indent, indent) -> list[str]:
            res = []
            next_indent = crt_indent + indent
            lead = crt_indent * " " + "+- "
            num = self.__max_list_elements if self.__max_list_elements > 0 else len(lst)
            num_digits = int(ceil(log10(num)))
            fmt = f"{num_digits}d"
            for k, val in enumerate(lst):
                if k > num:
                    res.append(f"{lead}... plus {len(lst)-num} other elements...")
                    break
                # TODO: actually we may want another ListFormatter instead of self...
                sub_res = _format_as_tree(val, indent, next_indent, self)
                sub_res[0] = f"{lead}[{k:{fmt}}] -> {sub_res[0]}"
                res.extend(sub_res)
            return ["["] + res + [crt_indent * " " + "]"]


def _format_as_tree(val, indent, crt_indent, list_formatter: ListFormatter.Interface) -> list[str]:
    def _recurse_dict(dct, crt_indent) -> list[str]:
        res = []
        next_indent = crt_indent + indent
        lead = crt_indent * " " + "+- "
        max_length = max((len(k) for k in dct.keys()))
        for k, val in dct.items():
            right_padding = max_length - len(str(k)) + 1
            start = f"{lead}{k!r}{right_padding*' '}= "
            sub_res = _format_as_tree(
                val,
                indent,
                next_indent,
                list_formatter,
            )
            assert isinstance(sub_res, list)
            sub_res[0] = f"{start}{sub_res[0]}"
            res.extend(sub_res)
        return res

    next_indent = crt_indent + indent
    if isinstance(val, (list, np.ndarray)):
        return list_formatter.format(val, crt_indent, indent)
    if isinstance(val, dict):
        return ["{"] + _recurse_dict(val, next_indent) + [(next_indent) * " " + "}"]
    return [f"{val!r}"]


def format_as_tree(
    val,
    indent=4,
    crt_indent=0,
    list_formatter: ListFormatter.Interface | None = None,
) -> str:
    """
    Helper function to display dictionary structures.
    A bit like :func:`pprint.format`, but much more readable.

    :param                         val:            Value to format.
    :param int                     indent:         Indent increment when recursing.
    :param int                     crt_indent:     Indent level to use when new lines are required.
    :param ListFormatter.Interface list_formatter: Dictates how all lists are displayed.
                                                   Default: ``ListFormatter.OneLine(5)``
    :return: A string ready to be printed/logged.
    :rtype: str

    A typical output would be:

    .. code-block::

        blabla {
            +- 'times'    = ndarray[float64]
            +- 'time_ref' = 'UTC'
            }


    """
    format_list = list_formatter or ListFormatter.OneLine(5)
    return "\n".join(_format_as_tree(val, indent=indent, crt_indent=crt_indent, list_formatter=format_list))
