from ai_request import (
    check_ollama_status, OllamaLLM)

from flask import session

from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException


# OLLAMAURL = "http://localhost:11434"
OLLAMAURL = "https://carlollama.victoriousflower-d746971e.uksouth.azurecontainerapps.io"
OLLAMAMODEL = "mistral"
# Flag to query different LLM. If False, it will use OpenAI API
OFFLINE = True
RANDOM_LABEL = "Surprise me!"


def generate_topics():
    """Generate a list of 5 topics (plus Random)"""   
    # Ollama
    if check_ollama_status(OLLAMAURL) == 0: # pragma: no cover
        return None

    instruction = "Generate 5 different topics for the game. Each topic can have maximum 2 words."
    
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
        model = OllamaLLM(model=OLLAMAMODEL, temperature=0.8, base_url=OLLAMAURL)
    else:
        model = ChatOpenAI(model="gpt-4", temperature=0.8)
    chain = prompt | model | output_parser
    
    try:
        llm_response = chain.invoke({"instruction": instruction})        
    except Exception as e:
        print(e)
        return None
        
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
    if check_ollama_status(OLLAMAURL) == 0: # pragma: no cover
        return None
    
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
        model = OllamaLLM(model=OLLAMAMODEL, temperature=0.8, base_url=OLLAMAURL)
    else:
        model = ChatOpenAI(model="gpt-4", temperature=0.8)
    chain = prompt | model | output_parser

    try:
        llm_response = chain.invoke({"instruction": instruction})        
    except Exception as e:
        print(e)
        return None

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
    if check_ollama_status(OLLAMAURL) == 0: # pragma: no cover
        return None, None, None

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
Higher the value, more complex the question will be. \
Lower the value, more simple the question will be. \
The index of the question is " + str(session['index']) + "\
Make sure the answer is among the list of options. \
\n{format_instructions}\n{instruction}",
        input_variables=["instruction"],
        partial_variables={"format_instructions": format_instructions},
    )
    if OFFLINE:
        model = OllamaLLM(model=OLLAMAMODEL, temperature=0.8, base_url=OLLAMAURL)
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
    except Exception as e:
        print(e)
        return None, None, None 