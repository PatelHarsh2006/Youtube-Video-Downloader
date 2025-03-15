from flask import Flask, render_template, request, send_from_directory
import yt_dlp as ytdl
import os
import threading

global sequence_counter
sequence_counter = 1

def download_video(video_url, download_folder):
    global sequence_counter
    ydl_opts = {
        'format': 'bestvideo[height=1080]+bestaudio/best',
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-c', 'copy'],
        'outtmpl': os.path.join(download_folder, f'# {sequence_counter} - %(title)s.%(ext)s'),
    }
    with ytdl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    sequence_counter += 1

def download_playlist_sequentially(playlist_url, download_folder):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False
    }
    with ytdl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        video_urls = [entry['url'] for entry in info['entries']]
    
    for video_url in video_urls:
        download_video(video_url, download_folder)

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    
    if 'playlist' in video_url:
        threading.Thread(target=download_playlist_sequentially, args=(video_url, DOWNLOAD_FOLDER)).start()
    else:
        threading.Thread(target=download_video, args=(video_url, DOWNLOAD_FOLDER)).start()
    
    return "Download started! Check the downloads folder."

if __name__ == '__main__':
    app.run(debug=True)
