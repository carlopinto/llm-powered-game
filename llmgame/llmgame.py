""""""
from flask import (
    Blueprint, render_template, request, jsonify, session)
from werkzeug.exceptions import abort

from llmgame.ai_request import check_llm_server_status, single_query_llm

bp = Blueprint('llmgame', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/welcome', methods=('GET', 'POST'))
def welcome():
    
    if request.method == 'POST':
        name = request.form['name']

        if not name:
            name = 'Player'
            
        session['name'] = name
        
        # generate topics
        if check_llm_server_status() == 0: # pragma: no cover
            return abort(404, 'LLM server is not available.')

        instruction = "Generate 5 different topics for the game. \
Return the single array of 5 topics in JSON format. \
Two examples are: \n\
{ \
\"topics\": [ \
'History', 'Science', 'Movies', 'Music', 'Sport'] \
} \n\
{ \
\"topics\": [ \
'Politics', 'Economy', 'Environment', 'Computing', 'Food'] \
}   "

        sys_msg = "Act as an AI assistant that is providing content to a A LLM-powered Game \
inspired by 'Who wants to be a millionaire' and more specifically randomly generated questions \
across a vast range of topics."

        llm_response = single_query_llm(instruction, "", sys_msg)
        
        if llm_response != "" and llm_response is not None:
            print (llm_response)
        
        topics = ["History", "Science", "Movies", "Music", "Sport", "Random"]

        return render_template('main.html', name=name, topics=topics)
    
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

