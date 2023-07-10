import json
import openai


def get_completion_messages(user_prompt):
    delimiter = "####"
    system_message = f"""
你將會收到一些客戶服務查詢。
每個客戶服務查詢將以 {delimiter} 字元進行分隔。
請將每個查詢分類為主要類別和次要類別。
並以 json 格式提供你的輸出，鍵值為：primary（主類別）和 secondary（次類別）。

Primary（主類別）: 帳單、技術支援、帳戶管理或一般查詢

帳單的次類別:
取消訂閱或升級
增加付款方式
收費說明
爭議收費

技術支援次類別:
一般故障排除
設備相容性
軟體更新

帳戶管理次要類別:
重設密碼
更新個人資訊
關閉帳戶
帳戶安全

一般查詢的次要類別:
產品資訊
價格
反饋
與真人客服對話

"""
    messages =  [  
        {'role':'system', 'content': system_message},    
        {'role':'user', 'content': f"{delimiter}{user_prompt}{delimiter}"},  
    ]
    return messages


def get_completion_messages1(user_prompt):
    delimiter = "####"
    system_message = f"""
你將會收到一些使用者的指令。
每個使用者的指令將以 {delimiter} 字元進行分隔。
請將每個查詢分類為主要類別和次要類別。
並以 json 格式提供你的輸出，鍵值為：primary（主類別）和 secondary（次類別）。

Primary（主類別）: 帶路導覽、取得物品、清理環境、提供資訊、打招呼或不屬於服務類別

打招呼的次類別:
一般
快樂

帶路導覽的次類別:
帶去公園
帶去入口
帶去廁所
帶去出口
帶去餐廳

取得物品次要類別:
拿一本書
拿一杯水
拿搖控器
拿一顆蘋果

清理環境次要類別:
清理桌子
清理地面
清理窗戶
清理牆壁

提供資訊的次要類別:
產品規格資訊
價格資訊
評論資訊
與真人對話
提供餐廳位置
提供娛樂場所位置

"""
    messages =  [  
        {'role':'system', 'content': system_message},    
        {'role':'user', 'content': f"{delimiter}{user_prompt}{delimiter}"},  
    ]
    return messages


def get_completion_messages2(user_prompt):
    delimiter = "####"
    system_message = f"""
You will receive an instruction from a user.
The user's directive will be separated by {delimiter} characters.
Please categorize the demand into major and minor categories.
And provide your output in json format with key values: primary (major category) and secondary (minor category).

Primary (main category): go somewhere, get items, clean up the mess, provide information, greeting or unsupported categories.

minor categories of greeting:
normal
happy

minor categories of lead the way:
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
    return messages


def get_triplet_completion_messages(user_prompt):
    delimiter = "####"
    system_message = f"""
你將會收到使用者所說的話。
使用者所說的話將以 {delimiter} 字元進行分隔。
請將使用者所說的話以 json 格式提供你的輸出，鍵值為：subject（主語）、predict（謂語）和 object（賓語）。
"""
    messages =  [  
        {'role':'system', 'content': system_message},    
        {"role": "assistant", "content": "注意以下規範："},
        {"role": "assistant", "content": "1. Use ONLY ONE English word for the value of each key."},
        {"role": "assistant", "content": "2. If there is no subject, infer the subject."},
        {"role": "assistant", "content": "3. Answer in English"},
        {"role": "system", "name": "example_user", "content": "I would like to go to a park."},
        {"role": "system", "name": "example_assistant", "content": """{"subject": "I",
"predict": "would like",
"object": "park"""},
        {"role": "system", "name": "example_user", "content": "He's going to the bathroom."},
        {"role": "system", "name": "example_assistant", "content": """{"subject": "he",
"predict": "go",
"object": "bathroom\""""},
        {'role':'user', 'content': f"{delimiter}{user_prompt}{delimiter}"},  
    ]
    return messages


if __name__ == '__main__':
    openai.api_key = ""

    user_prompt = "I would like to watch TV."    # O
    user_prompt = "I would like to go to a park."    # O
    user_prompt = "I would like to go to school."    # O
    user_prompt = "I have to see a doctor right now."    # O
    user_prompt = "I need to pee now."    # O
    user_prompt = "I want to read harry potter"    # O 
    user_prompt = "The floor is dirty, please clean it"  # O
    user_prompt = "please clean up these clutter"  # O
    user_prompt = "I want you to delete my profile and all user data" # X
    user_prompt = "So boring, I want to find a place to have fun."    # O
    user_prompt = "I'm hungry, I need to eat"
    user_prompt = "I'm hungry"    # O
    user_prompt = "hello, how are you?"    # O
    user_prompt = "hi good morning nice to meet you"    # O
    user_prompt = "wow good morning very nice to meet you"    # O
    user_prompt = "I was so glad to meet you"    # O
    user_prompt = "good morning"
    user_prompt = "i want diarrhea"   
    user_prompt = "my stomach hurts" 
    user_prompt = "I'm so thirsty"    # O
    user_prompt = "someone spilled a drink on the table"    # O
    user_prompt = "I want to watch TV"    # X
    user_prompt = "How much is the latest MacBook Pro?"    # O
    user_prompt = "i want to go for a walk with the dog."    # O

    messages = get_completion_messages2(user_prompt)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=messages
    )
    classfication = completion['choices'][0]['message']['content']
    values_tuple = tuple(json.loads(classfication).values())
    print(f"Classfication:\n{values_tuple}")


if __name__ == 'x__main__':
    openai.api_key = ""

    user_prompt = "我要你刪除我的個人資料和所有使用者資料" # X
    user_prompt = "地上很髒請打掃一下"  # O
    user_prompt = "我想要去遛狗"    # O
    user_prompt = "最新的MacBook Pro一台多少錢？"    # O
    user_prompt = "我要看電視"    # X
    user_prompt = "有人在桌上打翻了飲料"    # O
    user_prompt = "我想閱讀哈利波特"    # O 
    user_prompt = "我的口好渴"    # O
    user_prompt = "I would like to watch TV."    # O
    user_prompt = "我的肚子好痛"    # X
    user_prompt = "我想拉肚子"    # X
    user_prompt = "早安"    # O
    user_prompt = "嗨早安，見到你真開心"    # O
    user_prompt = "哈囉，你好"    # O
    user_prompt = "我肚子餓了"    # O
    user_prompt = "我要找一間餐廳吃飯"    # O
    user_prompt = "請帶我去一間餐廳"    # O
    user_prompt = "好無聊"    # O
    user_prompt = "好無聊，我想找個地方的玩"    # O
    user_prompt = "我要找地方尿尿"    # O
    user_prompt = "我要去公園"    # O
    user_prompt = "I would like to go to a park."    # O

    messages = get_completion_messages1(user_prompt)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=messages
    )
    classfication = completion['choices'][0]['message']['content']
    print(f"Classfication:\n{classfication}")

    messages = get_triplet_completion_messages(user_prompt)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=messages
    )
    classfication = completion['choices'][0]['message']['content']
    print(f"\nTriplet:\n{classfication}")
