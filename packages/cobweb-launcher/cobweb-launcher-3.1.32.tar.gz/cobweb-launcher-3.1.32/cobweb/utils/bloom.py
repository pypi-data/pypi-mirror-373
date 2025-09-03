# import math
# import time
#
# import mmh3
# import redis
# from cobweb import setting
#
#
# class BloomFilter:
#
#     def __init__(self, key, redis_config=None, capacity=None, error_rate=None):
#         redis_config = redis_config or setting.REDIS_CONFIG
#         capacity = capacity or setting.CAPACITY
#         error_rate = error_rate or setting.ERROR_RATE
#         redis_config['db'] = 3
#
#         self.key = key
#
#         pool = redis.ConnectionPool(**redis_config)
#         self._client = redis.Redis(connection_pool=pool)
#         self.bit_size = self.get_bit_size(capacity, error_rate)
#         self.hash_count = self.get_hash_count(self.bit_size, capacity)
#         self._init_bloom_key()
#
#     def add(self, value):
#         for seed in range(self.hash_count):
#             result = mmh3.hash(value, seed) % self.bit_size
#             self._client.setbit(self.key, result, 1)
#         return True
#
#     def exists(self, value):
#         if not self._client.exists(self.key):
#             return False
#         for seed in range(self.hash_count):
#             result = mmh3.hash(value, seed) % self.bit_size
#             if not self._client.getbit(self.key, result):
#                 return False
#         return True
#
#     def _init_bloom_key(self):
#         lua_script = """
#         redis.call("SETBIT", KEYS[1], ARGV[1], ARGV[2])
#         redis.call("EXPIRE", KEYS[1], 604800)
#         """
#         if self._client.exists(self.key):
#             return True
#         execute = self._client.register_script(lua_script)
#         execute(keys=[self.key], args=[self.bit_size-1, 1])
#
#     @classmethod
#     def get_bit_size(cls, n, p):
#         return int(-(n * math.log(p)) / (math.log(2) ** 2))
#
#     @classmethod
#     def get_hash_count(cls, m, n):
#         return int((m / n) * math.log(2))
#
#
