#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.7
###################################################################

import os
import shutil

from dayu_widgets.qt import *
from dayu_widgets.label import MLabel
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.push_button import MPushButton


class WFieldMixin(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(WFieldMixin, self).__init__(parent)
        self._init_ui()
        self.is_set = False

    def _init_ui(self):
        self.main_layout = QGridLayout()
        # self.main_layout.addWidget(MLabel(u'制作者：').code(), 0, 0)
        self.artist_label = MLabel()
        # self.main_layout.addWidget(self.artist_label, 0, 1)
        # self.main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)

        # self.main_layout.addWidget(MLabel(u'提交日期：').code(), 1, 0)
        self.updated_time = MLabel('')
        # self.main_layout.addWidget(self.updated_time, 1, 1)
        # self.main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 2)

        # self.main_layout.addWidget(MLabel(u'当前版本：').code(), 2, 0)
        self.current_version = MLabel()
        # self.main_layout.addWidget(self.current_version, 2, 1)
        # self.main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 2)

        self.main_layout.addWidget(MLabel(u'提交描述：').code(), 3, 0)
        self.version_description = MTextEdit()
        self.version_description.setMinimumWidth(600)
        self.version_description.setReadOnly(True)
        self.version_description.setStyleSheet("border:none;background:none;")
        self.main_layout.addWidget(self.version_description, 3, 1)
        self.view_description_detail = MPushButton(u'查看详情').small()
        self.view_description_detail.hide()
        self.view_description_detail.setMaximumWidth(100)
        self.main_layout.addWidget(self.view_description_detail, 3, 2)
        self.main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 3, 2)

        self.main_layout.addWidget(MLabel(u'反馈内容：').code(), 4, 0)
        self.feedback = MTextEdit()
        self.feedback.setReadOnly(True)
        self.feedback.setStyleSheet("border:none;background:none;")
        self.main_layout.addWidget(self.feedback, 4, 1)
        self.view_feedback_detail = MPushButton(u'查看详情').small()
        self.view_feedback_detail.hide()
        self.view_feedback_detail.setMaximumWidth(100)
        self.main_layout.addWidget(self.view_feedback_detail, 4, 2)
        self.main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 4, 3)

        self.setLayout(self.main_layout)
        self.view_description_detail.clicked.connect(self.view_dc_detail)
        self.view_feedback_detail.clicked.connect(self.view_fb_detail)

        self.feedback_rich_text = ''
        self.submit_description = ''

    def view_dc_detail(self):
        win = QMainWindow(self)
        dialog = QWidget()
        win.setCentralWidget(dialog)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        te = MTextEdit(self)
        te.setReadOnly(True)
        win.setMinimumSize(1300, 800)
        win.setWindowTitle(u'提交者描述')
        try:
            imgs = self.submit_description.split('src=')[1:]
            imgs_server = [i.split('>')[0] for i in imgs]
            wok_temp_local = os.environ.get('WOK_TEMP_DIR')
            for each in imgs_server:
                file_name = each.split('/')[-1].split('\\')[-1]
                shutil.copyfile(each, wok_temp_local + file_name)
                self.submit_description = self.submit_description.replace(each, wok_temp_local + file_name)
        except:
            pass
        te.setText(self.submit_description)
        layout.addWidget(te)
        win.show()

    def view_fb_detail(self):
        win = QMainWindow(self)
        dialog = QWidget()
        win.setCentralWidget(dialog)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        te = MTextEdit(self)
        te.setReadOnly(True)
        win.setMinimumSize(1300, 800)
        win.setWindowTitle(u'返修意见详情')
        try:
            imgs = self.feedback_rich_text.split('src=')[1:]
            imgs_server = [i.split('>')[0] for i in imgs]
            wok_temp_local = os.environ.get('WOK_TEMP_DIR')
            for each in imgs_server:
                file_name = each.split('/')[-1].split('\\')[-1]
                shutil.copyfile(each, wok_temp_local + file_name)
                self.feedback_rich_text = self.feedback_rich_text.replace(each, wok_temp_local + file_name)
        except:
            pass
        te.setText(self.feedback_rich_text)
        layout.addWidget(te)
        win.show()

    def set_details(self, artist, date, version_code, version_description, feedback):
        self.artist_label.setText(artist)
        self.updated_time.setText(date)
        self.current_version.setText(version_code)
        self.version_description.setText(version_description)
        self.feedback.setText(feedback)
        self.is_set = True
        self.view_feedback_detail.show()
        self.view_description_detail.show()
        self.submit_description = version_description
        self.feedback_rich_text = feedback

    def paintEvent(self, event):
        # if self.is_set:
        #     return super(WFieldMixin, self).paintEvent(event)
        from dayu_widgets import dayu_theme
        pix_map = MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/version-detail-kiana.png')
        text = u' '
        painter = QPainter(self)
        font_metrics = painter.fontMetrics()
        painter.setPen(QPen(dayu_theme.secondary_text_color))
        content_height = pix_map.height() + font_metrics.height()
        padding = 10
        proper_min_size = min(self.height() - padding * 2, self.width() - padding * 2, content_height)
        if proper_min_size < content_height:
            pix_map = pix_map.scaledToHeight(proper_min_size - font_metrics.height(),
                                             Qt.SmoothTransformation)
            content_height = proper_min_size
        painter.drawText(self.width() / 2 - font_metrics.width(text) / 2,
                         self.height() / 2 + content_height / 2 - font_metrics.height() / 2,
                         text)
        painter.drawPixmap(self.width() - pix_map.width(),
                           self.height() / 2 - content_height / 2, pix_map)
        painter.end()
        return super(WFieldMixin, self).paintEvent(event)


