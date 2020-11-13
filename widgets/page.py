#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.6
# wechat : 18250844478
###################################################################
import os
import pprint

from dayu_widgets.item_model import MTableModel, MSortFilterModel
from dayu_widgets.item_view import MTableView
from dayu_widgets.divider import MDivider
from dayu_widgets.message import MMessage
from dayu_widgets.qt import *
from dayu_widgets import dayu_theme
from operator import methodcaller
import datetime

import utils
import thumbnail_delegate
from actions import register as actions_register


class WTableView(MTableView):
    selection_changed = Signal(list)

    def __init__(self, *args, **kwargs):
        super(WTableView, self).__init__()
        self.is_showing = False

    def show_pic(self, img):
        thumbnail_win = QDialog(self.parent())
        thumbnail_win.setWindowTitle(u'缩略图详情')
        layout = QHBoxLayout()
        label = QLabel()
        label.setPixmap(QPixmap(img))
        layout.addWidget(label)
        thumbnail_win.setLayout(layout)
        thumbnail_win.show()

    def selectionChanged(self, selected, deselected):
        self.selection_changed.emit([selected, deselected])

    # def event(self, event):
    #     if event.type() == QEvent.Type.HoverMove:
    #         pos = event.pos()
    #         current_index = self.indexAt(pos)
    #         if not current_index.column() == 2:
    #             thumbnail_win.close()
    #             event.accept()
    #             return True
    #         img = current_index.data(Qt.DisplayRole)
    #         if self.is_showing and img == self.img:
    #             thumbnail_win.mapToGlobal(pos)
    #             event.accept()
    #             return True
    #         self.show_pic(img)
    #         thumbnail_win.mapToGlobal(pos)
    #     event.accept()
    #     return True
    
    def mouseDoubleClickEvent(self, event):
        current_index = self.currentIndex()
        if not current_index.column() == 2:
            return
        img = current_index.data(Qt.DisplayRole)
        self.show_pic(img)


class SheetContent(QWidget):
    parse_finished = Signal(bool)

    def __init__(self, config=None,  parent=None):
        super(SheetContent, self).__init__(parent=parent)
        # self.setMinimumHeight(970)
        self.__config = {}
        self.set_config(config)
        self.header = []
        self.data = []
        self.actions = {}
        self.svg = None
        self.name = None
        self.msg = None
        self.results = []
        self.msg_parent = utils.get_widget_top_parent(self)
        self.project = None
        self.user = os.environ.get('SG_PANDA')
        self.action_param = {}  # 用来传递给action的参数
        self.is_load = False  # 切换tab时是否需要刷新数据的标志
        self.show_msg = False

        self.model = MTableModel()
        self.model_sort = MSortFilterModel()
        self.table = WTableView(size=dayu_theme.small, show_row_count=False)
        self.table.setShowGrid(True)
        self.table.set_no_data_text(u'没有锅！！！')
        self.table.set_no_data_image(MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/page-wuguo.png'))
        self.table.horizontalHeader().setStretchLastSection(1)
        self.main_lay = QGridLayout()
        self.model_sort.setSourceModel(self.model)
        self.table.setModel(self.model_sort)
        self.table.setShowGrid(True)
        self.main_lay.setContentsMargins(0, 0, 0, 0)
        self.main_lay.addWidget(self.table, 0, 0, 1, 1)
        self.divider = MDivider(u'共0个')
        self.main_lay.addWidget(self.divider)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_menu)
        self.table.contextMenu = QMenu(self)

        self.setLayout(self.main_lay)

        self.fetch_data_thread = utils.MFetchDataThread(using_cache=True)
        self.fetch_data_thread.result_sig.connect(self.get_fetch_result)
        # 监控连接超时
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_thread_running)

    def check_thread_running(self):
        if not self.is_load:
            print 'Retrying Connecting...'
            if self.msg:
                self.msg._content_label.setText(u'连接超时，正在重试...')
            self.fetch_data_thread.terminate()
            self.fetch_data_thread.wait()
            # self.fetch_data_thread.quit()
            self.fetch_data_thread.start()
            self.timer.start(5000)

    def show_menu(self, *args):
        selected_indexes = self.table.selectedIndexes()
        rows = list(set([index.row() for index in selected_indexes]))
        self.action_param.update({'id': [int(self.model_sort.index(row, 0).data()) for row in rows]})
        self.action_param.update({'selected': self.get_selected_content()})
        self.table.contextMenu.popup(QCursor.pos())
        self.table.contextMenu.show()

    @Slot()
    def add_action(self, action_data):
        self.table.contextMenu.clear()
        self.actions.clear()
        i = 0
        for each in action_data:
            try:
                label, method, icon, mode = each['label'], each['value'], each['icon'], each['mode']
            except KeyError:
                continue
            if method in self.actions.values():
                continue

            # if mode == '0':  # 如果不是右键菜单，就以双击方式启动
            #     self.table.doubleClicked.connect(lambda i=i, method=method:
            #                                      methodcaller(method, self.action_param)(actions_register))
            #     continue
            self.actions.update({label: method})
            action = self.table.contextMenu.addAction(MIcon(icon, dayu_theme.primary_color), label)
            action.triggered.connect(
                lambda i=i, method=method: methodcaller(method, self.action_param)(actions_register))
            i += 1
        self.__config['page_actions'] = action_data

    def set_up(self, *args):
        new_header = []
        for each_head in self.header:
            if 'order' in each_head.keys():
                if not isinstance(each_head['order'], Qt.SortOrder):
                    del each_head['order']
            new_header.append(each_head)
        self.header = new_header[:]
        self.model.set_header_list(self.header)
        self.model_sort.set_header_list(self.header)
        self.table.set_header_list(self.header)
        self.set_current_page()

    def set_current_page(self, *args):
        self.model.set_data_list(self.data)

    def set_config(self, config):
        if config:
            self.__config = config

    def get_config(self, *args):
        return self.__config

    def get_selected_content(self, *args):
        selected_indexes = self.table.selectedIndexes()
        rows = list(set([index.row() for index in selected_indexes]))
        selected_ids = [int(self.model_sort.index(row, 0).data()) for row in rows]
        result_data = []
        for each_data in self.data:
            if each_data["id"] in selected_ids:
                for r in self.results:
                    if r.get('id') == each_data.get('id'):
                        each_data.update({'sg_data': r})
                        break
                result_data.append(each_data)
        return result_data

    def parse_config(self, *args):
        self.data = []
        self.header = []
        entity_type = self.__config['page_type']
        filters = self.__config['page_filters']
        order = self.__config.get('page_order', None)
        fields = [f['key'] for f in self.__config['page_fields']]
        self.svg = self.__config.get('page_svg', None)
        self.name = self.__config.get('page_name', None)

        page_fields_order = self.__config.get('page_fields_order', None)

        self.header = [{'label': u'编号', 'key': 'id', 'searchable': False, 'show': 0}]
        self.header.extend(self.__config['page_fields'])

        if page_fields_order:
            try:
                self.header = sorted(self.header, key=lambda x: int(page_fields_order[x['label']]))
            except KeyError:
                pass

        self.fetch_data_thread.mode = 'find'
        self.fetch_data_thread.data = [entity_type, filters, fields, order]
        if self.show_msg:
            MMessage.config(duration=99)
            if self.msg:
                self.msg.close()
            self.msg = MMessage.loading(u'读取中...', parent=self.msg_parent)
        self.fetch_data_thread.start()
        self.timer.start(5000)

    def get_fetch_result(self, results):
        self.results = results
        self.divider.set_dayu_text(u'共%s个'% len(results))
        thumbnail_list = []
        for index, each_result in enumerate(results):
            result_dict = {}
            for field, value in each_result.items():
                field_name = field
                field_value = value
                if type(field_value) == dict:
                    # print field_value
                    value = field_value['name']
                result_dict.update({field_name: value})
            self.data.append(result_dict)  # pass
            # pprint.pprint(each_result)
            if each_result.get('sg_thumbnail_path'):
                thumbnail_list.append(each_result.get('sg_thumbnail_path'))
        self.set_up()
        # 使用delegate来显示缩略图
        if thumbnail_list:
            td = thumbnail_delegate.WThumbnailDelegate(parent=self.table)
            self.table.setItemDelegateForColumn(2, td)
            self.table.setColumnWidth(2, 100)
            # self.table.resizeRowsToContents()
        # self.table.resizeColumnsToContents()
        # 传入调用actions时需要的参数
        self.action_param['project'] = self.project
        self.action_param['user'] = self.user
        self.action_param['type'] = self.__config['page_type']
        self.action_param['widget'] = utils.get_widget_top_parent(self)
        self.action_param['config'] = self.__config
        if self.__config['page_actions']:
            self.add_action(self.__config['page_actions'])
        if self.show_msg:
            MMessage.config(1)
            MMessage.success(u'数据拉取成功！', parent=self.msg_parent)
            self.msg.close()
        self.is_load = True
        self.timer.stop()
        for i, ef in enumerate(self.header):
            if ef.get('show') == 0:
                self.table.hideColumn(i)
        self.parse_finished.emit(True)


if __name__ == '__main__':
    import sys
    from dayu_widgets import dayu_theme
    from dayu_widgets.qt import QApplication

    app = QApplication(sys.argv)
    config = {"page_actions": [],
                      "page_fields": [{'searchable': True, 'key': 'content', 'label': u'任务名'}],
                      "page_filters": [['project.Project.id', 'is', 192], ['entity', 'type_is', 'Shot']],
                      "page_name": u"所有版本",
                      "page_type": "Task",
                      "page_svg": "calendar_line.svg"}
    page = SheetContent(config=config)
    page.show_msg = True
    page.parse_config()
    dayu_theme.apply(page)
    page.show()
    sys.exit(app.exec_())
