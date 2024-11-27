from flask import Flask, render_template, request, jsonify
import subprocess
import json  # Add this import for JSON handling

app = Flask(__name__)
current_process = None  # To track the OMXPlayer process
current_url = None  # To store the current stream URL


def fetch_metadata(url):
    """
    Fetch metadata from the internet radio stream using ffprobe.
    """
    try:
        # Run ffprobe to get metadata from the stream
        command = [
            "ffprobe", "-i", url,
            "-show_entries", "format_tags=icy-name,icy-genre,icy-url,StreamTitle",
            "-v", "quiet", "-of", "json"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        metadata = result.stdout.decode('utf-8').strip()
        
        if metadata:
            # Extract relevant metadata fields from the JSON output
            metadata_dict = {}
            try:
                metadata_json = json.loads(metadata)  # Parse the JSON response
                format_tags = metadata_json.get("format", {}).get("tags", {})
                metadata_dict['station_name'] = format_tags.get('icy-name', 'Unknown')
                metadata_dict['genre'] = format_tags.get('icy-genre', 'Unknown')
                metadata_dict['url'] = format_tags.get('icy-url', 'Unknown')
                metadata_dict['track_title'] = format_tags.get('StreamTitle', 'Unknown')
            except Exception as e:
                metadata_dict = {'error': f"Error parsing metadata: {e}"}
            
            return metadata_dict
        else:
            return {'error': 'No metadata available'}
    except Exception as e:
        return {'error': f"Error fetching metadata: {e}"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
    global current_process, current_url
    url = request.form['url']
    stop()  # Stop any currently playing process
    current_url = url
    current_process = subprocess.Popen(['omxplayer', url], stdin=subprocess.PIPE)
    return "", 204


@app.route('/pause', methods=['POST'])
def pause():
    if current_process:
        current_process.stdin.write(b'p')  # Send 'p' to toggle pause
        current_process.stdin.flush()
    return "", 204


@app.route('/stop', methods=['POST'])
def stop():
    global current_process, current_url
    if current_process:
        current_process.stdin.write(b'q')  # Send 'q' to stop OMXPlayer
        current_process.stdin.flush()
        current_process.terminate()
        current_process = None
        current_url = None
    return "", 204


@app.route('/metadata', methods=['GET'])
def metadata():
    """
    Fetch and return metadata for the currently playing stream.
    """
    if current_url:
        metadata = fetch_metadata(current_url)
        return jsonify(metadata)
    return jsonify({"error": "No stream is currently playing"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

