import os
from pycardano import (
    BlockFrostChainContext, Network, PaymentSigningKey,
    PaymentVerificationKey, Address, TransactionBuilder,
    TransactionOutput, PlutusData
)
from dotenv import load_dotenv
from dataclasses import dataclass 

load_dotenv()

# Ánh xạ cấu trúc Datum tương thích với Smart Contract
@dataclass
class OnChainDurianDatum(PlutusData):
    CONSTR_ID = 0
    farmer_cultivation_hash: bytes
    lab_inspection_hash: bytes
    enterprise_process_hash: bytes
    authorized_enterprise: bytes

class CardanoService:
    def __init__(self):
        # Khởi tạo kết nối Blockfrost Testnet
        project_id = os.getenv("BLOCKFROST_PROJECT_ID")
        if not project_id:
            raise ValueError("Chưa cấu hình BLOCKFROST_PROJECT_ID trong file .env")
        self.context = BlockFrostChainContext(
            project_id=project_id,
            network=Network.TESTNET
        )
        # Nạp cặp khóa Doanh nghiệp để làm ví vận hành
        try:
            self.sk = PaymentSigningKey.load("keys/enterprise.sk")
            self.vk = PaymentVerificationKey.load("keys/enterprise.vk")
            self.enterprise_address = Address(payment_part=self.vk.hash(), network=Network.TESTNET)
        except Exception as e:
            print("Lỗi: Chưa tìm thấy file keys/enterprise.sk. Hãy chạy lại setup_wallet.py")
    
    def mint_export_qr_onchain(self, batch_id: str, farmer_hash: str, lab_hash: str, phc_hash: str) -> str:
        """
        Hàm đóng gói 3 bằng chứng bất biến và đẩy lên Cardano.
        Trả về Transaction Hash (Dùng để in QR Code).
        """
        # Bước 1: Khởi tạo Datum mang dữ liệu băm
        datum = OnChainDurianDatum(
            farmer_cultivation_hash=farmer_hash.encode('utf-8'),
            lab_inspection_hash=lab_hash.encode('utf-8'),
            enterprise_process_hash=phc_hash.encode('utf-8'),
            authorized_enterprise=bytes(self.vk.hash())
        )

        # Bước 2: Xây dựng Giao dịch (Build Transaction)
        builder = TransactionBuilder(self.context)
        builder.add_input_address(self.enterprise_address)
        
        # Gắn Datum vào Output (Lưu trữ vĩnh viễn trên sổ cái)
        # Gửi 1 ADA (1,000,000 Lovelace) tượng trưng để neo dữ liệu
        builder.add_output(TransactionOutput(
            address=self.enterprise_address,
            amount=1_000_000, 
            datum=datum
        ))

        # Bước 3: Ký duyệt bằng Private Key của Doanh nghiệp và Submit
        signed_tx = builder.build_and_sign([self.sk], change_address=self.enterprise_address)
        self.context.submit_tx(signed_tx)
        
        # Trả về mã Hash của giao dịch
        return signed_tx.transaction_body.hash().hex()