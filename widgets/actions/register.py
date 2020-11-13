#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.6
# wechat : 18250844478
###################################################################


# def create_wok(kwargs):
#     from create_wok import main
#     win = main.CreateWokMain(kwargs.get('widget'))
#     win.show()
#     pass


def submit_version(kwargs):
    from action_submit_version import main
    win = main.Submit(parent=kwargs.get('widget'), config=kwargs)
    win.show()


def edit_wok(kwargs):
    import action_edit_wok
    win = action_edit_wok.main(parent=kwargs.get('widget'), wok_id=kwargs.get('id')[0])
    win.show()


def start_opt(kwargs):
    from action_start_optimize import main as action_start_optimize_main
    win = action_start_optimize_main.OptWin(parent=kwargs.get('widget'), config=kwargs)
    win.show()


def file_to_p4(kwargs):
    from action_file_to_p4 import main as action_file_to_p4_main
    win = action_file_to_p4_main.P4SubmitWin(parent=kwargs.get('widget'), config=kwargs)
    win.show()


def change_wok_status(kwargs):
    from action_change_wok_status import main as action_change_wok_status
    win = action_change_wok_status.ChangeWokStatus(parent=kwargs.get('widget'), config=kwargs)
    win.show()

