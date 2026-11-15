import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    # Lấy danh sách URL web gốc của video (giới hạn 15 video mới nhất)
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
            
            # Lấy tiêu đề video
            title_cmd = ["yt-dlp", "--print", "%(title)s", web_url]
            title_res = subprocess.run(title_cmd, capture_output=True, text=True, timeout=10)
            clean_title = title_res.stdout.strip() if title_res.returncode == 0 else ""
            if not clean_title or clean_title == "NA":
                clean_title = f"Dailymotion Video {count + 1}"
            
            # Lấy trực tiếp link stream m3u8 có cả hình và tiếng thông qua -g
            stream_cmd = ["yt-dlp", "-g", web_url]
            stream_res = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=15)
            
            stream_url = ""
            if stream_res.returncode == 0:
                sub_lines = [l.strip() for l in stream_res.stdout.strip().split("\n") if l.strip()]
                for l in sub_lines:
                    # Ưu tiên bắt đúng link manifest m3u8 chuẩn
                    if ".m3u8" in l or "manifest" in l or "cdndirector" in l:
                        stream_url = l
                        break
                # Nếu không khớp từ khóa nhưng có kết quả, lấy dòng chứa liên kết http hợp lệ đầu tiên
                if not stream_url and sub_lines:
                    for l in sub_lines:
                        if l.startswith("http"):
                            stream_url = l
                            break
            
            # CHỈ THÊM VÀO PLAYLIST KHI LẤY ĐƯỢC LINK M3U8 CHUẨN, TUYỆT ĐỐI KHÔNG FALLBACK VỀ LINK WEB
            if stream_url and stream_url.startswith("http") and ".m3u8" in stream_url:
                clean_title = clean_title.replace("\n", " ").strip()
                m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                m3u_content.append(stream_url)
                count += 1
                print(f"Đã thêm thành công: {clean_title}")
            else:
                print(f"Bỏ qua do không trích xuất được link m3u8 chuẩn: {web_url}")
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} link m3u8 vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi khi quét kênh:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
