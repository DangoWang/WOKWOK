#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: Wang donghao
# Date  : 2020.6
# wechat : 18250844478
###################################################################
import datetime
import json
import os
import subprocess
import time
import shutil
import psycopg2
from operator import methodcaller
from dayu_widgets.qt import *


#  获取widget的最上层parent控件
def get_widget_top_parent(widget):
    if not widget.parent():
        return widget
    return get_widget_top_parent(widget.parent())


def get_sg_instance():
    import shotgun_api3
    return shotgun_api3.Shotgun('*****',
                                script_name='*****',
                                ensure_ascii=False,
                                api_key='*****')


def change_dict_encoding(input_str, encoding='utf-8'):
    if isinstance(input_str, dict):
        return {change_dict_encoding(key): change_dict_encoding(value) for key, value in input_str.iteritems()}
    elif isinstance(input_str, list):
        return [change_dict_encoding(element) for element in input_str]
    elif isinstance(input_str, unicode):
        return input_str.encode(encoding)
    else:
        return input_str


class FindSqlCache:
    def __init__(self):
        pass

    def find(self, entity, filters, fields, order=None):
        # print entity, filters, fields, order
        self.conn = psycopg2.connect(**eval(os.environ['SG_PG_CONFIG']))
        self.cursor = self.conn.cursor()
        order_script = ''
        default_script = 'ORDER BY '
        if order:
            order_script = []
            for o in order:
                direction = 'DESC' if o.get('direction') == 'desc' else 'ASC'
                order_script.append(o.get('field_name') + ' ' + direction)
            order_script = ','.join(order_script)
            order_script = default_script + order_script
        order_script += ';'
        # print order_script
        self.cursor.execute('SELECT ID FROM %s %s' % (entity, order_script))
        results_ids_temp = list(self.cursor.fetchall())
        results_ids = []
        for ri in results_ids_temp:
            results_ids.append(ri[0])
        result = self.__deal_filter(results_ids, entity, filters)  # 把拉取到的id进行过滤
        final_results = self.__deal_fields(result, entity, fields)
        self.conn.close()
        return final_results

    def __deal_filter(self, *args):
        results_ids, entity, filters = args
        if not filters:
            return results_ids
        final_results = []
        for id in results_ids:
            is_match = False
            dealed_result = False
            for fil in filters:
                if not fil:
                    is_match = True
                    continue
                dealed_result = self.__deal_jump_filter(entity, id, fil)
                if not dealed_result:
                    is_match = False
                    break
                is_match = True
            if is_match and dealed_result:
                final_results.append(id)
        return final_results

    def __deal_jump_filter(self, entity, id, fil):
        #  entity: Version
        #  fil: ['sg_task.Task.code', 'is', 'aaa']
        #  id:
        _filter, operate, limit = fil
        _filter_list = _filter.split('.')
        table = entity
        _id = id
        field = _filter_list[-1]
        i = 0
        while 1:
            if i+3 > len(_filter_list):
                r = False
                if operate == 'is':
                    s = "SELECT * FROM %s WHERE ID=%s AND %s='%s';" % (table, _id, field, limit)
                    self.cursor.execute(s)
                elif operate == 'in':
                    limit = ','.join(["'"+l+"'" for l in limit])
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND %s IN (%s);" % (table, _id, field, limit))
                elif operate == 'is_not':
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND NOT %s='%s';" % (table, _id, field, limit))
                elif operate == 'not_in':
                    limit = ','.join(["'" + l + "'" for l in limit])
                    self.cursor.execute("SELECT * FROM %s WHERE ID=%s AND %s NOT IN (%s);" % (table, _id, field, limit))
                elif operate == 'contains':
                    self.cursor.execute("SELECT * FROM {} WHERE ID={} AND {} LIKE '%{}%';" .format(table, _id, field,limit))
                else:
                    return False
                r = list(self.cursor.fetchall())
                if list(r):
                    return True
                return False
            else:
                script = "SELECT %s FROM %s WHERE ID=%s;" % (_filter_list[i], table, _id)
                self.cursor.execute(script)
                next_table_info = list(self.cursor.fetchall())
                ttt = list(next_table_info)[0][0]
                if not ttt:
                    return False
                if isinstance(eval(ttt), list) and len(eval(ttt)) > 1:
                    result = []
                    for each in eval(ttt):
                        result.append(self.__deal_jump_filter(_filter_list[i + 1], each.get('id'),
                                                              [_filter_list[i + 2], operate, limit]))
                    if any(result):
                        return True
                if isinstance(eval(ttt), list):
                    t_dict = eval(ttt)[0]
                else:
                    t_dict = eval(ttt)
                _id = t_dict.get('id')
                table = _filter_list[i + 1]
                field = _filter_list[i + 2]
            i += 2

    def __deal_fields(self, result_ids, entity, fields):
        #  result_ids: [1,2,3...]
        #  entity: Version
        #  fields: ['sg_task.Task.code', 'code']
        #  return: [{'id': , 'type': , 'code': , 'sg_task.Task.code': }]
        final_results = []
        for _id in result_ids:
            this_result = {'id': _id, 'type': entity}
            for f in fields:
                i = 0
                fields_list = f.split('.')
                field = fields_list[-1]
                table = entity
                __id = _id
                while 1:
                    if i+3 > len(fields_list):
                        self.cursor.execute(
                            "SELECT %s FROM %s WHERE ID=%s;" % (field, table, __id))
                        r = list(self.cursor.fetchall())
                        if not r:
                            this_result[f] = '-'
                        else:
                            fr = list(r)[0][0]
                            try:
                                this_result[f] = eval(fr)
                            except:
                                this_result[f] = fr
                        break
                    else:
                        self.cursor.execute(
                            "SELECT %s FROM %s WHERE ID=%s;" % (fields_list[i], table, __id))
                        next_table_info = list(self.cursor.fetchall())
                        if not next_table_info[0][0]:
                            this_result[f] = '-'
                            break
                        __id = eval(next_table_info[0][0]).get('id')
                        table = fields_list[i+1]
                        field = fields_list[i+2]
                    i += 2
            final_results.append(this_result)
        return json.loads(json.dumps(final_results))

    def find_one(self, entity, filters, fields):
        result = self.find(entity, filters, fields) or [{}]
        return result[0]


class MFetchDataThread(QThread):
    result_sig = Signal(list)
    finished = Signal(bool)

    def __init__(self, mode=None, data=None, using_cache=False):
        super(MFetchDataThread, self).__init__()
        self.mode = mode
        self.data = data
        self.using_cache = using_cache
        self.__sg = None

    def run(self, *args, **kwargs):
        # if 'find' not in self.mode:
        #     while 1:
        #         if os.environ.get('SG_REQUESTING') and os.environ.get('SG_REQUESTING') == '1':
        #             print u'当前有任务正在执行中...'
        #             time.sleep(0.5)
        #         else:
        #             os.environ['SG_REQUESTING'] = '1'
        #             break
        if not self.__sg:
            self.__sg = get_sg_instance() if not self.using_cache else FindSqlCache()
            if not hasattr(self.__sg, self.mode):
                self.__sg = get_sg_instance()
        if self.data:
            # methodcaller(self.mode, *self.data)(self.__sg) or []
            # try:
                # i = 0
                # while i < 6:
                #     try:
            # print self.data
            final_result = methodcaller(self.mode, *self.data)(self.__sg) or []
                #     break
                # except Exception as e:
                #     print (e)
                #     time.sleep(1)
            if 'find' not in self.mode:
                time.sleep(5)
                # os.environ['SG_REQUESTING'] = '0'
            self.result_sig.emit(final_result)
            # except Exception, e:
            #     print self.mode, self.data
            #     self.result_sig.emit({'error': e})
        self.finished.emit(True)


def get_copy_list(source_dir, target_dir):
    #  把文件夹-->文件夹转为文件-->文件
    #  ('C:/a/', 'D:/b/') --> [['C:/a/a.txt', 'D:/b/cc.txt'], [], []...]
    source_dir, target_dir = json.loads(json.dumps([source_dir, target_dir], ensure_ascii=False))
    if not source_dir:
        return []
    files = []
    for f in os.listdir(source_dir):
        source_file = source_dir + '/' + f
        target_file = target_dir + '/' + f
        if os.path.isfile(source_file):
            files.append([source_file, target_file])
        if os.path.isdir(source_file):
            files.extend(get_copy_list(source_file, target_file))
    return files


class CopyFile(QThread):
    # finished = Signal(bool)
    progress = Signal(list)

    def __init__(self, copy_list='', compare_modify=False):
        super(CopyFile, self).__init__()
        self.copy_list = copy_list
        self.compare_modify = compare_modify
        self.copy_num = 0.0
        self.__copy_tuples = []
        # copy_list: [['C:/a/a.txt', 'D:/b/cc.txt'], [], []...]

    def run(self):
        copy_tuples = []
        if not self.copy_list:
            self.finished.emit(True)
            return
        #  先把所有的文件夹--文件夹变成文件--文件
        for ct in self.copy_list:
            if os.path.isdir(ct[0]):
                copy_tuples.extend(get_copy_list(ct[0], ct[1]))
            if os.path.isfile(ct[0]):
                copy_tuples.append([ct[0], ct[1]])
        self.__copy_tuples = [f for f in copy_tuples if '.db' not in f[0]]
        # thread_pool = ThreadPool(8)
        copied = []
        self.copy_num = 0.0
        # _args = []
        # all_copied = []
        for i, each in enumerate(self.__copy_tuples):
            if each[1] in copied:
                self.copy_num += 1.0
                continue
            copied.append(each[1])
            dest_path = os.path.dirname(each[1])
            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
                # os.remove(each[1])
            # _args.append(each)
            self.concurrency_copy_file(each)
            # all_copied.append(thread_pool.apply_async(self.concurrency_copy_file, args=(each,)))
        # thread_pool.close()
        # thread_pool.join()
        # if all_copied:
        # self.finished.emit(True)

    def concurrency_copy_file(self, each):
        # if os.path.isfile(each[0]):  # 如果是文件的话
        try:
            if os.path.isfile(each[1]):
                if self.compare_modify:
                    a = time.localtime(os.stat(each[0]).st_mtime)
                    b = time.localtime(os.stat(each[1]).st_mtime)
                    mTimeS = time.strftime('%Y-%m-%d %H:%M:%S', a)
                    mTimeD = time.strftime('%Y-%m-%d %H:%M:%S', b)
                    s_size = os.path.getsize(each[0])
                    d_size = os.path.getsize(each[1])
                    if mTimeS == mTimeD and s_size == d_size:  # 如果修改日期和大小完全一致，不拷贝
                        pass
                else:
                    shutil.copy2(each[0], each[1])
            else:
                shutil.copy2(each[0], each[1])
            print u'拷贝了 ', each[0], each[1]
            self.copy_num += 1.0
            # print self.copy_num*100.0/float(len(self.copy_list))
            self.progress.emit([each[0].split('/')[-1].split('\\')[-1],
                                self.copy_num*100.0/float(len(self.__copy_tuples))])
            return each[0]
        except Exception as e:
            print u'CopyFile ERROR', e
            # self.finished.emit([])
            return False


def grab_pic():
    clipboard = QApplication.clipboard()
    scrab_exe = os.environ.get('WOKWOK_ROOT')+'/bin/PrScrn.dll'
    subprocess.call('rundll32.exe '+scrab_exe+' ,PrScrn')
    image = clipboard.pixmap()
    return image


if __name__ == '__main__':
    os.environ['WOKWOK_ROOT'] = 'D:/dango_repo/WOKWOK'
    grab_pic()
    # os.environ['SG_CACHE_FILE'] = '//10.10.98.51/anime_srv/shotgun/sqlite3_cache/data.db'
    # db_instance = FindSqlCache()
    # print db_instance.find('Task', [['project.Project.name', 'is', 'FUKA']], ['content', 'entity', 'entity.Asset.code', 'entity.Shot.code'])
































