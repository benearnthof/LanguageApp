import random
from flask import Flask, render_template, request, jsonify
import sqlite3
import csv

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('vocabulary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS words
                 (id INTEGER PRIMARY KEY, french TEXT, english TEXT, times_queried INTEGER, score INTEGER)''')
    conn.commit()
    conn.close()

def populate_db():
    # TODO: Adjust to include synonyms & Phrases
    conn = sqlite3.connect('vocabulary.db')
    c = conn.cursor()
    with open('french_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            c.execute("INSERT OR IGNORE INTO words (french, english, times_queried, score) VALUES (?, ?, 0, 0)",
                      (row[0], row[1]))
    conn.commit()
    conn.close()

init_db()
populate_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_word')
def get_word():
    conn = sqlite3.connect('vocabulary.db')
    c = conn.cursor()
    c.execute("SELECT id, french FROM words ORDER BY RANDOM() LIMIT 1")
    word = c.fetchone()
    conn.close()
    return jsonify({'id': word[0], 'french': word[1]})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    # TODO: Adjust to check for synonyms from parser
    word_id = request.form['id']
    user_answer = request.form['answer']
    
    conn = sqlite3.connect('vocabulary.db')
    c = conn.cursor()
    c.execute("SELECT english FROM words WHERE id = ?", (word_id,))
    correct_answer = c.fetchone()[0]
    
    is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
    
    c.execute("UPDATE words SET times_queried = times_queried + 1, score = score + ? WHERE id = ?",
              (1 if is_correct else 0, word_id))
    conn.commit()
    conn.close()
    
    return jsonify({'correct': is_correct, 'answer': correct_answer})

@app.route('/stats')
def stats():
    conn = sqlite3.connect('vocabulary.db')
    c = conn.cursor()
    c.execute("SELECT SUM(score) as total_score, SUM(times_queried) as total_queries FROM words")
    stats = c.fetchone()
    conn.close()
    return jsonify({'total_score': stats[0], 'total_queries': stats[1]})

if __name__ == '__main__':
    app.run(debug=True)