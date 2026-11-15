import subprocess
import json

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    list_command = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", "15",
        "--dump-json",
        "--no-warnings",
        "--impersonate", "chrome",
        CHANNEL_URL
    ]
    
    m3u_content = ["#EXTM3U"]
    count = 0
    
    try:
        # Tăng timeout lên 120s để an toàn
        result = subprocess.run(list_command, capture_output=True, text=True, check=True, timeout=120)
        json_lines = result.stdout.strip().split("\n")
        
        for line in json_lines:
            if not line.strip():
                continue
                
            try:
                video_data = json.loads(line)
                web_url = video_data.get("url") or video_data.get("webpage_url")
                
                if not web_url:
                    continue
                    
                clean_title = video_data.get("title", "")
                if not clean_title or clean_title == "NA" or "Dailymotion Video" in clean_title:
                    clean_title = f"HP-Media Video {count + 1}"
                
                print(f"Đang xử lý: {clean_title}")
                
                stream_cmd = [
                    "yt-dlp", 
                    "-f", "best[protocol^=http]/best", 
                    "-g", 
                    "--no-warnings",
                    "--no-playlist", # Ngăn yt-dlp tải cả kênh nếu link bị nhận diện nhầm
                    "--impersonate", "chrome", 
                    web_url
                ]
                stream_res = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=30)
                
                stream_url = ""
                if stream_res.returncode == 0:
                    sub_lines = [l.strip() for l in stream_res.stdout.strip().split("\n") if l.strip()]
                    for l in sub_lines:
                        if ".m3u8" in l:
                            stream_url = l
                            break
                    if not stream_url and sub_lines:
                        stream_url = sub_lines[0]
                
                if not stream_url or not stream_url.startswith("http"):
                    stream_url = web_url
                
                # Làm sạch tiêu đề
                clean_title = clean_title.replace("\n", " ").replace('"', "'").strip()
                
                m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                m3u_content.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}')
                m3u_content.append(f'#EXTVLCOPT:http-referrer=https://www.dailymotion.com/')
                m3u_content.append(stream_url)
                
                count += 1
                print(f"Đã thêm: {clean_title}")
                
            except Exception as e:
                print(f"Lỗi xử lý 1 video: {e}")
                continue
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"\n✅ Đã cập nhật thành công {count} video vào playlist.m3u!")
        
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng khi quét kênh: {e}")
        # Fallback nếu toàn bộ quá trình lỗi (VD: Dailymotion chặn IP)
        if count == 0:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
