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
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.qt import *
from dayu_widgets import dayu_theme
from dayu_widgets.menu import MMenu
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.qt import QDialog, QFormLayout, Qt, QHBoxLayout, QVBoxLayout
from dayu_widgets.loading import MLoadingWrapper
from dayu_widgets.button_group import MCheckBoxGroup

from ..screen_grabber import thumbnail
from ..comboBox_completer import combo_box


class CreateWokWin(QDialog, MFieldMixin):
    def __init__(self, parent=None):
        super(CreateWokWin, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowTitle(u'创建一个锅')
        form_lay = QFormLayout()
        form_lay.setLabelAlignment(Qt.AlignRight)

        self.wok_name_le = MLineEdit().small()
        form_lay.addRow(u'锅名:', self.wok_name_le)

        self.entity_cb = combo_box.WSelectTaskComboBox()
        self.loading_wrapper = MLoadingWrapper(widget=self.entity_cb, loading=False)
        form_lay.addRow(u'镜头/角色:', self.loading_wrapper)

        # self.pandas_cb = combo_box.WSelectTaskComboBox()
        # self.pandas_menu = MMenu(exclusive=False)
        self.pandas_lb = MToolButton().text_only()
        self.pandas_lb.setStyleSheet('background-color: rgba(200, 188, 161, 50);')
        self.menu_win = WMenu(self)
        # self.pandas_cb.set_menu(self.pandas_menu)
        # self.loading_wrapper_2 = MLoadingWrapper(widget=self.pandas_cb, loading=False)
        # form_lay.addWidget(self.loading_wrapper)
        # entity_widget = QWidget()
        # self.entity_layout = QVBoxLayout()
        # entity_widget.setLayout(self.entity_layout)
        # self.entity_layout.addWidget(self.entity_cb)
        form_lay.addRow(u'分配给:', self.pandas_lb)

        self.thumbnail = thumbnail.Thumbnail()
        dayu_theme.apply(self.thumbnail)
        self.thumbnail.setMaximumSize(250, 200)
        form_lay.addRow(u'缩略图:', self.thumbnail)

        self.description_te = MTextEdit()
        form_lay.addRow(u'说明:', self.description_te)

        button_lay = QHBoxLayout()
        button_lay.addStretch()
        self.create_pb = MPushButton(text=u'执行').primary()
        button_lay.addWidget(self.create_pb)
        self.cancel_pb = MPushButton(text=u'取消')
        button_lay.addWidget(self.cancel_pb)

        delete_layout = QHBoxLayout()
        self.delete_pb = MPushButton(text=u'请稍等').small().danger()
        self.delete_pb.setEnabled(False)
        delete_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        delete_layout.addWidget(self.delete_pb)
        self.delete_pb.hide()

        main_lay = QVBoxLayout()
        main_lay.addLayout(form_lay)
        main_lay.addLayout(delete_layout)
        # main_lay.addWidget(MCheckBox('I accept the terms and conditions'))
        main_lay.addStretch()
        main_lay.addWidget(MDivider())
        main_lay.addLayout(button_lay)
        self.setLayout(main_lay)


class WMenu(QDialog):

    def __init__(self, parent=None):
        super(WMenu, self).__init__(parent=parent)
        self.setWindowTitle(u'选择小熊猫')
        self.radio_group_b = MCheckBoxGroup()
        layout = QHBoxLayout()
        layout.addWidget(self.radio_group_b)
        self.setLayout(layout)

    def set_data_list(self, datas):
        for each_panda in datas:
            self.add_panda(each_panda)

    def add_panda(self, panda):
        icon = MIcon(os.environ['WOKWOK_ROOT'] + '/resources/icons/users/%s.png' % panda)
        self.radio_group_b.add_button({'text': panda, 'icon': icon})

    def set_checked(self, panda):
        for each in self.radio_group_b.get_button_group().buttons():
            if each.text() in panda:
                each.setChecked(True)


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication

    app = QApplication(sys.argv)
    test = CreateWokWin()
    from dayu_widgets import dayu_theme

    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())
