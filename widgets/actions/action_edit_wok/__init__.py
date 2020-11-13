#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: WangDonghao
# Date  : 2020.8
###################################################################

from widgets import create_wok


def main(parent, wok_id):
    update_win = create_wok.main.CreateWokMain(parent=parent, mode='update', wok_id=wok_id)
    update_win.setWindowTitle(u'编辑锅：%s' % wok_id)
    return update_win
