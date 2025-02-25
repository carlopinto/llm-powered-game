import random
from flask import (
    Blueprint, render_template, request, jsonify, session, redirect, Response, url_for)


bp = Blueprint('lifelines', __name__, url_prefix='/lifeline')


@bp.route('/remove_options', methods=['POST'])
def remove_options():
    """"""
    incorrect_answers = remove_two_answers(session['options'], session['answer'])

    # update lifeline flag
    session['lifelines'][0] = 0
    session.modified = True
        
    return jsonify({'first': incorrect_answers[0], 'second': incorrect_answers[1]})


@bp.route('/flip_question', methods=['POST'])
def flip_question():
    """"""
    # update lifeline flag
    session['lifelines'][1] = 0
    session.modified = True
    
    return jsonify({'prevAnswer': session['answer'], 'topic': session['selectedtopic']})


@bp.route('/ask_host', methods=['POST'])
def ask_host():
    """"""
    hint = ""

    # update lifeline flag
    session['lifelines'][2] = 0
    session.modified = True
    
    return jsonify({'hint': hint})


@bp.route('/ask_audience', methods=['POST'])
def ask_audience():
    """"""
    hint = ""

    # update lifeline flag
    session['lifelines'][3] = 0
    session.modified = True
    
    return jsonify({'hint': hint})


def remove_two_answers(options, answer):
    """
    Selects two random incorrect answers from a list of options.

    Args:
        options: A list of all possible options.
        answer: The correct answer among the options.

    Returns:
        A list containing two randomly selected incorrect answers.
    """
    
    incorrect_answers = []
    while len(incorrect_answers) < 2:
        incorrect_answer = random.choice(options)
        if incorrect_answer != answer and incorrect_answer not in incorrect_answers:
            incorrect_answers.append(incorrect_answer)

    return incorrect_answers    
    
