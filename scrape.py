import subprocess
import json
import urllib.request

CHANNEL_URL = "https://www.dailymotion.com/user/HP-Media/videos"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_manifest_url(video_id):
    """Hàm lấy chính xác link manifest.m3u8 từ API Dailymotion"""
    api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # 1. Tìm trong qualities -> auto (nơi chứa link chuẩn thường thấy)
            if 'qualities' in data and 'auto' in data['qualities']:
                for q in data['qualities']['auto']:
                    if 'manifest.m3u8' in q.get('url', ''):
                        return q['url']
            
            # 2. Tìm trong các luồng HLS khác nếu cấu trúc thay đổi
            if 'qualities' in data:
                for key, qualities in data['qualities'].items():
                    for q in qualities:
                        if 'manifest.m3u8' in q.get('url', ''):
                            return q['url']
                            
    except Exception as e:
        print(f"⚠️ Lỗi API {video_id}: {e}")
    return None

def generate_m3u():
    print(f"Đang lấy danh sách video từ kênh...")
    
    # yt-dlp chỉ dùng để lấy danh sách video (không lấy link stream)
    cmd = ["yt-dlp", "--flat-playlist", "--playlist-end", "15", "--dump-json", "--no-warnings", CHANNEL_URL]
    
    m3u_content = ["#EXTM3U"]
    count = 0
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        
        for line in result.stdout.strip().split("\n"):
            if not line.strip(): continue
            try:
                v_info = json.loads(line)
                v_id = v_info.get("id")
                v_title = v_info.get("title", f"Video {count+1}").replace("\n", " ").replace('"', "'").strip()
                
                print(f"Đang lấy link manifest: {v_title}")
                
                # Lấy link manifest.m3u8
                stream_url = get_manifest_url(v_id)
                
                if stream_url:
                    m3u_content.append(f'#EXTINF:-1 group-title="HP-Media Dailymotion", {v_title}')
                    m3u_content.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}')
                    m3u_content.append(f'#EXTVLCOPT:http-referrer=https://www.dailymotion.com/')
                    m3u_content.append(stream_url)
                    count += 1
                    print(f"✅ OK: {v_title}")
                else:
                    print(f"❌ Bỏ qua (không lấy được link manifest): {v_title}")
                    
            except Exception as e:
                print(f"Lỗi xử lý video: {e}")
                continue
                
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_content))
        print(f"\n✅ Hoàn tất! Đã thêm {count} video vào playlist.")
        
    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    generate_m3u()
