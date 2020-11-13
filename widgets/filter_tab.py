#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.10
###################################################################
import os

from dayu_widgets.qt import *
from dayu_widgets.collapse import MCollapse
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.label import MLabel
from dayu_widgets.menu import MMenu
from dayu_widgets.theme import MTheme
from dayu_widgets.push_button import MPushButton


class FilterWidget(QWidget):
    start_filter_sig = Signal(str)

    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent=parent)

        title_label = MLabel(u'                页面设置').warning().h4().strong()

        self.show_thumb_cb = MCheckBox(u'显示缩略图')
        self.show_thumb_cb.setChecked(True)
        filter_widget = QWidget(self)
        layout_1 = QVBoxLayout()
        form_lay = QFormLayout()
        layout_1.addLayout(form_lay)
        form_lay.setLabelAlignment(Qt.AlignRight)
        filter_widget.setLayout(layout_1)
        self.any_le = MLineEdit(self)
        self.any_le.setPlaceholderText(u'输入任意字符...')
        self.wok_name_le = MLineEdit(self)
        self.wok_name_le.setPlaceholderText(u'输入锅名...')
        self.panda_name_le = MLineEdit(self)
        self.panda_name_le.setPlaceholderText(u'输入制作人的名字...')
        self.link_le = MLineEdit(self)
        self.link_le.setPlaceholderText(u'输入资产/镜头...')
        theme = MTheme('light')
        menu = MMenu()
        theme.apply(menu)
        menu.set_data(['']+eval(os.environ.get('STATUS_DICT')).values())
        self.status_cb = MComboBox()
        self.status_cb.set_menu(menu)
        form_lay.addRow(u'锅名:', self.wok_name_le)
        form_lay.addRow(u'谁的锅:', self.panda_name_le)
        form_lay.addRow(u'角色/镜头:', self.link_le)
        form_lay.addRow(u'状态:', self.status_cb)
        form_lay.addRow(u'任意字符:', self.any_le)
        self.status_cb.setCurrentIndex(1)

        self.any_le.editingFinished.connect(self.start_filter)
        self.wok_name_le.editingFinished.connect(self.start_filter)
        self.panda_name_le.editingFinished.connect(self.start_filter)
        self.link_le.editingFinished.connect(self.start_filter)
        self.status_cb.textChanged.connect(self.start_filter)
        section_list = [
            {
                'title': u'栏设置',
                'expand': True,
                'widget': self.show_thumb_cb
            }, {
                'title': u'过滤设置',
                'expand': True,
                'widget': filter_widget
            }
        ]
        section_group = MCollapse()
        section_group.add_section_list(section_list)

        main_lay = QVBoxLayout()
        main_lay.addWidget(MLabel('----------------------------------------'))
        main_lay.addWidget(title_label)
        main_lay.addWidget(section_group)
        main_lay.addStretch()
        clear_pb_layout = QHBoxLayout()
        self.clear_filter_pb = MPushButton(u'清空筛选条件').small().success()
        self.clear_filter_pb.clicked.connect(self.clear_filter)
        clear_pb_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        clear_pb_layout.addWidget(self.clear_filter_pb)
        clear_pb_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_1.addWidget(QLabel(' '))
        layout_1.addLayout(clear_pb_layout)
        # main_lay.addWidget(self.clear_filter_pb)
        # main_lay.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main_lay)

    def start_filter(self):
        format_text = '|'.join([a for a in [self.any_le.text(), self.wok_name_le.text(), self.panda_name_le.text(), self.link_le.text(), self.status_cb.currentText()] if a != ''])
        self.start_filter_sig.emit(format_text)

    @property
    def pattern(self):
        return '|'.join([a for a in [self.any_le.text(), self.wok_name_le.text(), self.panda_name_le.text(), self.link_le.text(), self.status_cb.currentText()] if a != ''])

    def clear_filter(self):
        self.any_le.setText('')
        self.wok_name_le.setText('')
        self.panda_name_le.setText('')
        self.link_le.setText('')
        self.status_cb.lineEdit().setText('')


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication
    from dayu_widgets import dayu_theme
    app = QApplication(sys.argv)
    test = FilterWidget()
    dayu_theme.apply(test)
    test.show()
    sys.exit(app.exec_())