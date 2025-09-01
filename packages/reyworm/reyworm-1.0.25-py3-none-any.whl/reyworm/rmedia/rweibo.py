# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-22 14:06:05
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Weibo methods.
"""


from typing import Any, Literal
from fake_useragent import UserAgent
from reykit.rnet import request, join_url
from reykit.rtime import now


__all__ = (
    'get_weibo_hot_search',
)


def get_weibo_hot_search() -> list[dict[Literal['rank', 'time', 'title', 'type', 'hot', 'url'], Any]]:
    """
    Get hot search table from `weibo` website.

    Returns
    -------
    Hot search table.
        - `Key 'rank'`: Hot search rank.
        - `Key 'time'`: Hot search time.
        - `Key 'title'`: Hot search title.
        - `Key 'type'`: Hot search type.
        - `Key 'hot'`: Hot search hot value.
        - `Key 'url'`: Hot search URL.
    """

    # Request.
    url = 'https://weibo.com/ajax/side/searchBand'
    timestamp_second = int(now('timestamp') / 10)
    params = {
        'type': 'hot',
        'last_tab': 'hot',
        'last_table_time': timestamp_second
    }
    ua = UserAgent()
    headers = {
        'cookie': 'SUB=_2AkMfz4Opf8NxqwFRmvoWyGPnZIh0zA_EieKpk3JyJRMxHRl-yT9yqmEItRB6NE-teHuyVk5ZEiU3azHTQckY6H3Ale7I; '
            'XSRF-TOKEN=fijm7qRcprz35OqHAiOSs_s1; '
            'WBPSESS=aEftxDBVPukTPk6-ZoWBoFyWKR9WXuoQPJZmP-r3bkFMPJn3Wjg95F_I7ilFxmRpNYa5qqAbIcLktpnZwknv0Fhbp7wuHdtQY0torFGlZa26JERUGb_Bdbs5Lf-nW8nk',
        'referer': 'https://weibo.com/newlogin?tabtype=weibo&gid=102803&openLoginLayer=0&url=https%3A%2F%2Fwww.weibo.com%2F',
        'user-agent': ua.edge,
    }
    response = request(url, params, headers=headers, check=True)

    # Extract.
    response_json = response.json()
    table: list[dict] = response_json['data']['realtime']

    # Convert.
    table = [
        {
            'title': info['word'],
            'hot': info['num'],
            'url': join_url(
                'https://s.weibo.com/weibo',
                {'q': '#%s#' % info['word']}
            )
        }
        for info in table
        if 'flag' in info
    ]
    sort_key = lambda row: (
        0
        if row['hot'] is None
        else row['hot']
    )
    table.sort(key=sort_key, reverse=True)
    table = [
        {
            'rank': index,
            **row
        }
        for index, row in enumerate(table)
    ]

    return table
