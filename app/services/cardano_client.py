# ============================================================
# PATH: app/services/cardano_client.py
# DURIAN SMART - ON-CHAIN MULTI-SIG ENGINE
# ============================================================
import os
from pycardano import (
    BlockFrostChainContext, Network, PaymentSigningKey, 
    PaymentVerificationKey, Address, TransactionBuilder, 
    TransactionOutput, PlutusData
)
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Phải khớp hoàn toàn với cấu trúc DurianDatum trong Aiken
@dataclass
class OnChainDurianDatum(PlutusData):
    CONSTR_ID = 0
    farmer_hash: bytes
    enterprise_hash: bytes
    lab_hash: bytes
    enterprise_pkh: bytes
    lab_pkh: bytes

class CardanoMultiSigService:
    def __init__(self):
        project_id = os.getenv("BLOCKFROST_PROJECT_ID")
        if not project_id:
            raise ValueError("Thiếu cấu hình BLOCKFROST_PROJECT_ID trong file .env")
            
        # Tự động nhận diện mạng lưới (Preprod) thông qua Blockfrost ID
        self.context = BlockFrostChainContext(
            project_id=project_id,
            network=Network.TESTNET
        )
        
        # Nạp Private Keys từ thư mục bảo mật
        self._load_wallet_keys()

    def _load_wallet_keys(self):
        """Nạp cả 2 chìa khóa bí mật vào bộ nhớ"""
        try:
            # Ví Doanh nghiệp
            self.ent_sk = PaymentSigningKey.load("keys/enterprise.sk")
            self.ent_vk = PaymentVerificationKey.from_signing_key(self.ent_sk)
            self.ent_pkh = self.ent_vk.hash()
            self.ent_address = Address(payment_part=self.ent_pkh, network=Network.TESTNET)
            
            # Ví Phòng Lab
            self.lab_sk = PaymentSigningKey.load("keys/lab.sk")
            self.lab_vk = PaymentVerificationKey.from_signing_key(self.lab_sk)
            self.lab_pkh = self.lab_vk.hash()
            self.lab_address = Address(payment_part=self.lab_pkh, network=Network.TESTNET)
        except Exception as e:
            print("⚠️ CẢNH BÁO: Không tìm thấy thư mục keys. Cần chạy file setup_wallet.py!")

    def mint_export_qr_onchain(self, batch_id: str, farmer_hash: str, ent_hash: str, lab_hash: str) -> str:
        """Thực thi Giao dịch Đa chữ ký lên Cardano"""
        print(f"⏳ Khởi tạo giao dịch Đa chữ ký cho lô hàng: {batch_id}")
        
        # 1. Đóng gói Datum chuẩn
        datum = OnChainDurianDatum(
            farmer_hash=bytes.fromhex(farmer_hash),
            enterprise_hash=bytes.fromhex(ent_hash),
            lab_hash=bytes.fromhex(lab_hash),
            enterprise_pkh=bytes(self.ent_pkh),
            lab_pkh=bytes(self.lab_pkh)
        )

        # 2. Xây dựng giao dịch (Lấy tiền từ ví Doanh nghiệp làm phí Gas)
        builder = TransactionBuilder(self.context)
        builder.add_input_address(self.ent_address)
        
        # Mô phỏng việc đúc 1 NFT tượng trưng cho Mã QR
        # (Trong thực tế sẽ dùng Plutus Minting Policy, ở đây xuất Output kèm Datum)
        output = TransactionOutput(
            address=self.ent_address,
            amount=2_000_000, # Trả lại 2 ADA vào ví kèm Dữ liệu
            datum=datum
        )
        builder.add_output(output)
        
        # 3. Yêu cầu Đa chữ ký (Bắt buộc phải có mặt cả 2 chữ ký)
        builder.required_signers = [self.ent_pkh, self.lab_pkh]

        # 4. Ký giao dịch bằng cả 2 Private Keys
        signed_tx = builder.build_and_sign(
            signing_keys=[self.ent_sk, self.lab_sk],
            change_address=self.ent_address
        )

        # 5. Bắn lên mạng lưới
        self.context.submit_tx(signed_tx)
        
        tx_hash = signed_tx.transaction.id.payload.hex()
        print(f"✅ Giao dịch Multi-sig thành công! TxHash: {tx_hash}")
        return tx_hash