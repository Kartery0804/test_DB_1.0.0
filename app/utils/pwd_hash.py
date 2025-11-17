import hashlib
import os
import base64
import hmac

def hash_password(password, salt=None):
    """带盐值的密码哈希"""
    if salt is None:
        salt = os.urandom(32)  # 32字节盐
    elif isinstance(salt, str):
        # 如果salt是十六进制字符串，转换为字节
        salt = bytes.fromhex(salt)
    
    # 使用PBKDF2算法
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    combined = salt + hashed
    return base64.b64encode(combined).decode('utf-8')

def verify_password(password, hashed_password):
    """验证密码是否匹配哈希值"""
    try:
        # 解码Base64字符串
        decoded = base64.b64decode(hashed_password)
        salt = decoded[:32]  # 前32字节是盐
        stored_hash = decoded[32:64]  # 明确取32字节的哈希值
        
        # 使用相同的盐值计算输入密码的哈希
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        # 使用hmac模块的compare_digest函数
        return hmac.compare_digest(stored_hash, new_hash)
    except Exception as e:
        print(f"验证过程中出现异常: {e}")
        return False

# 测试代码
if __name__ == "__main__":
    password = "my_password"
    salt = "32000e4736d10afb99fba6db0db6b3750ae4f1b933816a7e9617ad009b3255e2"
    hashed = hash_password(password,salt)
    
    # 解码并分离盐和哈希值
    decoded = base64.b64decode(hashed)
    salt = decoded[:32]
    hash_value = decoded[32:64]  # 明确指定长度
    
    # 打印结果
    print("Base64编码的完整哈希:", hashed)
    print("解码后总长度:", len(decoded))
    print("盐 (十六进制):", salt.hex())
    print("哈希值 (十六进制):", hash_value.hex())
    print("盐长度:", len(salt))
    print("哈希值长度:", len(hash_value))
    
    # 验证密码
    print("\n验证结果:", verify_password(password, hashed))
    print("错误密码验证:", verify_password("wrong_password", hashed))