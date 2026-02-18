import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


def generate_daily_practice(level, previous_summary=None, previous_plan=None):
    prompt = f"""你是一位专业的音乐教育专家，负责为吉他学生生成每日和弦练习内容。

学生当前级别：{level}级（1-10 级，1 级最简单，10 级最难）

"""
    
    if previous_summary:
        prompt += f"""
上次练习总结：
{previous_summary}

上次练习后的改进计划：
{previous_plan}

"""
    
    prompt += """请生成今日的和弦练习内容，要求：
1. 每次练习约 1 分钟，包含 5-8 个和弦
2. 根据级别选择合适的和弦：
   - 1-2 级：C, D, E, G, A, Am, Em, Dm 等基础三和弦
   - 3-4 级：F, Bm, 以及更多调的和弦
   - 5-6 级：七和弦（Cmaj7, Dm7, G7 等）
   - 7-8 级：延伸和弦、变化和弦
   - 9-10 级：复杂爵士和弦
3. 如果学生之前有薄弱环节，适当增加相关练习

请以严格的 JSON 格式返回，格式如下：
{
    "chords": [
        {"name": "C", "notes": ["C", "E", "G"]},
        {"name": "Am", "notes": ["A", "C", "E"]}
    ],
    "focus_area": "本次练习重点",
    "tips": "练习建议"
}

只返回 JSON，不要其他内容。"""

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7
    }
    
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    # 提取 JSON
    start = content.find('{')
    end = content.rfind('}') + 1
    json_str = content[start:end]
    
    return json.loads(json_str)


def generate_practice_summary(practice_data):
    prompt = f"""你是一位专业的音乐教育专家，请根据学生的练习数据生成一份详细的总结报告。

练习数据：
- 级别：{practice_data['level']}
- 得分：{practice_data['score']}
- 总题数：{practice_data['total_questions']}
- 正确数：{practice_data['correct_answers']}
- 练习时长：{practice_data['duration_seconds']}秒
- 练习的和弦：{practice_data['chords_practiced']}
- 各和弦正确率：{practice_data['chord_accuracy']}

请生成一份鼓励性的总结，包括：
1. 整体表现评价
2. 掌握得好的和弦
3. 需要加强的和弦
4. 具体的改进建议

请以 JSON 格式返回，包含以下字段：
- overall_comment: 整体评价
- strengths: 掌握好的方面（数组）
- weaknesses: 需要加强的方面（数组）
- suggestions: 建议（数组）
- encouragement: 鼓励的话

只返回 JSON，不要其他内容。"""

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7
    }
    
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    start = content.find('{')
    end = content.rfind('}') + 1
    json_str = content[start:end]
    
    return json.loads(json_str)


def generate_next_practice_plan(summary, current_level):
    prompt = f"""你是一位专业的音乐教育专家，请根据学生上次练习的总结，生成下次练习的计划建议。

当前级别：{current_level}
上次练习总结：
{json.dumps(summary, ensure_ascii=False)}

请生成下次练习的计划，包括：
1. 建议的级别（可以保持、提升或降低）
2. 建议重点练习的和弦类型
3. 具体的练习目标

请以 JSON 格式返回，包含以下字段：
- suggested_level: 建议级别（数字）
- focus_chords: 建议和弦（数组）
- practice_goals: 练习目标（数组）
- message: 给学生的建议消息

只返回 JSON，不要其他内容。"""

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7
    }
    
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    start = content.find('{')
    end = content.rfind('}') + 1
    json_str = content[start:end]
    
    return json.loads(json_str)
