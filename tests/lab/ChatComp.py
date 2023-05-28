#Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import ast
import re

import openai

openai.api_key = 'xxx'

def test_chat():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ]
    )
    print(f"completion: {completion['choices'][0]['message']['content']}")

def test_chat1():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a language teacher."},
                {"role": "assistant", "content": "Please translate the Chinese to English:"},
                {"role": "assistant", "content": "1.你有權保持緘默，毋需違背意志做任何陳述。"},
                {"role": "user", "content": "Answer: First, you have the right to remain silent and do not have to make any statement against your will."},
                # {"role": "user", "content": "Answer: Frist, dog you have the right to remain silent and doo not have to make any statement against your will."},
                {"role": "assistant", "content": "Are there grammatical errors in the answer? please list if any."},
                # {"role": "assistant", "content": "How well does this user translate? Just list your comment."},
                # {"role": "assistant", "content": "Are there spelling mistakes in the answer? please list the error words if any."},
            ]
    )
    print(f"completion: {completion['choices'][0]['message']}")
    # print(f"completion: {completion['choices'][0]['message']['content']}")


def test_chat2():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a sentence analyzer."},
                {"role": "assistant", "content": "Convert user's sentence to (subject, predict, object) format following the rules below:"},
                {"role": "assistant", "content": "1. Subject, predict and object use only one word. 2. Predict uses infinitive verb, if it is a verb. 3. Respond ONLY in the requested format: (subject, predict, object), without any other wrods."},
                {"role": "user", "content": "I want to go to the zoo."},
            ]
    )
    # print(f"completion: {completion['choices'][0]['message']}")
    # print(f"completion: {completion['choices'][0]['message']['content']}")
    print(f"completion: {completion}")


def test_chat3():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a sentence analyzer."},
                {"role": "assistant", "content": "Convert user's sentence to (subject, predict, object) format following the rules below:"},
                {"role": "assistant", "content": "1. Subject, predict and object use only one word."},
                {"role": "assistant", "content": "2. Predict uses infinitive verb, if it is a verb."},
                {"role": "assistant", "content": "3. Respond ONLY in the requested format: (subject, predict, object), without any other wrods."},
                {"role": "user", "content": "terminate system"},
            ]
    )
    # print(f"completion: {completion['choices'][0]['message']}")
    # print(f"completion: {completion['choices'][0]['message']['content']}")
    print(f"completion: {completion}")


def is_sentence(sentence):
    # completion = complete_sentence(f"Does this sentence have a predicate and object? '{sentence}'. Just answer yes or no.")
    # return "yes" in completion['choices'][0]['text'].lower()
    return yes_or_no(f"Does this sentence have a predicate and object?'{sentence}'")


def is_verb(sentence):
    # completion = complete_sentence(f"Is '{sentence}' just a verb?. Just answer yes or no.")
    # return "yes" in completion['choices'][0]['text'].lower()
    verbs = ['back']
    return True if sentence in verbs \
        else yes_or_no(f"Is '{sentence}' just a verb?")


def is_noun(sentence):
    # completion = complete_sentence(f"Is '{sentence}' just a noun?. Just answer yes or no.")
    # return "yes" in completion['choices'][0]['text'].lower()
    nouns = ['IRI']
    return True if sentence in nouns \
        else yes_or_no(f"Is '{sentence}' just a noun?")


def is_negative(sentence):
    return yes_or_no(f"Does '{sentence}' mean negative emotion?")


def is_positive(sentence):
    return yes_or_no(f"Does '{sentence}' mean positive emotion?")


def complete_sentence(sentence):
    print(f"complete_sentence: {sentence}")
    completion = openai.Completion.create(
        model = "text-davinci-003",
        prompt = sentence,
        max_tokens = 3,
        temperature = 0,
        top_p = 1,
        n = 1,
        # stream = False,
        # logprobs = None,
        # stop = "\n"
    )
    # return example:
    # {
    #   "choices": [
    #     {
    #       "finish_reason": "length",
    #       "index": 0,
    #       "logprobs": null,
    #       "text": "\n\nYes"
    #     }
    #   ],
    #   "created": 1684747093,
    #   "id": "cmpl-7Ivy9uUdvQHxcbClY6R5mu2W06J7s",
    #   "model": "text-davinci-003",
    #   "object": "text_completion",
    #   "usage": {
    #     "completion_tokens": 3,
    #     "prompt_tokens": 7,
    #     "total_tokens": 10
    #   }
    # }
    # print(f'{completion}')
    return completion


def yes_or_no(user_prompt):
    print(f"yes_or_no: {user_prompt}")

    user_prompt += ". Is yes or no?"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a sentence analyzer."},
                {"role": "assistant", "content": "Just answer yes or no."},
                {"role": "assistant", "name": "example_user", "content": "Is 'park' a noun?"},
                {"role": "assistant", "name": "example_assistant", "content": "yes"},
                {"role": "assistant", "name": "example_user", "content": "Is 'shoot' a verb?"},
                {"role": "assistant", "name": "example_assistant", "content": "yes"},
                {"role": "assistant", "name": "example_user", "content": "Is 'I shot an arrow.' a sentence?"},
                {"role": "assistant", "name": "example_assistant", "content": "yes"},
                {"role": "assistant", "name": "example_user", "content": "Is 'eat' a noun?"},
                {"role": "assistant", "name": "example_assistant", "content": "no"},
                {"role": "user", "content": user_prompt},
            ]
    )
    # print(f"completion: {completion['choices'][0]['message']}")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    # print(f'{completion}')
    content = completion['choices'][0]['message']['content']
    result = 'yes' in content.lower()
    print(f"result: {'yes' if result else 'no'}")
    return result


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
    

def edit_sentence(sentence):
    print(f"edit_sentence: {sentence}")
    completion = openai.Edit.create(
        model = "text-davinci-edit-001",
        input = sentence,
        temperature = 0,
        instruction = "Fix to a correct sentence with subject, predicate and object."
    )
    # return example:
    # {
    #     "choices": [
    #         {
    #         "index": 0,
    #         "text": "back to the future\n"
    #         }
    #     ],
    #     "created": 1684753916,
    #     "object": "edit",
    #     "usage": {
    #         "completion_tokens": 16,
    #         "prompt_tokens": 25,
    #         "total_tokens": 41
    #     }
    # }
    # print(f'{completion}')
    editted = completion['choices'][0]['text'].strip()
    print(f"editted: {editted}")
    return editted


def is_keyword(prompt:str):
    print(f"is_keyword: {prompt}")
    keywords = [
        'yes',
        'no',
        # 'forward',
        # 'back',
        # 'turn',
        ]
    result = prompt.lower() in keywords
    print(f"is_keyword: {'yes' if result else 'no'}")
    return result


def parse_sentence(user_prompt:str):
    print(f"parse_sentence: {user_prompt}")

    if not user_prompt:
        return None
    
    if is_sentence(user_prompt):
        return parse_to_triplet(user_prompt)
    elif is_verb(user_prompt):
        return f"(, {user_prompt},)"
    elif is_noun(user_prompt):
        return f"(, , {user_prompt})"
    # elif is_keyword(user_prompt):
    #     return user_prompt.lower()
    else:
        return None
    

def understand(prompt):
    if is_keyword(prompt):
        triplet = f'(, {prompt},)'
    else:
        triplet = parse_sentence(prompt)
        if not triplet:        
            prompt2 = f"It {prompt}"
            triplet = parse_sentence(prompt2)
            if not triplet:        
                edited_prompt2 = edit_sentence(prompt2)
                triplet = parse_sentence(edited_prompt2)
                if not triplet:
                    if is_positive(prompt):
                        triplet = f'(, yes,)'
                    elif is_negative(prompt):
                        triplet = f'(, no,)'
                    else:
                        triplet = f'(, {prompt},)'

    print(f'triplet: {triplet}')
    tuple_0 = tuple(triplet[1:-1].split(','))
    tuple_1 = tuple(x.strip() if x else None for x in tuple_0)
    return tuple_1


if __name__ == 'x__main__':
    edit_sentence("back")


if __name__ == '__main__':
    print(f'***** {__file__} Start *****\n')

    # completion = test_chat4("I'm going to the convenience store")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    # completion = test_chat4("Open the door.")
    # print(f"completion: {completion['choices'][0]['message']['content']}")

    prompt = "I want to eat McDonald's for dinner"
    prompt = "我要吃麥當勞。"
    prompt = "Building"
    prompt = "I shoot a arrow"
    prompt = "stop the car"
    prompt = "悠悅光，擁有時尚純白的建築外觀"
    prompt = "Run"
    prompt = "I woulk like to eat Chinese food."
    prompt = "系統關機"
    prompt = "系統"
    prompt = "How many chat completion choices to generate for each input message?"
    prompt = "Yes"
    prompt = "Dog"
    prompt = "I love my Ting"
    prompt = "I want to go to eastern building"
    prompt = "you go back!"
    prompt = "go back from me"
    prompt = "I go back from you."
    prompt = "turn left"
    prompt = "back"
    prompt = "stop"
    prompt = "wonderful"
    prompt = "go ahead"
    prompt = "shutup"
    prompt = "我想吃大便"
    prompt = "estern"
    prompt = "Please take me to the park"
    prompt = "我要去公園"
    prompt = "我要吃西餐"
    prompt = "yes"
    prompt = "我要去樓上"
    triplet = understand(prompt)

    print(f"result: {triplet}")

    print(f'\n***** {__file__} Stop *****')
