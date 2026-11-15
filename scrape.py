import subprocess
import json

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    # Bước 1: Lấy danh sách các URL video trước (giới hạn 15 video mới nhất để chạy nhanh)
    list_command = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", "15",
        "--print", "%(url)s",
        CHANNEL_URL
    ]
    
    try:
        result = subprocess.run(list_command, capture_output=True, text=True, check=True, timeout=30)
        video_urls = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        
        m3u_content = ["#EXTM3U"]
        count = 0
        
        for web_url in video_urls:
            print(f"Đang xử lý video: {web_url}")
            # Bước 2: Lấy tiêu đề thật và link m3u8 chuẩn (.m3u8) cho từng video
            # Sử dụng --print kết hợp title và url trực tiếp qua yt-dlp
            info_command = [
                "yt-dlp",
                "--get-title",
                "-g",
                web_url
            ]
            
            try:
                info_res = subprocess.run(info_command, capture_output=True, text=True, timeout=15)
                if info_res.returncode == 0:
                    output_lines = info_res.stdout.strip().split("\n")
                    if len(output_lines) >= 2:
                        title = output_lines[0].strip()
                        stream_url = output_lines[-1].strip() # Link m3u8 thực tế nằm ở dòng cuối
                        
                        clean_title = title.replace("\n", " ").strip()
                        if not clean_title:
                            clean_title = f"Dailymotion Video {count + 1}"
                        
                        m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                        m3u_content.append(stream_url)
                        count += 1
            except subprocess.TimeoutExpired:
                print(f"Bỏ qua video do quá thời gian: {web_url}")
                continue
            except Exception:
                continue
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} link m3u8 vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi khi quét kênh:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
