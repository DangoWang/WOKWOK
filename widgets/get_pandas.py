#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.7
# Email : dd.parkhere@gmail.com
###################################################################

from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.message import MMessage
from dayu_widgets.push_button import MPushButton
from dayu_widgets.qt import QDialog, QHBoxLayout, Qt, QVBoxLayout
import utils
import os


class WGetPandaWin(QDialog):
    def __init__(self, parent=None):
        super(WGetPandaWin, self).__init__(parent)
        self.setWindowTitle('Examples for MLineEdit')
        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.size_lay = QVBoxLayout()
        self.setLayout(self.size_lay)
        h_layout = QHBoxLayout()
        self.label = MLabel(u'初来乍到的舰长！请在这里输入你的绰号哦！').warning()
        self.line_edit = MLineEdit().small()
        self.ok_pb = MPushButton(u'ok').success()
        self.ok_pb.clicked.connect(self.create_panda)
        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.ok_pb)
        self.size_lay.addWidget(self.label)
        self.size_lay.addLayout(h_layout)
        self.panda_dict = {}
        self.get_pandas_thread = utils.MFetchDataThread('find', [os.environ.get('SG_PANDA_ENTITY'), [], ['code', 'sg_login_name']], using_cache=True)
        self.get_pandas_thread.result_sig.connect(self.get_pandas)
        self.get_pandas_thread.start()
        self.create_panda_thread = utils.MFetchDataThread(using_cache=False)
        self.create_panda_thread.result_sig.connect(self.get_pandas)
        self.msg = None
        self.this_panda = {}

    def get_pandas(self, pandas):
        if isinstance(pandas, list):
            for p in pandas:
                self.panda_dict[p.get('code')] = p#.get('id')
                if p.get('sg_login_name') == os.environ.get('SG_PANDA'):
                    self.this_panda = p
                    os.environ['SG_PANDA_NICK_NAME'] = p.get('code').encode('gbk')
            if self.this_panda.get('sg_login_name'):
                os.environ['SG_PANDA_DICT'] = str(self.panda_dict)
                return
            self.show()
            return True
        #  如果到这里了说明是创建当前小熊猫成功了
        try:
            self.panda_dict[pandas.get('code')] = pandas#.get('id')
            os.environ['SG_PANDA_NICK_NAME'] = pandas.get('code').encode('gbk')
            os.environ['SG_PANDA_DICT'] = str(self.panda_dict)
        except Exception as e:
            MMessage.error(parent=self, text=u'出现了错误！%s' % e, duration=2)
        # print "os.environ['SG_PANDA_DICT']", os.environ['SG_PANDA_DICT']
        if self.msg:
            self.msg.close()
        self.close()
        return True

    def create_panda(self):
        if not self.line_edit.text():
            MMessage.error(parent=self, text=u'请输入绰号哦！', duration=3)
            return
        self.msg = MMessage.info(parent=self, text=u'正在创建...', duration=999)
        self.create_panda_thread.mode = 'create'
        self.create_panda_thread.data = [os.environ.get('SG_PANDA_ENTITY'), {'code': self.line_edit.text(),
                                                          'sg_login_name': os.environ.get('SG_PANDA'),
                                                          }, ['code']]
        self.create_panda_thread.using_cache = False
        self.create_panda_thread.start()
        pass


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication

    app = QApplication(sys.argv)
    test = WGetPandaWin()
    from dayu_widgets.theme import MTheme
    light = MTheme('dark')
    light.apply(test)
    test.show()
    sys.exit(app.exec_())
