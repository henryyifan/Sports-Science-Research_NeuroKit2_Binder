import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_research_package(file_path):
    print("开始执行科研级数据处理...")
    
    # 1. 数据加载与清洗
    df = pd.read_csv(file_path)
    raw_data = pd.to_numeric(df['duration'], errors='coerce').dropna().values
    
    # 物理过滤 (确保生理准确性)
    rr_clean = raw_data[(raw_data >= 300) & (raw_data <= 2000)]
    n = len(rr_clean)
    
    # 2. 生成图表 1: 原始 RR 间期全景图 (Proof of raw data)
    plt.figure(figsize=(12, 5))
    plt.plot(rr_clean, color='#3498DB', alpha=0.6)
    plt.title(f"Complete Session RR Interval Profile (Total Beats: {n})")
    plt.ylabel("RR Interval (ms)")
    plt.xlabel("Beat Index")
    plt.grid(True, alpha=0.3)
    plt.savefig('1_Raw_RR_Profile.png')
    plt.close()
    print("- 已生成 1_Raw_RR_Profile.png")

    # 3. 分段计算逻辑 (每 1000 个心跳为一组)
    step = 1000
    report_list = []
    
    for i in range(0, n, step):
        seg = rr_clean[i:i+step]
        if len(seg) < 100: continue
        
        # 计算核心指标
        rmssd = np.sqrt(np.mean(np.diff(seg)**2))
        avg_hr = 60000 / np.mean(seg)
        sdnn = np.std(seg)
        
        report_list.append({
            'Segment': f"Beats {i}-{i+len(seg)}",
            'RMSSD_ms': round(rmssd, 2),
            'Avg_HR_BPM': round(avg_hr, 1),
            'SDNN_ms': round(sdnn, 2)
        })

    report_df = pd.DataFrame(report_list)
    
    # 4. 生成图表 2: 心率与 HRV 关联趋势图 (Scientific Insight)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel('Training Progression (Segments)')
    ax1.set_ylabel('RMSSD (ms) - Vagal Tone', color='tab:red')
    ax1.plot(report_df.index, report_df['RMSSD_ms'], marker='o', color='tab:red', linewidth=2, label='RMSSD')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Heart Rate (BPM)', color='tab:blue')
    ax2.plot(report_df.index, report_df['Avg_HR_BPM'], marker='x', color='tab:blue', linestyle='--', label='HR')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    
    plt.title('Autonomic Nervous System Response during Heavy Strength Training')
    fig.tight_layout()
    plt.savefig('2_HRV_HR_Correlation.png')
    plt.close()
    print("- 已生成 2_HRV_HR_Correlation.png")

    # 5. 生成报告表 3: CSV 汇总表
    report_df.to_csv('3_Training_Statistical_Report.csv', index=False)
    print("- 已生成 3_Training_Statistical_Report.csv")
    
    print("\n" + "="*30)
    print("✅ 分析包准备就绪！请将以下文件发送给教授：")
    print("1. 1_Raw_RR_Profile.png (展示数据完整性)")
    print("2. 2_HRV_HR_Correlation.png (核心科学趋势)")
    print("3. 3_Training_Statistical_Report.csv (详细数值)")
    print("="*30)

# 运行脚本
generate_research_package('data/mydata.csv')
