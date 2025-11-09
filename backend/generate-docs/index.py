import json
import os
import re
from typing import Dict, Any, List
import urllib.request
import urllib.error

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: Generate Markdown documentation from Figma Frame using Figma API and DeepSeek AI
    Args: event - dict with httpMethod, body (figmaUrl)
          context - object with request_id, function_name
    Returns: HTTP response with generated markdown
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body_data = json.loads(event.get('body', '{}'))
        figma_url = body_data.get('figmaUrl', '').strip()
        
        if not figma_url:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Figma URL is required'}),
                'isBase64Encoded': False
            }
        
        file_key, node_id = parse_figma_url(figma_url)
        
        if not file_key or not node_id:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid Figma URL format. Expected: figma.com/file/FILE_KEY/...?node-id=NODE_ID'}),
                'isBase64Encoded': False
            }
        
        figma_token = os.environ.get('FIGMA_ACCESS_TOKEN')
        deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        
        if not figma_token:
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'FIGMA_ACCESS_TOKEN not configured'}),
                'isBase64Encoded': False
            }
        
        if not deepseek_key:
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'DEEPSEEK_API_KEY not configured'}),
                'isBase64Encoded': False
            }
        
        figma_data = fetch_figma_node(file_key, node_id, figma_token)
        
        if not figma_data:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Failed to fetch Figma data. Check your token and URL'}),
                'isBase64Encoded': False
            }
        
        elements = extract_ui_elements(figma_data)
        
        frame_name = figma_data.get('name', 'UI Screen')
        
        ai_enhanced_elements = enhance_with_deepseek(elements, frame_name, deepseek_key)
        
        markdown = generate_markdown(ai_enhanced_elements, frame_name)
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({
                'markdown': markdown,
                'frameName': frame_name,
                'elementsCount': len(ai_enhanced_elements)
            }),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Internal error: {str(e)}'}),
            'isBase64Encoded': False
        }


def parse_figma_url(url: str) -> tuple:
    file_match = re.search(r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)', url)
    node_match = re.search(r'node-id=([0-9%-]+)', url)
    
    file_key = file_match.group(1) if file_match else None
    node_id = node_match.group(1).replace('-', ':') if node_match else None
    
    return file_key, node_id


def fetch_figma_node(file_key: str, node_id: str, token: str) -> Dict[str, Any]:
    url = f'https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}'
    
    req = urllib.request.Request(url)
    req.add_header('X-Figma-Token', token)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            nodes = data.get('nodes', {})
            node_data = nodes.get(node_id, {}).get('document', {})
            return node_data
    except urllib.error.HTTPError as e:
        return {}


def extract_ui_elements(node: Dict[str, Any], elements: List[Dict] = None, counter: List[int] = None) -> List[Dict]:
    if elements is None:
        elements = []
    if counter is None:
        counter = [1]
    
    node_type = node.get('type', '')
    node_name = node.get('name', 'Unnamed')
    
    if node_type in ['FRAME', 'GROUP', 'COMPONENT', 'INSTANCE']:
        children = node.get('children', [])
        for child in children:
            extract_ui_elements(child, elements, counter)
    
    elif node_type == 'TEXT':
        elements.append({
            'id': counter[0],
            'type': 'text',
            'name': sanitize_name(node_name),
            'raw_name': node_name,
            'figma_type': node_type
        })
        counter[0] += 1
    
    elif node_type == 'RECTANGLE':
        if is_button_like(node):
            elements.append({
                'id': counter[0],
                'type': 'button',
                'name': sanitize_name(node_name),
                'raw_name': node_name,
                'figma_type': node_type
            })
        else:
            elements.append({
                'id': counter[0],
                'type': 'card',
                'name': sanitize_name(node_name),
                'raw_name': node_name,
                'figma_type': node_type
            })
        counter[0] += 1
    
    elif node_type in ['VECTOR', 'BOOLEAN_OPERATION', 'STAR', 'LINE', 'ELLIPSE']:
        elements.append({
            'id': counter[0],
            'type': 'icon',
            'name': sanitize_name(node_name),
            'raw_name': node_name,
            'figma_type': node_type
        })
        counter[0] += 1
    
    else:
        children = node.get('children', [])
        for child in children:
            extract_ui_elements(child, elements, counter)
    
    return elements


def is_button_like(node: Dict[str, Any]) -> bool:
    name = node.get('name', '').lower()
    has_rounded_corners = node.get('cornerRadius', 0) > 0
    
    return 'button' in name or 'btn' in name or has_rounded_corners


def sanitize_name(name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    sanitized = re.sub(r'_+', '_', sanitized).strip('_').lower()
    return sanitized or 'element'


def enhance_with_deepseek(elements: List[Dict], frame_name: str, api_key: str) -> List[Dict]:
    if not elements:
        return elements
    
    element_summary = '\n'.join([
        f"{e['id']}. {e['type']}: {e['raw_name']}"
        for e in elements
    ])
    
    prompt = f"""Analyze this UI screen called "{frame_name}" with the following elements:

{element_summary}

For each element, provide:
1. A brief Russian description (what it is)
2. Its business logic (what happens when user interacts with it)

Return ONLY a JSON array with this exact structure:
[
  {{"id": 1, "description": "Описание элемента", "logic": "Логика работы"}},
  ...
]

Rules:
- Keep descriptions concise (max 50 chars)
- Keep logic concise (max 80 chars)
- Use Russian language
- Return valid JSON only, no markdown, no extra text"""

    try:
        ai_response = call_deepseek_api(prompt, api_key)
        ai_data = json.loads(ai_response)
        
        ai_map = {item['id']: item for item in ai_data}
        
        for element in elements:
            ai_info = ai_map.get(element['id'], {})
            element['description'] = ai_info.get('description', f"Элемент {element['type']}")
            element['logic'] = ai_info.get('logic', 'Стандартное взаимодействие')
        
        return elements
        
    except Exception:
        for element in elements:
            element['description'] = f"Элемент {element['type']}: {element['raw_name']}"
            element['logic'] = 'Базовое взаимодействие с элементом'
        return elements


def call_deepseek_api(prompt: str, api_key: str) -> str:
    url = 'https://api.deepseek.com/v1/chat/completions'
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.3,
        'max_tokens': 2000
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        content = data['choices'][0]['message']['content']
        
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            return json_match.group(0)
        return content


def generate_markdown(elements: List[Dict], frame_name: str) -> str:
    md = f"# {frame_name} Documentation\n\n"
    md += "| № | Тип элемента | Название | Описание | Логика работы |\n"
    md += "|---|--------------|----------|-----------|---------------|\n"
    
    for element in elements:
        md += f"| {element['id']} | {element['type']} | {element['name']} | "
        md += f"{element.get('description', '')} | {element.get('logic', '')} |\n"
    
    return md
