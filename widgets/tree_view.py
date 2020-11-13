#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
# Email : dd.parkhere@gmail.com
###################################################################
import functools
import os
import utils
from dayu_widgets.qt import *
from dayu_widgets import dayu_theme
from dayu_widgets.loading import MLoadingWrapper

os.environ['WOKWOK_ROOT'] = r'D:\dango_repo\WOKWOK'


class WFileTreeView(QWidget):
    def __init__(self, parent=None):
        super(WFileTreeView, self).__init__(parent)
        self.tree = WTreeView2(self)
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

        self.loading_wrapper = MLoadingWrapper(widget=self.tree, loading=False)
        layout.addWidget(self.loading_wrapper)
        self.tree.copy_file_thread.started.connect(functools.partial(self.loading_wrapper.set_dayu_loading, True))
        self.tree.copy_file_thread.finished.connect(functools.partial(self.loading_wrapper.set_dayu_loading, False))

    def set_root_path(self, path):
        self.tree.set_root_path(path)


class WTreeView(QTreeView):
    def __init__(self, parent=None):
        super(WTreeView, self).__init__(parent=parent)
        self.doubleClicked.connect(self.open_file)  # 双击文件打开
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.contextMenu = QMenu(self)
        self.download_action = \
            self.contextMenu.addAction(MIcon('down_line_dark.svg', dayu_theme.primary_color), u'下载全部')
        self.download_action.triggered.connect(self.download_all)
        self.open_action = \
            self.contextMenu.addAction(MIcon('circle.svg', dayu_theme.primary_color), u'打开当前路径')
        self.open_action.triggered.connect(self.open_dir)
        # necessary params
        self.root_path = ''
        self.copy_file_thread = utils.CopyFile(compare_modify=True)
        self.copy_file_thread.finished.connect(self.download_finished)
        self.no_data_model = self.model()
        self.file_model = QFileSystemModel()

    def draw_empty_content(self, view, text=None, pix_map=None):
        from dayu_widgets import dayu_theme
        pix_map = pix_map or MPixmap('empty.svg')
        text = text or view.tr('No Data')
        painter = QPainter(view)
        font_metrics = painter.fontMetrics()
        painter.setPen(QPen(dayu_theme.secondary_text_color))
        content_height = pix_map.height() + font_metrics.height()
        padding = 10
        proper_min_size = min(view.height() - padding * 2, view.width() - padding * 2, content_height)
        if proper_min_size < content_height:
            pix_map = pix_map.scaledToHeight(proper_min_size - font_metrics.height(),
                                             Qt.SmoothTransformation)
            content_height = proper_min_size
        painter.drawText(view.width() - font_metrics.width(text),
                         view.height() / 2 + content_height / 2,  # + font_metrics.height() / 2,
                         text)
        painter.drawPixmap(view.width() - pix_map.width(),
                           view.height() / 2 - content_height / 2, pix_map)
        painter.end()

    def paintEvent(self, event):
        """Override paintEvent when there is no data to show, draw the preset picture and text."""
        if not self.root_path:
            self.draw_empty_content(self.viewport(), u'舰长，这里好像没文件。',
                               MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/no-files.png'))
        else:
            self.draw_empty_content(self.viewport(), u'操作提示：双击-打开，右键-下载~',
                                    MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/tree-xier.png'))
        return super(WTreeView, self).paintEvent(event)

    def show_menu(self, args):
        if self.root_path:
            self.contextMenu.popup(QCursor.pos())
            self.contextMenu.show()

    def download_all(self):
        if self.root_path:
            wok_server = os.environ.get('WOK_SERVER')
            wok_local = os.environ.get('WOK_LOCAL').decode('unicode_escape')
            if wok_server and wok_local:
                dest = self.root_path.replace(wok_server, wok_local)
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                self.copy_file_thread.copy_list = [[self.root_path, dest]]
                self.copy_file_thread.start()
                return
            raise RuntimeError('Related ENV Not Found!')

    def open_dir(self):
        if self.root_path:
            os.startfile(r'%s' % self.root_path.encode('GB2312').replace('/', '\\'))

    def download_finished(self):
        wok_server = os.environ.get('WOK_SERVER')
        wok_local = os.environ.get('WOK_LOCAL').decode('unicode_escape')
        os.startfile(r'%s' % self.root_path.replace(wok_server, wok_local))

    def set_root_path(self, path):
        # path = u'//WDH-SERVER/data/anime/MEI/donghao.wang/试试中文/v005/works'
        new_path = path
        if not new_path or not os.path.isdir(new_path):
            print u'没有发现文件'
            self.root_path = None
            self.setModel(self.no_data_model)
            return
        self.file_model.setRootPath(new_path)
        self.setModel(self.file_model)
        self.setRootIndex(self.file_model.index(new_path))
        self.root_path = new_path

    def open_file(self, Qmodelidx):
        path = self.model().filePath(Qmodelidx).encode('GB2312').replace('/', '\\')
        os.startfile(r'%s' % path)


class StandardItem(QStandardItem):
    def __init__(self, parent, text):
        super(StandardItem, self).__init__(parent=parent)
        self.setEditable(False)
        if text:
            self.setText(text)

    def set_text(self, text):
        self.setText(text)

    def set_icon(self, icon):
        icon_full_path = os.environ['WOKWOK_ROOT'] + '/resources/icons/file_thumb/%s.svg' % icon
        if os.path.isfile(icon_full_path):
            self.setIcon(QIcon(icon_full_path))
        else:
            self.setIcon(QIcon(os.environ['WOKWOK_ROOT'] + u'/resources/icons/file_thumb/unknown.svg'))


class WTreeView2(QTreeView):
    def __init__(self, parent=None):
        super(WTreeView2, self).__init__(parent=parent)
        self._init_ui()

    def _init_ui(self):
        # self.setHeaderHidden(True)
        self.tree_model = QStandardItemModel(0, 3)
        self.tree_model.setHeaderData(0, Qt.Horizontal, u'文件名')
        self.tree_model.setHeaderData(1, Qt.Horizontal, u'文件类型')
        self.tree_model.setHeaderData(2, Qt.Horizontal, u'大小')
        self.root_node = self.tree_model.invisibleRootItem()
        self.setModel(self.tree_model)
        # self.setStyleSheet("border:none;background:none;")
        self.files_data = {}
        # self.setMinimumWidth(500)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.contextMenu = QMenu(self)
        self.download_action = \
            self.contextMenu.addAction(MIcon('down_line_dark.svg', dayu_theme.primary_color), u'下载全部')
        self.download_action.triggered.connect(self.download_all)
        self.open_action = \
            self.contextMenu.addAction(MIcon('circle.svg', dayu_theme.primary_color), u'打开当前路径')
        self.open_action.triggered.connect(self.open_dir)
        # necessary params
        self.root_path = ''
        self.copy_file_thread = utils.CopyFile(compare_modify=True)
        self.copy_file_thread.finished.connect(self.download_finished)

        self.doubleClicked.connect(self.open_file)  # 双击文件打开

    def draw_empty_content(self, view, text=None, pix_map=None):
        from dayu_widgets import dayu_theme
        pix_map = pix_map or MPixmap('empty.svg')
        text = text or view.tr('No Data')
        painter = QPainter(view)
        font_metrics = painter.fontMetrics()
        painter.setPen(QPen(dayu_theme.secondary_text_color))
        content_height = pix_map.height() + font_metrics.height()
        padding = 10
        proper_min_size = min(view.height() - padding * 2, view.width() - padding * 2, content_height)
        if proper_min_size < content_height:
            pix_map = pix_map.scaledToHeight(proper_min_size - font_metrics.height(),
                                             Qt.SmoothTransformation)
            content_height = proper_min_size
        painter.drawText(view.width() - font_metrics.width(text),
                         view.height() / 2 + content_height / 2,  # + font_metrics.height() / 2,
                         text)
        painter.drawPixmap(view.width() - pix_map.width(),
                           view.height() / 2 - content_height / 2, pix_map)
        painter.end()

    def paintEvent(self, event):
        """Override paintEvent when there is no data to show, draw the preset picture and text."""
        if not self.root_path:
            self.draw_empty_content(self.viewport(), u'舰长，这里好像没文件。',
                                    MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/no-files.png'))
        else:
            self.draw_empty_content(self.viewport(), u'操作提示：双击-打开，右键-下载~',
                                    MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/tree-xier.png'))
        return super(WTreeView2, self).paintEvent(event)

    def show_menu(self, args):
        if self.root_path:
            self.contextMenu.popup(QCursor.pos())
            self.contextMenu.show()

    def download_all(self):
        if self.root_path:
            wok_server = os.environ.get('WOK_SERVER')
            wok_local = os.environ.get('WOK_LOCAL').decode('unicode_escape')
            if wok_server and wok_local:
                dest = self.root_path.replace(wok_server, wok_local)
                if not os.path.isdir(dest):
                    os.makedirs(dest)
                self.copy_file_thread.copy_list = [[self.root_path, dest]]
                self.copy_file_thread.start()
                return
            raise RuntimeError('Related ENV Not Found!')

    def open_dir(self):
        if self.root_path:
            os.startfile(r'%s' % self.root_path.encode('GB2312').replace('/', '\\'))

    def download_finished(self):
        wok_server = os.environ.get('WOK_SERVER')
        wok_local = os.environ.get('WOK_LOCAL').decode('unicode_escape')
        os.startfile(r'%s' % self.root_path.replace(wok_server, wok_local))

    def get_file_size(self, size, Standard=1024):
        division = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB', 'NB', 'DB', 'CB', 'XB']
        if size == None:
            raise TypeError("Required argument 'size' (pos 1) not found")
        else:
            try:
                size = float(size)
            except:
                raise TypeError("Object of size must be number, not '%s'" % (type(size)))
            else:
                if (Standard != 1024) and (Standard != 1000):
                    raise Exception("Convert Standard must be '1000' or '1024', not '%s'" % (Standard))
                else:
                    if size < 1024:
                        return (str(size) + ' ' + division[0])
                    for cube in range(1, 15):
                        if size <= Standard ** cube and size >= Standard ** (cube - 1):
                            if size == Standard ** cube:
                                return (str('%.2f' % (size / Standard ** cube)) + " " + division[cube])
                            else:
                                return (str('%.2f' % (size / Standard ** (cube - 1))) + " " + division[cube - 1])
                        else:
                            continue
                    raise Exception("Out of the maximum conversion range (%s^14 bytes)" % (Standard))

    def set_root_path(self, path):
        _path = path.replace('\\', '/')
        self.root_path = _path
        if not _path or not os.path.isdir(_path):
            print u'没有发现文件'
            self.root_node.setRowCount(0)
            self.root_path = None
            return
        if self.root_node.hasChildren():
            self.root_node.setRowCount(0)
        self.files_data = {_path: {'item': self.root_node, 'text': _path, 'size': 0}}

        for root, folders, files in os.walk(path, topdown=False):
            for f in files:
                if 'Thumbs.db' in f:
                    continue
                file_full_path = os.path.join(root, f).replace('\\', '/')
                split_path = file_full_path.replace(_path, '').split('/')
                s_left_path = []
                for s in split_path:
                    if s:
                        s_left_path.append(s)
                        s_full_path = _path + '/' + '/'.join(s_left_path)
                        s_full_path_p = '/'.join(s_full_path.split('/')[:-1])
                        if s_full_path in self.files_data.keys():
                            continue
                        elif s_full_path_p in self.files_data.keys():
                            item_data = self.files_data.get(s_full_path_p)
                            parent_item = item_data.get('item')
                            this_item = StandardItem(parent_item, text=s)
                            parent_item.appendRow(this_item)
                            this_item.path_info = s_full_path
                            this_item.size_info = 0
                            this_file_type = ' '
                            if os.path.isfile(s_full_path):
                                this_item.size_info = os.path.getsize(s_full_path)
                                this_file_type = s_full_path.split('.')[-1]
                                this_item.set_icon(this_file_type)
                            else:
                                this_item.set_icon('folder')
                            parent_item.setChild(this_item.row(), 1, StandardItem(parent_item, text=this_file_type))
                            parent_item.setChild(this_item.row(), 2, StandardItem(parent_item, text=str(self.get_file_size(this_item.size_info))))
                            self.files_data.update({s_full_path: {'item': this_item, 'size': this_item.size_info, 'text': s}})
                        else:
                            print 'error inserting item: ' + s
        self.expandAll()
        self.header().setResizeMode(0, QHeaderView.Stretch)

    def open_file(self, Qmodelidx):
        pass
        item = self.tree_model.itemFromIndex(Qmodelidx)
        if hasattr(item, 'path_info'):
            path =item.path_info.encode('GB2312').replace('/', '\\')
            os.startfile(r'%s' % path)
        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = WTreeView2()
    from dayu_widgets.theme import MTheme
    MTheme('light').apply(test)
    # test.set_root_path(u'//WDH-SERVER/data/anime/MEI/donghao.wang')
    test.set_root_path(u'Z:\\Animation\\11_Fuka2\\【G ok】')
    test.show()
    sys.exit(app.exec_())


