"""XML serializer component."""
from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET

from speedbeesynapse.component.base import DataType, HiveComponentBase, HiveComponentInfo, HiveWindowData, InColumn


@HiveComponentInfo(uuid='{{REPLACED-UUID}}', name='XML Serializer', inports=1, outports=1)
class HiveComponent(HiveComponentBase):

    """XML Serializer component."""

    def main(self, _param: str | None) -> None:
        """Execute main procedure."""
        self.fileclm = self.out_port1.Column('XMLFILE', DataType.FILE)

        #with self.in_port0.ContinuousReader(start=self.get_timestamp()) as reader:
        with self.in_port1.ContinuousReader(start=self.get_timestamp()) as reader:
            while self.is_runnable():
                window_data = reader.read()
                if not window_data:
                    self.log.debug('no data yet')
                    continue

                xml_data = self.make_xml(window_data)
                if xml_data:
                    self.insert_xml(window_data, xml_data)

    def make_xml(self, window_data: HiveWindowData) -> bytes | None:
        """
        Make xml string data.

        Examples:
            <?xml version="1.0" encoding="utf-8"?>
            <window-data>
              <record timestamp="2025-01-02T12:34:00.000000000Z">
                <column name="Column-int" data-type="UINT32">1</column>
                <column name="Column-float" data-type="FLOAT[3]">1.23 3.45 6.22</column>
                <column name="Column-string" data-type="STRING">aiueoあいうえお - 1</column>
              </record>
              <record timestamp="2025-01-02T12:34:00.250000000Z">
                <column name="Column-int" data-type="UINT32">2</column>
              </record>
              <record timestamp="2025-01-02T12:34:00.500000000Z">
                <column name="Column-int" data-type="UINT32">3</column>
                <column name="Column-string" data-type="STRING">aiueoあいうえお - 2</column>
              </record>
              <record timestamp="2025-01-02T12:34:00.750000000Z">
                <column name="Column-int" data-type="UINT32">4</column>
              </record>
            </window-data>

        """
        root = ET.Element('window-data')
        for record in window_data.records:
            elm_record = ET.SubElement(root, 'record')
            ts_datetime = datetime.datetime.fromtimestamp(record.timestamp / 1e9, tz=datetime.timezone.utc)
            elm_record.set('timestamp', ts_datetime.isoformat(timespec='microseconds'))

            for data in record.data:
                if data.value is not None and data.data_size > 0:
                    elm_clm = ET.SubElement(elm_record, 'column')
                    elm_clm.set('name', data.column.data_name)
                    elm_clm.set('data-type', to_data_type_label(data.column))
                    elm_clm.text = to_value_string(data.value)

        if hasattr(ET, 'indent'):
            # ET.indent is added at Python3.9.
            ET.indent(root, space='  ')
        return ET.tostring(root, encoding='utf-8', method='xml', xml_declaration=True)

    def insert_xml(self, window_data: HiveWindowData, xmltext: bytes) -> None:
        """Register XML text data into the column."""
        with self.fileclm.open_file() as fo:
            fo.write(xmltext)
            ts = self.get_timestamp()
            meta = {
                # 'filename': 'a', noqa
                'media_type': 'text/plain',
                'begin_timestamp': window_data.time_range[0],
                'end_timestamp': window_data.time_range[1],
            }
            self.fileclm.insert_file(fo, ts, meta)


def to_data_type_label(column: InColumn) -> str:
    """Return data-type label."""
    if column.array_size > 0:
        return f'{column.data_type.name}[{column.array_size}]'

    return f'{column.data_type.name}'


def to_value_string(value: any) -> str:
    """Return value string."""
    if isinstance(value, list):
        return ' '.join([str(v) for v in value])

    return str(value)
