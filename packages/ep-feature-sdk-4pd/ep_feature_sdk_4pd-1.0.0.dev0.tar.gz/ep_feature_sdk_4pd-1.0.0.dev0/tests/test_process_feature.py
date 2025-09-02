import random
from datetime import datetime, timedelta

import pandas as pd

from ep_feature_sdk_4pd.db_handler import DBHandler


def generate_simulated_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    生成模拟数据，包含 96 个点（每 15 分钟一个点）。
    输入：起始日期、结束日期（格式为 'YYYY-MM-DD'）
    输出：包含 backup_load 和 timestamp 的 DataFrame
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    df_wide_data = []
    for date in [start_dt + timedelta(days=i) for i in range((end_dt - start_dt).days + 1)]:
        for hour in range(24):  # 24 小时
            for minute in [0, 15, 30, 45]:  # 每 15 分钟一个点
                timestamp = date.replace(hour=hour, minute=minute, second=0)
                backup_load = random.uniform(100, 500)  # 随机生成备份负载值
                df_wide_data.append({
                    'timestamp': timestamp,
                    'backup_load': backup_load
                })

    return pd.DataFrame(df_wide_data)


def process_feature(start_date='2024-01-01', end_date='2025-06-30'):
    """
    输入起始和终止时间
    返回一个字典:
    {
        "back_ratio1": {
            "2024-01-01 00:15:00": "a",
            "2024-01-02 00:30:00": "b"
        }
    }
    """
    # 第一步：获取相关底表数据
    results = DBHandler.query("SELECT * FROM history_dd_dayahead_posinegarequirement LIMIT 10")
    print(f"查询结果: {results}")

    # 获取真实数据
    df_wide = DBHandler.query_to_dataframe("SELECT * FROM history_dd_dayahead_posinegarequirement")

    # 使用模拟数据
    # if df_wide.empty:
    #     df_wide = generate_simulated_data(start_date, end_date)
    df_wide = generate_simulated_data(start_date, end_date)

    # 数据预处理
    df_wide['back_ratio'] = df_wide['backup_load'] / 100
    df_wide['timestamp'] = pd.to_datetime(df_wide['timestamp'])

    # 第二步：特征处理
    result_dict = {}
    for _, row in df_wide.iterrows():
        timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:00')
        back_ratio = round(row['back_ratio'], 4)
        result_dict[timestamp_str] = back_ratio

    return {
        "back_ratio1": result_dict,
        "back_ratio2": result_dict  # 假设两个特征相同，实际可自定义
    }


if __name__ == '__main__':
    result = process_feature('2024-01-01', '2024-01-03')
    print(result)
