from .exceptd import ExceptInfo
import requests
import traceback
requests.packages.urllib3.disable_warnings()


class RequestObj(object):
    __slots__ = ('__query', '__status_code', '__res_headers', '__res_cookies', '__response', '__res_type')

    def __init__(self):
        self.__query = None
        self.__status_code = None
        self.__res_headers = None
        self.__res_cookies = None
        self.__response = None
        self.__res_type = None

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, value):
        self.__query = value

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, value):
        self.__status_code = value

    @property
    def res_headers(self):
        return self.__res_headers

    @res_headers.setter
    def res_headers(self, value):
        self.__res_headers = value

    @property
    def res_cookies(self):
        return self.__res_cookies

    @res_cookies.setter
    def res_cookies(self, value):
        self.__res_cookies = value

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, value):
        self.__response = value

    @property
    def res_type(self):
        return self.__res_type

    @res_type.setter
    def res_type(self, value):
        self.__res_type = value


class ExceptObj:
    __slots__ = ('__msg_dict')

    def __init__(self):
        self.__msg_dict = None

    @property
    def msg_dict(self):
        return self.__msg_dict

    @msg_dict.setter
    def msg_dict(self, value):
        self.__msg_dict = value


class DRTHTTP:
    def __init__(self, host='', temp_query={}):
        self.__temp_query = temp_query
        self.host = host
        self.headers = dict()
        self.cookies = dict()
        self.verify = None
        self.proxies = None
        self.cert = None

    def __handle_query(self, kwargs):
        encode = kwargs.pop("encode") if "encode" in kwargs else "utf-8"
        if not kwargs['url'].lower().startswith('http'):
            kwargs['url'] = self.host + kwargs['url']
        if kwargs.get("headers"):
            self.headers.update(kwargs.get("headers"))
        if kwargs.get("cookies"):
            self.cookies.update(kwargs.get("cookies"))
        if "verify" in kwargs:
            self.verify = kwargs["verify"]
        else:
            if self.verify is None:
                if kwargs['url'].lower().startswith("https://"):
                    self.verify = False
        if "proxies" in kwargs:
            self.proxies = kwargs["proxies"]
        if "cert" in kwargs:
            self.cert = kwargs["cert"]
        kwargs["headers"] = self.headers
        kwargs["cookies"] = self.cookies
        kwargs["verify"] = self.verify
        kwargs["proxies"] = self.proxies
        kwargs["cert"] = self.cert
        # 过滤没有值的字段
        new_kwargs = {}
        for k, v in kwargs.items():
            if k == "verify" or v:
                new_kwargs[k] = v
        return new_kwargs, encode

    def query(self, method=None, url=None, **kwargs):
        Q = RequestObj()
        E = ExceptObj()
        try:
            if method:
                kwargs["method"] = method
            if url:
                kwargs["url"] = url
            kwargs, encode = self.__handle_query(kwargs)
            Q.query = kwargs.copy()
            Q.status_code = 500
            r = requests.request(**kwargs)
            r.encoding = encode
            status_code = r.status_code
            headers = dict(r.headers)
            cookies = r.cookies.get_dict()
            if cookies:
                self.cookies = self.cookies or {}
                self.cookies.update(cookies)
            try:
                response = r.json()
                Q.res_type = "json"
            except Exception as e:
                response = r.text
                Q.res_type = "text"
            Q.status_code, Q.res_headers, Q.res_cookies, Q.response = status_code, headers, cookies, response
            self.__temp_query["ddquery"] = Q
            return r
        except Exception:
            E.msg_dict = traceback.format_exc()
            ExceptInfo(Q, E).raised()
