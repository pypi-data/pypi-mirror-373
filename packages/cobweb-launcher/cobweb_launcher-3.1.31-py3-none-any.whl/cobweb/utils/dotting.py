import os
import json
import time

from aliyun.log import LogClient, LogItem, PutLogsRequest
from cobweb.base import Queue, logger


class LoghubDot:

    def __init__(self, stop):
        self.stop = stop
        self.queue = Queue()
        self.client = LogClient(
            endpoint=os.getenv("LOGHUB_ENDPOINT"),
            accessKeyId=os.getenv("LOGHUB_ACCESS_KEY"),
            accessKey=os.getenv("LOGHUB_SECRET_KEY")
        )

    def build(self, topic, **kwargs):
        temp = {}
        log_item = LogItem()
        for key, value in kwargs.items():
            if not isinstance(value, str):
                temp[key] = json.dumps(value, ensure_ascii=False)
            else:
                temp[key] = value
        contents = sorted(temp.items())
        log_item.set_contents(contents)
        self.queue.push((topic, log_item), direct_insertion=True)

    def build_run(self):
        while not self.stop.is_set():
            start_time = int(time.time())
            while True:
                cost_time = int(time.time()) - start_time
                if self.queue.length >= 1000 or cost_time > 10:
                    break
                time.sleep(0.5)
            try:
                log_item_info = {}
                for _ in range(1000):
                    its = self.queue.pop()
                    if not its:
                        break
                    topic, item = its
                    log_item_info.setdefault(topic, []).append(item)
                for topic, log_items in log_item_info.items():
                    request = PutLogsRequest(
                        project="databee-download-log",
                        logstore="log",
                        topic=topic,
                        logitems=log_items,
                        compress=True
                    )
                    self.client.put_logs(request=request)
            except Exception as e:
                logger.info(str(e))
