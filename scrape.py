import subprocess
import json

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print("Bắt đầu chạy...")
    
    cmd = ["yt-dlp", "--flat-playlist", "--playlist-end", "3", "--dump-json", "--no-warnings", CHANNEL_URL]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        lines = result.stdout.strip().split("\n")
        
        for line in lines:
            if not line.strip(): continue
            v_info = json.loads(line)
            v_id = v_info.get("id")
            v_url = v_info.get("url")
            print(f"\n--- Đang kiểm tra video: {v_id} ---")
            
            # Gọi thử lệnh yt-dlp lấy link để xem nó báo lỗi gì
            test_cmd = ["yt-dlp", "-g", "--no-warnings", v_url]
            res = subprocess.run(test_cmd, capture_output=True, text=True)
            
            if res.returncode == 0:
                print(f"-> Lấy link THÀNH CÔNG. Link đầu tiên: {res.stdout.strip().split()[0][:100]}...")
            else:
                print(f"-> LẤY LINK THẤT BẠI. Lỗi chi tiết từ yt-dlp:")
                print(res.stderr.strip()) # IN RA TOÀN BỘ LỖI

    except Exception as e:
        print(f"Lỗi script: {e}")

if __name__ == "__main__":
    generate_m3u()
