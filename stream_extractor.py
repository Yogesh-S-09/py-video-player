# stream_extractor.py
# (Your updated code)

from yt_dlp import YoutubeDL
import logging

logger = logging.getLogger(__name__)

def get_all_streams(url):
    """
    Extracts available video, audio, and subtitle streams using yt-dlp.
    """
    logger.info(f"Starting stream extraction for: {url}")
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_streams = []
        audio_streams = []
        
        # --- Handle direct media URLs without formats ---
        if info.get('formats') is None:
            if info.get('video_ext') == "unknown_video":
                return {
                    'title': info.get('title', url),
                    'video_streams': [{
                            'name': "Direct Stream",
                            'url': info.get('url', url),
                            'lang': "und",
                            'vcodec': info.get('vcodec', ""),
                            'acodec': info.get('acodec', ""),
                            'bandwidth': info.get('tbr', 0)
                        }],
                    'audio_streams': []
                }
            logger.warning(f"No formats found for URL: {url}")
            return None
        # ---------------------

        for f in info.get('formats', []):
            if not f.get('url'):
                continue
            
            # --- Video Streams (must have video, can have audio) ---
            if f.get('vcodec') and f.get('vcodec') != 'none':
                video_streams.append({
                    'name': f"📺 {f.get('format_note', f'{f.get('resolution')} {f.get('ext')}')}",
                    'url': f['url'],
                    'lang': f.get('language'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'bandwidth': f.get('tbr', 0)
                })
            
            # --- Audio-Only Streams (must have audio, NO video) ---
            elif (f.get('acodec') and f.get('acodec') != 'none' and 
                  (not f.get('vcodec') or f.get('vcodec') == 'none')):
                audio_streams.append({
                    'name': f"🔊 {f.get('format_note', f.get('ext'))} [{f.get('language', 'und')}]",
                    'url': f['url'],
                    'lang': f.get('language'),
                    'acodec': f.get('acodec'),
                    'bandwidth': f.get('tbr', 0)
                })

        logger.info(f"Found {len(video_streams)} video, {len(audio_streams)} audio streams.")
        
        video_streams.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
        
        return {
            'title': info.get('title', url),
            'video_streams': video_streams,
            'audio_streams': audio_streams
        }
            
    except Exception as e:
        logger.error(f"Stream extraction failed: {e}", exc_info=True)
        return None