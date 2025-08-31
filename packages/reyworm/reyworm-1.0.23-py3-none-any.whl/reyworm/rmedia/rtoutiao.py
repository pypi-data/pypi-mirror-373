# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-22 14:06:05
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Toutiao methods.
"""


from typing import Any, Literal
from reykit.rnet import request


__all__ = (
    'get_toutiao_hot_search',
)


def get_toutiao_hot_search() -> list[dict[Literal['title', 'type', 'label', 'hot', 'url', 'image'], Any]]:
    """
    Get hot search table from `toutiao` website.

    Returns
    -------
    Hot search table.
        - `Key 'title'`: Hot search title.
        - `Key 'type'`: Hot search type list.
        - `Key 'label'`: Hot search label.
        - `Key 'hot'`: Hot search hot value.
        - `Key 'url'`: Hot search URL.
        - `Key 'image'`: Hot search image URL.
    """

    # Request.
    url = 'https://www.toutiao.com/hot-event/hot-board/'
    params = {'origin': 'toutiao_pc'}
    response = request(
        url,
        params,
        check=True
    )

    # Extract.
    response_json = response.json()
    table: list[dict] = response_json['data']

    # Convert.
    table = [
        {
            'title': info['Title'],
            'type': info.get('InterestCategory'),
            'label': info.get('LabelDesc'),
            'hot': int(info['HotValue']),
            'url': info['Url'],
            'image': info['Image']['url'],
        }
        for info in table
    ]
    sort_key = lambda row: row['hot']
    table.sort(key=sort_key, reverse=True)
    table = [
        {
            'rank': index,
            **row
        }
        for index, row in enumerate(table)
    ]

    return table
