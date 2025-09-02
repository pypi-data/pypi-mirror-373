from muse.data_source.demo_ds import DemoDataSource
from muse.data_source.data_source_api import DataSourceApi
from muse.data_source.base import DataSourceInterface

class _DataSourceManager:
    _data_source = DataSourceApi()
    def init_ds(self, ds):
        if isinstance(ds, DataSourceInterface):
            self._data_source = ds
            ds_name = ds.get_datasource_name()
            print(f'加载数据源: "{ds_name}" ...... 成功!')
    def get_ds(self):
        ds_name = self._data_source.get_datasource_name()
        # print(f'正在使用数据源: "{ds_name}" ......')
        return self._data_source

ds_manager = _DataSourceManager()