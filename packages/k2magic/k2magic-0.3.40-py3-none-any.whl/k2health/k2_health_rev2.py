import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import os
import warnings
import matplotlib.pyplot as plt


# 健康模型训练: 对单个目标量进行训练的内部函数
def health_train_unit(df, col_X, col_y, input_scale=None, model_type='linear', outlier_filter=False, plot=False,
                      condition_name='default', **kwargs):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，包含因子量X、目标量Y对应的列， 要求Y有且只有一列，X至少一列，且仅包含一种工况下的数据，以时间作为index，按时间正序排列
        * col_X -> list/tuple: 因子量X对应的列名组成的列表，只有一列时采用包含一个元素的列表，model_type为'pca'时会忽略该参数
        * col_y -> str/list: 目标量y对应的列名，当类型为list时，model_type只能为'pca'
        * input_scale -> str/None: (default: None) 对输入量的scaling方式，目前支持的参数包括：
                                   - None: 不进行scaling
                                   - 'minmax': sklearn.preprocessing.MinMaxScaler
                                   - 'zscore': sklearn.preprocessing.StandardScaler
                                   - #####To do: 支持sklearn中全部常用的scaling方式#####
        * model_type -> str: (default: 'linear') 回归模型的类型，目前支持的参数包括：
                             - 'linear': 线性回归模型
                             - 'poly': 多项式回归模型
                             - 'pca': 主成分分析模型，【注意:】model_type为'pca'时，col_y须为包含至少两个元素的list
                             - #####To do: 按需求支持更多的拟合模型形式#####
        * outlier_filter -> bool: (default: False) 模型异常值过滤，置为True时将在第一次训练后移除预测残差较大的训练点再训练一次，通常用于提取系统行为的最稳定部分，
                                  model_type为'pca'时，outlier_filter会被忽略
        * plot -> bool: (default: False) 是否绘制训练结果图：
                        - False: 不绘制结果图
                        - True: 绘制结果图，绘制的图像将保存在'./figures/'目录中，文件名为'train_目标量_工况名称.png'
        * condition_name -> str: (default: 'default') 训练数据对应的工况名称，用于生成结果图的标题，在plot为False时被忽略
        * **kwargs -> 以关键字参数形式输入的回归模型超参数，目前有超参数需求的回归模型如下：
                      - model_type = 'poly', 所需超参数包括：
                          * order -> int: (必选) 多项式回归模型的阶次，必须为大于1的整数，一般推荐使用2或3以降低过拟合的风险
                      - model_type = 'pca'，所需超参数包括：
                          * n_components -> int/float: (必选) 为整数时，为保留的主元个数；为 (0, 1) 区间内的浮点数时为保留的解释方差比例
    return:
        * res -> dict: 包含训练得到的模型及相关信息的字典
            *keys:
                'model' -> Pipeline: 训练得到的模型Pipeline，包括预处理模型 (scaling、多项式特征生成等) 和回归模型
                'model_type' -> str: 模型类型
                'X' -> list: 模型的输入项列表
                'score' -> float/list: 模型在训练数据集上的得分，model_type为'pca'时为一个与col_y等长的list           #####To do: 引入交叉检验#####
                'sigma' -> float: 模型在训练数据上的拟合残差标准差，model_type为'pca'时为一个与col_y等长的list      #####To do: 引入交叉检验#####
                'start_time' -> str: 训练数据的起始时间，在输入数据无k_ts列时为空
                'end_time' -> str: 训练数据的结束时间，在输入数据无k_ts列是为空
                'residue_mean' -> float: 训练数据上的拟合残差均值，model_type为'pca'时为一个与col_y等长的list
    '''
    # 输入类型检查
    assert (type(col_X) is list) or (type(col_X) is tuple), "形参col_X要求是list或tuple类型"
    # assert type(col_y) is str, "形参col_y要求是str类型"
    assert (type(input_scale) is str) or (input_scale is None), "形参input_scale要求是str类型或为None"
    assert type(model_type) is str, "形参model_type要求是str类型"
    if model_type == 'pca':
        assert (type(col_y) is list) or (type(col_y) is tuple), "model_type为'pca'时，形参col_y要求是list或tuple类型"
        assert len(col_y) > 1, "model_type为'pca'时，col_y中至少须有2个元素"
    else:
        assert type(col_y) is str, "model_type不为'pca'时，形参col_y要求是str类型"
    assert type(outlier_filter) is bool, "形参outlier_filter要求是bool类型"
    assert type(plot) is bool, "形参plot要求是bool类型"
    # assert type(condition_name) is str, "形参condition_name要求是str类型"

    # 输入参数合法性检查
    input_scale_list = (None, 'minmax', 'zscore')
    assert input_scale in input_scale_list, "不支持的scaling模式'%s'，输入模式的可选项为: %s" % (
    input_scale, input_scale_list)
    model_type_list = ('linear', 'poly', 'pca')
    assert model_type in model_type_list, "不支持的拟合模型类型'%s'， 模型类型的可选项为: %s" % (
    model_type, model_type_list)

    # 输入df的列检查
    if model_type == 'pca':
        for clm in col_y:
            assert clm in df.columns, "输入数据中不存在目标列：'%s'" % clm
    else:
        assert col_y in df.columns, "输入数据中不存在目标量列: '%s'" % col_y
    for clm in col_X:
        assert clm in df.columns, "输入数据中不存在因子量列: '%s'" % clm

    # 输入df数据检查，为空时直接返回空模型
    if df.empty:
        res = {'model': None,
               'X': None,
               'score': None,
               'sigma': None,
               'start_time': None,
               'end_time': None,
               'residue_mean': None}
        warnings.warn("目标量为'%s',因子量为%s，工况为'%s'下的数据集为空，将返回空模型" % (col_y, col_X, condition_name),
                      RuntimeWarning)
        return res

    # 模型的输入输出整理
    X = df[col_X].values
    y = df[col_y].values
    print(f'    Y={col_y},X={col_X}, df.shape={df.shape} 模型输入检查完毕')

    # 组装模型pipeline
    pipeline_list = []
    ## scaling部分
    if input_scale is not None:
        if input_scale == 'minmax':
            scaler = MinMaxScaler()
        elif input_scale == 'zscore':
            scaler = StandardScaler()
        pipeline_list.append(('scaler', scaler))

    ## 多项式特征生成
    if model_type == 'poly':
        if 'order' not in kwargs:
            raise RuntimeError("model_type为'poly'时，必须使用关键词参数'order'输入多项式的阶次")
        assert (type(kwargs['order']) is int) and (kwargs['order'] > 0), "多项式拟合的阶次(order)必须为正整数"
        pipeline_list.append(('poly', PolynomialFeatures(degree=kwargs['order'])))

    ## 回归模型
    if model_type in ('linear', 'poly'):
        pipeline_list.append(('regression', LinearRegression()))
    elif model_type == 'pca':
        if 'n_components' not in kwargs:
            raise RuntimeError("model_type为'pca'时，必须使用关键词参数'n_components'输入保留的主元个数或解释方差比例")
        pipeline_list.append(('pca', PCA(n_components=kwargs['n_components'])))

    pipeline_model = Pipeline(pipeline_list)

    # 模型训练与相关输出参数计算
    if model_type == 'pca':  # 采用pca模型时，没有因子量x，且预测值y_pred需要经过一次变换后再反变换得到
        pipeline_model.fit(y)
        y_tr = pipeline_model.transform(y)
        y_pred = pipeline_model.inverse_transform(y_tr)
        residue = y - y_pred
        sigma = residue.std(axis=0)
        residue_mean = residue.mean(axis=0)
        model_score = 1 - (residue ** 2).sum(axis=0) / ((y - y.mean(axis=0)) ** 2).sum(axis=0)
    else:
        pipeline_model.fit(X, y)
        y_pred = pipeline_model.predict(X)
        model_score = pipeline_model.score(X, y)
        residue = y - y_pred
        sigma = residue.std()
        residue_mean = residue.mean()
    print(f'    Y={col_y},X={col_X}, df.shape={df.shape} 模型训练完毕')

    ## 处理异常值过滤的情况（outlier_filter = True):滤掉残差较大的点后再重新训练一次
    #  pca本身有异常值过滤机制（异常值一般占方差比例很小），因此采用pca模型时忽略异常值过滤过程
    if (outlier_filter) and (model_type != 'pca'):
        sample_use = (residue > residue_mean - 3 * sigma) & (residue < residue_mean + 3 * sigma)
        X_use = X[sample_use, :]
        y_use = y[sample_use]
        pipeline_model.fit(X_use, y_use)
        y_use_pred = pipeline_model.predict(X_use)
        model_score = pipeline_model.score(X_use, y_use)
        residue = y_use - y_use_pred
        sigma = residue.std()
        residue_mean = residue.mean()
        print(f'    去除异常值后，模型重训练完毕')

    ## 提取训练数据起止时间信息
    start_time = df.index[0]
    end_time = df.index[-1]

    # 画图
    if plot:
        if model_type == 'pca':
            N = len(col_y)
            fig, axes = plt.subplots(N, 1, figsize=(12, 6 * N))
            for i, ax in enumerate(axes):
                ax.plot(df.index, y[:, i])
                ax.plot(df.index, y_pred[:, i])
                ax.plot(df.index, y_pred[:, i] + 3 * sigma[i], '--')
                ax.plot(df.index, y_pred[:, i] - 3 * sigma[i], '--')
                ax.set_xlabel('x_ts')
                ax.set_ylabel(col_y[i])
                ax.grid()
                ax.legend(['y', 'y_pred', 'upper limit', 'lower limit'])
            if N <= 3:
                title = '%s_%s' % (col_y, condition_name)
            else:
                title = ','.join(col_y[:2]) + ' etc._' + condition_name
            axes[0].set_title(title)

        else:
            fig = plt.figure(figsize=(15, 3))
            if outlier_filter:  # 采用异常值过滤后再次训练的模型重新预测整个训练集上的目标值
                y_pred = pipeline_model.predict(X)
            plt.plot(df.index, df[col_y])
            plt.plot(df.index, y_pred, 'g', linewidth=0.5)
            plt.plot(df.index, y_pred + 3 * sigma, 'r--', linewidth=0.5)
            plt.plot(df.index, y_pred - 3 * sigma, 'r--', linewidth=0.5)
            plt.xlabel('timestamp')
            plt.ylabel(col_y)
            plt.grid(True)
            plt.legend([col_y, 'baseline', 'upper limit', 'lower limit'])
            plt.ylim([min(y_pred) - 4 * sigma, max(y_pred) + 4 * sigma])
            plt.title('%s_%s' % (col_y, condition_name))

        save_path = './figures'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        filename = 'train_%s_%s.png' % (col_y, condition_name)
        plt.savefig(os.path.join(save_path, filename), dpi=100)

    # 结果组装与输出
    res = {'model': pipeline_model,
           'X': col_X,
           'model_type': model_type,
           'score': model_score,
           'sigma': sigma,
           'start_time': start_time,
           'end_time': end_time,
           'residue_mean': residue_mean}
    return res


# 健康模型训练
def health_train(df, col_Y, col_C=None, model_config={}, plot=False):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，包含因子量X、目标量Y、工况量C (可选) 对应的列， 要求X、Y各至少有一列，C至多有一列，以时间作为index，按时间正序排列
        * col_Y -> list/tuple: 目标量Y对应的列名组成的列表，如['Y1', 'Y2', ...]，只有一个目标量时采用包含一个元素的列表，在包含pca模型时，col_Y中对应位置为pca模型训练的变量组，
                               使用','将变量组中的各个目标量名称拼接成一个长字符串
                               例如，在Y1, Y2, Y8采用回归模型，而Y3 ~ Y7采用pca模型时，对应的col_Y采用如下形式：
                               ['Y1', 'Y2', 'Y3,Y4,Y5,Y6,Y7', 'Y8']
        * col_C -> str/None: (default: None) 工况量C对应的列名，若为None则意味着不区分工况，所有数据将会当做同一工况处理
        * model_config -> dict: (default: 空字典) 每个目标量对应的模型设置，【注意:】该字典的keys须与形参col_Y中的元素一一对应
            *keys:
                'Y1' -> dict: 对目标量Y1的模型训练设置
                    *keys:
                        'X' -> list: 该目标量的因子量(即模型输入项)对应的列名列表，如['X1', 'X2', ...],只有一个因子量时采用包含一个元素的列表
                        'input_scale' -> str/None: 对输入量的scaling方式，选择下列各项中的一项：
                                                   - None: 不进行scaling
                                                   - 'minmax': sklearn.preprocessing.MinMaxScaler
                                                   - 'zscore': sklearn.preprocessing.StandardScaler
                                                   - #####To do: 支持sklearn中全部常用的scaling方式#####
                        'model_type' -> str: 回归模型的类型，选择下列各项中的一项：
                                             - 'linear': 线性回归模型
                                             - 'poly': 多项式回归模型
                                             - #####To do: 按需求支持更多的拟合模型形式#####
                        'model_param' -> dict: 回归模型的超参数，各种model_type下的超参数需求如下：
                                               - model_type = 'linear':
                                                   * 无超参数需求，可设置为{}
                                               - model_type = 'poly':
                                                   * order -> int: (必选) 多项式回归模型的阶次，必须为大于1的整数，一般推荐使用2或3以降低过拟合的风险
                        'outlier_filter' -> bool: 模型异常值过滤，置为True时将在第一次训练后移除预测残差较大的训练点再训练一次，通常用于提取系统行为的最稳定部分，
                                                  没有这一key时取为默认值False
                'Y2' -> dict: 同上
                'Y3,Y4,Y5,Y6,Y7' -> dict: 同上('model_type'对应为'pca')
                ...
        * plot -> bool: (default: False) 是否绘制训练结果图：
                        - False: 不绘制结果图
                        - True: 绘制结果图，对每个目标量在每个工况下的模型训练结果绘制一张PNG图片，以'train_目标量_工况名称.png'的方式命名，绘制的图像将保存在
                                './figures/'目录中
    return:
        *res -> dict： 包含训练得到的模型及相关信息的嵌套字典，keys为col_Y中的各项元素，如'Y1', 'Y2', ...
            *keys:
                'Y1' -> dict: 对目标量Y1在各种工况下训练得到的模型
                              - 在col_C不为None时，keys为各个工况的名称，即df[col_C].unique()中的各个元素，如'C1', 'C2', ...
                                每个key对应的value为该工况下训练得到的模型字典 (health_training_unit的输出)，示例如下:
                                {'C1': {'model': $$$,
                                        'X': $$$,
                                        'score': $$$,
                                        'sigma': $$$,
                                        'start_time': $$$,
                                        'end_time': $$$,
                                        'residue_mean': $$$}
                                 'C2': {'model': $$$,
                                        'X': $$$,
                                        'score': $$$,
                                        'sigma': $$$,
                                        'start_time': $$$,
                                        'end_time': $$$,
                                        'residue_mean': $$$}
                                 ...}
                              - 在col_C为None时，key为'default'，对应的value为采用全量数据训练得到的模型字典，示例如下:
                                {'default': {'model': $$$,
                                             'X': $$$,
                                             'score': $$$,
                                             'sigma': $$$,
                                             'start_time': $$$,
                                             'end_time': $$$,
                                             'residue_mean': $$$}}
                'Y2' -> dict: 同上
                'Y3,Y4,Y5,Y6,Y7' -> dict: 同上
                ...
    '''
    # 输入类型检查
    assert (type(col_Y) is list) or (type(col_Y) is tuple), "形参col_Y要求是list或tuple类型"
    assert (type(col_C) is str) or (col_C is None), "形参col_C要求是str类型或为None"
    assert type(model_config) is dict, "形参model_config要求是dict类型"
    assert type(plot) is bool, "形参plot要求是bool类型"

    # 输入df的列检查
    if col_C is not None:
        assert col_C in df.columns, "输入数据中不存在工况量列: '%s'" % col_C
    for Y in col_Y:
        if model_config[Y]['model_type'] != 'pca':
            assert Y in df.columns, "输入数据中不存在目标量列: '%s'" % Y
        else:
            for clm in Y.split(','):
                assert clm in df.columns, "输入数据中不存在目标量列: '%s'" % clm

    # 逐个目标量进行模型训练
    res = {}
    keys_require = ['X', 'input_scale', 'model_type', 'model_param']
    for y in col_Y:
        print('')
        print("#######开始目标量'%s'的基准模型训练#######" % y)

        # 检查model_config的合法性
        config = model_config[y]
        for k in keys_require:
            assert k in config, "模型配置(model_config)中缺少'%s'项" % k
        if 'outlier_filter' not in config:
            config['outlier_filter'] = False

        # 模型训练主过程
        if config['model_type'] == 'pca':  # 对pca模型需要将y拆成各个列名组成的list再输入到单元模型中
            y_in = y.split(',')
        else:
            y_in = y

        if col_C is None:
            model_train = health_train_unit(df, config['X'], y_in, input_scale=config['input_scale'],
                                            model_type=config['model_type'],
                                            outlier_filter=config['outlier_filter'], plot=plot, **config['model_param'])
            res[y] = {'default': model_train}
        else:
            res_y = {}
            for c, group in df.groupby(col_C):
                print("-------工况: '%s'-------" % c)
                model_train = health_train_unit(group, config['X'], y_in, input_scale=config['input_scale'],
                                                model_type=config['model_type'],
                                                outlier_filter=config['outlier_filter'], plot=plot, condition_name=c,
                                                **config['model_param'])
                res_y[c] = model_train
            res[y] = res_y

    return res


# 内部函数：计算统计窗口内的残差特征
def _cal_residue_feature(df):
    df_cal = df.copy()
    df_cal['if_lower'] = (df_cal['measurement'] < df_cal['lower'])
    df_cal['if_upper'] = (df_cal['measurement'] > df_cal['upper'])
    res_dict = {}

    # 基本统计量
    res_dict['max'] = df_cal['residue'].max()
    res_dict['min'] = df_cal['residue'].min()
    res_dict['mean'] = df_cal['residue'].mean()
    res_dict['std'] = df_cal['residue'].std()

    # 超限次数
    res_dict['upper_count'] = (df_cal['if_upper'] != df_cal['if_upper'].shift().fillna(False)).sum()
    res_dict['lower_count'] = (df_cal['if_lower'] != df_cal['if_lower'].shift().fillna(False)).sum()
    res_dict['outrange_count'] = res_dict['upper_count'] + res_dict['lower_count']

    # 超限比例
    res_dict['upper_ratio'] = df_cal['if_upper'].sum() / len(df_cal)
    res_dict['lower_ratio'] = df_cal['if_lower'].sum() / len(df_cal)
    res_dict['outrange_ratio'] = res_dict['upper_ratio'] + res_dict['lower_ratio']

    # 超限烈度
    if res_dict['upper_ratio'] == 0:
        res_dict['upper_power'] = 0
    else:
        res_dict['upper_power'] = (df_cal[df_cal['if_upper']]['residue'] ** 2).mean()
    if res_dict['lower_ratio'] == 0:
        res_dict['lower_power'] = 0
    else:
        res_dict['lower_power'] = (df_cal[df_cal['if_lower']]['residue'] ** 2).mean()
    if res_dict['outrange_ratio'] == 0:
        res_dict['outrange_power'] = 0
    else:
        res_dict['outrange_power'] = (df_cal[(df_cal['if_upper']) | (df_cal['if_lower'])]['residue'] ** 2).mean()

    res = pd.Series(res_dict, name='value').to_frame().reset_index().rename(columns={'index': 'feature_name'})
    return res


# 内部函数：绘制测量值、预测值和动态上下限阈值的时序曲线
def _health_assess_plot(residues):
    for x, residue in residues.groupby(["Y", 'condition']):
        col_y, condition_name = x[0], x[1]
        fig = plt.figure(figsize=(15, 3))
        plt.plot(residue.index, residue['measurement'])
        plt.plot(residue.index, residue['predict'], 'g', linewidth=0.5)
        plt.plot(residue.index, residue['upper'], 'r--', linewidth=0.5)
        plt.plot(residue.index, residue['lower'], 'r--', linewidth=0.5)
        min_val = residue['measurement'].quantile(0.01)
        max_val = residue['measurement'].quantile(0.99)
        interval = max_val - min_val
        plt.ylim([min_val - 0.1 * interval, max_val + 0.1 * interval])
        plt.xlabel('k_ts')
        plt.ylabel(col_y)

        plt.grid()
        plt.legend([col_y, 'baseline', 'upper limit', 'lower limit'])
        plt.title('%s_%s' % (col_y, condition_name))
        save_path = './figures'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        filename = 'assess_%s_%s.png' % (col_y, condition_name)
        plt.savefig(os.path.join(save_path, filename), dpi=100)


# 健康评估：对单个目标量，在单个工况使用训练的健康模型进行健康评估，输出残差及特征
def health_assess_unit(df, col_y, unit_model, n=3, condition_name='default', feature_index='right', plot=False):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，包含因子量X、目标量y对应的列， 要求y有且只有一列，X至少一列，且仅包含一种工况下的数据，以时间作为index，按时间正序排列
        * col_y -> str: 目标量y对应的列名，在模型类型为pca时为变量组中各个变量名采用','拼接得到的字符串
        * unit_model -> dict, 对应目标量与工况量的模型训练结果，至少包括以下各项：
            *keys:
                'X' -> list: 因子量X对应的列名组成的列表
                'model' -> Pipeline: 训练得到的模型Pipeline，包括预处理模型 (scaling、多项式特征生成等) 和回归模型
                'model_type' -> str: 模型类型，详见model_train_unit函数中对形参model_type的说明
                'sigma' -> float: 模型在训练数据上的拟合残差标准差
                'residue_mean' -> float: 训练数据上的拟合残差均值
        * n -> int: (default: 3) 用于确定动态上下限阈值的标准差倍数，必须为正整数
        * condition_name -> str: (default: 'default') 数据对应的工况名称
        * feature_index -> str: (default: 'right')残差统计值的索引选择，支持的参数包括：
                                - 'left': 残差统计索引为时间窗口左侧时间(起始时间)
                                - 'right': 残差统计索引为时间窗口右侧时间(结束时间)
                                - 'center': 残差统计索引为窗口的中间时间(起始时间与结束时间的均值)
        * plot -> bool: (default: False) 是否绘制结果图：
                        - False: 不绘制结果图
                        - True: 绘制结果图，绘制的图像将保存在运行环境的根目录上，文件名为'assess_目标量_工况名称.png'
    return:
        * residue -> pd.DataFrame: 模型预测结果、预测残差及上下限
            * columns:
                - 'Y' -> str: 目标量名称
                - 'condition' -> str: 工况名称
                - 'measurement' -> float: 测量值，即数据中的实际值
                - 'predict' -> float: 模型预测值
                - 'residue' -> float: 预测残差
                - 'upper' -> float: 预测上限
                - 'lower' -> float: 预测下限
        * residue_feature -> pd.DataFrame: 残差统计值
            * columns:
                - 'Y' -> str: 目标量名称
                - 'feature_name' -> str: 残差统计特征名称，输出的特征量包括：
                    'max': 残差最大值
                    'min': 残差最小值
                    'mean': 残差均值
                    'std': 残差标准差
                    'upper_count': 超出上限次数
                    'lower_count': 超出下限次数
                    'outrange_count': 超出动态阈值范围次数
                    'upper_ratio': 超出上限的时间占比
                    'lower_ratio': 超出下限的时间占比
                    'outrange_ratio': 超出动态阈值范围的时间占比
                    'upper_power': 超出上限部分的烈度 (平方均值)
                    'lower_power': 超出下限部分的烈度 (平方均值)
                    'outrange_power': 超出动态阈值范围部分的烈度 (平方均值)
                - 'value' -> float: 特征的值
    '''
    # 输入类型检查
    assert type(col_y) is str, "形参col_y要求是str类型"
    assert type(unit_model) is dict, "形参unit_model要求是dict类型"
    assert (type(n) is int) and (n > 0), "形参n要求是正整数"
    assert type(feature_index) is str, "形参feature_index要求是str类型"
    assert type(plot) is bool, "形参plot要求是bool类型"
    # assert type(condition_name) is str, "形参condition_name要求是str类型"

    # 输入参数合法性检查
    feature_index_list = ('right', 'left', 'center')
    assert feature_index in feature_index_list, "不支持的feature_index方式'%s'，输入模式的可选项为: %s" % (
    feature_index, feature_index_list)

    # unit_model合法性检查
    keys_require = ['X', 'model', 'sigma', 'residue_mean']
    for k in keys_require:
        assert k in unit_model, "基准模型中缺少'%s'项" % k

    # 输入df的列检查
    if unit_model['model_type'] != 'pca':
        assert col_y in df.columns, "输入数据中不存在目标量列: '%s'" % col_y
    else:
        for clm in col_y.split(','):
            assert clm in df.columns, "输入数据中不存在目标量列: '%s'" % clm
    for col_x in unit_model['X']:
        assert col_x in df.columns, "输入数据中不存在因子量列: '%s'" % col_x

    # 处理输入数据为空的情形: 返回空DataFrame
    if df.empty:
        residue = pd.DataFrame([], columns=['Y', 'condition', 'measurement', 'predict', 'residue', 'upper', 'lower'])
        residue_feature = pd.DataFrame([], columns=['Y', 'feature_name', 'value'])
        return residue, residue_feature

    # 模型预测与残差计算
    if unit_model['model_type'] == 'pca':  # pca模型情形
        # 残差计算
        y_list = col_y.split(',')
        y = df[y_list]
        y_tr = unit_model['model'].transform(y.values)
        y_pred = pd.DataFrame(unit_model['model'].inverse_transform(y_tr), index=y.index.copy(),
                              columns=y.columns.copy())
        residue = y - y_pred
        y = y.stack().reset_index().rename(columns={'level_1': 'Y', 0: 'measurement'})
        y_pred = y_pred.stack().reset_index().rename(columns={'level_1': 'Y', 0: 'predict'})
        residue = y.merge(y_pred, on=['k_ts', 'Y'], how='left')
        residue['condition'] = condition_name
        residue['residue'] = residue['measurement'] - residue['predict']
        residue['sigma'] = residue['Y'].map({clm: s for clm, s in zip(y_list, unit_model['sigma'])})
        residue['upper'] = residue['predict'] + n * residue['sigma']
        residue['lower'] = residue['predict'] - n * residue['sigma']
        residue = residue.set_index('k_ts')[['Y', 'condition', 'measurement', 'predict', 'residue', 'upper', 'lower']]

    else:  # 回归模型情形
        residue = df[[col_y]].copy().rename(columns={col_y: 'measurement'})
        residue['Y'] = col_y
        residue['condition'] = condition_name
        X = df[unit_model['X']].values
        residue['predict'] = unit_model['model'].predict(X)
        residue['residue'] = residue['measurement'] - residue['predict']
        residue['upper'] = residue['predict'] + n * unit_model['sigma']
        residue['lower'] = residue['predict'] - n * unit_model['sigma']
        residue = residue[['Y', 'condition', 'measurement', 'predict', 'residue', 'upper', 'lower']]

    # 残差特征统计
    rf_list = []
    for clm, group in residue.groupby('Y'):
        rf = _cal_residue_feature(group)
        rf['Y'] = clm
        if feature_index == 'left':
            rf['k_ts'] = df.index[0]
        elif feature_index == 'right':
            rf['k_ts'] = df.index[-1]
        elif feature_index == 'center':
            rf['k_ts'] = df.index[0] + (df.index[-1] - df.index[0]) / 2
        rf.set_index('k_ts', inplace=True)

        rf_list.append(rf)
    residue_feature = pd.concat(rf_list)

    # 画图
    if plot:
        _health_assess_plot(residue)

    return residue, residue_feature


# 健康在线评估
def health_assess(df, model, col_C=None, n=3, feature_index='right', plot=False):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，包含因子量X、目标量Y、工况量C对应的列， 要求Y有且只有一列，X至少一列,C至多有一列 (取决于训练模型时是否有工况列),以时间作为index，按时间正序排列
        * model -> dict: 包含训练得到的模型及相关信息的嵌套字典，具体数据结构参见health_train函数的输出数据说明
        * col_C -> str/None: (default: None) 工况量C对应的列名，若为None则意味着不区分工况，所有数据将会当做同一工况处理，【注意:】必须与模型训练时保持一致
        * n -> int: (default: 3) 用于确定动态上下限阈值的标准差倍数，必须为正整数
        * feature_index -> str: (default: 'right')残差统计值的索引选择，支持的参数包括：
                                - 'left': 残差统计索引为时间窗口左侧时间(起始时间)
                                - 'right': 残差统计索引为时间窗口右侧时间(结束时间)
                                - 'center': 残差统计索引为窗口的中间时间(起始时间与结束时间的均值)
        * plot -> bool: (default: False) 是否绘制结果图：
                        - False: 不绘制结果图
                        - True: 绘制结果图，对每个目标量在每个工况下的模型预测结果绘制一张PNG图片，以'assess_目标量_工况名称.png'的方式命名，绘制的图像将保存在
                                运行环境的根目录上
    return:
        * residue -> pd.DataFrame: 模型预测结果、预测残差及上下限
            * columns:
                - 'Y' -> str: 目标量名称
                - 'condition' -> str: 工况名称
                - 'measurement' -> float: 测量值，即数据中的实际值
                - 'predict' -> float: 模型预测值
                - 'residue' -> float: 预测残差
                - 'upper' -> float: 预测上限
                - 'lower' -> float: 预测下限
        * residue_feature -> pd.DataFrame: 残差统计值
            * columns:
                - 'Y' -> str: 目标量名称
                - 'feature_name' -> str: 残差统计特征名称，输出的特征量包括：
                    'max': 残差最大值
                    'min': 残差最小值
                    'mean': 残差均值
                    'std': 残差标准差
                    'upper_count': 超出上限次数
                    'lower_count': 超出下限次数
                    'outrange_count': 超出动态阈值范围次数
                    'upper_ratio': 超出上限的时间占比
                    'lower_ratio': 超出下限的时间占比
                    'outrange_ratio': 超出动态阈值范围的时间占比
                    'upper_power': 超出上限部分的烈度 (平方均值)
                    'lower_power': 超出下限部分的烈度 (平方均值)
                    'outrange_power': 超出动态阈值范围部分的烈度 (平方均值)
                - 'value' -> float: 特征的值
    '''
    # 输入类型检查
    assert type(model) is dict, "形参model要求是dict类型"
    assert (type(col_C) is str) or (col_C is None), "形参col_C要求是str类型或为None"
    assert (type(n) is int) and (n > 0), "形参n要求是正整数"
    assert type(feature_index) is str, "形参feature_index要求是str类型"
    assert type(plot) is bool, "形参plot要求是bool类型"

    # 输入df的列检查
    if col_C is not None:
        assert col_C in df.columns, "输入数据中不存在工况量列: '%s'" % col_C

    # 逐个目标量进行模型预测和残差统计
    residue_list = []
    residue_feature_list = []
    for y, model_y in model.items():
        if col_C is None:  # 不区分工况情形
            residue_cal, residue_feature_cal = health_assess_unit(df, y, model_y['default'], n=n,
                                                                  feature_index=feature_index, plot=plot)
            residue_list.append(residue_cal)
            residue_feature_list.append(residue_feature_cal)

        else:  # 区分工况情形，逐个工况进行模型预测和残差统计
            for c, model_c in model_y.items():
                df_c = df[df[col_C] == c]
                residue_cal, residue_feature_cal = health_assess_unit(df_c, y, model_c, n=n, condition_name=c,
                                                                      feature_index=feature_index, plot=plot)
                residue_list.append(residue_cal)
                residue_feature_list.append(residue_feature_cal)

    residue = pd.concat(residue_list)
    residue_feature = pd.concat(residue_feature_list)

    return residue, residue_feature


# 内部函数: 按照数据、窗口、步长生成时间段切片的list组合
def _gen_interval_list(df, window, step):
    steps = (df.index[-1] - df.index[0]) / pd.Timedelta(step)
    start_time = df.index[0]
    interval_list = []
    for i in range(int(steps) + 1):
        time_left = start_time + i * pd.Timedelta(step)
        interval_list.append([time_left, time_left + pd.Timedelta(window)])
    return interval_list


# 批量划分时间窗口进行健康在线评估，通常用于模拟
def health_assess_batch(df, model, col_C=None, n=3, window='1D', step='1H', feature_index='right', plot=False):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，包含因子量X、目标量Y、工况量C对应的列， 要求Y有且只有一列，X至少一列,C至多有一列 (取决于训练模型时是否有工况列),以时间作为index，按时间正序排列
        * model -> dict: 包含训练得到的模型及相关信息的嵌套字典，具体数据结构参见health_train函数的输出数据说明
        * col_C -> str/None: (default: None) 工况量C对应的列名，若为None则意味着不区分工况，所有数据将会当做同一工况处理，【注意:】必须与模型训练时保持一致
        * n -> int: (default: 3) 用于确定动态上下限阈值的标准差倍数，必须为正整数
        * window -> str/pd.Timedelta: (defalut: '1H') 残差特征的统计时间窗口，要求必须为合法的DateOffset字符串，或pd.Timedalta对象
        * step -> str/pd.Timedelta: (defalut: '1H') 残差特征的统计时间步长，要求必须为合法的DateOffset字符串，或pd.Timedalta对象
        * feature_index -> str: (default: 'right')残差统计值的索引选择，支持的参数包括：
                                - 'left': 残差统计索引为时间窗口左侧时间(起始时间)
                                - 'right': 残差统计索引为时间窗口右侧时间(结束时间)
                                - 'center': 残差统计索引为窗口的中间时间(起始时间与结束时间的均值)
    return:
        * residue -> pd.DataFrame: 模型预测结果、预测残差及上下限
            * columns:
                - 'Y' -> str: 目标量名称
                - 'condition' -> str: 工况名称
                - 'measurement' -> float: 测量值，即数据中的实际值
                - 'predict' -> float: 模型预测值
                - 'residue' -> float: 预测残差
                - 'upper' -> float: 预测上限
                - 'lower' -> float: 预测下限
        * residue_feature -> pd.DataFrame: 残差统计值
            * columns:
                - 'Y' -> str: 目标量名称
                - 'feature_name' -> str: 残差统计特征名称，输出的特征量包括：
                    'max': 残差最大值
                    'min': 残差最小值
                    'mean': 残差均值
                    'std': 残差标准差
                    'upper_count': 超出上限次数
                    'lower_count': 超出下限次数
                    'outrange_count': 超出动态阈值范围次数
                    'upper_ratio': 超出上限的时间占比
                    'lower_ratio': 超出下限的时间占比
                    'outrange_ratio': 超出动态阈值范围的时间占比
                    'upper_power': 超出上限部分的烈度 (平方均值)
                    'lower_power': 超出下限部分的烈度 (平方均值)
                    'outrange_power': 超出动态阈值范围部分的烈度 (平方均值)
                - 'value' -> float: 特征的值
    '''
    # 输入类型检查
    assert (type(window) is str) or (type(window) is pd.Timedelta), "形参window要求是str类型或pandas.Timedelta对象"
    assert (type(step) is str) or (type(step) is pd.Timedelta), "形参step要求是str类型或pandas.Timedelta对象"
    assert type(plot) is bool, "形参plot要求是bool类型"

    # 根据window和step生成残差的统计时间窗口列表
    interval_list = _gen_interval_list(df, window, step)
    # print("interval_list", interval_list)

    # 对各个时间窗口计算残差及特征并汇总
    residue_list, feature_list = [], []
    for inter in interval_list:
        data = df[inter[0]:inter[1]]
        if not data.empty:
            residue, feature = health_assess(data, model, col_C=col_C, n=n)

            residue_list.append(residue)
            feature_list.append(feature)

    residue = pd.concat(residue_list)
    # 去掉residue中因窗口重叠导致的重复数据
    residue = residue.reset_index()
    residue = residue.rename(columns={residue.columns[0]: 'k_ts'}).drop_duplicates(['k_ts', 'Y']).set_index('k_ts')
    residue_feature = pd.concat(feature_list)

    # 画图
    if plot:
        _health_assess_plot(residue)
    return residue, residue_feature


# 健康评分函数：线性
def linear_score(z, llim, ulim):
    '''
    param:
        * z -> float: 特征取值
        * llim -> float: 扣分下限，z <= llim时不扣分
        * ulim -> float: 扣分上限，z >= ulim时扣除所有分
    return:
        * score -> float: 扣除的健康分数值
    '''
    if z <= llim:
        return 0
    elif z >= ulim:
        return 100
    else:
        return 100 * (z - llim) / (ulim - llim)


# 健康评分函数：二次项
def binomial_score(z, llim=0, a=1):
    """
    计算特征健康度
    :param
        * z -> float: 特征取值
        * llim -> float: 扣分下限，z <= llim时不扣分
        * a -> int: 二次项系数
    :return
        * score -> float: 扣除的健康分数值
    """
    if z <= llim:
        return 0
    else:
        return a * (z - llim) ** 2


# 内部函数，对单个目标量的健康评分
def _health_scoring_unit(residue_feature, config, lower_limit=0):
    '''
    param:
        * residue_feature -> pd.DataFrame: 残差统计结果
            * columns:
                - 'Y' -> str: 目标量名称
                - 'feature_name' -> str: 残差统计特征名称
                - 'value' -> float: 特征的值
        * config -> dict: 评分函数配置，keys为进行评分采用的残差特征的名称，如'mean', 'outrange_count', ...
            * keys:
                'mean' -> dict: 对该项特征的评分函数设置
                    *keys:
                        'weight' -> float: 评分权重
                        'map_func' -> callable: 评分函数
                        'params'-> dict: 评分函数需要的参数
                'outrange_count' -> dict: 同上
                ...
        * lower_limit -> float/int: 健康评分的输出下限，小于下限的部分将被置为下限值
    return:
        * health_score -> pd.Series: 健康评分结果
            *columns:
                -'score' -> float: 健康评分
    '''
    score_list = []
    for feature, feature_config in config.items():  # 对每项特征依次计算扣分值
        df_f = residue_feature[residue_feature['feature_name'] == feature]
        score = df_f['value'].apply(feature_config['map_func'], **feature_config['params']) * feature_config['weight']
        score_list.append(score.rename(feature))

    df_score = pd.concat(score_list, axis=1)
    health_score = 100 - df_score.sum(axis=1)
    health_score.rename('score', inplace=True)
    health_score[health_score < lower_limit] = lower_limit
    return health_score


# 健康值评分
def health_scoring(residue_feature, config, lower_limit=0, plot=False):
    '''
    param:
        * residue_feature -> pd.DataFrame: 残差统计结果
            * columns:
                - 'Y' -> str: 目标量名称
                - 'feature_name' -> str: 残差统计特征名称
                - 'value' -> float: 特征的值
        * config -> dict: 评分函数配置，keys为进行评分采用的残差特征的名称，如'mean_value', 'outrange_count', ...
            * keys:
                'mean' -> dict: 对该项特征的评分函数设置
                    *keys:
                        'weight' -> float: 评分权重
                        'map_func' -> callable: 评分函数
                        'params'-> dict: 评分函数需要的参数
                'outrange_count' -> dict: 同上
                ...
        * lower_limit -> float/int: 健康评分的输出下限，小于下限的部分将被置为下限值
        * plot -> bool: (default: False) 是否绘制结果图：
                        - False: 不绘制结果图
                        - True: 绘制结果图，绘制的图像将保存在运行环境的根目录上，文件名为'health_score.png'
    return:
        * health_score -> pd.DataFrame: 健康评分结果
            *columns:
                -'Y' -> str: 目标量名称
                -'score' -> float: 健康评分
    '''
    # 输入类型检查
    assert type(config) is dict, "形参config要求是dict类型"
    assert (type(lower_limit) is float) or (type(lower_limit) is int), "形参lower_limit要求是float或int类型"

    health_score = residue_feature.groupby('Y').apply(_health_scoring_unit, config=config, lower_limit=lower_limit)

    if plot:
        health_score.T.plot(figsize=(12, 100), subplots=True)
        save_path = './figures'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        filename = 'health_score.png'
        plt.savefig(os.path.join(save_path, filename), dpi=400)

    health_score = health_score.stack().reset_index(level=0).rename(columns={0: 'score'})
    return health_score


# 按测点与部件的归属关系以及部件、设备、系统之间的归属关系（设备树），将健康评分由测点级起向上逐级聚合
def score_agg(para_score, config_point, config_part=pd.DataFrame()):
    '''
    param:
        * df_score -> pd.DataFrame: 测点健康评分计算结果
            * columns:
                - 'Y' -> str: 测点名称
                - 'score' -> float: 健康评分
        * config_point -> pd.DataFrame: 点位配置表（测点与部件的对应关系）
            * columns:
                - 'point_name': 测点名称，对应'Y'
                - 'device_en': 该测点所属设备（子设备、部件）英文名
        * config_part -> pd.DataFrame: 设备树（设备与部件、系统与设备等的包含关系）
            * columns:
                - 'child_device': 子设备
                - 'parent_device': 父设备
    return:
        * df_score -> pd.DataFrame: 测点健康分数
            * columns:
                - 'k_ts' -> pd.Timestamp: 时间戳
                - 'sub_unit' -> str: 测点、子部件、部件
                - 'value' -> float: 健康得分
    '''
    s = para_score.reset_index().drop_duplicates(['k_ts', 'Y'])
    s = s.pivot(index='k_ts', columns="Y", values='score')  # 展成宽表
    mapping_point_dict = \
    config_point[config_point["point_name"].isin(s.columns)].dropna(subset=["device_name"]).groupby("device_name")[
        "point_name"].apply(list)
    mapping_dict = mapping_point_dict  # 设备树为空的情况下仅由测点表生成映射关系

    if not config_part.empty:  # 存在设备树的情况下将设备的包含关系扩展进映射关系中
        mapping_part_dict = config_part.groupby("parent_device")["child_device"].apply(list)
        mapping_dict = dict(mapping_point_dict, **mapping_part_dict)

    for key, value in mapping_dict.items():
        cosl = list(s.columns)
        inner_cols = list(set(value) & set(cosl))
        s[key] = s[inner_cols].sum(axis=1) / len(inner_cols)

    device_score = pd.melt(s.reset_index(), id_vars='k_ts').rename(columns={"Y": "sub_unit"})
    return device_score.dropna(subset=['value'])


# 健康报警生成
def gen_alarm(df, config):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，长表形式，包含部件名称（测点、部件、设备等）， 健康评分和对应的时间
            * columns:
                - 'k_ts'  -> pd.Timestamp: 时间戳
                - 'sub_unit' -> str: 部件名称
                - 'value' -> str: 健康评分
        * config ->pd.DataFrame: 报警生成配置表
            *columns:
                'value' -> float: 该等级对应的健康评分阈值，健康度低于阈值时触发该等级报警，高等级报警覆盖低等级报警
                'alarm_type' -> str: 报警类型，一般为'健康度报警'
                'alarm_level'-> int: 报警等级，规定为1,2,3..，数值越大，等级越高
                'level_cn' -> str: 报警等级对应的中文名称，用于在应用中的展现等
                'alarm_desc'-> str: 报警描述
    return:
        * df_alarm -> pd.DataFrame: 模型报警结果
            * columns:
                - 'k_ts' -> pd.Timestamp: 时间戳
                - 'sub_unit' -> str: 部件名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> int: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'alarm_desc' -> str: 报警描述
    '''

    # 阈值判断
    config = config.sort_values('alarm_level').reset_index(drop=True)
    flags = [df['value'] < k for k in config['value']]

    # 筛选出满足level1阈值的报警，该报警也满足level2/3的阈值要求。多个等级报警阈值同时满足时，保留最高等级报警。
    df_alarm = df.loc[flags[0]]

    for i, row in config.iterrows():
        df_alarm.loc[flags[i], 'alarm_type'] = row['alarm_type']
        df_alarm.loc[flags[i], 'alarm_level'] = row['alarm_level']
        df_alarm.loc[flags[i], 'alarm_desc'] = row['alarm_desc']
        df_alarm.loc[flags[i], 'level_cn'] = row['level_cn']

    df_alarm['alarm_level'] = df_alarm['alarm_level'].astype('int')
    df_alarm.drop(['value'], axis=1, inplace=True)
    df_alarm.sort_values('k_ts', inplace=True)
    df_alarm.reset_index(drop=True, inplace=True)

    return df_alarm


# 内部函数，报警间隔时间计算与合并报警标记
def _gen_groups(df, time_diff=60):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，某一报警在统计窗口内的数据
            * columns:
                - 'k_ts'  -> Timestamp: 时间列
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> int: 报警等级
                - 'alarm_desc' -> str: 报警描述

        * time_diff -> int(default: 60): 相同报警之间的时间间隔，单位为分钟，小于等于该值时，为同一组报警

    return:
        * df -> pd.DataFrame: 报警分组结果
            * columns:
                - 'k_ts'  -> Timestamp: 时间列
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> int: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'alarm_desc' -> str: 报警描述
                - 'groups' -> str: 分组结果
    '''
    # 输入类型检查
    assert (type(time_diff) is float) or (type(time_diff) is int), "形参time_diff要求是float或int类型"

    df = df.sort_values('k_ts')

    # 对报警进行分组，间隔时间小于等于time_diff的分为一组，组号从1开始，例如第一组为1、第二组为2.....
    df['groups'] = (df['k_ts'].diff().dt.total_seconds() / 60 > time_diff).cumsum() + 1

    return df


def _gen_start_end_time(df, different_levels=True):
    '''
    param:
        * df -> pd.DataFrame: 输入数据，某一报警在某一分组的数据
            * columns:
                - 'k_ts'  -> Timestamp: 时间列
                  - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> int: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'alarm_desc' -> str: 报警描述
                - 'groups' -> str: 分组
        * different_levels -> bool: (default: True) 用于选择报警是否按报警等级分组

    return:
        * res -> pd.DataFrame: 报警组数据，包含该分组报警的起止时间数据
            * columns:
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> int: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'start_time' -> Timestamp: 报警组开始时间
                - 'end_time' -> Timestamp: 报警组结束时间
                - 'count' -> int: 报警组里该报警的次数
                - 'sort' -> int: 统计窗口内相同报警的报警组的序号，按end_time正序排列
    '''
    # 输入类型检查
    assert type(different_levels) is bool, "形参different_levels要求是bool类型"

    # 取按时间正序排列的第一行数据作为起始时间
    df = df.sort_values('k_ts')
    res = df.head(1)
    res = res.rename(columns={'k_ts': 'start_time'})

    # 取最后一行数据的时间作为结束时间
    res['end_time'] = df.iloc[-1]['k_ts']
    res['count'] = df.shape[0]
    res['sort'] = df.iloc[0]['groups']
    if not different_levels:
        res['alarm_level'] = df['alarm_level'].max()

    res = res[['sub_unit', 'alarm_type', 'alarm_level', 'start_time', 'end_time', 'count', 'sort']]
    return res


# 报警组合并，将间隔时间较小的同类报警合并为同一报警组
def alarm_merge(df_alarm, df_alarm_merge_historical=pd.DataFrame(), time_diff=60, different_levels=True):  # 保留所有报警组

    '''
    param:
        * df_alarm -> pd.DataFrame: 某一统计窗口（新生成）的报警数据
            * columns:
                - 'k_ts'  -> Timestamp: 时间列
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> str: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'alarm_desc' -> str: 报警描述

        * df_alarm_merge_historical -> pd.DataFrame: 历史报警组数据，包含该分组报警的起止时间数据
            * columns:
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> str: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'start_time' -> Timestamp: 报警开始时间
                - 'end_time' -> Timestamp: 报警结束时间
                - 'count' -> int: 报警组里该报警的次数
                - 'sort' -> int: 报警组的序号，按end_time正序排列
                - 'id' -> str: 报警组id

        * time_diff -> int(default: 60): 相同报警之间的时间间隔，单位为分钟，小于等于该值时，为同一组报警
        * different_levels -> bool: (default: True) 用于选择报警是否按报警等级分组

    return:
        * res -> pd.DataFrame: 统计窗口内的报警组数据
            * columns:
                - 'sub_unit' -> str: 目标量名称
                - 'alarm_type' -> str: 报警类型
                - 'alarm_level' -> str: 报警等级
                - 'level_cn' -> str: 报警等级名称
                - 'start_time' -> Timestamp: 报警开始时间
                - 'end_time' -> Timestamp: 报警结束时间
                - 'count' -> int: 报警组里该报警的次数
                - 'sort' -> int: 报警组的序号，按end_time正序排列
                - 'id' -> str: 报警组编码
                - 'alarm_desc'-> str: 报警描述
    '''

    # 输入类型检查
    assert (type(time_diff) is float) or (type(time_diff) is int), "形参time_diff要求是float或int类型"
    assert type(different_levels) is bool, "形参different_levels要求是bool类型"

    if different_levels:
        # 按sub_unit和alarm_level对统计窗口内的报警结果进行分组
        df_groups = df_alarm.groupby(['sub_unit', 'alarm_level']).apply(_gen_groups, time_diff, ).reset_index(drop=True)
        # 按sub_unit和alarm_level生成报警组数据，包含报警信息及起止时间
        df_alarm_merge_new = df_groups.groupby(['sub_unit', 'alarm_level', 'groups']).apply(_gen_start_end_time,
                                                                                            different_levels, ).reset_index(
            drop=True)
    else:
        # 仅按sub_unit对统计窗口内的报警结果进行分组
        df_groups = df_alarm.groupby(['sub_unit']).apply(_gen_groups, time_diff, ).reset_index(drop=True)
        # 仅按sub_unit生成报警组数据，包含报警信息及起止时间
        df_alarm_merge_new = df_groups.groupby(['sub_unit', 'groups']).apply(_gen_start_end_time,
                                                                             different_levels, ).reset_index(drop=True)

    # 若存在历史报警组信息，新生成的报警组若与对应的最近一条历史报警组信息的间隔时间小于等于time_diff，则合并为一个报警组
    if df_alarm_merge_historical.shape[0] != 0:

        # 取各历史报警组最近一组报警信息并与各新生成的报警组信息进行匹配
        if different_levels:
            df_old = df_alarm_merge_historical.groupby(['sub_unit', 'alarm_level']).apply(
                lambda x: x.sort_values('end_time').iloc[-1]).reset_index(drop=True)
            df_alarm_merge_new = pd.merge(df_alarm_merge_new, df_old, on=['sub_unit', 'alarm_type', 'alarm_level'],
                                          suffixes=('_new', '_old'), how='left')
        else:
            df_old = df_alarm_merge_historical.groupby(['sub_unit']).apply(
                lambda x: x.sort_values('end_time').iloc[-1]).reset_index(drop=True)
            df_alarm_merge_new = pd.merge(df_alarm_merge_new, df_old, on=['sub_unit', 'alarm_type'],
                                          suffixes=('_new', '_old'), how='left')

        # 筛选出新生成报警组中与历史最近一组报警组间隔时间小于等于time_diff的报警组
        df_alarm_merge_new1 = df_alarm_merge_new[(df_alarm_merge_new['start_time_new'] - df_alarm_merge_new[
            'end_time_old']).dt.total_seconds() / 60 <= time_diff]
        # 筛选出新生成报警组中其余的报警组
        df_alarm_merge_new2 = df_alarm_merge_new[~((df_alarm_merge_new['start_time_new'] - df_alarm_merge_new[
            'end_time_old']).dt.total_seconds() / 60 <= time_diff)]

        # 对历史和新生成报警组中间隔时间小于等于time_diff的报警组进行合并
        df_alarm_merge_new1 = df_alarm_merge_new1.rename(
            columns={'start_time_old': 'start_time', 'end_time_new': 'end_time'})
        df_alarm_merge_new1['count'] = df_alarm_merge_new1['count_new'] + df_alarm_merge_new1['count_old']
        df_alarm_merge_new1['sort'] = df_alarm_merge_new1['sort_old']
        if not different_levels:
            df_alarm_merge_new1['alarm_level'] = df_alarm_merge_new1[['alarm_level_new', 'alarm_level_old']].max(axis=1)
        df_alarm_merge_new1 = df_alarm_merge_new1[
            ['sub_unit', 'alarm_type', 'alarm_level', 'start_time', 'end_time', 'count', 'sort']]

        # 对新生成报警组中不能与历史报警组合并的报警组进行排序（sort）修正
        df_alarm_merge_new2 = df_alarm_merge_new2.rename(
            columns={'start_time_new': 'start_time', 'end_time_new': 'end_time', 'count_new': 'count'})
        if not different_levels:
            df_alarm_merge_new2 = df_alarm_merge_new2.rename(columns={'alarm_level_new': 'alarm_level'})
        df_alarm_merge_new2['uni'] = df_alarm_merge_new2['sub_unit'] + df_alarm_merge_new2['alarm_level'].astype('str')
        flag = df_alarm_merge_new2['uni'].isin(
            df_alarm_merge_new1['sub_unit'] + df_alarm_merge_new1['alarm_level'].astype('str'))
        # 与df_alarm_merge_new1中相同报警的报警组，因该报警的报警组存在与历史报警组合并，所以排序数减一
        df_alarm_merge_new2.loc[flag, 'sort_new'] = df_alarm_merge_new2.loc[flag, 'sort_new'] - 1
        # 不存在历史报警组的，历史排序值填充为0
        df_alarm_merge_new2['sort_old'] = df_alarm_merge_new2['sort_old'].fillna(0)
        # 报警组的排序值为新生成的排序值加上历史最近一组报警组的排序值
        df_alarm_merge_new2['sort'] = df_alarm_merge_new2['sort_new'] + df_alarm_merge_new2['sort_old']
        df_alarm_merge_new2 = df_alarm_merge_new2[
            ['sub_unit', 'alarm_type', 'alarm_level', 'start_time', 'end_time', 'count', 'sort']]

        res = pd.concat([df_alarm_merge_new1, df_alarm_merge_new2])

    # 若不存在历史报警组信息，则无需合并，直接输出新生成的报警组
    else:
        res = df_alarm_merge_new

    res[['count', 'sort']] = res[['count', 'sort']].astype('int')
    res['alarm_group_id'] = res['sub_unit'] + '-' + res['end_time'].dt.year.astype('str') + '-' + res['sort'].astype(
        'str') + \
                            '-' + '(' + res['start_time'].astype('str') + '—' + res['end_time'].astype('str') + ')'
    res = pd.merge(res, df_alarm[['sub_unit', 'alarm_level', 'alarm_desc', 'level_cn']].drop_duplicates(),
                   on=['sub_unit', 'alarm_level'], how='left')
    return res