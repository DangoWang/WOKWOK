#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.7
###################################################################

import os
from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.label import MLabel
from dayu_widgets.qt import *
from dayu_widgets.qt import QDialog, QFormLayout, Qt, QHBoxLayout, QVBoxLayout
from dayu_widgets.check_box import MCheckBox
from ...screen_grabber import thumbnail
from dayu_widgets import dayu_theme


class DropArea(QLabel):

    def __init__(self, parent=None):
        super(DropArea, self).__init__(parent)
        self.setPixmap(QPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/dropfiles-holder.png'))
        # self.setPixmap(QPixmap('D:/dango_repo/WOKWOK/resources/icons/dropfiles-holder.png'))
        self.setScaledContents(True)


class SubmitDialog(QDialog, MFieldMixin):

    def __init__(self, parent=None):
        super(SubmitDialog, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(u'提交文件')
        self.form_lay = QFormLayout()
        self.form_lay.setLabelAlignment(Qt.AlignRight)

        self.wok_name_label = MLabel().danger().h4()
        self.form_lay.addRow(u'锅名：', self.wok_name_label)

        self.drop_area = DropArea(self)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.drop_area)

        self.description_te = MTextEdit()


        button_lay = QHBoxLayout()
        button_lay.addStretch()
        self.create_pb = MPushButton(text=u'提交').primary()
        button_lay.addWidget(self.create_pb)
        self.cancel_pb = MPushButton(text=u'取消')
        button_lay.addWidget(self.cancel_pb)
        main_lay = QVBoxLayout()
        main_lay.addLayout(self.form_lay)
        main_lay.addWidget(MDivider(u'拖入文件/文件夹（支持多个）'))
        main_lay.addWidget(self.scroll)

        self.use_thumb = MCheckBox(u'附加缩略图（非必须）')
        self.form_lay.addWidget(self.use_thumb)

        self.thumbnail = thumbnail.Thumbnail()
        self.thumbnail.hide()
        dayu_theme.apply(self.thumbnail)
        self.thumbnail.setMaximumSize(250, 200)
        self.form_lay.addRow(u'', self.thumbnail)

        self.use_thumb.stateChanged.connect(self.toggle_thumbnail)
        # self.use_thumb.stateChanged.connect(self.thumbnail.show)


        main_lay.addWidget(MDivider(u'在下面输入描述吧！'))
        main_lay.addWidget(self.description_te)
        # main_lay.addWidget(MCheckBox('I accept the terms and conditions'))
        main_lay.addStretch()
        main_lay.addWidget(MDivider())
        main_lay.addLayout(button_lay)
        self.setLayout(main_lay)

        self.setAcceptDrops(True)
        self.all_files = []
        
    def toggle_thumbnail(self):
        # pass
        if self.use_thumb.isChecked():
            self.thumbnail.show()
        else:
            self.thumbnail.hide()

    def dragEnterEvent(self, event):
        """获取拖拽过来的文件夹+文件"""
        if event.mimeData().hasFormat("text/uri-list"):
            self.all_files = [url.toLocalFile().replace('\\', '/') for url in event.mimeData().urls()]
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.drop_area.setText('\n'.join(self.all_files))
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    from dayu_widgets.theme import MTheme
    win = SubmitDialog()
    MTheme('light').apply(win)
    win.show()
    sys.exit(app.exec_())
