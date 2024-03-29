""""""
import json
from flask import (
    Blueprint, render_template, request, jsonify, session, redirect, url_for)
from werkzeug.exceptions import abort

from llmgame.ai_request import check_llm_server_status, single_query_llm, single_query_openai

bp = Blueprint('llmgame', __name__)

SYS_MSG = "Act as an AI assistant that is providing content to a A LLM-powered Game \
inspired by 'Who wants to be a millionaire' and more specifically randomly generated questions \
across a vast range of topics."

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
        session['index'] = 1
        
        topics = generate_topics()        

        return render_template('main.html',
                               name=name,
                               topics=topics)
    
    return render_template('welcome.html')


@bp.route('/display_question') 
def display_question():
    selected_topic = request.args.get('selected_topic')
    topics = json.loads(request.args.get('all_topics')) 

    # Set up the question based on the topic
    if selected_topic == "Random":
        selected_topic = generate_random_topic(topics)

    session['topic'] = selected_topic

    question, options, answer = generate_question(selected_topic)
    session['answer'] = answer

    return render_template('question.html', 
                           question=question, 
                           options=options,
                           current_question=session['index']) 


@bp.route('/next', methods=('GET', 'POST'))
def next_question():
    
    session['index'] += 1
    
    topics = generate_topics()        

    return render_template('main.html',
                            name=session['name'],
                            topics=topics)


def generate_topics():
    """Generate a list of 5 topics (plus Random)"""
    # if check_llm_server_status() == 0: # pragma: no cover
    #     return abort(404, 'LLM server is not available.')

    instruction = "Generate 5 different topics for the game. \
Return the single array of 5 topics in JSON format. \
Two examples are: \n\
{ \
\"topics\": [ \
\"History\", \"Science\", \"Movies\", \"Music\", \"Sport\"] \
} \n\
{ \
\"topics\": [ \
\"Politics\", \"Economy\", \"Environment\", \"Computing\", \"Food\"] \
}   "

    sys_msg = SYS_MSG

    llm_response = single_query_openai(instruction, "", sys_msg)
    if llm_response != "" and llm_response is not None:
        # print (llm_response)
        if "topics" in llm_response:
            # from str to python dict
            response_json = json.loads(llm_response)
            # extract list from dict
            topics = response_json['topics']
            # add random topic to list
            topics.append("Random")
            return topics
    
    predef_topics = ["History", "Science", "Movies", "Music", "Sport", "Random"]
    return predef_topics


def generate_random_topic(topics: list):
    """Generate the 6th topic which can be 
    anything but the 5 topics already generated"""
    # if check_llm_server_status() == 0: # pragma: no cover
    #     return abort(404, 'LLM server is not available.')

    instruction = "Generate one random topic for the game. \
Return the single string in JSON format. \
Do not pick any of these topics: " + ' ,'.join(topics) + ". \
Two examples are: \n\
{ \
\"random_topic\": \"History\" \
} \n\
{ \
\"random_topic\": \"Computing\" \
}"

    sys_msg = SYS_MSG

    llm_response = single_query_openai(instruction, "", sys_msg)
    if llm_response != "" and llm_response is not None:
        # print(llm_response)
        if "random_topic" in llm_response:
            # from str to python obj
            response_json = json.loads(llm_response)
            # extract str from dict
            random_topic = response_json['random_topic']
            return random_topic

    predef_random_topic = "Technology"
    return predef_random_topic


def generate_question(topic: str):
    """Generate the 6th topic which can be 
    anything but the 5 topics already generated"""
    # if check_llm_server_status() == 0: # pragma: no cover
    #     return abort(404, 'LLM server is not available.')

    instruction = "Generate one question based on the chosen topic of " + topic + \
"for the game. \
Return the question, four possible options and the correct answer in JSON format. \
Use the given index of the question to come up with questions \
with increasing complexity. Its value can be between 1 and 15; if it is equal to 1, the question \
will be extremely easy and if it is equal to 15, the question will be extremely difficult. \
The index of the question is " + str(session['index']) + \
". Three examples are - listed by increasing difficulty: \n \
{ \
\"question\": \"What is the capital of France?\" \
\"options\": [ \"London\", \"Paris\", \"Rome\", \"Berlin\"] \
\"answer\": \"Paris\" \
} \n\
{ \
\"question\": \"Traditionally, mozzarella cheese is made from the milk of which Animal?\" \
\"options\": [ \"Sheep\", \"Goat\", \"Moose\", \"Buffalo\"] \
\"answer\": \"Buffalo\" \
} \n\
\"question\": \"Complete the title of the musical by Andrew Lloyd Webber, ‘Tell Me On A …’?\" \
\"options\": [ \"Sunday\", \"Monday\", \"Tuesday\", \"Friday\"] \
\"answer\": \"Sunday\" \
}"

    sys_msg = SYS_MSG

    llm_response = single_query_openai(instruction, "", sys_msg)
    if llm_response != "" and llm_response is not None:
        # print(llm_response)
        if "question" in llm_response and "options" in llm_response and "answer" in llm_response:
            # from str to python obj
            response_json = json.loads(llm_response)
            # extract data from dict
            question = response_json['question']
            options = response_json['options']
            answer = response_json['answer']
            print(question)
            print(answer)
            
            return question, options, answer

    # for testing purposes
    # question = "Placeholder: What is the capital of France?" 
    # options = ["London", "Paris", "Berlin", "Rome"]  
    # answer = "Paris" 
    # return question, options, answer

    error = "Failed to generate a question"
    return abort(404, error)

@bp.route('/check_answer', methods=['POST'])
def check_answer():
    """"""
    selected_option = request.form['selected_option']

    if selected_option == session['answer']:
        feedback = "Correct answer!"
    else:
        feedback = "Wrong! The correct answer is " + session['answer']

    return jsonify({'feedback': feedback, 'answer': session['answer']})

