import os
import logging
from typing import List

import requests
import pandas as pd
from pandas import DataFrame

from k2magic.handler.nailgun_repo_data import readRepoData


class K2A:

    def __init__(self, api_base=None, basic_auth=None):

        # 例如：https://dev.kstonedata.k2/api/v2
        self.api_base = api_base

        # 暂时只支持basic auth一种认证方式
        # 值例如：Basic YWRtaW46MjEyMzJGMjk3QTU3QTVBNzQzODk0QTBFNEE4MDFGQzM =
        self.basic_auth = basic_auth

        # 日志配置
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        # 检查是否已经有处理器添加到这个logger，避免重复添加
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # 创建格式化器并将其添加到处理器
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
            console_handler.setFormatter(formatter)

            # 将处理器添加到logger
            self.logger.addHandler(console_handler)

    def is_online(self) -> bool:
        """
        当前python代码是否在k2assets作业容器里运行
        如果是在作业容器里运行的情况，环境变量里会有 k_job_id 项，以此作为判断依据。
        :return: True表示当前运行在容器里
        """
        job_id = os.environ.get('k_job_id')
        return job_id is not None

    def get_repo_data(self, repo: str, begin_time: int, end_time: int, devices: List[str], columns: List[str],
                      limit: int = 100, aggr_function: str = None, aggr_interval: int = None,
                      filter: str = None, value_filter: str = None, desc: bool = None) -> DataFrame:
        """
        从指定repo里读取数据。此方法会自动检测当前是否运行在k2a作业容器里：
            1. 如果是在k2a作业容器里，则通过storage api直接获取数据，提高效率；
            2. 如果不是在k2a作业容器里，则使用rest api获取数据；
        这样做的好处是在本地笔记本上调试好代码后，完全不用修改就可以上传到k2a知识沉淀里运行。
        :param repo:
        :param begin_time:
        :param end_time:
        :param devices:
        :param columns:
        :param limit:
        :param aggr_function:
        :param aggr_interval:
        :param filter:
        :param value_filter:
        :param desc:
        :return:
        """
        self.logger.info('Getting repo data')

        # 参数校验和处理
        if devices == None:
            devices = ['*']
        if columns == None:
            columns = ['*']
        if '*' not in columns and 'k_device' not in devices:
            columns.append('k_device')
        if '*' not in columns and 'k_ts' not in columns:
            columns.append('k_ts')

        # 如果是在k2a容器里运行的情况，环境变量里会有k_job_id项
        job_id = os.environ.get('k_job_id')

        if self.is_online():
            self.logger.info(f'Running in a k2a runtime container (job {job_id}), will use STORAGE API')
            return readRepoData(repo, begin_time, end_time, devices, columns, limit, aggr_function, aggr_interval,
                                filter, value_filter, desc)
        else:
            self.logger.info(f'Running standalone, will use REST API')
            return self._get_repo_data_by_rest(repo, begin_time, end_time, devices, columns, limit)

    def _get_repo_data_by_rest(self, repo: str, begin_time: int, end_time: int, devices: List[str],
                               columns: List[str],
                               limit: int = 100, aggr_function: str = None, aggr_interval: int = None,
                               filter: str = None, value_filter: str = None, desc: bool = None):
        """
        此方法的功能是通过rest api获取指定repo的时序数据，api文档：https://dev.kstonedata.k2/docs/developer-guide/index.html#/api/get-repo-data
        代码内容来自 https://gitlab.kstonedata.k2/data_analysis/k2assets_operators/blob/develop/package_util/k2_magic/handler/RepoHandler.py
        并在原有代码基础上做了重构和增加功能。
        :param repo:
        :param begin_time:
        :param end_time:
        :param devices:
        :param columns:
        :param limit:
        :return:
        """

        columns_str = ','.join(columns)
        device_str = ','.join(devices)

        params = f'columns={columns_str}&deviceIds={device_str}&beginTime={begin_time}&endTime={end_time}&limit={limit}'

        if aggr_function:
            params += f'&aggrFunction={aggr_function}'

        if aggr_interval:
            params += f'&aggrInterval={aggr_interval}'

        if value_filter:
            params += f'&valueFilter={value_filter}'

        if filter:
            params += f'&filter={filter}'

        if desc:
            params += f'&desc=true'

        url = f'{self.api_base.rstrip("/")}/repo-data/{repo}?{params}'
        self.logger.info(f'Request url: {url}')

        headers = {'Authorization': self.basic_auth}

        resp = requests.get(url, headers=headers, verify=False)
        self.logger.info(f'Status code: {resp.status_code}')

        if resp.status_code != 200:
            raise ConnectionError(resp.json())
        ### 将数据从json转换成dataframe
        data_list = []
        for rdata_dict in resp.json()['body']['items']:
            rdata = pd.Series(rdata_dict).to_frame().T
            data_list.append(rdata)

        if not len(data_list):
            df = pd.DataFrame()
            self.logger.warning("Got empty data!", UserWarning)
        else:
            df = pd.concat(data_list)
            df.index = range(len(df))
            df['k_ts'] = df['k_ts'].map(lambda x: str(pd.to_datetime(x * 10e5) + pd.to_timedelta('8H')))  ## 时间戳格式转换
        return df
