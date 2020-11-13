#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.7
# Email : dd.parkhere@gmail.com
###################################################################
import os
import tempfile
import getpass
import datetime

os.environ['WOK_SERVER'] = '*****'  # 存储服务器

env_dict = dict(
    SG_PANDA=getpass.getuser(),
    SG_PANDA_NICK_NAME='',
    WOK_CHECKER='*****',
    SG_PANDA_DICT='',  # 这个变量会在get_pandas启动时被覆盖，格式是'{'panda_code': {},}'，注意是个字符串，需要eval转成字典。
    WOK_PROJECT='',  # 这个变量会在combobox切换项目之后被覆盖
    WOK_PROJECT_DICT='',  # 这个变量会在combobox获取项目列表时被覆盖，格式是'{'project_code': id,}'，注意是个字符串，需要eval转成字典。
    WOK_THEME='light',
    P4_PORT='*****',
    WOK_ENTITY='CustomEntity06',
    WOK_VERSION_ENTITY='CustomEntity07',
    SG_PANDA_ENTITY='CustomNonProjectEntity01',
    WOK_COMMENT_ENTITY='CustomThreadedEntity01',
    WOK_TEMP_DIR=tempfile.gettempdir() + '/WOKWOK',
    STATUS_DICT=str(dict(wo=u'通过', wh=u'等等再看', wr=u'返修', wc=u'待检查', wf=u'归档', wd=u'正在制作', wp=u'整合', wt=u'翻译', omt=u'忽略')),
    MQ_CONFIG=str(dict(username="****",  # rabbit mq
                                  password="*****",
                                  host="*****",
                                  port=5672)),
    SG_PG_CONFIG=str(dict(database="*****",  # 缓存数据库
                                  user="*****",
                                  password="*****",
                                  host="*****",
                                  port="5432")),
    WOK_PATH_FORMAT=os.environ.get('WOK_SERVER')+'/{wok_project}/{status}/{link}/{code}',
    WOK_THUMBNAIL_PATH_FORMAT=os.environ.get('WOK_SERVER')+'/{wok_project}/{status}/{link}/{code}/%s.thumbnail' % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
    WOK_VERSION_WORK_PATH_FORMAT=os.environ.get('WOK_SERVER')+'/{wok_project}/{status}/{link}/{code}/{sg_panda}/{sg_version_code}/works',
    WOK_VERSION_FEEDBACK_PATH_FORMAT=os.environ.get('WOK_SERVER')+'/{wok_project}/{status}/{link}/{code}/{sg_panda}/{sg_version_code}/feedback',
)


os.environ.update(env_dict)

if __name__ == '__main__':
    pass


