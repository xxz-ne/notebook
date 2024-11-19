import requests
import json

API_KEY = "DUMt8TAT7lYAlIZxMAswPakO"
SECRET_KEY = "5HFcLpQ2352MWpMYZvjFw4FoCZMbtINm"

def getAI(inputs):
    # 获取用户输入

    
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + get_access_token()
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": inputs  # 将用户输入放入消息内容中
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    try:
        # 尝试从返回的JSON中提取result
        response_json = response.json()
        result = response_json.get('result', '未找到result字段')
        return result
    except json.JSONDecodeError:
        return "响应不是有效的JSON格式:"


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))



