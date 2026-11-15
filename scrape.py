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
                print(f"Đang xử lý: {web_url}")
                
                # Cấu hình để trích xuất link manifest chuẩn của Dailymotion
                detail_opts = {
                    'quiet': True,
                    'noplaylist': True,
                    # Ép lấy định dạng HLS/m3u8 trực tiếp từ extractor của Dailymotion
                    'format': 'best[protocol^=m3u8]/best',
                }
                
                try:
                    with yt_dlp.YoutubeDL(detail_opts) as detail_ydl:
                        info = detail_ydl.extract_info(web_url, download=False)
                        title = info.get('title', f"Dailymotion Video {count + 1}")
                        
                        stream_url = ""
                        
                        # 1. Thử lấy trực tiếp từ thuộc tính manifest_url nếu có
                        if 'manifest_url' in info and info['manifest_url']:
                            stream_url = info['manifest_url']
                        
                        # 2. Nếu không có, quét trong danh sách formats tìm link cdndirector hoặc m3u8
                        if not stream_url and 'formats' in info:
                            for f in info['formats']:
                                f_url = f.get('url', '')
                                if 'cdndirector.dailymotion.com' in f_url or '.m3u8' in f_url:
                                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                                        stream_url = f_url
                                        break
                            # Nếu vẫn chưa thấy, lấy format bất kỳ có chứa m3u8
                            if not stream_url:
                                for f in info['formats']:
                                    f_url = f.get('url', '')
                                    if '.m3u8' in f_url:
                                        stream_url = f_url
                                        break
                        
                        # 3. Fallback cuối cùng lấy url chính của info
                        if not stream_url:
                            stream_url = info.get('url', '')

                        # Kiểm tra nếu đúng định dạng chứa cdndirector hoặc m3u8 thì ghi vào playlist
                        if stream_url and ("cdndirector.dailymotion.com" in stream_url or ".m3u8" in stream_url):
                            clean_title = title.replace("\n", " ").strip()
                            m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {clean_title}')
                            m3u_content.append(stream_url)
                            count += 1
                            print(f"Đã lấy thành công link m3u8 cho: {clean_title}")
                        else:
                            print(f"Bỏ qua do không tìm thấy link m3u8 chuẩn: {web_url}")
                            
                except Exception as e:
                    print(f"Lỗi khi xử lý video {web_url}: {e}")
                    continue
                    
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
            
        print(f"Đã cập nhật thành công {count} link m3u8 chuẩn vào playlist.m3u!")
        
    except Exception as e:
        print("Lỗi toàn cục:", e)
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXTINF:-1 group-title=\"HP-Media\", Lỗi cào dữ liệu\nhttps://vsc9.vip")

if __name__ == "__main__":
    generate_m3u()
