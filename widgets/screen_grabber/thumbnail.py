#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.7
###################################################################
import os
from dayu_widgets.qt import *
import grabber
from widgets.utils import grab_pic


class Thumbnail(QLabel):
    """
    A specialized, custom widget that either displays a
    static square thumbnail or a thumbnail that can be captured
    using screen capture and other methods.
    """

    # emitted when screen is captured
    # passes the QPixmap as a parameter
    screen_grabbed = Signal(object)

    # internal signal to initiate screengrab
    _do_screengrab = Signal()

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        QLabel.__init__(self, parent)

        # _multiple_values allows to display indicator that the summary thumbnail is not applied to all items
        self._multiple_values = False

        self._thumbnail = None
        self._enabled = True
        self.using_dll = True
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setCursor(Qt.PointingHandCursor)
        self._no_thumb_pixmap = QPixmap(os.environ['WOKWOK_ROOT'] + '/resources/icons/thumbnail-holder.png')
        # self._no_thumb_pixmap.scaledToHeight(True)
        # self._no_thumb_pixmap.scaledToWidth(True)
        self._do_screengrab.connect(self._on_screengrab)
        self.set_thumbnail(self._no_thumb_pixmap)
        self.setAcceptDrops(True)

    def setEnabled(self, enabled):
        """
        Overrides base class setEnabled

        :param bool enabled: flag to indicate enabled state of the widget
        """
        self._enabled = enabled
        if enabled:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.unsetCursor()

    def set_thumbnail(self, pixmap):
        """
        Set pixmap to be displayed

        :param pixmap: QPixmap to show or None in order to show default one.
        """
        if pixmap is None:
            self._set_screenshot_pixmap(self._no_thumb_pixmap)
        else:
            self._set_screenshot_pixmap(pixmap)

    def mousePressEvent(self, event):
        """
        Fires when the mouse is pressed.
        In order to emulate the aesthetics of a button,
        a white frame is rendered around the label at mouse press.
        """
        QLabel.mousePressEvent(self, event)

        if self._enabled:
            self.setStyleSheet("QLabel {border: 1px solid #eee;}")

    def mouseReleaseEvent(self, event):
        """
        Fires when the mouse is released
        Stops drawing the border and emits an internal
        screen grab signal.
        """
        QLabel.mouseReleaseEvent(self, event)

        if self._enabled:
            # disable style
            self.setStyleSheet(None)

            # if the mouse is released over the widget,
            # kick off the screengrab
            pos_mouse = event.pos()
            if self.rect().contains(pos_mouse):
                self._do_screengrab.emit()

    def dragEnterEvent(self, event):
        """获取拖拽过来的文件夹+文件"""
        if event.mimeData().hasFormat("text/uri-list"):
            self.thumb = [url.toLocalFile() for url in event.mimeData().urls()][0]
            event.acceptProposedAction()

    def dropEvent(self, event):
        """获取拖拽过来的文件夹"""
        pixmap = QPixmap(self.thumb)
        self._multiple_values = False
        self._set_screenshot_pixmap(pixmap)
        self.screen_grabbed.emit(pixmap)
        pass

    def _on_screengrab(self):
        """
        Perform a screengrab and update the label pixmap.
        Emit screen_grabbed signal.
        """

        self.window().hide()
        try:
            pixmap = grabber.ScreenGrabber.screen_capture() if not self.using_dll else grab_pic()
        finally:
            self.window().show()

        if pixmap:
            self.window().show()
            self._multiple_values = False
            self._set_screenshot_pixmap(pixmap)
            self.screen_grabbed.emit(pixmap)

    def _set_multiple_values_indicator(self, is_multiple_values):
        """
        Specifies wether to show multiple values indicator
        """
        self._multiple_values = is_multiple_values

    def paintEvent(self, paint_event):
        """
        Paint Event override
        """
        # paint multiple values indicator
        if self._multiple_values == True:
            p = QPainter(self)
            p.drawPixmap(
                0,
                0,
                self.width(),
                self.height(),
                self._no_thumb_pixmap,
                0,
                0,
                self._no_thumb_pixmap.width(),
                self._no_thumb_pixmap.height(),
            )
            p.fillRect(0, 0, self.width(), self.height(), QColor(42, 42, 42, 237))
            p.setFont(QFont("Arial", 15, QFont.Bold))
            pen = QPen(QColor("#18A7E3"))
            p.setPen(pen)
            p.drawText(self.rect(), Qt.AlignCenter, "Multiple Values")

        else:
            # paint thumbnail
            QLabel.paintEvent(self, paint_event)

    def _set_screenshot_pixmap(self, pixmap):
        """
        Takes the given QPixmap and sets it to be the thumbnail
        image of the note input widget.

        :param pixmap:  A QPixmap object containing the screenshot image.
        """
        self._thumbnail = pixmap

        # format it to fit the label size
        thumb = self._thumbnail.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.setPixmap(thumb)
