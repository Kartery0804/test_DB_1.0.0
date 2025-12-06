import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mtick
import numpy as np
from datetime import datetime, timedelta
import calendar
from matplotlib import rcParams
from app.services import config_mysql as cf

# 设置中文字体（如果需要显示中文）
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def plot_monthly_attendance_rate_with_table(conn:pymysql.Connection,month=None, year=None, output_path='attendance_table.png',**kwargs):
    """
    包含数据表格的小窗口版本，添加迟到/早退分钟累计时间，图例放在柱状图外面
    表格中的"总数"列放在最后一列
    """
    
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    try:
        conn = pymysql.connect(
            **cf.default_dict1
        )
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        # 修改查询语句，添加迟到和早退分钟数的累计
        query = f"""
        SELECT 
            date,
            WEEK(date, 1) as week_number,
            CASE 
                WHEN absent = 1 THEN 'absent'
                WHEN late_minutes > 0 THEN 'late'
                WHEN early_leave_minutes > 0 THEN 'early_leave'
                WHEN checkin_time IS NOT NULL AND checkout_time IS NOT NULL THEN 'present'
                ELSE 'no_record'
            END as attendance_status,
            SUM(late_minutes) as total_late_minutes,
            SUM(early_leave_minutes) as total_early_leave_minutes
        FROM attendance_record
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY date, attendance_status, week_number
        ORDER BY date
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            print(f"没有找到{year}年{month}月的数据")
            return False
        
        # 创建紧凑布局：图表在上，表格在下
        fig = plt.figure(figsize=(12, 6))
        matplotlib.use('Agg')
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1.5], hspace=0.4)
        
        ax1 = fig.add_subplot(gs[0])  # 图表区域
        ax2 = fig.add_subplot(gs[1])  # 表格区域
        
        # 处理数据
        weeks = sorted(df['week_number'].unique())
        week_labels = []
        attendance_data = {
            'present': [], 'late': [], 'early_leave': [], 'absent': [], 'no_record': []
        }
        
        weekly_stats = []  # 用于存储每周统计，包括分钟数
        
        for week in weeks:
            week_df = df[df['week_number'] == week]
            total_records = len(week_df)
            
            if total_records == 0:
                continue
            
            # 计算迟到和早退总分钟数
            total_late_minutes = week_df['total_late_minutes'].sum()
            total_early_leave_minutes = week_df['total_early_leave_minutes'].sum()
            
            # 将分钟数转换为"X小时Y分钟"格式
            def format_minutes(minutes):
                if pd.isna(minutes) or minutes == 0:
                    return "0分钟"
                hours = int(minutes // 60)
                mins = int(minutes % 60)
                if hours > 0:
                    return f"{hours}小时{mins}分钟"
                else:
                    return f"{mins}分钟"
            
            status_counts = week_df['attendance_status'].value_counts()
            week_labels.append(f"第{week}周")
            
            week_stat = {
                'week': week, 
                'total': total_records,
                'late_minutes': format_minutes(total_late_minutes),
                'early_leave_minutes': format_minutes(total_early_leave_minutes)
            }
            
            for status in attendance_data.keys():
                count = status_counts.get(status, 0)
                percentage = (count / total_records) * 100 if total_records > 0 else 0
                attendance_data[status].append(percentage)
                week_stat[status] = f"{percentage:.1f}%"
            
            weekly_stats.append(week_stat)
        
        # 绘制图表
        colors = ['#4CAF50', '#FF9800', '#FFC107', '#2196F3', '#F44336']
        labels = ['正常', '迟到', '早退', '无记录', '缺席']
        
        bottom = np.zeros(len(week_labels))
        for i, status in enumerate(['present', 'late', 'early_leave', 'no_record', 'absent']):
            ax1.bar(week_labels, attendance_data[status], 
                   bottom=bottom, color=colors[i], label=labels[i],
                   edgecolor='white', linewidth=0.8, alpha=0.9)
            bottom += np.array(attendance_data[status])
        
        # 图表美化
        month_name = f"{year}年{month}月"
        ax1.set_title(f'{month_name} 每周出勤率统计', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('百分比', fontsize=11)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.tick_params(axis='x', labelsize=10)
        ax1.tick_params(axis='y', labelsize=9)
        ax1.set_ylim(0, 105)
        
        # 添加网格线
        ax1.grid(True, axis='y', alpha=0.2, linestyle='--')
        ax1.set_axisbelow(True)
        
        # 将图例放在柱状图外面（右侧）
        ax1.legend(fontsize=9, loc='upper left', bbox_to_anchor=(1.02, 1), 
                  title='出勤状态', title_fontsize=10, frameon=True, 
                  framealpha=0.9, edgecolor='#DDD')
        
        # 在柱状图上添加数值标签
        for i, week in enumerate(week_labels):
            total_height = 0
            for j, status in enumerate(['present', 'late', 'early_leave', 'no_record', 'absent']):
                value = attendance_data[status][i]
                if value > 5:  # 只显示大于5%的值，避免重叠
                    # 根据背景颜色决定文字颜色
                    if status in ['present', 'absent']:
                        text_color = 'white'
                    else:
                        text_color = 'black'
                    
                    ax1.text(i, total_height + value/2, 
                           f'{value:.0f}%', ha='center', va='center',
                           fontsize=8, color=text_color, fontweight='bold')
                    
                total_height += value
        
        # 添加数据表格
        ax2.axis('off')
        
        # 准备表格数据（包含迟到/早退分钟数，总数放在最后一列）
        table_data = []
        headers = ['周次', '正常', '迟到', '早退', '无记录', '缺席', '迟到累计', '早退累计', '总数']
        
        for stat in weekly_stats:
            row = [
                f"第{stat['week']}周",
                stat['present'],
                stat['late'],
                stat['early_leave'],
                stat['no_record'],
                stat['absent'],
                stat['late_minutes'],
                stat['early_leave_minutes'],
                str(stat['total'])
            ]
            table_data.append(row)
        
        # 创建表格
        table = ax2.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='center',
                         colColours=['#f8f9fa']*len(headers))
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.3)  # 调整表格行高
        
        # 设置表格单元格颜色和样式（调整列索引）
        for i in range(len(table_data) + 1):
            for j in range(len(headers)):
                cell = table[(i, j)]
                if i == 0:  # 表头
                    cell.set_facecolor('#2C3E50')
                    cell.set_text_props(color='white', fontweight='bold', fontsize=9)
                elif j == 5:  # 缺席列（现在是第6列，索引5）
                    cell.set_facecolor('#FFEBEE')
                    cell.set_text_props(fontweight='bold')
                elif j == 1:  # 正常列（现在是第2列，索引1）
                    cell.set_facecolor('#E8F5E9')
                elif j == 2:  # 迟到列（现在是第3列，索引2）
                    cell.set_facecolor('#FFF3E0')
                elif j == 3:  # 早退列（现在是第4列，索引3）
                    cell.set_facecolor('#FFF8E1')
                elif j == 6:  # 迟到累计列（现在是第7列，索引6）
                    cell.set_facecolor('#FFF3E0')
                    cell.set_text_props(fontweight='bold')
                elif j == 7:  # 早退累计列（现在是第8列，索引7）
                    cell.set_facecolor('#FFF8E1')
                    cell.set_text_props(fontweight='bold')
                elif j == 8:  # 总数列（现在是最后一列，索引8）
                    cell.set_facecolor('#E3F2FD')
                    cell.set_text_props(fontweight='bold')
        
        # 在表格上方添加标题
        ax2.text(0.5, 1.02, '详细统计数据', transform=ax2.transAxes, 
                ha='center', fontsize=11, fontweight='bold')
        
        # 调整整体布局，为图例留出空间
        plt.tight_layout(rect=[0, 0, 0.85, 0.95])
        
        # 保存图表
        plt.savefig(cf.res_path+output_path, dpi=300, bbox_inches='tight')
        print(f"带表格图表已保存到: {cf.res_path+output_path}")
        
        # 显示图表
        #plt.show()
        
        # 打印汇总信息
        print(f"\n{year}年{month}月出勤统计汇总:")
        print("=" * 60)
        
        # 计算整体迟到/早退分钟数
        total_all_late_minutes = df['total_late_minutes'].sum()
        total_all_early_leave_minutes = df['total_early_leave_minutes'].sum()
        
        # 格式化整体分钟数
        def format_total_minutes(minutes):
            if pd.isna(minutes) or minutes == 0:
                return "0分钟"
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            if hours > 0:
                return f"{hours}小时{mins}分钟"
            else:
                return f"{mins}分钟"
        
        # 计算整体出勤率
        total_records = len(df)
        if total_records > 0:
            overall_present = (df['attendance_status'] == 'present').sum() / total_records * 100
            overall_absent = (df['attendance_status'] == 'absent').sum() / total_records * 100
            
            print(f"整体出勤率: {overall_present:.1f}%")
            print(f"整体缺勤率: {overall_absent:.1f}%")
            print(f"总迟到时间: {format_total_minutes(total_all_late_minutes)}")
            print(f"总早退时间: {format_total_minutes(total_all_early_leave_minutes)}")
            print(f"总记录数: {total_records}")
            print("=" * 60)
            
            # 打印每周详细统计
            for stat in weekly_stats:
                print(f"\n第{stat['week']}周:")
                print(f"  正常出勤: {stat['present']}")
                print(f"  迟到: {stat['late']} (累计: {stat['late_minutes']})")
                print(f"  早退: {stat['early_leave']} (累计: {stat['early_leave_minutes']})")
                print(f"  缺席: {stat['absent']}")
                print(f"  无记录: {stat['no_record']}")
                print(f"  总记录数: {stat['total']}")
        return True
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False


# 增强版：更详细的统计信息，总数在最后一列
def plot_monthly_attendance_rate_enhanced(host, user, password, database, 
                                          month=None, year=None, 
                                          output_path='attendance_enhanced.png'):
    """
    增强版：包含更多统计信息的出勤率图表，表格中的"总数"列放在最后一列
    """
    
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        # 更详细的查询，包含更多统计信息
        query = f"""
        SELECT 
            WEEK(date, 1) as week_number,
            COUNT(*) as total_records,
            SUM(CASE WHEN absent = 1 THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN late_minutes > 0 THEN 1 ELSE 0 END) as late_count,
            SUM(CASE WHEN early_leave_minutes > 0 THEN 1 ELSE 0 END) as early_leave_count,
            SUM(CASE WHEN checkin_time IS NOT NULL AND checkout_time IS NOT NULL AND 
                absent = 0 AND late_minutes = 0 AND early_leave_minutes = 0 THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN checkin_time IS NULL OR checkout_time IS NULL THEN 1 ELSE 0 END) as no_record_count,
            SUM(late_minutes) as total_late_minutes,
            SUM(early_leave_minutes) as total_early_leave_minutes
        FROM attendance_record
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY week_number
        ORDER BY week_number
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty or len(df) == 0:
            print(f"没有找到{year}年{month}月的数据")
            return 
        
        # 创建图表布局
        fig = plt.figure(figsize=(11, 9))
        gs = fig.add_gridspec(2, 1, height_ratios=[2.5, 1.5], hspace=0.35)
        
        ax1 = fig.add_subplot(gs[0])  # 图表区域
        ax2 = fig.add_subplot(gs[1])  # 表格区域
        
        # 准备数据
        week_labels = [f"第{week}周" for week in df['week_number']]
        
        # 计算百分比
        total_records = df['total_records'].values
        present_pct = (df['present_count'] / total_records * 100).values
        late_pct = (df['late_count'] / total_records * 100).values
        early_leave_pct = (df['early_leave_count'] / total_records * 100).values
        absent_pct = (df['absent_count'] / total_records * 100).values
        no_record_pct = (df['no_record_count'] / total_records * 100).values
        
        # 绘制堆叠柱状图
        colors = ['#4CAF50', '#FF9800', '#FFC107', '#2196F3', '#F44336']
        labels = ['正常出勤', '迟到', '早退', '无记录', '缺席']
        
        bottom = np.zeros(len(week_labels))
        data_arrays = [present_pct, late_pct, early_leave_pct, no_record_pct, absent_pct]
        
        for i in range(5):
            ax1.bar(week_labels, data_arrays[i], 
                   bottom=bottom, color=colors[i], label=labels[i],
                   edgecolor='white', linewidth=1, alpha=0.9)
            bottom += data_arrays[i]
        
        # 图表美化
        month_name = f"{year}年{month}月"
        ax1.set_title(f'{month_name} 每周出勤率统计（增强版）', 
                     fontsize=15, fontweight='bold', pad=20, color='#2C3E50')
        ax1.set_ylabel('出勤率 (%)', fontsize=12, fontweight='bold')
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.tick_params(axis='x', labelsize=11, rotation=0)
        ax1.tick_params(axis='y', labelsize=10)
        ax1.set_ylim(0, 105)
        
        # 添加网格线
        ax1.grid(True, axis='y', alpha=0.2, linestyle='--', color='#BDC3C7')
        ax1.set_axisbelow(True)
        
        # 将图例放在柱状图外面（右侧）
        ax1.legend(fontsize=10, loc='upper left', bbox_to_anchor=(1.02, 1), 
                  title='出勤状态', title_fontsize=11, frameon=True, 
                  framealpha=0.95, edgecolor='#BDC3C7', facecolor='#F8F9FA')
        
        # 添加数值标签
        for i, week in enumerate(week_labels):
            total_height = 0
            for j, data in enumerate(data_arrays):
                value = data[i]
                if value > 4:  # 只显示大于4%的值
                    text_color = 'white' if j in [0, 4] else 'black'  # 正常和缺席用白色文字
                    ax1.text(i, total_height + value/2, 
                           f'{value:.0f}%', ha='center', va='center',
                           fontsize=9, color=text_color, fontweight='bold')
                total_height += value
        
        # 添加数据表格
        ax2.axis('off')
        
        # 准备表格数据（总数放在最后一列）
        table_data = []
        headers = ['周次', '正常', '迟到', '早退', '无记录', '缺席', '迟到分钟', '早退分钟', '总数']
        
        for idx, row in df.iterrows():
            # 格式化分钟数
            def format_minutes_simple(minutes):
                if pd.isna(minutes) or minutes == 0:
                    return "0"
                return f"{int(minutes)}"
            
            table_row = [
                f"第{row['week_number']}周",
                f"{present_pct[idx]:.1f}%",
                f"{late_pct[idx]:.1f}%",
                f"{early_leave_pct[idx]:.1f}%",
                f"{no_record_pct[idx]:.1f}%",
                f"{absent_pct[idx]:.1f}%",
                format_minutes_simple(row['total_late_minutes']),
                format_minutes_simple(row['total_early_leave_minutes']),
                str(int(row['total_records']))
            ]
            table_data.append(table_row)
        
        # 创建表格
        table = ax2.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='center',
                         colColours=['#F8F9FA']*len(headers))
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.4)
        
        # 设置表格样式（调整列索引）
        for i in range(len(table_data) + 1):
            for j in range(len(headers)):
                cell = table[(i, j)]
                if i == 0:  # 表头
                    cell.set_facecolor('#2C3E50')
                    cell.set_text_props(color='white', fontweight='bold')
                elif j == 1:  # 正常列（索引1）
                    cell.set_facecolor('#E8F5E9')
                elif j == 2:  # 迟到列（索引2）
                    cell.set_facecolor('#FFF3E0')
                elif j == 3:  # 早退列（索引3）
                    cell.set_facecolor('#FFF8E1')
                elif j == 5:  # 缺席列（索引5）
                    cell.set_facecolor('#FFEBEE')
                    cell.set_text_props(fontweight='bold')
                elif j == 6:  # 迟到分钟列（索引6）
                    cell.set_facecolor('#FFF3E0')
                    cell.set_text_props(fontweight='bold')
                elif j == 7:  # 早退分钟列（索引7）
                    cell.set_facecolor('#FFF8E1')
                    cell.set_text_props(fontweight='bold')
                elif j == 8:  # 总数列（最后一列，索引8）
                    cell.set_facecolor('#E3F2FD')
                    cell.set_text_props(fontweight='bold')
        
        # 表格标题
        ax2.text(0.5, 1.02, '详细统计（含累计分钟数）', transform=ax2.transAxes, 
                ha='center', fontsize=12, fontweight='bold', color='#2C3E50')
        
        # 调整布局
        plt.tight_layout(rect=[0, 0, 0.82, 0.95])
        
        # 保存图表
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"增强版图表已保存到: {output_path}")
        
        # 显示图表
        plt.show()
        
        # 打印整体统计
        print(f"\n{year}年{month}月整体统计:")
        print("=" * 60)
        total_records_all = df['total_records'].sum()
        total_late_minutes_all = df['total_late_minutes'].sum()
        total_early_leave_minutes_all = df['total_early_leave_minutes'].sum()
        
        if total_records_all > 0:
            overall_present = df['present_count'].sum() / total_records_all * 100
            print(f"总记录数: {int(total_records_all)}")
            print(f"整体出勤率: {overall_present:.1f}%")
            print(f"总迟到分钟数: {int(total_late_minutes_all)}分钟 ({total_late_minutes_all/60:.1f}小时)")
            print(f"总早退分钟数: {int(total_early_leave_minutes_all)}分钟 ({total_early_leave_minutes_all/60:.1f}小时)")
        
    except Exception as e:
        print(f"发生错误: {e}")
        if 'conn' in locals():
            conn.close()


# 简洁版：只有柱状图和简单表格，总数在最后一列
def plot_monthly_attendance_rate_simple_table(host, user, password, database, 
                                              month=None, year=None, 
                                              output_path='attendance_simple_table.png'):
    """
    简洁版：只有柱状图和简单表格，总数在最后一列
    """
    
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        # 简单查询
        query = f"""
        SELECT 
            WEEK(date, 1) as week_number,
            COUNT(*) as total_records,
            SUM(CASE WHEN absent = 1 THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN late_minutes > 0 THEN 1 ELSE 0 END) as late_count,
            SUM(CASE WHEN early_leave_minutes > 0 THEN 1 ELSE 0 END) as early_leave_count,
            SUM(late_minutes) as total_late_minutes,
            SUM(early_leave_minutes) as total_early_leave_minutes
        FROM attendance_record
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY week_number
        ORDER BY week_number
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty or len(df) == 0:
            print(f"没有找到{year}年{month}月的数据")
            return
        
        # 创建图表布局
        fig = plt.figure(figsize=(10, 7))
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.3)
        
        ax1 = fig.add_subplot(gs[0])  # 图表区域
        ax2 = fig.add_subplot(gs[1])  # 表格区域
        
        # 准备数据
        week_labels = [f"W{week}" for week in df['week_number']]
        
        # 计算百分比（简化为三类：正常、迟到/早退、缺席）
        total_records = df['total_records'].values
        normal_count = total_records - df['absent_count'].values - df['late_count'].values - df['early_leave_count'].values
        normal_pct = (normal_count / total_records * 100).values
        late_early_pct = ((df['late_count'] + df['early_leave_count']) / total_records * 100).values
        absent_pct = (df['absent_count'] / total_records * 100).values
        
        # 绘制堆叠柱状图（简化版）
        colors = ['#4CAF50', '#FF9800', '#F44336']
        labels = ['正常出勤', '迟到/早退', '缺席']
        
        bottom = np.zeros(len(week_labels))
        data_arrays = [normal_pct, late_early_pct, absent_pct]
        
        for i in range(3):
            ax1.bar(week_labels, data_arrays[i], 
                   bottom=bottom, color=colors[i], label=labels[i],
                   edgecolor='white', linewidth=0.8, alpha=0.9)
            bottom += data_arrays[i]
        
        # 图表美化
        month_name = f"{year}年{month}月"
        ax1.set_title(f'{month_name} 每周出勤率统计（简洁版）', fontsize=13, fontweight='bold', pad=15)
        ax1.set_ylabel('出勤率 (%)', fontsize=11)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.tick_params(axis='x', labelsize=10)
        ax1.tick_params(axis='y', labelsize=9)
        ax1.set_ylim(0, 105)
        ax1.legend(fontsize=9, loc='upper right')
        ax1.grid(True, axis='y', alpha=0.2, linestyle='--')
        
        # 添加数据表格（简洁版）
        ax2.axis('off')
        
        # 准备表格数据（总数在最后一列）
        table_data = []
        headers = ['周次', '正常', '迟到/早退', '缺席', '迟到分钟', '早退分钟', '总数']
        
        for idx, row in df.iterrows():
            normal_pct_val = normal_pct[idx]
            late_early_pct_val = late_early_pct[idx]
            absent_pct_val = absent_pct[idx]
            
            table_row = [
                f"第{row['week_number']}周",
                f"{normal_pct_val:.1f}%",
                f"{late_early_pct_val:.1f}%",
                f"{absent_pct_val:.1f}%",
                f"{int(row['total_late_minutes'])}",
                f"{int(row['total_early_leave_minutes'])}",
                str(int(row['total_records']))
            ]
            table_data.append(table_row)
        
        # 创建表格
        table = ax2.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='center',
                         colColours=['#f2f2f2']*len(headers))
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # 设置表格样式
        for i in range(len(table_data) + 1):
            for j in range(len(headers)):
                cell = table[(i, j)]
                if i == 0:  # 表头
                    cell.set_facecolor('#2C3E50')
                    cell.set_text_props(color='white', fontweight='bold')
                elif j == 1:  # 正常列
                    cell.set_facecolor('#E8F5E9')
                elif j == 2:  # 迟到/早退列
                    cell.set_facecolor('#FFF3E0')
                elif j == 3:  # 缺席列
                    cell.set_facecolor('#FFEBEE')
                elif j == 6:  # 总数列（最后一列）
                    cell.set_facecolor('#E3F2FD')
                    cell.set_text_props(fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"简洁版图表已保存到: {output_path}")
        plt.show()
        
    except Exception as e:
        print(f"发生错误: {e}")
        if 'conn' in locals():
            conn.close()


# 使用示例
if __name__ == "__main__":
    # 配置数据库连接信息
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'aq'
    }
    
    # 使用示例1：带表格的版本（包含迟到/早退分钟数，总数在最后一列）
    plot_monthly_attendance_rate_with_table(**DB_CONFIG, month=12, year=2025,output_path='attendance_with_table.png')
    
    # 使用示例2：增强版（总数在最后一列）
    # plot_monthly_attendance_rate_enhanced(**DB_CONFIG, month=5, year=2024,
    #                                       output_path='attendance_enhanced.png')
    
    # 使用示例3：简洁版
    # plot_monthly_attendance_rate_simple_table(**DB_CONFIG, month=5, year=2024,
    #                                           output_path='attendance_simple.png')
    