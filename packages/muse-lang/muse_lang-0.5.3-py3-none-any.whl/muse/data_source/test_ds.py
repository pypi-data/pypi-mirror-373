from muse.data_source.base import DataSourceInterface
from muse.data_source.ds_utils import filter_ports, filter_ports_sec, convert_decimal_to_float, get_all_unique_fields
from muse.muse_config import APP_LOCATE
import polars as pl

class TestDataSource(DataSourceInterface):
    data_locate = APP_LOCATE + '/data/'

    def get_datasource_name(self):
        return 'Test用数据源'

    def get_basic_inds(self):
        return ['资产代码', '资产名称', '资产标签', '产品代码', '产品简称', '产品标签', '主体代码', '主体名称', '主体标签', '日期']

    def get_port_tags(self):
        tags = pl.read_excel(self.data_locate + '产品标签列.xlsx')
        return tags.columns

    def get_port_inds(self):
        inds = pl.read_excel(self.data_locate + '产品指标列.xlsx')
        return inds.columns

    def get_asset_tags(self):
        tags = pl.read_excel(self.data_locate + '资产标签列.xlsx')
        return tags.columns

    def get_asset_inds(self):
        inds = pl.read_excel(self.data_locate + '资产指标列.xlsx')
        return inds.columns

    def get_data(self, run_method: str, data_subject: str, sec_ids: list = [], port_ids: list = [], tags: list = [],
                 inds: list = [], start_date=None, end_date=None, penetrate=None):
        if penetrate:
            penetrate = '全穿透'
        else:
            penetrate = '不穿透'
        pdf = None

        if data_subject == '持仓指标':
            asset_df = pl.read_excel(self.data_locate + '资产指标汇总.xlsx')
            asset_tags = pl.read_excel(self.data_locate + '资产标签.xlsx')
            asset_df = asset_df.join(asset_tags, on=['资产代码'], how='left')
            pdf = filter_ports_sec(pdf=asset_df, port_ids=port_ids, sec_ids=sec_ids, start_date=start_date,
                                   end_date=end_date)
            # 获得产品代码
            port_ids = pdf.select("产品代码").unique().to_series().to_list()
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx')
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            ports = filter_ports(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)
            # 合并资产和产品
            pdf = pdf.join(ports, on=['产品代码', '日期'], how='left')
            pdf = convert_decimal_to_float(pdf)
        elif data_subject == '产品指标':
            ports = pl.read_excel(self.data_locate + '产品指标汇总.xlsx')
            port_tags = pl.read_excel(self.data_locate + '产品标签.xlsx')
            ports = ports.join(port_tags, on=['产品代码'], how='left')
            pdf = filter_ports_sec(pdf=ports, port_ids=port_ids, start_date=start_date, end_date=end_date)

        merged_cols = tags + inds
        if len(merged_cols) > 0:
            all_cols = get_all_unique_fields(merged_cols, self.get_basic_inds())
            existing_cols = [c for c in all_cols if c in pdf.columns]
            pdf = pdf.select(existing_cols)
        return pdf

    def get_repository_inds(self, run_method: str, repository: str, ind_list: list, params: dict):
        # 处理指标列表
        port_tags = params.get('port_tags', None)
        asset_tags = params.get('asset_tags', None)
        start_date = params.get('start_date', None)
        end_date = params.get('end_date', None)
        port_ids = params.get('port_ids', None)
        if port_ids:
            port_ids = port_ids.split(',').strip()
        else:
            port_ids = []
        sec_ids = params.get('sec_ids', None)
        if sec_ids:
            sec_ids = sec_ids.split(',').strip()
        else:
            sec_ids = []
        # 读取指标库
        rep_locate = f'{self.data_locate}指标库/{repository}.xlsx'
        # 选择合适的指标
        df = pl.read_excel(rep_locate)
        existing_cols = [col for col in set(self.get_basic_inds() + ind_list) if col in df.columns]
        df = df.select(existing_cols)
        # 过滤产品代码、资产代码和日期区间
        df = filter_ports_sec(df, port_ids, sec_ids, start_date, end_date)
        # 处理产品标签
        if port_tags:
            # 检查标签是否存在
            valid_port_tags = [tag for tag in port_tags if tag in self.get_port_tags()]
            if not valid_port_tags:
                raise ValueError(f"产品标签 {port_tags} 不在数据列中！")
            p_tags = pl.read_excel(f'{self.data_locate}产品标签.xlsx')
            p_tags = p_tags.select(['产品代码'] + valid_port_tags)
            df = df.join(p_tags, on=['产品代码'], how='left')
            # 动态构建 OR 条件
            port_condition = pl.any_horizontal(
                *[pl.col(tag) == "是" for tag in valid_port_tags]
            )
            df = df.filter(port_condition)
        # 处理资产标签
        if asset_tags:
            # 检查标签是否存在
            valid_asset_tags = [tag for tag in asset_tags if tag in self.get_asset_tags()]
            if not valid_asset_tags:
                raise ValueError(f"资产标签 {asset_tags} 不在数据列中！")
            # 动态构建 OR 条件
            a_tags = pl.read_excel(f'{self.data_locate}资产标签.xlsx')
            a_tags = a_tags.select(['资产代码'] + valid_asset_tags)
            df = df.join(a_tags, on=['资产代码'], how='left')
            asset_condition = pl.any_horizontal(
                *[pl.col(tag) == "是" for tag in valid_asset_tags]
            )
            df = df.filter(asset_condition)
        return df