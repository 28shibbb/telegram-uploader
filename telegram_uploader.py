import asyncio
import os
import re
from pathlib import Path
import yt_dlp
from telegram import Bot
from telegram.error import TelegramError
import logging
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramVideoUploader:
    def __init__(self, bot_token, channel_id, links_file, download_dir="downloads"):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.links_file = links_file
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Track uploaded files
        self.uploaded_log = Path("uploaded_videos.txt")
        self.uploaded_videos = self.load_uploaded_videos()
        
    def load_uploaded_videos(self):
        if self.uploaded_log.exists():
            with open(self.uploaded_log, 'r') as f:
                return set(line.strip() for line in f)
        return set()
    
    def mark_as_uploaded(self, video_url):
        with open(self.uploaded_log, 'a') as f:
            f.write(f"{video_url}\n")
        self.uploaded_videos.add(video_url)
    
    def parse_links_file(self):
        videos = []
        
        with open(self.links_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match filename and URL
        pattern = r'([^:]+?):\s*(https?://[^\s]+)'
        matches = re.findall(pattern, content)
        
        for filename, url in matches:
            filename = filename.strip()
            url = url.strip()
            
            if url in self.uploaded_videos:
                logger.info(f"Skipping already uploaded: {filename}")
                continue
            
            # Generate safe filename
            safe_filename = re.sub(r'[<>:"/\\|?*]', '', filename)
            safe_filename = safe_filename.replace(' ', '_')[:100]
            
            videos.append({
                'filename': filename,
                'url': url,
                'safe_filename': safe_filename
            })
        
        return videos
    
    def download_video(self, video_info):
        url = video_info['url']
        safe_filename = video_info['safe_filename']
        
        # Skip YouTube embeds
        if 'youtube.com/embed' in url or 'youtu.be' in url:
            logger.info(f"Skipping YouTube embed: {url}")
            return None
        
        output_path = self.download_dir / f"{safe_filename}.mp4"
        
        if output_path.exists():
            logger.info(f"File already downloaded: {output_path}")
            return output_path
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(output_path),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'nooverwrites': True,
            'continuedl': True,
            'retries': 10,
            'fragment_retries': 10,
        }
        
        try:
            logger.info(f"Downloading: {video_info['filename']}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if output_path.exists():
                logger.info(f"Downloaded: {output_path}")
                return output_path
            return None
                
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return None
    
    async def upload_to_telegram(self, video_path, video_info):
        try:
            file_size = video_path.stat().st_size / (1024 * 1024)
            
            if file_size > 2000:  # 2GB limit
                logger.error(f"File too large ({file_size:.2f} MB): {video_path}")
                return False
            
            caption = video_info['filename']
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            logger.info(f"Uploading: {caption}")
            
            with open(video_path, 'rb') as video_file:
                await self.bot.send_video(
                    chat_id=self.channel_id,
                    video=video_file,
                    caption=caption,
                    supports_streaming=True,
                    read_timeout=300,
                    write_timeout=300
                )
            
            logger.info(f"Uploaded successfully: {caption}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading {video_path}: {str(e)}")
            return False
    
    async def process_videos(self, delay_between_uploads=10):
        videos = self.parse_links_file()
        
        if not videos:
            logger.info("No new videos to process")
            return
        
        logger.info(f"Found {len(videos)} videos to process")
        
        for i, video in enumerate(videos, 1):
            logger.info(f"Processing {i}/{len(videos)}: {video['filename']}")
            
            video_path = self.download_video(video)
            
            if video_path and video_path.exists():
                success = await self.upload_to_telegram(video_path, video)
                
                if success:
                    self.mark_as_uploaded(video['url'])
                    # Optional: Delete file after upload
                    # video_path.unlink()
                    
                    logger.info(f"Waiting {delay_between_uploads} seconds...")
                    await asyncio.sleep(delay_between_uploads)
                else:
                    logger.error(f"Failed to upload: {video['filename']}")
            else:
                logger.error(f"Failed to download: {video['filename']}")
        
        logger.info("All videos processed!")

async def main():
    # Get configuration from environment variables
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    LINKS_FILE = "links.txt"
    DOWNLOAD_DIR = "downloads"
    
    if not BOT_TOKEN or not CHANNEL_ID:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables")
        logger.error("Create a .env file or set them manually")
        return
    
    uploader = TelegramVideoUploader(
        bot_token=BOT_TOKEN,
        channel_id=CHANNEL_ID,
        links_file=LINKS_FILE,
        download_dir=DOWNLOAD_DIR
    )
    
    await uploader.process_videos(delay_between_uploads=15)

if __name__ == "__main__":
    asyncio.run(main())
