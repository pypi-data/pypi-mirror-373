import pandas as pd

def b_strip(df: pd.DataFrame):
    """
    去除dataframe中的空格
    :param df:
    :return:
    """
    # 处理columns
    df.columns = pd.Series(df.columns).map(lambda x: x.strip() if isinstance(x, str) else x)
    # 处理index
    df.index = df.index.map(lambda x: x.strip() if isinstance(x, str) else x)
    # 处理values
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    return df

def b_df2dict(df:pd.DataFrame, key:str, value:str):
    """
    dataframe转字典
    :param df:
    :param key:
    :param value:
    :return:
    """
    my_dict = df.set_index(key)[value].to_dict()
    return my_dict

