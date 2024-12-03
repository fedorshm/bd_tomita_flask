import pandas as pd
import subprocess
import os
from bs4 import BeautifulSoup
import psycopg2
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()
embedding = NewsEmbedding()
morph_tagger = NewsMorphTagger(embedding)

db_params = {
    "dbname": "tomitabdd",
    "user": "postgres",
    "password": "toor",
    "host": "db",
    "port": "5432"
}

csv_file_path = '/usr/src/app/news_15.csv'
config_file_path = '/usr/src/app/config.proto'
tomita_binary_path = '/usr/src/app/tomitaparser'
output_html_path = '/usr/src/app/templates/pretty.html'
temp_input_path = '/usr/src/app/temp_input.txt'

df = pd.read_csv(csv_file_path)

try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    for index, row in df.iterrows():
        text = row['text']
        
        cursor.execute("""
            INSERT INTO "Text" ("Text")
            VALUES (%s)
            RETURNING "IDText";
        """, (text,))
        id_text = cursor.fetchone()[0]

        with open(temp_input_path, 'w', encoding='utf8') as f:
            f.write(text)
        #runim tomitu
        subprocess.run([tomita_binary_path, config_file_path],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        with open(output_html_path, encoding="utf-8") as file:
            soup = BeautifulSoup(file, 'html.parser')
            tables = pd.read_html(str(soup))
        
        table = tables[0] if tables else pd.DataFrame()

        for _, row in table.iterrows():
            phrase_data = row['Text']
            
            cursor.execute("""
                INSERT INTO "Phrases" ("IDText", "Phrase")
                VALUES (%s, %s)
                RETURNING "IDPhrase";
            """, (id_text, phrase_data))
            id_phrase = cursor.fetchone()[0]

            doc = Doc(phrase_data)
            doc.segment(segmenter)
            doc.tag_morph(morph_tagger)
            
            for token in doc.tokens:
                token.lemmatize(morph_vocab)
                word_data = token.text
                lemmatized_data = token.lemma
                pos_tag = token.pos

                cursor.execute("""
                    INSERT INTO "Ngram" ("Word", "IDText")
                    VALUES (%s, %s)
                    RETURNING "IDWord";
                """, (word_data, id_text))
                id_word = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO "Lem" ("Lem", "PoS", "IDWord", "IDText")
                    VALUES (%s, %s, %s, %s);
                """, (lemmatized_data, pos_tag, id_word, id_text))

    conn.commit()
    print("Uspeh.")

except Exception as e:
    print("Error:", e)
finally:
    if conn:
        cursor.close()
        conn.close()


