#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.10
###################################################################

import os
from dayu_widgets.qt import *
from dayu_widgets.menu import MMenu
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.label import MLabel
from dayu_widgets.push_button import MPushButton
from widgets.utils import MFetchDataThread
from widgets.comboBox_completer import combo_box
from dayu_widgets.message import MMessage
from dayu_widgets.radio_button import MRadioButton
from widgets.mq import thread


class OptWin(QDialog):

    def __init__(self, parent=None, config={}):
        super(OptWin, self).__init__(parent=parent)
        if not config.get('selected'):
            MMessage.error(parent=self.parent(), text=u'请选中锅再操作哦~', duration=3)
            return
            # raise
        # self.wok_name = config.get('selected')[0].get('code')
        self.wok_detail = config
        self.wok_id = config.get('selected')[0].get('id')
        # get pandas
        self.pandas_cb = combo_box.WSelectTaskComboBox(self)
        self.panda_dict = {}
        main_lay = QVBoxLayout()
        self.setWindowTitle(u'整合翻译')
        rb_layout = QHBoxLayout()
        self.opt_rb = MRadioButton(u'整合')
        self.opt_rb.setChecked(True)
        self.translate_rb = MRadioButton(u'翻译')
        rb_layout.addWidget(self.opt_rb)
        rb_layout.addWidget(self.translate_rb)
        main_lay.addLayout(rb_layout)

        lay = QHBoxLayout()
        lay.addWidget(MLabel(u'PM指定:').warning().strong())
        lay.addWidget(self.pandas_cb)
        self.ok_pb = MPushButton('OK')
        lay.addWidget(self.ok_pb)
        main_lay.addLayout(lay)
        self.setLayout(main_lay)
        self.get_pandas_thread = MFetchDataThread('find', [os.environ.get('SG_PANDA_ENTITY'), [['sg_status_list', 'is_not', None]],
                                                                 ['code', 'sg_login_name']], using_cache=True)
        self.get_pandas_thread.result_sig.connect(self.get_pandas)
        self.get_pandas_thread.start()

        self.update_thread = MFetchDataThread()
        self.update_thread.finished.connect(self.finish)
        self.ok_pb.clicked.connect(self.ok)
        self.msg = None

    def get_pandas(self, pandas):
        for p in pandas:
            self.panda_dict[p.get('code')] = p
        self.pandas_cb.init_combobox(sorted(self.panda_dict.keys()))
        return True

    def ok(self):
        status = 'wp' if self.opt_rb.isChecked() else 'wt'
        self.setEnabled(False)
        MMessage.config(10)
        self.msg = MMessage.loading(text=u'正在执行操作...', parent=self.parent())
        self.update_thread.mode = 'update'
        self.update_thread.data = [os.environ.get('WOK_ENTITY'), self.wok_id, {'sg_pm': self.panda_dict.get(self.pandas_cb.combobox.currentText()),
                                                                               'sg_status_list': status
                                                                               }]
        self.update_thread.start()
        pass

    def finish(self):
        if self.msg:
            self.msg.close()
        self.send_msg()
        MMessage.config(3)
        MMessage.success(u'操作成功！', self.parent())
        self.close()
        self.parent().current_page.parse_config()

    def send_msg(self):
        # print os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')
        send_info = dict(info=u'你接到了一个整合任务！\n%s\n操作人：%s' % (self.wok_detail.get('selected')[0].get('code'),
                                                    os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')),
                    receiver=self.panda_dict.get(self.pandas_cb.combobox.currentText()).get('sg_login_name'),
                    sender=os.environ.get('SG_PANDA'))
        # print send_info
        thread.send(**send_info)


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication
    from dayu_widgets import dayu_theme
    app = QApplication(sys.argv)
    test = OptWin()
    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())

