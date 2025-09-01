# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 17:08:41
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Translate methods.
"""


from reykit.rnet import request


__all__ = (
    'trans_baidu',
    'trans'
)


def trans_baidu(text: str) -> str:
    """
    Use `fanyi.baidu.com` translated text.

    Parameters
    ----------
    text : Text to be translated.

    Retuens
    -------
    Translated text.
    """

    # Set parameter.
    url = 'https://fanyi.baidu.com/sug'
    data = {
        'kw': text
    }

    # Requests.
    response = request(url, data)
    response_data = response.json()['data']

    # Handle result.
    if not len(response_data):
        return
    translate_data = response_data[0]['v']
    translate_text = translate_data.split(';')[0].split('. ')[-1]

    return translate_text


def trans(text: str) -> str:
    """
    Translate text.

    Parameters
    ----------
    text : Text to be translated.

    Retuens
    -------
    Translated text.
    """

    # Set parameter.
    translate_func = [
        trans_baidu
    ]

    # Translate.
    for func in translate_func:
        translate_text = func(text)
        if translate_text is not None:
            return translate_text
