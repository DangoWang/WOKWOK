#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.6
# Email : dd.parkhere@gmail.com
###################################################################


from dayu_widgets.divider import MDivider
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.qt import *
from dayu_widgets.tool_button import MToolButton
from dayu_widgets.push_button import MPushButton


class WToolButton(MToolButton):
    def __init__(self, *args, **kwargs):
        super(WToolButton, self).__init__()
        self.setCheckable(True)

    # def G_look(self, *args, **kwargs):
    #     self.setStyleSheet("border-image: url(./resources/icons/G-look.png);")
    #     # self.setIcon(MIcon(os.environ['WOKWOK_ROOT'] + '/resources/icons/G-look.png'))
    #     return self
    #
    # def G_ok(self, *args, **kwargs):
    #     self.setStyleSheet("border-image: url(./resources/icons/G-ok.png);")
    #     return self

    def set_bg(self, bg, *args, **kwargs):
        self.setStyleSheet("border-image: url(%s);" % bg)
        return self


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    test = WToolButton(None).G_ok()
    test.show()
    # dayu_theme.apply(test)
    # look_win = test.G_ok()
    # look_win.show()
    sys.exit(app.exec_())






