# -*- coding: utf-8 -*-
import asyncio
from functools import partial
import blivedm
import tls_client
import aiohttp
import pyaudio
import wave
import io
import xml.etree.ElementTree as ET
import base64
import argparse

import sys
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
c_session = tls_client.Session(

    client_identifier="chrome107",

    random_tls_extension_order=True

)

#globals
character_external_id=''
history_id=''
tgt=''
access_token=''
appid=''
appsec=''
proxy=''
token=''
voiceurl=''
TEST_ROOM_ID = 0
msg_str_format=''
gift_str_format=''
USE_QQ_AUDIT=False
voiceargs=[]
cookies = {
    'amp_fef1e8': '57a8871e-f075-4c2a-bb3f-561b756061dbR...1gs7lct6v.1gs7lin67.6.0.6',
    '__cuid': '6c8146d1ccb54071877f8333565af650',
    '__cf_bm': 'uSOpu8d0pTJ85rLU2hh3vmDD0kV00hP1_cW5CVws3S8-1679933676-0-ASM21JyZn14/mSqLMGTbwPycyY9zxpkV70rgQTZxrJtqcNt90+xuyCOu1SRemb3D6d1gytcWdJDV+X9v29WGNpNVPLmv+xhlyGq2mm7lgso3OjmVHIp7pl3JvS+Ux355G+FGqziirkcOF6+hplSRTETH9Lxeu0dZf7ZSHDjjat33',
    'csrftoken': 'mDx5IhFALY9YTysCw2pOjbVJzmKGrGLJ',
}



#helpers
async def get_access_token(appid, appsecret):
    if USE_QQ_AUDIT==False:
        url='https://ci-exhibition.cloud.tencent.com/sts?prefix=text%2Fauditing&method=POST&action='
    else:
        url = f'https://api.q.qq.com/api/getToken?grant_type=client_credential&appid={appid}&secret={appsecret}'
    async with aiohttp.ClientSession() as asession:
        async with asession.get(url) as response:
            if USE_QQ_AUDIT==False:
                return await response.json()
            data = await response.json()
            return data['access_token']

async def refresh_access_token_every_n_seconds(appid, appsecret, n=3600):
    while True:
        global access_token
        access_token = await get_access_token(appid, appsecret)
        print(f"Access token: {access_token}")
        await asyncio.sleep(n)



async def chat(text):
    if access_token=='':
        return '没有access_token，尚未初始化'
    global history_id
    global tgt
    print(history_id)
    #greetings!
   
    if tgt=='':
        print('requesting tgt')
        headers = {
        'authority': 'beta.character.ai',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7',
        'authorization': 'Token '+token,
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://beta.character.ai',
        'referer': 'https://beta.character.ai/',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; TEL-AN00a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
        }
        json_data = {
        'character_external_id': character_external_id,
        }
        response = await asyncio.get_running_loop().run_in_executor(None,partial( c_session.post,'https://beta.character.ai/chat/history/create/', cookies=cookies, headers=headers, json=json_data,proxy=proxy))
        if response.status_code==200:
            history_id=response.json()['external_id'] if history_id==None else history_id
            tgt=response.json()['participants'][1]['user']['username'] if response.json()['participants'][1]['user']['username'].startswith('internal_id:') else response.json()['participants'][0]['user']['username']
            print('nh>',history_id)

        
    headers = {
    'authority': 'beta.character.ai',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7',
    'authorization': 'Token '+token,
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://beta.character.ai',
    'referer': 'https://beta.character.ai/',
    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; TEL-AN00a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
}
    # /streaming
    json_data = {
    'history_external_id': history_id,
    'character_external_id': character_external_id,
    'text': text,
    'tgt': tgt,
    'ranking_method': 'random',
    'staging': False,
    'model_server_address': None,
    'model_server_address_exp_chars': None,
    'override_prefix': None,
    'override_rank': None,
    'rank_candidates': None,
    'filter_candidates': None,
    'unsanitized_characters': None,
    'prefix_limit': None,
    'prefix_token_limit': None,
    'stream_params': None,
    'enable_tti': None,
    'initial_timeout': None,
    'insert_beginning': None,
    'stream_every_n_steps': 16,
    'chunks_to_pad': 8,
    'is_proactive': False,
    'image_rel_path': '',
    'image_description': '',
    'image_description_type': '',
    'image_origin_type': '',
    'voice_enabled': False,
    'parent_msg_uuid': None,
    'seen_msg_uuids': [],
    'retry_last_user_msg_uuid': None,
    'num_candidates': 1,
    'give_room_introductions': True,
    'mock_response': False,
}
    response = await asyncio.get_running_loop().run_in_executor(None,partial( c_session.post,'https://beta.character.ai/chat/streaming/', cookies=cookies, headers=headers, json=json_data,proxy=proxy))
    if response.status_code==200:
        try:
            text=response.json()['replies'][0]['text']
        except:
            params = {'history_external_id': history_id}
            response = await asyncio.get_running_loop().run_in_executor(None, partial(c_session.get,'https://beta.character.ai/chat/history/msgs/user/', params=params, cookies=cookies, headers=headers,proxy=proxy))
            text=response.json()['messages'][-1]['text']
    else:
        raise ValueError(response.text)
    #print(text)
    #print(access_token)
    return text
    
async def generate_and_play(text: str):
    if USE_QQ_AUDIT==True:
        json_data = {
            "content": text
        }
        async with aiohttp.ClientSession() as asession:
            async with asession.post(f'https://api.q.qq.com/api/json/security/MsgSecCheck?access_token={access_token}', json=json_data) as response:
                data = await response.json()
                if data['errCode'] =='87014':
                    raise ValueError('输入内容违规=>'+text)
                else:
                    if data['errCode']!=0:
                        print(data,'出错默认放行')
    else:
        url = "https://ci-h5-demo-1258125638.ci.ap-chengdu.myqcloud.com/text/auditing"
        headers = {
        'Accept': '*/*',
        'Authorization': access_token['Authorization'],
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/xml',
        'Origin': 'https://cloud.tencent.com',
        'x-ci-security-token': access_token['XCosSecurityToken']    }
        detect_type = "Porn,Terrorism,Politics,Ads,Illegal,Abuse"
        callback = ""
        xml_content = ET.Element("Request")
        input_element = ET.SubElement(xml_content, "Input")
        content_element = ET.SubElement(input_element, "Content")
        content_element.text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        conf_element = ET.SubElement(xml_content, "Conf")
        detect_type_element = ET.SubElement(conf_element, "DetectType")
        detect_type_element.text = detect_type
        callback_element = ET.SubElement(conf_element, "Callback")
        callback_element.text = callback
        xml_str = ET.tostring(xml_content, encoding="utf-8", method="xml")
        async with aiohttp.ClientSession() as session:

            async with session.post(url, headers=headers, data=xml_str) as response:
                response_text = await response.text()
                root = ET.fromstring(response_text)
                label = root.find('./JobsDetail/Label').text
                if label!='Normal':
                    raise ValueError(f'输出违规：{label}={text}')
                print('audit pass')


    # 构造请求数据
    voiceargs[2]=float(voiceargs[2])
    voiceargs[3]=float(voiceargs[3])
    voiceargs[4]=float(voiceargs[4])
    text=[text]
    text.extend(voiceargs)
    print(text)
    payload = {"data": text}

    async with aiohttp.ClientSession() as session:
        async with session.post(f'{voiceurl}/api/generate', json=payload,proxy=proxy) as response:
            if response.status == 200:
                result = await response.json()
                name = result['data'][1]['name']
                wav_bytes = await download_wav(session, f'{voiceurl}/file={name}')
                play_wav(wav_bytes)

async def download_wav(session, url):
    print(url)
    async with session.get(url,proxy=proxy) as response:
        if response.status == 200:
            return io.BytesIO(await response.read())


def play_wav(wav_bytes: io.BytesIO):
    CHUNK = 1024
    wf = wave.open(wav_bytes, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()
# 直播间ID的取值看直播间URL


async def main():
    if USE_QQ_AUDIT==True:
        n=3600
    else:
        n=500
    asyncio.create_task(refresh_access_token_every_n_seconds(appid,appsec,n))
    await run_single_client()
    


async def run_single_client():
    """
    演示监听一个直播间
    """

    room_id = TEST_ROOM_ID    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    #async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        #print(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        if message.msg=='赞':
            return
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        if '{resp}' in msg_str_format:
            resp=await chat(message.msg)
        else:
            resp=''
        print (msg_str_format.format(resp=resp,uname=message.uname,msg=message.msg))
        await generate_and_play(msg_str_format.format(resp=resp,uname=message.uname,msg=message.msg))

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        #print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
        #      f' （{message.coin_type}瓜子x{message.total_coin}）')
        print(gift_str_format.format(gift=message.gift_name,num=message.num,uname=message.uname,msg=message.msg))
        await generate_and_play(gift_str_format.format(gift=message.gift_name,num=message.num,uname=message.uname))

    #async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
    #    print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

   # async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
    #    print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')

def get_args():
    global character_external_id, history_id, voiceargs, appid, appsec, proxy, token, voiceurl,TEST_ROOM_ID,gift_str_format,msg_str_format,USE_QQ_AUDIT
    parser = argparse.ArgumentParser(description='跑路丸AI弹幕姬(也可以做其他角色)')
    parser.add_argument('--character_external_id','-c', type=str, help='角色外部ID，在地址栏里',default='orLhLPUschHtNoqlFtJwU2vPz_HTLM-P8-sk5wV9U48')
    parser.add_argument('--history_id','-hi', type=str, help='会话历史，自己新建会话，依然在地址栏里')
#    parser.add_argument('--tgt', type=str, help='内部id，F12看网络请求',default='internal_id:2d13b7c6-06cc-46da-8bb4-cbbf0b41fdb5')
    parser.add_argument('--appid','-ai', type=str, help='qqaudit=True用，小程序appid，用于文本审核，没有自己去q.qq.com注册')
    parser.add_argument('--appsec','-as', type=str, help='qqaudit=True用，小程序secret，同上')
    parser.add_argument('--proxy','-p', type=str, help='系统代理地址，因为c.ai国内上不去')
    parser.add_argument('-token','-t', type=str, help='c.ai的token，在authencation头')
    parser.add_argument('--voiceurl','-vu', type=str, help='tts api地址，不带最后的斜杠',default='https://mzltest-sayplw.hf.space')
    parser.add_argument('-room','-r', type=int, help='房号',required=True)
    parser.add_argument('--msg_str_format', '-mf',type=str, help='msg_str_format.format(resp=resp,uname=message.uname,msg=message.msg)',default='{uname}说{msg}，我觉得{resp}')
    parser.add_argument('--gift_str_format','-gf', type=str, help='gift_str_format.format(gift=message.gift_name,num=message.num,uname=message.uname)',default='')
    parser.add_argument('--qqaudit','-qa',type=bool,help='用qq小程序那边的审核(默认是腾讯云的那个demo)，未测试',default=False)
    parser.add_argument('--voiceargs','-va',nargs=5,help='语音合成选项，照着界面按顺序填，具体忘了',default=["中文", "group", 0.6 ,0.668, 1.2])

    args = parser.parse_args()
    character_external_id = args.character_external_id
    history_id = args.history_id
#    tgt = args.tgt
    appid = args.appid
    appsec = args.appsec
    proxy = args.proxy
    token = args.token
    voiceurl = args.voiceurl
    TEST_ROOM_ID=args.room
    msg_str_format=args.msg_str_format
    gift_str_format=args.gift_str_format
    USE_QQ_AUDIT=args.qqaudit
    voiceargs=args.voiceargs
    print(voiceargs)


if __name__ == '__main__':
    get_args()
    asyncio.run(main())
