import muse.data_interface as di
from muse.func_desc import FUNC_DESC

def _parse_products(stms: list):
    assets = list()
    ports = list()
    for index, s in enumerate(stms):
        if '函数调用:资产' in s or '函数调用:产品' in s:
            tags = list()
            indicators = list()
            start = index
            param_index = index + 1
            if param_index < len(stms):
                if '函数参数1' in stms[param_index]:
                    param_index = param_index + 1
                    if param_index < len(stms):
                        for m in stms[param_index:]:
                            if '字符串字面值:' in m:
                                tags.append(m.split(':')[1].strip())
                                param_index = param_index + 1
                            elif '数组' in m:
                                param_index = param_index + 1
                                continue
                            else:
                                break
            if param_index < len(stms):
                if '函数参数2' in stms[param_index]:
                    param_index = param_index + 1
                    if param_index < len(stms):
                        for m in stms[param_index:]:
                            if '字符串字面值:' in m:
                                indicators.append(m.split(':')[1].strip())
                                param_index = param_index + 1
                            elif '数组' in m:
                                param_index = param_index + 1
                                continue
                            else:
                                break
            if '函数调用:资产' in s:
                assets.append({'标签': tags, '指标': indicators, '位置': (start, param_index)})
            else:
                ports.append({'标签': tags, '指标': indicators, '位置': (start, param_index)})
    return assets, ports


def parse_info(stms: list):
    last_s = stms[-1]

    tags = list()
    indicators = list()
    funcs = list()
    variables = list()
    for s in stms:
        if '函数调用:' in s:
            funcs.append(s.split(':')[1])
        if '变量:' in s:
            variables.append(s.split(':')[1])
    colors = dict()
    funcs = list(set(funcs))
    colors['函数'] = funcs
    variables = list(set(variables))
    colors['变量'] = variables
    assets, ports = _parse_products(stms)
    for a in assets:
        tags = tags + a['标签']
        indicators = indicators + a['指标']
    for p in ports:
        tags = tags + p['标签']
        indicators = indicators + p['指标']
    tags = list(set(tags))
    indicators = list(set(indicators))
    colors['标签'] = tags
    colors['指标'] = indicators

    prompts = {}

    last_index = len(stms) - 1
    # print(last_s)
    # 情况一： AST最后一个元素为[变量]：提示之前定义过的变量或者固有的内部函数
    # 例子：回购资产 = 回TAB
    # 返回前端： ‘prompts’: {‘变量’: [所有之前定义的变量列表], ‘函数’: [所有支持的函数列表]}
    if '变量:' in last_s or '数组第' in last_s:
        if len(assets) > 0 and (assets[-1]['位置'][1] == last_index or assets[-1]['位置'][1] == last_index + 1):
                v = last_s.split(':')[1].strip()
                # 继续向前找看是那个函数参数
                for s in reversed(stms):
                    if '函数参数1' in s:
                        asset_tags = di.get_asset_tags()
                        if v != '':
                            asset_tags = list()
                            for t in di.get_asset_tags():
                                if v in t:
                                    asset_tags.append(t)
                        prompts = {'资产标签': asset_tags, '原文': v}
                        break
                    if '函数参数2' in s:
                        asset_inds = di.get_asset_cols()
                        if v != '':
                            asset_inds = list()
                            for t in di.get_asset_cols():
                                if v in t:
                                    asset_inds.append(t)
                        prompts = {'资产指标': asset_inds, '原文': v}
                        break

        elif len(ports) > 0 and (ports[-1]['位置'][1] == last_index or ports[-1]['位置'][1] == last_index + 1):
                v = last_s.split(':')[1].strip()
                # 继续向前找看是那个函数参数
                for s in reversed(stms):
                    if '函数参数1' in s:
                        port_tags = di.get_port_tags()
                        if v != '':
                            port_tags = list()
                            for t in di.get_port_tags():
                                if v in t:
                                    port_tags.append(t)
                        prompts = {'产品标签': port_tags, '原文': v}
                        break
                    if '函数参数2' in s:
                        port_inds = di.get_port_cols()
                        if v != '':
                            port_inds = list()
                            for t in di.get_port_cols():
                                if v in t:
                                    port_inds.append(t)
                        prompts = {'产品指标': port_inds, '原文': v}
                        break
        elif '变量:' in last_s:
            variable = last_s.split(':')[1].strip()
            if '指标部分:' in stms[-2]:
                inds = list()
                for ind in indicators + di.get_all_valid_cols():
                    if variable in ind:
                        inds.append(ind)
                prompts = {'指标': inds, '原文': variable}
            else:
                f_list = []
                for f in di.VALID_FUNCS:
                    if variable in f:
                        f_list.append(f)
                var_list = []
                for v in variables:
                    if variable in v:
                        var_list.append(v)
                if variable in var_list:
                    var_list.remove(variable)
                if variable in colors['变量']:
                    colors['变量'].remove(variable)
                prompts = {'变量': var_list, '函数': f_list, '原文': variable}
    # AST最后一个是[函数参数1]：向前找到函数的名称，提示函数的调用方法
    # 例子：回购资产 = agg(TAB
    # 返回前端：’prompts’: {‘函数’: {函数名: agg, 函数描述: 函数描述}}
    elif '函数参数1' in last_s:
        for s in reversed(stms):
            if '函数调用:' in s:
                func_name = s.split(':')[1].strip()
                if func_name in FUNC_DESC:
                    func_desc = FUNC_DESC[func_name]
                else:
                    func_desc = func_name
                prompts = {'函数': {'函数名': func_name, '函数描述': func_desc}, '原文': func_name}
                break
    elif '指标部分:' in last_s:
        prompts = {'指标': indicators + di.get_all_valid_cols(), '原文': ''}

    # print(assets)
    # print(ports)
    # print(last_index)
    return colors, prompts