// ============================================================
// PATH: contracts/validators/durian_multisig.ak
// DURIAN SMART - MULTI-SIG STATE MACHINE
// ============================================================
use aiken/list
use aiken/transaction.{ScriptContext, Transaction}
use aiken/transaction/credential.{VerificationKeyHash}

// Cấu trúc Dữ liệu gắn liền với tài sản trên Blockchain
type DurianDatum {
  farmer_hash: ByteArray,
  enterprise_hash: ByteArray,
  lab_hash: ByteArray,
  enterprise_pkh: VerificationKeyHash, // Khóa công khai Doanh nghiệp
  lab_pkh: VerificationKeyHash,        // Khóa công khai Phòng Lab
}

validator {
  // Hàm kiểm tra điều kiện xuất khẩu (Đúc QR)
  fn export_approval(datum: DurianDatum, _redeemer: Void, ctx: ScriptContext) -> Bool {
    let tx = ctx.transaction
    
    // 1. Kiểm tra chữ ký của Doanh nghiệp đóng gói
    let signed_by_enterprise = list.has(tx.extra_signatories, datum.enterprise_pkh)
    
    // 2. Kiểm tra chữ ký của Phòng kiểm định độc lập
    let signed_by_lab = list.has(tx.extra_signatories, datum.lab_pkh)
    
    // 3. Phán quyết On-chain: BẮT BUỘC CÓ CẢ HAI
    signed_by_enterprise && signed_by_lab
  }
}