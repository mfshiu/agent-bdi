#Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import ast
import re
import threading

import openai

openai.api_key = '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'

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
    

def understand(prompt):
    global _subject
    global _predict
    global _object


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
            max_tokens=3,
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
    threads.append(threading.Thread(target=parse_subject, args=(prompt,)))
    threads.append(threading.Thread(target=parse_predict, args=(prompt,)))
    threads.append(threading.Thread(target=parse_object, args=(prompt,)))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # subject = parse_subject(prompt)
    # predict = parse_predict(prompt)
    # obj = parse_object(prompt)
    return (_subject, _predict, _object)


if __name__ == '__main__':
    print(f'***** {__file__} Start *****\n')

    # completion = test_chat4("I'm going to the convenience store")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    # completion = test_chat4("Open the door.")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    prompt = "I want to eat McDonald's for dinner"
    prompt = "我要吃麥當勞。"
    prompt = "Building"
    prompt = "悠悅光，擁有時尚純白的建築外觀"
    prompt = "系統"
    prompt = "How many chat completion choices to generate for each input message?"
    prompt = "Yes"
    prompt = "I love my Ting"
    prompt = "I want to go to eastern building"
    prompt = "I go back from you."
    prompt = "back"
    prompt = "stop"
    prompt = "shutup"
    prompt = "我想吃大便"
    prompt = "estern"
    prompt = "turn left"
    prompt = "Dog"
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
    prompt = "wonderful"
    prompt = "you go back!"
    prompt = "yes"
    prompt = "Run"
    prompt = "我要去公園"
    triplet = understand(prompt)

    print(f"result: {triplet}")

    print(f'\n***** {__file__} Stop *****')
