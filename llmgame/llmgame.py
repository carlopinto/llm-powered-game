""""""
from flask import (
    Blueprint, render_template, request, jsonify)

bp = Blueprint('llmgame', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/welcome')
def welcome():
    return render_template('welcome.html')


@bp.route('/get_question', methods=['POST'])
def get_question():
    topic = request.form['topic']

    # Placeholder for your LLM integration to generate a question
    question = "Placeholder: What is the capital of France?" 
    options = ["London", "Paris", "Berlin", "Rome"]  
    answer = "Paris" 

    # Return data as JSON 
    return jsonify({
        "question": question,
        "options": options,
        "answer": answer 
    })

