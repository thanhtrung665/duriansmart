import {api} from "zalo-miniapp-sdk";

Page({
    data: {
        isRecording: false,
        tempAudioPath: "",
        selectedPuc: "PUC-TG-001",
        apiStatus: "Sẵn sàng gửi nhật ký canh tác"
    },
    // Hành động khi noong daan aans nuts Thu ama
    startVoiceRecord() {
        this.setData({isRecording: false});
        api.stopRecording({
            success: (res) => {
                // Zalo trả về đường dẫn file tạm thời trên điện thoại
                this.setData({ tempAudioPath: res.tempFilePath, apiStatus: "Đã thu aam xong. Sẵn sàng gửi"});

            }
        });
    },
    // Bấm nút quyết định: Bắn data xuyên qua đường hầm sang FastAPI Windows
    async submitToBlockchainCore() {
        if (!this.data.tempAudioPath) {
            this.setData({ apiStatus: "Vui lòng gửi ghi âm trước khi gửi!"});
            return;
        }
        this.setData({ apiStatus: "Đang đẩy sang AI Oracle đối soát luật, quy định từ GACC..."});

        // Cấu hình Schema khớp 100% FarmerInputSchema backend
        const farmerPayload = {
            puc_code: this.data.selectedPuc,
            durian_variety: "Ri6",
            gps: { latitude: 10.4083, longtitude: 106.7783},
            audio_file_name: "farmer_voice_zalo.wav"
        };

        // Gọi API upload file của zalo
        // điền link public url máy window -> dùng ngrok mở cổng backend window
        api.uploadFile({
            url: "https://rompishly-hygienic-adelaide.ngrok-free.app/api/v1/farmer/submit-log", // Thay bằng URL public của backend Windows
            filePath: this.data.tempAudioPath,
            name: "audio_file",  // Khớp tham số audio_file: UploadFile trong FastAPI
            formData: {
                payload: JSON.stringify(farmerPayload) // Khớp trường payload: str trong FastAPI

            },
            success: (response) => {
                const result = JSON.parse(response.data);
                if (result.status === "success"){
                    this.setData({
                        apiStatus: `Thành công! AI duyệt: ${result.blockchain_ready_data.ai_oracle_compliant ? "Hợp lệ" : "VI PHẠM LUẬT GACC"}`
                    });
                }
            },
            fail: (err) => {
                this.setData({ apiStatus: "Lỗi kết nối"});
            }
        });
    }
});