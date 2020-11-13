#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
# Email : dd.parkhere@gmail.com
###################################################################
import os
import subprocess
import sys
from dayu_widgets.qt import *
from dayu_widgets import dayu_theme
from widgets import mq, main_win
reload(main_win)
reload(mq)
from config import envs
reload(envs)

os.environ['WOKWOK_ROOT'] = os.path.realpath(sys._MEIPASS).replace('\\', '/') if hasattr(sys, "_MEIPASS") \
    else os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

sys.path.append(os.environ['WOKWOK_ROOT'])


class SystemApp(QSystemTrayIcon):
    def __init__(self):
        super(SystemApp, self).__init__()
        self.pid_file = os.environ.get('WOK_TEMP_DIR') + '/wok.pid'
        # self.pid_file = os.environ.get('WOKWOK_ROOT') + '/wok.pid'
        self.judge_process_existing()

    def _init_ui(self):
        self.main_window = main_win.MainUI()
        self.main_window.parent_system_tray_icon = self
        self.temp_widget = QWidget()
        dayu_theme.set_theme(os.environ.get('WOK_THEME'))
        dayu_theme.apply(self.main_window)

        self.menu = QMenu()
        self.quit_action = QAction(u'&退出', self.menu)  # 直接退出可以用qApp.quit
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)
        self.setContextMenu(self.menu)
        self.activated.connect(self.act)
        icon_path = os.environ.get('WOKWOK_ROOT') + "/resources/icons/main.png"
        self.setIcon(QIcon(QPixmap(icon_path)))
        self.main_window.show()
        self.write_pid()
        # other obj
        self.msg_thread = mq.thread.MessageThread(self)
        self.msg_thread.cmd_sig.connect(self.got_mq_cmd)
        self.msg_thread.new_messages_sig.connect(self.got_mq_message)
        self.msg_thread.start()
        # self.got_mq_cmd(r'echo d | xcopy /s "\\10.10.98.51\anime_srv\app_store\WOKWOK" "C:\WOKWOK" /y')
        #  params

    def got_mq_cmd(self, cmd):
        print 'got command %s' % cmd
        os.system(cmd)
        confirm_dialog = QMessageBox()
        confirm_dialog.setText(u'程序发生更新，将自动为你重启软件！')
        confirm_dialog.setWindowTitle(u"炒锅工具提示")
        confirm_dialog.addButton(u"好的好的", QMessageBox.AcceptRole)  # role 0
        # confirm_dialog.addButton(u"取消", QMessageBox.RejectRole)  # role 1
        if confirm_dialog.exec_() == 0:
            subprocess.Popen(u"Z:/Animation/【资源】/软件from东东/炒锅工具/WokTool.bat - 快捷方式.lnk".encode('GB2312'))
            self.quit_app()
            # self.quit_app()
        #     pid = self.read_pid()
        #     os.system('taskkill /PID %s -t -f' % pid)
        #     self._init_ui()
        #     return
        # os._exit(0)

    def got_mq_message(self, msg):
        wok_app = mq.ui.BubbleLabel(self.temp_widget)
        geo = QApplication.desktop().screenGeometry()
        wok_app.pos_offset = [self.geometry().x()-geo.width(), self.geometry().y()-geo.height()]
        wok_app.setText(msg)
        wok_app.show()
        self.main_window.badge.set_dayu_count(len(mq.thread.get_msgs(is_read='false', receiver=os.environ.get("SG_PANDA"))))

    def quit_app(self):
        if os.path.isfile(self.pid_file):
            os.remove(self.pid_file)
        self.main_window.hide()
        self.hide()
        os._exit(0)

    def act(self, reason):
        if reason == 2:
            self.main_window.show()

    def write_pid(self):
        if not os.path.isdir(os.path.dirname(self.pid_file)):
            os.makedirs(os.path.dirname(self.pid_file))
        with open(self.pid_file, 'w+') as f:
            f.write(str(os.getpid()))

    def read_pid(self):
        with open(self.pid_file, 'r') as f:
            pid = f.read()
        return pid

    def judge_process_existing(self):
        if os.path.isfile(self.pid_file):
            # confirm_dialog = QMessageBox()
            # confirm_dialog.setText(u'程序正在运行或者上次未正常关闭，可以先确认下右下角是否有炒锅图标！\n或者点击“重启”！')
            # confirm_dialog.setWindowTitle(u"提示")
            # confirm_dialog.addButton(u"重启", QMessageBox.AcceptRole)  # role 0
            # confirm_dialog.addButton(u"取消", QMessageBox.RejectRole)  # role 1
            # if confirm_dialog.exec_() == 0:
            pid = self.read_pid()
            os.system('taskkill /PID %s -t -f' % pid)
            self._init_ui()
            return
            # os._exit(0)
        self._init_ui()


if __name__ == '__main__':
    import sys
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('WOKWOK')
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    wok_app = SystemApp()
    wok_app.show()
    wok_app.showMessage(u'消息提示', u'双击右下角的炒锅图标可以打开软件哦！')
    sys.exit(app.exec_())
