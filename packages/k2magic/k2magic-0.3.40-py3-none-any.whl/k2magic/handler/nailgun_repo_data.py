# 此文件来自东汽定制的抽数SDK
# 功能是通过java版的storage api直接从repo抽取数据，而不需要经过rest api
# 依赖k2a带有nailgun的v3 runtime

import os
import glob
import json
import time
import pandas as pd
import datetime

def readRepoData(repoName, beginTime, endTime, deviceIds, columns, limit=None, aggrFunction=None, aggrInterval=None, filter=None, valueFilter=None, desc=None):
    # output_dir = 'D:\\temp'
    # storage_dir = 'D:\\K2Box\\deploy\\storage'
    output_dir = '/temp'
    storage_dir = '/home/k2data/storage'
    repo_info = None
    request_json_file = os.getenv('k_extract_data_request_path')
    with open(request_json_file, 'r') as f:
        input_request_array = json.load(f)
        if input_request_array and len(input_request_array) > 0:
            for input_request in input_request_array:
                if input_request['repoSimpleName'] == repoName:
                    repo_info = input_request['repoInfo']
                    repoName = input_request['repo']
                    break
    if repo_info is None:
        print("输入repo不存在%s", repoName)
        return None
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(output_dir, repoName)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(output_dir, str(round(time.time() * 1000)))
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    aggregation = None
    if aggrFunction is not None and aggrInterval is not None:
        function = aggrFunction.upper()
        aggrValue = None
        if function.startswith("QUANTILE"):
            aggrValue = float(function[8:])/100
            function = "QUANTILE"
        aggregation = {
            'function': function,
            'interval': aggrInterval,
            'value': aggrValue
        }
    if valueFilter is not None:
        valueFilter = valueFilter.replace(' and ', ' && ')
        valueFilter = valueFilter.replace(' or ', ' || ')
    # filter格式化 colA:100,101,102;colB:200 -> {colA: [100, 101, 102], colB: [200]}
    filter_map = None
    if filter is not None:
        filter_list = filter.split(';')
        filter_map = {}
        for item in filter_list:
            split_index = item.find(':')
            if split_index <= 0 or split_index >= len(item) - 1:
                continue
            values = item[split_index+1:]
            filter_map[item[:split_index]] = values.split(',')
    request = {
        'repo': repoName,
        'deviceIds': deviceIds,
        'columns': columns,
        'beginTime': beginTime,
        'endTime': endTime,
        'filter': filter_map,
        'filterExpression': valueFilter,
        'limit': limit,
        'desc': desc,
        'outputDir': output_dir,
        'repoInfo': repo_info,
        'aggregation': aggregation,
    }
    request_json_file = output_dir + '/request.json'
    with open(request_json_file, 'w') as f:
        json.dump([request], f)

    jars = glob.glob(os.path.join(storage_dir, 'k2box-storage-tool-*.jar'))
    if len(jars) == 0:
        print("未找到抽数工具包")
        return None
    cmd = "ng com.k2data.k2box.storage.tool.service.ExtractDataService" \
          " false {request_json_file} " \
        .format(request_json_file=request_json_file)
    print("exec cmd: ", cmd)
    os.system(cmd)
    csv_files = glob.glob(os.path.join(output_dir, '*.csv'))
    if len(csv_files) == 0:
        return None
    csv_file = csv_files[0]
    df = pd.read_csv(csv_file, index_col=False, encoding='utf-8', na_values='null')
    if 'k_ts' in df:
        df['k_ts'] = df['k_ts'].apply(lambda x:datetime.datetime.fromtimestamp(x/1000))
    return df


if __name__ == '__main__':
    readRepoData("test_dedup", 1692028800000, 1692115200000, ["dev01"], ["k_device", "k_ts", "col1"], 10,
                 'quantile30', 86400000, 'key1:value1,value2;key2:value3,value4',
                 'col1 <= 3 and col2 > 5 or col3 < 3', False)
