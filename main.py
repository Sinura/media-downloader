from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Netlify frontend එකට සම්බන්ධ වීමට ඉඩ දීම
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Backend is running!"}

@app.get("/api/extract")
def extract_media(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_list = []
            
            # Video + Audio එකට ඇති formats පෙරා ගැනීම
            for f in info.get('formats', []):
                if f.get('url'):
                    # Video + Audio දෙකම ඇති ඒවා
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        formats_list.append({
                            "type": "Video",
                            "quality": f.get('format_note') or f.get('resolution') or "Standard",
                            "ext": f.get('ext'),
                            "url": f.get('url')
                        })
                    # Audio පමණක් ඇති ඒවා (m4a / webm)
                    elif f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                        abr = f.get('abr')
                        quality_label = f"{int(abr)}kbps" if abr else "Audio"
                        formats_list.append({
                            "type": "Audio",
                            "quality": quality_label,
                            "ext": f.get('ext'),
                            "url": f.get('url')
                        })

            return {
                "title": info.get('title', 'Media File'),
                "thumbnail": info.get('thumbnail', ''),
                "duration": info.get('duration_string', ''),
                "formats": formats_list
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))