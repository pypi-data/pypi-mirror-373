# 指标提取引擎
# 根据金融对象.指标的方法提取金融对象的数值类指标
# 同一类金融对象需要一次性提取避免性能的额外开销
import logging
import polars as pl
import muse.data_interface as di

def indicator_handle(base, prop):
    if isinstance(base, pl.DataFrame) and prop not in base.columns:
        logging.error(f'调用点运算失败：{prop} 不在 {base}中')
        return prop, pl.DataFrame()
    return prop, base

def fetch_inds(params, port_ids=None, sec_ids=None, start_date=None, end_date=None, search_mode=None):
    # 第一个必填参数为指标库
    if len(params) < 3:
        logging.error(f'指标库调用函数需要3个参数，提供参数数量不正确')
        return pl.DataFrame()
    repository_name = params[0]
    ind_list = params[1]
    search_params = params[2]

    if port_ids:
        search_params['port_ids'] = port_ids
    if sec_ids:
        search_params['sec_ids'] = sec_ids
    if start_date:
        search_params['start_date'] = start_date
    if end_date:
        search_params['end_date'] = end_date

    return di.get_repository_inds(search_mode, repository_name, ind_list, search_params)