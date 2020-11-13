#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.7
###################################################################
import json
import time
import ui
import os
import shutil
import functools
from widgets import utils
from dayu_widgets.qt import *
from dayu_widgets import dayu_theme
from dayu_widgets.message import MMessage
from .. import toast
from ..mq import thread


class CreateWokMain(ui.CreateWokWin):
    def __init__(self, parent=None, mode='create', wok_id=None):
        super(CreateWokMain, self).__init__(parent)
        self.mode = mode
        self.wok_id = wok_id
        # get pandas
        self.get_pandas_thread = utils.MFetchDataThread('find', [os.environ.get('SG_PANDA_ENTITY'), [], ['code', 'sg_login_name']], using_cache=True)
        self.get_pandas_thread.result_sig.connect(self.get_pandas)
        self.get_pandas_thread.start()
        # get pandas done
        self.get_tasks_thread = utils.MFetchDataThread('find',
                                                       ['Task', [['project.Project.name', 'is', os.environ.get('WOK_PROJECT')]],
                                                        ['content', 'entity', 'entity.Asset.code', 'entity.Shot.code']], using_cache=True)
        self.get_tasks_thread.result_sig.connect(self.get_tasks)
        self.get_tasks_thread.start()
        self.get_tasks_thread.started.connect(functools.partial(self.loading_wrapper.set_dayu_loading, True))
        self.get_tasks_thread.finished.connect(lambda: self.loading_wrapper.set_dayu_loading(False))
        # self.setEnabled(False)
        if self.mode == 'update':
            self.delete_pb.show()
            self.delete_pb.clicked.connect(self.delete_wok)
            self.get_wok_thread = utils.MFetchDataThread('find_one',
                                                         [os.environ.get('WOK_ENTITY'), [['id', 'is', self.wok_id]],
                                                          ['code', 'description', 'sg_panda', 'sg_link', 'sg_thumbnail_path']]
                                                         , True)
            self.get_wok_thread.result_sig.connect(self.set_wok_settings)
            self.get_wok_thread.start()

        self.create_wok_thread = utils.MFetchDataThread()
        self.create_wok_thread.result_sig.connect(self.finished_creating)
        self.thumbnail.screen_grabbed.connect(self.get_thumbnail)
        self.create_pb.clicked.connect(self.create)
        self.cancel_pb.clicked.connect(self.close)
        self.pandas_lb.clicked.connect(self.menu_win.show)
        self.menu_win.radio_group_b.sig_checked_changed.connect(self.get_selected_pandas)
        # necessary params
        self.pandas = []
        self.entity_dict = {}
        self.this_panda = {}
        self.panda_dict = {}# eval(os.environ.get('SG_PANDA_DICT'))
        self.wok_path = ''
        self.thumb_path_local = ''
        self.thumbnail_path_server = ''
        self.this_wok_info = ''
        self.msg = None
        self.is_created = False
        # other

    def get_selected_pandas(self, pandas):
        pandas_str = ','.join(pandas)
        self.pandas_lb.setText(pandas_str)

    def get_pandas(self, pandas):
        for p in pandas:
            self.panda_dict[p.get('code')] = p
        os.environ['SG_PANDA_DICT'] = str(self.panda_dict)
        # self.pandas_cb.init_combobox(sorted(self.panda_dict.keys()))
        # self.pandas_menu.set_data(sorted(self.panda_dict.keys()))
        self.menu_win.set_data_list(sorted(self.panda_dict.keys()))
        return True

    def set_wok_settings(self, result):
        self.this_wok_info = result
        self.wok_name_le.setText(result.get('code'))
        # self.pandas_cb.combobox.setEditText(result.get('sg_panda')[0].get('name'))
        # self.entity_cb.combobox.setEditText(result.get('sg_link').get('name'))
        # self.thumb_path_local = result.get('sg_thumbnail_path')
        self.thumbnail.set_thumbnail(QPixmap(result.get('sg_thumbnail_path')))
        self.description_te.setText(result.get('description'))

    def get_tasks(self, tasks):
        # self.setEnabled(True)
        self.delete_pb.setEnabled(True)
        self.delete_pb.setText(u'删除这个锅')
        if not tasks or not isinstance(tasks, list):
            return
        for task in tasks:
            if not task or not task.get('entity'):
                continue
            if task.get('entity') and task.get('entity').get('type') == 'Asset':
                self.entity_dict[task.get('entity.Asset.code')] = task.get('entity')
            else:
                self.entity_dict[task.get('entity.Shot.code')] = task.get('entity')
        if self.entity_dict:
            self.entity_cb.init_combobox(sorted(self.entity_dict.keys()))
        if self.mode == 'update':
            if not self.this_wok_info:
                time.sleep(1)
            panda = ''
            if isinstance(self.this_wok_info.get('sg_panda'), list):
                pandas = []
                for each in self.this_wok_info.get('sg_panda'):
                    pandas.append(each.get('name'))
                panda = ','.join(pandas)
            else:
                if self.this_wok_info.get('sg_panda'):
                    panda = self.this_wok_info.get('sg_panda').get('name')
            self.pandas_lb.setText(panda)
            self.menu_win.set_checked(panda)
            self.entity_cb.combobox.setEditText(((self.this_wok_info.get('sg_link') or {}).get('name')) or '')
        pass

    def get_thumbnail(self, pixmap):
        if pixmap:
            if hasattr(self.thumbnail, 'thumb'):
                self.thumb_path_local = self.thumbnail.thumb
            else:
                self.thumb_path_local = os.environ.get('WOK_TEMP_DIR')
                if not os.path.isdir(self.thumb_path_local):
                    os.makedirs(self.thumb_path_local)
                self.thumb_path_local = self.thumb_path_local + 'thumbnail.png'
                pixmap.save(self.thumb_path_local)

    def show_error(self, msg):
        error_win = toast.error.WToast(parent=self.parent(), text=msg, duration=3)
        error_win.set_img(os.environ['WOKWOK_ROOT'] + '/resources/icons/kiana-critical.png')
        dayu_theme.apply(error_win)
        error_win.show()

    def create(self):
        warning_text = ''
        if not self.wok_name_le.text():
            warning_text = warning_text + u'必须输入锅名哦！'
        if not self.description_te.toPlainText():
            warning_text = warning_text + u'\n把描述写一下吧!!!'
        if not self.thumb_path_local and self.mode == 'create':
            warning_text = warning_text + u'\n别忘了缩略图哦！'
        # if not self.pandas_lb.text():
        #     warning_text = warning_text + u'\n分配给谁？！'
        if warning_text:
            self.show_error(warning_text)
            # MToast.error(parent=self.parent(), text=u'必须输入锅名哦！', duration=3)
            return
        MMessage.config(999)
        self.create_folder_tree()
        self.start_create()

    def create_folder_tree(self):
        wok_path_format = os.environ.get('WOK_PATH_FORMAT')
        thumb_format = os.environ.get('WOK_THUMBNAIL_PATH_FORMAT')
        format_dict = {'wok_project': os.environ.get('WOK_PROJECT'),
                          # 'sg_panda': os.environ.get('SG_PANDA'),
                       'code': self.wok_name_le.text().encode('GB2312'),
                       'status': 'check',
                       'link': self.entity_cb.combobox.currentText() or 'None',
                      }
        self.wok_path = wok_path_format.format(**format_dict)
        self.thumbnail_path_server = thumb_format.format(**format_dict)
        if not os.path.isdir(self.wok_path):
            os.makedirs(self.wok_path)
        # os.system('copy %s %s' % (self.thumb_path_local.encode('GB2312'), self.thumbnail_path_server))
        try:
            shutil.copyfile(self.thumb_path_local, self.thumbnail_path_server)
        except Exception as e:
            print e
        pass

    def start_create(self, delete=False):
        MMessage.config(20)
        self.msg = MMessage.loading(parent=self.parent(), text=u'正在执行，请稍等...')
        self.setEnabled(False)
        self.create_pb.setEnabled(False)
        self.cancel_pb.setEnabled(False)
        all_panda_nick_names = self.pandas_lb.text().split(',') or []
        if all_panda_nick_names:
            for each in all_panda_nick_names:
                if self.panda_dict.get(each):
                    self.pandas.append(self.panda_dict.get(each))
        # self.panda = self.panda_dict.get(self.pandas_cb.combobox.currentText())
        # if not self.panda:
        #     self.show_error(u'没有找到这只小熊猫，确定这个人存在嘛？？')
        #     return
        sg_link = None
        if self.entity_cb.combobox.currentText():
            sg_link = self.entity_dict.get(self.entity_cb.combobox.currentText(), {})#.get('entity')
        _data = {'code': self.wok_name_le.text(),
                                                              'description': self.description_te.toPlainText(),
                                                              # 'sg_status_list': 'wd',
                                                              # 'sg_link': sg_link,
                                                              'project': {'type': 'Project',
                                                                          'id': eval(os.environ.get('WOK_PROJECT_DICT'))
                                                                              .get(os.environ.get('WOK_PROJECT'))},
                                                              }
        if self.pandas:
            _data.update({'sg_panda': self.pandas})
        if sg_link:
            _data.update({'sg_link': sg_link})
        _data = json.loads(json.dumps(_data))
        if self.mode == 'create':
            self.create_wok_thread.mode = 'create'
            _data.update({'sg_thumbnail_path': self.thumbnail_path_server.decode('GB2312').encode('utf-8'),
                          'sg_status_list': 'wd'})
            _data = json.loads(json.dumps(_data))
            self.create_wok_thread.data = [os.environ.get('WOK_ENTITY'), _data]
        else:
            self.create_wok_thread.mode = 'update'
            if self.thumb_path_local:
                _data.update({'sg_thumbnail_path': self.thumbnail_path_server.decode('GB2312').encode('utf-8')})
                # _data['sg_thumbnail_path'] = self.thumbnail_path_server.decode('GB2312').encode('utf-8'),
            if delete:
                _data['sg_status_list'] = 'omt'
                _data['code'] = self.wok_name_le.text() + '(deleted)'
            self.create_wok_thread.data = [os.environ.get('WOK_ENTITY'), self.wok_id, _data]
        self.create_wok_thread.start()

    def finished_creating(self, wok_entity):
        if self.mode == 'update':
            if self.msg:
                self.msg.close()
            MMessage.success(parent=self.parent(), text=u'更新成功！！', duration=2)
            self.parent().current_page.parse_config()
            # self.send_msg()
            self.close()
            return
        # MMessage.error(parent=self.parent(), text=u'创建出现了问题！', duration=4)
        # return
        if wok_entity.get('error'):
            print wok_entity
            MMessage.error(parent=self.parent(), text=u'创建失败咯！请确认这个锅是不是已经存在了？？', duration=4)
            if self.msg:
                self.msg.close()
            self.msg = None
            # self.show_error(u'创建失败咯！请确认这个锅是不是已经存在了？？')
            return
        # if wok_entity.get('type') != os.environ.get('WOK_ENTITY'):
        #     self.is_created = True
        #     if self.msg:
        #         self.msg.close()
        #         self.close()
        #     return
        # if not isinstance(wok_entity, dict):
        #     if isinstance(wok_entity, int):
        if self.msg:
            self.msg.close()
        MMessage.success(parent=self.parent(), text=u'创建成功啦！', duration=2)
        self.parent().current_page.parse_config()
        self.send_msg()
        self.close()
        return
        # if not self.thumb_path_local or not os.path.isfile(self.thumb_path_local):
        #     return
        # wok_id = wok_entity.get('id')
        # self.create_wok_thread.mode = 'upload_thumbnail'
        # self.create_wok_thread.data = [os.environ.get('WOK_ENTITY'), wok_id, self.thumb_path_local]
        # self.create_wok_thread.start()
        pass

    def send_msg(self):
        # print os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')
        for each in self.pandas:
            thread.send(info=u'你接到了一个锅！\n%s\n操作人：%s' % (self.wok_name_le.text(),
                                                        os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')),
                        receiver=each.get('sg_login_name'),
                        sender=os.environ.get('SG_PANDA')
                        )

    def delete_wok(self):
        confirm_dialog = QMessageBox(parent=self)
        confirm_dialog.setText(u'确定要删除这个锅嘛？？？\n%s' % self.this_wok_info.get('code'))
        confirm_dialog.setWindowTitle(u"提示")
        confirm_dialog.addButton(u"是的，我确定！", QMessageBox.AcceptRole)  # role 0
        confirm_dialog.addButton(u"手滑点错了！", QMessageBox.RejectRole)  # role 1
        answer = confirm_dialog.exec_()
        if answer == 0:
            self.start_create(True)









