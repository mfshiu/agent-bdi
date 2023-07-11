#Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import json
import os
import threading

import openai

from src.holon import logger

# import tests.lab.lab_config

def set_openai_api_key(key):
    print(f"set_openai_api_key: {key}")
    openai.api_key = key


def parse_to_triplet(user_prompt):
    print(f"parse_to_triplet: {user_prompt}")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a sentence analyzer."},
                {"role": "assistant", "content": "Convert user's sentence to (subject, predict, object) format following the rules below:"},
                {"role": "assistant", "content": "1. Subject, predict and object use only one word."},
                {"role": "assistant", "content": "2. Predict uses infinitive verb, if it is a verb."},
                {"role": "assistant", "content": "3. Respond ONLY in the requested format: (subject, predict, object), without any other wrods."},
                {"role": "system", "name": "example_user", "content": "I want to go to the park."},
                {"role": "system", "name": "example_assistant", "content": "(I, go, park)"},
                {"role": "system", "name": "example_user", "content": "I'm going to the bathroom."},
                {"role": "system", "name": "example_assistant", "content": "(I, go, bathroom)"},
                {"role": "system", "name": "example_user", "content": "我晚餐想吃麥當勞漢堡。"},
                {"role": "system", "name": "example_assistant", "content": "(I, eat, McDonald's)"},
                {"role": "system", "name": "example_user", "content": "terminate system."},
                {"role": "system", "name": "example_assistant", "content": "(, terminate, system)"},
                {"role": "user", "content": f"Analyze: '{user_prompt}'"},
            ]
    )
    # print(f"completion: {completion}")
    # print(f"completion: {completion['choices'][0]['message']}")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    triplet = completion['choices'][0]['message']['content']
    result = triplet if '(' in triplet and ')' in triplet else None
    print(f"result: {result}, triplet: {triplet}")
    return result
    

def understand(prompt, last_sentence=None):
    global _subject
    global _predict
    global _object
    global _positivity
    global _classification

    print(f"openai.api_key: {openai.api_key}")
        

    def analyze_positivity(user_prompt):
        logger.info(f"analyze_positivity: {user_prompt}, last_sentence:{last_sentence}")

        if last_sentence:
            completion = openai.Completion.create(
                model="text-davinci-003",
                temperature=0,
                max_tokens=5,
                prompt=f"""Guide: '{last_sentence}'
User: '{user_prompt}'
Does that mean the user agrees or is positive? Just answer yes or no only."""
            )
        else:
            completion = openai.Completion.create(
                model="text-davinci-003",
                temperature=0,
                max_tokens=5,
                prompt=f"Is '{user_prompt}' a positive sentence or word? Just response yes or no."
                # prompt=f"Is the sentence express positive or negative?\n{user_prompt}"
                # prompt=f"Is the sentence express positive, negative or neutral?\n{user_prompt}"
            )

        # print(f'completion: {completion}')

        global _positivity
        text = completion['choices'][0]['text']
        #_positivity = 'pos' in text.lower()
        _positivity = 'yes' in text.lower()


    def classify_instruction(user_prompt):
        delimiter = "####"
        system_message = f"""
    You will receive an instruction from a user.
    The user's directive will be separated by {delimiter} characters.
    Please categorize the instruction into major and minor categories.
    And provide your output in json format with key values: primary (major category) and secondary (minor category).

    Primary (main category): go somewhere, get items, clean up the mess, provide information, greeting or unsupported categories.

    minor categories of greeting:
    normal
    happy

    minor categories of go somewhere:
    go to a park
    go to a entrance
    go to a toilet
    go to a export
    go to a restaurant

    minor categories of get items:
    take a book
    take a glass of water
    take the remote control
    take a fruit
    take some items

    minor categories of clean up the mess:
    clear the table
    clean up the ground
    clean windows
    clean others 

    minor categories of provide information:
    product specification
    price
    reviews
    restaurant suggestion
    others
    talk to real people

    """
        messages =  [  
            {'role':'system', 'content': system_message},    
            {'role':'user', 'content': f"{delimiter}{user_prompt}{delimiter}"},  
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=messages
        )
        content = completion['choices'][0]['message']['content']
        global _classification
        _classification = tuple(json.loads(content).values())


    def _process_result(result):
        if result:
            result = result.strip()
            if result[0] == "(":
                result = result[1:]
            if result[-1] == ")":
                result = result[:-1]
        print(f"result: {result}")
        return result
        

    def parse_subject(user_prompt):
        print(f"parse_subject: {user_prompt}")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=3,
            messages=[
                    {"role": "system", "content": "You are a sentence analyzer."},
                    {"role": "assistant", "content": "Convert user's sentence to (subject) format following the rules below:"},
                    {"role": "assistant", "content": "1. Response only one word."},
                    {"role": "assistant", "content": "2. If there is no subject, infer the subject."},
                    {"role": "assistant", "content": "3. Respond ONLY in the requested format: (subject), without any other wrods."},
                    {"role": "assistant", "content": "4. Answer in English"},
                    {"role": "system", "name": "example_user", "content": "I want to go to the park."},
                    {"role": "system", "name": "example_assistant", "content": "(I)"},
                    {"role": "system", "name": "example_user", "content": "He's going to the bathroom."},
                    {"role": "system", "name": "example_assistant", "content": "(He)"},
                    {"role": "system", "name": "example_user", "content": "我晚餐想吃麥當勞漢堡。"},
                    {"role": "system", "name": "example_assistant", "content": "(I)"},
                    {"role": "system", "name": "example_user", "content": "terminate system."},
                    {"role": "system", "name": "example_assistant", "content": "(You)"},
                    {"role": "user", "content": f"Analyze: \"{user_prompt}\", response only one word."},
                ]
        )

        global _subject
        _subject = _process_result(completion['choices'][0]['message']['content'])


    def parse_predict(user_prompt):
        print(f"parse_predict: {user_prompt}")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=3,
            messages=[
                    {"role": "system", "content": "You are a sentence analyzer."},
                    {"role": "assistant", "content": "Convert user's sentence to (predict) format following the rules below:"},
                    {"role": "assistant", "content": "1. Response only one word."},
                    {"role": "assistant", "content": "2. If there is no predict, infer the subject."},
                    {"role": "assistant", "content": "3. Respond ONLY in the requested format: (predict), without any other wrods."},
                    {"role": "assistant", "content": "4. Answer in English"},
                    {"role": "system", "name": "example_user", "content": "I want to go to the park."},
                    {"role": "system", "name": "example_assistant", "content": "(go)"},
                    {"role": "system", "name": "example_user", "content": "He's going to the bathroom."},
                    {"role": "system", "name": "example_assistant", "content": "(go)"},
                    {"role": "system", "name": "example_user", "content": "我晚餐想吃麥當勞漢堡。"},
                    {"role": "system", "name": "example_assistant", "content": "(eat)"},
                    {"role": "system", "name": "example_user", "content": "terminate system."},
                    {"role": "system", "name": "example_assistant", "content": "(terminate)"},
                    {"role": "user", "content": f"Analyze: \"{user_prompt}\", response only one word."},
                ]
        )

        global _predict
        _predict = _process_result(completion['choices'][0]['message']['content'])
        

    def parse_object(user_prompt):
        print(f"parse_object: {user_prompt}")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=4,
            messages=[
                    {"role": "system", "content": "You are a sentence analyzer."},
                    {"role": "assistant", "content": "Convert user's sentence to (object) format following the rules below:"},
                    {"role": "assistant", "content": "1. Response only one word."},
                    {"role": "assistant", "content": "2. If there is no object, infer the object."},
                    {"role": "assistant", "content": "3. Respond ONLY in the requested format: (object), without any other wrods."},
                    {"role": "assistant", "content": "4. Answer in English"},
                    {"role": "system", "name": "example_user", "content": "I want to go to the park."},
                    {"role": "system", "name": "example_assistant", "content": "(park)"},
                    {"role": "system", "name": "example_user", "content": "He's going to the bathroom."},
                    {"role": "system", "name": "example_assistant", "content": "(bathroom)"},
                    {"role": "system", "name": "example_user", "content": "我晚餐想吃麥當勞漢堡。"},
                    {"role": "system", "name": "example_assistant", "content": "(McDonald's hamburger)"},
                    {"role": "system", "name": "example_user", "content": "terminate system."},
                    {"role": "system", "name": "example_assistant", "content": "(system)"},
                    {"role": "user", "content": f"Analyze: \"{user_prompt}\", response only one word."},
                ]
        )

        global _object
        _object = _process_result(completion['choices'][0]['message']['content'])
    

    threads = []
    threads.append(threading.Thread(target=classify_instruction, args=(prompt,)))
    threads.append(threading.Thread(target=parse_subject, args=(prompt,)))
    threads.append(threading.Thread(target=parse_predict, args=(prompt,)))
    threads.append(threading.Thread(target=parse_object, args=(prompt,)))
    threads.append(threading.Thread(target=analyze_positivity, args=(prompt,)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # return (_subject, _predict, _object)
    return _classification, (_subject, _predict, _object, _positivity)


if __name__ == '__main__':
    print(f'***** {__file__} Start *****\n')

    set_openai_api_key(os.getenv('OPENAI_API_KEY'))

    prompt = "I want to eat McDonald's for dinner"
    prompt = "我要吃麥當勞。"
    prompt = "Building"
    prompt = "悠悅光，擁有時尚純白的建築外觀"
    prompt = "系統"
    prompt = "How many chat completion choices to generate for each input message?"
    prompt = "Yes"
    prompt = "I want to go to eastern building"
    prompt = "I go back from you."
    prompt = "back"
    prompt = "stop"
    prompt = "我想吃大便"
    prompt = "estern"
    prompt = "turn left"
    prompt = "Terminate the system"
    prompt = "Please take me to the park"
    prompt = "go back from me"
    prompt = "go ahead"
    prompt = "系統關機"
    prompt = "It's go back"
    prompt = "我要吃西餐"
    prompt = "stop the car"
    prompt = "I woulk like to eat Chinese food."
    prompt = "我要去樓上"
    prompt = "I shoot an arrow"
    prompt = "you go back!"
    prompt = "yes"
    prompt = "Run"
    prompt = "shutup"
    prompt = "I love my Ting"
    prompt = "wonderful"
    prompt = "Dog"
    prompt = "esto no está bien"
    prompt = "eso es bueno"
    prompt = "我要去公園"
    triplet = understand(prompt)

    print(f"result: {triplet}")

    print(f'\n***** {__file__} Stop *****')
