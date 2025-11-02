import subprocess
import sys

def start_mysql_service():
    """启动 MySQL 80 服务(Windows 专用）"""
    service_name = "MySQL80"  # MySQL 80 的默认服务名称
    
    try:
        # 检查服务是否已在运行
        status_result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if "RUNNING" in status_result.stdout:
            print(f"✅ MySQL 服务 '{service_name}' 已在运行")
            return True
        
        # 启动 MySQL 服务
        print(f"🚀 正在启动 MySQL 服务 '{service_name}'...")
        start_result = subprocess.run(
            ["net", "start", service_name],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if start_result.returncode == 0:
            print(f"✅ MySQL 服务 '{service_name}' 启动成功")
            return True
        else:
            print(f"❌ 启动失败: {start_result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

# 添加停止服务的功能
def stop_mysql_service():
    service_name = "MySQL80"
    try:
        print(f"🛑 正在停止 MySQL 服务 '{service_name}'...")
        stop_result = subprocess.run(
            ["net", "stop", service_name],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if stop_result.returncode == 0:
            print(f"✅ MySQL 服务 '{service_name}' 已停止")
            return True
        else:
            print(f"❌ 停止失败: {stop_result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 MySQL 80 服务管理程序")
    print("=" * 50)
    if len(sys.argv) < 2:
        print("请输入参数 [start|stop]")
    else:
        flag = sys.argv[1]
        if flag == "start":
            if start_mysql_service():
                print("\n✅ 操作成功完成")
            else:
                print("\n❌ 操作失败，请检查错误信息")
            
            print("\n" + "=" * 50)
            # 添加暂停，防止窗口立即关闭
            input("按 Enter 键退出...")
        elif flag == "stop":
            if stop_mysql_service():
                print("\n✅ 操作成功完成")
            else:
                print("\n❌ 操作失败，请检查错误信息")
        else:
            print("\n❌ 非法参数")