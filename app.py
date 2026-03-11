from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Serve the voting page
@app.route('/')
def vote_page():
    return render_template('vote.html')

# Receive vote submissions
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    token = request.form['token']
    votes = {k: float(v) for k, v in request.form.items() if k != 'token'}

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT used FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Invalid token'})
    if row[0]:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Token already used'})

    columns = ','.join(votes.keys())
    placeholders = ','.join('?' * len(votes))
    values = list(votes.values())
    cur.execute(f"INSERT INTO votes (token,{columns}) VALUES (?,{placeholders})", [token] + values)
    cur.execute("UPDATE tokens SET used=1 WHERE token=?", (token,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Vote submitted successfully!'})

# Calculate votes and averages, keep all votes in CSV, average excludes self
@app.route('/calculate_averages', methods=['GET'])
def calculate_averages():
    conn = sqlite3.connect('database.db')
    votes_df = pd.read_sql_query("SELECT * FROM votes", conn)
    token_mapping = pd.read_sql_query("SELECT token, participant_name FROM tokens", conn)
    conn.close()

    final_data = []

    for idx, row in token_mapping.iterrows():
        participant = row['participant_name']
        token = row['token']

        if participant in votes_df.columns:
            # All votes for CSV
            votes_csv = votes_df[participant].tolist()

            # Remove self-vote only for average calculation
            votes_for_avg = votes_df[participant].copy()
            votes_for_avg.loc[votes_df['token'] == token] = None
            actual_votes = votes_for_avg.dropna().tolist()
            avg = round(sum(actual_votes) / len(actual_votes), 2) if actual_votes else None

            # Pad CSV votes to 8 participants if needed (to always have 8 vote columns)
            votes_csv += [None] * (8 - len(votes_csv))

            final_data.append([participant] + votes_csv + [avg])

    # Columns: Participant + 8 votes + Average
    columns = ['Participant'] + [f'Vote{i+1}' for i in range(8)] + ['Average']
    final_df = pd.DataFrame(final_data, columns=columns)

    # Save CSV
    final_df.to_csv("peer_votes_and_avg.csv", index=False)

    return final_df.to_json()

# Download the CSV
@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        return send_file("peer_votes_and_avg.csv",
                         mimetype="text/csv",
                         download_name="peer_votes_and_avg.csv",
                         as_attachment=True)
    except Exception as e:
        return str(e)

# Run the app with Render port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)