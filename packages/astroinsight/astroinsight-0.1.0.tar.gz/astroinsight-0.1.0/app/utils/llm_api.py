#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/8/19 15:44
# @Author : 桐
# @QQ:1041264242
# 注意事项：
"""
该文件用于调用大模型API
"""

import json
import tiktoken
from app.core.prompt import llm_base_prompt
from app.core.config import DeepSeek_Key, QwenMax_Key
import dashscope
from http import HTTPStatus

# 假设DeepSeekV2模型的定价是每个token 0.0001美元
TOKEN_PRICE_USD = 0.0001
total_tokens_used = 0


def calculate_token_cost(content, model_name="gpt-3.5-turbo"):
    # 使用tiktoken库来计算token数量
    enc = tiktoken.encoding_for_model(model_name)
    tokens = enc.encode(content)
    token_count = len(tokens)
    # 计算费用
    cost_usd = token_count * TOKEN_PRICE_USD
    global total_tokens_used
    total_tokens_used += token_count
    print(f"\033[1;32m | INFO     | Have used total tokens：{total_tokens_used} \033[0m")
    return token_count, cost_usd


def call_with_deepseek(question, system_prompt=llm_base_prompt(), temperature=0.7):
    client = DeepSeek_Key
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=temperature,
        messages=messages
    )

    calculate_token_cost(content=question + system_prompt + response.choices[0].message.content)

    print("\033[1;32m | INFO     | Call_with_deepseek: OK! \033[0m")
    return response.choices[0].message.content


def call_with_deepseek_jsonout(system_prompt, question):
    client = DeepSeek_Key

    if system_prompt == "":
        system_prompt = """The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

EXAMPLE INPUT: 
Which is the highest mountain in the world? Mount Everest.

EXAMPLE JSON OUTPUT:
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    calculate_token_cost(content=question + system_prompt + response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)


def call_with_qwenmax(question, system_prompt=llm_base_prompt()):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    responses = dashscope.Generation.call(
        model="qwen-max-2025-01-25",
        api_key=QwenMax_Key,
        messages=messages,
        stream=False,
        result_format='message',  # 将返回结果格式设置为 message
        top_p=0.8,
        temperature=0.7,
        enable_search=False
    )

    if responses.status_code == HTTPStatus.OK:
        print(responses.output.choices[0].message.content)
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            responses.request_id, responses.status_code,
            responses.code, responses.message
        ))

    print("\033[1;32m  call_with_qwenmax ok! \033[0m")
    return responses.output.choices[0].message.content
