from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

# Serve the voting page
@app.route('/')
def vote_page():
    return render_template('vote.html')

# Receive vote submissions
@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    token = request.form['token']
    votes = {k: float(v) for k,v in request.form.items() if k != 'token'}

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT used FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'status':'error', 'message':'Invalid token'})
    if row[0]:
        conn.close()
        return jsonify({'status':'error', 'message':'Token already used'})

    columns = ','.join(votes.keys())
    placeholders = ','.join('?'*len(votes))
    values = list(votes.values())
    cur.execute(f"INSERT INTO votes (token,{columns}) VALUES (?,{placeholders})", [token]+values)
    cur.execute("UPDATE tokens SET used=1 WHERE token=?", (token,))
    conn.commit()
    conn.close()
    return jsonify({'status':'success', 'message':'Vote submitted successfully!'})

# Calculate averages and remove self-votes
@app.route('/calculate_averages', methods=['GET'])
def calculate_averages():
    conn = sqlite3.connect('database.db')
    votes_df = pd.read_sql_query("SELECT * FROM votes", conn)
    token_mapping = pd.read_sql_query("SELECT token, participant_name FROM tokens", conn)
    conn.close()

    # Remove self-votes
    for idx, row in token_mapping.iterrows():
        participant = row['participant_name']
        token = row['token']
        if participant in votes_df.columns and token in votes_df['token'].values:
            votes_df.loc[votes_df['token']==token, participant] = pd.NA

    votes_df = votes_df.drop(columns=['token'])
    averages = votes_df.mean()
    averages.to_csv("peer_averages.csv", header=True)
    return averages.to_json()

if __name__ == '__main__':
    app.run(debug=True)

from flask import send_file

@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        return send_file("peer_averages.csv",
                         mimetype="text/csv",
                         download_name="peer_averages.csv",
                         as_attachment=True)
    except Exception as e:
        return str(e)