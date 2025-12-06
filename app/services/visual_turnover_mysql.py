import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime
from app.services import config_mysql as cf
def generate_monthly_turnover_rate_no_table(conn:pymysql.Connection,year, output_file='turnover_rate.png',**kwargs):
    """
    计算某年每个月的离职率并生成折线图（不包含底部表格）
    
    参数：
    - year: 要计算的年份（如：2023）
    - host: 数据库主机地址
    - user: 数据库用户名
    - password: 数据库密码
    - database: 数据库名
    - output_file: 输出图片文件名
    
    返回：
    - 保存离职率折线图为PNG格式
    """
    
    # 设置中文字体（如果图表需要显示中文）
    try:
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
    except:
        pass
    
    # 连接数据库
    try:
        conn = pymysql.connect(
            **cf.default_dict
        )
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False
    
    try:
        # 使用更可靠的查询方式
        sql = f"""
        -- 生成12个月的数据
        WITH months AS (
            SELECT DATE('{year}-01-01') + INTERVAL (t.n) MONTH as month_start
            FROM (
                SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 
                UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
            ) t
        ),
        -- 获取每月离职人数
        monthly_resignations AS (
            SELECT 
                DATE_FORMAT(effective_date, '%Y-%m') as month,
                COUNT(DISTINCT employee_id) as resignations
            FROM employment_history 
            WHERE change_type = '状态变更' 
                AND (reason LIKE '%变更为 resigned%' OR reason LIKE '%变更为resigned%')
                AND YEAR(effective_date) = {year}
            GROUP BY DATE_FORMAT(effective_date, '%Y-%m')
        ),
        -- 获取每月月初在职人数
        monthly_headcount AS (
            SELECT 
                DATE_FORMAT(m.month_start, '%Y-%m') as month,
                COUNT(DISTINCT e.employee_id) as headcount
            FROM months m
            LEFT JOIN employee e ON e.hire_date <= m.month_start
                AND (
                    e.status != 'resigned' 
                    OR NOT EXISTS (
                        SELECT 1 
                        FROM employment_history eh
                        WHERE eh.employee_id = e.employee_id
                            AND eh.change_type = '状态变更'
                            AND (eh.reason LIKE '%变更为 resigned%' OR eh.reason LIKE '%变更为resigned%')
                            AND eh.effective_date <= m.month_start
                    )
                )
            GROUP BY m.month_start
        )
        -- 合并结果
        SELECT 
            h.month,
            h.headcount,
            COALESCE(r.resignations, 0) as resignations
        FROM monthly_headcount h
        LEFT JOIN monthly_resignations r ON h.month = r.month
        ORDER BY h.month;
        """
        
        # 执行查询
        with conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            result_df = pd.DataFrame(data)
        matplotlib.use('Agg')
        # 如果数据为空，提示并返回
        if result_df.empty:
            print(f"警告：{year}年没有找到相关数据")
            return False
        
        # 确保数据类型为数值型
        result_df['headcount'] = pd.to_numeric(result_df['headcount'], errors='coerce')
        result_df['resignations'] = pd.to_numeric(result_df['resignations'], errors='coerce')
        
        # 确保有12个月的数据
        all_months = [f'{year}-{str(i).zfill(2)}' for i in range(1, 13)]
        
        # 创建一个完整的月份DataFrame
        full_months_df = pd.DataFrame({'month': all_months})
        
        # 合并数据
        result_df = pd.merge(full_months_df, result_df, on='month', how='left')
        
        # 修复Pandas版本兼容性问题：使用ffill()而不是fillna(method='ffill')
        result_df['headcount'] = result_df['headcount'].ffill().fillna(0)
        result_df['resignations'] = result_df['resignations'].fillna(0)
        
        # 计算离职率（确保为浮点数）
        result_df['turnover_rate'] = result_df.apply(
            lambda row: (float(row['resignations']) / float(row['headcount']) * 100) 
            if row['headcount'] > 0 else 0.0, 
            axis=1
        )
        
        # 确保所有数值都是Python原生float类型，不是Decimal
        result_df['headcount'] = result_df['headcount'].astype(float)
        result_df['resignations'] = result_df['resignations'].astype(float)
        result_df['turnover_rate'] = result_df['turnover_rate'].astype(float)
        
        # 创建图表
        fig = plt.figure(figsize=(10, 5))
        
        # 创建主Y轴（离职率折线图）
        ax1 = plt.gca()
        
        # 绘制离职率折线图
        line_color = '#E63946'  # 红色系
        turnover_rates = result_df['turnover_rate'].tolist()
        line = ax1.plot(range(len(turnover_rates)), turnover_rates, 
                       marker='o', linewidth=3, markersize=10, color=line_color,
                       markerfacecolor='white', markeredgewidth=2, markeredgecolor=line_color,
                       label='离职率 (%)')
        
        # 设置主Y轴标签
        ax1.set_ylabel('离职率 (%)', fontsize=16, fontweight='bold', color=line_color)
        ax1.tick_params(axis='y', labelsize=14, labelcolor=line_color)
        
        # 设置X轴
        month_labels = [m[5:7] + '月' for m in result_df['month']]
        ax1.set_xticks(range(len(month_labels)))
        ax1.set_xticklabels(month_labels, fontsize=14, rotation=0)
        ax1.set_xlabel('月份', fontsize=16, fontweight='bold', labelpad=10)
        
        # 设置图表标题
        plt.title(f'{year}年每月离职率趋势分析', fontsize=20, fontweight='bold', pad=25)
        
        # 在折线上方标注具体数值 - 修复Decimal类型问题
        for i, rate in enumerate(turnover_rates):
            if rate > 0:  # 只在有离职率的时候显示数值
                # 确保rate是float类型
                rate_float = float(rate)
                ax1.text(i, rate_float + 0.05, f'{rate_float:.2f}%', 
                        ha='center', va='bottom', fontsize=11, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE5B4', alpha=0.9, edgecolor='#FF6B6B'))
        
        # 创建次Y轴（显示在职人数和离职人数）
        ax2 = ax1.twinx()
        
        # 绘制在职人数柱状图
        bar1_color = '#1D3557'  # 深蓝色
        headcounts = result_df['headcount'].tolist()
        bar1 = ax2.bar([x-0.2 for x in range(len(headcounts))], headcounts, 
                      width=0.4, alpha=0.7, color=bar1_color, label='月初在职人数')
        
        # 绘制离职人数柱状图
        bar2_color = '#E9C46A'  # 金色
        resignations = result_df['resignations'].tolist()
        bar2 = ax2.bar([x+0.2 for x in range(len(resignations))], resignations, 
                      width=0.4, alpha=0.7, color=bar2_color, label='当月离职人数')
        
        # 设置次Y轴标签
        ax2.set_ylabel('人数', fontsize=16, fontweight='bold')
        ax2.tick_params(axis='y', labelsize=14)
        
        # 在柱状图上标注人数
        max_headcount = max(headcounts) if headcounts else 0
        for i, (headcount, resignation) in enumerate(zip(headcounts, resignations)):
            # 标注在职人数
            if headcount > 0:
                ax2.text(i-0.2, headcount + max_headcount*0.01, 
                        f'{int(headcount)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # 标注离职人数
            if resignation > 0:
                ax2.text(i+0.2, resignation + max_headcount*0.01, 
                        f'{int(resignation)}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='darkred')
        
        # 设置网格线（只显示水平网格线）
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
        ax1.grid(False, axis='x')
        
        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, 
                  loc='upper left', fontsize=12, framealpha=0.9, shadow=True)
        
        # 设置Y轴范围
        max_rate = max(turnover_rates) if turnover_rates else 0
        ax1.set_ylim(0, max(max_rate * 1.4, 5))
        
        # 设置次Y轴范围
        ax2.set_ylim(0, max_headcount * 1.15)
        
        # 添加分区背景色（按季度）
        quarter_colors = ['#F0F8FF', '#FFF0F5', '#F0FFF0', '#FFF8DC']
        for i in range(4):
            start_idx = i * 3
            end_idx = min((i + 1) * 3, len(result_df))
            ax1.axvspan(start_idx-0.5, end_idx-0.5, alpha=0.1, color=quarter_colors[i])
            # # 添加季度标签
            # ax1.text(start_idx + 1, ax1.get_ylim()[1] * 0.95, f'Q{i+1}', 
            #         ha='center', va='top', fontsize=12, fontweight='bold',
            #         bbox=dict(boxstyle='round,pad=0.2', facecolor=quarter_colors[i], alpha=0.7))
        
        # 添加平均离职率参考线
        avg_rate = np.mean(turnover_rates) if turnover_rates else 0
        ax1.axhline(y=avg_rate, color='gray', linestyle='--', linewidth=2, alpha=0.7, 
                   label=f'平均离职率 ({avg_rate:.2f}%)')
        
        # 添加统计信息文本框
        total_resignations = sum(resignations)
        avg_headcount = np.mean(headcounts) if headcounts else 0
        annual_turnover_rate = (total_resignations / avg_headcount * 100) if avg_headcount > 0 else 0
        
        # 找到离职率最高和最低的月份
        if turnover_rates:
            max_rate_idx = np.argmax(turnover_rates)
            min_rate_idx = np.argmin([r if r > 0 else float('inf') for r in turnover_rates])
            min_rate_idx = min_rate_idx if min_rate_idx < len(turnover_rates) else 0
        else:
            max_rate_idx = 0
            min_rate_idx = 0
        
        stats_text = f"""
        年度统计摘要：
        • 全年总离职人数：{int(total_resignations)}人
        • 平均每月在职人数：{avg_headcount:.1f}人
        • 年度综合离职率：{annual_turnover_rate:.2f}%
        • 月度平均离职率：{avg_rate:.2f}%
        • 离职率最高月份：{month_labels[max_rate_idx]} ({turnover_rates[max_rate_idx]:.2f}%)
        • 离职率最低月份：{month_labels[min_rate_idx]} ({turnover_rates[min_rate_idx]:.2f}%)
        """
        
        # 将统计信息放在图表右上角
        # plt.figtext(0.75, 0.85, stats_text, fontsize=12, 
        #            bbox=dict(boxstyle='round', facecolor='#F8F9FA', alpha=0.9, 
        #                    edgecolor='#1D3557', linewidth=2))
        
        # 添加数据来源说明
        # plt.figtext(0.02, 0.02, f"数据来源: {database}数据库 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
        #            fontsize=10, style='italic', color='gray')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(cf.res_path+output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"图表已保存为：{cf.res_path+output_file}")
        
        # 显示图表（可选）
        #plt.show()
        
        # 在控制台打印数据摘要
        print("\n" + "="*70)
        print(f"{year}年每月离职率数据摘要")
        print("="*70)
        print(f"{'月份':<8} {'在职人数':<10} {'离职人数':<10} {'离职率':<10}")
        print("-"*40)
        
        for idx, row in result_df.iterrows():
            month_label = row['month'][5:7] + '月'
            print(f"{month_label:<8} {int(row['headcount']):<10} {int(row['resignations']):<10} {row['turnover_rate']:.2f}%")
        
        print("-"*40)
        print(f"年度总计: 平均在职{avg_headcount:.1f}人, 总离职{int(total_resignations)}人, 年度离职率{annual_turnover_rate:.2f}%")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"数据处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if conn:
            conn.close()


# 更简单直接的版本，避免复杂的数据处理
def generate_monthly_turnover_rate_simple(conn:pymysql.Connection,year, host, user, password, database, output_file='turnover_rate_simple.png'):
    """
    简单直接的离职率图表生成函数
    """
    
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # 使用更简单的查询，直接在SQL中计算离职率
        sql = f"""
        -- 生成所有月份
        WITH RECURSIVE months AS (
            SELECT 1 as month_num, DATE('{year}-01-01') as month_start
            UNION ALL
            SELECT month_num + 1, DATE_ADD(month_start, INTERVAL 1 MONTH)
            FROM months
            WHERE month_num < 12
        )
        SELECT 
            m.month_num,
            DATE_FORMAT(m.month_start, '%Y-%m') as month,
            -- 当月在职人数（排除当月之前已离职的）
            (
                SELECT COUNT(DISTINCT e.employee_id)
                FROM employee e
                WHERE e.hire_date <= m.month_start
                    AND (
                        e.status != 'resigned'
                        OR NOT EXISTS (
                            SELECT 1 
                            FROM employment_history eh
                            WHERE eh.employee_id = e.employee_id
                                AND eh.change_type = '状态变更'
                                AND (eh.reason LIKE '%resigned%')
                                AND eh.effective_date < m.month_start
                        )
                    )
            ) as headcount,
            -- 当月离职人数
            (
                SELECT COUNT(DISTINCT eh.employee_id)
                FROM employment_history eh
                WHERE eh.change_type = '状态变更'
                    AND (eh.reason LIKE '%resigned%')
                    AND DATE_FORMAT(eh.effective_date, '%Y-%m') = DATE_FORMAT(m.month_start, '%Y-%m')
            ) as resignations
        FROM months m
        ORDER BY m.month_num;
        """
        
        with conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
        
        if not data:
            print(f"没有找到{year}年的数据")
            return
        
        result_df = pd.DataFrame(data)
        
        # 转换为数值类型
        result_df['headcount'] = pd.to_numeric(result_df['headcount'], errors='coerce').fillna(0).astype(int)
        result_df['resignations'] = pd.to_numeric(result_df['resignations'], errors='coerce').fillna(0).astype(int)
        
        # 计算离职率（转换为float）
        result_df['turnover_rate'] = result_df.apply(
            lambda row: (float(row['resignations']) / float(row['headcount']) * 100) if row['headcount'] > 0 else 0.0,
            axis=1
        )
        
        # 创建图表
        plt.figure(figsize=(14, 8))
        
        # 创建折线图
        ax1 = plt.gca()
        line = ax1.plot(result_df['month_num'], result_df['turnover_rate'], 
                       marker='o', linewidth=3, markersize=8, color='red', label='离职率 (%)')
        
        # 设置X轴
        month_labels = [f'{i}月' for i in range(1, 13)]
        ax1.set_xticks(range(1, 13))
        ax1.set_xticklabels(month_labels, fontsize=12)
        ax1.set_xlabel('月份', fontsize=14)
        ax1.set_ylabel('离职率 (%)', fontsize=14, color='red')
        ax1.tick_params(axis='y', labelcolor='red')
        
        # 设置标题
        plt.title(f'{year}年每月离职率', fontsize=18, fontweight='bold', pad=20)
        
        # 添加数值标签
        # for i, row in result_df.iterrows():
        #     if row['turnover_rate'] > 0:
        #         ax1.text(row['month_num'], row['turnover_rate'] + 0.1, 
        #                 f'{row["turnover_rate"]:.1f}%', ha='center', fontsize=10)
        
        # 创建次坐标轴显示人数
        ax2 = ax1.twinx()
        
        # 绘制柱状图
        width = 0.35
        x = result_df['month_num']
        ax2.bar(x - width/2, result_df['headcount'], width, 
               alpha=0.6, color='blue', label='在职人数')
        ax2.bar(x + width/2, result_df['resignations'], width, 
               alpha=0.8, color='orange', label='离职人数')
        
        ax2.set_ylabel('人数', fontsize=14)
        
        # 添加网格和图例
        ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"图表已保存为：{output_file}")
        
        # 显示图表
        plt.show()
        
        return result_df
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if conn:
            conn.close()


# 使用示例
if __name__ == "__main__":
    conn = pymysql.connect(**cf.default_dict)
    
    # 使用修复后的版本
    year = 2025
    result = generate_monthly_turnover_rate_no_table(
        year=year,
        conn=conn,
        output_file=f'turnover_rate_{year}_fixed.png'
    )
    
    # 或者使用更简单的版本
    # result = generate_monthly_turnover_rate_simple(
    #     year=2023,
    #     host=DB_CONFIG['host'],
    #     user=DB_CONFIG['user'],
    #     password=DB_CONFIG['password'],
    #     database=DB_CONFIG['database'],
    #     output_file='turnover_rate_2023_simple.png'
    # )