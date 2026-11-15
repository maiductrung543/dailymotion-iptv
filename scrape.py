import subprocess

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét kênh: {CHANNEL_URL}...")
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
                title, url = line.split("\t", 1)
                clean_title = title.replace("\n", " ").strip()
                m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                m3u_content.append(url)
                count += 1
                
        # Ghi ra file playlist.m3u
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cào thành công {count} video vào file playlist.m3u!")
        
    except subprocess.CalledProcessError as e:
        print("Lỗi khi chạy yt-dlp:", e.stderr)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
