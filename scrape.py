import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    # Dùng yt-dlp lấy trực tiếp tiêu đề và link stream tổng hợp (cả hình và tiếng) thông qua định dạng best
    command = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", "15",
        "--print", "%(title)s",
        "--print", "%(url)s",
        CHANNEL_URL
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=40)
        lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        
        m3u_content = ["#EXTM3U"]
        count = 0
        
        # Vì --print sẽ in ra xen kẽ: [Title 1, URL 1, Title 2, URL 2, ...]
        i = 0
        while i < len(lines) - 1:
            title = lines[i]
            web_url = lines[i+1]
            
            # Nếu dòng lệch, dịch chuyển tìm kiếm
            if not web_url.startswith("http"):
                i += 1
                continue
                
            clean_title = title.replace("\n", " ").strip()
            if not clean_title or clean_title == "NA":
                clean_title = f"Dailymotion Video {count + 1}"
                
            print(f"Đang lấy link m3u8 cho: {clean_title}")
            
            # Lấy link m3u8 chuẩn có cả hình lẫn tiếng từ link web chi tiết
            stream_cmd = ["yt-dlp", "-f", "best", "-g", web_url]
            stream_res = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=15)
            
            stream_url = ""
            if stream_res.returncode == 0:
                sub_lines = [l.strip() for l in stream_res.stdout.strip().split("\n") if l.strip()]
                for l in sub_lines:
                    if ".m3u8" in l or "manifest" in l:
                        stream_url = l
                        break
                if not stream_url and sub_lines:
                    stream_url = sub_lines[0]
                    
            # Fallback nếu không bóc được link m3u8 thì dùng luôn link web gốc để IPTV tự render
            if not stream_url or not stream_url.startswith("http"):
                stream_url = web_url
                
            m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
            m3u_content.append(stream_url)
            count += 1
            i += 2
            
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} video vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
