#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.10
###################################################################


#  用来将文件归档到p4

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


class SubmitToP4(QThread):

    def __init__(self, parent=None):
        super(SubmitToP4, self).__init__(parent=parent)
        self.upload_dir = ''
        self.p4 = None

    def run(self):
        self.p4.run('add', self.upload_dir + '/...')
        self.p4.run_submit('-d', 'from wok tool')


class P4SubmitWin(QDialog):

    def __init__(self, parent=None, config={}):
        super(P4SubmitWin, self).__init__(parent=parent)
        self.setWindowTitle(u'归档至p4')
        if not config.get('selected'):
            MMessage.config(3)
            MMessage.error(parent=self.parent(), text=u'请选中锅再操作哦~', duration=3)
            return
        self.version_detail = self.parent().current_wok_version
        self.wok_detail = config
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setMinimumWidth(600)

        layout = QGridLayout()
        self.user_name_le = MLineEdit()
        self.user_name_le.setEnabled(True)
        # self.user_name_le.setText(os.environ.get('SG_PANDA'))
        self.user_name_le.setText(os.environ.get('SG_PANDA'))

        self.p4_port_le = MLineEdit()
        self.p4_port_le.setEnabled(False)
        # self.p4_port_le.setText(os.environ.get('P4_PORT'))
        self.p4_port_le.setText('bh3p4.mihoyo.com:2333')

        self.password_le = MLineEdit().password()
        # self.password_le.setText()

        self.client_cb = MComboBox()
        self.client_menu = MMenu()
        self.client_cb.set_menu(self.client_menu)

        layout.addWidget(MLabel(u'用户名:'), 0, 0)
        layout.addWidget(self.user_name_le, 0, 1)

        layout.addWidget(MLabel(u'Port:'), 1, 0)
        layout.addWidget(self.p4_port_le, 1, 1)

        layout.addWidget(MLabel(u'密码:'), 2, 0)
        layout.addWidget(self.password_le, 2, 1)

        self.login_pb = MPushButton(u'登录')

        layout.addWidget(self.login_pb, 3, 1)

        # layout.addWidget(self.client_cb, 4, 1)

        self.down_widget = QWidget()
        down_layout = QGridLayout()
        self.down_widget.setLayout(down_layout)
        self.down_widget.hide()
        self.client_root_detail_lb = MLabel()
        self.client_root_detail_lb.setEnabled(False)
        self.client_cb.setMaximumWidth(300)

        down_layout.addWidget(MLabel(u'选择工作区:'), 0, 0)
        down_layout.addWidget(self.client_cb, 0, 1)
        down_layout.addWidget(self.client_root_detail_lb, 0, 2)

        down_layout.addWidget(MLabel(u'p4本地归档路径：'), 1, 0)
        self.p4_path_le = MLineEdit()
        self.p4_path_le.setPlaceholderText(u'请先输入本地p4归档路径后回车...')
        down_layout.addWidget(self.p4_path_le, 1, 1)

        self.download_to_local_pb = MPushButton(u'开始同步！')
        self.download_to_local_pb.setEnabled(False)
        down_layout.addWidget(self.download_to_local_pb, 1, 2)

        self.upload_to_p4_server_pb = MPushButton(u'上传至p4')
        self.upload_to_p4_server_pb.setEnabled(False)
        down_layout.addWidget(self.upload_to_p4_server_pb, 2, 1)

        main_layout.addLayout(layout)
        main_layout.addWidget(self.down_widget)

        self.client_cb.sig_value_changed.connect(self.set_root_info)
        self.login_pb.clicked.connect(self.run_login)
        self.p4_path_le.editingFinished.connect(self.check_path)
        self.download_to_local_pb.clicked.connect(self.download_to_p4_local)
        self.upload_to_p4_server_pb.clicked.connect(self.upload_to_p4_server)

        self.copy_file_thread = utils.CopyFile()
        self.copy_file_thread.finished.connect(self.finish_copying)

        self.upload_to_p4_thread = SubmitToP4()
        self.upload_to_p4_thread.finished.connect(self.finish_submiting)

        self.update_wok_status = utils.MFetchDataThread()
        self.update_wok_status.finished.connect(self.finish_updating)

        self.q_settings = QSettings(u'ANIME_WOK_CONFIG', 'p4_config')
        self.client_dict = {}
        self.root = ''
        self.current_path = ''
        self.p4 = None
        self.get_config()
        self.msg = None

    def run_login(self):
        user = str(self.user_name_le.text())
        pass_word = str(self.password_le.text())
        port = str(self.p4_port_le.text())
        self.p4 = P4.P4()
        self.p4.user = user
        self.p4.port = port
        self.p4.password = pass_word
        try:
            self.p4.connect()
            self.p4.run_login()
            for client in self.p4.run_clients('-u', user):
                self.client_dict[client.get('client')] = client.get('Root')
        except:
            self.login_pb.setText(u'登录出现错误！')
            return
        self.q_settings.setValue('password', pass_word)
        self.login_pb.hide()
        self.down_widget.show()
        self.client_menu.set_data(self.client_dict.keys())

    def set_root_info(self, current_client):
        self.client_root_detail_lb.setText(u'本地工作区：'+self.client_dict.get(current_client).replace('\\', '/'))
        self.root = self.client_dict.get(current_client).replace('\\', '/')
        self.q_settings.setValue('client', current_client)
        self.p4.client = str(current_client)
        self.check_path()
        pass

    def get_config(self):
        password = self.q_settings.value('password')
        client = self.q_settings.value('client')
        if not password or not client:
            return
        self.password_le.setEnabled(False)
        self.password_le.setText(password)
        self.run_login()
        self.client_cb.setEditText(client)
        self.set_root_info(client)

    def check_path(self):
        current_path = self.p4_path_le.text().replace('\\', '/').replace('//', '/').rstrip('/')
        if not current_path:
            return
        if self.root.lower() not in current_path.lower():
            MMessage.config(3)
            MMessage.error(u'路径必须是本地工作区的路径！', self.parent())
            self.p4_path_le.setText('')
            return
        self.p4_path_le.setText(current_path)
        self.download_to_local_pb.setEnabled(True)
        self.current_path = current_path

    def download_to_p4_local(self):
        version_path = self.version_detail.get('sg_path')
        dest_path = self.current_path
        self.copy_file_thread.copy_list = [[version_path, dest_path]]
        self.copy_file_thread.start()
        MMessage.config(50)
        self.msg = MMessage.info(u'正在拷贝，请稍等。。。', self.parent())

    def finish_copying(self):
        if self.msg:
            self.msg.close()
            MMessage.config(3)
            MMessage.success(u'拷贝完成!', self.parent())
        # 在fileDialog中修改命名
        file_dialog = QFileDialog(self.parent(), u"请修改文件命名",
                                                  self.current_path,
                                                  "All Files (*);;"
                                                  )
        file_dialog.setFileMode(QFileDialog.AnyFile)
        widgets_to_hide = []
        widgets_to_hide.extend(file_dialog.findChildren(QPushButton)[:-1])
        widgets_to_hide.extend(file_dialog.findChildren(QLabel))
        widgets_to_hide.extend(file_dialog.findChildren(QLineEdit))
        widgets_to_hide.extend(file_dialog.findChildren(QComboBox))
        file_dialog.setLabelText(QFileDialog.Reject, u'改完了！')
        # print(widgets_to_hide)
        for each in widgets_to_hide:
            each.hide()
        file_dialog.findChildren(QSplitter)[0].setSizes([0, 300])
        file_dialog.exec_()
        self.download_to_local_pb.setEnabled(False)
        self.upload_to_p4_server_pb.setEnabled(True)

    def upload_to_p4_server(self):
        #  传到p4之后要更改锅的状态
        self.upload_to_p4_thread.upload_dir = self.current_path
        self.upload_to_p4_thread.p4 = self.p4
        self.upload_to_p4_thread.start()
        MMessage.config(50)
        self.msg = MMessage.info(u'正在上传，请稍等。。。', self.parent())
        self.upload_to_p4_server_pb.setEnabled(False)
        # try:
        #     self.p4.run('add', str(self.p4_path_le.text())+'/...')
        #     self.p4.run_submit('-d', u'from wok tool')
        # except Exception as e:
        #     print e
        #     MMessage.config(5)
        #     MMessage.error(u'发生错误!%s'%e, self.parent())
        #     return
        # self.p4.disconnect()
        # MMessage.success(u'归档成功！', self.parent())
        # self.close()
        pass

    def finish_submiting(self):
        if self.msg:
            self.msg.close()
        self.p4.disconnect()
        MMessage.config(999)
        self.msg = MMessage.loading(u'正在更新锅状态...', self.parent())
        self.update_wok_status.mode = 'update'
        self.update_wok_status.data = [os.environ.get('WOK_ENTITY'), self.wok_detail.get('selected')[0].get('id'),
                                       {'sg_status_list': 'wf',
                                        'sg_p4_path': self.current_path[1:].replace(self.root[1:], '//depot')}
                                       ]
        self.update_wok_status.start()
        pass

    def finish_updating(self):
        if self.msg:
            self.msg.close()
        MMessage.config(3)
        MMessage.success(u'归档成功！', self.parent())
        self.parent().current_page.parse_config()
        self.close()
        pass


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication
    from dayu_widgets import dayu_theme
    app = QApplication(sys.argv)

    file_dialog = QFileDialog(None, u"请修改文件命名",
                              "D:/",
                              "All Files (*);;"
                              )
    file_dialog.setFileMode(QFileDialog.AnyFile)
    widgets_to_hide = []
    widgets_to_hide.extend(file_dialog.findChildren(QPushButton)[:-1])
    widgets_to_hide.extend(file_dialog.findChildren(QLabel))
    widgets_to_hide.extend(file_dialog.findChildren(QLineEdit))
    widgets_to_hide.extend(file_dialog.findChildren(QComboBox))
    file_dialog.setLabelText(QFileDialog.Reject, u'改完了！')
    for each in widgets_to_hide:
        each.hide()
    file_dialog.findChildren(QSplitter)[0].setSizes([0, 300])
    file_dialog.exec_()
    # test = P4SubmitWin()
    # dayu_theme.apply(test)
    # test.show()

    sys.exit(app.exec_())