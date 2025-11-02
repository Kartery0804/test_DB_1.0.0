import create_data_csv as cdc


# 使用示例
def demo_basic_usage():
    #初始化
    generator = cdc.FakerDataGenerator('zh_CN')
    
    # 定义表属性
    user_columns = [
        {'name': 'username', 'type': 'string'},
        {'name': 'email', 'type': 'email'},
        {'name': 'age', 'type': 'int', 'min': 18, 'max': 80},
        {'name': 'salary', 'type': 'decimal', 'min': 3000, 'max': 50000, 'scale': 2},
        {'name': 'is_vip', 'type': 'boolean'},
        {'name': 'birth_date', 'type': 'date'},
        {'name': 'create_time', 'type': 'datetime'},
        {'name': 'city', 'type': 'string', 'generator': 'choice', 'choices': ['北京', '上海', '广州', '深圳']}
    ]
    
    #定义表
    generator.define_table(
        table_name='users',
        columns=user_columns,
        record_count=100,
        description='用户信息表'
    )
    
    #生成并导出
    result1 = generator.generate_all(output_path = './database')
    
    return result1

if __name__ == "__main__":
    cdc.setting.is_create_username_with_num = True
    result1 = demo_basic_usage()