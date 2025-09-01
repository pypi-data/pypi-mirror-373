#############################################
# File Name: ddreport
# Author: duanliangcong
# Mail: 137562703@qq.com
# Created Time:  2022-11-02 15:00:00
#############################################
from .api import DRTHTTP
from .db import DRTMysql, DRTPg
from .func import DRTFunctions, DRTDiff
from .handle import Process
from jsonpath import jsonpath
from _pytest.python import Function
from _pytest.runner import runtestprotocol
from collections.abc import Iterable
from uuid import uuid4
import pytest
import time
import ast
import json
import os
import shutil


def get_env(env_path, env_name):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            envs = json.loads(f.read())
        return jsonpath(envs, f'$..[?(@.name=="{env_name}")]')[0]
    except Exception:
        return dict()


def produce_png_name():
    return str(uuid4()).replace("-", "") + ".png"


class Gvalues(object):
    __slots__ = '__value'

    def __init__(self):
        self.__value = dict()

    def set(self, key, value):
        self.__value.update({key: value})

    def get(self, key):
        return self.__value.get(key)


class Image(object):
    def __init__(self):
        self.__src = ''
        self._dirname = []

    def src(self, value):
        self.__src = value


DRT_NAME = "ddreport"

replace_data = [{'name': '<', 'value': '&autoxyhth;'}, {'name': '>', 'value': '&autodyhth;'}]

CONVEY_DICT = {
    "gval": Gvalues(),
    "imgs": Image(),
    "host": "",
    "mysql_config": None,
    "pgsql_config": None,
    "loop_name": "",
    "temp_query": {"ddquery": None},
    "fail": False,
    "status": "passed",
    "response": {},
    "screen": [],
}

SUMMARY_FROM = {
    "envname": "",
    "desc": "",
    "tester": "",
    "start_time": "",
    "end_time": "",
    "failed": 0,
    "passed": 0,
    "skipped": 0,
    "error": 0,
    "db_connect_time": {}
}

CASE_TABLE = []

RES_DATA = {}


def pytest_addoption(parser):
    parser.addoption(
        "--ddreport",
        action="store",
        default=None,
        help="测试报告标识",
    )
    parser.addoption(
        "--desc",
        action="store",
        default=None,
        help="当前测试报告的说明",
    )
    parser.addoption(
        "--tester",
        action="store",
        default=None,
        help="测试人员",
    )
    parser.addoption(
        "--envpath",
        action="store",
        default=None,
        help="环境配置路径",
    ),
    parser.addoption(
        "--envname",
        action="store",
        default=None,
        help="环境名称",
    ),
    parser.addoption(
        "--recv",
        action="store",
        default=None,
        help="接收一个字典类型的参数",
    ),
    parser.addoption(
        "--screen",
        action="store",
        default=None,
        help="截图方法",
    )


def pytest_report_teststatus(config, report):
    # 更新终端打印（.  s   F  E）
    if report.outcome == 'error':
        return report.outcome, 'E', None


def pytest_sessionstart(session):
    drt = session.config.getoption('--ddreport')
    # 创建UI自动化失败截图的保存目录（[报告目录路径，图片保存目录名称]）
    CONVEY_DICT["imgs"]._dirname = [os.path.dirname(drt), time.strftime("%Y%m%d%H%M%S")]
    os.makedirs(os.path.join(*CONVEY_DICT["imgs"]._dirname), exist_ok=True)
    # 基本参数
    SUMMARY_FROM['desc'] = session.config.getoption('--desc') or ''
    SUMMARY_FROM['start_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    SUMMARY_FROM['tester'] = session.config.getoption('--tester') or ''
    # 获取环境配置
    envpath = session.config.getoption("--envpath")
    envname = session.config.getoption("--envname")
    if all([envpath, envname]):
        env_data = get_env(envpath, envname)
        SUMMARY_FROM["envname"] = envname
        CONVEY_DICT["host"] = env_data.get('host') or ''
        CONVEY_DICT["mysql_config"] = env_data.get('mysql')
        CONVEY_DICT["pgsql_config"] = env_data.get('pgsql')
    # 接收传参
    if (receive_dict := session.config.getoption("--recv")):
        try:
            receive_dict = json.loads(receive_dict)
        except Exception:
            try:
                receive_dict = ast.literal_eval(receive_dict)
            except Exception:
                receive_dict = {}
        for k, v in receive_dict.items():
            CONVEY_DICT["gval"].set(k, v)
    # 截图参数
    CONVEY_DICT["screen"] = session.config.getoption('--screen') or []


def pytest_sessionfinish(session, exitstatus):
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                # 尝试调用对象的默认序列化方法
                return super().default(obj)
            except TypeError:
                # 如果遇到非可序列化的对象，则将其转为字符串
                return str(obj)
    # img目录
    img_dir_path = os.path.join(*CONVEY_DICT["imgs"]._dirname)
    if os.path.exists(img_dir_path):
        if not (os.listdir(img_dir_path)):
            shutil.rmtree(img_dir_path)
    # 数据库连接耗时
    if (dbinfo := SUMMARY_FROM["db_connect_time"]):
        SUMMARY_FROM["db_connect_time"] = "DB连接耗时: " + " | ".join([f"({k}={v})" for k, v in dbinfo.items()])
    else:
        SUMMARY_FROM["db_connect_time"] = ""

    # 结束后相关操作
    SUMMARY_FROM['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    if (drt := session.config.getoption('--ddreport')):
        form_data = json.dumps(SUMMARY_FROM, cls=CustomJSONEncoder)
        table_data = json.dumps(CASE_TABLE, cls=CustomJSONEncoder)
        for item_rep in replace_data:
            form_data = form_data.replace(item_rep["name"], item_rep["value"])
            table_data = table_data.replace(item_rep["name"], item_rep["value"])
        # 报告路径
        report_dir_file = drt.replace('\\', '/').strip()
        if not report_dir_file.endswith('.html'):
            report_dir, report_name = report_dir_file, f'report_{time.strftime("%Y%m%d-%H%M%S")}.html'
        else:
            report_dir, report_name = '/'.join(report_dir_file.split('/')[:-1]), report_dir_file.split('/')[-1]
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        report_save_path = os.path.join(report_dir, report_name)
        # 读取测试报告文件
        template_path = os.path.join(os.path.dirname(__file__), 'template', 'index.html')
        with open(f'{template_path}', 'r', encoding='utf-8') as f:
            template = f.read()
        report_template = template.replace("const formData = {}", f"const formData = {form_data}")
        report_template = report_template.replace("const sourceData = []", f"const sourceData = {table_data}")
        report_template = report_template.replace("const formatList = []", f"const formatList = {replace_data}")
        with open(report_save_path, 'w', encoding='utf-8') as f:
            f.write(report_template)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    call.duration = '%.2f' % float(call.duration)  # 科学计数转普通格式
    info = {}
    if report.when == 'call':
        # 过滤不需要的funcargs
        RES_DATA.clear()
        params_keys = [om.args[0] for om in item.own_markers if om.args]
        for k in item.fixturenames:
            if k in ["_session_faker", "request"]:
                continue
            elif params_keys and k in params_keys:
                continue
            else:
                RES_DATA[k] = item.funcargs[k]
        info = node_handle(report, item, call)
        SUMMARY_FROM[report.outcome] += 1
        # 失败结束标签
        if item.funcargs:
            for k, ele_func in item.funcargs.items():
                if ele_func.__class__.__name__ == DRT_NAME and ele_func.failexit is True:
                    CONVEY_DICT["fail"] = True
                    CONVEY_DICT["status"] = report.outcome
                    if report.outcome != "passed":
                        info["fail_tag"] = "用例标记为: 非成功用例，程序结束"
    elif report.outcome == 'failed':
        report.outcome = 'error'
        info = node_handle(report, item, call)
        SUMMARY_FROM['error'] += 1
    elif report.outcome == 'skipped':
        info = node_handle(report, item, call)
        SUMMARY_FROM[report.outcome] += 1
    if report.when == 'teardown':
        # 是否有图片信息
        if (img_src := CONVEY_DICT["imgs"]._Image__src):
            if os.path.exists(img_src):
                png_name = produce_png_name()  # 图片名称
                img_path = os.path.join(*CONVEY_DICT["imgs"]._dirname, png_name)  # 图片存储路径
                shutil.copy2(img_src, img_path)
                report_img = os.path.join(CONVEY_DICT["imgs"]._dirname[-1], png_name)
                CONVEY_DICT["response"].update(dict(img=report_img))
            else:
                CONVEY_DICT["response"].update(dict(img=img_src + ""))
        CASE_TABLE.append(CONVEY_DICT["response"])
        # 初始化数据
        CONVEY_DICT["imgs"]._Image__src = ""
        CONVEY_DICT["temp_query"]["ddquery"] = {}
        # 是否条件结束程序
        if CONVEY_DICT["fail"] and CONVEY_DICT["status"] != "passed":
            pytest.exit("条件终止程序")
        # 修改条件结束参数
        if item.funcargs:
            for k, ele_func in item.funcargs.items():
                if ele_func.__class__.__name__ == DRT_NAME:
                    ele_func.failexit = False
                    CONVEY_DICT.update({"fail": False, "status": "passed"})
    CONVEY_DICT["response"] = info


def node_handle(node, item, call):

    d = dict()
    # 模块
    d['model'] = item.module.__name__
    # 类
    d['classed'] = '' if item.parent.obj == item.module else item.parent.obj.__name__
    # 方法
    d['method'] = item.originalname
    # 描述
    d['doc'] = item.function.__doc__
    # 响应时间
    d['duration'] = float(call.duration)
    # 结果
    d['status'] = node.outcome
    # 详细内容
    if node.sections:
        d["print"] = "\n".join([p[-1] for p in node.sections])
    # 异常信息展示
    if call.excinfo:
        excobj = node.longrepr
        try:
            if d['status'] == 'skipped':
                d["skipped"] = excobj[-1]
            else:
                # 错误的响应信息
                d.update(call.excinfo.value.value.query_info)
                d.update(call.excinfo.value.value.error_info)
        except Exception:
            # 异常情况
            try:
                exc_list = ["file " + excobj.reprcrash.path + ", line " + str(excobj.reprcrash.lineno), excobj.reprcrash.message]
            except Exception:
                try:
                    exc_list = excobj.tblines
                    errorstring = excobj.errorstring
                    exc_list.append(errorstring)
                except Exception:
                    exc_list = [str(call.excinfo)]
            d.update(dict(msg_dict="\n".join(exc_list)))
    # 打印正确请求
    query_data = CONVEY_DICT["temp_query"].get("ddquery")
    if query_data:
        pro = Process()
        pro.data_process(query_data, None)
        d.update(pro.query_info)
    return d


def pytest_runtest_protocol(item, nextitem):
    # 笛卡尔乘积索引
    def cartesian_product_index(input_list):
        if len(input_list) == 0:
            return [[]]
        result = []
        for ele, element in enumerate(input_list[0]):
            for sub_index in cartesian_product_index(input_list[1:]):
                result.append([(ele, element)] + sub_index)
        return result

    # copy-item-function
    def copy_item(curitem):
        newitem = Function.from_parent(name=curitem.originalname, parent=curitem.parent, callspec=curitem.callspec,
                                       fixtureinfo=curitem._fixtureinfo, originalname=curitem.originalname)
        return newitem

    # item.funcargs赋值
    def item_funcargs(item):
        # for k, v in RES_DATA.items():
        #     item.funcargs[k] = RES_DATA[k]
        pass

    module_name = item._request.node.module.__name__
    class_name = item._request.node.parent.obj.__name__
    function_name = item._request.node.originalname
    all_name = (module_name + class_name + function_name)
    if CONVEY_DICT["loop_name"] == all_name:
        return True
    # 是否使用动态参数化
    is_cus_loop = False
    data_list = list()
    for i in item.own_markers:
        if i.name == "parametrize":
            args_key = i.args[0]
            args_var = i.args[-1]
            if isinstance(args_var, set):
                is_cus_loop = True
                CONVEY_DICT["loop_name"] = all_name
                var_name = list(args_var)[0]
                if var_name.startswith("drt."):
                    data = CONVEY_DICT["gval"].get(var_name[4:]) or None
                else:
                    data = item.module.__dict__.get(var_name, None)
            else:
                data = args_var
            if not isinstance(data, Iterable):
                data = [data]
            data_list.append({args_key: data})
    if is_cus_loop:
        ks = list(map(lambda x: list(x.keys())[0], data_list))
        vals = list(map(lambda x: list(x.values())[0], data_list))
        index_list = cartesian_product_index(vals)
        for loop_data in index_list:
            cloned_item = copy_item(item)
            params_d = dict()
            indices_d = dict()
            for n, it in enumerate(loop_data):
                indices_val = it[0]
                params_val = it[1]
                indices_d.update({ks[n]: indices_val})
                params_d.update({ks[n]: params_val})
            cloned_item.callspec.params.update(params_d)
            cloned_item.callspec.indices.update(indices_d)
            item_funcargs(cloned_item)
            runtestprotocol(cloned_item, nextitem=None)
        return True
    else:
        item_funcargs(item)


def pytest_exception_interact(node, call, report):
    try:
        screen = json.loads(CONVEY_DICT["screen"])
    except Exception:
        screen = None
    if screen:
        drt_fixture_name, ui_fixture_name = screen[0], screen[1]
        drt_fixture = node._request.getfixturevalue(drt_fixture_name)
        if ui_fixture_name in node._fixtureinfo.names_closure:
            png_name = produce_png_name()
            img_path = os.path.join(*drt_fixture.image._dirname, png_name)
            ui_fixture = node.funcargs.get(ui_fixture_name)
            drt_fixture.image.src(os.path.join(drt_fixture.image._dirname[-1], png_name))
            screenshot_str = "ui_fixture." + screen[2].replace("%path%", '"' + img_path +'"' ).replace("\\", "/")
            exec(screenshot_str)


class ddreport:
    def __init__(self):
        self.host = CONVEY_DICT["host"]
        self.gval = CONVEY_DICT["gval"]
        self.mysql = None
        self.pgsql = None
        self.failexit = False
        self.api = DRTHTTP(self.host, CONVEY_DICT["temp_query"])
        self.func = DRTFunctions()
        self.diff = DRTDiff()
        self.image = CONVEY_DICT["imgs"]
        if CONVEY_DICT.get("mysql_config"):
            if "mysql" not in SUMMARY_FROM["db_connect_time"]:
                t1 = time.time()
                self.mysql = DRTMysql(CONVEY_DICT["mysql_config"])
                SUMMARY_FROM["db_connect_time"]["mysql"] = f"{round(time.time() - t1, 2)}s"
        if CONVEY_DICT.get("pgsql_config"):
            if "pgsql" not in SUMMARY_FROM["db_connect_time"]:
                t2 = time.time()
                self.pgsql = DRTPg(CONVEY_DICT["pgsql_config"])
                SUMMARY_FROM["db_connect_time"]["pgsql"] = f"{round(time.time() - t2, 2)}s"
        super().__init__()
