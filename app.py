from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  


def init_db():
    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()

    # Creating tables
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

    # Inserting example data

    # Users
    users = [
        ('Alice', 'password123', 10),
        ('Bob', 'securepwd', 20),
        ('Charlie', 'qwerty', 15)
    ]
    cursor.executemany('INSERT INTO users (pseudo, password, best_score) VALUES (?, ?, ?)', users)

    # Questions
    questions = [
        ("What is the capital of France?",),
        ("How many continents are there?",),
        ("Who painted the Mona Lisa?",)
    ]
    cursor.executemany('INSERT INTO questions (question_text) VALUES (?)', questions)

    # Retrieve the IDs of the inserted questions to use them in the answers
    cursor.execute('SELECT id FROM questions')
    question_ids = cursor.fetchall()

    # Answers
    # Make sure the question_id matches the actual IDs of the questions you inserted
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
        return "The database has been successfully initialized."
    except Exception as e:
        return str(e)
def is_user_logged_in():
    # Checks if 'user_id' is present in the session
    if 'user_id' in session:
        # If the user is logged in
        return True

@app.route('/')
def hello_world():
    return render_template('landing.html')

@app.route('/homepage')
def homepage():
    if not is_user_logged_in():
        print('------------------------------')
        # print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')

    if 'points' not in session:
        session['points'] = 0
    if 'used_questions' not in session:
        session['used_questions'] = []
    session['final_score'] = 0

    return render_template('homepage.html')

@app.route('/game')
def quiz():
    if not is_user_logged_in():
        print('------------------------------')
        # print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')

    if 'used_questions' not in session:
        session['used_questions'] = []

    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()

    # Retrieve all available question IDs
    cursor.execute('SELECT id FROM questions')
    all_question_ids = [row[0] for row in cursor.fetchall()]

    # Filter out those already used
    available_questions = [q_id for q_id in all_question_ids if q_id not in session['used_questions']]

    if not available_questions:
        # If all questions have been used, you could redirect the user or display a message
        user_id = session['user_id']
        points = session['points']
        
        db = sqlite3.connect('quiz_app.db')
        cursor = db.cursor()
        
        # Here, you might want to update the score only if it's higher than the previous best score
        cursor.execute('SELECT best_score FROM users WHERE id = ?', (user_id,))
        best_score = cursor.fetchone()[0]
        
        if points > best_score:
            cursor.execute('UPDATE users SET best_score = ? WHERE id = ?', (points, user_id))
            db.commit()
        
        db.close()


        if 'points' in session:
            session['scorefinal'] = points
            session['points'] = 0
        if 'used_questions'  in session:
            session['used_questions'] = []
        
        return redirect(url_for('finalresults'))

 # Choose a random ID from those remaining
    question_id = random.choice(available_questions)
    session['used_questions'].append(question_id)
    session.modified = True  # Make sure to mark the session as modified

    # Retrieve the selected question and its answers
    cursor.execute('SELECT question_text FROM questions WHERE id = ?', (question_id,))
    question_text = cursor.fetchone()[0]
    
    cursor.execute('SELECT id, answer_text FROM answers WHERE question_id = ?', (question_id,))
    answers = cursor.fetchall()
    
    db.close()
    
    return render_template('game.html', question=question_text, answers=answers)

@app.route('/checkanswer', methods=['POST'])
def check_answer():
    if is_user_logged_in() != True:
        print('------------------------------')
        #print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')

    selected_answer = request.form.get('answer')



    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()
    # Modify the query to also retrieve the question ID
 
    cursor.execute('SELECT is_correct, question_id FROM answers WHERE id = ?', (selected_answer,))
    result = cursor.fetchone()
    db.close()

    if result:
        question_id = result[1]  # Retrieve the question ID
        if question_id not in session['used_questions']:
            session['used_questions'].append(question_id)
            session.modified = True  # Important for modifications to lists/dicts in session

        if result[0] == 1:  # If the answer is correct
            session['points'] += 20  # Add 20 points to the user's score


            return render_template('goodresult.html')
        else:
            return render_template('badresult.html')
    else:
        # Handle the case where the query returns no result (e.g., invalid answer)
        return "Error: Answer not found."
        return "Error: Answer not found."





@app.route('/goodresult')
def goodresult():
    if is_user_logged_in() != True:
        print('------------------------------')
        #print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')

        return render_template('landing.html')
    return render_template('goodresult.html')

@app.route('/badresult')
def badresult():
    if is_user_logged_in() != True:
        print('------------------------------')
        #print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')
    return render_template('badresult.html')

@app.route('/leaderboard')
def leaderboard():
    if is_user_logged_in() != True:
        print('------------------------------')
        #print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')
    db = sqlite3.connect('quiz_app.db')
    cursor = db.cursor()
    cursor.execute('SELECT pseudo, best_score FROM users ORDER BY best_score DESC LIMIT 20')
    leaderboard_data = cursor.fetchall()
    db.close()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)



@app.route('/finalresults')
def finalresults():
    if is_user_logged_in() != True:
        print('------------------------------')
        #print(session['user_id'])
        print('No one is logged in, redirecting to the login page')
        print('------------------------------')
        return render_template('landing.html')

    
    return render_template('finalresults.html', scorefinal=session['scorefinal'])








@app.route('/logout')
def logout():
    is_user_logged_in()
    session.clear()
    return render_template('landing.html')


@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In a real case, you should hash this password before storing it
        db = sqlite3.connect('quiz_app.db')
        cursor = db.cursor()
        
          # Insert new user
        cursor.execute('INSERT INTO users (pseudo, password) VALUES (?, ?)', (username, password))
        db.commit()
        
        # Retrieve new user ID
        cursor.execute('SELECT id FROM users WHERE pseudo = ?', (username,))
        user_id = cursor.fetchone()[0]
        
        db.close()
        
          # Store user ID in session
        session['user_id'] = user_id
        
        return redirect(url_for('homepage'))
    else:
        return render_template('landing.html')  #  Display registration form




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
            session['user_id'] = user[0]  # Use user ID for session
     
            return redirect(url_for('homepage'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect.', 'error')
     # If the method is not POST or if the connection fails, display the form again

    return render_template('landing.html')

if __name__ == '__main__':
    app.run(debug=True)

#Comments

#Launching the program is as simple as running the app.py file.

#To set up the database, visit the /initdb endpoint.

#Then to register or sign in, go directly to the homepage at /.

#Access the /homepage to start playing the game.

#Note: This implementation does not include password hashing or optimal code practices, such as a dedicated function for database connections, clean database creation system with sql file.