#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
# Email : dd.parkhere@gmail.com
###################################################################
import os

from dayu_widgets.combo_box import MComboBox
from dayu_widgets.menu import MMenu
from dayu_widgets.qt import *
from dayu_widgets.theme import MTheme
from dayu_widgets.message import MMessage

import utils


class WComboBox(MComboBox):
    def __init__(self, parent=None):
        super(WComboBox, self).__init__(parent=parent)
        self.setFixedWidth(100)
        self.menu = MMenu()
        MTheme('light').apply(self.menu)
        self.set_menu(self.menu)

        self.proj_dict = {}

        self.get_projects_thread = utils.MFetchDataThread('find', ['Project', [['sg_status', 'is', 'Active']], ['name']], using_cache=True)
        # self.get_projects_thread = utils.MFetchDataThread('find', ['Project', [], ['name']], using_cache=True)
        self.get_projects_thread.result_sig.connect(self.set_projs)
        self.get_projects_thread.start()
        MMessage.config(duration=999)
        self.msg = MMessage.loading(u'正在连接shotgun...', parent=self)
        self.msg.setStyleSheet('color:black')
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_thread_running)
        self.timer.start(5000)
        self.setEnabled(False)

    def check_thread_running(self):
        if not self.proj_dict:
            if self.msg:
                self.msg._content_label.setText(u'连接超时，正在重试...')
            self.msg.setStyleSheet('color:black')
            self.get_projects_thread.terminate()
            self.get_projects_thread.wait()
        #     self.get_projects_thread.quit()
            self.get_projects_thread.start()
            self.timer.start(5000)
        elif self.msg:
            self.msg.close()

    def set_data(self, data):
        self.menu.set_data(data)

    def set_projs(self, p):
        self.msg.close()
        os.environ['WOK_PROJECT_DICT'] = ''
        if p:
            project_dict = {}
            for each in p:
                name = each.get('name')
                id = each.get('id')
                project_dict[name] = id
            os.environ['WOK_PROJECT_DICT'] = str(project_dict)
            ps = [each.get('name') for each in p]
            self.set_data(ps)
            for proj in p:
                self.proj_dict[proj.get('name')] = proj
        self.setEnabled(True)
        self.get_projects_thread.wait()
        self.get_projects_thread.quit()
        self.timer.stop()
        return p

    def closeEvent(self, *args, **kwargs):
        self.get_projects_thread.wait()
        self.get_projects_thread.quit()

