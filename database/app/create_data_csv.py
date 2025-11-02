import csv
import json
import random
import os
from faker import Faker
from datetime import datetime

class setting:
    is_create_username_with_num = True



class FakerDataGenerator:
    """精简版Faker数据生成器，仅支持JSON格式"""
    
    def __init__(self, locale='zh_CN'):
        self.faker = Faker(locale)
        self.metadata = {}
        self._sequence_counters = {}  # 用于序列生成器的计数器
    
    def define_table(self, table_name, columns, record_count=1000, description=""):
        """
        定义数据表结构
        
        Args:
            table_name: 表名
            columns: 列定义列表
            record_count: 记录数量
            description: 表描述
        """
        self.metadata = {
            'table_name': table_name,
            'description': description,
            'record_count': record_count,
            'columns': columns,
            'created_at': datetime.now().isoformat(),
            'locale': self.faker.locales[0] if self.faker.locales else 'zh_CN'
        }
        # 重置序列计数器
        self._sequence_counters = {}
    
    def generate_data(self):
        """生成数据"""
        if not self.metadata:
            raise ValueError("请先使用 define_table() 定义表结构")
        
        data = []
        for i in range(self.metadata['record_count']):
            record = {'id': i + 1}
            
            for col in self.metadata['columns']:
                record[col['name']] = self._generate_value(col, i)
            
            data.append(record)
        
        return data
    
    def _generate_value(self, col, record_index):
        """根据列定义生成单个字段值"""
        col_type = col.get('type', 'string')
        generator = col.get('generator', 'default')
        
        # 自定义生成器
        if generator == 'choice':
            return random.choice(col['choices'])
        elif generator == 'sequence':
            col_name = col['name']
            start = col.get('start', 1)
            step = col.get('step', 1)
            if col_name not in self._sequence_counters:
                self._sequence_counters[col_name] = start
            else:
                self._sequence_counters[col_name] += step
            return self._sequence_counters[col_name]
        
        # 特别处理用户名生成
        if col_type == 'string' and col.get('name') == 'username':
            return self._generate_better_chinese_username()
        
        # 根据类型生成
        type_generators = {
            'int': lambda: random.randint(col.get('min', 0), col.get('max', 1000)),
            'float': lambda: round(random.uniform(col.get('min', 0.0), col.get('max', 100.0)), col.get('decimals', 2)),
            'decimal': lambda: round(random.uniform(col.get('min', 0.0), col.get('max', 10000.0)), col.get('scale', 2)),
            'boolean': lambda: random.choice([0, 1]),
            'date': lambda: self.faker.date_between(
                start_date=col.get('start_date', '-30y'),
                end_date=col.get('end_date', 'today')
            ).strftime('%Y-%m-%d'),
            'datetime': lambda: self.faker.date_time_between(
                start_date=col.get('start_date', '-1y'),
                end_date=col.get('end_date', 'now')
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'email': lambda: self.faker.email(),
            'name': lambda: self.faker.name(),
            'address': lambda: self.faker.address().replace('\n', ', '),
            'phone': lambda: self.faker.phone_number(),
            'text': lambda: self.faker.text(max_nb_chars=col.get('max_length', 200))
        }
        
        return type_generators.get(col_type, lambda: self.faker.word())()

    def _generate_better_chinese_username(self):
        """生成更自然的中文用户名"""
        # 直接使用Faker的中文姓名，然后进行简单处理
        chinese_name = self.faker.name()
        
        # 用户名变体
        username_options = [
            chinese_name,  # 直接使用中文名
            chinese_name.replace(' ', ''),  # 去掉空格
        ]
        if setting.is_create_username_with_num:
            username_options += [
                chinese_name + str(random.randint(10, 99)),  # 姓名+两位数字
                chinese_name[:2] + str(random.randint(100, 999)),  # 姓氏+三位数字
            ]
        
        return random.choice(username_options)
    
    def _normalize_path(self, path):
        """规范化路径，确保以分隔符结尾"""
        if not path:
            return ""
        
        # 标准化路径（处理./和../等）
        path = os.path.normpath(path)
        
        # 确保路径以分隔符结尾
        if not path.endswith(os.path.sep):
            path += os.path.sep
            
        return path
    
    def save_csv(self, data, filename, output_path=None):
        """保存为CSV文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
            output_path: 输出路径，如'./output/'，默认为None（当前目录）
        """
        if not data:
            return
        
        # 处理输出路径
        if output_path:
            # 规范化路径
            output_path = self._normalize_path(output_path)
            # 创建目录（如果不存在）
            os.makedirs(output_path, exist_ok=True)
            filepath = os.path.join(output_path, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return filepath
    
    def save_metadata(self, filename, output_path=None):
        """保存元数据为JSON文件
        
        Args:
            filename: 文件名
            output_path: 输出路径，如'./output/'，默认为None（当前目录）
        """
        if not self.metadata:
            raise ValueError("没有可保存的元数据")
        
        # 处理输出路径
        if output_path:
            output_path = self._normalize_path(output_path)
            os.makedirs(output_path, exist_ok=True)
            filepath = os.path.join(output_path, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_metadata(self, filename, input_path=None):
        """从JSON文件加载元数据
        
        Args:
            filename: 文件名
            input_path: 输入路径，如'./input/'，默认为None（当前目录）
        """
        # 处理输入路径
        if input_path:
            input_path = self._normalize_path(input_path)
            filepath = os.path.join(input_path, filename)
        else:
            filepath = filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        # 重置序列计数器
        self._sequence_counters = {}
    
    def generate_sql(self, output_path=None):
        """生成MySQL建表语句
        
        Args:
            output_path: 输出路径，如'./output/'，默认为None（不保存文件）
        
        Returns:
            SQL语句字符串，如果指定output_path则保存到文件并返回文件路径
        """
        if not self.metadata:
            raise ValueError("请先定义表结构")
        
        table_name = self.metadata['table_name']
        columns = self.metadata['columns']
        
        # MySQL类型映射
        type_mapping = {
            'int': 'INT',
            'float': 'FLOAT',
            'decimal': 'DECIMAL(10,2)',
            'boolean': 'TINYINT(1)',
            'date': 'DATE',
            'datetime': 'DATETIME',
            'email': 'VARCHAR(100)',
            'name': 'VARCHAR(50)',
            'address': 'VARCHAR(200)',
            'phone': 'VARCHAR(20)',
            'text': 'TEXT',
            'string': 'VARCHAR(255)'
        }
        
        sql_lines = [f"CREATE TABLE {table_name} ("]
        sql_lines.append("    id INT PRIMARY KEY,")
        
        for col in columns:
            mysql_type = type_mapping.get(col.get('type', 'string'), 'VARCHAR(255)')
            sql_lines.append(f"    {col['name']} {mysql_type},")
        
        sql_lines[-1] = sql_lines[-1].rstrip(',')  # 移除最后一行逗号
        sql_lines.append(");")
        
        sql_content = '\n'.join(sql_lines)
        
        # 如果指定了输出路径，则保存到文件
        if output_path:
            output_path = self._normalize_path(output_path)
            os.makedirs(output_path, exist_ok=True)
            
            sql_file = f"{table_name}.sql"
            sql_filepath = os.path.join(output_path, sql_file)
            
            with open(sql_filepath, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            
            return sql_filepath
        else:
            return sql_content
    
    def generate_all(self, base_filename=None, output_path=None):
        """
        一键生成所有文件
        
        Args:
            base_filename: 基础文件名（不包含扩展名），如果为None则使用表名
            output_path: 输出路径，如'./output/'，默认为None（当前目录）
        
        Returns:
            包含生成文件信息的字典
        """
        data = self.generate_data()
        
        # 如果未指定基础文件名，使用表名
        if base_filename is None:
            base_filename = self.metadata['table_name']
        
        # 生成文件
        csv_file = f"{base_filename}.csv"
        metadata_file = f"{base_filename}_metadata.json"
        sql_file = f"{base_filename}.sql"
        
        # 保存文件
        csv_path = self.save_csv(data, csv_file, output_path + "/data")
        metadata_path = self.save_metadata(metadata_file, output_path + "/sql")
        sql_path = self.generate_sql(output_path+"/sql")
        
        print(f"生成完成！")
        print(f"数据文件: {csv_path}")
        print(f"元数据文件: {metadata_path}")
        print(f"建表语句: {sql_path if isinstance(sql_path, str) else '未保存到文件'}")
        print(f"记录数量: {len(data)}")
        
        return {
            'data': data,
            'csv_file': csv_path,
            'metadata_file': metadata_path,
            'sql_file': sql_path if isinstance(sql_path, str) else None,
            'sql': sql_path if not isinstance(sql_path, str) else None
        }
