#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.11
# wechat : 18250844478
###################################################################
import functools
import json
import os
from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.qt import *
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.message import MMessage
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.loading import MLoadingWrapper
from dayu_widgets.divider import MDivider
from dayu_widgets.push_button import MPushButton
from widgets import utils


class CommentField(QWidget):
    finish_setting_up_sig = Signal(int)

    def __init__(self, parent):
        super(CommentField, self).__init__(parent=parent)
        self.wok_detail = {'sg_thumbnail_path': os.environ['WOKWOK_ROOT'] + '/resources/icons/users/hold.thumbnail',
                           'description': u'没有描述'
                           }
        self._init_ui()
        self.msg = None
        self.card_list = []
        self.set_up_data = None

    def _init_ui(self):
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.thumb_label = QLabel()
        # self.pix = QPixmap(self.wok_detail.get('sg_thumbnail_path')).scaledToWidth(100)
        # self.thumb_label.setPixmap(self.pix)
        self.description_te = MTextEdit()
        # self.description_te.setFixedHeight(self.pix.height())
        self.description_te.setReadOnly(True)
        self.description_te.setStyleSheet("border:none;background:none;")
        self.description_te.setText(self.wok_detail.get('description'))
        top_layout.addWidget(self.thumb_label)
        top_layout.addWidget(self.description_te)
        main_layout.addLayout(top_layout)

        main_layout.addWidget(MDivider(u'评论区'))

        mid_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setMinimumWidth(150)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        mid_widget = QWidget()
        scroll.setWidget(mid_widget)
        mid_widget.setLayout(mid_layout)
        self._middle_layout = QVBoxLayout()
        mid_layout.addLayout(self._middle_layout)
        mid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.loading_wrapper = MLoadingWrapper(widget=scroll, loading=False)
        main_layout.addWidget(self.loading_wrapper)

        main_layout.addWidget(MDivider(u'增加评论↓'))

        down_layout = QVBoxLayout()
        self.add_replay_te = MTextEdit()
        self.add_replay_te.setFixedHeight(100)
        self.add_reply_pb = MPushButton(u'确定')
        down_layout.addWidget(self.add_replay_te)
        add_reply_layout = QHBoxLayout()
        add_reply_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        add_reply_layout.addWidget(self.add_reply_pb)
        down_layout.addLayout(add_reply_layout)

        main_layout.addLayout(down_layout)
        self.setLayout(main_layout)

        self.get_replies_detail_thread = utils.MFetchDataThread()
        self.get_replies_detail_thread.result_sig.connect(self.get_replies_detail)

        self.add_comment_thread = utils.MFetchDataThread()
        self.add_comment_thread.result_sig.connect(self.finish_adding_comment)

        self.add_reply_thread = utils.MFetchDataThread()
        self.add_reply_thread.result_sig.connect(self.finish_adding_reply)

        self.add_reply_pb.clicked.connect(self.add_reply)

        self.get_replies_detail_thread.started.connect(functools.partial(self.loading_wrapper.set_dayu_loading, True))
        self.get_replies_detail_thread.finished.connect(lambda: self.loading_wrapper.set_dayu_loading(False))

    def set_up(self):
        if self.get_replies_detail_thread.isRunning():
            self.get_replies_detail_thread.terminate()
        if not self.set_up_data:
            self.finish_setting_up_sig.emit(True)
            return
        wok_detail = self.set_up_data
        # print wok_detail.get('sg_thumbnail_path')
        if self.card_list:
            for each in self.card_list:
                each.deleteLater()
        self.card_list = []
        self.wok_detail = wok_detail
        pix = QPixmap(wok_detail.get('sg_thumbnail_path')).scaledToWidth(100)
        self.thumb_label.setPixmap(pix)
        self.description_te.setFixedHeight(pix.height())
        # self.pix.load(wok_detail.get('sg_thumbnail_path'))
        self.description_te.setText(wok_detail.get('description'))
        if not wok_detail.get('sg_entity'):
            self.finish_setting_up_sig.emit(True)
            return
        self.get_replies_detail_thread.mode = 'find'
        self.get_replies_detail_thread.data = ['Reply', [['entity', 'is', wok_detail.get('sg_entity')]], ['content']]
        self.get_replies_detail_thread.start()

    def get_replies_detail(self, result):
        if not result:
            self.finish_setting_up_sig.emit(True)
            return
        for reply in result:
            if reply.get('content') and '&&&&' in reply.get('content'):
                self.add_reply_card(reply.get('content'))
        self.finish_setting_up_sig.emit(1)

    def add_reply_card(self, content):
        panda, real_content = content.split('&&&&')
        thumb = os.environ['WOKWOK_ROOT'] + '/resources/icons/users/%s.thumbnail' % panda
        if not os.path.isfile(thumb):
            thumb = os.environ['WOKWOK_ROOT'] + '/resources/icons/users/hold.thumbnail'
        wid = QWidget()
        ly = QHBoxLayout()
        wid.setLayout(ly)
        pix = QPixmap(thumb).scaledToWidth(50)
        lb = QLabel()
        lb_1 = QLabel(panda)
        # lb_1.setAlignment(2)
        lb.setPixmap(pix)
        lb_wid = QWidget()
        lb_ly = QVBoxLayout()
        lb_wid.setLayout(lb_ly)
        lb_ly.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        lb_ly.addWidget(lb)
        lb_ly.addWidget(lb_1)
        lb_ly.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # lb_ly.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # ly.addLayout(lb_ly)
        ly.addWidget(lb_wid)
        te = WTextEdit()
        te.setStyleSheet("border:none;background:none;")
        # te.setFixedHeight(pix.height()*2)
        te.setReadOnly(True)
        ly.addWidget(te)
        te.setText(real_content)
        te.setMinimumHeight(100)
        # lb_wid.setMinimumHeight(100)
        # lb_wid.setMaximumHeight(200)
        self.card_list.append(wid)
        self._middle_layout.addWidget(wid)
        pass

    @property
    def content(self):
        return os.environ.get('SG_PANDA_NICK_NAME').decode('GBK') + '&&&&' + self.add_replay_te.toPlainText()

    def add_reply(self):
        self.add_reply_pb.setEnabled(False)
        if not self.wok_detail.get('sg_entity'):
            if not self.wok_detail.get('id'):
                return
            # 没有评论，需要先创建
            self.add_comment_thread.mode = 'create'
            _data = [os.environ.get('WOK_COMMENT_ENTITY'),
                                            {'sg_entities': [self.wok_detail],
                                             'code': self.wok_detail.get('description'),
                                             'project': self.wok_detail.get('project')
                                             }
                                            ]
            _data = json.loads(json.dumps(_data, ensure_ascii=False), encoding='utf-8')
            # _data = json.dumps(_data, ensure_ascii=False, encoding='utf-8')
            self.add_comment_thread.data = _data
            self.add_comment_thread.start()
            MMessage.config(999)
            self.msg = MMessage.loading(u'正在创建评论...', self.parent())
        else:
            self.add_reply_doit({'id': self.wok_detail.get('sg_entity').get('id'), 'content': self.content})
        pass

    def add_reply_doit(self, _data):
        # _data: {'id': 123, 'content': 'aaa'}
        self.msg = MMessage.loading(u'正在创建回复...', self.parent())
        self.add_reply_thread.mode = 'create'
        temp = ['Reply',
                      {'entity': {'type': os.environ.get('WOK_COMMENT_ENTITY'), 'id': _data.get('id')},
                       'content': _data.get('content')
                       }
                      ]
        _data2 = json.loads(json.dumps(temp, ensure_ascii=False), encoding='utf-8')
        # _data = json.dumps(_data, ensure_ascii=False, encoding='utf-8')
        self.add_reply_thread.data = _data2
        self.add_reply_thread.start()

    def finish_adding_comment(self, result):
        if not isinstance(result, dict):
            return
        id = result.get('id')
        self.add_reply_doit({'id': id, 'content': self.content})
        MMessage.config(999)
        if self.msg:
            self.msg.close()

    def finish_adding_reply(self, result):
        self.add_reply_pb.setEnabled(True)
        if not isinstance(result, dict):
            return
        self.add_reply_card(self.content)
        if self.msg:
            self.msg.close()
        pass


class WTextEdit(MTextEdit):

    def __init__(self, parent=None):
        super(WTextEdit, self).__init__(parent=parent)
        self.document = self.document()
        self.document.contentsChanged.connect(self.textAreaChanged)
        # self.setLineWrapMode(QTextEdit.NoWrap)

    def textAreaChanged(self):
        self.document.adjustSize()
        # newWidth = self.document.size().width() + 20
        newHeight = self.document.size().height() + 20
        # if newWidth != self.width():
        #     self.setFixedWidth(newWidth)
        if newHeight != self.height():
            self.setFixedHeight(newHeight)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = CommentField(None, {'description': u'测试', 'sg_thumbnail_path':r"C:\Users\donghao.wang\Pictures\timg (3).jpg"})
    from dayu_widgets.theme import MTheme
    MTheme('light').apply(test)
    test.show()
    sys.exit(app.exec_())





