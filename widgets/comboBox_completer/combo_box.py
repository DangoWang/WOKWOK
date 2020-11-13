#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.7
###################################################################
import os

from dayu_widgets.mixin import property_mixin, cursor_mixin, focus_shadow_mixin
from dayu_widgets.qt import *


class WSelectTaskComboBox(QWidget):
    def __init__(self, parent=None):
        super(WSelectTaskComboBox, self).__init__(parent)
        layout = QHBoxLayout(self)
        self.combobox = QComboBox(self)
        self.combobox.setEditable(True)
        line_edit = self.combobox.lineEdit()
        line_edit.setTextMargins(4, 0, 4, 0)
        line_edit.setStyleSheet('background-color:transparent')
        # line_edit.setCursor(Qt.PointingHandCursor)
        line_edit.setPlaceholderText(self.tr(u'输入或选择...'))
        self.combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addWidget(self.combobox)
        # 初始化combobox
        # self.init_combobox(data_list)
        # 增加选中事件
        # self.combobox.activated.connect(self.on_combobox_Activate)
        # 样式
        self.combobox.setStyleSheet('''QComboBox {
                                        border: 1px solid #bebebe;
                                        padding: 1px 18px 1px 3px;
                                        font: normal normal 16px "Microsoft YaHei";
                                        color: #555555;
                                        background: transparent;
                                    }
                                    
                                    
                                    QComboBox:editable{
                                        background: transparent;
                                    }
                                    
                                    QComboBox:!editable, QComboBox::drop-down:editable{
                                        background: transparent;
                                    }
                                    
                                    QComboBox:!editable:on, QComboBox::drop-down:editable:on{
                                        background: transparent;
                                    }
                                    
                                    QComboBox:!on{
                                    }
                                    
                                    QComboBox:on{ /* the popup opens */
                                        color: #555555;
                                        border-color: #327cc0;
                                        background: transparent;
                                    }
                                    
                                    QComboBox::drop-down{
                                        subcontrol-origin: padding;
                                        subcontrol-position: top right;
                                        width: 20px;
                                        border-left-width: 1px;
                                        border-left-color: darkgray;
                                    }
                                    
                                    QComboBox::down-arrow {
                                        image: url(%s/resources/icons/down.svg);
                                    }
                                    
                                    QComboBox::down-arrow:on {
                                        image: url(%s/resources/icons/down.svg);
                                    }
                                    
                                    QComboBox QAbstractItemView {
                                        outline: 0; 
                                        border: 1px solid #327cc0;
                                        background-color: #F1F3F3;
                                        font: normal normal 14px "Microsoft YaHei";
                                    }
                                    
                                    QComboBox QAbstractItemView::item {
                                        height: 32px;
                                        color: #555555;
                                        background-color: transparent;
                                    }
                                    
                                    QComboBox QAbstractItemView::item:hover {
                                        color: #FFFFFF;
                                        background-color: #327cc0;
                                    }
                                    
                                    QComboBox QAbstractItemView::item:selected {
                                        color: #FFFFFF;
                                        background-color: #327cc0;
                                    }
                                    
                                    QComboBox QAbstractScrollArea QScrollBar:vertical {
                                        background-color: #d0d2d4;
                                    }
                                    
                                    QComboBox QAbstractScrollArea QScrollBar::handle:vertical {
                                        background: rgb(160,160,160);
                                    }
                                    
                                    QComboBox QAbstractScrollArea QScrollBar::handle:vertical:hover {
                                        background: rgb(90, 91, 93);
                                    }'''%(os.environ.get('WOKWOK_ROOT'), os.environ.get('WOKWOK_ROOT')))
        self.data_list = []
        self.combobox.lineEdit().editingFinished.connect(self.on_combobox_Activate)

    def init_combobox(self, data_list):
        # 增加选项元素
        self.data_list = data_list
        for i in range(len(data_list)):
            self.combobox.addItem(data_list[i])
        self.combobox.setCurrentIndex(-1)
        # 增加自动补全
        # self.completer.setFilterMode(Qt.MatchContains)
        self.completer = QCompleter(data_list)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(self.completer.UnfilteredPopupCompletion)
        self.combobox.setCompleter(self.completer)

    def on_combobox_Activate(self):
        if not self.combobox.currentText() in self.data_list:
            self.combobox.lineEdit().setText('')


if __name__ == '__main__':
    import sys
    from dayu_widgets.qt import QApplication

    app = QApplication(sys.argv)
    test = WSelectTaskComboBox(["C","C++","Java","Python","JavaScript","C#","Swift","go","Ruby","Lua","PHP"])
    from dayu_widgets.theme import MTheme
    light = MTheme('light')
    light.apply(test)
    test.show()
    sys.exit(app.exec_())

