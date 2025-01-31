import json
import os
import re
import time

import pandas as pd
import requests

# 设置你的 OpenAI API key
api_key = "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"
prefix = """You will be given data about a specific location(with its streetview description and Nearby places name with direction) randomly sampled from all human-populated locations on Earth.
You give your rating keeping in mind that it is relative to all other human-populated locations on Earth (from all continents, countries, etc.).
You provide ONLY your answer in the exact format "Latitude A Longitude B My answer is X.X. " where 'X.X' represents your rating(from 0.0 to 10.0) for the given topic.


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
    request_count = 0 # 初始化请求计数器

    for data in jsonl_data:
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
        for choice in result['choices']:
            print(choice['message']['content'])
        results.append(result)

        request_count += 1  # 增加请求计数
        if request_count % 10 == 0:  # 每10个请求休息0.2秒
            time.sleep(0.2)
            print("sleep")

    return results

def extract_data_and_save(results, task):
    data = []
    pattern = r"Latitude\s+(\d+\.\d+)\s+Longitude\s+(-?\d+\.\d+)\s+My answer is\s+(\d+\.\d+)"
    save_path = f'results/{task}.csv'
    os.makedirs('results', exist_ok=True)  # 确保结果文件夹已创建
    header_written = not os.path.exists(save_path)  # 如果文件不存在，我们需要写入头部

    for result in results:
        for choice in result['choices']:
            matches = re.findall(pattern, choice['message']['content'])
            if matches:
                for match in matches:
                    data.append({
                        'Latitude': float(match[0]),
                        'Longitude': float(match[1]),
                        'Predictions': float(match[2])
                    })
        # 在数据量积累到一定程度时，进行分批写入
        if len(data) >= 100:  # 可以根据需要调整这个阈值
            df = pd.DataFrame(data)
            df.to_csv(save_path, mode='a', header=header_written, index=False)
            header_written = False  # 更新状态，以避免在未来的写入中重复添加头部
            data = []  # 重置数据列表，准备下一批次

    # 处理剩余的数据
    if data:
        df = pd.DataFrame(data)
        df.to_csv(save_path, mode='a', header=header_written, index=False)

    print(f"Successfully saved to {save_path}")
    if os.path.exists(save_path):
        print(f"File exists: {save_path}, rows: {len(pd.read_csv(save_path))}")
    else:
        print(f"Failed to find file at {save_path}")



def main():
    jsonl_path = 'prompts/coordinates1_updated_women BMI.jsonl'  # Ensure this is the correct path to your JSONL file
    task = 'women BMI'
    jsonl_data = read_jsonl(jsonl_path)
    results = send_openai_requests(jsonl_data, prefix, task)
    extract_data_and_save(results,task)

if __name__ == '__main__':
    main()