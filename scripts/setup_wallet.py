# ============================================================
# PATH: scripts/setup_wallet.py
# ============================================================
import os
from pycardano import PaymentSigningKey, PaymentVerificationKey, Address, Network

def create_wallet(role_name: str):
    # Khởi tạo Private Key
    sk = PaymentSigningKey.generate()
    sk.save(f"keys/{role_name}.sk")
    
    # Khởi tạo Public Key (Verification Key)
    vk = PaymentVerificationKey.from_signing_key(sk)
    vk.save(f"keys/{role_name}.vk")
    
    # Tạo địa chỉ ví trên mạng Preprod (Testnet)
    address = Address(payment_part=vk.hash(), network=Network.TESTNET)
    
    print(f"🔐 Đã tạo thành công ví cho: {role_name.upper()}")
    print(f"👉 Địa chỉ ví: {address}\n")

if __name__ == "__main__":
    print("⏳ Khởi tạo hệ thống Chìa khóa Đa chữ ký...\n")
    
    # Đảm bảo thư mục keys tồn tại
    if not os.path.exists("keys"):
        os.makedirs("keys")
        
    create_wallet("enterprise")
    create_wallet("lab")
    
    print("⚠️ LƯU Ý QUAN TRỌNG: Tuyệt đối KHÔNG đẩy thư mục keys/ lên GitHub!")