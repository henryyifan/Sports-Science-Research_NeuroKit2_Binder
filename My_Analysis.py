import neurokit2 as nk
import pandas as pd
import matplotlib.pyplot as plt

# 1. 读取数据 (Polar CSV 通常只有一列 RR 间期)
# 注意：如果你下载的文件第一行有文字标题，skiprows=1 可能需要根据实际情况调整
try:
    # 尝试自动读取含有 'RR' 字样的列
    df = pd.read_csv('data/mydata.csv')
    # 如果 Polar 导出的格式有标题行，提取那一列数字
    # 这里的列名 'RR-interval (ms)' 是 Polar 的标准命名
    rr_intervals = df['RR-interval (ms)'].values
    print(f"数据加载成功！共计 {len(rr_intervals)} 个心跳间期。")
except Exception as e:
    print(f"读取失败，请检查文件名或格式: {e}")

# 2. 信号处理与绘图
# 这一个函数就能生成 Poincaré Plot, 频域分析和时域指标
print("正在生成 HRV 分析报告...")
hrv_indices = nk.hrv(rr_intervals, sampling_rate=1000, show=True)

# 3. 提取你最关心的两个 CNS 疲劳指标
rmssd = hrv_indices['HRV_RMSSD'].values[0]
sd1_sd2 = hrv_indices['HRV_SD1SD2'].values[0]

print(f"\n--- 核心分析结果 ---")
print(f"RMSSD (恢复指标): {rmssd:.2f} ms")
print(f"SD1/SD2 (神经平衡): {sd1_sd2:.2f}")
