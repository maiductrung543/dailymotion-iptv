import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    # Lấy danh sách URL gốc của video (giới hạn 15 video mới nhất)
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
            print(f"Đang lấy link cho: {web_url}")
            
            # Lấy tiêu đề và link stream trực tiếp bằng định dạng --print thay vì -g để tránh lệch dòng
            info_command = [
                "yt-dlp",
                "--print", "%(title)s",
                "--print", "%(url)s",
                web_url
            ]
            
            try:
                info_res = subprocess.run(info_command, capture_output=True, text=True, timeout=15)
                if info_res.returncode == 0:
                    lines = [l.strip() for l in info_res.stdout.strip().split("\n") if l.strip()]
                    if len(lines) >= 2:
                        title = lines[0]
                        # Lấy trực tiếp link stream m3u8 chính hãng từ yt-dlp
                        stream_url = lines[1]
                        
                        clean_title = title.replace("\n", " ").strip()
                        if not clean_title or clean_title == "NA":
                            clean_title = f"Dailymotion Video {count + 1}"
                        
                        m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                        m3u_content.append(stream_url)
                        count += 1
            except subprocess.TimeoutExpired:
                print(f"Bỏ qua do quá thời gian: {web_url}")
                continue
            except Exception:
                continue
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} video vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi khi quét kênh:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
