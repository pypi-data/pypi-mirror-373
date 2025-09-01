from speedbeesynapse.component.base import HiveComponentBase, HiveComponentInfo
import pathlib
import requests
import time

DEFAULT_HOST = '127.0.0.1'
DEFAULT_METHOD = 'POST'


class Parameter:
    def __init__(self, param):
        use_tls = param.get('use_tls', False)
        self.protocol = 'https' if use_tls else 'http'
        self.host = param.get('host', DEFAULT_HOST)
        self.port = param.get('port', 443 if use_tls else 80)
        self.path = param.get('path', '/')
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        self.method = param.get('method', DEFAULT_METHOD)


@HiveComponentInfo(uuid='{{REPLACED-UUID}}', name='HTTP Emitter', inports=1, outports=0)
class HiveComponent(HiveComponentBase):
    def main(self, raw_param):
        self.param = Parameter(raw_param)

        time.sleep(1.0)
        self.log.info("get columns")
        columns = self.in_port1.get_columns()
        for column in columns:
            self.log.info(column)

        with self.in_port1.ContinuousReader(start=self.get_timestamp()) as reader:
            while self.is_runnable():
                window_data = reader.read()
                if not window_data:
                    self.log.info("no data yet")
                    continue

                self.window_iteration(window_data)

    def window_iteration(self, window_data):
        for record in window_data.records:
            for columnvalue in record.data:
                if not isinstance(columnvalue.value, pathlib.Path):
                    self.log.debug(f'ignore columnvalue {columnvalue}')
                    continue

                self.send(columnvalue)

    def send(self, columnvalue):
        # self.log.info(str(columnvalue.column))
        with columnvalue.value.open(mode="rb") as fo:
            p = self.param

            actual_path = p.path \
                .replace('$SOURCENAME', columnvalue.column.source_name) \
                .replace('$COLUMNNAME', columnvalue.column.data_name)
            url = f'{p.protocol}://{p.host}:{p.port}{actual_path}'
            requests.request(p.method, url, data=fo)
