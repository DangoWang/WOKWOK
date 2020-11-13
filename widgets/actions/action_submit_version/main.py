#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.7
###################################################################
import datetime
import json
import os
import time
import shutil
from ui import SubmitDialog
from ... import utils
from dayu_widgets.message import MMessage
from dayu_widgets.qt import QThread, Signal
from ...mq import thread


class SubmitToSGThread(QThread):
    path_sig = Signal(str)
    finish_creating = Signal(bool)

    def __init__(self):
        super(SubmitToSGThread, self).__init__()
        self.wok_id = ''
        self.version_description = ''
        self.version_thumbnail = None
        self.__sg = None

    def run(self, *args, **kwargs):
        if not self.__sg:
            self.__sg = utils.get_sg_instance()
        wok_details = self.__sg.find_one(os.environ.get('WOK_ENTITY'), [['id', 'is', self.wok_id]],
                                         ['sg_versions_count', 'code', 'sg_link', 'project.Project.name', 'project',
                                          'sg_link.Shot.Code', 'sg_link.Asset.Code'
                                          ])
        version_counts = int(wok_details.get('sg_versions_count') or 0)
        new_version_code = ('v' + str(version_counts+1).zfill(3))
        version_storage_format = os.environ.get('WOK_VERSION_WORK_PATH_FORMAT')
        #  format是个垃圾的格式化方法，不支持json的unicode，必须全部转成utf-8
        link = wok_details.get('sg_link') or {'name': 'None'}
        format_dict = utils.change_dict_encoding({
                                  'wok_project': wok_details.get('project.Project.name'),
                                  'sg_panda': os.environ.get('SG_PANDA'),
                                  'code': wok_details.get('code'),
                                  'status': 'check',
                                  'link': link.get('name'),
                                  'sg_version_code': new_version_code
                                            })
        version_storage = version_storage_format.format(**format_dict)
        version_storage = json.loads(json.dumps(version_storage))
        self.path_sig.emit(version_storage)
        panda_nick_name = os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')
        data = utils.change_dict_encoding(
                            {'code': wok_details.get('code') + '_' + new_version_code,
                            'sg_panda': eval(os.environ.get('SG_PANDA_DICT')).get(panda_nick_name),
                            'sg_path': version_storage,
                             'sg_status_list': 'wc',
                            'sg_version_code': new_version_code,
                            'sg_wok': wok_details,
                             'description': self.version_description,
                             'project': wok_details.get('project'),
                             'sg_thumbnail_path': version_storage.replace('/works', '/thumbnail') #if os.path.isfile(version_storage.replace('/works', '/thumbnail')) else None
                            }, encoding='unicode_escape')
        data = json.loads(json.dumps(data))
        self.__sg.update(os.environ.get('WOK_ENTITY'), wok_details.get('id'), {'sg_versions_count': version_counts+1, 'sg_status_list': 'wc'})
        self.__sg.create(os.environ.get('WOK_VERSION_ENTITY'), data)
        time.sleep(5)
        self.finish_creating.emit(True)


class Submit(SubmitDialog):
    def __init__(self, parent, config):
        super(Submit, self).__init__(parent=parent)
        if not config.get('selected'):
            MMessage.error(parent=self.parent(), text=u'请选中锅再上传哦~', duration=3)
            # raise
        self.wok_name = config.get('selected')[0].get('code')
        self.wok_id = config.get('selected')[0].get('id')
        self.wok_name_label.setText(self.wok_name)
        self.finish_creating_result = False
        self.finishing_copy_result = False

        self.cancel_pb.clicked.connect(self.close)
        self.create_pb.clicked.connect(self.start_submit)

        self._change_wok_status_thread = SubmitToSGThread()
        self.copy_file_thread = utils.CopyFile(compare_modify=True)
        self._change_wok_status_thread.path_sig.connect(self.start_copy)
        self._change_wok_status_thread.finish_creating.connect(self.finish_creating)
        self.copy_file_thread.finished.connect(self.finishing_copy)

        self.thumbnail.screen_grabbed.connect(self.get_thumbnail)
        self.msg = None
        self.thumb_path_local = None
        # self.thumb_path_server = None

    def get_thumbnail(self, pixmap):
        if pixmap:
            if hasattr(self.thumbnail, 'thumb'):
                self.thumb_path_local = self.thumbnail.thumb
            else:
                self.thumb_path_local = os.environ.get('WOK_TEMP_DIR')
                if not os.path.isdir(self.thumb_path_local):
                    os.makedirs(self.thumb_path_local)
                self.thumb_path_local = self.thumb_path_local + '/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '_thumbnail.png'
                pixmap.save(self.thumb_path_local)
                # print self.thumb_path_local
                # self.thumb_path_server = self.thumb_path_local.replace('/works', '/thumbnail')

    def start_submit(self):
        warning_text = ''
        if not self.wok_id:
            warning_text = u'咦，好像没办法确定你上传到了哪个锅，你再确认下是不是在锅上面右键的？？'
        if not self.all_files:
            warning_text = u'没有文件的话是没法提交的哦！'
        if not self.description_te.toPlainText():
            warning_text = u'写个描述吧！！'
        if warning_text:
            MMessage.error(parent=self.parent(), text=warning_text, duration=3)
            return
        MMessage.config(999)
        self.msg = MMessage.loading(parent=self.parent(), text=u'正在创建，请稍等。。')
        self._change_wok_status_thread.wok_id = self.wok_id
        self._change_wok_status_thread.files_list = self.all_files
        # self._change_wok_status_thread.version_thumbnail = self.thumb_path_server
        self._change_wok_status_thread.version_description = self.description_te.toPlainText()
        self._change_wok_status_thread.start()
        self.cancel_pb.setEnabled(False)
        self.create_pb.setEnabled(False)
        pass

    def start_copy(self, dest_path):
        self.msg._content_label.setText(u'正在拷贝文件...')
        copy_list = []
        if self.thumb_path_local:
            if not os.path.isdir(dest_path.replace('/works', '')):
                os.mkdir(dest_path.replace('/works', ''))
            shutil.copyfile(self.thumb_path_local, dest_path.replace('/works', '/thumbnail'))
            # copy_list = [self.thumb_path_local, dest_path.replace('/works', '/thumbnail')]
        for each in self.all_files:
            file_dir, file_name = os.path.split(each)
            dest = dest_path + '/' + file_name
            copy_list.append([each, dest])
        self.copy_file_thread.copy_list = copy_list
        self.copy_file_thread.start()
        pass

    def finish_creating(self, r):
        if r:
            self.finish_creating_result = True
            if self.finishing_copy_result:
                self.all_done()

    def finishing_copy(self):
        self.finishing_copy_result = True
        if self.finish_creating_result:
            self.all_done()

    def all_done(self):
        MMessage.config(3)
        self.msg.close()
        MMessage.success(parent=self.parent(), text=u'创建成功！', duration=3)
        self.parent().current_page.parse_config()
        self.send_msg()
        self.close()

    def send_msg(self):
        thread.send(info=u'%s的锅%s上传了一个新版本等你check，可以去看看啦！'%(os.environ.get('SG_PANDA_NICK_NAME').decode('gbk'),
                                                           self.wok_name
                                                           ),
                    receiver=os.environ.get('WOK_CHECKER'),
                    sender=os.environ.get('SG_PANDA'),
                    )


