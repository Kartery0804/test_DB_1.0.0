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
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches
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



def create_attendance_heatmap(year, month, host, user, password, database, output_path='attendance_heatmap.png'):
    """
    生成指定年月每周每天的出勤率热力图
    
    参数:
    year: 年份 (int)
    month: 月份 (int)
    host: 数据库主机
    user: 数据库用户名
    password: 数据库密码
    database: 数据库名
    output_path: 输出图片路径
    """
    
    # 连接数据库
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        print("数据库连接成功")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None
    
    try:
        # 计算该月的第一天和最后一天
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 构建查询SQL
        query = f"""
        SELECT 
            DATE(date) as attendance_date,
            DAYOFWEEK(date) as day_of_week,
            COUNT(*) as total_employees,
            SUM(CASE 
                WHEN absent = 0 AND (work_hours > 0 OR checkin_time IS NOT NULL) 
                THEN 1 
                ELSE 0 
            END) as present_employees,
            SUM(CASE WHEN absent = 1 THEN 1 ELSE 0 END) as absent_employees,
            SUM(CASE WHEN late_minutes > 0 THEN 1 ELSE 0 END) as late_employees
        FROM attendance_record
        WHERE date BETWEEN '{first_day.strftime('%Y-%m-%d')}' AND '{last_day.strftime('%Y-%m-%d')}'
        GROUP BY DATE(date), DAYOFWEEK(date)
        ORDER BY attendance_date
        """
        
        # 执行查询
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print(f"{year}年{month}月没有考勤数据")
            return None
        
        # 计算出勤率
        df['attendance_rate'] = (df['present_employees'] / df['total_employees'] * 100).round(2)
        
        # 创建热力图数据矩阵
        # 获取该月的天数
        num_days = calendar.monthrange(year, month)[1]
        
        # 创建一个5x7的矩阵（最多5周，每周7天）
        heatmap_data = np.full((6, 7), np.nan)  # 6行x7列，初始为NaN
        
        # 填充热力图数据
        for _, row in df.iterrows():
            date = row['attendance_date']
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            
            # 计算周数（从0开始）
            # 获取该日期是该月的第几天
            day_num = date.day
            
            # 计算该日期是星期几（0=周一, 6=周日）
            weekday = date.weekday()  # 0=Monday, 6=Sunday
            
            # 计算周数
            week_num = (day_num - 1 + date.weekday()) // 7
            
            # 将出勤率填入矩阵
            heatmap_data[week_num, weekday] = row['attendance_rate']
        
        # 创建热力图
        plt.figure(figsize=(12, 8))
        
        # 创建自定义颜色映射（从红色到绿色）
        colors = ['#ff4d4d', '#ff9999', '#ffcccc', '#e6f7ff', '#99e699', '#4dff4d']
        cmap = LinearSegmentedColormap.from_list('attendance_cmap', colors, N=100)
        
        # 绘制热力图
        im = plt.imshow(heatmap_data, cmap=cmap, aspect='auto', vmin=0, vmax=100)
        
        # 添加颜色条
        cbar = plt.colorbar(im, fraction=0.03, pad=0.04)
        cbar.set_label('出勤率 (%)', fontsize=12, fontproperties='SimHei')
        
        # 设置坐标轴
        plt.title(f'{year}年{month}月 每周出勤率热力图', 
                 fontsize=16, fontweight='bold', pad=20, fontproperties='SimHei')
        
        # 设置x轴（星期）
        weekdays_chinese = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        plt.xticks(range(7), weekdays_chinese, fontproperties='SimHei')
        
        # 设置y轴（周数）
        plt.yticks(range(6), [f'第{i+1}周' for i in range(6)], fontproperties='SimHei')
        
        # 在单元格中显示数值
        for i in range(heatmap_data.shape[0]):
            for j in range(heatmap_data.shape[1]):
                value = heatmap_data[i, j]
                if not np.isnan(value):
                    # 根据背景颜色调整文字颜色
                    cell_color = im.cmap(im.norm(value))
                    # 计算亮度
                    brightness = cell_color[0] * 0.299 + cell_color[1] * 0.587 + cell_color[2] * 0.114
                    text_color = 'black' if brightness > 0.5 else 'white'
                    
                    plt.text(j, i, f'{value:.1f}%', 
                            ha='center', va='center', 
                            color=text_color, fontsize=10, fontweight='bold',
                            fontproperties='SimHei')
        
        # 添加网格线
        plt.grid(which='major', color='gray', linestyle='-', linewidth=0.5)
        
        # 添加额外信息
        plt.figtext(0.5, 0.01, 
                   f'数据统计时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} | 数据来源: {database}',
                   ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"热力图已保存到: {output_path}")
        
        # 显示图片（可选）
        plt.show()
        
        plt.close()
        
        # 返回统计数据
        stats = {
            'month': f'{year}-{month:02d}',
            'total_days': len(df['attendance_date'].unique()),
            'avg_attendance_rate': df['attendance_rate'].mean(),
            'min_attendance_rate': df['attendance_rate'].min(),
            'max_attendance_rate': df['attendance_rate'].max()
        }
        
        return stats
        
    except Exception as e:
        print(f"生成热力图时出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        conn.close()

def create_attendance_heatmap_rounded(conn:pymysql.Connection,year, month, output_path='attendance_heatmap_rounded.png',**kwargs):
    """
    生成圆角矩形样式、有间距的热力图
    """
    
    try:
        conn = pymysql.connect(
            **cf.default_dict1
        )
        
        # 计算日期范围
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 查询数据
        query = f"""
        SELECT 
            DATE(date) as attendance_date,
            DAYOFWEEK(date) as day_of_week,
            COUNT(*) as total_employees,
            SUM(CASE 
                WHEN absent = 0 AND (work_hours > 0 OR checkin_time IS NOT NULL) 
                THEN 1 
                ELSE 0 
            END) as present_employees
        FROM attendance_record
        WHERE date BETWEEN '{first_day.strftime("%Y-%m-%d")}' AND '{last_day.strftime("%Y-%m-%d")}'
        GROUP BY DATE(date), DAYOFWEEK(date)
        ORDER BY attendance_date
        """
        
        df = pd.read_sql(query, conn)
        matplotlib.use('Agg')
        if df.empty:
            print(f"{year}年{month}月没有考勤数据")
            return False
        
        # 计算出勤率
        df['attendance_rate'] = (df['present_employees'] / df['total_employees'] * 100).round(2)
        
        # 创建热力图数据矩阵
        heatmap_data = np.full((6, 7), np.nan)
        
        # 填充数据
        for _, row in df.iterrows():
            date = row['attendance_date']
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            
            day_num = date.day
            weekday = date.weekday()  # 0=Monday, 6=Sunday
            week_num = (day_num - 1 + date.weekday()) // 7
            
            heatmap_data[week_num, weekday] = row['attendance_rate']
        
        # 创建圆角矩形热力图
        plt.figure(figsize=(11, 7))
        
        # 使用更美观的配色方案
        colors = [
            "#D4DCFA",  # 蓝灰
            "#D0E7FF",  # 非常浅的蓝色
            '#B3D9FF',  # 浅蓝色
            '#80BFFF',  # 中等浅蓝
            '#4DA6FF',  # 蓝色
            '#1A8CFF',  # 深蓝色
            '#0066CC'   # 更深蓝色 (100% 出勤率)
        ]
        cmap = LinearSegmentedColormap.from_list('attendance_cmap', colors, N=256)
        
        # 设置方块参数
        cell_width = 0.85  # 方块的宽度（小于1表示有间距）
        cell_height = 0.85  # 方块的高度
        cell_spacing = 0.15  # 方块之间的间距
        
        # 绘制圆角矩形
        for i in range(6):
            for j in range(7):
                value = heatmap_data[i, j]
                if not np.isnan(value):
                    # 计算矩形中心位置
                    x_center = j
                    y_center = 5 - i  # 反转Y轴方向，使第一周在最上面
                    
                    # 创建圆角矩形
                    rect = patches.FancyBboxPatch(
                        (x_center - cell_width/2 + cell_spacing/2, 
                         y_center - cell_height/2 + cell_spacing/2),
                        cell_width - cell_spacing,
                        cell_height - cell_spacing,
                        boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.1),
                        linewidth=0,  # 无边框
                        edgecolor='none',  # 无边缘颜色
                        facecolor=cmap(value/100),  # 根据出勤率设置颜色
                        alpha=0.9,  # 稍微透明
                        transform=plt.gca().transData
                    )
                    plt.gca().add_patch(rect)
                    
                    # 添加数值文本
                    # 根据背景亮度决定文字颜色
                    color = cmap(value/100)
                    brightness = color[0]*0.299 + color[1]*0.587 + color[2]*0.114
                    text_color = 'white' if brightness < 0.6 else 'black'
                    
                    plt.text(x_center, y_center, f'{value:.1f}%',
                            ha='center', va='center',
                            color=text_color, fontsize=11, fontweight='bold',
                            fontproperties='Microsoft YaHei')  # 使用雅黑字体
        
        # 设置坐标轴
        plt.title(f'{year}年{month}月 每周出勤率热力图', 
                 fontsize=18, fontweight='bold', pad=25,
                 fontproperties='Microsoft YaHei')
        
        weekdays_chinese = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        plt.xticks(range(7), weekdays_chinese, fontsize=12, fontproperties='Microsoft YaHei')
        plt.yticks(range(6), [f'第{i+1}周' for i in range(5, -1, -1)], fontsize=12, fontproperties='Microsoft YaHei')
        
        # 设置坐标轴范围，考虑间距
        plt.xlim(-0.5 - cell_spacing, 6.5 + cell_spacing)
        plt.ylim(-0.5 - cell_spacing, 5.5 + cell_spacing)
        
        # 隐藏不必要的边框
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(True)
        plt.gca().spines['left'].set_visible(True)
        
        # 添加网格线（可选，这里添加淡淡的参考线）
        #plt.gca().yaxis.grid(True, linestyle='--', alpha=0.3, color='gray', linewidth=0.5)
        #plt.gca().xaxis.grid(True, linestyle='--', alpha=0.3, color='gray', linewidth=0.5)
        
        # 添加颜色条
        cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap), 
                           fraction=0.03, pad=0.04, ax=plt.gca())
        cbar.set_label('出勤率 (%)', fontsize=12, fontproperties='Microsoft YaHei')
        
        # 设置颜色条范围
        cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        cbar.set_ticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
        
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(cf.res_path+output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"圆角热力图已保存到: {cf.res_path+output_path}")
        
        #plt.show()
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"生成热力图时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()


# 使用示例
if __name__ == "__main__":
    import app.services.connect_mysql as cm
    # 配置数据库连接信息
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'aq'
    }
    conn = cm.connect_mysql(*cf.default)
    # 使用示例1：带表格的版本（包含迟到/早退分钟数，总数在最后一列）
    #plot_monthly_attendance_rate_with_table(**DB_CONFIG, month=12, year=2025,output_path='attendance_with_table.png')
    
    # 使用示例2：增强版（总数在最后一列）
    # plot_monthly_attendance_rate_enhanced(**DB_CONFIG, month=5, year=2024,
    #                                       output_path='attendance_enhanced.png')
    stats = create_attendance_heatmap_rounded(
        conn,
        year=2025,
        month=12,
        output_path='attendance_heatmap_202512.png'
    )
    if stats:
        print("\n统计信息:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    # 使用示例3：简洁版
    # plot_monthly_attendance_rate_simple_table(**DB_CONFIG, month=5, year=2024,
    #                                           output_path='attendance_simple.png')
    