#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Author: wang donghao
# Date  : 2020.7
# Email : dd.parkhere@gmail.com
###################################################################
import datetime
import os
from dayu_widgets.qt import QThread, Signal
import pika


class MessageThread(QThread):
    new_messages_sig = Signal(basestring)
    cmd_sig = Signal(basestring)

    def __init__(self, parent=None):
        super(MessageThread, self).__init__(parent)
        self.user = os.environ.get('SG_PANDA')
        self.mq_config = eval(os.environ['MQ_CONFIG'])
        credentials = pika.PlainCredentials(self.mq_config.get('username'), self.mq_config.get('password'))  # mq用户名和密码
        self.bc = pika.BlockingConnection(pika.ConnectionParameters(host=self.mq_config.get('host'),
                                                                    port=self.mq_config.get('port'),
                                                                    virtual_host='/',
                                                                    credentials=credentials))

    def get_message_from_mq(self, ch, method, properties, body):
        if body:
            self.new_messages_sig.emit(body.decode('utf-8'))
            
    def get_cmd_msg_from_mq(self, ch, method, properties, body):
        if body:
            self.cmd_sig.emit(body)

    def run(self):
        print u'消息已开始监听...'
        try:
            self.channel = self.bc.channel()
            notice_result = self.channel.queue_declare(queue=self.user+'_msg', exclusive=False)
            cmd_result = self.channel.queue_declare(queue=self.user+'_cmd', exclusive=False)
            self.channel.queue_bind(exchange='notice', queue=notice_result.method.queue)
            self.channel.queue_bind(exchange='cmd', queue=cmd_result.method.queue)
            self.channel.basic_consume(queue=notice_result.method.queue, on_message_callback=self.get_message_from_mq, auto_ack=True)
            self.channel.basic_consume(queue=cmd_result.method.queue, on_message_callback=self.get_cmd_msg_from_mq, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            pass


def send(info,
         exchange='notice',
         sender=os.environ.get("SG_PANDA"),
         receiver='',
         sender_nick_name=''):
    mq_config = eval(os.environ['MQ_CONFIG'])
    credential = pika.PlainCredentials(mq_config.get('username'), mq_config.get('password'))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=mq_config.get('host'), port=mq_config.get('port'),
                                  virtual_host='/', credentials=credential))
    channel = connection.channel()
    routing_key = receiver + '_msg' if receiver else ''
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=info)
    connection.close()

    #  在pg中创建一条数据
    if receiver:
        import psycopg2
        pg_conn = psycopg2.connect(**eval(os.environ['SG_PG_CONFIG']))
        cursor = pg_conn.cursor()
        exe_script = "insert into anime_message (sender, reciever, is_read, content, time_created, sender_nick_name) " \
                     "values ('%s', '%s', false, '%s', '%s', '%s')" \
                     % (sender, receiver, info, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        os.environ.get("SG_PANDA_NICK_NAME").decode('gbk'))
        cursor.execute(exe_script)
        pg_conn.commit()
        pg_conn.close()


def read(info):
    if info:
        import psycopg2
        pg_conn = psycopg2.connect(**eval(os.environ['SG_PG_CONFIG']))
        cursor = pg_conn.cursor()
        cursor.execute("update anime_message set is_read=true where content='%s'"%info)
        pg_conn.commit()
        pg_conn.close()


def get_msgs(is_read=None, sender=None, receiver=None):
    import psycopg2
    pg_conn = psycopg2.connect(**eval(os.environ['SG_PG_CONFIG']))
    cursor = pg_conn.cursor()
    filter_list = []
    filter_str = ''
    if is_read:
        filter_list.append("is_read='%s'" % is_read)
    if sender:
        filter_list.append("sender='%s'" % sender)
    if receiver:
        filter_list.append("reciever='%s'" % receiver)
    if filter_list:
        filter_str = ' where ' + ' and '.join(filter_list)
    cursor.execute("select * from anime_message" + filter_str)
    r = cursor.fetchall()
    pg_conn.commit()
    pg_conn.close()
    return r


if __name__ == '__main__':
    from config import envs
    print get_msgs('false', 'donghao.wang')





