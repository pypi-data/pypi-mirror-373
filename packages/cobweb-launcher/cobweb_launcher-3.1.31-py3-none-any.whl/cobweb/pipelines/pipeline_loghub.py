import os
import json

from cobweb.base import BaseItem
from cobweb.pipelines import Pipeline
from aliyun.log import LogClient, LogItem, PutLogsRequest
from collections import defaultdict


class Loghub(Pipeline):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = LogClient(
            endpoint=os.getenv("LOGHUB_ENDPOINT"),
            accessKeyId=os.getenv("LOGHUB_ACCESS_KEY"),
            accessKey=os.getenv("LOGHUB_SECRET_KEY")
        )
        self.project = os.getenv("LOGHUB_PROJECT")
        self.source = os.getenv("LOGHUB_SOURCE")
        self.topic = os.getenv("LOGHUB_TOPIC")

    def build(self, item: BaseItem):
        log_item = LogItem()
        temp = item.to_dict
        for key, value in temp.items():
            if not isinstance(value, str):
                temp[key] = json.dumps(value, ensure_ascii=False)
        contents = sorted(temp.items())
        log_item.set_contents(contents)
        return (
            log_item,
            item.baseitem_topic or self.topic,
            item.baseitem_source or self.source,
            item.baseitem_project or self.project,
        )

    def upload(self, table, datas):

        upload_items = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for log_item, topic, source, project in datas:
            upload_items[project][source][topic].append(log_item)

        for request in [
            PutLogsRequest(
                logstore=table, project=project,
                topic=topic, source=source,
                logitems=log_items, compress=True
            ) for project, sources in upload_items.items()
            for source, topics in sources.items()
            for topic, log_items in topics.items()
        ]:
            self.client.put_logs(request=request)
