#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
# Email : dd.parkhere@gmail.com
###################################################################
import os
from dayu_widgets.qt import *
common_actions = [
                      # {'label': u'上传文件', 'value': 'submit_version', 'icon': 'upload_line.svg', 'mode': '1',},
                      {'label': u'编辑这个锅', 'value': 'edit_wok', 'icon': 'edit_line.svg', 'mode': '1',},
                  ]
common_fields = [
                  {'searchable': True, 'key': 'code', 'label': u'锅名'},
                  {'searchable': False, 'key': 'sg_thumbnail_path', 'label': u'缩略图'},#, 'icon': lambda x, y: x, 'display': '', 'align': 'Center'},
                  # {'searchable': True, 'key': 'sg_wok_code', 'label': u'锅代码'},
                  {'searchable': True, 'key': 'sg_panda', 'label': u'谁的锅'},
                  {'searchable': True, 'key': 'sg_link', 'label': u'角色/镜头'},
                  {'searchable': True, 'key': 'sg_status_list', 'label': u'状态',
                    'icon': lambda x, y: (os.environ['WOKWOK_ROOT'] + '/resources/icons/%s.png' % x),
                    'display': lambda x, y: eval(os.environ['STATUS_DICT']).get(x),
                   },
                  {'searchable': False, 'key': 'created_at', 'label': u'创建于'},
                  {'searchable': False, 'key': 'updated_at', 'label': u'更新于'},
                  {'searchable': False, 'key': 'description', 'label': u'详细说明'},
                 {'searchable': False, 'key': 'sg_entity', 'label': u'评论', 'show': 0},
                 {'searchable': False, 'key': 'project', 'label': u'项目', 'show': 0}
                 ]
common_filters = [
                        ['project.Project.name', 'is', os.environ.get('WOK_PROJECT')],
                  ]

page_type = os.environ.get('WOK_ENTITY')

#  wo我的
page_configs = [{"page_actions": common_actions +
                                 [
                                     {'label': u'上传文件', 'value': 'submit_version', 'icon': 'upload_line.svg', 'mode': '1',}
                                  ],
                      "page_fields": common_fields,
                      "page_filters": common_filters +
                                      [
                                          ['sg_panda.%s.sg_login_name' % os.environ.get('SG_PANDA_ENTITY'),
                                                                                    'is', os.environ.get('SG_PANDA')],
                                          ['sg_status_list', 'is_not', 'omt']
                                      ],
                      "page_type": page_type,
                 },
                #  进行中
                 {"page_actions": common_actions + [{'label': u'更改锅状态', 'value': 'change_wok_status', 'icon': 'edit_fill.svg','mode': '1', }],
                      "page_fields": common_fields,
                      "page_filters": common_filters +
                                       [['sg_status_list', 'in', ['wd', 'wr']]],
                      # "page_name": u"所有版本",
                      "page_type": page_type,
                      # "page_svg": "calendar_line.svg"
                  },
                #  G 看
                {"page_actions": common_actions + [{'label': u'更改锅状态', 'value': 'change_wok_status', 'icon': 'edit_fill.svg', 'mode': '1',}],
                      "page_fields": common_fields,
                      "page_filters": common_filters +
                                       [['sg_status_list', 'not_in', ['wo', 'wf', 'omt', 'wp', 'wt', 'wd', 'wr']]],
                      # "page_name": u"所有版本",
                      "page_type": page_type,
                      # "page_svg": "calendar_line.svg"
                  },
                #  G ok
                {"page_actions": common_actions+[{'label': u'整合翻译', 'value': 'start_opt', 'icon': os.environ['WOKWOK_ROOT'] + '/resources/icons/wp.png', 'mode': '1',},
                                                 {'label': u'更改锅状态', 'value': 'change_wok_status', 'icon': 'edit_fill.svg','mode': '1', },
 ],
                      "page_fields": common_fields[:3] + [{'searchable': True, 'key': 'sg_pm', 'label': u'PM'}] + common_fields[3:],
                      "page_filters": common_filters +
                                       [['sg_status_list', 'in', ['wo']]],
                      # "page_name": u"所有版本",
                      "page_type": page_type,
                      # "page_svg": "calendar_line.svg"
               }, # 整合
                {"page_actions": common_actions + [{'label': u'整合翻译', 'value': 'start_opt', 'icon': os.environ['WOKWOK_ROOT'] + '/resources/icons/wp.png', 'mode': '1',},
                                                    {'label': u'归档至p4', 'value': 'file_to_p4', 'icon': os.environ['WOKWOK_ROOT'] + '/resources/icons/wok-file.png', 'mode': '1',},
                                                    {'label': u'更改锅状态', 'value': 'change_wok_status', 'icon': 'edit_fill.svg', 'mode': '1',},
                                                   ],
                      "page_fields": common_fields[:3] + [{'searchable': True, 'key': 'sg_pm', 'label': u'PM'}] + common_fields[3:],
                      "page_filters": common_filters +
                                       [['sg_status_list', 'in', ['wp', 'wt']]],
                      # "page_name": u"所有版本",
                      "page_type": page_type,
                      # "page_svg": "calendar_line.svg"
               },  # 归档
                {"page_actions": [{'label': u'更改锅状态', 'value': 'change_wok_status', 'icon': 'edit_fill.svg','mode': '1'},
{'label': u'归档至p4', 'value': 'file_to_p4', 'icon': os.environ['WOKWOK_ROOT'] + '/resources/icons/wok-file.png', 'mode': '1',},
                                  ],
                      "page_fields": common_fields[:3] + [{'searchable': True, 'key': 'sg_pm', 'label': u'PM'}] +
                                     common_fields[3:] + [{'searchable': True, 'key': 'sg_p4_path', 'label': u'归档路径'}
                                                         ],
                      "page_filters": common_filters +
                                       [['sg_status_list', 'in', ['wf']]],
                      # "page_name": u"所有版本",
                      "page_type": page_type,
                      # "page_svg": "calendar_line.svg"
               },
]
