import neurokit2 as nk
import pandas as pd
import matplotlib.pyplot as plt

# 1. 读取数据
try:
    # 路径记得和你 Binder 左侧列表对齐，如果是根目录就去掉 'data/'
    df = pd.read_csv('mydata.csv') 
    rr_intervals = df['duration'].values
    print(f"数据加载成功！共计 {len(rr_intervals)} 个心跳间期。")
except Exception as e:
    print(f"读取失败，请检查文件名或格式: {e}")

# 2. 核心转换：将 RR 间期转换为峰值点 (解决 ValueError)
# NeuroKit2 需要知道每个 R 波发生的具体时间点
peaks = nk.intervals_to_peaks(rr_intervals)

# 3. 信号处理与绘图
print("正在生成 HRV 分析报告...")
# 传入转换后的 peaks 而不是原始 intervals
hrv_indices = nk.hrv(peaks, sampling_rate=1000, show=True)

# 强制保存图片，否则在终端运行你看不到弹窗
plt.savefig('HRV_Analysis_Result.png') 
print("图表已保存为: HRV_Analysis_Result.png")

# 4. 提取指标
rmssd = hrv_indices['HRV_RMSSD'].values[0]
sd1_sd2 = hrv_indices['HRV_SD1SD2'].values[0]

print(f"\n--- 核心分析结果 ---")
print(f"RMSSD (恢复指标): {rmssd:.2f} ms")
print(f"SD1/SD2 (神经平衡): {sd1_sd2:.2f}")
