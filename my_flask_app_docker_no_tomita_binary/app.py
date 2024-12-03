from flask import Flask, render_template, request
import psycopg2
import re

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='tomitabdd',
        user='postgres',
        password='toor',
        host='db',
        port=5432
    )
    return conn

def extract_contexts(text, search_query, window=60):
    contexts = []
    for match in re.finditer(re.escape(search_query), text, re.IGNORECASE):
        start = max(match.start() - window, 0)
        end = min(match.end() + window, len(text))
        context = text[start:end]
        contexts.append((match.group(), context))
    return contexts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search(): 
    results = {'words': [], 'phrases': [], 'texts': [], 'contexts': []}
    if request.method == 'POST':
        search_text = request.form.get('search_text', '').strip()
        pos_tag = request.form.get('pos_tag', '').strip()
        lem = request.form.get('lem', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        
        if search_text:
            cursor.execute("SELECT \"IDText\", \"Text\" FROM \"Text\" WHERE \"Text\" LIKE %s;", (f'%{search_text}%',))
            texts = cursor.fetchall()
            results['texts'] = texts
            # Extract contexts for KWIC
            for text in texts:
                contexts = extract_contexts(text[1], search_text)
                results['contexts'].extend(contexts)

        if pos_tag:
            cursor.execute("""
                SELECT n."Word", l."PoS"
                FROM "Ngram" n
                JOIN "Lem" l ON n."IDWord" = l."IDWord" AND n."IDText" = l."IDText"
                WHERE l."PoS" = %s;
            """, (pos_tag,))
            results['words'] = cursor.fetchall()
            
            cursor.execute("""
                SELECT DISTINCT p."Phrase", t."Text"
                FROM "Phrases" p
                JOIN "Ngram" n ON n."IDText" = p."IDText"
                JOIN "Lem" l ON n."IDWord" = l."IDWord" AND n."IDText" = l."IDText"
                JOIN "Text" t ON t."IDText" = p."IDText"
                WHERE l."PoS" = %s AND n."Word" = ANY(STRING_TO_ARRAY(p."Phrase", ' '));
            """, (pos_tag,))
            results['phrases'] = cursor.fetchall()

        if lem:
            cursor.execute("""
                SELECT DISTINCT p."Phrase", t."Text"
                FROM "Lem" l
                JOIN "Ngram" n ON n."IDWord" = l."IDWord" AND n."IDText" = l."IDText"
                JOIN "Phrases" p ON p."IDText" = n."IDText"
                JOIN "Text" t ON t."IDText" = p."IDText"
                WHERE l."Lem" = %s AND n."Word" = ANY(STRING_TO_ARRAY(p."Phrase", ' '));
            """, (lem,))
            results['texts'].extend(cursor.fetchall())

        conn.close()

    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
