import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video và lấy link m3u8 chuẩn từ: {CHANNEL_URL}...")
    
    # Bước 1: Lấy danh sách URL gốc của video (giới hạn 15 video mới nhất)
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
            print(f"Đang bóc tách m3u8 cho: {web_url}")
            
            # Bước 2: Dùng yt-dlp trích xuất link master m3u8 và tiêu đề thật
            # Thêm cờ --format hoặc lấy trực tiếp định dạng hls/master stream
            info_command = [
                "yt-dlp",
                "--get-title",
                "-f", "best[ext=mp4]/best", # Ưu tiên định dạng tốt nhất có đủ hình/tiếng
                "-g",
                web_url
            ]
            
            try:
                info_res = subprocess.run(info_command, capture_output=True, text=True, timeout=15)
                if info_res.returncode == 0:
                    output_lines = info_res.stdout.strip().split("\n")
                    if len(output_lines) >= 2:
                        title = output_lines[0].strip()
                        # Lọc lấy dòng chứa m3u8 hoặc dòng stream tốt nhất thay vì audio-only
                        stream_url = ""
                        for line in output_lines[1:]:
                            if ".m3u8" in line or "manifest" in line:
                                stream_url = line.strip()
                                break
                        # Nếu không lọc được dòng m3u8 ưu tiên, lấy dòng cuối cùng
                        if not stream_url:
                            stream_url = output_lines[-1].strip()
                        
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
