import os

import time
import redis
from redis.exceptions import ConnectionError, TimeoutError


class RedisDB:
    def __init__(
            self,
            host=None,
            password=None,
            port=6379, db=0
    ):
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.port = port or os.getenv("REDIS_PORT", 6379)
        self.db = db or os.getenv("REDIS_DB", 0)

        self.max_retries = 5
        self.retry_delay = 5
        self.client = None
        self.connect()

    def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                self.client.ping()
                return
            except (ConnectionError, TimeoutError) as e:
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception("达到最大重试次数，无法连接 Redis")

    def is_connected(self):
        try:
            self.client.ping()
            return True
        except (ConnectionError, TimeoutError):
            return False

    def reconnect(self):
        self.connect()

    def execute_command(self, command, *args, **kwargs):
        retries = 0
        while retries < self.max_retries:
            try:
                if not self.is_connected():
                    self.reconnect()
                return getattr(self.client, command)(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception("达到最大重试次数，无法执行命令")

    def get(self, name):
        # with self.get_connection() as client:
        #     return client.get(name)
        return self.execute_command("get", name)

    def incrby(self, name, value):
        # with self.get_connection() as client:
        #     client.incrby(name, value)
        self.execute_command("incrby", name, value)

    def setnx(self, name, value=""):
        # with self.get_connection() as client:
        #     client.setnx(name, value)
        self.execute_command("setnx", name, value)

    def setex(self, name, t, value=""):
        # with self.get_connection() as client:
        #     client.setex(name, t, value)
        self.execute_command("setex", name, t, value)

    def expire(self, name, t, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        # with self.get_connection() as client:
        # client.expire(name, t, nx, xx, gt, lt)
        self.execute_command("expire", name, t, nx, xx, gt, lt)

    def ttl(self, name):
        # with self.get_connection() as client:
        #     return client.ttl(name)
        return self.execute_command("ttl", name)

    def delete(self, name):
        # with self.get_connection() as client:
        #     return client.delete(name)
        return self.execute_command("delete", name)

    def exists(self, *name) -> bool:
        # with self.get_connection() as client:
        #     return client.exists(*name)
        return self.execute_command("exists", *name)

    def sadd(self, name, value):
        # with self.get_connection() as client:
        #     return client.sadd(name, value)
        return self.execute_command("sadd", name, value)

    def zcard(self, name) -> bool:
        # with self.get_connection() as client:
        #     return client.zcard(name)
        return self.execute_command("zcard", name)

    def zadd(self, name, item: dict, **kwargs):
        # with self.get_connection() as client:
        #     return client.zadd(name, item, **kwargs)
        if item:
            return self.execute_command("zadd", name, item, **kwargs)

    def zrem(self, name, *value):
        # with self.get_connection() as client:
        #     return client.zrem(name, *value)
        return self.execute_command("zrem", name, *value)

    def zcount(self, name, _min, _max):
        # with self.get_connection() as client:
        #     return client.zcount(name, _min, _max)
        return self.execute_command("zcount", name, _min, _max)

    # def zrangebyscore(self, name, _min, _max, start, num, withscores: bool = False, *args):
    #     with self.get_connection() as client:
    #        return client.zrangebyscore(name, _min, _max, start, num, withscores, *args)

    def lua(self, script: str, keys: list = None, args: list = None):
        keys = keys or []
        args = args or []
        keys_count = len(keys)
        return self.execute_command("eval", script, keys_count, *keys, *args)

    def lua_sha(self, sha1: str, keys: list = None, args: list = None):
        keys = keys or []
        args = args or []
        keys_count = len(keys)
        return self.execute_command("evalsha", sha1, keys_count, *keys, *args)

    def execute_lua(self, lua_script: str, keys: list, *args):
        execute = self.execute_command("register_script", lua_script)
        return execute(keys=keys, args=args)

    def lock(self, key, t=15) -> bool:
        lua_script = """
        local status = redis.call('setnx', KEYS[1], 1)
        if ( status == 1 ) then
            redis.call('expire', KEYS[1], ARGV[1])
        end 
        return status 
        """
        status = self.execute_lua(lua_script, [key], t)
        return bool(status)

    def members(self, key, score, start=0, count=1000, _min="-inf", _max="+inf") -> list:
        lua_script = """
        local min = ARGV[1]
        local max = ARGV[2]
        local start = ARGV[3]
        local count = ARGV[4]
        local score = ARGV[5]
        local members = nil

        if ( type(count) == string ) then
            members = redis.call('zrangebyscore', KEYS[1], min, max, 'WITHSCORES')
        else
            members = redis.call('zrangebyscore', KEYS[1], min, max, 'WITHSCORES', 'limit', start, count)
        end

        local result = {}

        for i = 1, #members, 2 do
            local priority = nil
            local member = members[i]
            local originPriority = nil
            if ( members[i+1] + 0 < 0 ) then
                originPriority = math.ceil(members[i+1]) * 1000 - members[i+1] * 1000
            else
                originPriority = math.floor(members[i+1])
            end

            if ( score + 0 >= 1000 ) then
                priority = -score - originPriority / 1000
            elseif ( score + 0 == 0 ) then
                priority = originPriority
            else
                originPriority = score 
                priority = score
            end
            redis.call('zadd', KEYS[1], priority, member)
            table.insert(result, member)
            table.insert(result, originPriority)
        end

        return result
        """
        members = self.execute_lua(lua_script, [key], _min, _max, start, count, score)
        return [(members[i].decode(), int(members[i + 1])) for i in range(0, len(members), 2)]

    def done(self, keys: list, *args):
        lua_script = """
        for i, member in ipairs(ARGV) do
            redis.call("zrem", KEYS[1], member)
            redis.call("sadd", KEYS[2], member)
        end
        """
        self.execute_lua(lua_script, keys, *args)
