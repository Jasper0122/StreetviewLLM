import json
import os
import re
import time

import pandas as pd
import requests
from tqdm import tqdm  # 导入 tqdm 用于显示进度条

# 设置你的 OpenAI API key
api_key = "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"
prefix = """You will be given data about a specific location (with its streetview image and Nearby places name with direction) randomly sampled from all human-populated locations on Earth.
Analyze the given data and describe the key factors that lead to the task question. Provide your response in two parts: 

1. Key influencing factors (4 points, each no more than 20 words)
2. Rationale (40 words)

Do not repeat the input content.
"""

def read_jsonl(file_path):
    """Read and parse the JSONL file."""
    with open(file_path, 'r') as file:
        return [json.loads(line.strip()) for line in file]

def send_openai_requests(jsonl_data, prefix, task):
    """Send requests to OpenAI API using the data from JSONL file."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    results = []
    request_count = 0  # 初始化请求计数器

    for data in tqdm(jsonl_data, desc="Processing requests"):
        # Using the text from the JSONL data instead of a fixed string
        formatted_text = prefix + data["text"].strip().replace("<TASK>", task)
        message_content = [
            {"type": "text", "text": formatted_text},
            {"type": "image_url", "image_url": {"url": data["image_url"]}}
        ]
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": message_content}],
            "max_tokens": 300,
            "temperature": 0
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        results.append(result)

        request_count += 1  # 增加请求计数
        if request_count % 10 == 0:  # 每10个请求休息0.2秒
            time.sleep(0.2)

    return results

def save_results_to_jsonl(jsonl_data, results, task, output_path, jsonl_path):
    output_file = os.path.join(output_path, f'{os.path.splitext(os.path.basename(jsonl_path))[0]}_{task}.jsonl')
    with open(output_file, 'w') as file:
        for i, data in enumerate(jsonl_data):
            result = results[i]
            response_text = result['choices'][0]['message']['content']
            data["text"] += response_text
            file.write(json.dumps(data) + '\n')

def main():
    jsonl_path = 'prompts/coordinates1_updated.jsonl'  # Ensure this is the correct path to your JSONL file
    task = 'women BMI'
    jsonl_data = read_jsonl(jsonl_path)
    results = send_openai_requests(jsonl_data, prefix, task)
    save_results_to_jsonl(jsonl_data, results, task, os.path.dirname(jsonl_path), jsonl_path)

if __name__ == '__main__':
    main()
