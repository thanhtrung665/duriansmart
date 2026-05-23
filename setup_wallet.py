import os
from pycardano import PaymentKeyPair, Address, Network

# Tạo thư mục chứa khóa bí mật
os.makedirs("keys", exist_ok=True)

# Sinh cặp khóa mới
key_pair = PaymentKeyPair.generate()

# Lưu Private Key (Khóa bí mật dùng để ký giao dịch đúc QR)
key_pair.signing_key.save("keys/enterprise.sk")

# Lưu public key
key_pair.verification_key.save("keys/enterprise.vk")

# Sinh địa chỉ ví trên mạng Testnet
enterprise_address = Address(
    payment_part=key_pair.verification_key.hash(),
    network=Network.TESTNET
)
print("Tạo ví doanh nghiệp thành công")
print(f"Địa chỉ ví: {enterprise_address}")
print(f"Mã băm Public Key: {key_pair.verification_key.hash().to_primitive().hex()}")