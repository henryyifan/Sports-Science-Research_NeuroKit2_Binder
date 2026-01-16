def generate_research_package(file_path):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import neurokit2 as nk
    if not hasattr(np, 'trapz'):
        np.trapz = np.trapezoid

    # 1. 读取数据
    try:
        df = pd.read_csv(file_path)

        # 提取 'duration' 这一列
        if 'duration' in df.columns:
            raw_data = df['duration'].values
        else:
        # 万一有的文件没表头，取第一列
            raw_data = df.iloc[:, 0].values

        print(f"原始数据读取成功，共 {len(raw_data)} 个点。")
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        return
    
    # 数据加载与清洗
    try:
    # 确保它是 float 类型
        rr_intervals = raw_data.astype(float)

    # 使用 neurokit2 清洗数据
    # sep_method="strong" 对运动中的伪影处理效果很好
        processed_data = nk.intervals_process(rr_intervals, sep_method="strong")
        # 提取处理后的数组
        rr_clean = processed_data[0] if isinstance(processed_result, tuple) else processed_data
        if hasattr(rr_clean, 'iloc'):
            rr_clean = rr_clean.iloc[:, 0].values
    except Exception as e:
        print(f"⚠清洗失败: {e}，回退至原始数据。")
        rr_clean = rr_intervals

    # 再次检查清洗后的数据，防止空的 NumPy 数组
    rr_clean = np.atleast_1d(rr_clean).astype(float)
    n = len(rr_clean)

    if rr_clean.size == 0:
        print("错误：清洗后没有有效数字（全是 NaN 或为空）！")
        return
        
    # 生成图表:raw data
    plt.figure(figsize=(12, 4))
    plt.plot(rr_clean, color='#3498DB', alpha=0.6, label='Processed RR Intervals')
    plt.title(f"Complete Session RR Interval Profile (Total Beats: {n})")
    plt.ylabel("RR Interval (ms)")
    plt.xlabel("Beat Index")
    plt.grid(True, alpha=0.3)
    plt.savefig('Raw_RR_Profile.png')
    plt.close()
    print("- 已生成 Raw_RR_Profile.png")

    # 分段计算逻辑 (每 100 个心跳为一组)
    window_size = 100
    step = 20
    report_list = []

    # 定义安全提取工具
    def get_val(df, col, dec=3):
        if df is not None and col in df.columns:
            v = df[col].values[0]
            return round(v, dec) if pd.notnull(v) else 0
        return 0
    print(f"正在计算高级指标 (窗口 {window_size})...")

    for i in range(0, n - window_size, step):
        seg = rr_clean[i : i + window_size]

        # 一次性获取时域、频域和非线性指标
        # 采样率设为 1000（Polar H10 默认 1ms 精度）
        try:
            # 核心：将 RR 转换为 Peaks 索引
            peaks = nk.intervals_to_peaks(seg)

            # 拆分计算以确保最大化获取指标
            h_time = nk.hrv_time(peaks, sampling_rate=1000)
            h_freq = nk.hrv_frequency(peaks, sampling_rate=1000)
            h_non  = nk.hrv_nonlinear(peaks, sampling_rate=1000)
            hrv_all = pd.concat([h_time, h_freq, h_non], axis=1)

            # 手动计算基础指标
            rmssd = np.sqrt(np.mean(np.diff(seg)**2))
            avg_hr = 60000 / np.mean(seg)
            sdnn = np.std(seg)

            report_list.append({
                'Segment': f"{i}-{i+window_size}",
                'Avg_HR_BPM': round(avg_hr, 1),
                # 恢复与变异性（时域）
                'RMSSD_ms': round(rmssd, 2),
                'SDNN_ms': round(sdnn, 2),
                'pNN50_pct': get_val(hrv_all, 'HRV_pNN50', 2),
                # 压力与平衡（频域与非线性）
                'LFHF_Ratio': get_val(hrv_all, 'HRV_LFHF', 2),
                'CSI_Stress': get_val(hrv_all, 'HRV_CSI', 2),
                'SNS_Index': get_val(hrv_all, 'HRV_SNS', 2),
                # 中枢神经状态
                'SD2_ms': get_val(hrv_all, 'HRV_SD2', 2),
                'SampEn': get_val(hrv_all, 'HRV_SampEn', 3)
            })
        except Exception:
            continue # 跳过无法计算的小段

    if not report_list:
        print("❌ 错误：数据量不足以生成分析报告。")
        return

    report_df = pd.DataFrame(report_list)
    
    # 生成图表: 多维度图表
    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # --- 上方子图：应激与心率 ---
    ax_top.set_title('Autonomic Nervous System: Stress & Intensity', fontsize=12)
    ax_top.plot(report_df.index, report_df['Avg_HR_BPM'], color='tab:blue', linewidth=2, label='Heart Rate (BPM)')
    ax_top.set_ylabel('Heart Rate (BPM)', color='tab:blue')
    
    ax_stress = ax_top.twinx()
    ax_stress.plot(report_df.index, report_df['CSI_Stress'], color='tab:orange', linestyle='--', label='CSI (Stress)')
    ax_stress.set_ylabel('CSI (Cardiac Sympathetic Index)', color='tab:orange')
    
    # --- 下方子图：恢复与中枢疲劳 ---
    ax_bot.set_title('Recovery & CNS Fatigue Status', fontsize=12)
    ax_bot.plot(report_df.index, report_df['RMSSD_ms'], color='tab:red', linewidth=2, label='RMSSD (Recovery)')
    ax_bot.set_ylabel('RMSSD (ms)', color='tab:red')
    
    ax_cns = ax_bot.twinx()
    ax_cns.plot(report_df.index, report_df['SD2_ms'], color='tab:green', marker='.', alpha=0.5, label='SD2 (CNS)')
    ax_cns.set_ylabel('SD2 (ms) - Long-term Var', color='tab:green')
    
    # 细节美化
    ax_bot.set_xlabel('Training Progression (Segments of 100 beats)')
    ax_top.grid(True, alpha=0.3)
    ax_bot.grid(True, alpha=0.3)
    fig.tight_layout()
    
    plt.savefig('Comprehensive_Body_Insight.png')
    plt.close()
    print("- 趋势图已生成")

    # 生成报告表CSV 汇总表
    report_df.to_csv('Training_Statistical_Report.csv', index=False)
    print("- 已生成 Training_Statistical_Report.csv")

    # 读取刚生成的报告
    df = pd.read_csv('Training_Statistical_Report.csv')

    # 创建双 Y 轴图表
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # 绘制 RMSSD (恢复指标) - 使用填充区域显示疲劳感
    ax1.set_xlabel('Timeline (Training Progress)', fontsize=12)
    ax1.set_ylabel('Recovery: RMSSD (ms)', color='tab:blue', fontsize=12)
    ax1.plot(df.index, df['RMSSD_ms'], color='tab:blue', linewidth=2, label='RMSSD (Recovery)')
    ax1.fill_between(df.index, df['RMSSD_ms'], alpha=0.2, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # 实例化第二个坐标轴
    ax2 = ax1.twinx()
    ax2.set_ylabel('Stress: CSI Index', color='tab:red', fontsize=12)
    ax2.plot(df.index, df['CSI_Stress'], color='tab:red', linewidth=2, linestyle='--', label='CSI (Stress)')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # 标注高强度训练区间
    peak_stress_idx = df['CSI_Stress'].idxmax()
    ax2.annotate('Max Effort (220kg Squat?)',
                xy=(peak_stress_idx, df['CSI_Stress'].max()),
                xytext=(peak_stress_idx+10, df['CSI_Stress'].max()+2),
                arrowprops=dict(facecolor='black', shrink=0.05))

    plt.title('Training Load Analysis: Stress vs. Recovery Balance', fontsize=15)
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()

    # 保存图片
    plt.savefig('Stress_Recovery_Comparison.png', dpi=300)
    plt.close()
    print("对比图已生成：Stress_Recovery_Comparison.png")
    
    print("\n" + "="*30)
    print("1. Raw_RR_Profile.png (原始数据)")
    print("2. Comprehensive_Body_Insight.png (多维度图表)")
    print("3. Training_Statistical_Report.csv (详细数值)")
    print("4. Stress_Recovery_Comparison.png")
    print("="*30)

# 运行脚本
import glob
import os
import time

if __name__ == "__main__":
    # 查找指定目录下所有以 RR 结尾的文件
    data_dir = "/home/van/Documents/Sports Data/Data/"

    # 获取该目录下所有的文件
    if not os.path.exists(data_dir):
        print(f"错误：找不到目录 {data_dir}")
    else:
        all_files = os.listdir(data_dir)

        # 筛选包含 _RR 且后缀是 csv (忽略大小写) 的文件
        list_of_files = [
            os.path.join(data_dir, f) for f in all_files
            if "_RR" in f and f.lower().endswith(".csv")
        ]
    
        if not list_of_files:
            print("错误：未找到符合格式的原始数据文件！")
            print("请确保 Polar 导出的文件在当前目录或 data 目录下。")
        else:
            # 按文件修改时间排序，自动选择最新生成的那个
            latest_file = max(list_of_files, key=os.path.getmtime)
        
            print(f"自动识别到最新训练数据: {latest_file}")
            print(f"文件生成时间: {time.ctime(os.path.getmtime(latest_file))}")
        
            generate_research_package(latest_file)
