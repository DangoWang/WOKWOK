# -*- coding: utf-8 -*-

from dayu_widgets.qt import *
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.theme import MTheme
import thread


class BubbleLabel(QWidget):

    BackgroundColor = QColor(195, 195, 195)
    BorderColor = QColor(150, 150, 150)

    def __init__(self, *args, **kwargs):
        text = kwargs.pop("text", "")
        super(BubbleLabel, self).__init__(*args, **kwargs)
        self.pos_offset = [0, 0]
        # 设置无边框置顶
        self.setWindowFlags(
            Qt.Window | Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        # 设置最小宽度和高度
        # self.setMinimumWidth(200)
        # self.setMinimumHeight(200)
        # self.setMaximumSize(300, 300)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        layout = QVBoxLayout(self)
        # 左上右下的边距（下方16是因为包括了三角形）
        layout.setContentsMargins(8, 8, 8, 16)
        self.label = QLabel(self)
        self.label.setGeometry(QRect(328, 240, 329, 27 * 4))
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label)
        self.setText(text)
        # 获取屏幕高宽
        self._desktop = QApplication.instance().desktop()

    def setText(self, text):
        self.label.setText(text)

    def text(self):
        return self.label.text()

    def stop(self):
        self.hide()
        self.animationGroup.stop()
        self.close()

    def show(self):
        super(BubbleLabel, self).show()
        # 窗口开始位置
        startPos = QPoint(
            self._desktop.screenGeometry().width() - self.width() + self.pos_offset[0] + self.width()/5 + 5,
            self._desktop.availableGeometry().height() - self.height() + self.pos_offset[1])
        endPos = QPoint(
            self._desktop.screenGeometry().width() - self.width() + self.pos_offset[0] + self.width()/5 + 5,
            self._desktop.availableGeometry().height() - self.height() + 50 + self.pos_offset[1])# * 3 - 5)
        self.move(startPos)
        # 初始化动画
        self.initAnimation(startPos, endPos)

    def initAnimation(self, startPos, endPos):
        # 透明度动画
        opacityAnimation = QPropertyAnimation(self, "opacity")
        opacityAnimation.setStartValue(1.0)
        opacityAnimation.setEndValue(0.0)
        # 设置动画曲线
        opacityAnimation.setEasingCurve(QEasingCurve.InQuad)
        opacityAnimation.setDuration(1000)  # 在4秒的时间内完成
        # 往上移动动画
        moveAnimation = QPropertyAnimation(self, "pos")
        moveAnimation.setStartValue(startPos)
        moveAnimation.setEndValue(endPos)
        moveAnimation.setEasingCurve(QEasingCurve.OutElastic)
        moveAnimation.setDuration(1000)  # 在5秒的时间内完成
        # 并行动画组（目的是让上面的两个动画同时进行）
        self.animationGroup = QParallelAnimationGroup(self)
        self.opacity_animation_group = QParallelAnimationGroup(self)
        # self.animationGroup.addAnimation(opacityAnimation)
        self.animationGroup.addAnimation(moveAnimation)
        self.opacity_animation_group.addAnimation(opacityAnimation)
        self.opacity_animation_group.finished.connect(self.close)  # 动画结束时关闭窗口
        # moveAnimation.start()
        self.animationGroup.start()
        self.q_time = QTimer()
        self.q_time.timeout.connect(self.opacity_animation_group.start)
        self.opacity_animation_group.finished.connect(self.close)
        self.q_time.start(5000)
        # self.opacity_animation_group.start()

    def paintEvent(self, event):
        super(BubbleLabel, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        rectPath = QPainterPath()  # 圆角矩形
        triPath = QPainterPath()  # 底部三角形

        height = self.height() - 8  # 往上偏移8
        rectPath.addRoundedRect(QRectF(0, 0, self.width(), height), 5, 5)
        x = self.width() / 5 * 4
        triPath.moveTo(x, height)  # 移动到底部横线4/5处
        # 画三角形
        triPath.lineTo(x + 6, height + 8)
        triPath.lineTo(x + 12, height)

        rectPath.addPath(triPath)  # 添加三角形到之前的矩形上

        # 边框画笔
        painter.setPen(QPen(self.BorderColor, 1, Qt.SolidLine,
                            Qt.RoundCap, Qt.RoundJoin))
        # 背景画刷
        painter.setBrush(self.BackgroundColor)
        # 绘制形状
        painter.drawPath(rectPath)
        # 三角形底边绘制一条线保证颜色与背景一样
        painter.setPen(QPen(self.BackgroundColor, 1,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(x, height, x + 12, height)

    def windowOpacity(self):
        return super(BubbleLabel, self).windowOpacity()

    def setWindowOpacity(self, opacity):
        super(BubbleLabel, self).setWindowOpacity(opacity)

    def mousePressEvent(self, event):
        #  点击泡泡显示详情
        dialog = QMainWindow(self)
        centralwidget = QWidget(self)
        dialog.setCentralWidget(centralwidget)
        # dialog.setWindowFlags(Qt.FramelessWindowHint)
        theme = MTheme('light')
        theme.apply(dialog)
        layout = QVBoxLayout()
        centralwidget.setLayout(layout)
        te = MTextEdit(self)
        te.setReadOnly(True)
        dialog.setMinimumSize(700, 500)
        dialog.setWindowTitle(u'消息详情')
        te.setText(self.label.text().replace('\n', '<br>'))
        layout.addWidget(te)
        close_layout = QHBoxLayout()
        close_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        close_btn = MToolButton()
        close_layout.addWidget(close_btn)
        close_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        close_btn.setText(u'我知道了')
        close_btn.clicked.connect(lambda: thread.read(self.label.text()))
        close_btn.clicked.connect(dialog.close)
        # layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        dialog.show()
        self.close()
    # 由于opacity属性不在QWidget中需要重新定义一个
    opacity = Property(float, windowOpacity, setWindowOpacity)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wok_app = BubbleLabel()
    wok_app.setText(u'消息测试')
    wok_app.show()
    sys.exit(app.exec_())


