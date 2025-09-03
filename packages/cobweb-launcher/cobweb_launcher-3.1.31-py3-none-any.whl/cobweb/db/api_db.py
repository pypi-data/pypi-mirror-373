import os
import json
import requests


class ApiDB:

    def __init__(self, host=None, **kwargs):
        self.host = host or os.getenv("REDIS_API_HOST", "http://127.0.0.1:4396")

    def _get_response(self, api, params: dict = None):
        try:
            url = self.host + api
            response = requests.get(url, params=params)
            json_data = response.json()
            response.close()
            return json_data["data"]
        except:
            return None

    def _post_response(self, api, params: dict = None, data: dict = None):
        try:
            url = self.host + api
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, params=params, data=json.dumps(data))
            json_data = response.json()
            response.close()
            return json_data["data"]
        except:
            return None

    def get(self, name):
        return self._get_response(api="/get", params=dict(name=name))

    def setnx(self, name, value=""):
        return self._get_response(api="/setnx", params=dict(name=name, value=value))

    def setex(self, name, t, value=""):
        return self._get_response(api="/setex", params=dict(name=name, value=value, t=t))

    def expire(self, name, t, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        return self._get_response(api="/expire", params=dict(name=name, t=t, nx=nx, xx=xx, gt=gt, lt=lt))

    def ttl(self, name):
        return self._get_response(api="/ttl", params=dict(name=name))

    def delete(self, name):
        return self._get_response(api="/delete", params=dict(name=name))

    def exists(self, name):
        return self._get_response(api="/exists", params=dict(name=name))

    def incrby(self, name, value):
        return self._get_response(api="/incrby", params=dict(name=name, value=value))

    def zcard(self, name) -> bool:
        return self._get_response(api="/zcard", params=dict(name=name))

    def zadd(self, name, item: dict, **kwargs):
        if item:
            return self._post_response(api="/zadd", data=dict(name=name, mapping=item, **kwargs))

    def zrem(self, name, *values):
        return self._post_response(api="/zrem", data=dict(name=name, values=values))

    def zcount(self, name, _min, _max):
        return self._get_response(api="/zcount", params=dict(name=name, min=_min, max=_max))

    def lock(self, name, t=15) -> bool:
        return self._get_response(api="/lock", params=dict(name=name, t=t))

    def auto_incr(self, name, t=15, limit=1000) -> bool:
        return self._get_response(api="/auto_incr", params=dict(name=name, t=t, limit=limit))

    def members(self, name, score, start=0, count=1000, _min="-inf", _max="+inf"):
        return self._get_response(api="/members", params=dict(name=name, score=score, start=start, count=count, min=_min, max=_max))

    def done(self, name: list, *values):
        return self._post_response(api="/done", data=dict(name=name, values=values))




