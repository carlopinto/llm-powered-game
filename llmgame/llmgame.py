""""""
import json
from flask import (
    Blueprint, render_template, request, jsonify, session, redirect, url_for)
from werkzeug.exceptions import abort

from llmgame.ai_request import (
    #check_llm_server_status, single_query_llm, 
    #single_query_openai, query_ollama, 
    check_ollama_status, OllamaLLM)

from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException

bp = Blueprint('llmgame', __name__)

OFFLINE = True
# SYS_MSG = "Act as an AI assistant that is providing content to a A LLM-powered Game \
# inspired by 'Who wants to be a millionaire' and more specifically randomly generated questions \
# across a vast range of topics."
RANDOM_LABEL = "Surprise me!"

@bp.route('/')
def index():
    """Root endpoint"""
    return render_template('index.html')


@bp.route('/game_over')
def game_over():
    """Endpoint to show the last message to users"""
    if not session['end']:
        return render_template('milestone.html', question=session['index'])
    return render_template('gameover.html')


@bp.route('/welcome', methods=('GET', 'POST'))
def welcome():
    """Endpoint to show the list of topics
    for the first question"""
    if request.method == 'POST':
        name = request.form['name']

        if not name:
            name = 'Player'
            
        session['name'] = name
        session['index'] = 1
        session['end'] = False
        session['topic'] = None
        session['question'] = None
        session['answer'] = None
        session['options'] = []
        
        topics = generate_topics()        

        return render_template('main.html',
                               name=name,
                               topics=topics)
    
    return render_template('welcome.html')


@bp.route('/surprise', methods=('GET', 'POST'))
def display_surprise():
    """Endpoint to show the random topic"""
    if request.method == 'POST':
        topics = request.get_json()
        topic = generate_random_topic(topics)
        session['topic'] = topic
        return topic

    return render_template('surprise.html', 
                           topic=session['topic']) 


@bp.route('/question', methods=('GET', 'POST'))
def display_question():
    """Endpoint to show the question to users"""
    if request.method == 'POST':
        selected_topic = request.get_json()
        # Set up the question based on the topic
        session['topic'] = selected_topic
        question, options, answer = generate_question(selected_topic)
        if question is None:
            # try one more time
            print("Trying to generate question one more time...")
            question, options, answer = generate_question(selected_topic)
            if question is None:
                # give up
                print("Failed to generate question! Back to index.")
                return redirect(url_for('llmgame.index'))
        session['question'] = question
        session['answer'] = answer
        session['options'] = options
        return question

    if not session['end']:
        if session['question'] is None:
            # something went wrong
            return abort(404, "Something went wrong generating the question.")
        return render_template('question.html', 
                            question=session['question'], 
                            options=session['options'],
                            current_question=session['index'])
    else:
        # show game over message
        return redirect(url_for('llmgame.game_over')) 


@bp.route('/topics', methods=('GET', 'POST'))
def next_question():
    """Endpoint to show the list of topics
    for following questions"""
    session['index'] += 1

    topics = generate_topics()        

    return render_template('main.html',
                            name=session['name'],
                            topics=topics)


def generate_topics():
    """Generate a list of 5 topics (plus Random)"""
    # LM Studio
    # if check_llm_server_status() == 0: # pragma: no cover
    #     return abort(404, 'LLM server is not available.')
    
    # Ollama
    if check_ollama_status() == 0: # pragma: no cover
        return abort(404, 'Ollama is not available.')

    instruction = "Generate 5 different topics for the game"
    
    response_schemas = [
        ResponseSchema(name="topics", description="array of topics completely unrelated")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template="Follow the user's instruction and make sure you are inspired by 'Who wants to be a millionaire'.\n{format_instructions}\n{instruction}",
        input_variables=["instruction"],
        partial_variables={"format_instructions": format_instructions},
    )
    if OFFLINE:
        model = OllamaLLM(model="mistral", temperature=0.8)
    else:
        model = ChatOpenAI(model="gpt-4", temperature=0.8)
    chain = prompt | model | output_parser
    
    llm_response = chain.invoke({"instruction": instruction})
    if llm_response != "" and llm_response is not None:
        print (llm_response)
        if "topics" in llm_response:
            # from str to python dict - no longer needed
            # response_json = json.loads(llm_response)
            # extract list from dict
            topics = llm_response['topics']
            # add random topic to list
            topics.append(RANDOM_LABEL)
            return topics
    
    predef_topics = ["History", "Science", "Movies", "Music", "Sport", RANDOM_LABEL]
    return predef_topics


def generate_random_topic(topics: list):
    """Generate the 6th topic which can be 
    anything but the 5 topics already generated"""
    if check_ollama_status() == 0: # pragma: no cover
        return abort(404, 'Ollama is not available.')
    # remove Random from list
    topics.pop()
    instruction = "Generate one random topic for the game that has to be different from all these topics:\n" + '\n'.join(topics)
    response_schemas = [
        ResponseSchema(name="topic", description="string of the topic")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template="Follow the user's instruction and make sure you are inspired by 'Who wants to be a millionaire'.\n{format_instructions}\n{instruction}",
        input_variables=["instruction"],
        partial_variables={"format_instructions": format_instructions},
    )
    if OFFLINE:
        model = OllamaLLM(model="mistral", temperature=0.8)
    else:
        model = ChatOpenAI(model="gpt-4", temperature=0.8)
    chain = prompt | model | output_parser
    
    llm_response = chain.invoke({"instruction": instruction})
    if llm_response != "" and llm_response is not None:
        print(llm_response)
        if "topic" in llm_response:
            # from str to python obj - no longer needed
            #response_json = json.loads(llm_response)
            # extract str from dict
            random_topic = llm_response['topic']
            return random_topic

    predef_random_topic = "Technology"
    return predef_random_topic


def generate_question(topic: str):
    """Generate a question based on the given topic"""
    if check_ollama_status() == 0: # pragma: no cover
        return abort(404, 'Ollama is not available.')

    instruction = "Generate one question based on the chosen topic of \"" + topic + "\""
    response_schemas = [
        ResponseSchema(name="question", 
                       description="string of the question"),
        ResponseSchema(name="options",
                       description="list of four possible \
                       answers to the question and each answer is a string"),
        ResponseSchema(name="answer", 
                       description="string of the correct answer to the question")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template="Follow the user's instruction and make sure you are inspired by the game \
'Who wants to be a millionaire'. \
Use the given index of the question to come up with questions \
with increasing complexity. Its value can be between 1 and 15; if it is equal to 1, the question \
will be extremely easy and if it is equal to 15, the question will be extremely difficult. \
The index of the question is " + str(session['index']) + "\
Make sure the answer is among the list of options. \
\n{format_instructions}\n{instruction}",
        input_variables=["instruction"],
        partial_variables={"format_instructions": format_instructions},
    )
    if OFFLINE:
        model = OllamaLLM(model="mistral", temperature=0.8)
    else:
        model = ChatOpenAI(model="gpt-4", temperature=0.8)
    chain = prompt | model | output_parser

    try:
        llm_response = chain.invoke({"instruction": instruction})
        if llm_response != "" and llm_response is not None:
            print(topic)
            print(llm_response)
            if "question" in llm_response and "options" in llm_response and "answer" in llm_response:
                # from str to python obj - no longer needed
                #response_json = json.loads(llm_response)
                # extract data from dict
                question = llm_response['question']
                options = llm_response['options']
                answer = llm_response['answer']
                #print(question)
                #print(answer)
                if len(options) != 4 or str(answer) not in options:
                    # generate another question
                    return None, None, None
                
                return question, options, answer

        # for testing purposes
        # question = "Placeholder: What is the capital of France?" 
        # options = ["London", "Paris", "Berlin", "Rome"]  
        # answer = "Paris" 
        # return question, options, answer

        return None, None, None
    except OutputParserException:
        print("Failed to generate a question - (parsing LLM response)")
        return None, None, None
    

@bp.route('/check_answer', methods=['POST'])
def check_answer():
    """"""
    selected_option = request.form['selected_option']

    if selected_option == session['answer']:
        feedback = "Correct answer!"
        # set to None to prevent the following question
        # to be the same question again
        session['question'] = None
    else:
        feedback = "Wrong! The correct answer is " + session['answer']
        session['end'] = True

    return jsonify({'feedback': feedback, 'answer': session['answer']})

