import subprocess
import json

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét kênh và lấy link stream: {CHANNEL_URL}...")
    
    # Sử dụng yt-dlp để lấy tiêu đề và lấy trực tiếp link stream (.m3u8) thay vì link web
    command = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s\t%(url)s",
        CHANNEL_URL
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        
        m3u_content = ["#EXTM3U"]
        count = 0
        
        for line in lines:
            if "\t" in line:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    title, web_url = parts
                    clean_title = title.replace("\n", " ").strip()
                    
                    if not clean_title or clean_title == "NA":
                        clean_title = f"Video Dailymotion {count + 1}"
                    
                    # Trích xuất link stream m3u8 thực tế từ link web của video
                    stream_url = get_real_stream_url(web_url.strip())
                    if stream_url:
                        m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                        m3u_content.append(stream_url)
                        count += 1
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} kênh stream vào playlist.m3u!")
        
    except subprocess.CalledProcessError as e:
        print("Lỗi khi chạy yt-dlp:", e.stderr)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

def get_real_stream_url(video_url):
    try:
        # Dùng yt-dlp để lấy link phát trực tiếp (.m3u8) chuẩn xác
        cmd = ["yt-dlp", "-g", video_url]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            urls = res.stdout.strip().split("\n")
            return urls[-1] # Lấy link stream tối ưu nhất
    except Exception:
        pass
    return video_url # Fallback về link gốc nếu không bóc tách được

if __name__ == "__main__":
    generate_m3u()
