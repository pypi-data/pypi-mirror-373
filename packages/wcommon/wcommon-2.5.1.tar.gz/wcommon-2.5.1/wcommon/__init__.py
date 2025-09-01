# coding=utf-8
from __future__ import division
import time as timetool
import datetime as datetime_tool
import requests
import json
import subprocess
import socket
import traceback
import os
import sys
import aiomysql
import asyncio
import pymysql
import re
import configparser
import urllib.parse
from loguru import logger
import hashlib
import platform
import warnings
import random
import string
import queue
import threading
import zmq
import shutil
from sys import argv
import sys
import os
import shutil
import glob
from typing import Any, Optional, Tuple, List, Dict
import functools
import inspect
import uuid
from PIL import Image
import io

# reload(sys)
# sys.setdefaultencoding('utf8')
# logger.info("WARN:please configuration the configuraion_file variable")


def getConfig(config_file=None):
    warnings.warn("此方法已废弃，不推荐使用，请使用 get_config 替换。", DeprecationWarning)
    return get_config(config_file)


def execute_command(cmd):
    warnings.warn("此方法已废弃，不推荐使用，请使用 command 替换。", DeprecationWarning)
    return command(cmd)


def get_config(config_file=None):
    if config_file is None:
        configuration_path_prefix = os.path.expanduser("~")
        config_file = "{}/apps/public/conf.ini".format(configuration_path_prefix)

    logger.info(config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def command(cmd):
    """执行shell命令,并返回结果

    :param cmd:
    :return:
    """
    major = sys.version_info[0]
    if major == 2:
        proc = subprocess.Popen([cmd, ], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out
    else:
        status, output = subprocess.getstatusoutput(cmd)
        if status == 0:
            status = True
        else:
            status = False

        return status, output


# 将datetime转为timestamp
def timestamp(dt):
    return int(timetool.mktime(dt.timetuple()))


def set_logger_level(level):
    """设置loguru的日志级别

    Args:
        level: logger level,DEBUG,INFO,WARNING,ERROR....

    Returns:
        handler_id.
    """
    # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
    logger.remove()
    # 添加一个可以修改控制的handler
    handler_id = logger.add(sys.stderr, level=level)
    return handler_id


# 获取redisCluster的对象
# def getRedisCluster(redisClusterStr):
#     from rediscluster import StrictRedisCluster
#     logger.debug(redisClusterStr)
#     redisCluster = []
#     for nodePort in redisClusterStr.split(","):
#         kv = nodePort.split(":")
#         node = {"host": kv[0], "port": kv[1]}
#         redisCluster.append(node)
#
#     logger.debug(redisCluster)
#     rc = StrictRedisCluster(startup_nodes=redisCluster, decode_responses=True)
#     return rc


# 获取文件的创建时间
def getFileCreateTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的访问时间
def getFileAccessTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getatime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的修改时间
def getFileModifyTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getmtime(filePath)
    return datetime_tool.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def getHost(url):
    begin_index = url.find("//")
    end_index = url.find("/", begin_index + 2)
    host = url[begin_index + 2:end_index]
    return host


def getHostname(url):
    begin_index = url.find("//")
    end_index = url.find(":", begin_index + 2)
    if end_index < 0:
        end_index = url.find("/", begin_index + 2)
    hostname = url[begin_index + 2:end_index]
    return hostname


def getFileSize(filePath):
    fsize = os.path.getsize(filePath)
    return fsize


def getFilePrefix(path):
    return os.path.splitext(path)[0]


def getFilePostfix(path):
    return os.path.splitext(path)[1][1:]

def getFileExtension(path):
    return os.path.splitext(path)[1][1:]

def getLocalHostname():
    hostname = ""
    try:
        hostname = socket.gethostname()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return hostname


def getLocalIp():
    ip = ""
    try:
        # ip=socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.debug(e)
        traceback.print_exc()
    return ip


def generate_random_str(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_digit_str(length):
    return ''.join(random.choice(string.digits) for _ in range(length))


def generate_lower_str(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def get_external_ip():
    # 这里的-s参数目的是在进行网络请求的时候禁止在控制台输出进度
    proc = subprocess.Popen(["curl -s https://api.hohode.com/ip"], stdout=subprocess.PIPE, shell=True)
    (outer_ip, err) = proc.communicate()
    if isinstance(outer_ip, bytes):
        outer_ip = outer_ip.decode("utf8")
    return outer_ip


def ding_send_text(title, message, token=None, mobiles=[], is_at_all=False):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = re.sub("<PRE>","",message)
    message = re.sub("<POST>", "<br/>", message)
    if not token:
        config = get_config()
        token = config.get("dingding", "token")
    content = {
        "msgtype": "markdown",
        "markdown": {
            "title":title,
            "text": "### **{}**\n{}".format(title,message)
        }
    }
    data = json.dumps(content)
    resp =requests.post("https://oapi.dingtalk.com/robot/send?access_token=" + token, data,
                  auth=('Content-Type', 'application/json'),headers=header)
    return resp


def feishu_send_text(title, message, token=None, mobiles=[], is_at_all=False):
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = re.sub("<PRE>","",message)
    message = re.sub("<POST>", "", message)
    if not token:
        config = get_config()
        token = config.get("feishu", "token")
    content = {
        "msg_type": "interactive",
        "card": {
            "elements": [{
                    "tag": "div",
                    "text": {
                            "content": message,
                            "tag": "lark_md"
                    }
            }],
            "header": {
                    "title": {
                            "content": title,
                            "tag": "plain_text"
                    }
            }
        }
    }
    data = json.dumps(content)
    resp =requests.post("https://open.feishu.cn/open-apis/bot/v2/hook/" + token, data,
                  auth=('Content-Type', 'application/json'),headers=header)
    return resp


def eweixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    weixin_send_text(message, token, mobiles, is_at_all)


def weixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    if not token:
        config = get_config()
        token = config.get("eweixin", "token")
    content = "{}[{}]\n{}".format(getLocalHostname(), getLocalIp(), message)
    data = json.dumps({"msgtype": "text", "text": {"content": content, "mentioned_mobile_list": mobiles}})
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token, data,
                  auth=('Content-Type', 'application/json'))


def wecom_send_text(title,message, token=None):
    if not token:
        config = get_config()
        token = config.get("eweixin", "token")
    message = re.sub("<PRE>",">",message)
    message = re.sub("<POST>", "", message)
    content = {
        "msgtype": "markdown",
        "markdown": {
            "content": "### **{}**\n{}".format(title,message)
        }
    }
    data = json.dumps(content)
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token, data,
                  auth=('Content-Type', 'application/json'))


def md5(arg, is_file=False):
    """
    :param arg: 原始字符串，或者文件路径
    :param is_file: 如果为True，就对文件做md5处理
    :return : 对原始字符串进行MD5加密的字符串
    """

    class_name = arg.__class__.__module__ + "." + arg.__class__.__name__
    if class_name == "tornado.httputil.HTTPFile":
        return hashlib.md5(arg.body).hexdigest()
    content = arg
    m = hashlib.md5()
    temp_file = None
    if is_file:
        temp_file = open(arg, 'rb')
        content = temp_file.read()
    elif type(arg) is str:
        content = arg.encode(encoding='utf-8')
    m.update(content)
    if temp_file is not None:
        temp_file.close()
    return m.hexdigest()


# def aes(text,apiSecret):
#     """
#     AES加密
#     :param text:text
#     :param apiSecret:apiSecret
#     :return: AES加密后的字符串
#     """
#     key = apiSecret[:16].encode('gbk')# 密匙，apiSecret的前十六位
#     iv = apiSecret[16:].encode('gbk')# 偏移量，apiSecret的后十六位
#     mycipher = AES.new(key, AES.MODE_CBC, iv)
#     # 加密的明文长度必须为16的倍数，如果长度不为16的倍数，则需要补足为16的倍数
#     # 将iv（密钥向量）加到加密的密文开头，一起传输
#     ciphertext = iv + mycipher.encrypt(text.encode())
#     e = b2a_hex(ciphertext)[32:].decode() # 加密后
#     return e  # 加密

def dejson(content):
    """
    :param content: 非标准Json字符串，像JavaScript的类Json字符串那样
    :return: 标准的Json字符串
    """
    tmp_content = re.sub("\\s+", "", content)
    tmp_content = re.sub(":'", r':"', tmp_content)
    tmp_content = re.sub("':", r'":', tmp_content)
    tmp_content = re.sub("',", r'",', tmp_content)
    tmp_content = re.sub(",'", r',"', tmp_content)
    tmp_content = re.sub("[{]'([a-zA-Z]{2,})", r'{"\1', tmp_content)

    tmp_content = re.sub("\\['", r'["', tmp_content)
    tmp_content = re.sub("'}", r'"}', tmp_content)
    tmp_content = re.sub("']", r'"]', tmp_content)

    # tmp_content = re.sub("[{]([a-zA-Z])", r'{"\1', tmp_content)
    tmp_content = re.sub("""[{]([a-zA-Z])""", r'{"\1', tmp_content)
    tmp_content = re.sub("\\b([a-zA-Z])(\\w+):", r'\1\2":', tmp_content)
    tmp_content = re.sub(",([a-zA-Z])", r',"\1', tmp_content)
    return tmp_content


def check_requirement(requirement_list):
    """检查依赖包是否已经安装，如果还未安装，则提示安装。

    Args:
        requirement_list: 依赖包list
    """
    for package in requirement_list:
        try:
            exec("import {0}".format(package))
            logger.info("Requirement {} already!".format(package))
        except ModuleNotFoundError:
            inquiry = input("This script requires {0}. Do you want to install {0}? [y/n]".format(package))
            while (inquiry != "y") and (inquiry != "n"):
                inquiry = input("This script requires {0}. Do you want to install {0}? [y/n]".format(package))
            if inquiry == "y":
                import os
                logger.info("Execute command: pip3 install {0}".format(package))
                os.system("pip3 install {0}".format(package))
            else:
                logger.info("{0} is missing, so the program exits!".format(package))
                exit(-1)

def get_domain(url):
    '''
    获取域名，包含端口，例如：https://www.baidu.com:8080/path/to/page ，解析后为 www.baidu.com:8080
    '''
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    return domain

# reconnecting mysql , 参考 https://www.kingname.info/2017/04/17/decorate-for-method/
def pingmysql(original_function):
    def wrapper(self, *args, **kwargs):
        try:
            self.database.ping()
            if self.columns_dict is None or timetool.time() - self.meta_update_time > 300:
                cursor = self.database.cursor()
                self.columns_dict = {}
                sql = "select TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,DATA_TYPE from information_schema.columns where 1 =1 and TABLE_SCHEMA not in ('information_schema','performance_schema','mysql','sys') "
                cursor.execute(sql)
                for row in cursor:
                    table_schema = row.get("TABLE_SCHEMA")
                    table_name = row.get("TABLE_NAME")
                    column_name = row.get("COLUMN_NAME")
                    k = '{}.{}.{}'.format(table_schema, table_name, column_name)
                    self.columns_dict[k] = row
                self.meta_update_time = timetool.time()
            result = original_function(self, *args, **kwargs)
            return result
        except Exception as e:
            traceback.print_exc()
            return 'an Exception raised.'

    return wrapper


class Mysql():

    def __init__(self, configuration_file=None, section="mysql",host=None, port=3306, user=None, password=None,database_name=None, charset="utf8"):
        self.default_database_name = database_name
        self.database = None
        self.columns_dict = None
        self.meta_update_time = 0  # self.columns_dict数据的更新时间，self.columns_dict 每5分钟左右更新一次
        try:
            if host is None:
                logger.info(configuration_file)
                config = get_config(configuration_file)
                host = config.get(section, "host")
                port = int(config.get(section, "port"))
                user = config.get(section, "user")
                password = config.get(section, "passwd")
                self.default_database_name = config.get(section, "database")
                charset = config.get(section, "charset")
            
            port = int(port)
            logger.info(f"host: {host}, port: {port}, user: {user}, password: {password}, database: {self.default_database_name}, charset: {charset}")
            self.database = pymysql.connect(host=host, port=port, user=user, passwd=password,
                                            db=self.default_database_name,
                                            charset=charset, autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

        except ImportError:
            logger.error("Error: configparser or pymysql module not exists")
        except Exception as e:
            logger.error(e)
            traceback.print_exc()

    def is_legal_value(self, table_name, column_name, val):
        if val is None:
            return True
        if "." not in table_name:
            table_name = "{}.{}".format(self.default_database_name, table_name)
        col_name = "{}.{}".format(table_name, column_name)
        if self.columns_dict is None:
            return True
        row = self.columns_dict.get(col_name)
        if row is None:
            logger.warning(f"{self.columns_dict}中不包含{col_name}")
            return False
        data_type = row.get("DATA_TYPE")
        if data_type in ['int', 'tinyint', 'bigint']:
            str_val = str(val)
            if len(str_val) == 0:
                logger.warning("{} {} is not a valid {}".format(column_name, val, data_type))
                return False
            elif str_val.startswith("-") or str_val.startswith("+"):
                unsigned_number = str_val[1:]
                if not unsigned_number.isnumeric():
                    raise Exception("{} {} is not a wrong {}".format(column_name, val, data_type))
                    return False
            elif not str(val).isnumeric():
                logger.error("{} {} is not a wrong {}".format(column_name, val, data_type))
                raise Exception("{} {} is not a wrong {}".format(column_name, val, data_type))
                return False
        return True

    @pingmysql
    def query(self, sql, argumentTuple=(), timestamp2str=True):
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        rows = []

        if timestamp2str:
            timestamp_field_array = []
            date_field_array = []
            decimal_field_array = []
            for tp in cursor.description:
                if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP or tp[1] == pymysql.constants.FIELD_TYPE.DATETIME:
                    timestamp_field_array.append(tp[0])
                elif tp[1] == pymysql.constants.FIELD_TYPE.DATE:
                    date_field_array.append(tp[0])
                elif tp[1] == pymysql.constants.FIELD_TYPE.DECIMAL or tp[1] == pymysql.constants.FIELD_TYPE.NEWDECIMAL:
                    decimal_field_array.append(tp[0])

            for row in cursor:
                for field in timestamp_field_array:
                    tmp_value = row.get(field)
                    if tmp_value is not None:
                        row[field] = tmp_value.strftime("%Y-%m-%d %H:%M:%S")

                for field in date_field_array:
                    tmp_value = row.get(field)
                    if tmp_value is not None:
                        row[field] = tmp_value.strftime("%Y-%m-%d")

                for field in decimal_field_array:
                    tmp_value = row.get(field)
                    if tmp_value is not None:
                        row[field] = str(tmp_value)

                rows.append(row)
        else:
            for row in cursor:
                rows.append(row)
        return rows

    @pingmysql
    def value(self, sql, argumentTuple=()):
        """
        获取查询结果的第一行的第一个数据
        :param sql:
        :param argumentTuple:
        :return:
        """
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        first_row = cursor.fetchone()
        field = cursor.description[0][0]
        return first_row[field]

    @pingmysql
    def get_int(self, sql, argumentTuple=(), timestamp2str=True):
        val = self.value(sql, argumentTuple)
        if val is None:
            return None
        else:
            return int(val)

    @pingmysql
    def get_str(self, sql, argumentTuple=(), timestamp2str=True):
        val = self.value(sql, argumentTuple)
        if val is None:
            return None
        else:
            return str(val)

    @pingmysql
    def get_bool(self, sql, argumentTuple=(), timestamp2str=True):
        val = self.value(sql, argumentTuple)
        if val is None:
            return None
        else:
            return bool(val)

    @pingmysql
    def get(self, sql, argumentTuple=(), timestamp2str=True):
        """
        获取单条数据，要么返回一条数据，要么返回None
        :param sql:
        :param argumentTuple:
        :param timestamp2str:
        :return:
        """
        if sql and sql.lower().find("limit") == -1:
            sql = "{} limit 1".format(sql)

        rows = self.query(sql, argumentTuple, timestamp2str)
        if rows and len(rows) > 0:
            return rows[0]
        else:
            return None

    @pingmysql
    def insert(self, tableName, dic, commit=True):
        cursor = self.database.cursor()
        cols = []
        vals = []
        placeholders = []
        id = ""
        for key in dic.keys():
            val = dic[key]
            if val is not None and self.is_legal_value(tableName, key, val):
                cols.append(key)
                placeholders.append("%s")
                vals.append(val)
        insert_sql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
        logger.debug(insert_sql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(insert_sql, tuple(vals))
            id = cursor.lastrowid
        if commit:
            self.database.commit()

        return id
    
    @pingmysql
    def update(self, tableName, dic, idFieldName="id", commit=True):
        return self.update_by_id(tableName, dic, idFieldName, commit)

    @pingmysql
    def update_by_id(self, tableName, id, dic, idFieldName="id", commit=True):
        """
        if want to change one field value to NULL, you should put {'fieldname':None} to dic.

        :param tableName:
        :param id:
        :param dic:
        :param idFieldName:
        :param commit:
        :return:
        """
        cursor = self.database.cursor()
        vals = []
        placeholders = []
        for key in dic.keys():
            val = dic[key]
            if val is None:
                placeholders.append("{} = null ".format(key))
            elif self.is_legal_value(tableName, key, val):
                placeholders.append("{} = %s ".format(key))
                vals.append(val)
        setting = " , ".join(placeholders)
        vals.append(id)
        update_sql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
        logger.debug(update_sql)

        result = None
        if commit:
            logger.debug(tuple(vals))
            result = cursor.execute(update_sql, tuple(vals))
        if commit:
            self.database.commit()
        return result

    @pingmysql
    def execute(self, sql, argumentTuple=(), commit=True):
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        if commit:
            self.database.commit()

    @pingmysql
    def delete(self, sql, commit=True):
        cursor = self.database.cursor()
        logger.debug("delete sql:\t" + sql)
        if commit:
            cursor.execute(sql)
            self.database.commit()

    # Bulk Insert
    @pingmysql
    def bulk_insert(self, table_name, field_array, values_array, batch_size=100):
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()

    # Bulk Insert
    @pingmysql
    def bulk_insert2(self, table_name, data, batch_size=100):
        """
        insert the object array to the table use mysql batch insert commit api

        :param table_name: table name
        :param data:  object array
        :param batch_size: size of batch to commit
        :return: no return value
        """
        field_array = data[0].keys()
        field_line = ",".join(field_array)
        placeholder = ",".join(list(map(lambda x: "%s", field_array)))
        logger.info("insert bulk data ")
        ql = "INSERT INTO {} ({}) values ({})".format(table_name, field_line, placeholder)
        logger.debug(ql)

        values_array = []
        for row in data:
            tmp_ar = []
            for i in field_array:
                val = row.get(i)
                tmp_ar.append(val)
            values_array.append(tmp_ar)
        logger.debug(values_array)
        cursor = self.database.cursor()
        for start in range(0, len(values_array), batch_size):
            logger.debug(values_array[start:start + batch_size])
            cursor.executemany(ql, values_array[start:start + batch_size])
            self.database.commit()
            
def async_pingmysql(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if hasattr(self, "refresh_columns_dict") and inspect.iscoroutinefunction(self.refresh_columns_dict):
            await self.refresh_columns_dict()
        return await func(self, *args, **kwargs)
    return wrapper


class AsyncMysql:
    def __init__(self, host, port, user, password, db,
                 charset="utf8", minsize=1, maxsize=10, loop=None):
        self.default_database_name = db
        self.pool = None
        self.columns_dict = None
        self.meta_update_time = 0
        self.loop = loop or asyncio.get_event_loop()
        self.db_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db": db,
            "charset": charset,
            "minsize": minsize,
            "maxsize": maxsize,
        }

    @classmethod
    async def create(cls, **kwargs):
        instance = cls(**kwargs)
        await instance.init_pool()
        return instance

    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            loop=self.loop,
            cursorclass=aiomysql.DictCursor,
            autocommit=True,
            **self.db_config
        )

    async def refresh_columns_dict(self):
        if self.columns_dict is None or timetool.time() - self.meta_update_time > 300:
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        sql = """
                            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                            FROM information_schema.columns
                            WHERE TABLE_SCHEMA NOT IN ('information_schema','performance_schema','mysql','sys')
                        """
                        await cursor.execute(sql)
                        rows = await cursor.fetchall()
                        self.columns_dict = {
                            f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}.{row['COLUMN_NAME']}": row
                            for row in rows
                        }
                        self.meta_update_time = timetool.time()
            except Exception:
                traceback.print_exc()

    async def is_legal_value(self, table_name: str, column_name: str, val: Any) -> bool:
        if val is None:
            return True
        if "." not in table_name:
            table_name = f"{self.default_database_name}.{table_name}"
        col_name = f"{table_name}.{column_name}"
        await self.refresh_columns_dict()
        row = self.columns_dict.get(col_name)
        if row is None:
            logger.warning(f"{self.columns_dict} 中不包含 {col_name}")
            return False
        data_type = row.get("DATA_TYPE")
        if data_type in ['int', 'tinyint', 'bigint']:
            str_val = str(val)
            if not str_val.lstrip('+-').isnumeric():
                logger.error(f"{column_name} = {val} 不是合法的 {data_type}")
                return False
        return True

    @async_pingmysql
    async def query(self, sql: str, args: Tuple = (), timestamp2str: bool = True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                logger.debug("query sql:\t%s, arguments: %s", sql, args)
                await cursor.execute(sql, args)
                rows = await cursor.fetchall()
                if timestamp2str:
                    for row in rows:
                        for k, v in row.items():
                            if hasattr(v, "strftime"):
                                row[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                    return rows
                return rows

    @async_pingmysql
    async def get(self, sql: str, args: Tuple = (), timestamp2str: bool = True):
        if "limit" not in sql.lower():
            sql += " limit 1"
        rows = await self.query(sql, args, timestamp2str)
        return rows[0] if rows else None

    @async_pingmysql
    async def value(self, sql: str, args: Tuple = ()): 
        row = await self.get(sql, args)
        return next(iter(row.values())) if row else None

    @async_pingmysql
    async def get_int(self, sql: str, args: Tuple = ()): 
        val = await self.value(sql, args)
        return int(val) if val is not None else None

    @async_pingmysql
    async def get_str(self, sql: str, args: Tuple = ()): 
        val = await self.value(sql, args)
        return str(val) if val is not None else None

    @async_pingmysql
    async def get_bool(self, sql: str, args: Tuple = ()): 
        val = await self.value(sql, args)
        return bool(val) if val is not None else None

    @async_pingmysql
    async def insert(self, table_name: str, dic: dict, commit: bool = True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                cols, vals, placeholders = [], [], []
                for key, val in dic.items():
                    if val is not None and await self.is_legal_value(table_name, key, val):
                        cols.append(key)
                        placeholders.append("%s")
                        vals.append(val)
                sql = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({','.join(placeholders)})"
                logger.debug(sql)
                logger.debug(vals)
                await cursor.execute(sql, vals)
                if commit:
                    await conn.commit()
                return cursor.lastrowid

    @async_pingmysql
    async def update_by_id(self, table_name: str, id_val, dic: dict, id_field_name="id", commit: bool = True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                placeholders, vals = [], []
                for key, val in dic.items():
                    if val is None:
                        placeholders.append(f"{key} = NULL")
                    elif await self.is_legal_value(table_name, key, val):
                        placeholders.append(f"{key} = %s")
                        vals.append(val)
                vals.append(id_val)
                setting = ", ".join(placeholders)
                sql = f"UPDATE {table_name} SET {setting} WHERE {id_field_name} = %s"
                logger.debug(sql)
                logger.debug(vals)
                await cursor.execute(sql, vals)
                if commit:
                    await conn.commit()
                return cursor.rowcount

    @async_pingmysql
    async def update(self, table_name: str, dic: dict, id_field_name: str = "id", commit: bool = True):
        id_val = dic.get(id_field_name)
        if id_val is None:
            raise ValueError(f"{id_field_name} is required in update()")
        return await self.update_by_id(table_name, id_val, dic, id_field_name, commit)

    @async_pingmysql
    async def execute(self, sql: str, args: Tuple = (), commit: bool = True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                logger.debug("execute sql:\t%s, arguments: %s", sql, args)
                await cursor.execute(sql, args)
                if commit:
                    await conn.commit()
                return cursor.rowcount

    @async_pingmysql
    async def delete(self, sql: str, args: Tuple = (), commit: bool = True):
        logger.debug("delete sql:\t%s, args: %s", sql, args)
        return await self.execute(sql, args, commit)

    @async_pingmysql
    async def bulk_insert(self, table_name: str, data: List[Dict], batch_size: int = 100):
        if not data:
            return
        field_array = list(data[0].keys())
        placeholder = ",".join(["%s"] * len(field_array))
        field_line = ",".join(field_array)
        sql = f"INSERT INTO {table_name} ({field_line}) VALUES ({placeholder})"
        values_array = [[row.get(field) for field in field_array] for row in data]
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                for start in range(0, len(values_array), batch_size):
                    batch = values_array[start:start + batch_size]
                    await cursor.executemany(sql, batch)
                    await conn.commit()


class ElasticSearch():
    """
    通过requests来访问ElasticSearch
    """

    def __init__(self, host, port=9200, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.urlPrefix = "http://{}:{}".format(host, port)

    headers = {
        'content-type': 'application/json'
    }

    def _transfer_data(self, data=None, size=None, sort_field=None, sort_type=None):
        query_dict = {}
        if data is not None:
            if type(data) == str:
                # return data
                query_dict = json.loads(data)
            elif type(data) == dict:
                query_dict = json.loads(json.dumps(data))  # 避免后续修改原始data的内容

        if size is not None:
            query_dict["size"] = size
        if sort_field is not None:
            if sort_type is None:
                sort_type = "asc"
            query_dict["sort"] = [
                {
                    sort_field: {
                        "order": sort_type
                    }
                }
            ]
        return json.dumps(query_dict)

    def search(self, action, data=None, size=None, sort_field=None, sort_type=None):
        """
        :param action: 比如: /scene_model/_search
        :param data:
        :param size:
        :param sort_field:
        :param sort_type:
        :return:
        """
        data1 = self._transfer_data(data, size, sort_field, sort_type)
        return requests.get(url="{}{}".format(self.urlPrefix, action), auth=(self.username, self.password),
                            headers=self.headers, data=data1).json()

    def query(self, action, query_body=None):
        """
        :param action: 比如: /scene_model/_search
        :param query_body:
        :return:
        """
        data1 = self._transfer_data(query_body)
        result = requests.get(url="{}{}".format(self.urlPrefix, action), auth=(self.username, self.password),
                              headers=self.headers, data=data1).json()
        hits = result["hits"]["hits"]
        new_hits = []
        for row in hits:
            source = row["_source"]
            new_hits.append(source)
        return new_hits

    def scroll(self, action, query=None, how_long_keep="1m"):
        """
        Example:

        >>> result = elasticsearch.scroll("/words/_search",query=data)
        >>> for batch in result:
        >>>     rows = batch['hits']['hits']
        >>>     for row in rows:
        >>>         source = row['_source']
        >>>         print("{word},{type},{weight}".format(**source))
        """

        # 发起初始搜索请求
        first_scroll_action = "{}?scroll={}".format(action, how_long_keep)
        next_scroll_action = "/_search/scroll"

        query_dict = {}
        if query is not None:
            if type(query) == str:
                # return data
                query_dict = json.loads(query)
            elif type(query) == dict:
                query_dict = json.loads(json.dumps(query))  # 避免后续修改原始data的内容
        data1 = json.dumps(query_dict)

        resp_json = requests.get(url="{}{}".format(self.urlPrefix, first_scroll_action),
                                 auth=(self.username, self.password),
                                 headers=self.headers, data=data1).json()
        scroll_id = resp_json["_scroll_id"]
        yield resp_json

        while True:
            body = {
                "scroll": "{}".format(how_long_keep),
                "scroll_id": scroll_id
            }
            resp_json = requests.post(url="{}{}".format(self.urlPrefix, next_scroll_action),
                                      auth=(self.username, self.password),
                                      headers=self.headers,
                                      json=body).json()
            if len(resp_json["hits"]["hits"]) == 0:
                requests.delete(url="{}/_search/scroll".format(self.urlPrefix), auth=(self.username, self.password),
                                headers=self.headers, data='"scroll_id": ["{}"]'.format(scroll_id))
                break
            else:
                scroll_id = resp_json["_scroll_id"]
                yield resp_json

    def delete_by_query(self, index, data):
        """
        :param action: /sym/_delete_by_query
        :return:
        """
        data1 = self._transfer_data(data)
        return requests.post(url="{}/{}/_delete_by_query".format(self.urlPrefix, index),
                             auth=(self.username, self.password), headers=self.headers, data=data1)

    def delete(self, index, doc_id):
        return requests.delete(url="{}/{}/_doc/{}".format(self.urlPrefix, index, doc_id),
                               auth=(self.username, self.password))

    def put(self, action, data=None):
        """
        :param action:
        :param data:
        :return:
        """
        return self.post(action, data)

    def post(self, action, data=None):
        data1 = self._transfer_data(data)
        return requests.post(url="{}{}".format(self.urlPrefix, action), auth=(self.username, self.password),
                             headers=self.headers, data=data1)

    def update(self, index_name, doc_id, data):
        """
        :param index_name : 索引的名称
        :param doc_id : 文档的id
        :param data: 格式为{'id': '332214', 'price': '10', 'sort': '5', 'is_use': '3'}
        :return:
        """
        return self.post("/{}/_update/{}".format(index_name, doc_id), data={"doc": data})
    
    def upsert(self, index_name, doc_id, json,):
        """
        :param index_name : 索引的名称
        :param doc_id : 文档的id
        :param json: 格式为{'id': '332214', 'price': '10', 'sort': '5', 'is_use': '3'}
        :return:
        """

        return self.post("/{}/_update/{}".format(index_name, doc_id), data={"doc": json, "doc_as_upsert": True})
         
         
def is_number(str):
    """
    判断是否为数字，整数或者小数都可以
    :param str : 字符串
    :return:
    """
    try:
        float(str)
        return True
    except ValueError:
        return False


class AppleScriptTool():

    def __init__(self, name):
        self.name = name
        self.begin = f"""tell application "System Events"
    tell process "{name}"
        set frontmost to true """
        self.all_cmd = ""


    end = """end tell
end tell"""

    def show(self):
        """
        active 打开窗口
        :param name:
        :return:
        """

        cmd = f"""
            tell application "{self.name}"
                try
                    set winCount to count of windows
                    if winCount is 0 then
                        reopen -- 确保应用程序打开一个窗口
                    end if
                    activate
                on error
                    reopen
                    activate
                end try
            end tell
        """
        subprocess.run(["osascript", "-e", cmd])

    def before_return(self,cmd):
        self.all_cmd = f"{self.all_cmd}\n{cmd}"
        return cmd

    def delay_until(self, element):
        cmd = f"""
            repeat until {element}
            end repeat
        """
        return self.before_return(cmd)
    
    def click(self,element):
        cmd = f"""click {element}"""
        return self.before_return(cmd)

    def input(self, text):
        cmd = f"""
            set the clipboard to "{text}"
            tell application "System Events" to keystroke "v" using command down
        """
        return self.before_return(cmd)

    def press_enter(self):
        cmd = "keystroke return"
        return self.before_return(cmd)

    def press_down(self):
        cmd = "keystroke (ASCII character 31)"
        return self.before_return(cmd)
    
    def set_value(self,text_field,text):
        cmd = f"""  set theTextField to {text_field}
                    set value of theTextField to "{text}"
        """
        return self.before_return(cmd)

    def construct_cmd(self, cmd):
        cmd1 = f"""{self.begin}
                        {cmd}
       {self.end}"""
        cmd1 = cmd1.replace("press_enter", "keystroke return")
        cmd1 = cmd1.replace("press_down", "keystroke (ASCII character 31)")
        cmd1 = re.sub(r"""input (.+)""",
                      r"""set the clipboard to "\1" \n        tell application "System Events" to keystroke "v" using command down""",
                      cmd1)
        return cmd1

    def exec(self, cmd):
        """
                click menu item "搜索" of menu "编辑" of menu bar 1

                input {unionid}

                delay 1 -- 短暂延迟，确保窗口已激活

                press_enter

                {tool.input(message)}
                press_enter
        :param cmd:
        :return:
        """
        whole_cmd = self.construct_cmd(cmd)
        print(whole_cmd)
        self.show()
        subprocess.run(["osascript", "-e", whole_cmd ])

    def submit(self):
        cmd = self.construct_cmd(self.all_cmd)
        self.all_cmd = ""
        self.show()
        logger.info(cmd)
        subprocess.run(["osascript", "-e", cmd ])


    def copy(self,message,execute=False):
        cmd = f"""set the clipboard to "{message}" """
        if execute:
            subprocess.run(["osascript", "-e", cmd ])
        else:
            return self.before_return(cmd)

    def paste(self,execute=False):
        cmd = """tell application "System Events" to keystroke "v" using command down""" 
        if execute:
            subprocess.run(["osascript", "-e", cmd ])
        else:
            return self.before_return(cmd)
    
    def sleep(self,seconds=1):
        cmd = f"delay {seconds}"
        return self.before_return(cmd)
        
    def get_loc_size(self):
        cmd = f"""
            tell application "System Events"
                tell application process "{self.name}"
                    -- 获取窗口的左上角位置和大小
                    set windowPosition to position of window 1
                    set windowSize to size of window 1
                end tell
            end tell

            -- 获取窗口的坐标和大小
            set x to item 1 of windowPosition
            set y to item 2 of windowPosition
            set width to item 1 of windowSize
            set height to item 2 of windowSize
            """
        return self.before_return(cmd)
    
    def screenshot(self):
        """
        截图并将截图保存到剪贴板
        """
        cmd = self.get_loc_size()
        cmd = f"""{cmd}\n do shell script "screencapture -c -R" & x & "," & y & "," & width & "," & height & " " """
        return self.before_return(cmd)

    def screenshot_to(self,path):
        cmd = self.get_loc_size()
        cmd = f"""{cmd}\n do shell script "screencapture -R" & x & "," & y & "," & width & "," & height & " " & quoted form of "{path}" """
        return self.before_return(cmd)

class MqServer():
    # 创建一个阻塞队列
    message_queue = queue.Queue(maxsize=5000)  # 可以设置队列最大容量

    def __init__(self, publish_port=20055, receive_port=20065):
        self.publish_port = publish_port
        self.receive_port = receive_port
        self.context = zmq.Context()  # 共享同一个 Context
        self.publish_socket = None   # 发布端的 socket
        self.receive_socket = None   # 接收端的 socket

    def start_publish(self):
        self.publish_socket = self.context.socket(zmq.PUB)
        self.publish_socket.setsockopt(zmq.HEARTBEAT_IVL, 2000)      # 发送心跳的间隔（毫秒）
        self.publish_socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 6000)  # 超过此时间未收到心跳，认为断开（毫秒）
        self.publish_socket.setsockopt(zmq.HEARTBEAT_TTL, 3000)      # 客户端发送心跳的间隔时间（毫秒）
        self.publish_socket.bind(f"tcp://*:{self.publish_port}")

        while True:
            msg = self.message_queue.get()  # get() 会在队列为空时阻塞
            logger.info(f"消费消息: {msg}")
            self.message_queue.task_done()  # 通知队列任务已完成

            if msg == 'exit':
                sys.exit()
            self.publish_socket.send(msg.encode('utf-8'))
            timetool.sleep(1)

    def start_receive(self):
        self.receive_socket = self.context.socket(zmq.REP)
        self.receive_socket.bind(f"tcp://*:{self.receive_port}")
        while True:
            try:
                message = self.receive_socket.recv()
                self.message_queue.put(message.decode('utf-8'))
                self.receive_socket.send(message)
            except Exception as e:
                print('异常:', e)
                sys.exit()

    def broadcast(self, message):
        if isinstance(message, dict):
            message = json.dumps(message, ensure_ascii=False)
        self.message_queue.put(message)

    def close(self):
        """优雅关闭所有 ZeroMQ 资源"""
        logger.info("正在关闭 MqServer...")
        
        # 关闭 socket
        if self.publish_socket:
            self.publish_socket.close()
        if self.receive_socket:
            self.receive_socket.close()

        # 关闭 context
        if self.context:
            self.context.term()

        logger.info("MqServer 已关闭")

    def start(self):
        logger.info(f"启动发布通知的Server, port为{self.publish_port}")
        threading.Thread(target=self.start_publish).start()
        logger.info(f"启动接收通知的Server, port为{self.receive_port}")
        threading.Thread(target=self.start_receive).start()


class MqProducer():

    def __init__(self,host="localhost",port=20065):
        context = zmq.Context()
        print("zmq version ", zmq.__version__)
        print("Connecting to server...")
        self.socket = context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        self.socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 6000)
        self.socket.setsockopt(zmq.HEARTBEAT_TTL, 3000)
        self.socket.connect(f"tcp://{host}:{port}")
        print(f"Connected to server {host}:{port}.")

    def send(self,message):
        self.socket.send(message.encode('utf-8'))
        return self.socket.recv().decode('utf-8')


class MqConsumer():

    def __init__(self,host="localhost",port=20055):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.setsockopt(zmq.HEARTBEAT_IVL, 2000)
        socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 6000)
        socket.setsockopt(zmq.HEARTBEAT_TTL, 3000)

        # socket.connect("tcp://hohode.com:21055")
        socket.connect(f"tcp://{host}:{port}")
        socket.setsockopt(zmq.SUBSCRIBE, ''.encode('utf-8'))  # 接收所有消息
        self.socket = socket
    
    def close(self):
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.close()

    def receive(self):
        return self.socket.recv().decode('utf-8')

def backup_file():
    file_path = sys.argv[1]
    # 检查 bak 目录是否存在，不存在则创建
    if not os.path.isdir("./bak"):
        os.mkdir("./bak")

    # 获取当前时间
    day = datetime_tool.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 获取文件名
    filename = os.path.basename(file_path)
    # 构造目标文件名
    backup_name = f"./bak/{filename}.bak.{day}"
    # 移动并重命名文件
    shutil.move(file_path, backup_name)
    print(f"将文件备份为{backup_name}")


def temp_delete_file():
    file_path = sys.argv[1]
    dir1 = datetime_tool.datetime.now().strftime("%Y%m%d%H%M%S")
    targetDir = "/tmp/delete/"+dir1+"/"

    mkdirCmd = "mkdir -p "+targetDir
    os.system(mkdirCmd)
    shutil.move(file_path, targetDir)

def copy_file(file_path,target_path):
    shutil.copy(file_path, target_path)
    print(f"将文件复制到{target_path}")

def uuid32():
    # 生成 UUID
    return uuid.uuid4().hex

def is_video(file_path):
    file_path = file_path.lower()
    video_extensions = ['.mp4', '.mkv', '.avi', '.flv', '.mov', '.wmv']
    file_extension = os.path.splitext(file_path)[1]
    return file_extension.lower() in video_extensions

def is_image(file_path):
    file_path = file_path.lower()
    video_extensions = ['.png', '.jpeg', '.jpg', '.gif']
    file_extension = os.path.splitext(file_path)[1]
    return file_extension.lower() in video_extensions

def is_music(file_path):
    file_path = file_path.lower()
    video_extensions = ['.mp3']
    file_extension = os.path.splitext(file_path)[1]
    return file_extension.lower() in video_extensions

def is_mobile(user_agent):
    user_agent = user_agent.lower()
    mobile_patterns = [
        r'Android',
        r'iPhone',
        r'iPad',
        r'Windows Phone',
        r'BlackBerry'
    ]
    for pattern in mobile_patterns:
        if re.search(pattern, user_agent, re.IGNORECASE):
            return True
    return False

class Img:
    @staticmethod
    def compress(image, target_size_kb=1024, step=5, min_quality=20,output_path=None) -> bytes:
        """
        image: PIL.Image.Image or str
        将图片压缩到目标大小以内，返回压缩后的字节流
        """
        if isinstance(image, Image.Image):
            img = image
        elif isinstance(image, str):
            img = Image.open(image)
        else:
            raise ValueError("image must be a PIL.Image.Image or a string path")

        output = io.BytesIO()
        # PNG 转 JPEG
        img_format = img.format if img.format else "JPEG"
        if img_format.upper() == "PNG":
            img_format = "JPEG"
            img = img.convert("RGB")  # PNG 转 JPEG 必须转 RGB

        # 先尝试原图保存
        img.save(output, format=img_format, quality=95, optimize=True)
        if len(output.getvalue()) / 1024 <= target_size_kb:
            return output.getvalue()

        # 循环压缩
        quality = 95
        while quality >= min_quality:
            output.seek(0)
            output.truncate(0)
            img.save(output, format=img_format, quality=quality, optimize=True)
            size_kb = len(output.getvalue()) / 1024
            if size_kb <= target_size_kb:
                break
            quality -= step
        
        if output_path:
            with open(output_path, "wb") as f:
                f.write(output.getvalue())
        return output.getvalue()

    @staticmethod
    def cut(image,ratio,output_path=None) -> Image.Image:
        """
        image: PIL.Image.Image or str
        ration is a tuple with four elements: left, top, right, bottom，percent of height and width
        """
        if isinstance(image, Image.Image):
            img = image
        elif isinstance(image, str):
            img = Image.open(image)
        else:
            raise ValueError("image must be a PIL.Image.Image or a string path")
        
        height = img.height
        width = img.width
        left = 0 if ratio[0] is None or ratio[0] == -1 or ratio[0] == 0 else width * ratio[0]
        top = 0 if ratio[1] is None or ratio[1] == -1  or ratio[1] == 0 else height * ratio[1]
        right = width if ratio[2] is None or ratio[2] == -1 else width * ratio[2]
        bottom = height if ratio[3] is None or ratio[3] == -1 else height * ratio[3]
        new_image = img.crop((left, top, right, bottom))
        if output_path:
            new_image.save(output_path)
        return new_image
