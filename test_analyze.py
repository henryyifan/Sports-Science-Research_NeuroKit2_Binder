import neurokit2 as nk
import pandas as pd
import matplotlib.pyplot as plt

try:
    df = pd.read_csv('data/mydata.csv')
    rr_intervals = df['duration'].values
    
    # --- 关键：如果数据太多，只取前 2000 个点做分析 ---
    # 2000 个点足够分析出 RMSSD 和频域特征了
    if len(rr_intervals) > 2000:
        print("数据量较大，正在提取前 2000 个点进行轻量化分析...")
        rr_intervals = rr_intervals[:2000]

    peaks = nk.intervals_to_peaks(rr_intervals)
    
    print("正在进行轻量化分析（仅计算时域指标）...")
    # 使用 hrv_time 代替全量的 hrv，这会极大地节省内存和时间
    hrv_indices = nk.hrv_time(peaks, sampling_rate=1000, show=True)
    
    plt.savefig('HRV_Simple_Result.png')
    
    print(f"\nRMSSD: {hrv_indices['HRV_RMSSD'].values[0]:.2f} ms")
    print("分析成功！图片已保存。")

except Exception as e:
    print(f"运行失败: {e}")
