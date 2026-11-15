import yt_dlp

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"

def generate_m3u():
    print(f"Đang quét danh sách video từ: {CHANNEL_URL}...")
    
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'playlistend': 15,
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(CHANNEL_URL, download=False)
            if not playlist_info or 'entries' not in playlist_info:
                print("Không tìm thấy video nào!")
                return
            
            entries = playlist_info['entries']
            m3u_content = ["#EXTM3U"]
            count = 0
            
            for entry in entries:
                web_url = entry.get('url') or f"https://www.dailymotion.com/video/{entry.get('id')}"
                print(f"Đang trích xuất link chuẩn cho: {web_url}")
                
                # Dùng instance riêng để lấy thông tin chi tiết từng video (bao gồm link master m3u8 có cả hình lẫn tiếng)
                detail_opts = {
                    'format': 'best',
                    'quiet': True,
                    'noplaylist': True,
                }
                
                try:
                    with yt_dlp.YoutubeDL(detail_opts) as detail_ydl:
                        info = detail_ydl.extract_info(web_url, download=False)
                        title = info.get('title', f"Dailymotion Video {count + 1}")
                        
                        # Lấy đúng link url hoặc manifest m3u8 tổng hợp
                        stream_url = info.get('url')
                        if not stream_url and 'formats' in info:
                            # Lấy format tốt nhất có cả video và audio
                            for f in reversed(info['formats']):
                                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                                    stream_url = f.get('url')
                                    break
                        
                        if stream_url:
                            clean_title = title.replace("\n", " ").strip()
                            m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                            m3u_content.append(stream_url)
                            count += 1
                except Exception as e:
                    print(f"Bỏ qua video lỗi: {e}")
                    continue
                    
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} video chuẩn có cả hình và tiếng vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi toàn cục:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
