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
            
            # Dùng -f "bestvideo+bestaudio/best" hoặc --format hls kết hợp với -g 
            # để ép yt-dlp trả về link master stream có cả hình lẫn tiếng
            stream_cmd = ["yt-dlp", "-f", "bestvideo+bestaudio/best", "-g", web_url]
            stream_res = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=15)
            
            stream_url = ""
            if stream_res.returncode == 0:
                sub_lines = [l.strip() for l in stream_res.stdout.strip().split("\n") if l.strip()]
                
                # Duyệt qua các dòng kết quả, BỎ QUA các dòng chứa chữ aac hoặc audio thuần túy
                candidates = []
                for l in sub_lines:
                    if l.startswith("http"):
                        # Nếu dòng nào chứa "aac" hoặc "audio" thì loại trừ ngay lập tức
                        if "aac" in l or "audio" in l:
                            continue
                        candidates.append(l)
                
                # Ưu tiên lấy link manifest hoặc link dài chứa thông tin video
                for l in candidates:
                    if ".m3u8" in l or "manifest" in l or "video" in l:
                        stream_url = l
                        break
                
                # Nếu không tìm thấy link phù hợp qua lọc, lấy ứng viên hợp lệ đầu tiên không phải audio
                if not stream_url and candidates:
                    stream_url = candidates[0]
            
            # Chỉ thêm vào playlist khi có link stream chuẩn và không dính audio-only
            if stream_url and stream_url.startswith("http") and "aac" not in stream_url:
                clean_title = clean_title.replace("\n", " ").strip()
                m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                m3u_content.append(stream_url)
                count += 1
                print(f"Thêm thành công (có hình + tiếng): {clean_title}")
            else:
                print(f"Bỏ qua link audio-only hoặc lỗi: {web_url}")
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} link chuẩn vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi khi quét kênh:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
