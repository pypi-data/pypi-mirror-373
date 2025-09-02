from abc import ABC, abstractmethod

class DataSourceInterface(ABC):
    @abstractmethod
    def get_datasource_name(self):
        """数据源名称"""
        pass

    @abstractmethod
    def get_port_tags(self):
        """获取产品标签"""
        pass

    @abstractmethod
    def get_port_inds(self):
        """获取产品指标"""
        pass

    @abstractmethod
    def get_asset_tags(self):
        """获取资产标签"""
        pass

    @abstractmethod
    def get_asset_inds(self):
        """获取产品指标"""
        pass

    @abstractmethod
    def get_basic_inds(self):
        """获取基础列指标"""
        pass

    @abstractmethod
    def get_data(self, run_method: str, data_subject: str, sec_ids: list=[], port_ids: list=[],
             tags: list=[], inds: list=[], start_date = None, end_date = None, penetrate=None):
        """获取资产标签、产品标签及指标信息"""
        pass

    @abstractmethod
    def get_repository_inds(self, run_method: str, repository: str, ind_list: list, params: dict):
        """获取指标库及指标信息"""
        pass