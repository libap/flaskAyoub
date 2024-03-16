-- Création des tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL,
    password TEXT NOT NULL,
    best_score INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY(question_id) REFERENCES questions(id)
);

-- Data insertion for testing

-- Users
INSERT INTO users (pseudo, password, best_score) VALUES 
('Alice', 'password123', 10),
('Bob', 'securepwd', 20),
('Charlie', 'qwerty', 15);

-- Questions
INSERT INTO questions (question_text) VALUES 
('Quelle est la capitale de la France ?'),
('Combien de continents y a-t-il ?'),
('Qui a peint la Joconde ?');

-- Answers
-- Note: The question_ids used here are assumed to correspond to the actual IDs.
-- In a real scenario, make sure the IDs match or adjust them accordingly.
INSERT INTO answers (question_id, answer_text, is_correct) VALUES 
(1, 'Paris', 1),
(1, 'Lyon', 0),
(1, 'Marseille', 0),
(1, 'Bordeaux', 0),
(2, '5', 0),
(2, '6', 0),
(2, '7', 1),
(2, '8', 0),
(3, 'Leonardo da Vinci', 1),
(3, 'Vincent Van Gogh', 0),
(3, 'Pablo Picasso', 0),
(3, 'Claude Monet', 0);
