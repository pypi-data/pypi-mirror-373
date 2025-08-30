# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-08-25 15:37:50
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Douban methods.
"""


from typing import TypedDict
from bs4 import BeautifulSoup
from reydb.rdb import Database
from reykit.rbase import throw
from reykit.rnet import request
from reykit.rre import search, findall, sub

from ..rbase import WormCrawl


__all__ = (
    'WormDouban',
)


MediaRow = TypedDict(
    'MediaRow', 
    {
        'id': int,
        'type': str,
        'name': str,
        'score': float,
        'score_count': int,
        'image': str,
        'image_low': str,
        'episode': int | None,
        'episode_now': int | None,
        'year': int,
        'country': list[str],
        'class': list[str],
        'director': list[str] | None,
        'star': list[str] | None
    }
)
type MediaTable = list[MediaRow]
MediaInfo = TypedDict(
    'MediaInfo',
    {
        'type': str,
        'name': str,
        'year': int | None,
        'score': float,
        'score_count': int,
        'director': list[str] | None,
        'scriptwriter': list[str] | None,
        'star': list[str] | None,
        'class': list[str] | None,
        'country': list[str] | None,
        'language': list[str] | None,
        'premiere': dict[str, str] | None,
        'episode': int | None,
        'minute': int | None,
        'alias': list[str] | None,
        'imdb': str | None,
        'comment': list[str],
        'image': str,
        'image_low': str
    }
)


class WormDouban(WormCrawl):
    """
    Douban worm type.
    Can create database used `self.build` method.
    """


    def __init__(self, database: Database | None = None) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        database : `Database` instance.
            - `None`: Not use database.
            - `Database`: Automatic record to database.
        """

        # Build.
        self.database = database
 
        ## Database path name.
        self.db_names = {
            'worm': 'worm',
            'worm.douban_media': 'douban_media',
            'worm.douban_stats': 'douban_stats'
        }


    def crawl_table(self) -> MediaTable:
        """
        Crawl media table.

        Returns
        -------
        Media table.
        """

        # Handle parameter.
        url_format = 'https://m.douban.com/rexxar/api/v2/subject/recent_hot/%s'
        referer_format = 'https://movie.douban.com/%s/'
        types_params = (
            ('movie', 'explore', '热门', '华语'),
            ('movie', 'explore', '热门', '欧美'),
            ('movie', 'explore', '热门', '日本'),
            ('movie', 'explore', '热门', '韩国'),
            ('tv', 'tv', 'tv', 'tv_domestic'),
            ('tv', 'tv', 'tv', 'tv_american'),
            ('tv', 'tv', 'tv', 'tv_japanese'),
            ('tv', 'tv', 'tv', 'tv_korean'),
            ('tv', 'tv', 'tv', 'tv_animation'),
            ('tv', 'tv', 'tv', 'tv_documentary'),
            ('tv', 'tv', 'show', 'show_domestic'),
            ('tv', 'tv', 'show', 'show_foreign')
        )

        # Get.
        table_dict: dict[int, MediaRow] = {}
        for type_params in types_params:
            type_ = type_params[0]
            url = url_format % type_
            referer = referer_format % type_params[1]
            params = {
                'start': 0,
                'limit': 1000,
                'category': type_params[2],
                'type': type_params[3],
                'ck': 'Id-j'
            }
            headers = {
                'referer': referer,
                'user-agent': self.ua.edge
            }

            ## Request.
            response = request(
                url,
                params,
                headers=headers,
                check=True
            )

            ## Extract.
            response_json = response.json()
            items: list[dict] = response_json['items']
            for item in items:
                id_ = int(item['id'])

                ### Exist.
                if id_ in table_dict:
                    continue

                ### Base.
                row = {
                    'id': id_,
                    'type': type_,
                    'name': item['title'],
                    'score': float(item['rating']['value']),
                    'score_count': int(item['rating']['count']),
                    'image': item['pic']['large'],
                    'image_low': item['pic']['normal']
                }

                ### Score.
                row['score'] = float(item['rating']['value']) or None
                row['score_count'] = int(item['rating']['count']) or None

                ### Episode.
                if item['episodes_info'] == '':
                    row['episode_now'] = row['episode'] = None
                else:
                    row['episode_now'] = search(r'\d+', item['episodes_info'])
                    if '全' in item['episodes_info']:
                        row['episode'] = row['episode_now']
                    else:
                        row['episode'] = None

                ### Information.
                desc = item['card_subtitle'].split(' / ', 4)
                if len(desc) == 5:
                    year, countries, classes, directors, stars = desc
                elif len(desc) == 4:
                    year, countries, classes, stars = desc
                    directors = None
                else:
                    year, countries, classes = desc
                    directors = None
                    stars = None
                row['year'] = int(year)
                row['country'] = countries.split()
                row['class'] = classes.split()
                row['director'] = directors and directors.split()
                row['star'] = stars and stars.split()

                ### Add.
                table_dict[id_] = row

        ## Convert.
        table = list(table_dict.values())

        # Database.
        if self.database is not None:
            update_fields = (
                'id',
                'type',
                'name',
                'score',
                'score_count',
                'image',
                'image_low',
                'episode',
                'episode_now',
                'year'
            )
            self.database.execute_insert(
                (self.db_names['worm'], self.db_names['worm.douban_media']),
                table,
                update_fields
            )

        return table


    def crawl_info(self, id_: int) -> MediaInfo:
        """
        Crawl media information.

        Parameters
        ----------
        id\\_ : Douban media ID.

        Returns
        -------
        Media information.
        """

        # Handle parameter.
        url = f'https://movie.douban.com/subject/{id_}/'
        headers = {'user-agent': self.ua.edge}

        # Request.
        response = request(
            url,
            headers=headers,
            check=True
        )

        # Extract.
        html = response.text
        bs = BeautifulSoup(html, 'lxml')
        attrs = {'id': 'info'}
        element = bs.find(attrs=attrs)
        pattern = r'([^\n]+?): ([^\n]+)\n'
        result = findall(pattern, element.text)
        info_dict: dict[str, str] = dict(result)
        split_chars = ' / '
        infos = {}

        ## Type.
        if (
            'class="episode_list"' in html
            or '该剧目前还未确定具体集数，如果你知道，欢迎' in bs.find(attrs='article').text
        ):
            infos['type'] = 'tv'
        else:
            infos['type'] = 'movie'

        ## Name.
        pattern = r'<title>\s*(.+?)\s*\(豆瓣\)\s*</title>'
        infos['name'] = search(pattern, html)

        ## Year.
        pattern = r'<span class="year">\((\d{4})\)</span>'
        year: str | None = search(pattern, html)
        infos['year'] = year and int(year)

        ## Description.
        selector = '#link-report-intra span[property="v:summary"]'
        elements = bs.select(selector, limit=1)
        if len(elements) == 0:
            infos['desc'] = None
        else:
            element, = bs.select(selector, limit=1)
            text = element.text.strip()
            pattern = r'\s{2,}'
            infos['desc'] = sub(pattern, text, '')

        ## Score.
        element = bs.find(attrs='ll rating_num')
        if element.text == '':
            infos['score'] = None
        else:
            infos['score'] = float(element.text)

        ## Score count.
        if infos['score'] is not None:
            attrs = {'property': 'v:votes'}
            element = bs.find(attrs=attrs)
            infos['score_count'] = int(element.text)
        else:
            infos['score_count'] = None

        ## Directors.
        directors = info_dict.get('导演')
        infos['director'] = directors and directors.split(split_chars)

        ## Scriptwriters.
        scriptwriters = info_dict.get('编剧')
        infos['scriptwriter'] = scriptwriters and scriptwriters.split(split_chars)

        ## Stars.
        stars = info_dict.get('主演')
        infos['star'] = stars and stars.split(split_chars)

        ## Classes.
        classes = info_dict.get('类型')
        infos['class'] = classes and classes.split(split_chars)

        ## Countries.
        countries = info_dict.get('制片国家/地区')
        infos['country'] = countries and countries.split(split_chars)

        ## Languages.
        languages = info_dict.get('语言')
        infos['language'] = languages and languages.split(split_chars)

        ## Premieres.
        premieres = info_dict.get('上映日期')
        premieres = premieres or info_dict.get('首播')
        infos['premiere'] = premieres and {
            countrie: date
            for premiere in premieres.split(split_chars)
            for date, countrie in (search(r'([^\(]+)\((.+)\)', premiere),)
        }

        ## Episode.
        episode = info_dict.get('集数')
        infos['episode'] = episode and int(episode)

        ## Minute.
        minute = info_dict.get('片长')
        minute = minute or info_dict.get('单集片长')
        infos['minute'] = minute and int(search(r'\d+', minute))

        ## Alias.
        alias = info_dict.get('又名')
        infos['alias'] = alias and alias.split(split_chars)

        ## IMDb.
        infos['imdb'] = info_dict.get('IMDb')

        ## Comments.
        selector = '#hot-comments .comment-content'
        elements = bs.select(selector)
        comments = [
            sub(
                r'\s{2,}',
                (
                    element.find(attrs='full')
                    or element.find(attrs='short')
                ).text.strip(),
                ''
            )
            for element in elements
        ]
        infos['comment'] = comments

        ## Image.
        selector = '.nbgnbg>img'
        element, = bs.select(selector=selector, limit=1)
        image_url = element.attrs['src']
        infos['image_low'] = image_url.replace('.webp', '.jpg', 1)
        infos['image'] = infos['image_low'].replace('/s_ratio_poster/', '/m_ratio_poster/', 1)

        ## Video.
        element = bs.find(attrs='related-pic-video')
        if element is None:
            infos['video'] = None
        else:
            infos['video'] = element.attrs['href']

        # Database.
        if self.database is not None:
            data = {'id': id_}
            data.update(infos)
            self.database.execute_insert(
                (self.db_names['worm'], self.db_names['worm.douban_media']),
                data,
                'update'
            )

        return infos


    def build_db(self) -> None:
        """
        Check and build all standard databases and tables, by `self.db_names`.
        """

        # Check.
        if self.database is None:
            throw(ValueError, self.database)

        # Set parameter.

        ## Database.
        databases = [
            {
                'name': self.db_names['worm']
            }
        ]

        ## Table.
        tables = [

            ### 'douban_media'.
            {
                'path': (self.db_names['worm'], self.db_names['worm.douban_media']),
                'fields': [
                    {
                        'name': 'create_time',
                        'type': 'datetime',
                        'constraint': 'NOT NULL DEFAULT CURRENT_TIMESTAMP',
                        'comment': 'Record create time.'
                    },
                    {
                        'name': 'update_time',
                        'type': 'datetime',
                        'constraint': 'DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP',
                        'comment': 'Record update time.'
                    },
                    {
                        'name': 'id',
                        'type': 'int unsigned',
                        'constraint': 'NOT NULL',
                        'comment': 'Douban media ID.'
                    },
                    {
                        'name': 'imdb',
                        'type': 'char(10)',
                        'comment': 'IMDb ID.'
                    },
                    {
                        'name': 'type',
                        'type': 'varchar(5)',
                        'constraint': 'NOT NULL',
                        'comment': 'Media type.'
                    },
                    {
                        'name': 'name',
                        'type': 'varchar(50)',
                        'constraint': 'NOT NULL',
                        'comment': 'Media name.'
                    },
                    {
                        'name': 'year',
                        'type': 'year',
                        'constraint': 'NOT NULL',
                        'comment': 'Release year.'
                    },
                    {
                        'name': 'desc',
                        'type': 'varchar(1000)',
                        'comment': 'Media content description.'
                    },
                    {
                        'name': 'score',
                        'type': 'float',
                        'comment': 'Media score, [0,10].'
                    },
                    {
                        'name': 'score_count',
                        'type': 'int',
                        'comment': 'Media score count.'
                    },
                    {
                        'name': 'minute',
                        'type': 'smallint',
                        'comment': 'Movie or TV drama episode minute.'
                    },
                    {
                        'name': 'episode',
                        'type': 'smallint',
                        'comment': 'TV drama total episode number.'
                    },
                    {
                        'name': 'episode_now',
                        'type': 'smallint',
                        'comment': 'TV drama current episode number.'
                    },
                    {
                        'name': 'premiere',
                        'type': 'json',
                        'comment': 'Premiere region and date dictionary.'
                    },
                    {
                        'name': 'country',
                        'type': 'json',
                        'comment': 'Release country list.'
                    },
                    {
                        'name': 'class',
                        'type': 'json',
                        'comment': 'Class list.'
                    },
                    {
                        'name': 'director',
                        'type': 'json',
                        'comment': 'Director list.'
                    },
                    {
                        'name': 'star',
                        'type': 'json',
                        'comment': 'Star list.'
                    },
                    {
                        'name': 'scriptwriter',
                        'type': 'json',
                        'comment': 'Scriptwriter list.'
                    },
                    {
                        'name': 'language',
                        'type': 'json',
                        'comment': 'Language list.'
                    },
                    {
                        'name': 'alias',
                        'type': 'json',
                        'comment': 'Alias list.'
                    },
                    {
                        'name': 'comment',
                        'type': 'json',
                        'comment': 'Comment list.'
                    },
                    {
                        'name': 'image',
                        'type': 'varchar(150)',
                        'constraint': 'NOT NULL',
                        'comment': 'Picture image URL.'
                    },
                    {
                        'name': 'image_low',
                        'type': 'varchar(150)',
                        'constraint': 'NOT NULL',
                        'comment': 'Picture image low resolution URL.'
                    },
                    {
                        'name': 'video',
                        'type': 'varchar(150)',
                        'comment': 'Preview video Douban page URL.'
                    }
                ],
                'primary': 'id',
                'indexes': [
                    {
                        'name': 'u_imdb',
                        'fields': 'imdb',
                        'type': 'unique',
                        'comment': 'IMDb number unique index.'
                    },
                    {
                        'name': 'n_name',
                        'fields': 'name',
                        'type': 'noraml',
                        'comment': 'Media name normal index.'
                    }
                ],
                'comment': 'Douban media information table.'
            }

        ]

        ## View stats.
        views_stats = [

            ### 'douban_stats'.
            {
                'path': (self.db_names['worm'], self.db_names['worm.douban_stats']),
                'items': [
                    {
                        'name': 'count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media count.'
                    },
                    {
                        'name': 'past_day_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) = 0'
                        ),
                        'comment': 'Media count in the past day.'
                    },
                    {
                        'name': 'past_week_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 6'
                        ),
                        'comment': 'Media count in the past week.'
                    },
                    {
                        'name': 'past_month_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`\n'
                            'WHERE TIMESTAMPDIFF(DAY, `create_time`, NOW()) <= 29'
                        ),
                        'comment': 'Media count in the past month.'
                    },
                    {
                        'name': 'avg_score',
                        'select': (
                            'SELECT ROUND(AVG(`score`), 1)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media average score.'
                    },
                    {
                        'name': 'score_count',
                        'select': (
                            'SELECT FORMAT(SUM(`score_count`), 0)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media score count.'
                    },
                    {
                        'name': 'last_create_time',
                        'select': (
                            'SELECT MAX(`create_time`)\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media last record create time.'
                    },
                    {
                        'name': 'last_update_time',
                        'select': (
                            'SELECT IFNULL(MAX(`update_time`), MAX(`create_time`))\n'
                            f'FROM `{self.db_names['worm']}`.`{self.db_names['worm.douban_media']}`'
                        ),
                        'comment': 'Media last record update time.'
                    }
                ]

            }

        ]

        # Build.
        self.database.build.build(databases, tables, views_stats=views_stats)
