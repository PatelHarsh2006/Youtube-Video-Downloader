from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp as ytdl
import os

app = Flask(__name__)

# Directory to save downloaded files temporarily
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# A global counter to keep track of the sequence
sequence_counter = 1


@app.route('/')
def index():
    return render_template('index.html')  # Renders the input form for links


@app.route('/download', methods=['POST'])
def download():
    global sequence_counter  # Access the global counter

    try:
        video_url = request.form['url']

        # yt-dlp configuration
        ydl_opts = {
    'format': 'bestvideo[height=1080]+bestaudio/best',  # Ensures 1080p video
    'merge_output_format': 'mp4',  # Final format
    'postprocessor_args': ['-c', 'copy'],  # Copy streams, no re-encoding
    'outtmpl': os.path.join(
        DOWNLOAD_FOLDER,
        f'# {sequence_counter} - %(title)s.%(ext)s'  # Numbered file name
    ),
}



        # Download video
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'video')  # Get video title
            output_filename = f"# {sequence_counter} - {video_title}.mp4"
            output_filepath = os.path.join(DOWNLOAD_FOLDER, output_filename)

        # Increment the sequence counter for the next video
        sequence_counter += 1

        # Send the file to the browser for download and delete it afterward
        return send_file(output_filepath, as_attachment=True, download_name=output_filename)

    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/clear', methods=['POST'])
def clear_files():
    """Clears temporary files and resets the sequence counter."""
    global sequence_counter
    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    sequence_counter = 1  # Reset the counter
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
