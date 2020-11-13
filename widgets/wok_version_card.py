#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.7
# wechat : 18250844478
###################################################################
import datetime
import os
from dayu_widgets.qt import *
from dayu_widgets.card import MMeta
import utils


class WCard(QWidget):
    clicked = Signal(list)

    def __init__(self, *args, **kwargs):
        super(WCard, self).__init__()
        self.version_detail = {}
        self._init_ui()

    def _init_ui(self):
        self.main_layout = QVBoxLayout()
        self.meta = MMeta(extra=True)
        self.meta.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.main_layout.addWidget(self.meta)
        setattr(self.meta, 'focusInEvent', QWidget().focusInEvent)
        setattr(self.meta, 'focusOutEvent', QWidget().focusOutEvent)
        self.setLayout(self.main_layout)
        # self.meta.get_more_button().clicked.connect(self.show_thumbnail)
        # self.setFixedHeight(150)
        self.is_drawled = False
        pass

    def show_thumbnail(self):
        if not self.version_detail.get('sg_thumbnail_path'):
            return
        thumbnail_win = QDialog(self.parent())
        layout = QHBoxLayout()
        label = QLabel()
        label.setPixmap(QPixmap(self.version_detail.get('sg_thumbnail_path')))
        layout.addWidget(label)
        thumbnail_win.setLayout(layout)
        thumbnail_win.show()

    def setup_data(self, data):
        self.meta.setup_data(data)
        if self.version_detail.get('sg_thumbnail_path'):
            more_button = self.meta.get_more_button()
            # more_button.setMinimumSize(30, 30)
            more_button.svg(self.version_detail.get('sg_thumbnail_path'))
        else:
            pass

    def draw_shadow(self):
        shadow_effect = QGraphicsDropShadowEffect(self)
        color = '#eee176'
        shadow_effect.setColor(color)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(5)
        # shadow_effect.setEnabled(False)
        self.setGraphicsEffect(shadow_effect)
        self.is_drawled = False

    def restore_shadow(self):
        if self.is_drawled:
            return
        drop_effect = QGraphicsDropShadowEffect(self)
        drop_effect.setColor(QColor('#908f5e'))
        self.setGraphicsEffect(drop_effect)
        self.clicked.emit([self.version_detail, self])
        self.is_drawled = True

    def mousePressEvent(self, *args, **kwargs):
        self.restore_shadow()

    def mouseReleaseEvent(self, *args, **kwargs):
        pass

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.show_thumbnail()


class WokVersionListWidget(QWidget):
    finished_adding = Signal(bool)
    card_changed = Signal(dict)

    def __init__(self, parent=None):
        super(WokVersionListWidget, self).__init__(parent)
        self._init_ui()
        self._is_set = False
        self.wok_id = None
        self.selected_version_detail = {}
        self.selected_card = None
        self.fetch_data_thread = utils.MFetchDataThread(using_cache=True)
        self.fetch_data_thread.result_sig.connect(self._set_cards)
        self._card = []
        # self.spacer_item = QSpacerItem(QSizePolicy.Minimum, QSizePolicy.Expanding)
        # 监控连接超时
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_thread_running)

    # def check_thread_running(self):
    #     if not self._is_set:
    #         print 'Getting Versions Time out, Retrying...'
    #         self.fetch_data_thread.terminate()
    #         # self.fetch_data_thread.wait()
    #         self.fetch_data_thread.quit()
    #         self.fetch_data_thread.start()
            # self.timer.start(5000)

    def _init_ui(self):
        self.task_card_lay = QVBoxLayout()
        self.setLayout(self.task_card_lay)

    def set_versions_from_wok_id(self, wok_id):
        self.wok_id = wok_id
        self.fetch_data_thread.mode = 'find'
        self.fetch_data_thread.data = [os.environ.get('WOK_VERSION_ENTITY'),
                                       [['sg_wok.%s.id'%os.environ.get('WOK_ENTITY'), 'is', wok_id]],
                                       ['code', 'sg_version_code', 'sg_status_list', 'sg_wok.%s.code'%os.environ.get('WOK_ENTITY'),
                                        'description', 'sg_panda', 'sg_panda.%s.sg_login_name'%os.environ.get('SG_PANDA_ENTITY'),
                                        'sg_wok.%s.sg_link.Shot.code' % os.environ.get('WOK_ENTITY'),
                                        'sg_wok.%s.sg_link.Asset.code' % os.environ.get('WOK_ENTITY'),
                                        'updated_at', 'sg_wok', 'sg_feedback', 'sg_path', 'sg_thumbnail_path'],
                                       [{'field_name': 'sg_version_code', 'direction': 'desc'}]
                                        ]

    def parse(self):
        self.fetch_data_thread.start()
        # self.timer.start(5000)

    def _clear_cards(self):
        for card in self._card:
            card.deleteLater()
        # self.task_card_lay.removeItem(self.spacer_item)
        self._card = []

    def _set_cards(self, version_lists):
        self._clear_cards()
        if version_lists:
            # self.task_card_lay.addWidget(QLabel('test01'))
            for version in version_lists:
                version_update = version.get('updated_at').strftime('%Y-%m-%d-%H:%M:%S') if isinstance(version.get('updated_at'), datetime.datetime) else version.get('updated_at')
                version['updated_at'] = version_update
                # for _ in range(2):
                title = str(version.get('description')) if isinstance(version.get('description'), int) else version.get('description')
                date = version.get('updated_at').strftime('%y%m%d') if isinstance(version.get('updated_at'), datetime.datetime) else version.get('updated_at')
                setting = {
                    'title': title,
                    'description': '\n'.join([version.get('sg_version_code') or '', date]),
                    'avatar': MPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/%s.png' % version.get('sg_status_list'))
                }
                version['description'] = title
                meta_card = WCard()
                # meta_card.setMaximumHeight(100)
                meta_card.version_detail = version or {}
                meta_card.setup_data(setting)
                self.task_card_lay.addWidget(meta_card)
                self._card.append(meta_card)
                meta_card.clicked.connect(self.on_card_clicked)
            # self.task_card_lay.addItem(self.spacer_item)
            self._card[0].restore_shadow()
            self.finished_adding.emit(True)
        else:
            self.finished_adding.emit(False)

        # self.timer.stop()
        self._is_set = True

    def on_card_clicked(self, version_detail_widget):
        self.selected_version_detail, self.selected_card = version_detail_widget
        for card in self._card:
            if card != self.selected_card:
                card.draw_shadow()
        self.card_changed.emit(self.selected_version_detail)


