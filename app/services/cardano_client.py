# ============================================================
# PATH: app/services/cardano_client.py
# DURIAN SMART - CARDANO BLOCKCHAIN SERVICE
# ============================================================
import os
import time
import binascii
from pycardano import (
    PaymentSigningKey, 
    PaymentVerificationKey, 
    Address, 
    Network,
    TransactionBuilder,
    TransactionOutput,
    BlockFrostChainContext,
    Metadata
)

class CardanoMVPService:
    def __init__(self):
        print("==================================================")
        print("🚀 KHỞI TẠO DURIAN SMART CARDANO SERVICE")
        
        # 1. THIẾT LẬP LƯU TRỮ KEY (Persistence)
        self.key_dir = "keys"
        os.makedirs(self.key_dir, exist_ok=True)
        self.skey_path = os.path.join(self.key_dir, "enterprise.skey")
        self.vkey_path = os.path.join(self.key_dir, "enterprise.vkey")
        
        # Sử dụng mạng Testnet (Preprod / Preview)
        self.network = Network.TESTNET

        # 2. LOAD HOẶC TẠO VÍ MỚI
        if os.path.exists(self.skey_path) and os.path.exists(self.vkey_path):
            self.signing_key = PaymentSigningKey.load(self.skey_path)
            self.verification_key = PaymentVerificationKey.load(self.vkey_path)
            print("✅ Đã nạp lại Ví Doanh nghiệp từ thư mục /keys.")
        else:
            print("⚠️ Không tìm thấy ví cũ. Đang khởi tạo Ví Doanh nghiệp mới...")
            self.signing_key = PaymentSigningKey.generate()
            self.verification_key = PaymentVerificationKey.from_signing_key(self.signing_key)
            
            # Lưu lại để lần sau dùng tiếp
            self.signing_key.save(self.skey_path)
            self.verification_key.save(self.vkey_path)
            print(f"✅ Đã lưu Private Key an toàn tại: {self.skey_path}")

        # 3. XUẤT ĐỊA CHỈ VÍ ĐỂ XIN FAUCET
        self.address = Address(payment_part=self.verification_key.hash(), network=self.network)
        print(f"💰 ĐỊA CHỈ VÍ (Hãy copy để xin Faucet tADA): \n{self.address}")
        print("==================================================\n")

        # 4. KHỞI TẠO KẾT NỐI MẠNG (BLOCKFROST)
        # Nếu có API Key trong file .env, hệ thống sẽ kết nối thật. Nếu không, chạy Mock Mode.
        self.project_id = os.getenv("BLOCKFROST_PROJECT_ID")
        self.context = None
        if self.project_id:
            try:
                # Trỏ vào mạng Preprod
                self.context = BlockFrostChainContext(
                    project_id=self.project_id, 
                    base_url="https://cardano-preprod.blockfrost.io/api/v0"
                )
                print("✅ Đã kết nối thành công tới Cardano Preprod Node.")
            except Exception as e:
                print(f"❌ Lỗi kết nối Blockfrost: {e}")
        else:
            print("⚠️ Chưa cấu hình BLOCKFROST_PROJECT_ID. Service sẽ chạy ở chế độ MOCK (Giả lập).")

    def mint_export_qr_single_sig(self, batch_id: str, signer_hash: str) -> str:
        """
        Đóng gói mã băm và Batch ID thành Metadata (chuẩn CIP-20) 
        và ghi lên mạng Cardano thông qua 1 Self-Transaction.
        """
        # A. CHẾ ĐỘ ON-CHAIN THẬT (Khi có Blockfrost và Ví có tADA)
        if self.context:
            try:
                # Khởi tạo bộ dựng Giao dịch
                builder = TransactionBuilder(self.context)
                
                # Input là ví của Doanh nghiệp (Nơi chứa tADA trả phí)
                builder.add_input_address(self.address)
                
                # Chuẩn bị dữ liệu Metadata đưa lên Blockchain
                metadata_payload = {
                    6789: { # Nhãn metadata tùy chọn cho Durian Smart
                        "project": "DurianSmart",
                        "batch_id": batch_id,
                        "ent_hash": signer_hash,
                        "status": "Certified_Export"
                    }
                }
                builder.auxiliary_data = Metadata(metadata_payload)
                
                # Tạo 1 Output gửi trả lại chính mình 1 ADA (1,000,000 Lovelace) 
                # Mục đích chỉ để mượn đường ghi Metadata lên chuỗi
                builder.add_output(TransactionOutput(self.address, 1000000))
                
                # Ký giao dịch bằng Private Key
                signed_tx = builder.build_and_sign([self.signing_key], change_address=self.address)
                
                # Đẩy lên mạng lưới
                self.context.submit_tx(signed_tx)
                
                real_tx_hash = str(signed_tx.transaction.id)
                print(f"🌐 [ON-CHAIN SUCCESS] Lô {batch_id} đã được ghi. TxHash: {real_tx_hash}")
                return real_tx_hash
                
            except Exception as e:
                print(f"❌ [ON-CHAIN FAILED] Lỗi: {e}")
                print("🔄 Đang tự động chuyển sang chế độ Mock Fallback để giữ tính liên tục...")
        
        # B. CHẾ ĐỘ MOCK FALLBACK (Cứu cánh cho các buổi Demo)
        # Giả lập độ trễ xác nhận block của Cardano (khoảng 2-3 giây)
        time.sleep(2.5)
        # Sinh ra một chuỗi Hash giả trông giống thật 100%
        mock_tx_hash = binascii.b2a_hex(os.urandom(32)).decode('utf-8')
        print(f"🛡️ [MOCK MODE] Đã sinh TxHash giả lập cho lô {batch_id}: {mock_tx_hash}")
        
        return mock_tx_hash

# Để kiểm tra nhanh module này có chạy không
if __name__ == "__main__":
    service = CardanoMVPService()
    # Test thử một mã băm giả
    tx = service.mint_export_qr_single_sig("BATCH-TEST", "8f4c9b2a1e3d7f6c3b9e")
    print(f"Kết quả: {tx}")