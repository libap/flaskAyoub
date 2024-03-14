from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def init_db():
    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()

    # Création des tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT NOT NULL,
            password TEXT NOT NULL,
            best_score INTEGER DEFAULT 0
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            answer_text TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        );
    ''')

    # Insertion de données d'exemple

    # Utilisateurs
    users = [
        ('Alice', 'password123', 10),
        ('Bob', 'securepwd', 20),
        ('Charlie', 'qwerty', 15)
    ]
    cursor.executemany('INSERT INTO users (pseudo, password, best_score) VALUES (?, ?, ?)', users)

    # Questions
    questions = [
        ("Quelle est la capitale de la France ?",),
        ("Combien de continents y a-t-il ?",),
        ("Qui a peint la Joconde ?",)
    ]
    cursor.executemany('INSERT INTO questions (question_text) VALUES (?)', questions)

    # Récupérer les IDs des questions insérées pour les utiliser dans les réponses
    cursor.execute('SELECT id FROM questions')
    question_ids = cursor.fetchall()

    # Réponses
    # Assurez-vous que les question_id correspondent aux ID réels des questions que vous avez insérées
    answers = [
        (question_ids[0][0], "Paris", True),
        (question_ids[0][0], "Lyon", False),
        (question_ids[0][0], "Marseille", False),
        (question_ids[0][0], "Bordeaux", False),
        (question_ids[1][0], "5", False),
        (question_ids[1][0], "6", False),
        (question_ids[1][0], "7", True),
        (question_ids[1][0], "8", False),
        (question_ids[2][0], "Leonardo da Vinci", True),
        (question_ids[2][0], "Vincent Van Gogh", False),
        (question_ids[2][0], "Pablo Picasso", False),
        (question_ids[2][0], "Claude Monet", False)
    ]
    cursor.executemany('INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)', answers)

    db.commit()
    db.close()

@app.route('/initdb', methods=['GET'])
def create_db():
    try:
        init_db()
        return "La base de données a été initialisée avec succès."
    except Exception as e:
        return str(e)


@app.route('/')
def hello_world():
    return render_template('landing.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/goodresult')
def goodresult():
    return render_template('goodresult.html')

@app.route('/badresult')
def badresult():
    return render_template('badresult.html')

@app.route('/finalresults')
def finalresults():
    return render_template('finalresults.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/logout')
def logout():
    return render_template('landing.html')

@app.route('/createaccount')
def createaccount():
    return render_template('game.html')

@app.route('/login')
def createaccount():
    return render_template('game.html')




if __name__ == '__main__':
    app.run(debug=True)
