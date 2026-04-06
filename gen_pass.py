import secrets
import string

def generate_secure_password(length=14):
    """Tạo mật khẩu cực mạnh bao gồm chữ, số và ký tự đặc biệt."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        # Ràng buộc điều kiện tối thiểu để mk không quá yếu
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 2
                and any(c in "!@#$%^&*" for c in password)):
            return password

if __name__ == '__main__':
    print("=" * 50)
    print("🔒 TRÌNH TẠO MẬT KHẨU BẢO MẬT CAO")
    print("=" * 50)
    
    new_password = generate_secure_password(16)
    
    print(f"\nMật khẩu mới của bạn là: {new_password}\n")
    print("Hãy copy đoạn thông tin sau dán vào file .env của bạn:")
    print("-" * 50)
    print(f"ADMIN_USERNAME=admin")
    print(f"ADMIN_PASSWORD={new_password}")
    print("-" * 50)
