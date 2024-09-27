# app.py

from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secure_random_secret_key'  # Replace with a secure random key

def get_hint(word, category):
    # Provide category-specific hints
    if category.lower() == 'animals':
        return f"It's an animal that starts with '{word[0]}'."
    elif category.lower() == 'fruits':
        return f"It's a fruit that starts with '{word[0]}'."
    elif category.lower() == 'countries':
        return f"It's a country that starts with '{word[0]}'."
    elif category.lower() == 'sports':
        return f"It's a sport that starts with '{word[0]}'."
    elif category.lower() == 'colors':
        return f"It's a color that starts with '{word[0]}'."
    else:
        # Default hint
        return f"The word starts with '{word[0]}' and has {len(word)} letters."

@app.route('/', methods=['GET', 'POST'])
def select_category():
    # Get the list of categories from the 'words' directory
    categories = [filename[:-4] for filename in os.listdir('words') if filename.endswith('.txt')]

    if request.method == 'POST':
        category = request.form['category']
        difficulty = request.form['difficulty']
        session.clear()
        session['category'] = category
        session['difficulty'] = difficulty
        return redirect(url_for('play_game'))
    else:
        return render_template('select_category.html', categories=categories)

@app.route('/play', methods=['GET', 'POST'])
def play_game():
    if 'category' not in session or 'difficulty' not in session:
        return redirect(url_for('select_category'))

    category = session['category']
    difficulty = session['difficulty']
    total_rounds = 5  # Number of rounds per game

    # Load words from the selected category file
    words_file = os.path.join('words', f'{category}.txt')
    try:
        with open(words_file, 'r') as f:
            word_list = [line.strip().lower() for line in f if line.strip().isalpha()]
    except FileNotFoundError:
        return "Category not found.", 404

    # Filter words based on difficulty
    if difficulty == 'easy':
        filtered_words = [word for word in word_list if 4 <= len(word) <= 6]
    elif difficulty == 'medium':
        filtered_words = [word for word in word_list if 7 <= len(word) <= 8]
    elif difficulty == 'hard':
        filtered_words = [word for word in word_list if len(word) > 8]
    else:
        return redirect(url_for('select_category'))

    if not filtered_words:
        return "No words available for the selected category and difficulty.", 404

    if 'round' not in session:
        # Initialize game session variables
        session['round'] = 1
        session['score'] = 0
        session['words'] = random.sample(filtered_words, min(total_rounds, len(filtered_words)))

    round_num = session['round']
    score = session['score']
    words = session['words']
    total_rounds = len(words)

    if request.method == 'POST':
        user_guess = request.form['guess'].strip().lower()
        original_word = session.get('original_word', '')

        if user_guess == original_word:
            session['score'] += 1  # Increment score
            message = 'Correct! Well done!'
        else:
            message = f'Incorrect! The correct word was "{original_word}".'

        # Move to next round
        session['round'] += 1

        # Check if game is complete
        if session['round'] > total_rounds:
            # Game completed
            # Determine stars earned
            if session['score'] == total_rounds:
                stars = 3
            elif session['score'] >= total_rounds * 0.7:
                stars = 2
            elif session['score'] >= total_rounds * 0.4:
                stars = 1
            else:
                stars = 0

            return render_template(
                'game_complete.html',
                category=category.capitalize(),
                difficulty=difficulty.capitalize(),
                stars=stars,
                total_rounds=total_rounds,
                score=session['score']
            )
        else:
            # Continue to next round
            return render_template(
                'feedback.html',
                message=message,
                category=category.capitalize(),
                difficulty=difficulty.capitalize(),
                round_num=session['round'],
                score=session['score'],
                total_rounds=total_rounds
            )
    else:
        # Generate a new word
        if round_num - 1 < len(words):
            original_word = words[round_num - 1]
            scrambled_word = ''.join(random.sample(original_word, len(original_word)))
            hint = get_hint(original_word, category)

            # Store the word and hint in session
            session['original_word'] = original_word
            session['scrambled_word'] = scrambled_word
            session['hint'] = hint

            return render_template(
                'index.html',
                scrambled_word=scrambled_word,
                hint=hint,
                category=category.capitalize(),
                difficulty=difficulty.capitalize(),
                round_num=round_num,
                score=score,
                total_rounds=total_rounds
            )
        else:
            return redirect(url_for('game_complete'))

@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('select_category'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
