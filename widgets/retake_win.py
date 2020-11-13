#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2019.7
###################################################################
import datetime
import getpass
import json
import os
import shutil

from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.divider import MDivider
from dayu_widgets.push_button import MPushButton
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.message import MMessage
from dayu_widgets.qt import *
import utils
import mq


class WTextEdit(MTextEdit):
    pasted_jpg = Signal(QImage)

    def __init__(self, parent=None):
        super(WTextEdit, self).__init__(parent)

    # 读取截图
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            clipboard = QApplication.clipboard()
            data = clipboard.mimeData()
            if data.urls():
                # print data.urls()
                return
                # for path in data.urls():
                #     print path
            elif data.text():
                self.append(data.text())
                return
            else:
                self.pasted_jpg.emit(clipboard.image())
        super(WTextEdit, self).keyPressEvent(event)


class RetakeWin(QDialog):
    def __init__(self, parent=None, version_detail = None):
        super(RetakeWin, self).__init__(parent)
        self.version_detail = version_detail
        self._init_ui()
        self._init_cfg()

    def _init_ui(self):
        self.setWindowTitle(u'返修')
        self.setMinimumSize(600, 500)
        main_lay = QVBoxLayout()

        main_lay.addWidget(MDivider(u'写一下返修内容吧！(支持ctrl+v粘贴/选择图片+输入文字)'))

        self._add_pic_pb = MToolButton().text_only()
        self._add_pic_pb.setText(u'[+] 选择图片')
        self._grab_pic_pb = MToolButton().text_only()
        self._grab_pic_pb.setText(u'[✄] 截图')
        add_pic_layout = QHBoxLayout()
        add_pic_layout.addWidget(self._add_pic_pb)
        add_pic_layout.addWidget(self._grab_pic_pb)
        add_pic_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_lay.addLayout(add_pic_layout)

        self._feedback_te = WTextEdit(self)
        self._feedback_te.pasted_jpg.connect(self.add_tag)
        main_lay.addWidget(self._feedback_te)
        self._do_it_pb = MPushButton('OK').primary()
        main_lay.addWidget(self._do_it_pb)

        self.setLayout(main_lay)

        self._add_pic_pb.clicked.connect(self.select_pic)
        self._grab_pic_pb.clicked.connect(self.grab_pic)
        self._do_it_pb.clicked.connect(self.doit)
        self.tag_dict = {}
        self.msg = None
        self.img = ''
        self.server_path = ''

    def _init_cfg(self):
        # pass
        feedback_server_format = os.environ.get('WOK_VERSION_FEEDBACK_PATH_FORMAT')
        format_dict = utils.change_dict_encoding(dict(
                                                wok_project = os.environ.get('WOK_PROJECT'),
                                                sg_panda = self.version_detail.get('sg_panda.%s.sg_login_name' % os.environ.get('SG_PANDA_ENTITY')),
                                                status = 'check',
                                                link = self.version_detail.get('sg_wok.%s.sg_link.Shot.code' % os.environ.get('WOK_ENTITY')) or 'sg_wok.%s.sg_link.Asset.code' % os.environ.get('WOK_ENTITY') or 'None',
                                                code = self.version_detail.get('sg_wok.%s.code' % os.environ.get('WOK_ENTITY')),
                                                sg_version_code = self.version_detail.get('sg_version_code')
                                                ), encoding='unicode_escape')
        self.feedback_server = json.loads(json.dumps(feedback_server_format.format(**format_dict)))

    def add_tag(self, img):
        if isinstance(img, QImage) or isinstance(img, QPixmap):
            # print img
            save_to = os.environ.get('WOK_TEMP_DIR') + '/screengrab_temp_%s.jpg' % datetime.datetime.now().strftime('%Y-%b-%d-%H-%M-%S')
            img.save(save_to)
            img = save_to
        dn, fn = os.path.split(img)
        if fn in self.tag_dict.keys():
            return
        server_path = os.path.join(self.feedback_server, fn).replace('\\', '/')
        self.tag_dict[fn] = server_path
        if not os.path.isdir(os.path.dirname(server_path)):
            os.makedirs(os.path.dirname(server_path))
        if not server_path:
            return
        shutil.copyfile(img, server_path)
        # print server_path
        self.img = img
        self.server_path = server_path
        self._feedback_te.append(u"<img src=%s>" % img)

    def select_pic(self):
        file_choose, file_type = QFileDialog.getOpenFileName(self,
                                                                u"选取图片",
                                                                'C:/Users/%s/Desktop'%getpass.getuser(),  # 起始路径
                                                                "All Files (*);;")
        self.add_tag(file_choose)

    def grab_pic(self):
        from utils import grab_pic
        self.add_tag(grab_pic())

    def doit(self):
        all_text = self._feedback_te.toPlainText().replace(self.img, self.server_path)
        i = 0
        while 1:
            if u'\ufffc' not in all_text:
                break
            all_text = all_text.replace(u'\ufffc', u'<img src=%s>' % self.tag_dict.values()[i], 1)
            i += 1
        all_text = all_text.replace('\n', '<br>')
        MMessage.config(999)
        self.update_thread = utils.MFetchDataThread('update', [os.environ.get('WOK_VERSION_ENTITY'), self.version_detail.get('id'),
                                                               {'sg_feedback': all_text, 'sg_status_list': 'wr'}])
        self.update_thread.start()
        self.update_thread_wok = utils.MFetchDataThread('update', [os.environ.get('WOK_ENTITY'), self.version_detail.get('sg_wok').get('id'),
                                                               {'sg_status_list': 'wr'}])
        self.update_thread_wok.start()
        self.update_thread_wok.finished.connect(self.finish_creating)
        self.msg = MMessage.loading(text=u'正在创建，稍等...', parent=self.parent())
        self.update_thread_wok.finished.connect(lambda: mq.thread.send(info=u'你的锅%s收到了一条返修意见：\n%s \n操作人：%s' %
                                                                            (self.version_detail.get('sg_wok').get(
                                                                                'name'),
                                                                             all_text,
                                                                             os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')
                                                                             ),
                                                                       receiver=self.version_detail.get(
                                                                           'sg_panda.%s.sg_login_name' % os.environ.get('SG_PANDA_ENTITY')),
                                                                       sender=os.environ.get('SG_PANDA')
                                                                       )
                                                )
        self._do_it_pb.setEnabled(False)
        self._add_pic_pb.setEnabled(False)
        pass

    def finish_creating(self):
        self.msg.close()
        MMessage.success(text=u'创建成功！', parent=self.parent(), duration=3)
        self.close()


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication
    from dayu_widgets import dayu_theme
    app = QApplication(sys.argv)
    test = RetakeWin()
    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())
