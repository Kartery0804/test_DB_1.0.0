import hashlib
import os
import hmac
import binascii

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
    
    return hashed.hex(),salt.hex()

    # combined = salt + hashed
    # eturn base64.b64encode(combined).decode('utf-8')

def verify_password(password, hex_hash, hex_salt):
    """验证密码是否匹配哈希值"""
    try:
        # 将十六进制字符串转换为字节
        salt = bytes.fromhex(hex_salt)
        stored_hash = bytes.fromhex(hex_hash)
        
        # 使用相同的盐值计算输入密码的哈希
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        # 使用hmac模块的compare_digest函数安全比较
        return hmac.compare_digest(stored_hash, new_hash)
    except (ValueError, binascii.Error) as e:
        print(f"十六进制解码错误: {e}")
        return False
    except Exception as e:
        print(f"验证过程中出现异常: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    password = "seeyoutomorrow"
    salt = "32000e4736d10afb99fba6db0db6b3750ae4f1b933816a7e9617ad009b3255e2"
    hashed,salt = hash_password(password,salt)

    print("哈希(十六进制):", hashed)
    print("盐  (十六进制):", salt)

    
    # 验证密码
    print("\n验证结果:", verify_password(password,hashed,salt))
    print("错误密码验证:", verify_password("wrong_password",hashed,salt))