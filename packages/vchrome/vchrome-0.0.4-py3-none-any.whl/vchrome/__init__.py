__version__ = '0.0.4'
__author__ = 'v'
# ----------------------------------------------------------------------------------------------------
_allowed = {'Chrome'}
def __getattr__(name):
    if name in _allowed:
        return globals()[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
def __dir__():
    return list(_allowed)
__all__ = __dir__()
import re
import json
import copy
import types
import queue
import time
import inspect
import threading
from time import perf_counter
from math import factorial, sin, pi
from random import random
from collections import deque
import socket
import base64
import traceback
from json import JSONDecodeError
from functools import lru_cache
from threading import Thread, Event, RLock
from urllib import request
import builtins
rl = RLock()
print_hook = False
def monkey_print():
    global print_hook
    if not print_hook:
        _original_print = print
        def thread_safe_print(*args, **kwargs):
            with rl:
                _original_print(*args, **kwargs, flush=True)
        builtins.print = thread_safe_print
    print_hook = True
def cdp_client(hostname, port, debug=False):
    class Logger:
        def _I(self, id):
            return id
        def _L(self, data, key):
            if self.simple:
                return json.dumps(data.get(key),ensure_ascii=False)
            else:
                return json.dumps(data,ensure_ascii=False)
        def _T(self, tp, sessionId=None):
            t = None
            if tp == 'c': t = 'S:{} <->'
            if tp == 'i': t = 'S:{} [*]'
            return t.format(self._I(sessionId or self.id))
        def _C(self, id, msg):
            if self.debug: self.loginfo[id] = msg
        def _G(self, id):
            if self.debug:
                r = self.loginfo.get(id)
                if r: 
                    del self.loginfo[id]
                    return r
                else:
                    return {'msg': 'no cache'}
        def __init__(self, id, debug=False):
            self.id = id
            self.debug = debug
            self.simple = True
            self.loginfo = {}
            self.indent = 44
            if self.debug:
                monkey_print()
        def log(*a):
            print(*a)
        def __call__(self, tp, a):
            if self.debug:
                if tp == 'recv':
                    id = a.get('id')
                    md = a.get('method')
                    se = a.get('sessionId')
                    if id: 
                        c = self._G(id)
                        cse = c.get('sessionId')
                        cmd = c.get('method')
                        if self.debug(cmd):
                            print(self._T('c', cse), '[<={:3}] {}'.format(id, cmd).ljust(self.indent, ' '), self._L(a, 'result'))
                    if md: 
                        if self.debug(md):
                            print(self._T('i', se), (' '*8 + md).ljust(self.indent, ' '), self._L(a, 'params'))
                elif tp == 'req':
                    id = a.get('id')
                    md = a.get('method')
                    se = a.get('sessionId')
                    if self.debug(md):
                        self._C(id, a)
                        print(self._T('c', se), '[->{:3}] {}'.format(id, md).ljust(self.indent, ' '), self._L(a, 'params'))
                else:
                    if self.debug.rest:
                        print(self._T('i'), (' '*8 + tp).ljust(self.indent, ' '), a)
    class Pool:
        import queue, time, traceback
        from threading import Thread, main_thread
        class KillThreadParams(Exception): pass
        def __init__(self, num):
            if not getattr(Pool.Thread, 'isAlive', None):
                Pool.Thread.isAlive = Pool.Thread.is_alive
            self._pool = Pool.queue.Queue()
            self._monitor_run = Pool.queue.Queue()
            self.main_monitor()
            self.num = num
            self.init()
            self.is_close = True
        def __call__(self,func):
            def _run_threads(*args,**kw): 
                if self.is_close:
                    self.init()
                    self.main_monitor()
                self._pool.put((func,args,kw))
            return _run_threads
        def init(self):
            self.is_close = False
            def _pools_pull():
                while True:
                    v = self._pool.get()
                    if v == self.KillThreadParams: return
                    try:
                        func,args,kw = v
                        self._monitor_run.put('V')
                        func(*args,**kw)
                    except BaseException as e:
                        with rl:
                            print(Pool.traceback.format_exc())
                    finally:
                        self._monitor_run.get('V')
            for _ in range(self.num): 
                Pool.Thread(target=_pools_pull).start()
        def main_monitor(self):
            def _func():
                while True:
                    Pool.time.sleep(.12)
                    if not Pool.main_thread().isAlive() and self._monitor_run.empty():
                        self.close_all()
                        self.is_close = True
                        break
            Pool.Thread(target=_func,name="MainMonitor").start()
        def close_all(self):
            for i in range(self.num):
                self._pool.put(self.KillThreadParams)
    @lru_cache(maxsize=1024)
    def get_cached_signature(func):
        return inspect.signature(func)
    def to_human_read(size_in_bytes, decimal_places= 2):
        if size_in_bytes < 0:
            raise ValueError("byte size cannot be negative!")
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        scale = 1024
        if size_in_bytes == 0:
            return f"0 B"
        unit_idx = 0
        while size_in_bytes >= scale and unit_idx < len(units) - 1:
            size_in_bytes /= scale
            unit_idx += 1
        return f"{size_in_bytes:.{decimal_places}f} {units[unit_idx]}"
    def myget(url):
        r = request.Request(url, method='GET')
        opener = request.build_opener(request.ProxyHandler(None))
        return json.loads(opener.open(r).read().decode())
    def adj_wsurl(wsurl): 
        return re.sub('ws://[^/]+/devtools/', 'ws://{}:{}/devtools/'.format(hostname, port), wsurl)
    def make_dev_page_url(id):
        return "ws://{}:{}/devtools/page/{}".format(hostname, port, id)
    def try_run_result(data):
        is_err = False
        try:
            if data['result'].get('type') == 'undefined':
                return None
            elif data['result'].get('subtype') == 'null':
                return None
            elif data['result'].get('value', None) != None:
                return data['result']['value']
            elif data['result'].get('objectId', None) != None:
                return data['result']
            elif data['result'].get('description'):
                is_err = data['result']['description']
            else:
                raise Exception('err')
        except:
            return data
        if is_err:
            raise Exception(is_err)
    def is_function(obj):
        return type(obj) == types.FunctionType or type(obj) == types.MethodType
    def create_connection_saf(*a, **kw):
        for i in range(50):
            try:
                return create_connection(*a, **kw)
            except WebSocketBadStatusException as e:
                if b'No such target id:' in e.resp_body:
                    time.sleep(0.05)
                    continue
                raise Exception('connect ws error')
    class Err: pass
    class Waiter:
        def __init__(self, sniff, pattern, is_regex):
            self.s = sniff
            self.pattern = pattern
            self.is_regex = is_regex
            self.count = 0
            self.currc = 0
            self.cache = deque(maxlen=1024)
            self.is_remove = False
        def add(self, r):
            self.count += 1
            self.cache.appendleft(r)
        def wait(self, count=1, timeout=10):
            if self.is_remove:
                raise Exception('listener remove by waiter, cannot use wait.')
            start = perf_counter()
            while True:
                if self._check(count):
                    return self.cache.pop()
                time.sleep(0.15)
                if perf_counter() - start > timeout:
                    break
        def remove(self):
            f = getattr(self.s, 'remove_listen', None) or getattr(self.s, 'remove_change', None)
            f(self.pattern)
            self.is_remove = True
        def _check(self, count):
            if self.count >= self.currc + count:
                self.currc += count
                return True
            else:
                return False
        def __repr__(self):
            return '<Waiter is_regex:[{}] [{}]>'.format(self.is_regex, json.dumps(self.pattern, ensure_ascii=False))
    class SniffTools:
        def __init__(self, s):
            self.s = s
            self.qlist = queue.Queue()
            self.default_func = lambda a:True
            self.attach()
        def attach(self):
            self.s._match_url = self._match_url
            self.s.qlist = self.qlist
            self.s.default_func = self.default_func
        def _match_str(self, a, b, is_regex):
            if is_regex:
                return re.findall(a, b)
            else:
                return a in b
        def _match_url(self, v, url):
            pattern, is_regex = v
            if type(pattern) == str:
                return self._match_str(pattern, url, is_regex)
            if type(pattern) == list:
                for p in pattern:
                    if self._match_str(p, url, is_regex):
                        return True
                return False
    class SniffNetwork:
        class NetworkRequest:
            def __init__(self, rinfo, encoding='utf8'):
                self.rinfo = rinfo
                self.encoding = encoding
                self._url = rinfo['request'].get('url')
                self._method = rinfo['request'].get('method')
                self._headers = rinfo['request'].get('headers')
                if rinfo['request'].get('hasPostData'):
                    self._content = b''.join(base64.b64decode(e['bytes']) for e in rinfo['request'].get('postDataEntries', []))
            @property
            def url(self): return self._url
            @property
            def method(self): return self._method
            @property
            def headers(self): return self._headers
            @property
            def content(self): 
                assert self.method == 'POST', 'must be method: POST'
                return self._content
            @property
            def text(self): 
                assert self.method == 'POST', 'must be method: POST'
                return self._content.decode(self.encoding)
            def json(self):
                c = self.text
                return json.loads(c[c.find('{'):c.rfind('}')+1])
            def __repr__(self):
                return '<Request [{}] ReadOnly>'.format(self.method)
        class NetworkResponse:
            def __init__(self, rinfo, encoding='utf8'):
                self.rinfo = rinfo
                self.encoding = encoding
                self.error = None
                if rinfo.get('status') == 'ERROR':
                    self.error = rinfo['error']
                    self._request = 'ERROR'
                    self._url = 'ERROR'
                    self._status_code = -1
                    self._headers = {}
                    self._content = b'ERROR'
                    return
                self._request = SniffNetwork.NetworkRequest(rinfo)
                self._url = rinfo['response'].get('url')
                self._status_code = rinfo['response'].get('status')
                self._headers = rinfo['response'].get('headers')
                if rinfo['response_body'].get('base64Encoded'):
                    self._content = base64.b64decode(rinfo['response_body']['body'])
                elif 'body' in rinfo['response_body']:
                    self._content = rinfo['response_body']['body'].encode(self.encoding)
                else:
                    self._content = b'<cannot catch body data. maybe session redirect too fast.>'
            @property
            def url(self): return self._url
            @property
            def status_code(self): return self._status_code
            @property
            def headers(self): return self._headers
            @property
            def content(self): return self._content
            @property
            def text(self): return self._content.decode(self.encoding)
            def json(self):
                c = self.text
                return json.loads(c[c.find('{'):c.rfind('}')+1])
            @property
            def request(self): return self._request
            def __repr__(self):
                if self.error:
                    return '<Response [ERROR] reason:{}>'.format(self.error)
                return '<Response [{}] ReadOnly>'.format(self.status_code)
        def __init__(self, f):
            self.f = f
            self.type = self.f.type
            self.is_listen = False
            self.listen_sesslist = [None]
            self.info_listen = {}
            self.call_listen = {}
            self.call_listen_keys = []
            self.call_listen_vals = {}
            self.tools = SniffTools(self)
        def _listen_cdp(self, sessionId):
            self.f.cdp('Network.enable',{
                "maxTotalBufferSize": 100000000,
                "maxResourceBufferSize":50000000,
                "includeNetworkExtraInfo":True,
            }, sessionId=sessionId)
        def add_listen_session(self, sessionId):
            self.listen_sesslist.append(sessionId)
            if self.is_listen:
                self._listen_cdp(sessionId)
        def remove_listen(self, pattern):
            pk = json.dumps(pattern, sort_keys=True)
            self.call_listen.pop(pk, None)
            self.call_listen_keys = self.call_listen.keys()
            self.call_listen_vals.pop(pk, None)
        def listen(self, pattern, on_response=None, on_request=None, is_regex=False):
            if not self.is_listen:
                self._handle_network()
                for sessionId in self.listen_sesslist:
                    self._listen_cdp(sessionId)
                self.is_listen = True
            waiter = Waiter(self, pattern, is_regex)
            pk = json.dumps(pattern, sort_keys=True)
            if (not on_request) and (not on_response):
                on_response = self.default_func
            self.call_listen[pk] = [waiter, on_request, on_response]
            self.call_listen_keys = self.call_listen.keys()
            self.call_listen_vals[pk] = [pattern, is_regex]
            return waiter
        def _handle_network(self):
            self.f.set_method_callback('Network.requestWillBeSent', self.Network_requestWillBeSent)
            self.f.set_method_callback('Network.requestWillBeSentExtraInfo', self.Network_requestWillBeSentExtraInfo)
            self.f.set_method_callback('Network.responseReceived', self.Network_responseReceived)
            self.f.set_method_callback('Network.responseReceivedExtraInfo', self.Network_responseReceivedExtraInfo)
            self.f.set_method_callback('Network.loadingFinished', self.Network_loadingFinished)
            self.f.set_method_callback('Network.loadingFailed', self.Network_loadingFailed)
        def Network_requestWillBeSent(self, rdata):
            requestId = rdata['params']['requestId']
            self.info_listen[requestId] = self.info_listen.get(requestId, {})
            self.info_listen[requestId]['request'] = rdata['params']['request']
            if self.info_listen[requestId].get('request_extra'):
                request_extra = self.info_listen[requestId].get('request_extra')
                headers = self.info_listen[requestId]['request']['headers']
                self.info_listen[requestId]['request']['headers'] = {**headers, **request_extra['headers']}
                url = self.info_listen[requestId]['request']['url']
                for k in self.call_listen_keys:
                    if self._match_url(self.call_listen_vals[k], url):
                        waiter, on_request, on_response = self.call_listen[k]
                        if on_request:
                            r = SniffNetwork.NetworkRequest(self.info_listen[requestId])
                            if on_request(r):
                                waiter.add(r)
        def Network_requestWillBeSentExtraInfo(self, rdata):
            request_extra = rdata['params']
            requestId = request_extra['requestId']
            if self.info_listen.get(requestId):
                headers = self.info_listen[requestId]['request']['headers']
                self.info_listen[requestId]['request']['headers'] = {**headers, **request_extra['headers']}
                url = self.info_listen[requestId]['request']['url']
                for k in self.call_listen_keys:
                    if self._match_url(self.call_listen_vals[k], url):
                        waiter, on_request, on_response = self.call_listen[k]
                        if on_request:
                            r = SniffNetwork.NetworkRequest(self.info_listen[requestId])
                            if on_request(r):
                                waiter.add(r)
            else:
                self.info_listen[requestId] = {}
                self.info_listen[requestId]['request_extra'] = request_extra
        def Network_responseReceived(self, rdata):
            requestId = rdata['params']['requestId']
            if requestId not in self.info_listen: return
            self.info_listen[requestId]['response'] = rdata['params']['response']
            response_extra = self.info_listen[requestId].pop('response_extra', None)
            if response_extra:
                _headers = self.info_listen[requestId]['response']['headers']
                _headers = {**response_extra['headers'], **_headers}
                self.info_listen[requestId]['response']['headers'] = _headers
        def Network_responseReceivedExtraInfo(self, rdata):
            response_extra = rdata['params']
            requestId = response_extra['requestId']
            if requestId not in self.info_listen: return
            if self.info_listen[requestId].get('response'):
                _headers = self.info_listen[requestId]['response']['headers']
                _headers = {**response_extra['headers'], **_headers}
                self.info_listen[requestId]['response']['headers'] = _headers
            else:
                self.info_listen[requestId]['response_extra'] = response_extra
        def Network_loadingFinished(self, rdata):
            params = rdata['params']
            requestId = params['requestId']
            if requestId not in self.info_listen: return
            url = self.info_listen[requestId]['request']['url']
            for k in self.call_listen_keys:
                if self._match_url(self.call_listen_vals[k], url):
                    waiter, on_request, on_response = self.call_listen[k]
                    if on_response:
                        self.qlist.put('V')
                        rbody = self.f.cdp('Network.getResponseBody', {"requestId": requestId}, sessionId=rdata.get('sessionId'), limit_time=3)
                        self.info_listen[requestId]['response_body'] = rbody
                        r = SniffNetwork.NetworkResponse(self.info_listen[requestId])
                        if on_response(r):
                            waiter.add(r)
                        self.info_listen.pop(requestId, None)
                        self.qlist.get('V')
        def Network_loadingFailed(self, rdata):
            params = rdata['params']
            requestId = params['requestId']
            if requestId not in self.info_listen: return
            url = self.info_listen[requestId]['request']['url']
            self.info_listen[requestId]['status'] = 'ERROR'
            self.info_listen[requestId]['error'] = params['errorText']
            for k in self.call_listen_keys:
                if self._match_url(self.call_listen_vals[k], url):
                    waiter, on_request, on_response = self.call_listen[k]
                    if on_response:
                        self.qlist.put('V')
                        r = SniffNetwork.NetworkResponse(self.info_listen[requestId])
                        if on_response(r):
                            waiter.add(r)
                        self.qlist.get('V')
    class SniffFetch:
        class FetchFakeResponse:
            def __init__(self, rinfo, encoding='utf8'):
                self.rinfo = rinfo
                self.encoding = encoding
                self._url = rinfo.get('url')
                self._responseCode = 200
                self._responseHeaders = {"fake-vvv": "fake-vvv"}
                self._body = b''
                self.request = rinfo.get('request')
            @property
            def url(self): return self._url
            @property
            def status_code(self): return self._responseCode
            @status_code.setter
            def status_code(self, value): assert isinstance(value, int), 'must be type: int'; self._responseCode = value
            @property
            def headers(self): return self._responseHeaders
            @headers.setter
            def headers(self, value): assert isinstance(value, dict), 'must be type: dict'; self._responseHeaders = value
            @property
            def content(self): return self._body
            @content.setter
            def content(self, value): assert isinstance(value, bytes), 'must be type: bytes'; self._body = value
            @property
            def text(self): return self._body.decode(self.encoding)
            @text.setter
            def text(self, value): assert isinstance(value, str), 'must be type: str'; self._body = value.encode(self.encoding)
            def json(self):
                c = self.text
                return json.loads(c[c.find('{'):c.rfind('}')+1])
            def __repr__(self): return '<FakeResponse [{}]>'.format(self.status_code)
            def get(self, k):
                return getattr(self, '_'+k, None)
        class FetchRequest:
            def __init__(self, rinfo, encoding='utf8'):
                self.rinfo = rinfo
                self.encoding = encoding
                self._url = rinfo.get('url')
                self._url_copy = self._url
                self._method = rinfo.get('method')
                self._method_copy = self._method
                self._headers = rinfo.get('headers')
                self._headers_copy = copy.deepcopy(self._headers)
                self._postData = rinfo.get('postData')
                self._postData_copy = self._postData
                self._fake = None
            @property
            def url(self): return self._url
            @property
            def method(self): return self._method
            @method.setter
            def method(self, value): assert isinstance(value, str), 'must be type: str'; self._method = value
            @property
            def headers(self): return self._headers
            @headers.setter
            def headers(self, value): assert isinstance(value, dict), 'must be type: dict'; self._headers = value
            @property
            def content(self): return self._postData
            @content.setter
            def content(self, value): assert isinstance(value, bytes), 'must be type: bytes'; self._postData = value
            @property
            def text(self): return self._postData.decode(self.encoding)
            @text.setter
            def text(self, value): assert isinstance(value, str), 'must be type: str'; self._postData = value.encode(self.encoding)
            def json(self):
                c = self.text
                return json.loads(c[c.find('{'):c.rfind('}')+1])
            def __repr__(self): return '<Request [{}]>'.format(self.method)
            def check_change(self):
                return (
                    self._url != self._url_copy
                    or self._method != self._method_copy
                    or self._headers != self._headers_copy
                    or json.dumps(self._headers, sort_keys=True) != json.dumps(self._headers_copy, sort_keys=True) 
                    or (self._method == 'POST' and self._postData != self._postData_copy)
                )
            def get(self, k):
                return getattr(self, '_'+k, None)
            def fake_response(self):
                self._fake = SniffFetch.FetchFakeResponse({"url": self._url, "request": self})
                return self._fake
        class FetchResponse:
            def __init__(self, rinfo, encoding='utf8'):
                self.rinfo = rinfo
                self.encoding = encoding
                self.error = None
                self.request = rinfo.get('request')
                self._url = rinfo.get('url')
                self._url_copy = self._url
                self._responseCode = rinfo.get('responseCode')
                self._responseCode_copy = self._responseCode
                self._responseHeaders = rinfo.get('responseHeaders')
                self._responseHeaders_copy = copy.deepcopy(self._responseHeaders)
                self._body = rinfo.get('body')
                self._body_copy = self._body
            @property
            def url(self): return self._url
            @property
            def status_code(self): return self._responseCode
            @status_code.setter
            def status_code(self, value): assert isinstance(value, int), 'must be type: int'; self._responseCode = value
            @property
            def headers(self): return self._responseHeaders
            @headers.setter
            def headers(self, value): assert isinstance(value, dict), 'must be type: dict'; self._responseHeaders = value
            @property
            def content(self): return self._body
            @content.setter
            def content(self, value): assert isinstance(value, bytes), 'must be type: bytes'; self._body = value
            @property
            def text(self): return self._body.decode(self.encoding)
            @text.setter
            def text(self, value): assert isinstance(value, str), 'must be type: str'; self._body = value.encode(self.encoding)
            def json(self):
                c = self.text
                return json.loads(c[c.find('{'):c.rfind('}')+1])
            def __repr__(self): return '<Response [{}]>'.format(self.status_code)
            def check_change(self):
                return (
                    self._url != self._url_copy
                    or self._responseCode != self._responseCode_copy
                    or self._responseHeaders != self._responseHeaders_copy
                    or json.dumps(self._responseHeaders, sort_keys=True) != json.dumps(self._responseHeaders_copy, sort_keys=True) 
                    or self._body_copy != self._body
                )
            def get(self, k):
                return getattr(self, '_'+k, None)
        def __init__(self, f):
            self.f = f
            self.type = self.f.type
            self.is_change = False
            self.change_sesslist = [None]
            self.info_change = {}
            self.call_change = {}
            self.call_change_keys = []
            self.call_change_vals = {}
            self.tools = SniffTools(self)
        def _change_cdp(self, sessionId):
            self.f.cdp('Fetch.enable',{
                "handleAuthRequests": True,
                "patterns":[
                    {"urlPattern":"*","requestStage":"Request"},
                    {"urlPattern":"*","requestStage":"Response"},
            ]}, sessionId=sessionId)
        def add_change_session(self, sessionId):
            self.change_sesslist.append(sessionId)
            if self.is_change:
                self._change_cdp(sessionId)
        def remove_change(self, pattern):
            pk = json.dumps(pattern, sort_keys=True)
            self.call_change.pop(pk, None)
            self.call_change_keys = self.call_change.keys()
            self.call_change_vals.pop(pk, None)
        def intercept(self, pattern, on_response=None, on_request=None, is_regex=False):
            if not self.is_change:
                self._handle_fetch()
                for sessionId in self.change_sesslist:
                    self._change_cdp(sessionId)
                self.is_change = True
            waiter = Waiter(self, pattern, is_regex)
            pk = json.dumps(pattern, sort_keys=True)
            if (not on_request) and (not on_response):
                on_response = self.default_func
            self.call_change[pk] = [waiter, on_request, on_response]
            self.call_change_keys = self.call_change.keys()
            self.call_change_vals[pk] = [pattern, is_regex]
            return waiter
        def _handle_fetch(self):
            self.f.set_method_callback('Fetch.requestPaused', self.Fetch_requestPaused)
        def _dict_to_list(self, headers_dict):
            return [{"name": k, "value": v} for k, v in headers_dict.items()]
        def _list_to_dict(self, headers_list):
            d = {}
            for kv in headers_list:
                d[kv['name']] = kv['value']
            return d
        def Fetch_requestPaused(self, rdata):
            url = rdata['params']['request']['url']
            method = rdata['params']['request']['method']
            requestId = rdata['params']['requestId']
            if "responseStatusCode" not in rdata['params']:
                for k in self.call_change_keys:
                    if self._match_url(self.call_change_vals[k], url):
                        waiter, on_request, on_response = self.call_change[k]
                        x = SniffFetch.FetchRequest({
                            "url": url,
                            "method": method,
                            "headers": rdata['params']['request']['headers'],
                            "postData": b''.join(base64.b64decode(e['bytes']) for e in rdata['params']['request'].get('postDataEntries', [])),
                        })
                        if on_request:
                            try:
                                if on_request(x):
                                    waiter.add(x)
                            except:
                                self.f.logger.log('[ERROR] in request on_request', traceback.format_exc())
                                continue
                            try:
                                if x._fake:
                                    fk = x._fake
                                    d = {
                                        "requestId": requestId,
                                        "responseCode": fk.get('responseCode'),
                                        "responseHeaders": self._dict_to_list(fk.get('responseHeaders')),
                                        "body": base64.b64encode(fk.get('body')).decode("ascii")
                                    }
                                    self.f.cdp('Fetch.fulfillRequest', d, sessionId=rdata.get('sessionId'))
                                    return
                            except:
                                self.f.logger.log('[ERROR] in request on_fake continue', traceback.format_exc())
                            try:
                                if x.check_change():
                                    d = {
                                        "requestId": requestId,
                                        "method": x.get('method') or method,
                                        "headers": self._dict_to_list(x.get('headers') or rdata['params']['request']['headers']),
                                    }
                                    if x.get('method') == 'POST':
                                        d['postData'] = base64.b64encode(x.get('postData')).decode("ascii")
                                    self.f.cdp('Fetch.continueRequest', d, sessionId=rdata.get('sessionId'))
                                    return
                            except:
                                self.f.logger.log('[ERROR] in request on_request continue', traceback.format_exc())
                self.f.cdp('Fetch.continueRequest', {'requestId': requestId}, sessionId=rdata.get('sessionId'))
            else:
                for k in self.call_change_keys:
                    if self._match_url(self.call_change_vals[k], url):
                        waiter, on_request, on_response = self.call_change[k]
                        if on_response:
                            body_info = self.f.cdp("Fetch.getResponseBody", {"requestId": requestId}, sessionId=rdata.get('sessionId'))
                            body = base64.b64decode(body_info["body"]) if body_info['base64Encoded'] else body_info["body"].encode()
                            x = SniffFetch.FetchResponse({
                                "url": url,
                                "responseCode": rdata['params']['responseStatusCode'],
                                "responseHeaders": self._list_to_dict(rdata['params']['responseHeaders']),
                                "body": body,
                                "request": SniffFetch.FetchRequest(rdata['params']['request'])
                            })
                            try:
                                if on_response(x):
                                    waiter.add(x)
                            except:
                                self.f.logger.log('[ERROR] in response on_response', traceback.format_exc())
                                continue
                            try:
                                if x.check_change():
                                    d = {
                                        "requestId": requestId,
                                        "responseCode": x.get('responseCode'),
                                        "responseHeaders": self._dict_to_list(x.get('responseHeaders')),
                                        "body": base64.b64encode(x.get('body') or body).decode("ascii")
                                    }
                                    self.f.cdp('Fetch.fulfillRequest', d, sessionId=rdata.get('sessionId'))
                                    return
                            except Exception as e:
                                self.f.logger.log('[ERROR] in response on_response continue', traceback.format_exc())
                self.f.cdp('Fetch.continueResponse', {'requestId': requestId}, sessionId=rdata.get('sessionId'))
    class Page:
        def __init__(self, f):
            self.f = f
            self.f.set_method_callback('Page.frameDetached', self.Page_frameDetached)
            self.f.set_method_callback('Page.frameAttached', self.Page_frameAttached)
            self.f.set_method_callback('Page.frameScheduledNavigation', self.Page_frameScheduledNavigation)
            self.f.set_method_callback('Page.frameRequestedNavigation', self.Page_frameRequestedNavigation)
            self.f.set_method_callback('Page.frameStartedNavigating', self.Page_frameStartedNavigating)
            self.f.set_method_callback('Page.frameStartedLoading', self.Page_frameStartedLoading)
            self.f.set_method_callback('Page.frameNavigated', self.Page_frameNavigated)
            self.f.set_method_callback('Page.javascriptDialogOpening', self.Page_javascriptDialogOpening)
            self.f.set_method_callback('Page.javascriptDialogClosed', self.Page_javascriptDialogClosed)
            self.init()
            self.dialog = None
        def init(self, sessionId=None):
            self.f.cdp('Page.enable', sessionId=sessionId)
        def Page_frameNavigated(self, rdata):
            frameId = rdata['params']['frame']['id']
            f = self.f.root.trav_frame(frameId)
            if f:
                f.url = rdata['params']['frame']['url']
                f.iso_contextId = None
        def Page_frameDetached(self, rdata):
            frameId = rdata['params']['frameId']
            f = self.f.root.trav_frame(frameId)
            if f and rdata['params']['reason'] == 'remove':
                f.parent.frames.remove(f)
                f.iso_contextId = None
        def Page_frameAttached(self, rdata):
            frameId = rdata['params'].get('frameId')
            parentFrameId = rdata['params'].get('parentFrameId')
            pf = self.f.root.trav_frame(parentFrameId)
            if not self.f.root.trav_frame(frameId) and pf:
                self.f.root.add_common_frame(self.f, {
                    "frameId": frameId,
                    "parent": pf,
                })
        def _clear_iso(self, rdata):  
            frameId = rdata['params']['frameId']  
            f = self.f.root.trav_frame(frameId)  
            if f and rdata['params']['reason'] in (  
                'anchorClick', 'formSubmissionGet', 'formSubmissionPost', 'httpHeaderRefresh',   
                'initialFrameNavigation', 'metaTagRefresh', 'other', 'pageBlockInterstitial',   
                'reload', 'scriptInitiated'):  
                f.iso_contextId = None
        def Page_frameScheduledNavigation(self, rdata): self._clear_iso(rdata)
        def Page_frameRequestedNavigation(self, rdata): self._clear_iso(rdata)
        def Page_frameStartedNavigating(self, rdata): pass
        def Page_frameStartedLoading(self, rdata): pass
        def Page_javascriptDialogOpening(self, rdata):
            if self.dialog:
                r = self.dialog(rdata['params'])
                if type(r) == dict:
                    self.f.cdp('Page.handleJavaScriptDialog', {"accept": r.get('accept'), "promptText": r.get('promptText') or r.get('text')})
                if type(r) in (list, tuple) and len(r) == 2 and type(r[0]) == bool and type(r[1]) == str:
                    self.f.cdp('Page.handleJavaScriptDialog', {"accept": r[0], "promptText": r[1]})
                else:
                    self.f.cdp('Page.handleJavaScriptDialog', {"accept": bool(r)})
            else:
                time.sleep(0.5)
                self.f.cdp('Page.handleJavaScriptDialog', {"accept": True})
        def Page_javascriptDialogClosed(self, rdata):
            pass
    class Target:
        def __init__(self, f):
            self.f = f
            self.f.set_method_callback('Target.attachedToTarget', self.Target_attachedToTarget)
            self.f.set_method_callback('Target.targetDestroyed', self.Target_targetDestroyed)
            self.f.set_method_callback('Target.targetCreated', self.Target_targetCreated)
            self.f.set_method_callback('Target.targetInfoChanged', self.Target_targetInfoChanged)
            self.f.set_method_callback('Target.detachedFromTarget', self.Target_detachedFromTarget)
            self.init()
        def init(self, sessionId=None):
            self.f.cdp("Target.setAutoAttach", {
                "autoAttach": True,  
                "waitForDebuggerOnStart": True,  
                "flatten": True,
            }, sessionId=sessionId)
        def Target_attachedToTarget(self, rdata):
            self.f.root._add_init_check()
            tinfo = rdata['params']['targetInfo']
            if tinfo['url'].startswith('chrome-extension'):
                self.f.root._del_init_check()
                return
            if self.f.root.filter_extension(tinfo): 
                self.f.root._del_init_check()
                return
            if rdata['params'].get('targetInfo', {}).get('type') == 'service_worker':
                self.f.root._del_init_check()
                return
            # TODO 
            # need to be compatible with workers in the future
            if rdata['params'].get('targetInfo', {}).get('type') == 'worker':
                # and rdata['params'].get('targetInfo', {}).get('title', '').startswith('blob'):
                self.f.root._del_init_check()
                return
            frameId = tinfo['targetId']
            sessionId = rdata['params']['sessionId']
            # self.f.cdp("Target.setAutoAttach", {
            #     "autoAttach": True,  
            #     "waitForDebuggerOnStart": True,  
            #     "flatten": True,
            # }, sessionId=sessionId)
            self.f.cdp('DOM.enable', sessionId=sessionId)
            self.f.cdp('Page.enable', sessionId=sessionId)
            self.f.cdp('Runtime.enable', sessionId=sessionId)
            self.f.add_sniff_session(sessionId)
            self.f.cache.add_cache_session(sessionId)
            self.f.root.add_common_frame(self.f, {
                "frameId": frameId,
                "sessionId": sessionId,
            })
            if self.f.root.is_init and sessionId:
                f = self.f.root.trav_frame(sessionId, 'sessionId')
                if f:
                    self.f.root.trav_init_tree(f, self.f, sessionId)
                else:
                    # TODO
                    # manager worker process.
                    # some worker not work in iframe.
                    pass
            self.f._page_init_js(sessionId=sessionId)
            self.f.cdp('Runtime.runIfWaitingForDebugger', sessionId=sessionId)
            self.f.root._del_init_check()
        def Target_detachedFromTarget(self, rdata):
            sessionId = rdata['params']['sessionId']
            pass
        def Target_targetCreated(self, rdata):
            pass
        def Target_targetInfoChanged(self, rdata):
            pass
        def Target_targetDestroyed(self, rdata):
            self.f.cdp('Target.closeTarget', {'targetId': rdata['params']['targetId']})
    class JSIterator:
        def __init__(self, jsobj):
            self.idx = 0
            self.jsobj = jsobj
            self.leng = len(self.jsobj)
        def __next__(self):
            if self.idx < self.leng:
                value = self.jsobj[self.idx]
                self.idx += 1
                return value
            else:
                raise StopIteration
    class JSObject:
        def __init__(self, f, einfo, _this=None, iso=False):
            self.f = f
            self.className = einfo.get('className')
            self.objectId = einfo.get('objectId')
            self._this = _this
            self.iso = iso
            self.r_obj = self.f.run_iso_js_obj if self.iso else self.f.run_js_obj
        def __getitem__(self, a):
            einfo = self.r_obj('function(){return this[' + json.dumps(a) + ']}', objectId=self.objectId, returnByValue=False)
            return self.f._parse_js2py(einfo, self, iso=self.iso)
        def __setitem__(self, a, b):
            args = [None,self.f._parse_2arg(a), self.f._parse_2arg(b)]
            einfo = self.r_obj('function(a,b){return this[a]=b}', objectId=self.objectId, arguments=args, returnByValue=False)
            return self.f._parse_js2py(einfo, iso=self.iso)
        def __call__(self, *a):
            args = [self._this]
            for v in a: args.append(self.f._parse_2arg(v))
            scpt = 'function(o,...a){return this.call(o,...a)}' if self._this else 'function(...a){return this(...a)}'
            einfo = self.r_obj(scpt, objectId=self.objectId, arguments=args, returnByValue=False)
            return self.f._parse_js2py(einfo, iso=self.iso)
        def __repr__(self):
            return '<OBJ:[{}] [{}]>'.format(self.className, self.objectId)
        def __add__(self, other):
            args = [None,self.f._parse_2arg(other)]
            einfo = self.r_obj('function(other){return this+other}', objectId=self.objectId, arguments=args, returnByValue=False)
            return self.f._parse_js2py(einfo, iso=self.iso)
        def __iter__(self): return JSIterator(self)
        def __len__(self): return self['length']
        def __bool__(self): return True
        def json(self): return self.r_obj('function(){return this}', objectId=self.objectId, returnByValue=True)
    class Keyboard:
        # from pyppeteer
        def __init__(self, f):
            self.f = f
            self._key_maps = {'0': {'keyCode': 48, 'key': '0', 'code': 'Digit0'},'1': {'keyCode': 49, 'key': '1', 'code': 'Digit1'},'2': {'keyCode': 50, 'key': '2', 'code': 'Digit2'},'3': {'keyCode': 51, 'key': '3', 'code': 'Digit3'},'4': {'keyCode': 52, 'key': '4', 'code': 'Digit4'},'5': {'keyCode': 53, 'key': '5', 'code': 'Digit5'},'6': {'keyCode': 54, 'key': '6', 'code': 'Digit6'},'7': {'keyCode': 55, 'key': '7', 'code': 'Digit7'},'8': {'keyCode': 56, 'key': '8', 'code': 'Digit8'},'9': {'keyCode': 57, 'key': '9', 'code': 'Digit9'},'Power': {'key': 'Power', 'code': 'Power'},'Eject': {'key': 'Eject', 'code': 'Eject'},'Abort': {'keyCode': 3, 'code': 'Abort', 'key': 'Cancel'},'Help': {'keyCode': 6, 'code': 'Help', 'key': 'Help'},'Backspace': {'keyCode': 8, 'code': 'Backspace', 'key': 'Backspace'},'Tab': {'keyCode': 9, 'code': 'Tab', 'key': 'Tab'},'Numpad5': {'keyCode': 12, 'shiftKeyCode': 101, 'key': 'Clear', 'code': 'Numpad5', 'shiftKey': '5', 'location': 3},'NumpadEnter': {'keyCode': 13, 'code': 'NumpadEnter', 'key': 'Enter', 'text': '\r', 'location': 3},'Enter': {'keyCode': 13, 'code': 'Enter', 'key': 'Enter', 'text': '\r'},'\r': {'keyCode': 13, 'code': 'Enter', 'key': 'Enter', 'text': '\r'},'\n': {'keyCode': 13, 'code': 'Enter', 'key': 'Enter', 'text': '\r'},'ShiftLeft': {'keyCode': 16, 'code': 'ShiftLeft', 'key': 'Shift', 'location': 1},'ShiftRight': {'keyCode': 16, 'code': 'ShiftRight', 'key': 'Shift', 'location': 2},'ControlLeft': {'keyCode': 17, 'code': 'ControlLeft', 'key': 'Control', 'location': 1},'ControlRight': {'keyCode': 17, 'code': 'ControlRight', 'key': 'Control', 'location': 2},'AltLeft': {'keyCode': 18, 'code': 'AltLeft', 'key': 'Alt', 'location': 1},'AltRight': {'keyCode': 18, 'code': 'AltRight', 'key': 'Alt', 'location': 2},'Pause': {'keyCode': 19, 'code': 'Pause', 'key': 'Pause'},'CapsLock': {'keyCode': 20, 'code': 'CapsLock', 'key': 'CapsLock'},'Escape': {'keyCode': 27, 'code': 'Escape', 'key': 'Escape'},'Convert': {'keyCode': 28, 'code': 'Convert', 'key': 'Convert'},'NonConvert': {'keyCode': 29, 'code': 'NonConvert', 'key': 'NonConvert'},'Space': {'keyCode': 32, 'code': 'Space', 'key': ' '},'Numpad9': {'keyCode': 33, 'shiftKeyCode': 105, 'key': 'PageUp', 'code': 'Numpad9', 'shiftKey': '9', 'location': 3},'PageUp': {'keyCode': 33, 'code': 'PageUp', 'key': 'PageUp'},'Numpad3': {'keyCode': 34, 'shiftKeyCode': 99, 'key': 'PageDown', 'code': 'Numpad3', 'shiftKey': '3', 'location': 3},'PageDown': {'keyCode': 34, 'code': 'PageDown', 'key': 'PageDown'},'End': {'keyCode': 35, 'code': 'End', 'key': 'End'},'Numpad1': {'keyCode': 35, 'shiftKeyCode': 97, 'key': 'End', 'code': 'Numpad1', 'shiftKey': '1', 'location': 3},'Home': {'keyCode': 36, 'code': 'Home', 'key': 'Home'},'Numpad7': {'keyCode': 36, 'shiftKeyCode': 103, 'key': 'Home', 'code': 'Numpad7', 'shiftKey': '7', 'location': 3},'ArrowLeft': {'keyCode': 37, 'code': 'ArrowLeft', 'key': 'ArrowLeft'},'Numpad4': {'keyCode': 37, 'shiftKeyCode': 100, 'key': 'ArrowLeft', 'code': 'Numpad4', 'shiftKey': '4', 'location': 3},'Numpad8': {'keyCode': 38, 'shiftKeyCode': 104, 'key': 'ArrowUp', 'code': 'Numpad8', 'shiftKey': '8', 'location': 3},'ArrowUp': {'keyCode': 38, 'code': 'ArrowUp', 'key': 'ArrowUp'},'ArrowRight': {'keyCode': 39, 'code': 'ArrowRight', 'key': 'ArrowRight'},'Numpad6': {'keyCode': 39, 'shiftKeyCode': 102, 'key': 'ArrowRight', 'code': 'Numpad6', 'shiftKey': '6', 'location': 3},'Numpad2': {'keyCode': 40, 'shiftKeyCode': 98, 'key': 'ArrowDown', 'code': 'Numpad2', 'shiftKey': '2', 'location': 3},'ArrowDown': {'keyCode': 40, 'code': 'ArrowDown', 'key': 'ArrowDown'},'Select': {'keyCode': 41, 'code': 'Select', 'key': 'Select'},'Open': {'keyCode': 43, 'code': 'Open', 'key': 'Execute'},'PrintScreen': {'keyCode': 44, 'code': 'PrintScreen', 'key': 'PrintScreen'},'Insert': {'keyCode': 45, 'code': 'Insert', 'key': 'Insert'},'Numpad0': {'keyCode': 45, 'shiftKeyCode': 96, 'key': 'Insert', 'code': 'Numpad0', 'shiftKey': '0', 'location': 3},'Delete': {'keyCode': 46, 'code': 'Delete', 'key': 'Delete'},'NumpadDecimal': {'keyCode': 46, 'shiftKeyCode': 110, 'code': 'NumpadDecimal', 'key': '\u0000', 'shiftKey': '.', 'location': 3},'Digit0': {'keyCode': 48, 'code': 'Digit0', 'shiftKey': ')', 'key': '0'},'Digit1': {'keyCode': 49, 'code': 'Digit1', 'shiftKey': '!', 'key': '1'},'Digit2': {'keyCode': 50, 'code': 'Digit2', 'shiftKey': '@', 'key': '2'},'Digit3': {'keyCode': 51, 'code': 'Digit3', 'shiftKey': '#', 'key': '3'},'Digit4': {'keyCode': 52, 'code': 'Digit4', 'shiftKey': '$', 'key': '4'},'Digit5': {'keyCode': 53, 'code': 'Digit5', 'shiftKey': '%', 'key': '5'},'Digit6': {'keyCode': 54, 'code': 'Digit6', 'shiftKey': '^', 'key': '6'},'Digit7': {'keyCode': 55, 'code': 'Digit7', 'shiftKey': '&', 'key': '7'},'Digit8': {'keyCode': 56, 'code': 'Digit8', 'shiftKey': '*', 'key': '8'},'Digit9': {'keyCode': 57, 'code': 'Digit9', 'shiftKey': '(', 'key': '9'},'KeyA': {'keyCode': 65, 'code': 'KeyA', 'shiftKey': 'A', 'key': 'a'},'KeyB': {'keyCode': 66, 'code': 'KeyB', 'shiftKey': 'B', 'key': 'b'},'KeyC': {'keyCode': 67, 'code': 'KeyC', 'shiftKey': 'C', 'key': 'c'},'KeyD': {'keyCode': 68, 'code': 'KeyD', 'shiftKey': 'D', 'key': 'd'},'KeyE': {'keyCode': 69, 'code': 'KeyE', 'shiftKey': 'E', 'key': 'e'},'KeyF': {'keyCode': 70, 'code': 'KeyF', 'shiftKey': 'F', 'key': 'f'},'KeyG': {'keyCode': 71, 'code': 'KeyG', 'shiftKey': 'G', 'key': 'g'},'KeyH': {'keyCode': 72, 'code': 'KeyH', 'shiftKey': 'H', 'key': 'h'},'KeyI': {'keyCode': 73, 'code': 'KeyI', 'shiftKey': 'I', 'key': 'i'},'KeyJ': {'keyCode': 74, 'code': 'KeyJ', 'shiftKey': 'J', 'key': 'j'},'KeyK': {'keyCode': 75, 'code': 'KeyK', 'shiftKey': 'K', 'key': 'k'},'KeyL': {'keyCode': 76, 'code': 'KeyL', 'shiftKey': 'L', 'key': 'l'},'KeyM': {'keyCode': 77, 'code': 'KeyM', 'shiftKey': 'M', 'key': 'm'},'KeyN': {'keyCode': 78, 'code': 'KeyN', 'shiftKey': 'N', 'key': 'n'},'KeyO': {'keyCode': 79, 'code': 'KeyO', 'shiftKey': 'O', 'key': 'o'},'KeyP': {'keyCode': 80, 'code': 'KeyP', 'shiftKey': 'P', 'key': 'p'},'KeyQ': {'keyCode': 81, 'code': 'KeyQ', 'shiftKey': 'Q', 'key': 'q'},'KeyR': {'keyCode': 82, 'code': 'KeyR', 'shiftKey': 'R', 'key': 'r'},'KeyS': {'keyCode': 83, 'code': 'KeyS', 'shiftKey': 'S', 'key': 's'},'KeyT': {'keyCode': 84, 'code': 'KeyT', 'shiftKey': 'T', 'key': 't'},'KeyU': {'keyCode': 85, 'code': 'KeyU', 'shiftKey': 'U', 'key': 'u'},'KeyV': {'keyCode': 86, 'code': 'KeyV', 'shiftKey': 'V', 'key': 'v'},'KeyW': {'keyCode': 87, 'code': 'KeyW', 'shiftKey': 'W', 'key': 'w'},'KeyX': {'keyCode': 88, 'code': 'KeyX', 'shiftKey': 'X', 'key': 'x'},'KeyY': {'keyCode': 89, 'code': 'KeyY', 'shiftKey': 'Y', 'key': 'y'},'KeyZ': {'keyCode': 90, 'code': 'KeyZ', 'shiftKey': 'Z', 'key': 'z'},'MetaLeft': {'keyCode': 91, 'code': 'MetaLeft', 'key': 'Meta'},'MetaRight': {'keyCode': 92, 'code': 'MetaRight', 'key': 'Meta'},'ContextMenu': {'keyCode': 93, 'code': 'ContextMenu', 'key': 'ContextMenu'},'NumpadMultiply': {'keyCode': 106, 'code': 'NumpadMultiply', 'key': '*', 'location': 3},'NumpadAdd': {'keyCode': 107, 'code': 'NumpadAdd', 'key': '+', 'location': 3},'NumpadSubtract': {'keyCode': 109, 'code': 'NumpadSubtract', 'key': '-', 'location': 3},'NumpadDivide': {'keyCode': 111, 'code': 'NumpadDivide', 'key': '/', 'location': 3},'F1': {'keyCode': 112, 'code': 'F1', 'key': 'F1'},'F2': {'keyCode': 113, 'code': 'F2', 'key': 'F2'},'F3': {'keyCode': 114, 'code': 'F3', 'key': 'F3'},'F4': {'keyCode': 115, 'code': 'F4', 'key': 'F4'},'F5': {'keyCode': 116, 'code': 'F5', 'key': 'F5'},'F6': {'keyCode': 117, 'code': 'F6', 'key': 'F6'},'F7': {'keyCode': 118, 'code': 'F7', 'key': 'F7'},'F8': {'keyCode': 119, 'code': 'F8', 'key': 'F8'},'F9': {'keyCode': 120, 'code': 'F9', 'key': 'F9'},'F10': {'keyCode': 121, 'code': 'F10', 'key': 'F10'},'F11': {'keyCode': 122, 'code': 'F11', 'key': 'F11'},'F12': {'keyCode': 123, 'code': 'F12', 'key': 'F12'},'F13': {'keyCode': 124, 'code': 'F13', 'key': 'F13'},'F14': {'keyCode': 125, 'code': 'F14', 'key': 'F14'},'F15': {'keyCode': 126, 'code': 'F15', 'key': 'F15'},'F16': {'keyCode': 127, 'code': 'F16', 'key': 'F16'},'F17': {'keyCode': 128, 'code': 'F17', 'key': 'F17'},'F18': {'keyCode': 129, 'code': 'F18', 'key': 'F18'},'F19': {'keyCode': 130, 'code': 'F19', 'key': 'F19'},'F20': {'keyCode': 131, 'code': 'F20', 'key': 'F20'},'F21': {'keyCode': 132, 'code': 'F21', 'key': 'F21'},'F22': {'keyCode': 133, 'code': 'F22', 'key': 'F22'},'F23': {'keyCode': 134, 'code': 'F23', 'key': 'F23'},'F24': {'keyCode': 135, 'code': 'F24', 'key': 'F24'},'NumLock': {'keyCode': 144, 'code': 'NumLock', 'key': 'NumLock'},'ScrollLock': {'keyCode': 145, 'code': 'ScrollLock', 'key': 'ScrollLock'},'AudioVolumeMute': {'keyCode': 173, 'code': 'AudioVolumeMute', 'key': 'AudioVolumeMute'},'AudioVolumeDown': {'keyCode': 174, 'code': 'AudioVolumeDown', 'key': 'AudioVolumeDown'},'AudioVolumeUp': {'keyCode': 175, 'code': 'AudioVolumeUp', 'key': 'AudioVolumeUp'},'MediaTrackNext': {'keyCode': 176, 'code': 'MediaTrackNext', 'key': 'MediaTrackNext'},'MediaTrackPrevious': {'keyCode': 177, 'code': 'MediaTrackPrevious', 'key': 'MediaTrackPrevious'},'MediaStop': {'keyCode': 178, 'code': 'MediaStop', 'key': 'MediaStop'},'MediaPlayPause': {'keyCode': 179, 'code': 'MediaPlayPause', 'key': 'MediaPlayPause'},'Semicolon': {'keyCode': 186, 'code': 'Semicolon', 'shiftKey': ':', 'key': ';'},'Equal': {'keyCode': 187, 'code': 'Equal', 'shiftKey': '+', 'key': '='},'NumpadEqual': {'keyCode': 187, 'code': 'NumpadEqual', 'key': '=', 'location': 3},'Comma': {'keyCode': 188, 'code': 'Comma', 'shiftKey': '<', 'key': ','},'Minus': {'keyCode': 189, 'code': 'Minus', 'shiftKey': '_', 'key': '-'},'Period': {'keyCode': 190, 'code': 'Period', 'shiftKey': '>', 'key': '.'},'Slash': {'keyCode': 191, 'code': 'Slash', 'shiftKey': '?', 'key': '/'},'Backquote': {'keyCode': 192, 'code': 'Backquote', 'shiftKey': '~', 'key': '`'},'BracketLeft': {'keyCode': 219, 'code': 'BracketLeft', 'shiftKey': '{', 'key': '['},'Backslash': {'keyCode': 220, 'code': 'Backslash', 'shiftKey': '|', 'key': '\\'},'BracketRight': {'keyCode': 221, 'code': 'BracketRight', 'shiftKey': '}', 'key': ']'},'Quote': {'keyCode': 222, 'code': 'Quote', 'shiftKey': '"', 'key': '\''},'AltGraph': {'keyCode': 225, 'code': 'AltGraph', 'key': 'AltGraph'},'Props': {'keyCode': 247, 'code': 'Props', 'key': 'CrSel'},'Cancel': {'keyCode': 3, 'key': 'Cancel', 'code': 'Abort'},'Clear': {'keyCode': 12, 'key': 'Clear', 'code': 'Numpad5', 'location': 3},'Shift': {'keyCode': 16, 'key': 'Shift', 'code': 'ShiftLeft'},'Control': {'keyCode': 17, 'key': 'Control', 'code': 'ControlLeft'},'Alt': {'keyCode': 18, 'key': 'Alt', 'code': 'AltLeft'},'Accept': {'keyCode': 30, 'key': 'Accept'},'ModeChange': {'keyCode': 31, 'key': 'ModeChange'},' ': {'keyCode': 32, 'key': ' ', 'code': 'Space'},'Print': {'keyCode': 42, 'key': 'Print'},'Execute': {'keyCode': 43, 'key': 'Execute', 'code': 'Open'},'\u0000': {'keyCode': 46, 'key': '\u0000', 'code': 'NumpadDecimal', 'location': 3},'a': {'keyCode': 65, 'key': 'a', 'code': 'KeyA'},'b': {'keyCode': 66, 'key': 'b', 'code': 'KeyB'},'c': {'keyCode': 67, 'key': 'c', 'code': 'KeyC'},'d': {'keyCode': 68, 'key': 'd', 'code': 'KeyD'},'e': {'keyCode': 69, 'key': 'e', 'code': 'KeyE'},'f': {'keyCode': 70, 'key': 'f', 'code': 'KeyF'},'g': {'keyCode': 71, 'key': 'g', 'code': 'KeyG'},'h': {'keyCode': 72, 'key': 'h', 'code': 'KeyH'},'i': {'keyCode': 73, 'key': 'i', 'code': 'KeyI'},'j': {'keyCode': 74, 'key': 'j', 'code': 'KeyJ'},'k': {'keyCode': 75, 'key': 'k', 'code': 'KeyK'},'l': {'keyCode': 76, 'key': 'l', 'code': 'KeyL'},'m': {'keyCode': 77, 'key': 'm', 'code': 'KeyM'},'n': {'keyCode': 78, 'key': 'n', 'code': 'KeyN'},'o': {'keyCode': 79, 'key': 'o', 'code': 'KeyO'},'p': {'keyCode': 80, 'key': 'p', 'code': 'KeyP'},'q': {'keyCode': 81, 'key': 'q', 'code': 'KeyQ'},'r': {'keyCode': 82, 'key': 'r', 'code': 'KeyR'},'s': {'keyCode': 83, 'key': 's', 'code': 'KeyS'},'t': {'keyCode': 84, 'key': 't', 'code': 'KeyT'},'u': {'keyCode': 85, 'key': 'u', 'code': 'KeyU'},'v': {'keyCode': 86, 'key': 'v', 'code': 'KeyV'},'w': {'keyCode': 87, 'key': 'w', 'code': 'KeyW'},'x': {'keyCode': 88, 'key': 'x', 'code': 'KeyX'},'y': {'keyCode': 89, 'key': 'y', 'code': 'KeyY'},'z': {'keyCode': 90, 'key': 'z', 'code': 'KeyZ'},'Meta': {'keyCode': 91, 'key': 'Meta', 'code': 'MetaLeft'},'*': {'keyCode': 106, 'key': '*', 'code': 'NumpadMultiply', 'location': 3},'+': {'keyCode': 107, 'key': '+', 'code': 'NumpadAdd', 'location': 3},'-': {'keyCode': 109, 'key': '-', 'code': 'NumpadSubtract', 'location': 3},'/': {'keyCode': 111, 'key': '/', 'code': 'NumpadDivide', 'location': 3},';': {'keyCode': 186, 'key': ';', 'code': 'Semicolon'},'=': {'keyCode': 187, 'key': '=', 'code': 'Equal'},',': {'keyCode': 188, 'key': ',', 'code': 'Comma'},'.': {'keyCode': 190, 'key': '.', 'code': 'Period'},'`': {'keyCode': 192, 'key': '`', 'code': 'Backquote'},'[': {'keyCode': 219, 'key': '[', 'code': 'BracketLeft'},'\\': {'keyCode': 220, 'key': '\\', 'code': 'Backslash'},']': {'keyCode': 221, 'key': ']', 'code': 'BracketRight'},'\'': {'keyCode': 222, 'key': '\'', 'code': 'Quote'},'Attn': {'keyCode': 246, 'key': 'Attn'},'CrSel': {'keyCode': 247, 'key': 'CrSel', 'code': 'Props'},'ExSel': {'keyCode': 248, 'key': 'ExSel'},'EraseEof': {'keyCode': 249, 'key': 'EraseEof'},'Play': {'keyCode': 250, 'key': 'Play'},'ZoomOut': {'keyCode': 251, 'key': 'ZoomOut'},')': {'keyCode': 48, 'key': ')', 'code': 'Digit0'},'!': {'keyCode': 49, 'key': '!', 'code': 'Digit1'},'@': {'keyCode': 50, 'key': '@', 'code': 'Digit2'},'#': {'keyCode': 51, 'key': '#', 'code': 'Digit3'},'$': {'keyCode': 52, 'key': '$', 'code': 'Digit4'},'%': {'keyCode': 53, 'key': '%', 'code': 'Digit5'},'^': {'keyCode': 54, 'key': '^', 'code': 'Digit6'},'&': {'keyCode': 55, 'key': '&', 'code': 'Digit7'},'(': {'keyCode': 57, 'key': '(', 'code': 'Digit9'},'A': {'keyCode': 65, 'key': 'A', 'code': 'KeyA'},'B': {'keyCode': 66, 'key': 'B', 'code': 'KeyB'},'C': {'keyCode': 67, 'key': 'C', 'code': 'KeyC'},'D': {'keyCode': 68, 'key': 'D', 'code': 'KeyD'},'E': {'keyCode': 69, 'key': 'E', 'code': 'KeyE'},'F': {'keyCode': 70, 'key': 'F', 'code': 'KeyF'},'G': {'keyCode': 71, 'key': 'G', 'code': 'KeyG'},'H': {'keyCode': 72, 'key': 'H', 'code': 'KeyH'},'I': {'keyCode': 73, 'key': 'I', 'code': 'KeyI'},'J': {'keyCode': 74, 'key': 'J', 'code': 'KeyJ'},'K': {'keyCode': 75, 'key': 'K', 'code': 'KeyK'},'L': {'keyCode': 76, 'key': 'L', 'code': 'KeyL'},'M': {'keyCode': 77, 'key': 'M', 'code': 'KeyM'},'N': {'keyCode': 78, 'key': 'N', 'code': 'KeyN'},'O': {'keyCode': 79, 'key': 'O', 'code': 'KeyO'},'P': {'keyCode': 80, 'key': 'P', 'code': 'KeyP'},'Q': {'keyCode': 81, 'key': 'Q', 'code': 'KeyQ'},'R': {'keyCode': 82, 'key': 'R', 'code': 'KeyR'},'S': {'keyCode': 83, 'key': 'S', 'code': 'KeyS'},'T': {'keyCode': 84, 'key': 'T', 'code': 'KeyT'},'U': {'keyCode': 85, 'key': 'U', 'code': 'KeyU'},'V': {'keyCode': 86, 'key': 'V', 'code': 'KeyV'},'W': {'keyCode': 87, 'key': 'W', 'code': 'KeyW'},'X': {'keyCode': 88, 'key': 'X', 'code': 'KeyX'},'Y': {'keyCode': 89, 'key': 'Y', 'code': 'KeyY'},'Z': {'keyCode': 90, 'key': 'Z', 'code': 'KeyZ'},':': {'keyCode': 186, 'key': ':', 'code': 'Semicolon'},'<': {'keyCode': 188, 'key': '<', 'code': 'Comma'},'_': {'keyCode': 189, 'key': '_', 'code': 'Minus'},'>': {'keyCode': 190, 'key': '>', 'code': 'Period'},'?': {'keyCode': 191, 'key': '?', 'code': 'Slash'},'~': {'keyCode': 192, 'key': '~', 'code': 'Backquote'},'{': {'keyCode': 219, 'key': '{', 'code': 'BracketLeft'},'|': {'keyCode': 220, 'key': '|', 'code': 'Backslash'},'}': {'keyCode': 221, 'key': '}', 'code': 'BracketRight'},'"': {'keyCode': 222, 'key': '"', 'code': 'Quote'},}
            self._modifiers = 0
            self._pressed_keys = set()
            self.attach(f)
        def attach(self, f):
            f.make_input_events = self.make_input_events
            f.make_clear = self.make_clear
        def make_clear(self):
            charin = []
            charin.append(self._make_down('Control'))
            charin.append(self._make_down('a'))
            charin.append(self._make_up('Control'))
            charin.append(self._make_up('a'))
            charin.append(self._make_down('Delete'))
            charin.append(self._make_up('Delete'))
            return charin
        def make_input_events(self, text):
            return self._make_chain(text)
        def _key_desc(self, keyString):  # noqa: C901
            shift = self._modifiers & 8
            desc = {'key': '','keyCode': 0,'code': '','text': '','location': 0}
            defi = self._key_maps.get(keyString)
            if not defi: raise Exception('Unknown key: '+keyString)
            if 'key' in defi: desc['key'] = defi['key']
            if shift and defi.get('shiftKey'): desc['key'] = defi['shiftKey']
            if 'keyCode' in defi: desc['keyCode'] = defi['keyCode']
            if shift and defi.get('shiftKeyCode'): desc['keyCode'] = defi['shiftKeyCode']
            if 'code' in defi: desc['code'] = defi['code']
            if 'location' in defi: desc['location'] = defi['location']
            if len(desc['key']) == 1: desc['text'] = desc['key']
            if 'text' in defi: desc['text'] = defi['text']
            if shift and defi.get('shiftText'): desc['text'] = defi['shiftText']
            if self._modifiers & ~8: desc['text'] = ''
            return desc
        def _modifier_bit(self, key):
            if key == 'Alt': return 1
            if key == 'Control': return 2
            if key == 'Meta': return 4
            if key == 'Shift': return 8
            return 0
        def _make_chain(self, text):
            charin = []
            for char in text:
                if char in self._key_maps:
                    charin.append([self._make_down(char), self._make_up(char)])
                else:
                    charin.append(['insertText', char])
            return charin
        def _make_down(self, char):
            desc = self._key_desc(char)
            auto_rpt = desc['code'] in self._pressed_keys
            self._pressed_keys.add(desc['code'])
            self._modifiers |= self._modifier_bit(desc['key'])
            text = desc['text']
            return {
                'type': 'keyDown' if text else 'rawKeyDown','modifiers': self._modifiers,
                'windowsVirtualKeyCode': desc['keyCode'],
                'code': desc['code'],'key': desc['key'],'text': text,
                'unmodifiedText': text,'autoRepeat': auto_rpt,
                'location': desc['location'], 'isKeypad': desc['location'] == 3, }
        def _make_up(self, char):
            desc = self._key_desc(char)
            self._modifiers &= ~self._modifier_bit(desc['key'])
            if desc['code'] in self._pressed_keys: self._pressed_keys.remove(desc['code'])
            return {
                'type': 'keyUp', 'modifiers': self._modifiers,
                'key': desc['key'], 'windowsVirtualKeyCode': desc['keyCode'],
                'code': desc['code'], 'location': desc['location'], }
    class Screenshot:
        def __init__(self, b64img):
            self.i = b64img
            self.content = base64.b64decode(self.i.encode())
        def test_show(self, timeout=1.5):
            import cv2
            import numpy as np
            img = cv2.imdecode(np.frombuffer(self.content, np.uint8), cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError("decode img fail.")
            h, w = img.shape[:2]
            c1, c2, tile_size = 200, 150, 20
            rows = (np.arange(h) // tile_size) % 2
            cols = (np.arange(w) // tile_size) % 2
            checkerboard = np.where((rows[:, None] ^ cols[None, :]) == 0, c1, c2).astype(np.uint8)
            checkerboard = cv2.merge([checkerboard, checkerboard, checkerboard])
            if img.shape[2] == 4:
                alpha = img[:, :, 3] / 255.0
                bgr = img[:, :, :3]
                blended = (bgr * alpha[..., None] + checkerboard * (1 - alpha[..., None])).astype(np.uint8)
            else:
                blended = img
            cv2.imshow('test', blended)
            cv2.waitKey(int(timeout*1000))
            cv2.destroyAllWindows()
        def __repr__(self):
            return '<Screenshot [size]:{} [prop api]: .content>'.format(to_human_read(len(self.content)))
    class Element:
        def __init__(self, f, einfo, iso=True):
            # {'type': 'object', 'subtype': 'node', 'className': 'HTMLAnchorElement', 'description': 'a', 'objectId': '-1497388350229232364.96.1'}
            self.f = f
            self.className = einfo.get('className')
            self.objectId = einfo.get('objectId')
            self.cache_xy = None
            self.draggable = None
            self.iso = iso
            self.r_obj = self.f.run_iso_js_obj if self.iso else self.f.run_js_obj
            self.r_js = self.f.run_iso_js if self.iso else self.f.run_js
        @property
        def backendNodeId(self):
            return self.f.cdp('DOM.describeNode', {'objectId': self.objectId})['node']['backendNodeId']
        @property
        def _box(self):
            return self.f.cdp('DOM.getBoxModel', {'objectId': self.objectId})
        def __repr__(self):
            return '<DOM:[{}] [{}]>'.format(self.className, self.objectId)
        def clear(self, delay_uptime=0.15, timegap=0.01):
            self.wait_show()
            self.f.cdp('DOM.focus', {"objectId": self.objectId})
            clear_ents = self.f.rootf.make_clear()
            for kdn in clear_ents[:2]: time.sleep(timegap); self.f.cdp('Input.dispatchKeyEvent', kdn)
            time.sleep(delay_uptime)
            for kup in clear_ents[2:4]: time.sleep(timegap); self.f.cdp('Input.dispatchKeyEvent', kup)
            for delt in clear_ents[4:]: time.sleep(timegap); self.f.cdp('Input.dispatchKeyEvent', delt)
        def input(self, str, delay_time=0.02, delay_uptime=0.15, random_gap=0.01):
            self.wait_show()
            self.f.cdp('DOM.focus', {"objectId": self.objectId})
            for kdn, kup in self.f.rootf.make_input_events(str):
                if kdn == 'insertText':
                    self.f.cdp('Input.insertText', {"text": kup})
                    time.sleep(delay_time+(random_gap if random()>0.5 else 0))
                else:
                    self.f.cdp('Input.dispatchKeyEvent', kdn)
                    time.sleep(delay_time+(random_gap if random()>0.5 else 0))
                    def delay_up(kup, delay_uptime):
                        time.sleep(delay_uptime)
                        self.f.cdp('Input.dispatchKeyEvent', kup)
                    self.f.rootf.root.pool(delay_up)(kup, delay_uptime)
        def _get_xy(self, x, y, zero='center'):
            o = self.f.cdp('DOM.getBoxModel', {"objectId": self.objectId})
            m = o['model']
            if zero == 'center':
                _x = (m['content'][0] + m['content'][2]) / 2 + x;
                _y = (m['content'][1] + m['content'][5]) / 2 + y;
            elif zero == 'lefttop':
                _x = m['content'][0] + x
                _y = m['content'][1] + y
            elif zero == 'leftbottom':
                _x = m['content'][6] + x
                _y = m['content'][7] - y
            else:
                raise Exception('zero type must be in (center,lefttop,leftbottom).')
            return _x, _y
        def _set_in_view(self):
            self.f.cdp('DOM.scrollIntoViewIfNeeded', {"objectId": self.objectId})
        def click(self, x=1, y=2, zero='center', button='left', count=1):
            self.wait_show()
            self._set_in_view()
            _x, _y = self._get_xy(x, y, zero)
            self.f.cdp('Input.dispatchMouseEvent',{"buttons":0,"type":"mouseMoved","x":_x,"y":_y,"button":"none","clickCount":0})
            self.f.cdp('Input.dispatchMouseEvent',{"buttons":1,"type":"mousePressed","x":_x,"y":_y,"button":button,"clickCount":count})
            time.sleep(0.07)
            self.f.cdp('Input.dispatchMouseEvent',{"buttons":0,"type":"mouseReleased","x":_x,"y":_y,"button":button,"clickCount":count})
        def _bezier_xxyy(self, x1, y1, x2, y2):
            def step_len(x1, y1, x2, y2):
                ln = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                return int(ln / 4)
            slen = step_len(x1, y1, x2, y2)
            lp = (random() - 0.5) * 0.5
            rp = (random() - 0.5) * 0.5 + 1
            xx1 = int(x1 + (x2 - x1) / 12 * (4-lp*4))
            yy1 = int(y1 + (y2 - y1) / 12 * (8+lp*4))
            xx2 = int(x1 + (x2 - x1) / 12 * (8+rp*4))
            yy2 = int(y1 + (y2 - y1) / 12 * (4-rp*4))
            points = [[x1, y1], [xx1, yy1], [xx2, yy2], [x2, y2]]
            N = len(points)
            n = N - 1 
            r = []
            for T in range(slen + 1):
                t = T*(1/slen)
                t = (sin(t * pi / 2)) ** 18
                x,y = 0,0
                for i in range(N):
                    B = factorial(n)*t**i*(1-t)**(n-i)/(factorial(i)*factorial(n-i))
                    x += points[i][0]*B
                    y += points[i][1]*B
                r.append([x, y])
            return r
        def wait_show(self, timeout=5, pretime=0.1):
            start = perf_counter()
            count, acount = 0, 0
            px, py = 0, 0
            while True:
                v = self.visible()
                if v.get('isDisplayed'):
                    x, y = v['clickPoint']['x'], v['clickPoint']['y']
                    if x == px and y == py:
                        count += 1
                    else:
                        count = 0
                    acount += 1
                    px, py = x, y
                    if count > 1 or acount > 5:
                        break
                if perf_counter() - start > timeout:
                    raise Exception('wait show over time.')
                time.sleep(0.08)
            if pretime:
                time.sleep(pretime) # When the component appears, the event might not have been attached yet. Please wait a moment.
        def drag(self, x=1, y=2, zero='center', button='left', count=1):
            self.wait_show()
            self._set_in_view()
            x, y = self._get_xy(x, y, zero)
            self.cache_xy = [x, y]
            self.f.cdp('Input.dispatchMouseEvent',{"buttons":1,"type":"mousePressed","x":int(x),"y":int(y),"button":button,"clickCount":count})
            self.draggable = self['draggable']
            if self.draggable:
                print('[*] h5 draggable element cannot simulate drag and drop.')
            # draggable api, CDP not simulate and this api cannot record trajectory
            # self.f.cdp('Input.dispatchDragEvent',{"type":"dragEnter","x":int(x),"y":int(y),
            #     "data":{"items":[{"type":"text/plain","data":"some text"}]}
            #     })
            # self.f.cdp('Input.dispatchDragEvent',{"type":"dragOver","x":int(x),"y":int(y)})
            # self.f.cdp('Input.dispatchDragEvent',{"type":"drop","x":int(x),"y":int(y)})
            # and <input type=range> cannot simulate sliding through CDP.
            return self
        def dragmove(self, shiftx=0, shifty=0, button='left', count=1, costtime=0.8):
            if self.cache_xy:
                x, y = self.cache_xy
            else:
                cp = self._view_info()['clickPoint']
                x, y = cp['x'], cp['y']
            self.cache_xy = x, y
            c = self._bezier_xxyy(x,y,x+shiftx,y+shifty)
            g = costtime / len(c)
            start = perf_counter()
            ctime = 0
            gtime = 0
            for x, y in c:
                self.f.cdp('Input.dispatchMouseEvent',{"buttons":1,"type":"mouseMoved","x":int(x),"y":int(y),"button":"none","clickCount":0})
                self.cache_xy = x, y
                ctime += g
                gtime = perf_counter() - start
                if ctime > gtime:
                    time.sleep(ctime - gtime)
            return self
        def drop(self, button='left', count=1):
            if self.cache_xy:
                x, y = self.cache_xy
            else:
                cp = self._view_info()['clickPoint']
                x, y = cp['x'], cp['y']
            self.f.cdp('Input.dispatchMouseEvent',{"buttons":0,"type":"mouseReleased","x":int(x),"y":int(y),"button":button,"clickCount":count})
            self.cache_xy = None
            return self
        def drag_to(self, shiftx=0, shifty=0, button='left', x=1, y=2, zero='center', costtime=0.8, count=1):
            self.drag(x, y, zero, button, count) \
                .dragmove(shiftx, shifty, button, count, costtime) \
                .drop(button, count)
            return self
        def _is_coverd(self):
            try:
                c = self._view_info()['clickPoint']
                return self.backendNodeId != self.f.cdp('DOM.getNodeForLocation', {'x': c['x'], 'y': c['y']})['backendNodeId']
            except Exception as e:
                return True
        def pic(self, try_use_img=True):
            self.wait_show()
            if try_use_img and self.className == 'HTMLImageElement':
                try:
                    # If it’s an <img> tag, try to capture it via the element first; if that fails, fall back to a screenshot.
                    # Images from <img> tags are best captured as native images for better quality. 
                    # Of course, you can also set try_use_img=False to disable this method and use screenshots only, which makes the process more uniform.
                    src = self['src']
                    if src:
                        if src.startswith('http'):
                            return Screenshot(self.f.cdp("Page.getResourceContent", {"url": src, "frameId": self.f.frameId})['content'])
                        if src.startswith('data:image/png;base64,'):
                            return Screenshot(src.replace('data:image/png;base64,', ''))
                except:
                    pass
            rparentlist = self.f._get_remote_list()
            if not rparentlist:
                box = self.f.cdp('DOM.getBoxModel', {'objectId': self.objectId})
                x, y = box['model']['padding'][0], box['model']['padding'][1]
                width, height = box['model']['width'], box['model']['height']
                screenshot = self.f.cdp('Page.captureScreenshot', {"format":'png', 
                    "clip":{"x":x,"y":y,"width":width,"height":height,"scale":1} })
                return Screenshot(screenshot['data'])
            else:
                slfele = self.f.element._frame_element(self.f)
                sftx, sfty = 0, 0
                f = self.f.element._frame_element(rparentlist[-1])
                box = f._box['model']['padding']
                sftx += box[0]
                sfty += box[1]
                f_box = self._box
                x, y = f_box['model']['padding'][0], f_box['model']['padding'][1]
                width, height = f_box['model']['width'], f_box['model']['height']
                screenshot = self.f.rootf.cdp('Page.captureScreenshot', {"format":'png', 
                    "clip":{"x":x+sftx,"y":y+sfty,"width":width,"height":height,"scale":1} })
                return Screenshot(screenshot['data'])
        def _view_info(self):
            return self.f.element.visibility(self.objectId)
        def visible(self):
            d = self._view_info()
            # Page navigation destroys frames, invalidating the objectId's execution context and necessitating reacquisition.
            # only for ele(). on all need run wait_show() functions.
            if d.get('code') == -32000:
                f = getattr(self, 're_search', None)
                if f:
                    e = f()
                    if e:
                        self.className = e.className
                        self.objectId = e.objectId
                d = self._view_info()
            d['isCoverd'] = self._is_coverd()
            return d
        def info(self):
            d = self.visible()
            class ViewInfo:
                def __init__(self, d):
                    self.d = d
                def __repr__(self):
                    return json.dumps(self.d, indent=4)
            return ViewInfo(d)
        def xpath(self, s):
            return self.f.element.xpath(s, self.objectId)
        def css(self, s):
            return self.f.element.css(s, self.objectId)
        def _ele(self, s, one=False):
            r = []
            xf, tp = self.f.element._predict_xpath_or_css(s.strip())
            if tp == 'xpath': r.extend(self.xpath(xf))
            if tp == 'css': r.extend(self.css(xf))
            if one and r: return r
            nodeId = self.f.cdp('DOM.describeNode', {'objectId': self.objectId})['node']['nodeId']
            for sr in self.f.element._sr_root(nodeId):
                if tp == 'xpath': r.extend(sr.xpath(xf))
                if tp == 'css': r.extend(sr.css(xf))
                if one and r:  return r
            return r
        def ele(self, s):
            rt = self._ele(s, one=True)
            return rt[0] if rt else None
        def eles(self, s):
            return self._ele(s)
        def id(self, i):
            return self.ele('#'+i)
        def ijs(self, s):
            einfo = self.r_js(s, returnByValue=False)
            return self.f._parse_js2py(einfo, self, iso=self.iso)
        def __getitem__(self, a):
            einfo = self.r_obj('function(){return this[' + json.dumps(a) + ']}', objectId=self.objectId, returnByValue=False)
            return self.f._parse_js2py(einfo, self, iso=self.iso)
        def __setitem__(self, a, b):
            args = [None,self.f._parse_2arg(a), self.f._parse_2arg(b)]
            einfo = self.r_obj('function(a,b){return this[a]=b}', objectId=self.objectId, arguments=args, returnByValue=False)
            return self.f._parse_js2py(einfo, iso=self.iso)
        def __add__(self, other):
            einfo = self.r_obj('function(){return this["toString"]()}', objectId=self.objectId, returnByValue=False)
            return self.f._parse_js2py(einfo, self, iso=self.iso) + str(other)
        text = property(lambda s:s['outerHTML'] or s['textContent'])
        before = property(lambda s:s['previousElementSibling'])
        after = property(lambda s:s['nextElementSibling'])
        parent = property(lambda s:s['parentElement'])
        children = property(lambda s:s['children'])
    class ElementTools:
        def __init__(self, f):
            self.f = f
            self.attach(f)
        def attach(self, f):
            f.id = self.id
            f.ele = self.ele
            f.eles = self.eles
            f.xpath = self.xpath
            f.css = self.css
            f._sr_root = self._sr_root
        def _predict_xpath_or_css(self, x):
            if x.startswith('x:'):
                xf, tp = x[2:], 'xpath'
            elif x.startswith('c:'):
                xf, tp = x[2:], 'css'
            else:
                xf = x
                x = x.strip()
                if x == '.' or '/' in x:
                    tp = 'xpath'
                else:
                    tp = 'css'
            return xf, tp
        def _parse_x(self, x, all_frames, one=False, over_v_limit=False):
            r = []
            frms = [self.f]
            xf, tp = self._predict_xpath_or_css(x.strip())
            if all_frames:
                frms.extend(self.f.root.flat_child_frames(self.f.frames))
            for f in frms:
                if over_v_limit: f.iso_contextId = None
                if tp == 'xpath':
                    r.extend(f.xpath(xf))
                    if one and r: return r
                    if f.type == 'LocalFrame':continue
                    for sr in f._sr_root(): 
                        if one and r: return r
                        r.extend(sr.xpath(xf))
                elif tp == 'css':
                    r.extend(f.css(xf))
                    if one and r: return r
                    if f.type == 'LocalFrame':continue
                    for sr in f._sr_root(): 
                        if one and r: return r
                        r.extend(sr.css(xf))
            return r
        def id(self, x, timeout=8, no_wait=False, all_frames=True):
            return self.ele('#'+ x, timeout=timeout, no_wait=no_wait, all_frames=all_frames)
        def ele(self, x, timeout=8, no_wait=False, all_frames=True):
            start = perf_counter()
            over_v_time = 2
            over_v_limit = False
            while True:
                ctime = perf_counter()
                if ctime - start > over_v_time: over_v_limit = True
                r = self._parse_x(x, all_frames, one=True, over_v_limit=over_v_limit)
                if ctime - start > over_v_time: over_v_limit = False
                if r: 
                    r[0].re_search = lambda:self.ele(x)
                    return r[0]
                if no_wait: return None
                if ctime - start > timeout:
                    raise Exception('ele selecter timeout.')
                time.sleep(0.08)
        def eles(self, x, timeout=8, no_wait=False, all_frames=True):
            start = perf_counter()
            over_v_time = 2
            over_v_limit = False
            while True:
                ctime = perf_counter()
                if ctime - start > over_v_time: over_v_limit = True
                r = self._parse_x(x, all_frames, over_v_limit=over_v_limit)
                if ctime - start > over_v_time: over_v_limit = False
                if r: return r
                if no_wait: return []
                if ctime - start > timeout:
                    raise Exception('eles selecter timeout.')
                time.sleep(0.08)
        def _parse_array(self, r):
            if not r.get('objectId'):
                return []
            prps = self.f.cdp('Runtime.getProperties', { 'objectId': r['objectId'], 'ownProperties': True })
            rn = []
            for prp in prps.get('result', []):
                if prp['name'].isdigit() and 'objectId' in prp['value']:
                    rn.append(Element(self.f, prp['value']))
            return rn
        def _run_iso(self, fscpt, objectId, returnByValue=False):
            if objectId:
                r = self.f.run_iso_js_obj(fscpt, returnByValue=returnByValue, objectId=objectId)
            else:
                r = self.f.run_iso_js('({})()'.format(fscpt), returnByValue=returnByValue)
            return r
        def _trav_node_tree(self, rnode):
            def collect(n):
                d = {}
                d['nodeId'] = n['nodeId']
                d['backendNodeId'] = n['backendNodeId']
                d['nodeType'] = n['nodeType']
                d['nodeName'] = n['nodeName']
                if n.get('frameId'):
                    d['frameId'] = n['frameId']
                    if n.get('nodeName') == 'IFRAME' and 'contentDocument' in n:
                        _trav(n['contentDocument'])
                if n.get('shadowRoots'):
                    d['shadowRoots'] = n['shadowRoots']
                    for ssnode in d['shadowRoots']:
                        if ssnode.get('children'):
                            _trav(ssnode)
                clist.append(d)
            clist = []
            def _trav(rnode):
                collect(rnode)
                if rnode.get('children'):
                    for snode in rnode['children']:
                        _trav(snode)
            _trav(rnode)
            return clist
        def _get_doc_tree(self):
            start = perf_counter()
            while True:
                doc = self.f.cdp('DOM.getDocument', {'depth':-1, 'pierce':True})
                if 'root' in doc:
                    return doc
                else:
                    time.sleep(0.1)
                if perf_counter() - start > 2:
                    break
        def _get_flattened_node(self, nodeId=None):
            if nodeId == None:
                rnode = self._get_doc_tree()['root']
            else:
                rnode = self.f.cdp('DOM.describeNode', {'nodeId':nodeId, 'depth':-1, 'pierce':True})['node']
            mnodes = {"nodes": self._trav_node_tree(rnode)}
            return mnodes
        def _filter_shadow_root(self, mnodes):
            r = []
            if not mnodes.get('nodes'):
                return []
            for n in mnodes['nodes']:
                srlst = n.get('shadowRoots')
                if srlst:
                    for sr in srlst:
                        if (sr.get('nodeName') == '#document-fragment' 
                            and (
                                sr.get('shadowRootType') == 'closed' or 
                                sr.get('shadowRootType') == 'open')
                        ):
                            m = self.f.cdp('DOM.resolveNode', {"backendNodeId": sr['backendNodeId']})
                            if m.get('object'):
                                e = Element(self.f, m['object'])
                                r.append(e)
            return r
        def _sr_root(self, nodeId=None):
            mnodes = self._get_flattened_node(nodeId)
            return self._filter_shadow_root(mnodes)
        def _make_shadow_root_xpath(self, s):
            v = re.findall('^([^/]*)(/+)([^/]*)$', s)
            if v and len(v[0]) == 3:
                v = v[0]
                p = v[-1].split('[', 1)
                tag = p[0]
                pak = p[1] if len(p) == 2 else ''
                if pak:
                    pak = "[self::"+tag+' and ' + pak
                else:
                    pak = "[self::"+tag+']'
                return '(.|'+v[0]+v[1]+tag+')'+pak
            else:
                return s
        def xpath(self, s, objectId=None):
            s = s.lstrip()
            if s[0] != '.' and s[0] != '/': s = './' + s
            if s[0] == '/': s = '.' + s
            fscpt = '''
            function() {
                var contextNode = window === this ? document : this
                var node, nodes = [];
                if (contextNode instanceof ShadowRoot){ 
                    for (var i = 0; i < contextNode.children.length; i++) {
                        var snode = contextNode.children[i]
                        var iterator = document.evaluate('''+json.dumps(self._make_shadow_root_xpath(s))+''', snode, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
                        while ((node = iterator.iterateNext())) { nodes.push(node); }
                    }
                }else{
                    var iterator = document.evaluate('''+json.dumps(s)+''', contextNode, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
                    while ((node = iterator.iterateNext())) { nodes.push(node); }
                }
                return nodes;
            }
            '''
            r = self._run_iso(fscpt, objectId)
            return self._parse_array(r)
        def visibility(self, objectId=None):
            fscpt = '''
            function() {
                const rect = this.getBoundingClientRect();
                const s = window.getComputedStyle(this);
                return {
                    inViewport: (
                        rect.top < window.innerHeight &&
                        rect.bottom > 0 &&
                        rect.left < window.innerWidth &&
                        rect.right > 0
                    ),
                    style: {
                        display: s.display,
                        visibility: s.visibility,
                        opacity: s.opacity,
                        position: s.position,
                        zIndex: s.zIndex
                    },
                    isDisplayed: !(
                        s.visibility == 'hidden' ||
                        s.display == 'none' ||
                        this.hidden || 
                        rect.width == 0 || 
                        rect.height == 0
                    ),
                    rect: {
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top,
                        right: rect.right,
                        bottom: rect.bottom,
                        left: rect.left
                    },
                    clickPoint: {
                        x: (rect.x + rect.width/2)|0, 
                        y: (rect.y + rect.height/2)|0, 
                    },
                    inDocument: document.contains(this),
                    isClickable: (
                        s.pointerEvents !== 'none' &&
                        s.cursor !== 'not-allowed'
                    )
                };
            }
            '''
            r = self._run_iso(fscpt, objectId, returnByValue=True)
            return r
        def css(self, s, objectId=None):
            fscpt = '''
            function(){
                var contextNode = window === this ? document : this
                return Array.from(contextNode.querySelectorAll(''' + json.dumps(s) + '''));
            }
            '''
            r = self._run_iso(fscpt, objectId)
            return self._parse_array(r)
        @staticmethod
        def _frame_element(self):
            nodeId = self.parent.cdp('DOM.getDocument', {"depth": -1})['root']['nodeId']
            frs = self.parent.cdp('DOM.querySelectorAll', { "nodeId": nodeId, "selector": 'iframe' })
            node = None
            for fr in frs['nodeIds']:
                nd = self.parent.cdp('DOM.describeNode', { "nodeId": fr })
                if nd['node']['frameId'] == self.frameId:
                    node = nd['node']
                    break
            return Element(self.parent, self.parent.cdp('DOM.resolveNode', {"backendNodeId": node['backendNodeId']})['object'])
    class CDPTools:
        def __init__(self, f, rootf):
            self.f = f
            self.rootf = rootf
            self.attach(f)
        def attach(self, f):
            f.run_js = self.run_js
            f.run_js_obj = self.run_js_obj
            f.run_iso_js = self.run_iso_js
            f.run_iso_js_obj = self.run_iso_js_obj
            f._js2py = self._js2py
            f._parse_js2py = self._parse_js2py
            f._parse_2arg = self._parse_2arg
        def _init_iso(self, d):
            if not self.f.iso_contextId:
                x = self.rootf.cdp('Page.createIsolatedWorld', { "frameId": self.f.frameId }, sessionId=self.f.sessionId)
                if x.get('message') == 'No frame for given id found':
                    return
                if 'executionContextId' not in x:
                    print('error create iso:'+str(x))
                    return
                self.f.iso_contextId = x['executionContextId']
            if self.f.iso_contextId != None: d["contextId"] = self.f.iso_contextId
            return d
        def _parse_2arg(self, v):
            if isinstance(v, (JSObject, Element)):
                return {"objectId": v.objectId}
            else:
                return {"value": v}
        def _parse_js2py(self, e, _this=None, iso=False):
            if type(e) in (int, float, str, bool): return e
            if e == None: return None
            if iso and type(e) == dict and e.get('subtype') == 'node':
                # The ISO here is only used to isolate the impact of code on the main context.
                return Element(self.f, e, iso=iso)
            return JSObject(self.f, e, _this, iso)
        def _js2py(self, code, iso=False):
            return self._parse_js2py((self.run_iso_js if iso else self.run_js)(code, returnByValue=False), iso=iso)
        def run_js(self, script, awaitPromise=True, returnByValue=True):
            d = {  "expression": script, "awaitPromise": awaitPromise, "returnByValue": returnByValue }
            if self.f.contextId != None: d["contextId"] = self.f.contextId
            return self.rootf.cdp('Runtime.evaluate', d, sessionId=self.f.sessionId)
        def run_js_obj(self, script, awaitPromise=True, returnByValue=True, objectId=None, arguments=[None], includeCommandLineAPI=False):
            d = {  "functionDeclaration": script, "awaitPromise": awaitPromise, "returnByValue": returnByValue, "objectId": objectId, "includeCommandLineAPI": includeCommandLineAPI }
            if arguments[0]: 
                arguments[0] = { "objectId": arguments[0].objectId }
                d['arguments'] = arguments
            else:
                d['arguments'] = arguments[1:]
            if self.f.contextId != None: d["contextId"] = self.f.contextId
            return self.rootf.cdp('Runtime.callFunctionOn', d, sessionId=self.f.sessionId)
        def run_iso_js(self, script, awaitPromise=True, returnByValue=True, includeCommandLineAPI=False):
            d = self._init_iso({ "expression": script, "awaitPromise": awaitPromise,"returnByValue": returnByValue, "includeCommandLineAPI": includeCommandLineAPI })
            return self.rootf.cdp('Runtime.evaluate', d, sessionId=self.f.sessionId) if d else {}
        def run_iso_js_obj(self, script, awaitPromise=True, returnByValue=True, objectId=None, arguments=[None], includeCommandLineAPI=False):
            d = self._init_iso({ "functionDeclaration": script, "awaitPromise": awaitPromise,"returnByValue": returnByValue, "objectId": objectId, "includeCommandLineAPI": includeCommandLineAPI })
            if not d: return {}
            if arguments[0]: 
                arguments[0] = { "objectId": arguments[0].objectId }
                d['arguments'] = arguments
            else:
                d['arguments'] = arguments[1:]
            return self.rootf.cdp('Runtime.callFunctionOn', d, sessionId=self.f.sessionId) if d else {}
    class AbsFrame:
        def __init__(self, f, finfo):
            self.rootf = f
            self.frameId = finfo['frameId']
            self.frames = []
            self.parent = finfo.get('parent')
            self.url = finfo.get('url')
            # LocalFrame
            self.contextId = finfo.get('contextId')
            self.uniqueId = finfo.get('uniqueId')
            # RemoteFrame
            self.sessionId = finfo.get('sessionId')
            self.iso_contextId = None
            self.tools = CDPTools(self, self.rootf)
            self.element = ElementTools(self)
        @property
        def type(self):
            if self.sessionId:
                return 'RemoteFrame'
            if self.contextId:
                return 'LocalFrame'
            return 'UnknownFrame'
        def __repr__(self):
            if self.type == 'RemoteFrame':
                return '<[{}]|{}|F:{}|S:{}>'.format(self.type, self.url, self.frameId, self.sessionId)
            return '<[{}]|{}|F:{}>'.format(self.type, self.url, self.frameId)
        def cdp(self, *a, **kw):
            return self.rootf.cdp(*a, **kw, sessionId=self.sessionId)
        def _get_remote_list(self):
            _self = self
            _rlst = []
            while _self:
                if _self.type == 'RemoteFrame':
                    _rlst.append(_self)
                _self = _self.parent
            return _rlst
        def pic(self,):
            return self._js2py('document.documentElement', iso=True).pic()
    class Runtime:
        def __init__(self, f):
            self.f = f
            self.f.set_method_callback('Runtime.executionContextCreated', self.Runtime_executionContextCreated)
            self.f.set_method_callback('Runtime.executionContextDestroyed', self.Runtime_executionContextDestroyed)
            self.init()
        def init(self, sessionId=None):
            self.f.cdp('Runtime.enable', sessionId=sessionId)
        def Runtime_executionContextCreated(self, rdata):
            self.f.root._add_init_check()
            # {"context": 
            #     {"id": 10, 
            #     "origin": "http://lc1.test:18000", 
            #     "name": "", 
            #     "uniqueId": "-2899874725492390568.194300135741888500", 
            #     "auxData": 
            #         {"isDefault": true, 
            #         "type": "default", 
            #         "frameId": "6D49B34D12C4719D669CE5DC9BED71A4"}}}
            params = rdata['params']
            if 'auxData' not in params['context']:
                # extension context
                # {"context": {"id": 1, "origin": "chrome-extension://ognihjbdmbjhecdlpjjonacagooanpfa/background.js", "name": "", "uniqueId": "-5795409506706594697.-3458865582039429610"}}
                # maybe some blob:url
                # {"context": {"id": 1, "origin": "blob:https://steamdb.info/fd99df19-bda7-4360-8cff-80c782e38697", "name": "", "uniqueId": "-5913474193475720670.7988369434689538446"}}
                self.f.root._del_init_check()
                return
            if params['context']['auxData']['type'] == 'isolated':
                # DevTools tools isolate context
                # {"context": {"id": 100, "origin": "http://lc1.test:18000", "name": "DevTools Performance Metrics", "uniqueId": "-4717759096737431074.6555991471704808792", "auxData": {"isDefault": false, "type": "isolated", "frameId": "65764D3FB5953A54725C764602802733"}}}
                self.f.root._del_init_check()
                return
            frameId = params['context']['auxData']['frameId']
            uniqueId = params['context']['uniqueId']
            contextId = params['context']['id']
            if frameId != self.f.frameId:
                self.f.root.add_common_frame(self.f, {
                    "contextId": contextId, 
                    "uniqueId": uniqueId,
                    "frameId": frameId,
                }, sessionId=rdata.get('sessionId'))
            self.f.root._del_init_check()
        def Runtime_executionContextDestroyed(self, rdata):
            if 'executionContextUniqueId' in rdata['params']:
                f = self.f.root.trav_frame(rdata['params'].get('executionContextUniqueId'), 'uniqueId')
                if f:
                    f.parent.frames.remove(f)
    class Emulation:
        def __init__(self, f):
            self.f = f
            self.init()
        def init(self, sessionId=None):
            self.f.cdp('Emulation.setFocusEmulationEnabled', {'enabled': True}, sessionId=sessionId)
            # chrome 112+: Emulation.setDeviceMetricsOverride connot work in screenX/screenY.
            # self.f.cdp('Emulation.setDeviceMetricsOverride', {
            #     "positionX": 100,
            #     "positionY": 200,
            #     }, sessionId=sessionId)
    class CoreCDP:
        def __init__(self, ws, root, logger=None):
            self.ws = ws
            self.root = root
            self.logger = logger or (lambda *a,**kw:None)
            self.id = 0
            self.xid = 0
            self.qret = {}
            self.irun = {}
            self._start()
        def _start(self):
            self.is_running = True
            self.loop_recv = Thread(target=self.start_loop)
            self.loop_recv.daemon = True
            self.loop_recv.start()
        def _handle_method(self, rdata):
            method = rdata.get('method')
            if method in self.irun:
                for xid in self.irun[method]:
                    m = self.irun[method].get(xid, None)
                    if m:
                        if is_function(m):
                            m(rdata)
                        if isinstance(m, queue.Queue):
                            m.put(rdata['params'])
        def _handle_return(self, rdata):
            if rdata.get('id') in self.qret:
                if rdata.get('result', Err) != Err:
                    self.qret[rdata.get('id')].put(rdata['result'])
                elif rdata.get('error', Err) != Err:
                    self.qret[rdata.get('id')].put(rdata['error'])
                else:
                    self.logger(rdata, repr(rdata.get('result')))
                    raise Exception('un expect err.' + repr(rdata.get('result')))
        def attach(self, f):
            f.cdp = self.cdp
            f.wait_once_method = self.wait_once_method
            f.set_method_callback = self.set_method_callback
        def start_loop(self):
            while self.is_running:
                try:
                    recvd = self.ws.recv()
                    if not recvd:
                        continue
                    rdata = json.loads(recvd)
                    self.logger('recv', rdata)
                except WebSocketTimeoutException:
                    continue
                except (
                    OSError, 
                    JSONDecodeError,
                    WebSocketException, 
                    WebSocketConnectionClosedException, 
                    ConnectionResetError, 
                ) as e:
                    if not self.is_running: 
                        return
                    if (
                        'Connection to remote host was lost.' in str(e)
                        or 'socket is already closed.' in str(e)
                        or isinstance(e, OSError)
                    ):
                        # Closing the tab will trigger some return message exceptions and possible exception disconnections
                        return
                    raise Exception('[*] maybe exist ws connect from another python exe! pls close it.')
                except Exception as e:
                    print(e, 'rasie cdp loop 2')
                    raise 2
                self._handle_method(rdata)
                self._handle_return(rdata)
        def get_id(self):
            self.id += 1
            return self.id
        def get_xid(self):
            self.xid += 1
            return self.xid
        def cdp(self, protocal, data={}, sessionId=None, no_wait=False, limit_time=None):
            rid = self.get_id()
            cmd = { "id": rid, "method": protocal, "params": data }
            if sessionId: 
                cmd['sessionId'] = sessionId
            self.logger('req', cmd)
            if not no_wait:
                self.qret[rid] = queue.Queue()
            try:
                self.ws.send(json.dumps(cmd))
            except (
                OSError, 
                WebSocketConnectionClosedException
            ) as e:
                self.logger('[ERROR]', str(e))
                self.qret.pop(rid, None)
                return
            except Exception as e:
                print(e, 'rasie cdp 1')
                raise 1
            if limit_time != None:
                start = perf_counter()
            while not no_wait:
                try:
                    if limit_time != None:
                        if perf_counter() - start > limit_time:
                            self.qret.pop(rid, None)
                            return {'vvv': 'over time'}
                    ret = self.qret[rid].get(timeout=.15)
                    self.qret.pop(rid, None)
                    return try_run_result(ret)
                except queue.Empty:
                    continue
        def wait_once_method(self, method, timeout=10, check_ret_func=None, rasie_error=True):
            self.irun[method] = self.irun.get(method, {})
            xid = self.get_xid()
            self.irun[method][xid] = queue.Queue()
            start = perf_counter()
            while True:
                ctime = perf_counter()
                try:
                    if ctime - start > timeout:
                        self.irun[method].pop(xid, None)
                        return
                    ret = self.irun[method][xid].get(timeout=0.15)
                    if check_ret_func:
                        if not check_ret_func(ret):
                            continue
                    self.irun[method].pop(xid, None)
                    return ret
                except:
                    if ctime - start > timeout:
                        if rasie_error:
                            raise Exception('wait_once_method {} timeout: {}'.format(method, timeout))
                    continue
        def set_method_callback(self, method, func):
            xid = self.get_xid()
            self.irun[method] = self.irun.get(method, {})
            self.irun[method][xid] = self.root.pool(func)
            return xid
    class Closer:
        def __init__(self, f):
            self.f = f
            self.f.set_method_callback('Inspector.detached', self.close)
            self.toggle = True
        def close(self, rdata):
            self.f.tools.is_running = False
            self.f.ws.close()
            if self.f in self.f.root.tabs:
                self.f.root.tabs.remove(self.f)
            self.toggle = False
    class DOM:
        def __init__(self, f):
            self.f = f
            self.f.cdp('DOM.enable')
    class Cache:
        def __init__(self, f):
            self.f = f
            self.cache_sesslist = [None]
            self.is_enable = False
            self.attach(f)
        def _enable(self):
            if not self.is_enable:
                for sessionId in self.cache_sesslist:
                    self._cache_cdp(sessionId)
                self.is_enable = True
        def _cache_cdp(self, sessionId):
            self.f.cdp('Network.enable', sessionId=sessionId)
            self.f.cdp('Storage.enable', sessionId=sessionId)
        def attach(self, f):
            f.clear_cache = self.clear_cache
        def add_cache_session(self, sessionId):
            self.cache_sesslist.append(sessionId)
            if self.is_enable:
                self._cache_cdp(sessionId)
        def clear_cache(self):
            self._enable()
            for sessionId in self.cache_sesslist:
                self.f.cdp('Network.clearBrowserCookies',sessionId=sessionId)
                self.f.cdp('Storage.clearDataForOrigin', {'origin':'*','storageTypes':'local_storage,session_storage,indexeddb'},sessionId=sessionId);
    class Browser:
        def __init__(self, f):
            self.f = f
            self.attach(f)
        def attach(self, c):
            c.get = self.f._go_url
            c.cdp = self.f.cdp
            c.init_js = self.f.init_js
            c.ele = self.f.ele
            c.eles = self.f.eles
            c.listen = self.f.listen
            c.intercept = self.f.intercept
            c.clear_cache = self.f.clear_cache
            c.js = self.f.run_js
            c._js2py = self.f._js2py
            c.tabs = self.f.root.tabs
            c.quit = self.f.root.quit
            c.press = self.f.press
            c.release = self.f.release
            c.id = self.f.id
            c.set_rect = self.f.root.set_rect
            c.set_fullscreen = self.f.root.set_fullscreen
            c.set_maxscreen = self.f.root.set_maxscreen
            c.pic = self.f.pic
            c.get_dialog = lambda:self.f.page.dialog
            c.set_dialog = lambda v:setattr(self.f.page, 'dialog', v)
            c.get_cookies = lambda:self.f._get_cookies()
            c.set_cookies = lambda v:self.f._set_cookies(v)
            c.close = self.f.close
            def __gi(self,a):return self._js2py('window')[a]
            def __si(self,a,b):self._js2py('window')[a]=b
            c.__class__.__getitem__ = __gi
            c.__class__.__setitem__ = __si
            self.f.root.extension.attach(c)
    class CookieManager:
        def __init__(self, f): self.f = f
        @property
        def c(self): return self.f.cdp('Network.getCookies', {})['cookies']
        @property
        def d(self):
            dc = {}
            for d in self.c:
                dc[d['name']] = d
            return dc
        @property
        def string(self):
            _r = []
            for d in self.c:
                _r.append(d['name'] + '=' + d['value'])
            return '; '.join(_r)
        data = property(lambda s:s.c)
        def __getitem__(self, key): return self.d.get(key, {}).get('value')
        def __setitem__(self, k, v): 
            s = self.d.get(k)
            if s:
                s['value'] = v
                self.f._set_cookies([s])
            else:
                self.f._set_cookies(str(k)+'='+str(v))
        def __repr__(self): return '<Cookie ['+';'.join(list(self.d.keys()))+']>'
    class RootFrame:
        def __init__(self, wsinfo, root, is_auto_create=False):
            self.root = root
            self.rootf = self
            self.wsinfo = wsinfo
            if not self._check_page(wsinfo): return
            self.ws = create_connection_saf(wsinfo['webSocketDebuggerUrl'], enable_multithread=True, suppress_origin=True)
            self.type = wsinfo['type']
            self.frames = []
            self._doc_script = []
            self.url = wsinfo.get('url')
            self.parent = None
            self.init_once = False
            self.logger = Logger(wsinfo['id'], debug)
            self.frameId = wsinfo['id']
            self.sessionId = None # Used to maintain consistency with CDPTools objects
            self.contextId = None # Used to maintain consistency with CDPTools objects
            self.iso_contextId = None # Used to maintain consistency with CDPTools objects
            self.cdper = CoreCDP(self.ws, self.root, self.logger)
            self.cdper.attach(self)
            if is_auto_create: self._run_init_once()
            self.root.add_root_frame(self)
            self.target = Target(self)
            self.sniff_networt = SniffNetwork(self)
            self.sniff_fetch = SniffFetch(self)
            self.cache = Cache(self)
            self.page = Page(self)
            self.dom = DOM(self)
            self.runtime = Runtime(self)
            self.emulation = Emulation(self)
            self.tools = CDPTools(self, self)
            self.closer = Closer(self)
            self.element = ElementTools(self)
            self.browser = Browser(self)
            self.keyboard = Keyboard(self)
        def press(self, key): self.cdp('Input.dispatchKeyEvent', self.keyboard._make_down(key))
        def release(self, key): self.cdp('Input.dispatchKeyEvent', self.keyboard._make_up(key))
        def close(self):
            self.cdp('Target.closeTarget', {"targetId": self.frameId})
            while self.closer.toggle:
                time.sleep(0.07)
        def _get_cookies(self, line=False):
            return CookieManager(self)
        def _set_cookies(self, v):
            if type(v) == str:
                self.tools.run_iso_js('document.cookie='+json.dumps(v))
            elif type(v) == list:
                self.cdp('Network.setCookies', {"cookies": v})
            elif instanceof(v, CookieManager):
                self.cdp('Network.setCookies', {"cookies": v.data})
            else:
                # cookies must be (str/list)
                # str: document.cookie = 'vvv=123'
                # list: 
                #    [{'domain': '.baidu.com',
                #     'expires': 1790665876.734538,
                #     'httpOnly': False,
                #     'name': 'BIDUPSID',
                #     'path': '/',
                #     'priority': 'Medium',
                #     'sameParty': False,
                #     'secure': False,
                #     'session': False,
                #     'size': 40,
                #     'sourcePort': 443,
                #     'sourceScheme': 'Secure',
                #     'value': '2826F2D60D5E56C841B9E33F82051E8A'},...]
                # A str applies to the current URL page and can only be executed after visiting the page.
                # A list is used to perfectly restore the cookies state and can be executed before visiting the page.
                raise Exception('cookies must be (str/list/CookieManager)')
        def _get_remote_list(self):
            _self = self
            _rlst = []
            while _self:
                if _self.type == 'RemoteFrame':
                    _rlst.append(_self)
                _self = _self.parent
            return _rlst
        def pic(self,):
            return Screenshot(self.cdp('Page.captureScreenshot', {"format":'png' })['data'])
        def __repr__(self):
            return '<[RootFrame]|{}|F:{}>'.format(self.url, self.frameId)
        def _run_init_once(self):
            if not self.init_once:
                self._page_init_js()
                self.init_once = True
        def _check_page(self, wsinfo):
            if (wsinfo['type'] == "service_worker" and wsinfo['url'].startswith('chrome')) \
                or wsinfo['url'].startswith('devtools') \
                or wsinfo['type'] != 'page':
                return False
            return True
        def add_sniff_session(self, sessionId):
            self.sniff_networt.add_listen_session(sessionId)
            self.sniff_fetch.add_change_session(sessionId)
        def listen(self, *a,**kw):
            return self.sniff_networt.listen(*a,**kw)
        def intercept(self, *a,**kw):
            return self.sniff_fetch.intercept(*a,**kw)
        def _go_url(self, url, timeout=None):
            self.url = url
            self.iso_contextId = None
            self._run_init_once()
            self.cdp("Page.navigate", {"url": url})
            self.frames = []
            d_timeout = timeout if timeout != None else 5
            def check(ret):
                if self.frameId == ret['frameId']:
                    return True
            self.wait_once_method("Page.frameStoppedLoading", check_ret_func=check, timeout=d_timeout, rasie_error=False)
            start = perf_counter()
            while not timeout:
                if self.sniff_networt.qlist.empty() and self.sniff_fetch.qlist.empty():
                    break
                time.sleep(0.1)
                if perf_counter() - start > 3:
                    break
            f = self.cdp("Page.getFrameTree")
            self.url = f['frameTree']['frame']['url']
        def init_js(self, script):
            self._doc_script.append(script)
        def _page_init_js(self, sessionId=None):
            if self._doc_script:
                for s in self._doc_script:
                    self.cdp('Page.addScriptToEvaluateOnNewDocument', {"source": s}, sessionId=sessionId)
        def tree_view(self):
            r = ''
            def print_tree(f, level=0, prefix=''):
                nonlocal r
                info = str(f)
                if level == 0:
                    r += info + '\n'
                else:
                    r += ' ' * (level * 4 - 1) + prefix + info + '\n'
                for i, item in enumerate(f.frames):
                    if isinstance(item.frames, list):
                        new_prefix = '└──' if i == len(f.frames) - 1 else '├──'
                        print_tree(item, level + 1, new_prefix)
            print_tree(self)
            return r.rstrip('\n')
    class ExtensionConn:
        def __init__(self, wsinfo, root):
            self.root = root
            self.sessionId = None # Used to maintain consistency with CDPTools objects
            self.contextId = None # Used to maintain consistency with CDPTools objects
            self.iso_contextId = None # Used to maintain consistency with CDPTools objects
            self.ws = create_connection_saf(wsinfo['webSocketDebuggerUrl'], enable_multithread=True, suppress_origin=True)
            self.logger = Logger(wsinfo['id'], debug)
            self.cdper = CoreCDP(self.ws, self.root, self.logger)
            self.cdper.attach(self)
            self.cdp('Runtime.enable')
            self.tools = CDPTools(self, self)
        def set_proxy(self, p=None, method='PROXY', script=None):
            if p:
                func_script = script or '''
                function FindProxyForURL(url, host) {
                    return "'''+method+''' '''+p+'''";
                }'''
                spt = json.dumps('data:text/plain;base64,' + base64.b64encode((func_script+'''
                // '''+str(int(time.time()*1000))+'''
                ''').encode()).decode())
                cfgscript = '''{
                    mode: 'pac_script',
                    pacScript: { url: '''+spt+''' }
                }'''
            else:
                cfgscript = '{mode: "system"}'
            finscript = '''
            new Promise(function(r1,r2){
                chrome.proxy.settings.set({ 
                    value: '''+cfgscript+''', 
                    scope: 'regular', }, function(e){ r1(e) })
            })
            '''
            err = self.run_js(finscript)
            if err:
                raise Exception('set proxy:' + json.dumps(err))
    class ExtensionManager:
        def __init__(self, root):
            self.root = root
            self.e = None
        def attach(self, c):
            c.set_proxy = self.set_proxy
        def set_proxy(self, p=None, method='PROXY', script=None):
            # Usually there is no need to configure script, script is actually an emergency backup parameter
            # Perhaps in some cases, someone may need to customize and configure some bypass lists or handle some special proxy modes.
            t = self.root.rootchrome.new_tab(False)
            t.get(wvurl)
            t.close()
            while not self.e:
                time.sleep(0.1)
            self.e.set_proxy(p=p, method=method, script=script)
        def set_extension(self, e):
            if self.e:
                self.e.tools.is_running = False
                self.e.ws.close()
            self.e = e
    class Root:
        def __init__(self, verison, iframes):
            self.pool = Pool(10)
            self.id = 0
            self.verison = verison
            self.iframes = iframes
            self.active = None
            self.new_tab_frame = {}
            self.create_tab_must_be_single = queue.Queue(1)
            self.tabs = []
            self.is_init = True
            self.init_sign = 0
            self.ws = create_connection_saf(verison['webSocketDebuggerUrl'], enable_multithread=True, suppress_origin=True)
            self.logger = Logger('[[ ---------- ROOT ---------- ]]', debug)
            self.cdper = CoreCDP(self.ws, self, self.logger)
            self.cdper.attach(self)
            self.extension = ExtensionManager(self)
            self.extension.set_extension(self._get_extension())
            self.cdp("Target.setAutoAttach", {
                "autoAttach": True,  
                "waitForDebuggerOnStart": False,  
                "flatten": True,
            })
            self.set_method_callback('Target.attachedToTarget', self.Target_attachedToTarget)
            # self.cdp("Target.setDiscoverTargets", { "discover": True })
        def filter_extension(self, tinfo):
            return tinfo['url'].startswith('chrome-extension://') and tinfo['url'].endswith('/vvv.js')
        def _wid(self):
            return self.cdp('Browser.getWindowForTarget', {"targetId":self.tabs[0].frameId})['windowId']
        def set_rect(self, rect):
            self.cdp('Browser.setWindowBounds', {"windowId":self._wid(),"bounds":{"left":rect[0],"top":rect[1],"width":rect[2],"height":rect[3]}})
        def set_fullscreen(self, tg=True):
            self.cdp('Browser.setWindowBounds', {'windowId':self._wid(),'bounds':{'windowState':'fullscreen' if tg else 'normal'}})
        def set_maxscreen(self, tg=True):
            self.cdp('Browser.setWindowBounds', {'windowId':self._wid(),'bounds':{'windowState':'maximized' if tg else 'normal'}})
        def _new_driver(self, background):
            tid = self.cdp('Target.createTarget', {"url": "about:blank", "background": background})['targetId']
            tgap = 0.03
            while True:
                if self.new_tab_frame.get(tid):
                    break
                time.sleep(tgap)
                tgap = tgap * 1.3
            return self.new_tab_frame.pop(tid)
        def quit(self):
            self.cdp('Browser.close')
        def _get_extension(self):
            for tinfo in self.cdp('Target.getTargets')['targetInfos']:
                if self.filter_extension(tinfo):
                    return ExtensionConn({
                        'webSocketDebuggerUrl': make_dev_page_url(tinfo['targetId']),
                        'id': tinfo['targetId'],
                        'type': tinfo['type'],
                        'url': tinfo['url'],
                    }, self)
        def Target_attachedToTarget(self, rdata):
            params = rdata['params']
            sessionId = params.get('sessionId')
            targetInfo = params.get('targetInfo')
            url = targetInfo.get('url')
            d = {
                'webSocketDebuggerUrl': make_dev_page_url(targetInfo['targetId']),
                'id': targetInfo['targetId'],
                'type': targetInfo['type'],
                'url': url,
            }
            if url.startswith('chrome-extension://') and url.endswith('/vvv.js'):
                self.extension.set_extension(ExtensionConn(d, self))
                return
            # TODO
            # now, Page.addScriptToEvaluateOnNewDocument not fast. cannot work on click open url.
            f = RootFrame(d, self, is_auto_create=True)
            if targetInfo.get('openerFrameId'):
                # TODO
                # think about how to manager this. bind root? or rootframe?
                pass
            else:
                self.new_tab_frame[targetInfo['targetId']] = f
            self.cdp('Runtime.runIfWaitingForDebugger', sessionId=sessionId)
            self.cdp('Target.detachFromTarget', sessionId=sessionId)
        def _add_init_check(self):
            if self.is_init:
                self.init_sign += 1
        def _del_init_check(self):
            if self.is_init:
                self.init_sign -= 1
        def get_new_id(self):
            self.id += 1
            return self.id
        def add_root_frame(self, f):
            if not self.active and f.type == 'page':
                self.active = f
            self.tabs.append(f)
            self.trav_init_tree(f)
            self.trav_remote_tree(f)
        def add_common_frame(self, rootf, finfo, sessionId=None):
            f = self.trav_frame(finfo['frameId'])
            if f:
                if finfo.get("contextId"): f.contextId = finfo.get("contextId")
                if finfo.get("uniqueId"):  f.uniqueId = finfo.get("uniqueId")
                if finfo.get('sessionId'): f.sessionId = finfo.get('sessionId')
                f.frameId = finfo['frameId']
            else:
                pf = finfo.get('parent')
                if not pf:
                    # TODO
                    # This branch is only taken during the initialization phase, when the frame has not yet entered object management.
                    return
                lf = AbsFrame(rootf, {
                    "contextId": finfo.get("contextId"),
                    "uniqueId": finfo.get("uniqueId"),
                    "frameId": finfo['frameId'],
                    "sessionId": getattr(pf, 'sessionId', None),
                    "parent": pf,
                })
                pf.frames.append(lf)
        def trav_remote_tree(self, pf):
            for f in self.iframes:
                if f['parentId'] == pf.frameId:
                    lf = AbsFrame(pf, {
                        "frameId": f['id'],
                        "parent": pf,
                        "url": f['url'],
                    })
                    pf.frames.append(lf)
        def trav_init_tree(self, f, rootf=None, sessionId=None):
            t = f.cdp('Page.getFrameTree')
            def _trav(t, pf, rootf):
                if 'frame' in t:
                    url = t['frame']['url']
                    frameId = t['frame']['id']
                    if frameId != f.frameId:
                        lf = AbsFrame(rootf, {
                            "url": url,
                            "contextId": None,
                            "uniqueId": None,
                            "sessionId": sessionId,
                            "frameId": frameId,
                            "parent": pf,
                        })
                        pf.frames.append(lf)
                        pf = lf
                if 'childFrames' in t:
                    for i in t['childFrames']:
                        _trav(i, pf, rootf)
            _trav(t['frameTree'], f, rootf or f)
            if not rootf and not sessionId:
                f.url = t['frameTree']['frame']['url']
        def trav_frame(self, kdata, key='frameId'):
            def _trav(flist):
                for f in flist:
                    if getattr(f, key, None) == kdata:
                        return f
                    else:
                        r = _trav(f.frames)
                        if r:
                            return r
            return _trav(self.tabs)
        def flat_child_frames(self, flist=None):
            flst = []
            def _trav(flist):
                for f in flist:
                    flst.append(f)
                    _trav(f.frames)
            _trav(flist)
            return flst
    wurl = 'http://{}:{}/json'.format(hostname, port)
    wvurl = 'http://{}:{}/json/version'.format(hostname, port)
    wslist = myget(wurl)
    for idx in range(len(wslist)):
        wslist[idx]['webSocketDebuggerUrl'] = adj_wsurl(wslist[idx]['webSocketDebuggerUrl'])
    verison = myget(wvurl)
    verison['webSocketDebuggerUrl'] = adj_wsurl(verison['webSocketDebuggerUrl'])
    iframes = [i for i in wslist if i['type'] == 'iframe']
    root = Root(verison, iframes)
    for wsinfo in wslist: RootFrame(wsinfo, root)
    start = perf_counter()
    while root.init_sign:
        if perf_counter() - start > 2.5:
            break
        time.sleep(0.1)
    root.is_init = False
    return root
# ----------------------------------------------------------------------------------------------------
import sys
import re
import time
import json
import shutil
import socket
import hashlib
import platform
from os import environ, path, cpu_count, getenv
from platform import system
from tempfile import gettempdir
from pathlib import Path
from shutil import rmtree
from subprocess import Popen, DEVNULL
def find_chrome(path):
    def get_win_chrome_path():
        d = Path('C:\\Program Files\\Google\\Chrome\\Application')
        if d.exists() and (d / 'chrome.exe').exists():
            return d
        import os, winreg
        sub_key = [
            'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', 
            'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
        ]
        def get_install_list(key, root):
            try:
                _key = winreg.OpenKey(root, key, 0, winreg.KEY_ALL_ACCESS)
                for j in range(0, winreg.QueryInfoKey(_key)[0]-1):
                    try:
                        each_key = winreg.OpenKey(root, key + '\\' + winreg.EnumKey(_key, j), 0, winreg.KEY_ALL_ACCESS)
                        displayname, REG_SZ = winreg.QueryValueEx(each_key, 'DisplayName')
                        install_loc, REG_SZ = winreg.QueryValueEx(each_key, 'InstallLocation')
                        display_var, REG_SZ = winreg.QueryValueEx(each_key, 'DisplayVersion')
                        yield displayname, install_loc, display_var
                    except WindowsError:
                        pass
            except:
                pass
        for key in sub_key:
            for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                for name, local, var in get_install_list(key, root):
                    if name == 'Google Chrome':
                        return Path(local)
    if path:
        if Path(path).exists():
            return Path(path)
        return None
    sys = system().lower()
    if sys in ('macos', 'darwin', 'linux'):
        for p in (
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            '/usr/bin/google-chrome', 
            '/opt/google/chrome/google-chrome',
            '/user/lib/chromium-browser/chromium-browser'
        ):
            if Path(p).exists():
                return p
        return None
    elif sys != 'windows':
        return None
    return get_win_chrome_path()
def try_some(func, times=7, timegap=0.15):
    for i in range(times):
        try:
            func()
            return False
        except:
            time.sleep(timegap)
            continue
    return True
def find_free_port(start_port=9233, end_port=60000):
    class EnvPRNG:
        def __init__(self):
            self.seed = int(self.get_env_fingerprint(), 16)
            self.state = self.seed
        def get_env_fingerprint(self):
            try:
                system = platform.system()
                release = platform.release()
                version = platform.version()
                arch = platform.machine()
                python_version = platform.python_version()
                cpu_n = cpu_count()
                raw = f"{system}-{release}-{version}-{arch}-{python_version}-{cpu_n}-{getenv('USERNAME','')}-{getenv('USER','')}"
            except:
                raw = "vvv"
            return hashlib.sha256(raw.encode('utf-8')).hexdigest()
        def rand(self):
            self.state = (1664525 * self.state + 1013904223) % (2**32)
            return self.state
        def randint(self, a, b):
            return a + self.rand() % (b - a + 1)
    erdn = EnvPRNG()
    for _ in range(200):
        try:
            port = erdn.randint(start_port, end_port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise ValueError("no free port ({}-{})".format(start_port, end_port))
def is_port_open(port, host="127.0.0.1", timeout=0.01):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except socket.timeout:
        return False
def get_default_user_data_dir():
    home = path.expanduser("~")
    if sys.platform.startswith("win"):
        return path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
    elif sys.platform == "darwin":
        return path.join(home, "Library", "Application Support", "Google", "Chrome")
    elif sys.platform.startswith("linux"):
        return path.join(home, ".config", "google-chrome")
    else:
        raise Exception("Unsupported platform")
class Debug:
    def __init__(self, debug):
        self.all = False
        self.plist = [
            'env','rest','mouse','proxy',
            'Network','Fetch','Page','DOM','Target','Runtime','Input','Debugger','DOMDebugger',
        ]
        if type(debug) == str: self.parse_str(debug)
        if type(debug) == bool: self.parse_bool(debug)
        self._bool = self.has_Debug()
    def __call__(self, tp):
        if self.all:
            return True
        if type(tp) == str:
            return getattr(self, tp.split('.')[0], None)
    def __bool__(self):
        return self._bool
    def parse_str(self, debug):
        self.parse_bool(False)
        dbgls = re.split(r'[,;|/]', debug)
        for p in dbgls:
            if p in self.plist:
                setattr(self, p, True)
    def parse_bool(self, debug):
        for p in self.plist: setattr(self, p, debug)
        self.all = debug
    def has_Debug(self):
        tg = False
        for p in self.plist: 
            if getattr(self, p):
                tg = True
        return tg
class Chrome:
    def __init__(self, 
            debug = False,
            path = None,
            port = None,
            hostname = '127.0.0.1',
            user_path = None,
            use_system_user_path = False, 
            verison_check = True,
            headless = False,
            incognito = False,
            user_agent = None,
            arguments = [],
            proxy = None,
            extension = None,
        ):
        self.debug = Debug(debug)
        self.path = find_chrome(path)
        self.verison_check = verison_check
        self.headless = headless
        self.user_agent = user_agent
        self.incognito = incognito
        self.arguments = arguments
        self.proxy = proxy
        self.extension = extension
        self._user_cmd = self._make_user_cmd()
        if not self.path:
            raise Exception('chrome path not find.')
        self.port = port or find_free_port()
        self.hostname = hostname
        self.user_path_mode = None
        # chrome 136+
        # disable default user path to remote contral
        if use_system_user_path:
            self.user_path_mode = 'sys'
            user_path = Path(get_default_user_data_dir())
        if user_path:
            self.user_path_mode = 'user'
            user_path = Path(user_path)
            if not user_path.exists() or not user_path.is_dir():
                raise Exception('user path not exist.')
        else:
            self.user_path_mode = 'default'
        if self.debug.env:
            print('[*]', 'user_path_mode', self.user_path_mode)
        self.user_path = user_path or Path(gettempdir()) / 'vchrome' / 'cache_user_temp' / 'userData' / str(self.port)
        if self.debug.env:
            print('[*]', self.user_path)
        self._connect()
    def _cmd_check_in(self, ls, s):
        for i in ls:
            if i.startswith(s.split('=')[0]):
                return i, s
    def _make_user_cmd(self):
        _user_cmd = self.arguments
        if self.headless and not self._cmd_check_in(_user_cmd, '--headless'):
            # TODO
            # think about CDP:Input Event compatible.
            _user_cmd.append('--headless')
        if self.incognito and not self._cmd_check_in(_user_cmd, '--incognito'):
            _user_cmd.append('--incognito')
        if self.user_agent and not self._cmd_check_in(_user_cmd, '--user-agent'):
            _user_cmd.append('--user-agent=' + json.dumps(self.user_agent))
        if self.proxy and not self._cmd_check_in(_user_cmd, '--proxy-server'):
            _user_cmd.append('--proxy-server=' + self.proxy)
        if self.extension:
            if type(self.extension) == str:
                ep = self.extension
                _user_cmd.append('--disable-extensions-except=' + ep)
                _user_cmd.append('--load-extension=' + ep)
            if type(self.extension) == list:
                for ep in self.extension:
                    _user_cmd.append('--disable-extensions-except=' + ep)
                    _user_cmd.append('--load-extension=' + ep)
        return _user_cmd
    def new_tab(self, foreground=True):
        class Chrome:
            def __init__(self, root, dr):
                self.root = root
                self.dr = dr
                self.dr.browser.attach(self)
            def __str__(self):
                return str(self.dr.tree_view())
            def new_tab(self, foreground=True):
                return Chrome(self.root, self.dr.root._new_driver(not foreground))
            frames = property(lambda s:s.dr.frames)
            cookies = property(lambda s:s.get_cookies(), lambda s,v:s.set_cookies(v))
            dialog = property(lambda s:s.get_dialog(), lambda s,v:s.set_dialog(v))
        return Chrome(self.root, self.dr.root._new_driver(not foreground))
    frames = property(lambda s:s.dr.frames)
    cookies = property(lambda s:s.get_cookies(), lambda s,v:s.set_cookies(v))
    dialog = property(lambda s:s.get_dialog(), lambda s,v:s.set_dialog(v))
    def _check_lower_version(self):
        try:
            verison = self.dr.root.verison
            if verison and verison.get('Browser'):
                ver = int(verison.get('Browser').split('/')[-1].split('.')[0])
                # Restricting Chrome versions to prevent abnormal states
                if ver < 100:
                    return True
        except: pass
        return False
    def _connect(self):
        if not is_port_open(self.port):
            self._init()
        self.root = cdp_client(self.hostname, port=self.port, debug=self.debug)
        self.root.rootchrome = self
        self.dr = self.root.active
        if not self.dr:
            raise Exception('maybe single devtools not close.')
        self.dr.browser.attach(self)
        if self.verison_check and self._check_lower_version():
            raise Exception('chrome verison is less then 100. not reliable. you can set (verison_check=False) for ignore this alert.')
        if self.debug.mouse:
            jscode = r'''
            function f(e){
              var nDiv = document.createElement('div')
              var e = e || window.event
              Object.assign(nDiv.style, {
                position: 'fixed',
                left: `${e.clientX+1}px`,
                top: `${e.clientY+1}px`,
                width: '5px',
                height: '5px',
                backgroundColor: 'red',
                borderRadius: '50%',
                pointerEvents: 'none',
                userSelect: 'none',
                webkitUserSelect: 'none',
                mozUserSelect: 'none',
                msUserSelect: 'none',
                zIndex: '2147483647',
                willChange: 'transform',
              });
              document.body.appendChild(nDiv)
              setTimeout(function(){ nDiv.remove(); },1000)
            }
            document.addEventListener('mousemove', f, true)
            document.addEventListener('mousedown', f, true)
            document.addEventListener('mouseup', f, true)
            '''
            self.init_js(jscode)
    def _merge_config(self, cmd):
        # The Chrome command line is sequence sensitive and comes with conflict resolution. I just need to add my new command at the end. (Tail instruction priority)
        return cmd[:-1] + self._user_cmd + cmd[-1:]
    def _make_files_extension(self, path):
        def writeF(p, s):
            with open(p, 'w', encoding='utf8') as f:
                f.write(s)
        e = path / 'v_extension'
        e.mkdir(parents=True, exist_ok=True)
        d = {
            "name": "vvv", "version": "0.0.0", "description": "vvv",
            "permissions": [ "proxy" ],
            "background": { "service_worker": "vvv.js" },
            "content_scripts": [{
                "matches": ["<all_urls>"],
                "js": ["content_script.js"],
                "run_at": "document_idle"
            }],
            "host_permissions": [ "<all_urls>" ],
            "manifest_version": 3
        }
        writeF(e / 'manifest.json', json.dumps(d))
        writeF(e / 'content_script.js', '''
        var port = chrome.runtime.connect({ name: 'keepAlive' });
        port.postMessage({ ping: Date.now() })
        ''')
        writeF(e / 'vvv.js', '''
        var ctime;
        chrome.runtime.onConnect.addListener((port) => {
            if (port.name === 'keepAlive') { port.onMessage.addListener((msg) => { ctime = msg }); }
        });
        ''')
        return e
    def _prepare_cmd(self):
        # TODO
        # maybe need check writable compatible.
        path = self.path
        user_path = self.user_path
        port = self.port
        user_path_mode = self.user_path_mode
        p = Path(path)
        p = str(p / 'chrome') if p.is_dir() else str(path)
        u = '--user-data-dir='
        args = []
        if user_path_mode == 'sys':
            args.append(u + str(user_path))
        if user_path_mode == 'user':
            args.append(u + str(user_path))
        if user_path_mode == 'default':
            if user_path.exists():
                if try_some(lambda:shutil.rmtree(user_path)):
                    print('[*] error remove cache', user_path)
            user_path.mkdir(parents=True, exist_ok=True)
            args.append(u + str(user_path))
        ep = self._make_files_extension(user_path)
        # args.append('--disable-extensions-except=' + str(ep))
        args.append('--load-extension=' + str(ep))
        return [
            p, 
            '--remote-debugging-port=' + str(port), 
            '--no-default-browser-check', 
            '--disable-suggestions-ui', 
            '--no-first-run', 
            '--disable-infobars', 
            '--disable-popup-blocking', 
            '--hide-crash-restore-bubble', 
            '--remote-allow-origins=*', 
            '--enable-features=NetworkService',
            '--enable-features=NetworkServiceInProcess',
            '--disable-features=PaymentRequest',
            '--disable-features=DigitalGoodsApi',
            '--disable-features=PrivacySandboxSettings4',
            '--disable-features=DisableLoadExtensionCommandLineSwitch', # Starting from a higher version, the command line to load plugins has been disabled. This line needs to be added
            '--disable-component-extensions-with-background-pages',
            # # Disable automatic password saving prompt, the new version is invalid
            # '--password-store=basic',
            # # Disable automatic password saving prompt, the new version is invalid
            # '--disable-features=AutofillEnableSavePasswordBubble',
            # '--disable-features=PasswordManagerOnboarding',
            # '--disable-features=PasswordImport',
            # '--disable-features=PasswordManagerRedesign',
            # # Disable automatic password saving prompt, the new version is invalid
            # '--disable-save-password-bubble',
            # '--disable-autofill',
            # '--disable-password-manager-reauthentication',
            # '--disable-autofill-keyboard-accessory-view',
            # from pyppeteer
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-breakpad',
            '--disable-browser-side-navigation',
            '--disable-client-side-phishing-detection',
            '--disable-default-apps',
            '--disable-dev-shm-usage',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-sync',
            '--disable-translate',
            '--metrics-recording-only',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            # '--disable-component-update',
            # '--site-per-process',
            # '--disable-extensions',
            # '--disable-web-security',
            *args,
            'about:blank',
            # # This part may be related to performance
            # '--disable-extensions',
            # '--disable-gpu',
            # '--no-sandbox',
            # '--disable-dev-shm-usage',
        ]
    def _init(self):
        def _start_browser(cmd):
            try:
                return Popen(cmd, shell=False, stdout=DEVNULL, stderr=DEVNULL)
            except FileNotFoundError:
                raise FileNotFoundError('browser not find.')
        cmd = self._prepare_cmd()
        cmd = self._merge_config(cmd)
        if self.debug.env:
            print('[*]', json.dumps(cmd, indent=4))
        _start_browser(cmd)
    def __str__(self):
        return str(self.dr.tree_view())
# ----------------------------------------------------------------------------------------------------
"""
websocket - WebSocket client library for Python

Copyright 2024 engn33r

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# websocket-client:1.8.0
import array
import os
import struct
import sys
from threading import Lock
from typing import Callable, Optional, Union
class WebSocketException(Exception):pass
class WebSocketProtocolException(WebSocketException):pass
class WebSocketPayloadException(WebSocketException):pass
class WebSocketConnectionClosedException(WebSocketException):pass
class WebSocketTimeoutException(WebSocketException):pass
class WebSocketProxyException(WebSocketException):pass
class WebSocketBadStatusException(WebSocketException):
    def __init__(self, message: str, status_code: int, status_message=None, resp_headers=None, resp_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.resp_headers = resp_headers
        self.resp_body = resp_body
class WebSocketAddressException(WebSocketException):pass
from typing import Union
class NoLock:
    def __enter__(self) -> None:pass
    def __exit__(self, exc_type, exc_value, traceback) -> None:pass
try:
    from wsaccel.utf8validator import Utf8Validator
    def _validate_utf8(utfbytes: Union[str, bytes]) -> bool:
        result: bool = Utf8Validator().validate(utfbytes)[0]
        return result
except ImportError:
    _UTF8_ACCEPT = 0
    _UTF8_REJECT = 12
    _UTF8D = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 10, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 11, 6, 6, 6, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 0, 12, 24, 36, 60, 96, 84, 12, 12, 12, 48, 72, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 0, 12, 12, 12, 12, 12, 0, 12, 0, 12, 12, 12, 24, 12, 12, 12, 12, 12, 24, 12, 24, 12, 12, 12, 12, 12, 12, 12, 12, 12, 24, 12, 12, 12, 12, 12, 24, 12, 12, 12, 12, 12, 12, 12, 24, 12, 12, 12, 12, 12, 12, 12, 12, 12, 36, 12, 36, 12, 12, 12, 36, 12, 12, 12, 12, 12, 36, 12, 36, 12, 12, 12, 36, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
    def _decode(state: int, codep: int, ch: int) -> tuple:
        tp = _UTF8D[ch]
        codep = ch & 63 | codep << 6 if state != _UTF8_ACCEPT else 255 >> tp & ch
        state = _UTF8D[256 + state + tp]
        return (state, codep)
    def _validate_utf8(utfbytes: Union[str, bytes]) -> bool:
        state = _UTF8_ACCEPT
        codep = 0
        for i in utfbytes:
            (state, codep) = _decode(state, codep, int(i))
            if state == _UTF8_REJECT:
                return False
        return True
def validate_utf8(utfbytes: Union[str, bytes]) -> bool:
    return _validate_utf8(utfbytes)
def extract_err_message(exception: Exception) -> Union[str, None]:
    if exception.args:
        exception_message: str = exception.args[0]
        return exception_message
    else:
        return None
def extract_error_code(exception: Exception) -> Union[int, None]:
    if exception.args and len(exception.args) > 1:
        return exception.args[0] if isinstance(exception.args[0], int) else None
try:
    from wsaccel.xormask import XorMaskerSimple
    def _mask(mask_value: array.array, data_value: array.array) -> bytes:
        mask_result: bytes = XorMaskerSimple(mask_value).process(data_value)
        return mask_result
except ImportError:
    native_byteorder = sys.byteorder
    def _mask(mask_value: array.array, data_value: array.array) -> bytes:
        datalen = len(data_value)
        int_data_value = int.from_bytes(data_value, native_byteorder)
        int_mask_value = int.from_bytes(mask_value * (datalen // 4) + mask_value[:datalen % 4], native_byteorder)
        return (int_data_value ^ int_mask_value).to_bytes(datalen, native_byteorder)
STATUS_NORMAL = 1000
STATUS_GOING_AWAY = 1001
STATUS_PROTOCOL_ERROR = 1002
STATUS_UNSUPPORTED_DATA_TYPE = 1003
STATUS_STATUS_NOT_AVAILABLE = 1005
STATUS_ABNORMAL_CLOSED = 1006
STATUS_INVALID_PAYLOAD = 1007
STATUS_POLICY_VIOLATION = 1008
STATUS_MESSAGE_TOO_BIG = 1009
STATUS_INVALID_EXTENSION = 1010
STATUS_UNEXPECTED_CONDITION = 1011
STATUS_SERVICE_RESTART = 1012
STATUS_TRY_AGAIN_LATER = 1013
STATUS_BAD_GATEWAY = 1014
STATUS_TLS_HANDSHAKE_ERROR = 1015
VALID_CLOSE_STATUS = (STATUS_NORMAL, STATUS_GOING_AWAY, STATUS_PROTOCOL_ERROR, STATUS_UNSUPPORTED_DATA_TYPE, STATUS_INVALID_PAYLOAD, STATUS_POLICY_VIOLATION, STATUS_MESSAGE_TOO_BIG, STATUS_INVALID_EXTENSION, STATUS_UNEXPECTED_CONDITION, STATUS_SERVICE_RESTART, STATUS_TRY_AGAIN_LATER, STATUS_BAD_GATEWAY)
class ABNF:
    OPCODE_CONT = 0
    OPCODE_TEXT = 1
    OPCODE_BINARY = 2
    OPCODE_CLOSE = 8
    OPCODE_PING = 9
    OPCODE_PONG = 10
    OPCODES = (OPCODE_CONT, OPCODE_TEXT, OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG)
    OPCODE_MAP = {OPCODE_CONT: 'cont', OPCODE_TEXT: 'text', OPCODE_BINARY: 'binary', OPCODE_CLOSE: 'close', OPCODE_PING: 'ping', OPCODE_PONG: 'pong'}
    LENGTH_7 = 126
    LENGTH_16 = 1 << 16
    LENGTH_63 = 1 << 63
    def __init__(self, fin: int=0, rsv1: int=0, rsv2: int=0, rsv3: int=0, opcode: int=OPCODE_TEXT, mask_value: int=1, data: Union[str, bytes, None]='') -> None:
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.mask_value = mask_value
        if data is None:
            data = ''
        self.data = data
        self.get_mask_key = os.urandom
    def validate(self, skip_utf8_validation: bool=False) -> None:
        if self.rsv1 or self.rsv2 or self.rsv3:
            raise WebSocketProtocolException('rsv is not implemented, yet')
        if self.opcode not in ABNF.OPCODES:
            raise WebSocketProtocolException('Invalid opcode %r', self.opcode)
        if self.opcode == ABNF.OPCODE_PING and (not self.fin):
            raise WebSocketProtocolException('Invalid ping frame.')
        if self.opcode == ABNF.OPCODE_CLOSE:
            l = len(self.data)
            if not l:
                return
            if l == 1 or l >= 126:
                raise WebSocketProtocolException('Invalid close frame.')
            if l > 2 and (not skip_utf8_validation) and (not validate_utf8(self.data[2:])):
                raise WebSocketProtocolException('Invalid close frame.')
            code = 256 * int(self.data[0]) + int(self.data[1])
            if not self._is_valid_close_status(code):
                raise WebSocketProtocolException('Invalid close opcode %r', code)
    @staticmethod
    def _is_valid_close_status(code: int) -> bool:
        return code in VALID_CLOSE_STATUS or 3000 <= code < 5000
    def __str__(self) -> str:
        return f'fin={self.fin} opcode={self.opcode} data={self.data}'
    @staticmethod
    def create_frame(data: Union[bytes, str], opcode: int, fin: int=1) -> 'ABNF':
        if opcode == ABNF.OPCODE_TEXT and isinstance(data, str):
            data = data.encode('utf-8')
        return ABNF(fin, 0, 0, 0, opcode, 1, data)
    def format(self) -> bytes:
        if any((x not in (0, 1) for x in [self.fin, self.rsv1, self.rsv2, self.rsv3])):
            raise ValueError('not 0 or 1')
        if self.opcode not in ABNF.OPCODES:
            raise ValueError('Invalid OPCODE')
        length = len(self.data)
        if length >= ABNF.LENGTH_63:
            raise ValueError('data is too long')
        frame_header = chr(self.fin << 7 | self.rsv1 << 6 | self.rsv2 << 5 | self.rsv3 << 4 | self.opcode).encode('latin-1')
        if length < ABNF.LENGTH_7:
            frame_header += chr(self.mask_value << 7 | length).encode('latin-1')
        elif length < ABNF.LENGTH_16:
            frame_header += chr(self.mask_value << 7 | 126).encode('latin-1')
            frame_header += struct.pack('!H', length)
        else:
            frame_header += chr(self.mask_value << 7 | 127).encode('latin-1')
            frame_header += struct.pack('!Q', length)
        if not self.mask_value:
            if isinstance(self.data, str):
                self.data = self.data.encode('utf-8')
            return frame_header + self.data
        mask_key = self.get_mask_key(4)
        return frame_header + self._get_masked(mask_key)
    def _get_masked(self, mask_key: Union[str, bytes]) -> bytes:
        s = ABNF.mask(mask_key, self.data)
        if isinstance(mask_key, str):
            mask_key = mask_key.encode('utf-8')
        return mask_key + s
    @staticmethod
    def mask(mask_key: Union[str, bytes], data: Union[str, bytes]) -> bytes:
        if data is None:
            data = ''
        if isinstance(mask_key, str):
            mask_key = mask_key.encode('latin-1')
        if isinstance(data, str):
            data = data.encode('latin-1')
        return _mask(array.array('B', mask_key), array.array('B', data))
class frame_buffer:
    _HEADER_MASK_INDEX = 5
    _HEADER_LENGTH_INDEX = 6
    def __init__(self, recv_fn: Callable[[int], int], skip_utf8_validation: bool) -> None:
        self.recv = recv_fn
        self.skip_utf8_validation = skip_utf8_validation
        self.recv_buffer: list = []
        self.clear()
        self.lock = Lock()
    def clear(self) -> None:
        self.header: Optional[tuple] = None
        self.length: Optional[int] = None
        self.mask_value: Union[bytes, str, None] = None
    def has_received_header(self) -> bool:
        return self.header is None
    def recv_header(self) -> None:
        header = self.recv_strict(2)
        b1 = header[0]
        fin = b1 >> 7 & 1
        rsv1 = b1 >> 6 & 1
        rsv2 = b1 >> 5 & 1
        rsv3 = b1 >> 4 & 1
        opcode = b1 & 15
        b2 = header[1]
        has_mask = b2 >> 7 & 1
        length_bits = b2 & 127
        self.header = (fin, rsv1, rsv2, rsv3, opcode, has_mask, length_bits)
    def has_mask(self) -> Union[bool, int]:
        if not self.header:
            return False
        header_val: int = self.header[frame_buffer._HEADER_MASK_INDEX]
        return header_val
    def has_received_length(self) -> bool:
        return self.length is None
    def recv_length(self) -> None:
        bits = self.header[frame_buffer._HEADER_LENGTH_INDEX]
        length_bits = bits & 127
        if length_bits == 126:
            v = self.recv_strict(2)
            self.length = struct.unpack('!H', v)[0]
        elif length_bits == 127:
            v = self.recv_strict(8)
            self.length = struct.unpack('!Q', v)[0]
        else:
            self.length = length_bits
    def has_received_mask(self) -> bool:
        return self.mask_value is None
    def recv_mask(self) -> None:
        self.mask_value = self.recv_strict(4) if self.has_mask() else ''
    def recv_frame(self) -> ABNF:
        with self.lock:
            if self.has_received_header():
                self.recv_header()
            (fin, rsv1, rsv2, rsv3, opcode, has_mask, _) = self.header
            if self.has_received_length():
                self.recv_length()
            length = self.length
            if self.has_received_mask():
                self.recv_mask()
            mask_value = self.mask_value
            payload = self.recv_strict(length)
            if has_mask:
                payload = ABNF.mask(mask_value, payload)
            self.clear()
            frame = ABNF(fin, rsv1, rsv2, rsv3, opcode, has_mask, payload)
            frame.validate(self.skip_utf8_validation)
        return frame
    def recv_strict(self, bufsize: int) -> bytes:
        shortage = bufsize - sum(map(len, self.recv_buffer))
        while shortage > 0:
            bytes_ = self.recv(min(16384, shortage))
            self.recv_buffer.append(bytes_)
            shortage -= len(bytes_)
        unified = b''.join(self.recv_buffer)
        if shortage == 0:
            self.recv_buffer = []
            return unified
        else:
            self.recv_buffer = [unified[bufsize:]]
            return unified[:bufsize]
class continuous_frame:
    def __init__(self, fire_cont_frame: bool, skip_utf8_validation: bool) -> None:
        self.fire_cont_frame = fire_cont_frame
        self.skip_utf8_validation = skip_utf8_validation
        self.cont_data: Optional[list] = None
        self.recving_frames: Optional[int] = None
    def validate(self, frame: ABNF) -> None:
        if not self.recving_frames and frame.opcode == ABNF.OPCODE_CONT:
            raise WebSocketProtocolException('Illegal frame')
        if self.recving_frames and frame.opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY):
            raise WebSocketProtocolException('Illegal frame')
    def add(self, frame: ABNF) -> None:
        if self.cont_data:
            self.cont_data[1] += frame.data
        else:
            if frame.opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY):
                self.recving_frames = frame.opcode
            self.cont_data = [frame.opcode, frame.data]
        if frame.fin:
            self.recving_frames = None
    def is_fire(self, frame: ABNF) -> Union[bool, int]:
        return frame.fin or self.fire_cont_frame
    def extract(self, frame: ABNF) -> tuple:
        data = self.cont_data
        self.cont_data = None
        frame.data = data[1]
        if not self.fire_cont_frame and data[0] == ABNF.OPCODE_TEXT and (not self.skip_utf8_validation) and (not validate_utf8(frame.data)):
            raise WebSocketPayloadException(f'cannot decode: {repr(frame.data)}')
        return (data[0], frame)
import inspect
import selectors
import socket
import threading
import time
from typing import Any, Callable, Optional, Union
import logging
_logger = logging.getLogger('websocket')
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record) -> None:pass
_logger.addHandler(NullHandler())
_traceEnabled = False
def enableTrace(traceable: bool, handler: logging.StreamHandler=logging.StreamHandler(), level: str='DEBUG') -> None:
    global _traceEnabled
    _traceEnabled = traceable
    if traceable:
        _logger.addHandler(handler)
        _logger.setLevel(getattr(logging, level))
def dump(title: str, message: str) -> None:
    if _traceEnabled:
        _logger.debug(f'--- {title} ---')
        _logger.debug(message)
        _logger.debug('-----------------------')
def error(msg: str) -> None:
    _logger.error(msg)
def warning(msg: str) -> None:
    _logger.warning(msg)
def debug(msg: str) -> None:
    _logger.debug(msg)
def info(msg: str) -> None:
    _logger.info(msg)
def trace(msg: str) -> None:
    if _traceEnabled:
        _logger.debug(msg)
def isEnabledForError() -> bool:
    return _logger.isEnabledFor(logging.ERROR)
def isEnabledForDebug() -> bool:
    return _logger.isEnabledFor(logging.DEBUG)
def isEnabledForTrace() -> bool:
    return _traceEnabled
import socket
import struct
import threading
import time
from typing import Optional, Union
import hashlib
import hmac
import os
from base64 import encodebytes as base64encode
from http import HTTPStatus
import http.cookies
from typing import Optional
class SimpleCookieJar:
    def __init__(self) -> None:
        self.jar: dict = {}
    def add(self, set_cookie: Optional[str]) -> None:
        if set_cookie:
            simple_cookie = http.cookies.SimpleCookie(set_cookie)
            for v in simple_cookie.values():
                if (domain := v.get('domain')):
                    if not domain.startswith('.'):
                        domain = f'.{domain}'
                    cookie = self.jar.get(domain) if self.jar.get(domain) else http.cookies.SimpleCookie()
                    cookie.update(simple_cookie)
                    self.jar[domain.lower()] = cookie
    def set(self, set_cookie: str) -> None:
        if set_cookie:
            simple_cookie = http.cookies.SimpleCookie(set_cookie)
            for v in simple_cookie.values():
                if (domain := v.get('domain')):
                    if not domain.startswith('.'):
                        domain = f'.{domain}'
                    self.jar[domain.lower()] = simple_cookie
    def get(self, host: str) -> str:
        if not host:
            return ''
        cookies = []
        for (domain, _) in self.jar.items():
            host = host.lower()
            if host.endswith(domain) or host == domain[1:]:
                cookies.append(self.jar.get(domain))
        return '; '.join(filter(None, sorted([f'{k}={v.value}' for cookie in filter(None, cookies) for (k, v) in cookie.items()])))
import errno
import os
import socket
from base64 import encodebytes as base64encode
import errno
import selectors
import socket
from typing import Union
try:
    import ssl
    from ssl import SSLError, SSLEOFError, SSLWantReadError, SSLWantWriteError
    HAVE_SSL = True
except ImportError:
    class SSLError(Exception):pass
    class SSLEOFError(Exception):pass
    class SSLWantReadError(Exception):pass
    class SSLWantWriteError(Exception):pass
    ssl = None
    HAVE_SSL = False
DEFAULT_SOCKET_OPTION = [(socket.SOL_TCP, socket.TCP_NODELAY, 1)]
if hasattr(socket, 'SO_KEEPALIVE'):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1))
if hasattr(socket, 'TCP_KEEPIDLE'):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPIDLE, 30))
if hasattr(socket, 'TCP_KEEPINTVL'):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPINTVL, 10))
if hasattr(socket, 'TCP_KEEPCNT'):
    DEFAULT_SOCKET_OPTION.append((socket.SOL_TCP, socket.TCP_KEEPCNT, 3))
_default_timeout = None
class sock_opt:
    def __init__(self, sockopt: list, sslopt: dict) -> None:
        if sockopt is None:
            sockopt = []
        if sslopt is None:
            sslopt = {}
        self.sockopt = sockopt
        self.sslopt = sslopt
        self.timeout = None
def setdefaulttimeout(timeout: Union[int, float, None]) -> None:
    global _default_timeout
    _default_timeout = timeout
def getdefaulttimeout() -> Union[int, float, None]:
    return _default_timeout
def recv(sock: socket.socket, bufsize: int) -> bytes:
    if not sock:
        raise WebSocketConnectionClosedException('socket is already closed.')
    def _recv():
        try:
            return sock.recv(bufsize)
        except SSLWantReadError:pass
        except socket.error as exc:
            error_code = extract_error_code(exc)
            if error_code not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                raise
        sel = selectors.DefaultSelector()
        sel.register(sock, selectors.EVENT_READ)
        r = sel.select(sock.gettimeout())
        sel.close()
        if r:
            return sock.recv(bufsize)
    try:
        if sock.gettimeout() == 0:
            bytes_ = sock.recv(bufsize)
        else:
            bytes_ = _recv()
    except TimeoutError:
        raise WebSocketTimeoutException('Connection timed out')
    except socket.timeout as e:
        message = extract_err_message(e)
        raise WebSocketTimeoutException(message)
    except SSLError as e:
        message = extract_err_message(e)
        if isinstance(message, str) and 'timed out' in message:
            raise WebSocketTimeoutException(message)
        else:
            raise
    if not bytes_:
        raise WebSocketConnectionClosedException('Connection to remote host was lost.')
    return bytes_
def recv_line(sock: socket.socket) -> bytes:
    line = []
    while True:
        c = recv(sock, 1)
        line.append(c)
        if c == b'\n':
            break
    return b''.join(line)
def send(sock: socket.socket, data: Union[bytes, str]) -> int:
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not sock:
        raise WebSocketConnectionClosedException('socket is already closed.')
    def _send():
        try:
            return sock.send(data)
        except SSLWantWriteError:pass
        except socket.error as exc:
            error_code = extract_error_code(exc)
            if error_code is None:
                raise
            if error_code not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                raise
        sel = selectors.DefaultSelector()
        sel.register(sock, selectors.EVENT_WRITE)
        w = sel.select(sock.gettimeout())
        sel.close()
        if w:
            return sock.send(data)
    try:
        if sock.gettimeout() == 0:
            return sock.send(data)
        else:
            return _send()
    except socket.timeout as e:
        message = extract_err_message(e)
        raise WebSocketTimeoutException(message)
    except Exception as e:
        message = extract_err_message(e)
        if isinstance(message, str) and 'timed out' in message:
            raise WebSocketTimeoutException(message)
        else:
            raise
import os
import socket
import struct
from typing import Optional
from urllib.parse import unquote, urlparse
def parse_url(url: str) -> tuple:
    if ':' not in url:
        raise ValueError('url is invalid')
    (scheme, url) = url.split(':', 1)
    parsed = urlparse(url, scheme='http')
    if parsed.hostname:
        hostname = parsed.hostname
    else:
        raise ValueError('hostname is invalid')
    port = 0
    if parsed.port:
        port = parsed.port
    is_secure = False
    if scheme == 'ws':
        if not port:
            port = 80
    elif scheme == 'wss':
        is_secure = True
        if not port:
            port = 443
    else:
        raise ValueError('scheme %s is invalid' % scheme)
    if parsed.path:
        resource = parsed.path
    else:
        resource = '/'
    if parsed.query:
        resource += f'?{parsed.query}'
    return (hostname, port, resource, is_secure)
DEFAULT_NO_PROXY_HOST = ['localhost', '127.0.0.1']
def _is_ip_address(addr: str) -> bool:
    try:
        socket.inet_aton(addr)
    except socket.error:
        return False
    else:
        return True
def _is_subnet_address(hostname: str) -> bool:
    try:
        (addr, netmask) = hostname.split('/')
        return _is_ip_address(addr) and 0 <= int(netmask) < 32
    except ValueError:
        return False
def _is_address_in_network(ip: str, net: str) -> bool:
    ipaddr: int = struct.unpack('!I', socket.inet_aton(ip))[0]
    (netaddr, netmask) = net.split('/')
    netaddr: int = struct.unpack('!I', socket.inet_aton(netaddr))[0]
    netmask = 4294967295 << 32 - int(netmask) & 4294967295
    return ipaddr & netmask == netaddr
def _is_no_proxy_host(hostname: str, no_proxy: Optional[list]) -> bool:
    if not no_proxy:
        if (v := os.environ.get('no_proxy', os.environ.get('NO_PROXY', '')).replace(' ', '')):
            no_proxy = v.split(',')
    if not no_proxy:
        no_proxy = DEFAULT_NO_PROXY_HOST
    if '*' in no_proxy:
        return True
    if hostname in no_proxy:
        return True
    if _is_ip_address(hostname):
        return any([_is_address_in_network(hostname, subnet) for subnet in no_proxy if _is_subnet_address(subnet)])
    for domain in [domain for domain in no_proxy if domain.startswith('.')]:
        if hostname.endswith(domain):
            return True
    return False
def get_proxy_info(hostname: str, is_secure: bool, proxy_host: Optional[str]=None, proxy_port: int=0, proxy_auth: Optional[tuple]=None, no_proxy: Optional[list]=None, proxy_type: str='http') -> tuple:
    if _is_no_proxy_host(hostname, no_proxy):
        return (None, 0, None)
    if proxy_host:
        if not proxy_port:
            raise WebSocketProxyException('Cannot use port 0 when proxy_host specified')
        port = proxy_port
        auth = proxy_auth
        return (proxy_host, port, auth)
    env_key = 'https_proxy' if is_secure else 'http_proxy'
    value = os.environ.get(env_key, os.environ.get(env_key.upper(), '')).replace(' ', '')
    if value:
        proxy = urlparse(value)
        auth = (unquote(proxy.username), unquote(proxy.password)) if proxy.username else None
        return (proxy.hostname, proxy.port, auth)
    return (None, 0, None)
try:
    from python_socks._errors import *
    from python_socks._types import ProxyType
    from python_socks.sync import Proxy
    HAVE_PYTHON_SOCKS = True
except:
    HAVE_PYTHON_SOCKS = False
    class ProxyError(Exception):pass
    class ProxyTimeoutError(Exception):pass
    class ProxyConnectionError(Exception):pass
class proxy_info:
    def __init__(self, **options):
        self.proxy_host = options.get('http_proxy_host', None)
        if self.proxy_host:
            self.proxy_port = options.get('http_proxy_port', 0)
            self.auth = options.get('http_proxy_auth', None)
            self.no_proxy = options.get('http_no_proxy', None)
            self.proxy_protocol = options.get('proxy_type', 'http')
            self.proxy_timeout = options.get('http_proxy_timeout', None)
            if self.proxy_protocol not in ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']:
                raise ProxyError('Only http, socks4, socks5 proxy protocols are supported')
        else:
            self.proxy_port = 0
            self.auth = None
            self.no_proxy = None
            self.proxy_protocol = 'http'
def _start_proxied_socket(url: str, options, proxy) -> tuple:
    if not HAVE_PYTHON_SOCKS:
        raise WebSocketException('Python Socks is needed for SOCKS proxying but is not available')
    (hostname, port, resource, is_secure) = parse_url(url)
    if proxy.proxy_protocol == 'socks4':
        rdns = False
        proxy_type = ProxyType.SOCKS4
    elif proxy.proxy_protocol == 'socks4a':
        rdns = True
        proxy_type = ProxyType.SOCKS4
    elif proxy.proxy_protocol == 'socks5':
        rdns = False
        proxy_type = ProxyType.SOCKS5
    elif proxy.proxy_protocol == 'socks5h':
        rdns = True
        proxy_type = ProxyType.SOCKS5
    ws_proxy = Proxy.create(proxy_type=proxy_type, host=proxy.proxy_host, port=int(proxy.proxy_port), username=proxy.auth[0] if proxy.auth else None, password=proxy.auth[1] if proxy.auth else None, rdns=rdns)
    sock = ws_proxy.connect(hostname, port, timeout=proxy.proxy_timeout)
    if is_secure:
        if HAVE_SSL:
            sock = _ssl_socket(sock, options.sslopt, hostname)
        else:
            raise WebSocketException('SSL not available.')
    return (sock, (hostname, port, resource))
def connect(url: str, options, proxy, socket):
    if proxy.proxy_host and (not socket) and (proxy.proxy_protocol != 'http'):
        return _start_proxied_socket(url, options, proxy)
    (hostname, port_from_url, resource, is_secure) = parse_url(url)
    if socket:
        return (socket, (hostname, port_from_url, resource))
    (addrinfo_list, need_tunnel, auth) = _get_addrinfo_list(hostname, port_from_url, is_secure, proxy)
    if not addrinfo_list:
        raise WebSocketException(f'Host not found.: {hostname}:{port_from_url}')
    sock = None
    try:
        sock = _open_socket(addrinfo_list, options.sockopt, options.timeout)
        if need_tunnel:
            sock = _tunnel(sock, hostname, port_from_url, auth)
        if is_secure:
            if HAVE_SSL:
                sock = _ssl_socket(sock, options.sslopt, hostname)
            else:
                raise WebSocketException('SSL not available.')
        return (sock, (hostname, port_from_url, resource))
    except:
        if sock:
            sock.close()
        raise
def _get_addrinfo_list(hostname, port: int, is_secure: bool, proxy) -> tuple:
    (phost, pport, pauth) = get_proxy_info(hostname, is_secure, proxy.proxy_host, proxy.proxy_port, proxy.auth, proxy.no_proxy)
    try:
        if not phost:
            addrinfo_list = socket.getaddrinfo(hostname, port, 0, socket.SOCK_STREAM, socket.SOL_TCP)
            return (addrinfo_list, False, None)
        else:
            pport = pport and pport or 80
            addrinfo_list = socket.getaddrinfo(phost, pport, 0, socket.SOCK_STREAM, socket.SOL_TCP)
            return (addrinfo_list, True, pauth)
    except socket.gaierror as e:
        raise WebSocketAddressException(e)
def _open_socket(addrinfo_list, sockopt, timeout):
    err = None
    for addrinfo in addrinfo_list:
        (family, socktype, proto) = addrinfo[:3]
        sock = socket.socket(family, socktype, proto)
        sock.settimeout(timeout)
        for opts in DEFAULT_SOCKET_OPTION:
            sock.setsockopt(*opts)
        for opts in sockopt:
            sock.setsockopt(*opts)
        address = addrinfo[4]
        err = None
        while not err:
            try:
                sock.connect(address)
            except socket.error as error:
                sock.close()
                error.remote_ip = str(address[0])
                try:
                    eConnRefused = (errno.ECONNREFUSED, errno.WSAECONNREFUSED, errno.ENETUNREACH)
                except AttributeError:
                    eConnRefused = (errno.ECONNREFUSED, errno.ENETUNREACH)
                if error.errno not in eConnRefused:
                    raise error
                err = error
                continue
            else:
                break
        else:
            continue
        break
    else:
        if err:
            raise err
    return sock
def _wrap_sni_socket(sock: socket.socket, sslopt: dict, hostname, check_hostname):
    context = sslopt.get('context', None)
    if not context:
        context = ssl.SSLContext(sslopt.get('ssl_version', ssl.PROTOCOL_TLS_CLIENT))
        context.keylog_filename = os.environ.get('SSLKEYLOGFILE', None)
        if sslopt.get('cert_reqs', ssl.CERT_NONE) != ssl.CERT_NONE:
            cafile = sslopt.get('ca_certs', None)
            capath = sslopt.get('ca_cert_path', None)
            if cafile or capath:
                context.load_verify_locations(cafile=cafile, capath=capath)
            elif hasattr(context, 'load_default_certs'):
                context.load_default_certs(ssl.Purpose.SERVER_AUTH)
        if sslopt.get('certfile', None):
            context.load_cert_chain(sslopt['certfile'], sslopt.get('keyfile', None), sslopt.get('password', None))
        if sslopt.get('cert_reqs', ssl.CERT_NONE) == ssl.CERT_NONE and (not sslopt.get('check_hostname', False)):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        else:
            context.check_hostname = sslopt.get('check_hostname', True)
            context.verify_mode = sslopt.get('cert_reqs', ssl.CERT_REQUIRED)
        if 'ciphers' in sslopt:
            context.set_ciphers(sslopt['ciphers'])
        if 'cert_chain' in sslopt:
            (certfile, keyfile, password) = sslopt['cert_chain']
            context.load_cert_chain(certfile, keyfile, password)
        if 'ecdh_curve' in sslopt:
            context.set_ecdh_curve(sslopt['ecdh_curve'])
    return context.wrap_socket(sock, do_handshake_on_connect=sslopt.get('do_handshake_on_connect', True), suppress_ragged_eofs=sslopt.get('suppress_ragged_eofs', True), server_hostname=hostname)
def _ssl_socket(sock: socket.socket, user_sslopt: dict, hostname):
    sslopt: dict = {'cert_reqs': ssl.CERT_REQUIRED}
    sslopt.update(user_sslopt)
    cert_path = os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE')
    if cert_path and os.path.isfile(cert_path) and (user_sslopt.get('ca_certs', None) is None):
        sslopt['ca_certs'] = cert_path
    elif cert_path and os.path.isdir(cert_path) and (user_sslopt.get('ca_cert_path', None) is None):
        sslopt['ca_cert_path'] = cert_path
    if sslopt.get('server_hostname', None):
        hostname = sslopt['server_hostname']
    check_hostname = sslopt.get('check_hostname', True)
    sock = _wrap_sni_socket(sock, sslopt, hostname, check_hostname)
    return sock
def _tunnel(sock: socket.socket, host, port: int, auth) -> socket.socket:
    debug('Connecting proxy...')
    connect_header = f'CONNECT {host}:{port} HTTP/1.1\r\n'
    connect_header += f'Host: {host}:{port}\r\n'
    if auth and auth[0]:
        auth_str = auth[0]
        if auth[1]:
            auth_str += f':{auth[1]}'
        encoded_str = base64encode(auth_str.encode()).strip().decode().replace('\n', '')
        connect_header += f'Proxy-Authorization: Basic {encoded_str}\r\n'
    connect_header += '\r\n'
    dump('request header', connect_header)
    send(sock, connect_header)
    try:
        (status, _, _) = read_headers(sock)
    except Exception as e:
        raise WebSocketProxyException(str(e))
    if status != 200:
        raise WebSocketProxyException(f'failed CONNECT via proxy status: {status}')
    return sock
def read_headers(sock: socket.socket) -> tuple:
    status = None
    status_message = None
    headers: dict = {}
    trace('--- response header ---')
    while True:
        line = recv_line(sock)
        line = line.decode('utf-8').strip()
        if not line:
            break
        trace(line)
        if not status:
            status_info = line.split(' ', 2)
            status = int(status_info[1])
            if len(status_info) > 2:
                status_message = status_info[2]
        else:
            kv = line.split(':', 1)
            if len(kv) != 2:
                raise WebSocketException('Invalid header')
            (key, value) = kv
            if key.lower() == 'set-cookie' and headers.get('set-cookie'):
                headers['set-cookie'] = headers.get('set-cookie') + '; ' + value.strip()
            else:
                headers[key.lower()] = value.strip()
    trace('-----------------------')
    return (status, headers, status_message)
VERSION = 13
SUPPORTED_REDIRECT_STATUSES = (HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.FOUND, HTTPStatus.SEE_OTHER, HTTPStatus.TEMPORARY_REDIRECT, HTTPStatus.PERMANENT_REDIRECT)
SUCCESS_STATUSES = SUPPORTED_REDIRECT_STATUSES + (HTTPStatus.SWITCHING_PROTOCOLS,)
CookieJar = SimpleCookieJar()
class handshake_response:
    def __init__(self, status: int, headers: dict, subprotocol):
        self.status = status
        self.headers = headers
        self.subprotocol = subprotocol
        CookieJar.add(headers.get('set-cookie'))
def handshake(sock, url: str, hostname: str, port: int, resource: str, **options) -> handshake_response:
    (headers, key) = _get_handshake_headers(resource, url, hostname, port, options)
    header_str = '\r\n'.join(headers)
    send(sock, header_str)
    dump('request header', header_str)
    (status, resp) = _get_resp_headers(sock)
    if status in SUPPORTED_REDIRECT_STATUSES:
        return handshake_response(status, resp, None)
    (success, subproto) = _validate(resp, key, options.get('subprotocols'))
    if not success:
        raise WebSocketException('Invalid WebSocket Header')
    return handshake_response(status, resp, subproto)
def _pack_hostname(hostname: str) -> str:
    if ':' in hostname:
        return f'[{hostname}]'
    return hostname
def _get_handshake_headers(resource: str, url: str, host: str, port: int, options: dict) -> tuple:
    headers = [f'GET {resource} HTTP/1.1', 'Upgrade: websocket']
    if port in [80, 443]:
        hostport = _pack_hostname(host)
    else:
        hostport = f'{_pack_hostname(host)}:{port}'
    if options.get('host'):
        headers.append(f"Host: {options['host']}")
    else:
        headers.append(f'Host: {hostport}')
    (scheme, url) = url.split(':', 1)
    if not options.get('suppress_origin'):
        if 'origin' in options and options['origin'] is not None:
            headers.append(f"Origin: {options['origin']}")
        elif scheme == 'wss':
            headers.append(f'Origin: https://{hostport}')
        else:
            headers.append(f'Origin: http://{hostport}')
    key = _create_sec_websocket_key()
    if not options.get('header') or 'Sec-WebSocket-Key' not in options['header']:
        headers.append(f'Sec-WebSocket-Key: {key}')
    else:
        key = options['header']['Sec-WebSocket-Key']
    if not options.get('header') or 'Sec-WebSocket-Version' not in options['header']:
        headers.append(f'Sec-WebSocket-Version: {VERSION}')
    if not options.get('connection'):
        headers.append('Connection: Upgrade')
    else:
        headers.append(options['connection'])
    if (subprotocols := options.get('subprotocols')):
        headers.append(f"Sec-WebSocket-Protocol: {','.join(subprotocols)}")
    if (header := options.get('header')):
        if isinstance(header, dict):
            header = [': '.join([k, v]) for (k, v) in header.items() if v is not None]
        headers.extend(header)
    server_cookie = CookieJar.get(host)
    client_cookie = options.get('cookie', None)
    if (cookie := '; '.join(filter(None, [server_cookie, client_cookie]))):
        headers.append(f'Cookie: {cookie}')
    headers.extend(('', ''))
    return (headers, key)
def _get_resp_headers(sock, success_statuses: tuple=SUCCESS_STATUSES) -> tuple:
    (status, resp_headers, status_message) = read_headers(sock)
    if status not in success_statuses:
        content_len = resp_headers.get('content-length')
        if content_len:
            response_body = sock.recv(int(content_len))
        else:
            response_body = None
        raise WebSocketBadStatusException(f'Handshake status {status} {status_message} -+-+- {resp_headers} -+-+- {response_body}', status, status_message, resp_headers, response_body)
    return (status, resp_headers)
_HEADERS_TO_CHECK = {'upgrade': 'websocket', 'connection': 'upgrade'}
def _validate(headers, key: str, subprotocols) -> tuple:
    subproto = None
    for (k, v) in _HEADERS_TO_CHECK.items():
        r = headers.get(k, None)
        if not r:
            return (False, None)
        r = [x.strip().lower() for x in r.split(',')]
        if v not in r:
            return (False, None)
    if subprotocols:
        subproto = headers.get('sec-websocket-protocol', None)
        if not subproto or subproto.lower() not in [s.lower() for s in subprotocols]:
            error(f'Invalid subprotocol: {subprotocols}')
            return (False, None)
        subproto = subproto.lower()
    result = headers.get('sec-websocket-accept', None)
    if not result:
        return (False, None)
    result = result.lower()
    if isinstance(result, str):
        result = result.encode('utf-8')
    value = f'{key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11'.encode('utf-8')
    hashed = base64encode(hashlib.sha1(value).digest()).strip().lower()
    if hmac.compare_digest(hashed, result):
        return (True, subproto)
    else:
        return (False, None)
def _create_sec_websocket_key() -> str:
    randomness = os.urandom(16)
    return base64encode(randomness).decode('utf-8').strip()
class WebSocket:
    def __init__(self, get_mask_key=None, sockopt=None, sslopt=None, fire_cont_frame: bool=False, enable_multithread: bool=True, skip_utf8_validation: bool=False, **_):
        self.sock_opt = sock_opt(sockopt, sslopt)
        self.handshake_response = None
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.get_mask_key = get_mask_key
        self.frame_buffer = frame_buffer(self._recv, skip_utf8_validation)
        self.cont_frame = continuous_frame(fire_cont_frame, skip_utf8_validation)
        if enable_multithread:
            self.lock = threading.Lock()
            self.readlock = threading.Lock()
        else:
            self.lock = NoLock()
            self.readlock = NoLock()
    def __iter__(self):
        while True:
            yield self.recv()
    def __next__(self):
        return self.recv()
    def next(self):
        return self.__next__()
    def fileno(self):
        return self.sock.fileno()
    def set_mask_key(self, func):
        self.get_mask_key = func
    def gettimeout(self) -> Union[float, int, None]:
        return self.sock_opt.timeout
    def settimeout(self, timeout: Union[float, int, None]):
        self.sock_opt.timeout = timeout
        if self.sock:
            self.sock.settimeout(timeout)
    timeout = property(gettimeout, settimeout)
    def getsubprotocol(self):
        if self.handshake_response:
            return self.handshake_response.subprotocol
        else:
            return None
    subprotocol = property(getsubprotocol)
    def getstatus(self):
        if self.handshake_response:
            return self.handshake_response.status
        else:
            return None
    status = property(getstatus)
    def getheaders(self):
        if self.handshake_response:
            return self.handshake_response.headers
        else:
            return None
    def is_ssl(self):
        try:
            return isinstance(self.sock, ssl.SSLSocket)
        except:
            return False
    headers = property(getheaders)
    def connect(self, url, **options):
        self.sock_opt.timeout = options.get('timeout', self.sock_opt.timeout)
        (self.sock, addrs) = connect(url, self.sock_opt, proxy_info(**options), options.pop('socket', None))
        try:
            self.handshake_response = handshake(self.sock, url, *addrs, **options)
            for _ in range(options.pop('redirect_limit', 3)):
                if self.handshake_response.status in SUPPORTED_REDIRECT_STATUSES:
                    url = self.handshake_response.headers['location']
                    self.sock.close()
                    (self.sock, addrs) = connect(url, self.sock_opt, proxy_info(**options), options.pop('socket', None))
                    self.handshake_response = handshake(self.sock, url, *addrs, **options)
            self.connected = True
        except:
            if self.sock:
                self.sock.close()
                self.sock = None
            raise
    def send(self, payload: Union[bytes, str], opcode: int=ABNF.OPCODE_TEXT) -> int:
        frame = ABNF.create_frame(payload, opcode)
        return self.send_frame(frame)
    def send_text(self, text_data: str) -> int:
        return self.send(text_data, ABNF.OPCODE_TEXT)
    def send_bytes(self, data: Union[bytes, bytearray]) -> int:
        return self.send(data, ABNF.OPCODE_BINARY)
    def send_frame(self, frame) -> int:
        if self.get_mask_key:
            frame.get_mask_key = self.get_mask_key
        data = frame.format()
        length = len(data)
        if isEnabledForTrace():
            trace(f'++Sent raw: {repr(data)}')
            trace(f'++Sent decoded: {frame.__str__()}')
        with self.lock:
            while data:
                l = self._send(data)
                data = data[l:]
        return length
    def send_binary(self, payload: bytes) -> int:
        return self.send(payload, ABNF.OPCODE_BINARY)
    def ping(self, payload: Union[str, bytes]=''):
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        self.send(payload, ABNF.OPCODE_PING)
    def pong(self, payload: Union[str, bytes]=''):
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        self.send(payload, ABNF.OPCODE_PONG)
    def recv(self) -> Union[str, bytes]:
        with self.readlock:
            (opcode, data) = self.recv_data()
        if opcode == ABNF.OPCODE_TEXT:
            data_received: Union[bytes, str] = data
            if isinstance(data_received, bytes):
                return data_received.decode('utf-8')
            elif isinstance(data_received, str):
                return data_received
        elif opcode == ABNF.OPCODE_BINARY:
            data_binary: bytes = data
            return data_binary
        else:
            return ''
    def recv_data(self, control_frame: bool=False) -> tuple:
        (opcode, frame) = self.recv_data_frame(control_frame)
        return (opcode, frame.data)
    def recv_data_frame(self, control_frame: bool=False) -> tuple:
        while True:
            frame = self.recv_frame()
            if isEnabledForTrace():
                trace(f'++Rcv raw: {repr(frame.format())}')
                trace(f'++Rcv decoded: {frame.__str__()}')
            if not frame:
                raise WebSocketProtocolException(f'Not a valid frame {frame}')
            elif frame.opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY, ABNF.OPCODE_CONT):
                self.cont_frame.validate(frame)
                self.cont_frame.add(frame)
                if self.cont_frame.is_fire(frame):
                    return self.cont_frame.extract(frame)
            elif frame.opcode == ABNF.OPCODE_CLOSE:
                self.send_close()
                return (frame.opcode, frame)
            elif frame.opcode == ABNF.OPCODE_PING:
                if len(frame.data) < 126:
                    self.pong(frame.data)
                else:
                    raise WebSocketProtocolException('Ping message is too long')
                if control_frame:
                    return (frame.opcode, frame)
            elif frame.opcode == ABNF.OPCODE_PONG:
                if control_frame:
                    return (frame.opcode, frame)
    def recv_frame(self):
        return self.frame_buffer.recv_frame()
    def send_close(self, status: int=STATUS_NORMAL, reason: bytes=b''):
        if status < 0 or status >= ABNF.LENGTH_16:
            raise ValueError('code is invalid range')
        self.connected = False
        self.send(struct.pack('!H', status) + reason, ABNF.OPCODE_CLOSE)
    def close(self, status: int=STATUS_NORMAL, reason: bytes=b'', timeout: int=3):
        if not self.connected:
            return
        if status < 0 or status >= ABNF.LENGTH_16:
            raise ValueError('code is invalid range')
        try:
            self.connected = False
            self.send(struct.pack('!H', status) + reason, ABNF.OPCODE_CLOSE)
            sock_timeout = self.sock.gettimeout()
            self.sock.settimeout(timeout)
            start_time = time.time()
            while timeout is None or time.time() - start_time < timeout:
                try:
                    frame = self.recv_frame()
                    if frame.opcode != ABNF.OPCODE_CLOSE:
                        continue
                    if isEnabledForError():
                        recv_status = struct.unpack('!H', frame.data[0:2])[0]
                        if recv_status >= 3000 and recv_status <= 4999:
                            debug(f'close status: {repr(recv_status)}')
                        elif recv_status != STATUS_NORMAL:
                            error(f'close status: {repr(recv_status)}')
                    break
                except:
                    break
            self.sock.settimeout(sock_timeout)
            self.sock.shutdown(socket.SHUT_RDWR)
        except:pass
        self.shutdown()
    def abort(self):
        if self.connected:
            self.sock.shutdown(socket.SHUT_RDWR)
    def shutdown(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            self.connected = False
    def _send(self, data: Union[str, bytes]):
        return send(self.sock, data)
    def _recv(self, bufsize):
        try:
            return recv(self.sock, bufsize)
        except WebSocketConnectionClosedException:
            if self.sock:
                self.sock.close()
            self.sock = None
            self.connected = False
            raise
def create_connection(url: str, timeout=None, class_=WebSocket, **options):
    sockopt = options.pop('sockopt', [])
    sslopt = options.pop('sslopt', {})
    fire_cont_frame = options.pop('fire_cont_frame', False)
    enable_multithread = options.pop('enable_multithread', True)
    skip_utf8_validation = options.pop('skip_utf8_validation', False)
    websock = class_(sockopt=sockopt, sslopt=sslopt, fire_cont_frame=fire_cont_frame, enable_multithread=enable_multithread, skip_utf8_validation=skip_utf8_validation, **options)
    websock.settimeout(timeout if timeout is not None else getdefaulttimeout())
    websock.connect(url, **options)
    return websock
RECONNECT = 0
def setReconnect(reconnectInterval: int) -> None:
    global RECONNECT
    RECONNECT = reconnectInterval
class DispatcherBase:
    def __init__(self, app: Any, ping_timeout: Union[float, int, None]) -> None:
        self.app = app
        self.ping_timeout = ping_timeout
    def timeout(self, seconds: Union[float, int, None], callback: Callable) -> None:
        time.sleep(seconds)
        callback()
    def reconnect(self, seconds: int, reconnector: Callable) -> None:
        try:
            _logging.info(f'reconnect() - retrying in {seconds} seconds [{len(inspect.stack())} frames in stack]')
            time.sleep(seconds)
            reconnector(reconnecting=True)
        except KeyboardInterrupt as e:
            _logging.info(f'User exited {e}')
            raise e
class Dispatcher(DispatcherBase):
    def read(self, sock: socket.socket, read_callback: Callable, check_callback: Callable) -> None:
        sel = selectors.DefaultSelector()
        sel.register(self.app.sock.sock, selectors.EVENT_READ)
        try:
            while self.app.keep_running:
                if sel.select(self.ping_timeout):
                    if not read_callback():
                        break
                check_callback()
        finally:
            sel.close()
class SSLDispatcher(DispatcherBase):
    def read(self, sock: socket.socket, read_callback: Callable, check_callback: Callable) -> None:
        sock = self.app.sock.sock
        sel = selectors.DefaultSelector()
        sel.register(sock, selectors.EVENT_READ)
        try:
            while self.app.keep_running:
                if self.select(sock, sel):
                    if not read_callback():
                        break
                check_callback()
        finally:
            sel.close()
    def select(self, sock, sel: selectors.DefaultSelector):
        sock = self.app.sock.sock
        if sock.pending():
            return [sock]
        r = sel.select(self.ping_timeout)
        if len(r) > 0:
            return r[0][0]
class WrappedDispatcher:
    def __init__(self, app, ping_timeout: Union[float, int, None], dispatcher) -> None:
        self.app = app
        self.ping_timeout = ping_timeout
        self.dispatcher = dispatcher
        dispatcher.signal(2, dispatcher.abort)
    def read(self, sock: socket.socket, read_callback: Callable, check_callback: Callable) -> None:
        self.dispatcher.read(sock, read_callback)
        self.ping_timeout and self.timeout(self.ping_timeout, check_callback)
    def timeout(self, seconds: float, callback: Callable) -> None:
        self.dispatcher.timeout(seconds, callback)
    def reconnect(self, seconds: int, reconnector: Callable) -> None:
        self.timeout(seconds, reconnector)
class WebSocketApp:
    def __init__(self, url: str, header: Union[list, dict, Callable, None]=None, on_open: Optional[Callable[[WebSocket], None]]=None, on_reconnect: Optional[Callable[[WebSocket], None]]=None, on_message: Optional[Callable[[WebSocket, Any], None]]=None, on_error: Optional[Callable[[WebSocket, Any], None]]=None, on_close: Optional[Callable[[WebSocket, Any, Any], None]]=None, on_ping: Optional[Callable]=None, on_pong: Optional[Callable]=None, on_cont_message: Optional[Callable]=None, keep_running: bool=True, get_mask_key: Optional[Callable]=None, cookie: Optional[str]=None, subprotocols: Optional[list]=None, on_data: Optional[Callable]=None, socket: Optional[socket.socket]=None) -> None:
        self.url = url
        self.header = header if header is not None else []
        self.cookie = cookie
        self.on_open = on_open
        self.on_reconnect = on_reconnect
        self.on_message = on_message
        self.on_data = on_data
        self.on_error = on_error
        self.on_close = on_close
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.on_cont_message = on_cont_message
        self.keep_running = False
        self.get_mask_key = get_mask_key
        self.sock: Optional[WebSocket] = None
        self.last_ping_tm = float(0)
        self.last_pong_tm = float(0)
        self.ping_thread: Optional[threading.Thread] = None
        self.stop_ping: Optional[threading.Event] = None
        self.ping_interval = float(0)
        self.ping_timeout: Union[float, int, None] = None
        self.ping_payload = ''
        self.subprotocols = subprotocols
        self.prepared_socket = socket
        self.has_errored = False
        self.has_done_teardown = False
        self.has_done_teardown_lock = threading.Lock()
    def send(self, data: Union[bytes, str], opcode: int=ABNF.OPCODE_TEXT) -> None:
        if not self.sock or self.sock.send(data, opcode) == 0:
            raise WebSocketConnectionClosedException('Connection is already closed.')
    def send_text(self, text_data: str) -> None:
        if not self.sock or self.sock.send(text_data, ABNF.OPCODE_TEXT) == 0:
            raise WebSocketConnectionClosedException('Connection is already closed.')
    def send_bytes(self, data: Union[bytes, bytearray]) -> None:
        if not self.sock or self.sock.send(data, ABNF.OPCODE_BINARY) == 0:
            raise WebSocketConnectionClosedException('Connection is already closed.')
    def close(self, **kwargs) -> None:
        self.keep_running = False
        if self.sock:
            self.sock.close(**kwargs)
            self.sock = None
    def _start_ping_thread(self) -> None:
        self.last_ping_tm = self.last_pong_tm = float(0)
        self.stop_ping = threading.Event()
        self.ping_thread = threading.Thread(target=self._send_ping)
        self.ping_thread.daemon = True
        self.ping_thread.start()
    def _stop_ping_thread(self) -> None:
        if self.stop_ping:
            self.stop_ping.set()
        if self.ping_thread and self.ping_thread.is_alive():
            self.ping_thread.join(3)
        self.last_ping_tm = self.last_pong_tm = float(0)
    def _send_ping(self) -> None:
        if self.stop_ping.wait(self.ping_interval) or self.keep_running is False:
            return
        while not self.stop_ping.wait(self.ping_interval) and self.keep_running is True:
            if self.sock:
                self.last_ping_tm = time.time()
                try:
                    _logging.debug('Sending ping')
                    self.sock.ping(self.ping_payload)
                except Exception as e:
                    _logging.debug(f'Failed to send ping: {e}')
    def run_forever(self, sockopt: tuple=None, sslopt: dict=None, ping_interval: Union[float, int]=0, ping_timeout: Union[float, int, None]=None, ping_payload: str='', http_proxy_host: str=None, http_proxy_port: Union[int, str]=None, http_no_proxy: list=None, http_proxy_auth: tuple=None, http_proxy_timeout: Optional[float]=None, skip_utf8_validation: bool=False, host: str=None, origin: str=None, dispatcher=None, suppress_origin: bool=False, proxy_type: str=None, reconnect: int=None) -> bool:
        if reconnect is None:
            reconnect = RECONNECT
        if ping_timeout is not None and ping_timeout <= 0:
            raise WebSocketException('Ensure ping_timeout > 0')
        if ping_interval is not None and ping_interval < 0:
            raise WebSocketException('Ensure ping_interval >= 0')
        if ping_timeout and ping_interval and (ping_interval <= ping_timeout):
            raise WebSocketException('Ensure ping_interval > ping_timeout')
        if not sockopt:
            sockopt = ()
        if not sslopt:
            sslopt = {}
        if self.sock:
            raise WebSocketException('socket is already opened')
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.ping_payload = ping_payload
        self.has_done_teardown = False
        self.keep_running = True
        def teardown(close_frame: ABNF=None):
            with self.has_done_teardown_lock:
                if self.has_done_teardown:
                    return
                self.has_done_teardown = True
            self._stop_ping_thread()
            self.keep_running = False
            if self.sock:
                self.sock.close()
            (close_status_code, close_reason) = self._get_close_args(close_frame if close_frame else None)
            self.sock = None
            self._callback(self.on_close, close_status_code, close_reason)
        def setSock(reconnecting: bool=False) -> None:
            if reconnecting and self.sock:
                self.sock.shutdown()
            self.sock = WebSocket(self.get_mask_key, sockopt=sockopt, sslopt=sslopt, fire_cont_frame=self.on_cont_message is not None, skip_utf8_validation=skip_utf8_validation, enable_multithread=True)
            self.sock.settimeout(getdefaulttimeout())
            try:
                header = self.header() if callable(self.header) else self.header
                self.sock.connect(self.url, header=header, cookie=self.cookie, http_proxy_host=http_proxy_host, http_proxy_port=http_proxy_port, http_no_proxy=http_no_proxy, http_proxy_auth=http_proxy_auth, http_proxy_timeout=http_proxy_timeout, subprotocols=self.subprotocols, host=host, origin=origin, suppress_origin=suppress_origin, proxy_type=proxy_type, socket=self.prepared_socket)
                _logging.info('Websocket connected')
                if self.ping_interval:
                    self._start_ping_thread()
                if reconnecting and self.on_reconnect:
                    self._callback(self.on_reconnect)
                else:
                    self._callback(self.on_open)
                dispatcher.read(self.sock.sock, read, check)
            except (WebSocketConnectionClosedException, ConnectionRefusedError, KeyboardInterrupt, SystemExit, Exception) as e:
                handleDisconnect(e, reconnecting)
        def read() -> bool:
            if not self.keep_running:
                return teardown()
            try:
                (op_code, frame) = self.sock.recv_data_frame(True)
            except (WebSocketConnectionClosedException, KeyboardInterrupt, SSLEOFError) as e:
                if custom_dispatcher:
                    return handleDisconnect(e, bool(reconnect))
                else:
                    raise e
            if op_code == ABNF.OPCODE_CLOSE:
                return teardown(frame)
            elif op_code == ABNF.OPCODE_PING:
                self._callback(self.on_ping, frame.data)
            elif op_code == ABNF.OPCODE_PONG:
                self.last_pong_tm = time.time()
                self._callback(self.on_pong, frame.data)
            elif op_code == ABNF.OPCODE_CONT and self.on_cont_message:
                self._callback(self.on_data, frame.data, frame.opcode, frame.fin)
                self._callback(self.on_cont_message, frame.data, frame.fin)
            else:
                data = frame.data
                if op_code == ABNF.OPCODE_TEXT and (not skip_utf8_validation):
                    data = data.decode('utf-8')
                self._callback(self.on_data, data, frame.opcode, True)
                self._callback(self.on_message, data)
            return True
        def check() -> bool:
            if self.ping_timeout:
                has_timeout_expired = time.time() - self.last_ping_tm > self.ping_timeout
                has_pong_not_arrived_after_last_ping = self.last_pong_tm - self.last_ping_tm < 0
                has_pong_arrived_too_late = self.last_pong_tm - self.last_ping_tm > self.ping_timeout
                if self.last_ping_tm and has_timeout_expired and (has_pong_not_arrived_after_last_ping or has_pong_arrived_too_late):
                    raise WebSocketTimeoutException('ping/pong timed out')
            return True
        def handleDisconnect(e: Union[WebSocketConnectionClosedException, ConnectionRefusedError, KeyboardInterrupt, SystemExit, Exception], reconnecting: bool=False) -> bool:
            self.has_errored = True
            self._stop_ping_thread()
            if not reconnecting:
                self._callback(self.on_error, e)
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                teardown()
                raise
            if reconnect:
                _logging.info(f'{e} - reconnect')
                if custom_dispatcher:
                    _logging.debug(f'Calling custom dispatcher reconnect [{len(inspect.stack())} frames in stack]')
                    dispatcher.reconnect(reconnect, setSock)
            else:
                _logging.error(f'{e} - goodbye')
                teardown()
        custom_dispatcher = bool(dispatcher)
        dispatcher = self.create_dispatcher(ping_timeout, dispatcher, parse_url(self.url)[3])
        try:
            setSock()
            if not custom_dispatcher and reconnect:
                while self.keep_running:
                    _logging.debug(f'Calling dispatcher reconnect [{len(inspect.stack())} frames in stack]')
                    dispatcher.reconnect(reconnect, setSock)
        except (KeyboardInterrupt, Exception) as e:
            _logging.info(f'tearing down on exception {e}')
            teardown()
        finally:
            if not custom_dispatcher:
                teardown()
        return self.has_errored
    def create_dispatcher(self, ping_timeout: Union[float, int, None], dispatcher: Optional[DispatcherBase]=None, is_ssl: bool=False) -> Union[Dispatcher, SSLDispatcher, WrappedDispatcher]:
        if dispatcher:
            return WrappedDispatcher(self, ping_timeout, dispatcher)
        timeout = ping_timeout or 10
        if is_ssl:
            return SSLDispatcher(self, timeout)
        return Dispatcher(self, timeout)
    def _get_close_args(self, close_frame: ABNF) -> list:
        if not self.on_close or not close_frame:
            return [None, None]
        if close_frame.data and len(close_frame.data) >= 2:
            close_status_code = 256 * int(close_frame.data[0]) + int(close_frame.data[1])
            reason = close_frame.data[2:]
            if isinstance(reason, bytes):
                reason = reason.decode('utf-8')
            return [close_status_code, reason]
        else:
            return [None, None]
    def _callback(self, callback, *args) -> None:
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                _logging.error(f'error from callback {callback}: {e}')
                if self.on_error:
                    self.on_error(self, e)