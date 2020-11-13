#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.7
# Email : dd.parkhere@gmail.com
###################################################################

import os
import locale
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.qt import *
from dayu_widgets.push_button import MPushButton
from dayu_widgets.message import MMessage


class SetPath(QDialog):
    def __init__(self, parent=None):
        super(SetPath, self).__init__(parent)
        self.setWindowTitle(u'设置路径')
        self.q_settings = QSettings(u'ANIME_WOK_CONFIG', 'SetPath')
        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(700, 150)
        main_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(MLabel(u'服务器路径:'))
        self.server_le = MLineEdit().small().folder()
        self.server_le.setMinimumWidth(500)
        self.server_le.setEnabled(False)
        h_layout.addWidget(self.server_le)
        h_layout.addStretch()
        h_layout_2 = QHBoxLayout()
        h_layout_2.addWidget(MLabel(u'本地工作路径:'))
        self.local_work_path_le = MLineEdit().small().folder()
        self.local_work_path_le.setPlaceholderText(u'未设置')
        h_layout_2.addWidget(self.local_work_path_le)
        main_layout.addLayout(h_layout)
        main_layout.addLayout(h_layout_2)
        self.ok_pb = MPushButton(u'确定')
        main_layout.addWidget(self.ok_pb)
        self.setLayout(main_layout)
        self.ok_pb.clicked.connect(self.on_ok_pb_click)
        wok_server = os.environ.get('WOK_SERVER')
        wok_local = self.q_settings.value('WOK_LOCAL')# or os.environ.get('WOK_LOCAL')
        if wok_server:
            self.server_le.setText(wok_server)
        if wok_local:
            self.local_work_path_le.setText(u'%s' % wok_local.decode('unicode_escape'))

    def on_ok_pb_click(self):
        if self.server_le.text() and self.local_work_path_le.text():
            local = self.local_work_path_le.text().replace('\\', '/')
            os.environ['WOK_SERVER'] = self.server_le.text().replace('\\', '/')
            os.environ['WOK_LOCAL'] = local.encode('unicode_escape')
            # self.q_settings.setValue('WOK_SERVER', os.environ['WOK_SERVER'])
            self.q_settings.setValue('WOK_LOCAL', local.encode('unicode_escape'))
            self.close()
            return
        MMessage.config(5)
        MMessage.error(parent=self.parent(), text=u'请输入正确的路径！')


if __name__ == '__main__':
    print('E:/woks/\u6d4b\u8bd5'.decode('unicode_escape'))


