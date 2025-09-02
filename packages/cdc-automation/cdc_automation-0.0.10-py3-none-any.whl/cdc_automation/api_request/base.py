import requests
from requests.models import Response
from requests.sessions import Session
import json as JSON
import re
import logging
import inspect
import warnings
from .package_info import PackageEnvInfo


class Request(PackageEnvInfo, Session):

    def __init__(self, test_env: str = None):
        """
        Build a Request object
        :param test_env: if you want to use specific test env in this instance
        """
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        # self.session = requests.sessions.Session()
        super().__init__()
        self.url = None
        self._env = test_env if test_env else super().TestEnv
        self.logger = logging.getLogger(__name__)

    def re_param(self, url, **kwargs):
        """
        please add own data in env_info.py and update to cdc_automation.package_info.PackageEnvInfo
        """
        if "http" not in url:
            self.url = super().build_url(url, self._env)
        else:
            self.url = url

        if "headers" not in kwargs:
            # self.session.headers = super().build_header(url, self._env)
            self.headers = super().build_header(url, self._env)

    def _custom_logger(self, response):
        def repl(matchobj):
            if matchobj.group(0) == "\\":
                return ""
            else:
                return matchobj.group(0)[:-1] + "."
        caller_frame = inspect.currentframe().f_back.f_back
        frame_info = inspect.getframeinfo(caller_frame)
        file_path = re.search(rf"{re.escape(str(super().project_root_dir))}(.+)", frame_info.filename).group(1)
        function_name = frame_info.function
        line_number = frame_info.lineno

        matched_regex = ".*?\\\\"
        response_log = self.format_res_log(response)
        self.logger.debug(
            f'{re.sub(matched_regex, repl, file_path)}:{function_name}[{line_number}] {JSON.dumps(response_log)}',
            extra=response_log
        )

    def get(self, url, logged=True, **kwargs):
        self.re_param(url, **kwargs)
        # res = self.session.get(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        res = super().get(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        if logged is True:
            self._custom_logger(res)
        return res

    def post(self, url, data=None, json=None, logged=True, **kwargs):
        self.re_param(url, **kwargs)
        # res = self.session.post(self.url, data, json, **kwargs, verify=False if 'https://' in self.url else None)
        res = super().post(self.url, data, json, **kwargs, verify=False if 'https://' in self.url else None)
        if logged is True:
            self._custom_logger(res)
        return res

    def put(self, url, data=None, **kwargs):
        self.re_param(url, **kwargs)
        # res = self.session.put(self.url, data, **kwargs, verify=False if 'https://' in self.url else None)
        res = super().put(self.url, data, **kwargs, verify=False if 'https://' in self.url else None)
        self._custom_logger(res)
        return res

    def delete(self, url, **kwargs):
        self.re_param(url, **kwargs)
        # res = self.session.delete(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        res = super().delete(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        self._custom_logger(res)
        return res

    @staticmethod
    def format_res_log(res: Response) -> dict:
        """
        Change Response Obj to log format

        :param res: Response Obj
        :return: log format as dict
        """
        if res.request.method == "GET":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }
        elif res.request.method == "POST":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers),
                    "body": JSON.loads(res.request.body) if res.request.headers.get("content-type") == "application/json" else None
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }
        elif res.request.method == "PUT":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers),
                    "body": JSON.loads(res.request.body)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }
        elif res.request.method == "DELETE":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }

