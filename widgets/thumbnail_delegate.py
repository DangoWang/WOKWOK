#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.7
# Email : dd.parkhere@gmail.com
###################################################################

from dayu_widgets.qt import *
import os
import shutil
from config import envs
reload(envs)


class WImage(QWidget):
    _prePixmap = None

    @property
    def prePixmap(self):
        return self._prePixmap

    @prePixmap.setter
    def prePixmap(self, imagePath):
        self.img_path = imagePath
        # if not os.path.exists(imagePath):
        #     raise

        # self.title.setText(os.path.splitext(os.path.basename(imagePath))[0])

        self._prePixmap = None
        # temp_folder = envs.env_dict.get('WOK_TEMP_DIR')
        # file_name = temp_folder.split('/')[-1].split('\\')[-1]
        # dest_thumb = temp_folder + file_name
        # shutil.copyfile(imagePath.encode('GB2312'), dest_thumb)
        # img = QImage(dest_thumb)
        # print imagePath
        # img = img.scaledToWidth(40)
        # self._prePixmap = QPixmap.fromImage(img)
        self._prePixmap = QPixmap(imagePath)
        if self._prePixmap.isNull():
            self._prePixmap.load(imagePath, 'jpg')

    def __init__(self, parent=None):
        super(WImage, self).__init__(parent)

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        # self.title = QLabel('preview')
        # self.title.setAlignment(Qt.AlignCenter)
        # mainLayout.addWidget(self.title)

        self.previewLabel = QLabel()
        self.previewLabel.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Expanding)
        self.previewLabel.setAlignment(Qt.AlignCenter)
        self.previewLabel.setMinimumSize(40, 40)
        mainLayout.addWidget(self.previewLabel)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.setSizePolicy(sizePolicy)

        self.img_path = ''

    def resizeEvent(self, QResizeEvent):
        scaledSize = self.prePixmap.size()
        scaledSize.scale(self.previewLabel.size(), Qt.KeepAspectRatio)
        if not self.previewLabel.pixmap() or scaledSize != self.previewLabel.pixmap().size():
            self.updatePreviewLabel()

    def updatePreviewLabel(self):
        self.previewLabel.setPixmap(self.prePixmap.scaled(
            self.previewLabel.size(), Qt.KeepAspectRatio,
            Qt.SmoothTransformation))

    def mouseDoubleClickEvent(self, *args, **kwargs):
        thumbnail_win = QDialog(self.parent())
        layout = QHBoxLayout()
        label = QLabel()
        label.setPixmap(self.prePixmap)
        layout.addWidget(label)
        thumbnail_win.setLayout(layout)
        thumbnail_win.show()
        # os.startfile(self.img_path)


class WImage2(QLabel):

    def __init__(self, parent=None, img_path=''):
        super(WImage2, self).__init__(parent=parent)
        default = os.environ['WOKWOK_ROOT'] + '/resources/icons/thumb-load-error.png'
        if not os.path.isfile(img_path):
            img_path = default
        try:
            img = QImage(img_path)
        except:
            img = QImage(default)
        w, h = img.width(), img.height()
        for _ in xrange(999):
            if w <= 100:
                break
            w = w * 0.9
            h = h * 0.9
        size = QSize(w, h)
        pic = QPixmap(img.scaled(size, Qt.IgnoreAspectRatio))
        # widget.setFixedSize(30, 20)
        self.prePixmap = QPixmap(img_path)
        self.setPixmap(pic)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        thumbnail_win = QDialog(self.parent())
        layout = QHBoxLayout()
        label = QLabel()
        label.setPixmap(self.prePixmap)
        layout.addWidget(label)
        thumbnail_win.setLayout(layout)
        thumbnail_win.show()
        # os.startfile(self.img_path)


class WThumbnailDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(WThumbnailDelegate, self).__init__(parent=parent)

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QPen(Qt.NoPen))
        value = index.data(Qt.DisplayRole)
        pix_map = QPixmap(value)  # .scaledToWidth(100)
        pix_bili = float(pix_map.width())/pix_map.height()
        new_height = 100.0/pix_bili
        pix_map = pix_map.scaled(100.0, new_height)
        painter.drawPixmap(option.rect, pix_map)
        painter.restore()
        self.parent().setRowHeight(index.row(), new_height)


