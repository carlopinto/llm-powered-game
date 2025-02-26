""""""
from flask import (
    Blueprint, render_template, request, jsonify, session)

from llm_generation import *

bp = Blueprint('llmgame', __name__)

@bp.route('/')
def index():
    """Root endpoint"""
    return render_template('index.html')


@bp.route('/error/<msg>')
def error(msg="error"):
    """Error endpoint"""
    return render_template('error.html',
                           errorMessage=msg)


@bp.route('/game_over')
def game_over():
    """Endpoint to show the last message to users"""
    init_session_variables()
    if not session['end']:
        return render_template('milestone.html', question=session['index'])
    return render_template('gameover.html')


@bp.route('/welcome', methods=('GET', 'POST'))
def welcome():
    """Endpoint to show the list of topics
    for the first question"""
    if request.method == 'POST':
        name = request.form['name']
        # set default name if none is given
        if not name:
            name = 'Player'
        init_session_variables()
        session['name'] = name
        # generate new topics and store them in session object
        session['topics'] = generate_topics()
        if session['topics'] is None:
            return render_template('error.html', 
                                errorMessage="AI model is offline! Try again later.")

        return render_template('main.html',
                               name=session['name'],
                               topics=session['topics'])
    
    return render_template('welcome.html')


def init_session_variables():
    """Init/Reset session variables"""
    # Name of the player
    session['name'] = None
    # Question index
    session['index'] = 1
    # Flag set to True when wrong answer is given
    session['end'] = False
    # Topic chosen by player
    session['selectedtopic'] = None
    # Topics shown to the player
    session['topics'] = []
    # Question for the player based on selected topic
    session['question'] = None
    # Correct answer to the question
    session['answer'] = None
    # List of options / possible answers
    session['options'] = []
    # List of answers given by the player
    session['answers'] = []
    # Flags to indicate whether lifelines have been used
    # lifelines can be used only once
    # value will change to 0 when used
    session['lifelines'] = [1, 1, 1, 1]


@bp.route('/surprise', methods=('GET', 'POST'))
def display_surprise():
    """Endpoint to show the random topic"""
    if request.method == 'POST':
        topics = request.get_json()
        topic = generate_random_topic(topics)
        if topic is None:
            return {
                "status": 500,
                "data": "AI model is offline! Try again later."
            }
        session['selectedtopic'] = topic
        return {
            "status": 200,
            "data": topic
        }

    # make sure topics have been genereted in POST request and
    # the player has not seen the question already
    if not session['topics']:
        session['end'] = True
        session['question'] = None
        return render_template('error.html', 
                        errorMessage="That's not how you are supposed to play the game! Try again.")
    else:
        return render_template('surprise.html', 
                           topic=session['selectedtopic']) 


@bp.route('/question', methods=('GET', 'POST'))
def display_question():
    """Endpoint to show the question to users"""
    if request.method == 'POST':
        selected_topic = request.get_json()
        # Set up the question based on the topic
        session['selectedtopic'] = selected_topic
        # empty list to prevent unapproved behaviours
        session['topics'] = []
        question = None
        attempts = 0
        while question is None and attempts < 3:
            question, options, answer = generate_question(selected_topic)
            if question is None:
                attempts = attempts + 1
                # try one more time
                print("Trying to generate question one more time...")
            if attempts == 3:
                # give up after 3 attempts
                print("Failed to generate question!")
                return {
                    "status": 500,
                    "data": "Failed to generate a question! Try again later."
                }
        session['question'] = question
        session['answer'] = answer
        session['options'] = options
        return {
            "status": 200,
            "data": question
        }

    if session['question'] is None or session['end']:
        return render_template('error.html', 
                                errorMessage="Something went wrong!")
    return render_template('question.html', 
                        question=session['question'], 
                        options=session['options'],
                        current_question=session['index'],
                        lifelines=session['lifelines'])


@bp.route('/topics', methods=('GET', 'POST'))
def next_question():
    """Endpoint to show the list of topics
    for following questions"""
    if session['index'] == 15:
        # You win!
        # TODO replace with something great
        return render_template('winner.html', question=session['index'])
    else:
        if request.method == 'POST':
            # check if a wrong answer has been submitted AND
            # make sure the question index is equal to the number of answers given
            if not session['end'] and session['index'] == len(session['answers']):
                # progress to next question
                session['index'] += 1
                # generate new topics and store them in session object
                session['topics'] = generate_topics()
                if session['topics'] is None:
                    return {
                        "status": 500,
                        "data": "AI model is offline! Try again later."
                    }
                return {
                    "status": 200,
                    "data": session['topics']
                }  
            else:
                # show game over message
                return {
                    "status": 400,
                    "data": "error"
                }     
        else:
            # make sure topics have been genereted in POST request above and stored in session
            if not session['topics']:
                session['end'] = True
                session['question'] = None
                return render_template('error.html', 
                                errorMessage="That's not how you are supposed to play the game! Try again.")
            else:
                return render_template('main.html',
                                    name=session['name'],
                                    topics=session['topics'])


@bp.route('/check_answer', methods=['POST'])
def check_answer():
    """"""
    selected_option = request.form['selected_option']

    session['answers'].append(selected_option)

    if selected_option == session['answer']:
        feedback = "Correct answer!"
        # set to None to prevent the following question
        # to be the same question again
        session['question'] = None
    else:
        feedback = "Wrong! The correct answer is " + session['answer']
        session['end'] = True

    return jsonify({'feedback': feedback, 'answer': session['answer']})

