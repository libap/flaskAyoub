from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Nécessaire pour utiliser les sessions




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

@app.route('/homepage')
def homepage():
    if 'points' not in session:
        session['points'] = 0
    if 'used_questions' not in session:
        session['used_questions'] = []
        
    scorefinal = session['scorefinal']
        
    return render_template('homepage.html', scorefinal=scorefinal)



@app.route('/game')
def quiz():
    if 'used_questions' not in session:
        session['used_questions'] = []

    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()

    # Récupérer tous les IDs de questions disponibles
    cursor.execute('SELECT id FROM questions')
    all_question_ids = [row[0] for row in cursor.fetchall()]

    # Filtrer ceux déjà utilisés
    available_questions = [q_id for q_id in all_question_ids if q_id not in session['used_questions']]

    if not available_questions:
        # Si toutes les questions ont été utilisées, vous pourriez rediriger l'utilisateur ou afficher un message
        user_id = session['user_id']
        points = session['points']
        
        db = sqlite3.connect('quiz_app.db')
        cursor = db.cursor()
        
        # Ici, vous pourriez vouloir mettre à jour le score seulement s'il est supérieur au meilleur score précédent
        cursor.execute('SELECT best_score FROM users WHERE id = ?', (user_id,))
        best_score = cursor.fetchone()[0]
        
        if points > best_score:
            cursor.execute('UPDATE users SET best_score = ? WHERE id = ?', (points, user_id))
            db.commit()
        
        db.close()

        scorefinal = session['scorefinal']
        session['scorefinal'] = session['points']
        if 'points' in session:
            session['points'] = 0
        if 'used_questions'  in session:
            session['used_questions'] = []
        
        return render_template('homepage.html')

    # Choisir un ID au hasard parmi ceux restants
    question_id = random.choice(available_questions)
    session['used_questions'].append(question_id)
    session.modified = True  # Assurez-vous de marquer la session comme modifiée

    # Récupérer la question sélectionnée et ses réponses
    cursor.execute('SELECT question_text FROM questions WHERE id = ?', (question_id,))
    question_text = cursor.fetchone()[0]
    
    cursor.execute('SELECT id, answer_text FROM answers WHERE question_id = ?', (question_id,))
    answers = cursor.fetchall()
    
    db.close()
    
    return render_template('game.html', question=question_text, answers=answers)

@app.route('/checkanswer', methods=['POST'])
def check_answer():
    selected_answer = request.form.get('answer')



    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()
    # Modifier la requête pour récupérer aussi l'ID de la question
    cursor.execute('SELECT is_correct, question_id FROM answers WHERE id = ?', (selected_answer,))
    result = cursor.fetchone()
    db.close()

    if result:
        question_id = result[1]  # Récupérer l'ID de la question
        if question_id not in session['used_questions']:
            session['used_questions'].append(question_id)
            session.modified = True  # Important pour les modifications de list/dict dans session

        if result[0] == 1:  # Si la réponse est correcte
            session['points'] += 1  # Ajouter un point
            return render_template('goodresult.html')
        else:
            return render_template('badresult.html')
    else:
        # Gérer le cas où la requête ne retourne pas de résultat (p. ex., réponse invalide)
        return "Erreur : Réponse non trouvée."





@app.route('/goodresult')
def goodresult():
    return render_template('goodresult.html')

@app.route('/badresult')
def badresult():
    return render_template('badresult.html')

@app.route('/leaderboard')
def leaderboard():
    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()
    cursor.execute('SELECT pseudo, best_score FROM users ORDER BY best_score DESC LIMIT 5')
    leaderboard_data = cursor.fetchall()
    db.close()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)



@app.route('/finalresults')
def finalresults():
    return render_template('finalresults.html')








@app.route('/logout')
def logout():
    session.clear()
    return render_template('landing.html')


@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Dans un cas réel, vous devriez hasher ce mot de passe avant de le stocker
        db = sqlite3.connect('quiz_app.db')
        cursor = db.cursor()
        
        # Insérer le nouvel utilisateur
        cursor.execute('INSERT INTO users (pseudo, password) VALUES (?, ?)', (username, password))
        db.commit()
        
        # Récupérer l'ID du nouvel utilisateur
        cursor.execute('SELECT id FROM users WHERE pseudo = ?', (username,))
        user_id = cursor.fetchone()[0]
        
        db.close()
        
        # Stocker l'ID de l'utilisateur dans la session
        session['user_id'] = user_id
        
        return redirect(url_for('homepage'))
    else:
        return render_template('landing.html')  # Afficher le formulaire d'inscription




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = sqlite3.connect('quiz_app.db')
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE pseudo = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        db.close()
        
        if user:
            session['user_id'] = user[0]  # Utiliser l'ID de l'utilisateur pour la session
            return redirect(url_for('homepage'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'error')
    # Si la méthode n'est pas POST ou si la connexion échoue, afficher à nouveau le formulaire
    return render_template('landing.html')


if __name__ == '__main__':
    app.run(debug=True)
