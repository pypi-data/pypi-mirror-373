import polars as pl
from muse.data_source.ds_manager import ds_manager
from muse.func_desc import VALID_FUNCS

TAGS = ['资产', '主体', '产品']
# BASIC_COLS = dsg.get_basic_inds()
def get_basic_cols():
    dsg = ds_manager.get_ds()
    return dsg.get_basic_inds()

# ASSET_INDS = dsg.get_asset_tags()       # 资产标签
def get_asset_tags():
    dsg = ds_manager.get_ds()
    return dsg.get_asset_tags()

# HLD_INDS = dsg.get_asset_inds()          # 持仓指标
def get_asset_cols():
    dsg = ds_manager.get_ds()
    return dsg.get_asset_inds()

# ISSUER_INDS = ASSET_INDS + HLD_INDS
def get_asset_all_cols():
    return get_asset_tags() + get_asset_cols()

# PORT_TAGS = dsg.get_port_tags()       # 产品标签
def get_port_tags():
    dsg = ds_manager.get_ds()
    return dsg.get_port_tags()

# PORT_ZB = dsg.get_port_inds()               # 产品指标
def get_port_cols():
    dsg = ds_manager.get_ds()
    return dsg.get_port_inds()

# PORT_INDS = PORT_TAGS + PORT_ZB     # 产品标签+指标
def get_port_all_cols():
    return get_port_tags() + get_port_cols()

# VALID_INDS = ASSET_INDS + HLD_INDS + ISSUER_INDS + PORT_INDS
def get_all_valid_cols():
    return get_asset_all_cols() + get_port_all_cols()


def get_port_inds(run_method: str, start_date: str, end_date: str, port_ids, inds: list):
    dsg = ds_manager.get_ds()
    port_inds = dsg.get_data(run_method, "产品指标", port_ids = port_ids, start_date=start_date, end_date=end_date, inds=inds)

    cols = ['产品代码', '日期']
    if inds is not None and len(inds) > 0:
        prop_list = filter_inds('产品', inds)
        cols = cols + prop_list
    if len(port_ids) > 0:
        df_lazy = (
            port_inds.lazy().filter(pl.col('产品代码').is_in(port_ids)).select(tuple(cols))
        )
    else:
        df_lazy = (
            port_inds.lazy().select(tuple(cols))
        )
    return df_lazy.collect()

def get_ports(run_method: str, start_date: str, end_date: str, tags: list, port_ids: list, inds: list, port_inds=None):
    # 获取产品指标（假设返回的是 Polars DataFrame）
    dsg = ds_manager.get_ds()
    if port_inds is None:
        port_inds = dsg.get_data(run_method, "产品指标", port_ids = port_ids, start_date=start_date, end_date=end_date, tags=tags, inds=inds)
    if port_inds is None or port_inds.is_empty():
        return pl.DataFrame()
    # 1. 产品标签筛选（OR 关系：任意一个标签为 "是"）
    port_condition = None
    if tags:
        # 检查标签是否存在
        valid_port_tags = [tag for tag in tags if tag in port_inds.columns]
        if not valid_port_tags:
            raise ValueError(f"产品标签 {tags} 不在数据列中！")

        # 动态构建 OR 条件
        port_condition = pl.any_horizontal(
            *[pl.col(tag) == "是" for tag in valid_port_tags]
        )
    if port_condition is not None:
        filtered_df = port_inds.filter(port_condition)
    else:
        filtered_df = port_inds  # 无筛选条件

    return filtered_df


def get_asset_by_tags(run_method: str, start_date: str, end_date: str, tags: list, drop_duplicates=False):
    dsg = ds_manager.get_ds()
    hlds = dsg.get_data(run_method, "持仓指标", start_date=start_date, end_date=end_date, tags=tags)
    if hlds is None or hlds.is_empty():
        return pl.DataFrame()

    # 1. 资产标签筛选（OR 关系：任意一个标签为 "是"）
    ast_condition = None
    if tags:
        # 检查标签是否存在
        valid_ast_tags = [tag for tag in tags if tag in hlds.columns]
        if not valid_ast_tags:
            raise ValueError(f"资产标签 {tags} 不在数据列中！")

        # 动态构建 OR 条件
        ast_condition = pl.any_horizontal(
            *[pl.col(tag) == "是" for tag in valid_ast_tags]
        )

    if ast_condition is not None:
        filtered_df = hlds.filter(ast_condition)
    else:
        filtered_df = hlds  # 无筛选条件
    return filtered_df

def get_asset_by_ids(run_method: str, start_date: str, end_date: str, sec_ids: list):
    dsg = ds_manager.get_ds()
    ast = dsg.get_data(run_method, '持仓指标', sec_ids = sec_ids, start_date=start_date, end_date=end_date)

    if len(sec_ids) > 0:
        df_lazy = (
            ast.lazy().filter(pl.col('资产代码').is_in(sec_ids))
        )
    else:
        df_lazy = (
            ast.lazy().select('资产代码', '资产简称', '主体代码').unique()
        )
    result = df_lazy.collect()
    return result


def get_asset_inds(run_method: str, start_date: str, end_date: str, sec_ids: list, inds: list):
    dsg = ds_manager.get_ds()
    ast_inds = dsg.get_data(run_method, '资产指标', sec_ids = sec_ids, start_date=start_date, end_date=end_date)
    cols = ['资产代码', '日期']
    if inds is not None and len(inds) > 0:
        prop_list = filter_inds('资产', inds)
        cols = cols + prop_list
    if len(sec_ids) > 0:
        df_lazy = (
            ast_inds.lazy().filter(pl.col('资产代码').is_in(sec_ids)).select(tuple(cols))
        )
    else:
        df_lazy = (
            ast_inds.lazy().select(tuple(cols))
        )

    return df_lazy.collect()


def get_assets(run_method: str, start_date: str, end_date: str, tags: list, sec_ids: list, inds: list):
    # 获取持仓数据（假设返回的是 Polars DataFrame
    dsg = ds_manager.get_ds()
    hlds = dsg.get_data(run_method, "持仓指标", sec_ids = sec_ids, start_date=start_date, end_date=end_date, tags=tags, inds=inds)
    if hlds is None or hlds.is_empty():
        return pl.DataFrame()

    # 1. 资产标签筛选（OR 关系：任意一个标签为 "是"）
    ast_condition = None
    if tags:
        # 检查标签是否存在
        valid_ast_tags = [tag for tag in tags if tag in hlds.columns]
        if not valid_ast_tags:
            raise ValueError(f"资产标签 {tags} 不在数据列中！")

        # 动态构建 OR 条件
        ast_condition = pl.any_horizontal(
            *[pl.col(tag) == "是" for tag in valid_ast_tags]
        )
    if ast_condition is not None:
        filtered_df = hlds.filter(ast_condition)
    else:
        filtered_df = hlds  # 无筛选条件

    return filtered_df

def get_issuer_by_tags(start_date: str, end_date: str, tags: list, drop_duplicates=False):
    dsg = ds_manager.get_ds()
    issuer = dsg.get_data('主体信息')
    df_lazy = (
        issuer.lazy().filter(pl.col('主体标签').is_in(tags))
    )

    return df_lazy.collect()

def get_issuer_by_ids(start_date: str, end_date: str, issuer_ids: list):
    dsg = ds_manager.get_ds()
    issuer = dsg.get_data('主体信息')
    if len(issuer_ids) > 0:
        df_lazy = (
            issuer.lazy().filter(pl.col('主体代码').is_in(issuer_ids))
        )
    else:
        df_lazy = (
            issuer.lazy().select('主体代码', '主体名称').unique()
        )
    return df_lazy.collect()

def get_issuer_inds(run_method: str, start_date: str, end_date: str, issuer_ids: list, inds: list):
    dsg = ds_manager.get_ds()
    issuer_inds = dsg.get_data(run_method, '主体指标', start_date=start_date, end_date=end_date, inds=inds)
    cols = ['主体代码', '日期']
    if inds is not None and len(inds) > 0:
        prop_list = filter_inds('主体', inds)
        cols = cols + prop_list

    if len(issuer_ids) > 0:
        df_lazy =(
            issuer_inds.lazy().filter(pl.col('主体代码').is_in(issuer_ids)).select(tuple(cols))
        )
    else:
        df_lazy = (
            issuer_inds.lazy().select(tuple(cols))
        )
    return df_lazy.collect()

def get_issuers(run_method: str, start_date: str, end_date: str, tags, issuer_ids: list, inds: list):
    if len(issuer_ids) > 0:
        issuers = get_issuer_by_ids(start_date, end_date, issuer_ids)
    elif len(tags) > 0:
        issuers = get_issuer_by_tags(start_date, end_date, tags)
    else:
        issuers = get_issuer_by_ids(start_date, end_date, [])
    # 根据资产中的代码和<日期>, 查询指标数据
    issuer_list = issuers.select('主体代码').unique()
    issuer_inds = get_issuer_inds(run_method, start_date, end_date, issuer_list, inds)
    issuers = issuers.join(issuer_inds, on=['主体代码'], how='left')
    return issuers

def get_hld_inds(run_method: str, start_date: str, end_date: str, port_ids: list, sec_ids: list, inds: list, penetrate=None):
    dsg = ds_manager.get_ds()
    cols = ['资产代码', '产品代码', '日期']
    if inds is not None and len(inds) > 0:
        hld_list = filter_inds('持仓', inds)
        cols = cols + hld_list

    # 根据资产中的代码和<日期>, 查询指标数据
    hld = dsg.get_data(run_method, '持仓指标', port_ids = port_ids, sec_ids = sec_ids, start_date=start_date, end_date=end_date, inds = inds, penetrate = penetrate)

    df_lazy = (
        hld.lazy().select(tuple(cols)).filter(pl.col('产品代码').is_in(port_ids) & pl.col('资产代码').is_in(sec_ids))
    )
    return df_lazy.collect()

def get_hlds3(run_method: str, start_date: str, end_date: str, asts: list, ports: list, inds: list):
    sec_ids = asts.select('资产代码').unique()
    port_ids = ports.select('产品代码').unique()
    # 获取持仓指标
    hlds = get_hld_inds(run_method, start_date, end_date, port_ids, sec_ids, inds)
    df_lazy =(
       hlds.lazy().join(asts.lazy(), on=['资产代码', '日期'], how='left',suffix="_asts")
                  .join(ports.lazy(), on=['产品代码', '日期'], how='left',suffix="_ports")
    )
    hlds = df_lazy.collect()
    df_lazy = (
        hlds.lazy().select([col for col in hlds.columns if not ('_asts' in col or '_ports' in col)])
    )
    hlds = df_lazy.collect()
    return hlds

def get_hlds2(run_method: str, start_date: str, end_date: str, asts, issuers, ports, inds: list, penetrate=None):
    issuer_ids = issuers.select('主体代码').unique()
    ast_lazy = (
        asts.lazy().filter(pl.col('主体代码').is_in(issuer_ids)).join(issuers.lazy(), on=['主体代码', '日期'], how='left')
    )
    ast_issuers = ast_lazy.collect()
    sec_ids = ast_issuers.select('资产代码').unique()
    port_ids = ports.select('产品代码').unique()
    # 获取持仓指标
    hlds = get_hld_inds(run_method, start_date, end_date, port_ids, sec_ids, inds, penetrate=penetrate)
    # 将资产数据补齐
    df_lazy = (
        hlds.lazy().join(ast_lazy, on=['资产代码', '日期'], how='left').join(ports.lazy(), on=['产品代码', '日期'], how='left')
    )
    hlds = df_lazy.collect()
    return hlds

def get_hlds(run_method: str, start_date: str, end_date: str, ast_tags: list, port_tags: list,  inds: list, sec_ids=None, port_ids=None, penetrate=None):
    dsg = ds_manager.get_ds()
    # try:
        # 获取持仓数据（假设返回的是 Polars DataFrame）
    merge_tags = ast_tags + port_tags
    hlds = dsg.get_data(run_method, "持仓指标", sec_ids = sec_ids, port_ids = port_ids, start_date=start_date, end_date=end_date, tags=merge_tags, inds=inds, penetrate=penetrate)
    if hlds is None or hlds.is_empty():
        return pl.DataFrame()

    # 1. 资产标签筛选（OR 关系：任意一个标签为 "是"）
    ast_condition = None
    if ast_tags:
        # 检查标签是否存在
        valid_ast_tags = [tag for tag in ast_tags if tag in hlds.columns]
        if not valid_ast_tags:
            raise ValueError(f"资产标签 {ast_tags} 不在数据列中！")

        # 动态构建 OR 条件
        ast_condition = pl.any_horizontal(
            *[pl.col(tag) == "是" for tag in valid_ast_tags]
        )

    # 2. 产品标签筛选（OR 关系：任意一个标签为 "是"）
    port_condition = None
    if port_tags:
        # 检查标签是否存在
        valid_port_tags = [tag for tag in port_tags if tag in hlds.columns]
        if not valid_port_tags:
            raise ValueError(f"产品标签 {port_tags} 不在数据列中！")

        # 动态构建 OR 条件
        port_condition = pl.any_horizontal(
            *[pl.col(tag) == "是" for tag in valid_port_tags]
        )

    # 3. 组合条件（AND 关系）
    if ast_condition is not None and port_condition is not None:
        filtered_df = hlds.filter(ast_condition & port_condition)
    elif ast_condition is not None:
        filtered_df = hlds.filter(ast_condition)
    elif port_condition is not None:
        filtered_df = hlds.filter(port_condition)
    else:
        filtered_df = hlds  # 无筛选条件
    return filtered_df

def get_repository_inds(run_method: str, repository:str, ind_list:list, params:dict):
    dsg = ds_manager.get_ds()
    return dsg.get_repository_inds(run_method, repository, ind_list, params)

def get_inds(inds_type: str) -> list:
    dsg = ds_manager.get_ds()
    inds_df = dsg.get_data('测试', inds_type)
    return list(set(inds_df.columns) - set(get_basic_cols()))

def filter_inds(ind_type: str, inds: list):
    if len(inds) <= 0:
        return list()
    if ind_type == '资产':
        inds_list = get_asset_tags()
    elif ind_type == '主体':
        inds_list = get_asset_all_cols()
    elif ind_type == '持仓':
        inds_list = get_asset_cols()
    else:
        inds_list = get_port_all_cols()

    return list(set(inds).intersection(set(inds_list)))

def find_prop(cols: list):
    inds = [c for c in cols if c not in get_basic_cols()]
    if len(inds) > 0:
        return inds[0]
    else:
        return None

def find_all_props(cols: list):
    return [c for c in cols if c not in get_basic_cols()]

def find_basic(cols: list) -> list:
    inds = [c for c in cols if c in get_basic_cols()]
    return inds

def is_valid_indicator(prop: str) -> bool:
    return prop in get_all_valid_cols() + get_basic_cols()

def is_valid_ind(prop: str) -> bool:
    return prop in get_all_valid_cols()

def is_valid_func(func_name: str) -> bool:
    return func_name in VALID_FUNCS


if __name__ == '__main__':
    port_list = ['P01', 'P02', 'P03']
    port_props = ['单位净值', '个人投资者占比']
    port_tags = ['公募开放式', '固定收益类']
    ports = get_ports('', '', port_tags, [], port_props)
    asts = get_assets('', '', ['信用债', '债券回购'], [], ['资产到期日', '久期'])
    # df = get_issuers('', '', ['银行金融机构', '非银行金融机构'], [], ['上一季度末净资产'])
    sec_list = ['B1', 'B7', 'B8']
    # df = get_hld_inds('', '', port_list, sec_list, ['持仓市值'])
    df = get_hlds('', '', asts, ports, ['持仓市值'])
    df = df.select(pl.col('单位净值').alias('复权单位净值'))
    print(df)
