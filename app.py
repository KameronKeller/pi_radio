from flask import Flask, render_template, request, jsonify
import subprocess
import json
import sqlite3


app = Flask(__name__)
current_process = None
current_url = None

def init_db():
    conn = sqlite3.connect('radio_stations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations
                 (id INTEGER PRIMARY KEY, url TEXT, station_name TEXT)''')
    conn.commit()
    conn.close()

def fetch_metadata(url):
    try:
        command = [
            "ffprobe", "-i", url,
            "-show_entries", "format_tags=icy-name,icy-genre,icy-url,StreamTitle",
            "-v", "quiet", "-of", "json"
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        metadata = result.stdout.decode('utf-8').strip()
        
        if metadata:
            metadata_dict = {}
            try:
                metadata_json = json.loads(metadata)
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

def save_station(url, station_name):
    conn = sqlite3.connect('radio_stations.db')
    c = conn.cursor()
    c.execute("INSERT INTO stations (url, station_name) VALUES (?, ?)", (url, station_name))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST'])
def play():
    global current_process, current_url
    url = request.form['url']
    stop()
    current_url = url
    metadata = fetch_metadata(url)
    station_name = metadata.get('station_name', 'Unknown')
    save_station(url, station_name)
    current_process = subprocess.Popen(['omxplayer', url], stdin=subprocess.PIPE)
    return "", 204

@app.route('/pause', methods=['POST'])
def pause():
    if current_process:
        current_process.stdin.write(b'p')
        current_process.stdin.flush()
    return "", 204

@app.route('/stop', methods=['POST'])
def stop():
    global current_process, current_url
    if current_process:
        current_process.stdin.write(b'q')
        current_process.stdin.flush()
        current_process.terminate()
        current_process = None
        current_url = None
    return "", 204

@app.route('/metadata', methods=['GET'])
def metadata():
    if current_url:
        metadata = fetch_metadata(current_url)
        return jsonify(metadata)
    return jsonify({"error": "No stream is currently playing"})

@app.route('/stations', methods=['GET'])
def stations():
    conn = sqlite3.connect('radio_stations.db')
    c = conn.cursor()
    c.execute("SELECT id, url, station_name FROM stations")
    stations = c.fetchall()
    conn.close()
    return jsonify(stations)

@app.route('/play_station/<int:station_id>', methods=['POST'])
def play_station(station_id):
    global current_process, current_url
    conn = sqlite3.connect('radio_stations.db')
    c = conn.cursor()
    c.execute("SELECT url FROM stations WHERE id = ?", (station_id,))
    station = c.fetchone()
    conn.close()
    if station:
        url = station[0]
        stop()
        current_url = url
        current_process = subprocess.Popen(['omxplayer', url], stdin=subprocess.PIPE)
        return "Playing " + url
    return "Station not found", 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)