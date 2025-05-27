from flask import Flask, render_template, request
import re
from sympy import symbols, Eq, solve, pretty
import wikipedia
from difflib import SequenceMatcher
import re

def simple_sentence_split(text):
    return [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]

def compare_explanation_with_wikipedia(user_input, wiki_summary):
    user_sentences = simple_sentence_split(user_input.lower())
    wiki_sentences = simple_sentence_split(wiki_summary.lower())

    correct = []
    missed = []
    elaborate = []

    for ws in wiki_sentences:
        match_found = False
        for us in user_sentences:
            similarity = SequenceMatcher(None, us, ws).ratio()
            if similarity > 0.7:
                correct.append(ws)
                match_found = True
                break
            elif 0.4 < similarity <= 0.7:
                elaborate.append(ws)
                match_found = True
                break
        if not match_found:
            missed.append(ws)

    return {
        "correct": correct,
        "missed": missed,
        "elaborate": elaborate
    }
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')



    # Wikipedia summary (cleaned and more accurate)
@app.route('/submit', methods=['POST'])
def submit():
    topic = request.form['topic'].strip()
    explanation = request.form['explanation'].strip()

    wikipedia.set_lang("en")

    # Try to get a Wikipedia summary
    try:
        try:
            wiki_summary = wikipedia.summary(topic, sentences=5)
        except wikipedia.exceptions.DisambiguationError as e:
            wiki_summary = wikipedia.summary(e.options[0], sentences=5)
        except wikipedia.exceptions.PageError:
            search_results = wikipedia.search(topic)
            if search_results:
                wiki_summary = wikipedia.summary(search_results[0], sentences=5)
            else:
                wiki_summary = f"No Wikipedia page found for '{topic}'."
        comparison = compare_explanation_with_wikipedia(explanation, wiki_summary)
    except Exception as e:
        wiki_summary = f"Could not fetch Wikipedia info for '{topic}'. Error: {e}"

    # Split Wikipedia summary into simple bullet points
    wiki_points = [point.strip() for point in wiki_summary.split('.') if len(point.strip()) > 15]

    # Tokenize user explanation (lowercased)
    explanation_lower = explanation.lower()
    correct_points = []
    missing_points = []
    elaboration_points = []

    for point in wiki_points:
        simplified = point.lower()
        if simplified in explanation_lower or any(word in explanation_lower for word in simplified.split()[:3]):
            correct_points.append(point)
        elif any(word in explanation_lower for word in simplified.split()):
            elaboration_points.append(point)
        else:
            missing_points.append(point)

    # Feedback
    if len(correct_points) >= 2:
        feedback = "Great job! You're covering the core ideas well. Try to add even more depth next time!"
    elif len(correct_points) >= 1:
        feedback = "Nice start! You're on the right track. Try expanding your explanation further."
    else:
        feedback = "Keep going! Try to include more key ideas about this topic."

    print("Comparison:", comparison)
    print("Explanation:", explanation)
    print("Wiki summary:", wiki_summary)



    print("Type of comparison:", type(comparison))

    return render_template('result.html', topic=topic, explanation=explanation, wiki_summary=wiki_summary, feedback=feedback, comparison=comparison)



if __name__ == '__main__':
    app.run(debug=True)
