import psycopg2.extras
import pymysql
from sshtunnel import SSHTunnelForwarder


class DRTMysql:
    def __init__(self, db_config):
        if db_config and db_config.get('ssh'):
            self.__SSH = True
            db_ssh = db_config.get('ssh')
            ssh_address_or_host = (db_ssh["host"], db_ssh['port'])
            ssh_username = db_ssh['user']
            remote_bind_address = (db_config['host'], db_config['port'])
            ssh_db_config = {"ssh_address_or_host": ssh_address_or_host, "ssh_username": ssh_username, "remote_bind_address": remote_bind_address}
            if db_ssh.get('password'):
                ssh_db_config['ssh_password'] = db_ssh.get('password')
            else:
                ssh_db_config['ssh_pkey'] = db_ssh.get('pkey') or None
            self.__server = SSHTunnelForwarder(**ssh_db_config)
            del db_config['ssh']
        else:
            self.__SSH = False
        self.__dbConnect(db_config)

    def __dbConnect(self, db_config):
        try:
            data = {'charset': 'utf8', 'cursorclass': pymysql.cursors.DictCursor, 'autocommit': True}
            data.update(db_config)
            if self.__SSH is True:
                self.__server.start()
                data['host'], data['port'] = "127.0.0.1", self.__server.local_bind_port  # 重新赋值
            self.__conn = pymysql.connect(**data)
            self.__conn.ping(reconnect=True)
            self.__cursor = self.__conn.cursor()
        except Exception:
            self.__conn = None

    def query(self, selector, args=None):
        if self.__conn:
            is_many = False
            selector = selector.strip()
            if args and isinstance(args, (list, tuple)):
                if isinstance(args[0], (list, tuple)):
                    is_many = True
            if is_many:
                self.__cursor.executemany(selector, args)
                self.__cursor.fetchall()
                return True
            else:
                self.__cursor.execute(selector, args)
                if selector.upper().startswith('INSERT INTO'):  # 如果是插入单条数据，则返回id值
                    last_id = self.__cursor.lastrowid
                    self.__cursor.fetchall()
                    return last_id
                else:
                    res = self.__cursor.fetchall()
                    return res or []
        else:
            raise ConnectionError("Mysql Connection timed out: Connect failed")

    def off(self):
        if self.__conn:
            self.__cursor.close()  # 关闭游标
            self.__conn.close()  # 关闭数据库连接
            if self.__SSH is True:
                self.__server.close()
                

class DRTPg:
    def __init__(self, pg_config):
        try:
            connection = psycopg2.connect(**pg_config)
            self.__cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            self.__dbStatus = True
        except Exception:
            self.__dbStatus = False

    def query(self, selector):
        if self.__dbStatus:
            self.__cursor.execute(selector)
            pg_res = self.__cursor.fetchall()
            res = pg_res and list(map(lambda x: dict(x), pg_res)) or []
            return res
        else:
            raise ConnectionError("pgsql Connection timed out: Connect failed")
