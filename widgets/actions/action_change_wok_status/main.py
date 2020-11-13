#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.10
###################################################################

#  更改锅状态

import os
import P4
from dayu_widgets.qt import *
from dayu_widgets.menu import MMenu
from dayu_widgets.label import MLabel
from dayu_widgets.push_button import MPushButton
from dayu_widgets.message import MMessage
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.combo_box import MComboBox
from widgets import utils


class ChangeWokStatus(QDialog):

    def __init__(self, parent=None, config={}):
        super(ChangeWokStatus, self).__init__(parent=parent)
        self.setWindowTitle(u'更改状态')
        if not config.get('selected'):
            MMessage.error(parent=self.parent(), text=u'请选中锅再上传哦~', duration=3)
            return
            # raise
        self.wok_name = config.get('selected')[0].get('code')
        self.wok_id = config.get('selected')[0].get('id')
        main_layout = QHBoxLayout()
        main_layout.addWidget(MLabel(u'更改成:'))
        self.setLayout(main_layout)
        self.status_cb = MComboBox()
        self.stauts_menu = MMenu()
        self.stauts_menu.set_data(eval(os.environ.get('STATUS_DICT')).values())
        self.status_cb.set_menu(self.stauts_menu)
        main_layout.addWidget(self.status_cb)
        self.ok_pb = MPushButton(u'确定')
        main_layout.addWidget(self.ok_pb)
        self.ok_pb.clicked.connect(self.change_status_doit)
        self.change_status_thread = utils.MFetchDataThread()
        self.change_status_thread.finished.connect(self.finish_changing)
        self.msg = None

    def change_status_doit(self):
        target_status = self.status_cb.currentText()
        status_dict = eval(os.environ.get('STATUS_DICT'))
        status = ''
        for k, v in status_dict.items():
            if v == target_status:
                status = k
        self.change_status_thread.mode = 'update'
        self.change_status_thread.data = [os.environ.get('WOK_ENTITY'), self.wok_id, {'sg_status_list': status}]
        self.change_status_thread.start()
        MMessage.config(999)
        self.msg = MMessage.loading(u'正在执行...', self.parent())
        self.ok_pb.setEnabled(False)

    def finish_changing(self):
        if self.msg:
            self.msg.close()
        MMessage.config(3)
        MMessage.success(u'操作成功！', self.parent())
        self.parent().current_page.parse_config()
        self.close()


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication
    from dayu_widgets import dayu_theme
    app = QApplication(sys.argv)
    test = ChangeWokStatus()
    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())