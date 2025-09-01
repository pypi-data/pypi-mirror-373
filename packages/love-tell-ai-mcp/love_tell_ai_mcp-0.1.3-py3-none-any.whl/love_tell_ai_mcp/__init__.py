import os
from http import HTTPStatus
from dashscope import Application
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.dependencies import get_http_request

# 初始化FastMCP实例
mcp = FastMCP(port=8888,debug=True)

# 内置app_id
TAOHUAXING_APP_ID = '6fd5f6dc3f5a4b29b7b7f7a4946061db'
QINGGANMOSHI_APP_ID = 'fc6ae977e2194ad98f62839551fd6dbc'
HUNYINGGONG_APP_ID = '8224100adf964981adbb1472adc35355'
PEIOUXING_APP_ID = 'ec2ac94067eb43c9ae4ac7694e3caee0'
DAYUNLIUNIAN_APP_ID = '012c3ff47d584f05989a1fd46c573539'
BANLVTEZHI_APP_ID = '98e54470c60b44458d659f0778d6796a'
HUDONGMOSHI_APP_ID = '374ed5c508064b63a8e3e5e5aed95567'

@mcp.tool()
def lovetell_thx(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的桃花星。
    输入用户八字为JSON格式。输出用户的桃花星格局解析，以下JSON格式：
    {
        "咸池桃花": {...},
        "红艳煞": {...},
        "神煞与十神组合": {...},
        "桃花星曜": {...},
        "关键宫位": {...},
        "桃花格局": {...},
    }
    
    Args:
        bazi: 用户输入的八字信息
    
    Returns:
        用户的桃花星格局解析JSON
    """
    return call_dashscope(bazi, TAOHUAXING_APP_ID)

@mcp.tool()
def lovetell_qgms(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的情感模式。
    输入用户八字为JSON格式。输出用户的情感模式解析，以下JSON格式：
    {
        "情感底色": ...,
        "情感需求": ...,
        "情感表达": ...,
        "情感冲突": ...
    }
    """
    return call_dashscope(bazi, QINGGANMOSHI_APP_ID)

@mcp.tool()
def lovetell_hyg(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的婚姻宫。
    输入用户八字为JSON格式。输出用户的婚姻宫格局解析，以下JSON格式：
    {
        "日支五行和藏干": {...},
        "婚姻宫稳定性": {...},
        "婚姻宫内部结构": {...},
        "神煞影响": {...},
        "紫微斗数夫妻宫": {...}
    }
    """
    return call_dashscope(bazi, HUNYINGGONG_APP_ID)

@mcp.tool()
def lovetell_pox(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的配偶星。
    输入用户八字为JSON格式。输出用户的配偶星格局解析，以下JSON格式：
    {
        "配偶星定位":{...},
        "配偶宫分析":{...},
        "紫微斗数辅证":{...},
        "命理与心理学结合":{...} 
    }
    """
    return call_dashscope(bazi, PEIOUXING_APP_ID)



@mcp.tool()
def lovetell_dyln(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的大运流年。
    输入用户八字为JSON格式。要求你的测算结果以JSON格式输出，内容全部以算命术语表达
    """
    return call_dashscope(bazi, DAYUNLIUNIAN_APP_ID)

@mcp.tool()
def lovetell_bltz(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的伴侣特质。
    输入用户八字为JSON格式。要求你的测算结果以JSON格式输出，内容全部以算命术语表达
    """
    return call_dashscope(bazi, BANLVTEZHI_APP_ID)


@mcp.tool()
def lovetell_hdms(bazi: str):
    """
    你是专为恋爱婚姻做情感咨询的算命大师，你的任务是根据用户输入的八字信息，测算用户的互动模式。
    输入用户八字为JSON格式。要求你的测算结果以JSON格式输出，内容全部以算命术语表达
    """
    return call_dashscope(bazi, HUDONGMOSHI_APP_ID)



def call_dashscope(bazi: str, app_id:str):
    
    # 优先从头信息中获取
    headers = get_http_headers()
    api_key = headers.get("api_key","")

    # 从环境变量获取api_key，由用户在安装时指定
    if not api_key:
        api_key = os.getenv("api_key")
    
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY环境变量未设置，请在安装时指定api_key")
    
    responses = Application.call(
        api_key=api_key,
        app_id=app_id,
        prompt=bazi,
        stream=True,
        incremental_output=True
    )
    
    result = ""
    for response in responses:
        if response.status_code != HTTPStatus.OK:
            error_msg = f'request_id={response.request_id}, code={response.status_code}, message={response.message}'
            raise Exception(error_msg)
        else:
            result += response.output.text
    
    return result
def main() -> None:
    mcp.run(transport='stdio')
