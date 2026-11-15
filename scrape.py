import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    # Bước 1: Lấy danh sách URL web gốc của video (giới hạn 15 video mới nhất)
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
            print(f"Đang lấy dữ liệu cho: {web_url}")
            
            # Bước 2: Lấy tiêu đề video
            title_cmd = ["yt-dlp", "--print", "%(title)s", web_url]
            title_res = subprocess.run(title_cmd, capture_output=True, text=True, timeout=10)
            clean_title = title_res.stdout.strip() if title_res.returncode == 0 else ""
            if not clean_title or clean_title == "NA":
                clean_title = f"Dailymotion Video {count + 1}"
            
            # Bước 3: Lấy đúng link stream m3u8 chuẩn có cả hình và tiếng bằng cờ -g
            stream_cmd = ["yt-dlp", "-g", web_url]
            stream_res = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=15)
            
            stream_url = ""
            if stream_res.returncode == 0:
                lines = [l.strip() for l in stream_res.stdout.strip().split("\n") if l.strip()]
                # Duyệt tìm dòng chứa manifest.m3u8 hoặc cdndirector để lấy đúng link video chính
                for l in lines:
                    if ".m3u8" in l or "manifest" in l:
                        stream_url = l
                        break
                # Nếu không khớp, lấy dòng cuối cùng làm fallback
                if not stream_url and lines:
                    stream_url = lines[-1]
            
            # Chỉ thêm vào playlist nếu lấy được link hợp lệ
            if stream_url and stream_url.startswith("http"):
                m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                m3u_content.append(stream_url)
                count += 1
            else:
                print(f"Bỏ qua do không bóc được link stream: {web_url}")
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} video vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi khi quét kênh:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
