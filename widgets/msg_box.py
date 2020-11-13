#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.8
# Email : dd.parkhere@gmail.com
###################################################################
#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2019.8
import os
from dayu_widgets.qt import *
from dayu_widgets import label
from dayu_widgets import line_edit
from dayu_widgets.radio_button import MRadioButton
from dayu_widgets import text_edit
import page
from functools import partial
from mq import thread


class UnreadMessageUIClass(QMainWindow):
    def __init__(self, parent=None):
        super(UnreadMessageUIClass, self).__init__(parent)
        self.resize(1300, 500)
        # self.find_thread = utils.MFetchDataThread()
        self.this_name = os.environ.get('SG_PANDA')
        self.setWindowTitle(u'消息列表')
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.gridLayout_main = QGridLayout(self.central_widget)
        # left
        self.frame_left = QFrame(self.central_widget)
        self.gridLayout_main.addWidget(self.frame_left, 0, 0, 1, 1)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_left.sizePolicy().hasHeightForWidth())
        self.frame_left.setSizePolicy(sizePolicy)
        self.frame_left.setFrameShape(QFrame.StyledPanel)
        self.frame_left.setFrameShadow(QFrame.Raised)
        self.gridLayout_left = QGridLayout(self.frame_left)

        # self.pushButton_add = MToolButton().svg('add_line.svg').icon_only()
        # self.gridLayout_left.addWidget(self.pushButton_add, 0, 0, 1, 1)

        # 搜索框
        self.line_edit_find = line_edit.MLineEdit(self.frame_left).search().small()
        self.line_edit_find.setPlaceholderText(u'输入任意字符搜索...')
        self.gridLayout_left.addWidget(self.line_edit_find, 0, 1, 1, 1)
        # 弹簧
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_left.addItem(spacerItem, 0, 2, 1, 1)
        # 类型选择
        self.unread_bt = MRadioButton(u"未读")
        self.read_bt = MRadioButton(u"已读")
        self.all_bt = MRadioButton(u"全部")
        self.gridLayout_left.addWidget(self.unread_bt, 0, 3, 1, 1)
        self.gridLayout_left.addWidget(self.read_bt, 0, 4, 1, 1)
        self.gridLayout_left.addWidget(self.all_bt, 0, 5, 1, 1)
        self.unread_bt.setChecked(1)
        self.unread_bt.clicked.connect(partial(self.find_note, 0))
        self.read_bt.clicked.connect(partial(self.find_note, 1))
        self.all_bt.clicked.connect(partial(self.find_note, 2))
        # note 列表eee
        self.listview = page.SheetContent()
        self.listview.table.set_no_data_text(u'这里没消息啦！')
        self.listview.table.set_no_data_image(MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/messages.png'))
        self.listview.show_msg = False
        self.listview.msg_parent = self.listview
        self.listview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listview.setMinimumHeight(300)
        self.listview.setMinimumWidth(666)
        self.gridLayout_left.addWidget(self.listview, 2, 0, 1, 5)
        self.listview.table.clicked.connect(self.show_select_info)
        self.line_edit_find.textChanged.connect(self.listview.model_sort.set_search_pattern)

        # right
        self.frame_right = QFrame(self.central_widget)
        self.gridLayout_main.addWidget(self.frame_right, 0, 1, 1, 1)
        self.frame_right.setFrameShape(QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QFrame.Raised)
        self.gridLayout_right = QGridLayout(self.frame_right)
        label_03 = label.MLabel(parent=self.frame_right)
        label_03.setText(u"描述：")
        label_03.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.gridLayout_right.addWidget(label_03, 2, 0, 1, 1)
        self.description = text_edit.MTextEdit(self.frame_right)
        self.description.setReadOnly(True)
        self.gridLayout_right.addWidget(self.description, 2, 1, 1, 1)

        self.clean_info()
        self.find_note(0)

    def show_select_info(self):
        self.clean_info()
        selected_content = self.listview.get_selected_content()
        if not selected_content:
            return
        note = selected_content[0]["content"]
        thread.read(note)
        self.description.setText(note)

    def clean_info(self):
        self.description.setText("")

    def find_note(self, num):
        filters = [["reciever", "is", os.environ.get("SG_PANDA")]]
        if num == 0:
            filters = [["reciever", "is", os.environ.get("SG_PANDA")],
                       ["is_read", "is", 'false']]
        elif num == 1:
            filters = [["reciever", "is", os.environ.get("SG_PANDA")],
                       ["is_read", "is", 'true']]

        self.listview.set_config({"page_actions": [],
                                  "page_fields": [
                                      {u"label": u"发送自", u"key": "sender_nick_name", 'searchable': 1},
                                      {u"label": u"主题", u"key": "content", 'searchable': 1},
                                                  {u"label": u"创建时间", u"key": "time_created", 'searchable': 1}],
                                  # "page_filters": [["sg_if_read", "is", True]],
                                  "page_filters": filters,
                                  "page_name": u"消息",
                                  "page_type": "anime_message",
                                  "page_order": [{'field_name': 'time_created', 'direction': 'desc'}]
                                 })
        self.listview.parse_config()

    def closeEvent(self, event):
        self.parent().badge.set_dayu_count(len(thread.get_msgs(is_read='false', receiver=os.environ.get('SG_PANDA'))))
        event.accept()


def main(parent=None):
    win = UnreadMessageUIClass(parent)
    return win


if __name__ == '__main__':
    import sys
    from config import envs
    app = QApplication(sys.argv)
    wok_app = main()
    wok_app.show()
    sys.exit(app.exec_())




