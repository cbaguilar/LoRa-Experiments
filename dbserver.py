from flask import Flask, request, jsonify, render_template_string
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname='tsdb',
        user='postgres',
        host='127.0.0.1'
    )
    return conn

# Create tables if they do not exist
def create_tables():
    print("Getting db connection...")
    conn = get_db_connection()
    print("got db connection")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS signal_strength (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            value INTEGER NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS packet_message (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

create_tables()

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not all(key in data for key in ('timestamp', 'data_value', 'data_type', 'source_ip')):
        return jsonify({"error": "Missing fields"}), 400

    try:
        timestamp = datetime.fromisoformat(data['timestamp'])
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    data_value = data['data_value']
    data_type = data['data_type']

    conn = get_db_connection()
    cur = conn.cursor()
    if data_type == 'signal_strength':
        cur.execute('INSERT INTO signal_strength (timestamp, value) VALUES (%s, %s)', (timestamp, int(data_value)))
    elif data_type == 'packet_message':
        cur.execute('INSERT INTO packet_message (timestamp, value) VALUES (%s, %s)', (timestamp, data_value))
    else:
        cur.close()
        conn.close()
        return jsonify({"error": "Invalid data type"}), 400

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data received"}), 200

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT timestamp, value FROM signal_strength ORDER BY timestamp DESC LIMIT 100')
    latest_signal_strengths = cur.fetchall()
    cur.execute('SELECT timestamp, value FROM packet_message ORDER BY timestamp DESC LIMIT 100')
    latest_packet_messages = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <!doctype html>
    <html>
    <head><title>Latest Data</title></head>
    <body>
        <h1>Latest Signal Strengths</h1>
        <ul>
            {% for entry in latest_signal_strengths %}
            <li>{{ entry[0] }}: {{ entry[1] }}</li>
            {% endfor %}
        </ul>
        <h1>Latest Packet Messages</h1>
        <ul>
            {% for entry in latest_packet_messages %}
            <li>{{ entry[0] }}: {{ entry[1] }}</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    ''', latest_signal_strengths=latest_signal_strengths, latest_packet_messages=latest_packet_messages)

if __name__ == '__main__':
    print("starting flask app")
    app.run(host="0.0.0.0", port=8080)

