#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
###################################################################
import json
import os

from dayu_widgets.divider import MDivider
from dayu_widgets.flow_layout import MFlowLayout
from dayu_widgets.qt import *
from dayu_widgets.tool_button import MToolButton
from dayu_widgets import dayu_theme
from dayu_widgets.label import MLabel
from dayu_widgets.line_tab_widget import MLineTabWidget
from dayu_widgets.push_button import MPushButton
from dayu_widgets.message import MMessage
from dayu_widgets.badge import MBadge
import combo_box, page, tree_view, utils, wok_version_card, \
       version_detail_field, set_path, get_pandas, create_wok, retake_win, mq, msg_box, filter_tab, wok_comments
reload(combo_box)
reload(page)
reload(tree_view)
reload(utils)
reload(wok_version_card)
reload(version_detail_field)
reload(set_path)
reload(get_pandas)
reload(create_wok)
reload(retake_win)
reload(msg_box)
reload(mq)
reload(filter_tab)
reload(wok_comments)
from config import page_settings
reload(page_settings)


class MainUI(QMainWindow):
    def __init__(self, parent=None):
        super(MainUI, self).__init__(parent)
        geo = QApplication.desktop().screenGeometry()
        self.setGeometry(geo.width() / 6, geo.height() / 6, geo.width() / 1.3, geo.height() / 1.3)
        self._init_ui()
        self._connect_slot()

    def _init_ui(self):
        current_user = os.environ.get("SG_PANDA")
        self.setWindowTitle(u'苦逼小熊猫炒锅台 v0.2 Beta                       当前用户: %s' % current_user)
        self.setWindowIcon(QIcon(os.environ['WOKWOK_ROOT'] + '/resources/icons/main.png'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)

        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(50)
        toolbar_lay = QHBoxLayout()
        toolbar_widget.setLayout(toolbar_lay)

        toolbar_lay.addWidget(MLabel(u'选择项目:'))
        self.proj_cb = combo_box.WComboBox(self).small()
        toolbar_lay.addWidget(self.proj_cb)

        self.setting_tb = MToolButton(parent=self)
        self.setting_tb.setMinimumSize(30, 40)
        self.setting_tb.set_dayu_svg(os.environ['WOKWOK_ROOT'] + '/resources/icons/toolbar_setting.png')
        toolbar_lay.addWidget(self.setting_tb)

        # toolbar_lay.addWidget(MDivider.vertical())

        self.create_wok_pb = MToolButton(self)
        self.create_wok_pb.set_dayu_svg(os.environ['WOKWOK_ROOT'] + '/resources/icons/wok-new.png')
        toolbar_lay.addWidget(self.create_wok_pb)

        self.refresh_pb = MToolButton(self)
        self.refresh_pb.set_dayu_svg(os.environ['WOKWOK_ROOT'] + '/resources/icons/refresh.png')
        toolbar_lay.addWidget(self.refresh_pb)

        toolbar_lay.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # toolbar_lay.setSpacing(20)
        self.msg_box_tb = MToolButton(self).large()
        self.msg_box_tb.set_dayu_svg('alert_fill.svg')
        self.badge = MBadge.dot(True, widget=self.msg_box_tb)
        self.badge.set_dayu_count(len(mq.thread.get_msgs(is_read='false', receiver=os.environ.get('SG_PANDA'))))
        # self.msg_box.set_dayu_svg(os.environ['WOKWOK_ROOT'] + '/resources/icons/messages.png')
        toolbar_lay.addWidget(self.badge)


        # 中间的表格部分
        self.tabs_widget = MLineTabWidget()
        self.all_tabs = []
        self.my_task_sheet_widget = page.SheetContent(parent=self)
        self.task_in_progress_sheet_widget = page.SheetContent(parent=self)

        self.G_look_sheet_widget = page.SheetContent(parent=self)
        self.G_ok_sheet_widget = page.SheetContent(parent=self)

        self.optimize_sheet_widget = page.SheetContent(parent=self)
        self.file_sheet_widget = page.SheetContent(parent=self)
        # self.qt_sheet_widget = page.SheetContent(parent=self)
        # self.qt_sheet_widget.show_msg = True
        self.all_tabs = [self.my_task_sheet_widget, self.task_in_progress_sheet_widget, self.G_look_sheet_widget,
                         self.G_ok_sheet_widget, self.optimize_sheet_widget, self.file_sheet_widget]#, self.qt_sheet_widget]
        # self.my_task_sheet_widget.parse_config()
        # self.G_look_sheet_widget.parse_config()
        # self.G_ok_sheet_widget.parse_config()

        self.tabs_widget.add_tab(self.my_task_sheet_widget,
                                 {'text': u'我的', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/my-wok.svg'})
        self.tabs_widget.add_tab(self.task_in_progress_sheet_widget,
                                 {'text': u'进行中', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/wok-inprogress.png'})
        self.tabs_widget.add_tab(self.G_look_sheet_widget,
                                 {'text': u'G 看', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/G-look2.svg'})
        self.tabs_widget.add_tab(self.G_ok_sheet_widget,
                                 {'text': u'G OK', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/G-ok2.svg'})
        self.tabs_widget.add_tab(self.optimize_sheet_widget,
                                 {'text': u'整合翻译', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/wp.png'})
        self.tabs_widget.add_tab(self.file_sheet_widget,
                                 {'text': u'归档', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/wok-file.png'})
        # self.tabs_widget.add_tab(self.qt_sheet_widget,
        #                          {'text': u'QT', 'svg': os.environ['WOKWOK_ROOT'] + '/resources/icons/G-ok2.svg'})
        self.tabs_widget.tool_button_group.set_dayu_checked(0)

        tab_widget = QWidget()
        tab_widget_layout = QHBoxLayout()
        tab_widget.setLayout(tab_widget_layout)
        tab_widget_layout.addWidget(self.tabs_widget)

        self.filter_widget = filter_tab.FilterWidget(parent=self)
        self.filter_widget.setMaximumWidth(250)

        task_list_lay = QGridLayout()

        task_list_lay.addWidget(toolbar_widget, 0, 0)
        task_list_splitter = QSplitter()
        task_list_splitter.addWidget(self.filter_widget)
        task_list_splitter.addWidget(tab_widget)
        task_list_splitter.setLineWidth(10)
        # task_list_splitter.setStretchFactor(20, 30)
        # task_list_splitter.setStretchFactor(10, 10)
        # task_list_lay.addWidget(self.filter_widget, 1, 0)
        # task_list_lay.addWidget(self.tabs_widget, 1, 1)
        task_list_lay.addWidget(task_list_splitter, 1, 0)
        task_list_lay.setSpacing(0)
        left_widget = QWidget()
        left_widget.setLayout(task_list_lay)

        # 右边的版本历史
        right_lay = QVBoxLayout()
        # right_lay.addWidget(MDivider(u'提交历史'))
        scroll = QScrollArea()
        scroll.setMinimumWidth(150)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        # scroll.setAlignment(Qt.AlignTop)
        self.wok_version_widget = wok_version_card.WokVersionListWidget(self)
        scroll.setWidget(self.wok_version_widget)
        right_lay.addWidget(scroll)

        right_lay_2 = QVBoxLayout()
        self.comments_list = wok_comments.CommentField(self)
        right_lay_2.addWidget(self.comments_list)

        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_widget.setLayout(right_lay)

        self.right_tab = MLineTabWidget()
        self.right_tab.add_tab(right_widget, {'text': u'提交历史'})
        self.right_tab.add_tab(self.comments_list, {'text': u'评论'})
        self.right_tab.tool_button_group.set_dayu_checked(0)

        splitter = QSplitter()
        # splitter.addWidget(self.filter_widget)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.right_tab)
        splitter.setStretchFactor(0, 80)
        splitter.setStretchFactor(1, 20)

        up_widget = QWidget()
        up_lay = QVBoxLayout()
        up_widget.setLayout(up_lay)
        # up_lay.addWidget(toolbar_widget)
        up_lay.addWidget(splitter)

        self.look_tree_view = tree_view.WFileTreeView()
        self.look_tree_view.setMinimumSize(100, 100)
        self.look_tree_view.setMaximumHeight(230)
        # self.look_tree_holder = MLabel(u'这儿什么也没有o(╯□╰)o').strong().warning()
        # self.look_tree_holder.set_dayu_image(MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/no-files.svg'))
        # self.look_tree_holder.setMinimumSize(300, 100)
        # self.look_tree_holder.setMaximumHeight(230)
        # self.look_tree_holder.hide()
        look_widget = QWidget()
        look_layout = QVBoxLayout()
        look_widget.setLayout(look_layout)
        look_top_layout = QHBoxLayout()
        # look_top_layout.addWidget(MLabel(u'文件列表：'))
        look_top_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.look_ok_pb = MPushButton(u'OK',  MIcon('success_fill.svg', '#ddd')).small().success()
        self.look_nook_pb = MPushButton(u'不OK',  MIcon('close_fill.svg', '#fff')).small().danger()
        self.look_waite_pb = MPushButton(u'等等看',  MIcon('circle.svg', '#cec15a')).small().warning()
        look_top_layout.addWidget(self.look_ok_pb)
        look_top_layout.addWidget(self.look_nook_pb)
        look_top_layout.addWidget(self.look_waite_pb)
        look_layout.addLayout(look_top_layout)
        look_layout.addWidget(self.look_tree_view)
        # look_layout.addWidget(self.look_tree_holder)

        self.version_detail_widget = version_detail_field.WFieldMixin(self)
        self.version_detail_widget.setMinimumWidth(500)
        self.version_detail_widget.setMaximumHeight(230)

        splitter_down = QSplitter(Qt.Horizontal)
        splitter_down.addWidget(look_widget)
        splitter_down.addWidget(self.version_detail_widget)
        splitter_down.setSizes([450, 450])
        # splitter_down.setStretchFactor(0, 20)
        # splitter_down.setStretchFactor(1, 5)

        splitter_main = QSplitter(Qt.Vertical)
        splitter_main.addWidget(up_widget)
        splitter_main.addWidget(splitter_down)
        # splitter_main.setStretchFactor(80, 0)
        # splitter_main.setStretchFactor(20, 1)

        main_lay = QVBoxLayout()
        main_lay.addWidget(splitter_main)

        self.central_layout.addLayout(main_lay)
        # other windows
        self.get_panda_window = get_pandas.WGetPandaWin()
        dayu_theme.apply(self.get_panda_window)
        self.msg = None
        # necessary param for self
        self.parent_system_tray_icon = None
        self.current_wok_version = ''

    def _connect_slot(self):
        self.setting_tb.clicked.connect(self.set_server_path)
        self.proj_cb.sig_value_changed.connect(self.change_current_project)
        self.tabs_widget.stack_widget.currentChanged.connect(self.change_current_page)
        for tab in self.all_tabs:
            tab.table.selection_changed.connect(self.select_wok_changed)
            tab.parse_finished.connect(self.current_page_parsing_finished)
            self.filter_widget.start_filter_sig.connect(tab.model_sort.set_search_pattern)
            self.filter_widget.show_thumb_cb.stateChanged.connect(self.toggle_show_thumb)
        self.wok_version_widget.finished_adding.connect(self.finish_adding_cards)
        self.wok_version_widget.card_changed.connect(self.card_select_changed)
        self.create_wok_pb.clicked.connect(self.show_create_wok_win)
        self.refresh_pb.clicked.connect(self.refresh_current_page)
        self.look_ok_pb.clicked.connect(self.set_wok_ok)
        self.look_nook_pb.clicked.connect(self.set_wok_retake)
        self.look_waite_pb.clicked.connect(self.set_wok_waite)
        self.msg_box_tb.clicked.connect(self.show_msg_box)
        self.right_tab.tool_button_group.sig_checked_changed.connect(lambda: self.select_wok_changed(1))
        self.comments_list.finish_setting_up_sig.connect(lambda: self.current_page.setEnabled(True))

    def toggle_show_thumb(self, checked):
        if not checked:
            self.current_page.table.hideColumn(2)
        else:
            self.current_page.table.showColumn(2)
            # self.current_page.parse_config()
        # if

    def set_wok_ok(self):
        if not self.current_wok_version:
            MMessage.error(parent=self, text=u'未选中任何版本！', duration=3)
            return
        self.change_status_to(u'确定要把这个锅ok了嘛？？？\n%s'
                              % self.current_wok_version.get('sg_wok.%s.code'% os.environ.get('WOK_ENTITY')), 'wo')

    def set_wok_retake(self):
        if not self.current_wok_version:
            MMessage.error(parent=self, text=u'未选中任何版本！', duration=3)
            return
        win = retake_win.RetakeWin(self, self.current_wok_version)
        win.show()
        pass

    def set_wok_waite(self):
        if not self.current_wok_version:
            MMessage.error(parent=self, text=u'未选中任何版本！', duration=3)
            return
        self.change_status_to(u'要把这个锅状态改成等等看嘛？？？\n%s'
                              % self.current_wok_version.get('sg_wok.%s.code'%os.environ.get('WOK_ENTITY')), 'wh')

    def change_status_to(self, text, status):
        status_dict = eval(os.environ['STATUS_DICT'])
        confirm_dialog = QMessageBox(parent=self)
        # confirm_dialog.setText(u'要把这个锅状态改成等等看嘛？？\n%s' % self.current_wok_version.get('sg_wok.%s.code'%os.environ.get('WOK_ENTITY')))
        confirm_dialog.setText(text)
        confirm_dialog.setWindowTitle(u"提示")
        confirm_dialog.addButton(u"是的，我确定！", QMessageBox.AcceptRole)  # role 0
        confirm_dialog.addButton(u"手滑点错了！", QMessageBox.RejectRole)  # role 1
        answer = confirm_dialog.exec_()
        if answer == 0:
            #  执行变更状态
            MMessage.config(999)
            self.msg = MMessage.loading(text=u'正在执行操作，稍等哦~', parent=self)
            # 如果是ok的话需要把文件移动到publish
            version_path = None
            if status == 'wo':
                old_path = self.current_wok_version.get('sg_path')
                new_path = old_path.replace('/check/', '/publish/')
                self.copy_thread = utils.CopyFile()
                self.copy_thread.copy_list = [[old_path, new_path]]
                self.copy_thread.start()
                version_path = new_path
            # done
            # batch_data = []
            data = {'sg_status_list': status, 'sg_path': version_path} if status == 'wo' else {'sg_status_list': status}
            # batch_data.append({"request_type": "update",
            #                    "entity_type": os.environ.get('WOK_VERSION_ENTITY'),
            #                    "entity_id": self.current_wok_version.get('id'),
            #                    "data": data})
            self.update_version_status = utils.MFetchDataThread('update',
                                                                [os.environ.get('WOK_VERSION_ENTITY'), self.current_wok_version.get('id'), data])
            self.update_version_status.start()
            # batch_data.append({"request_type": "update",
            #                    "entity_type": os.environ.get('WOK_ENTITY'),
            #                    "entity_id": self.current_wok_version.get('sg_wok').get('id'),
            #                    "data":
            #                        {'sg_status_list': status}})
            self.update_wok_status = utils.MFetchDataThread('update', [os.environ.get('WOK_ENTITY'), self.current_wok_version.get('sg_wok').get('id'), {'sg_status_list': status}])
            self.update_wok_status.start()
            self.current_page.setEnabled(False)
            self.update_wok_status.finished.connect(self.current_page.parse_config)
            self.update_wok_status.finished.connect(self.msg.close)
            self.update_wok_status.finished.connect(lambda: self.current_page.setEnabled(True))
            self.update_wok_status.finished.connect(lambda: mq.thread.send(info=u'你的锅%s状态已由 %s 更新为 %s \n操作人：%s'%
                                                                           (self.current_wok_version.get('sg_wok').get('name'),
                                                                            status_dict.get(self.current_wok_version.get('sg_status_list')),
                                                                            status_dict.get(status),
                                                                            os.environ.get('SG_PANDA_NICK_NAME').decode('gbk')
                                                                            ),
                                                                           receiver=self.current_wok_version.get('sg_panda.%s.sg_login_name'%os.environ.get('SG_PANDA_ENTITY')),
                                                                           sender=os.environ.get('SG_PANDA')
                                                                           ),
                                                    )

            # print self.current_wok_version.get('sg_panda.%s.sg_login_name'%os.environ.get('SG_PANDA_ENTITY'))
            # self.current_page.parse_config()
            return
        return

    def show_create_wok_win(self):
        if not os.environ.get('WOK_PROJECT'):
            MMessage.error(parent=self, text=u'未选择项目，请先选项目哦！！', duration=3)
            return
        create_wok_win = create_wok.main.CreateWokMain(self)
        create_wok_win.show()

    def show_msg_box(self):
        msg_box_win = msg_box.UnreadMessageUIClass(self)
        msg_box_win.show()
        pass

    def set_server_path(self):
        wet_win = set_path.SetPath(self)
        wet_win.show()

    def change_current_project(self, value):
        local_wok_dir = QSettings(u'ANIME_WOK_CONFIG', 'SetPath').value('WOK_LOCAL')
        if local_wok_dir:
            os.environ['WOK_LOCAL'] = local_wok_dir
        if not os.environ.get('WOK_LOCAL'):
            MMessage.config(7)
            MMessage.error(parent=self, text=u'未设置本地工作路径，请打开设置填入正确路径！')
            self.set_server_path()
            # raise RuntimeError
        print 'project item changed to :', value
        os.environ['WOK_PROJECT'] = value
        for tab in self.all_tabs:
            tab.is_load = False
            tab.model.clear()
        self.tabs_widget.tool_button_group.set_dayu_checked(0)
        self.change_current_page(0)

    def select_wok_changed(self, indexes):
        if indexes:
            selected_content = self.current_page.get_selected_content()
            if selected_content and selected_content[0].get('type') != os.environ.get('WOK_ENTITY'):
                self.look_tree_view.set_root_path('')
                return
            if selected_content:
                selected_wok_id = selected_content[0].get('id')
                self.wok_version_widget.set_versions_from_wok_id(selected_wok_id)
                sg_result = selected_content[0].get('sg_data')
                self.comments_list.set_up_data = sg_result
                self.current_page.setEnabled(False)

                if self.right_tab.tool_button_group.get_dayu_checked() == 0:
                    self.wok_version_widget.parse()
                else:
                    self.comments_list.set_up()
                # MMessage.config(duration=999)
                # if hasattr(self, 'msg') and self.msg:
                #     self.msg.close()
                # self.msg = MMessage.loading(u'正在拉取版本信息...', parent=self)

    def finish_adding_cards(self, result):
        self.current_page.setEnabled(True)
        # self.msg.close()
        if not result:
            self.current_wok_version = ''
            self.look_tree_view.set_root_path('')
            self.version_detail_widget.set_details(*['-', '-', '-', '-', '-'])
            self.version_detail_widget.view_feedback_detail.hide()

    def card_select_changed(self, version_detail):
        self.current_wok_version = version_detail
        root_path = version_detail.get('sg_path', '')
        self.look_tree_view.set_root_path(root_path)
        self.version_detail_widget.set_details(
                                               (version_detail.get('sg_panda') or {}).get('name'),
                                               version_detail.get('updated_at'),
                                               version_detail.get('sg_version_code'),
                                               version_detail.get('description'),
                                               version_detail.get('sg_feedback')
                                               )
        pass

    @property
    def current_page(self):
        return self.tabs_widget.stack_widget.currentWidget()

    def change_current_page(self, index):
        if not os.environ.get('WOK_PROJECT'):
            return
        reload(page_settings)
        if self.current_page and not self.current_page.is_load:
            # print page_settings.page_configs[index]
            self.current_page.set_config(page_settings.page_configs[index])
            self.current_page.parse_config()

    def current_page_parsing_finished(self, r):
        if r:
            if len(self.current_page.results) > 10:
                self.filter_widget.show_thumb_cb.setChecked(False)
            else:
                self.filter_widget.show_thumb_cb.setChecked(True)

    def refresh_current_page(self):
        print(u'页面已刷新')
        self.current_page.parse_config()

    def closeEvent(self, event):
        self.parent_system_tray_icon.showMessage(u'消息提示', u'双击右下角的炒锅图标可以打开软件哦！')
        event.accept()






