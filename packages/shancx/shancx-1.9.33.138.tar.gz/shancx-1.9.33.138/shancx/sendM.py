import requests
import datetime 
def sendMES(message,key='0f313-17b2-4e3d-84b8-3f9c290fa596',NN = None):
    webHookUrl = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={NN}{key}'
    if NN=="MT":
       webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8b7df0c1-bde0-4091-9e11-f77519439823"
    elif NN=="MT1":
       webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=461a6eab-90e1-48d9-bb7e-ee91f6e16131"
    elif NN=="WT":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=de0c3cc5-d32b-4631-b807-9db3ae44c6df"
    elif NN=="H9":
       webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=652ed7d5-7f31-437c-90e2-25efce6a8a8a"
    elif NN=="GOES18":
       webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=32c59698-92ff-4049-a1bb-12908fb7b0da"
    elif NN=="GOES19":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=aac8d435-2d21-4c5e-a465-7b51396f4b25"  
    elif NN=="FY4B":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0f4e28f6-af3b-44b0-9889-827df8f3dcc1" 
    elif NN=="MSGIN":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7a4e8f4a-27a7-451b-9b31-dd0339a25e85" 
    elif NN=="MSG":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a4222299-a66a-4909-834a-8deeda35c60a" 
    elif NN=="LAST":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1b975d3f-0f8c-4ac8-97aa-7de3c5b75802" 
    elif NN=="MTGH":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=64ec68e0-28dd-40d2-9c23-7b7f3808030c" 
    elif NN=="GOES19NA":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=790f59bc-64c5-4f37-9795-f1c848ab3fa0" 
    elif NN=="GOES19SA":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a195b0e1-ab72-4071-9300-2a148b5e4744" 
        
    elif NN=="H9CHNNEAS":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=504d8947-b69d-4f0e-8de4-384a1966d7e2" 
    elif NN=="H9SEAS":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2db6e407-5397-44c9-b3cf-3aa27900627c" 
    elif NN=="H9OC":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b11a7591-f917-48ba-9bdf-8754aebefd01"         

    elif NN=="MSGER":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ad6cd972-599d-426f-8dfd-81e930ad40cd" 
    elif NN=="MSGAF":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5797fbe9-1c19-4a67-a6fc-83a85cb464a7"      
    elif NN=="GOES18C":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4ddac32b-692b-4aa0-9d69-0e655552ff17"   
        

    elif NN=="GFS":
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=13f39c2f-e191-4100-b1ee-7316ac9c2451"    
    else:
        webHookUrl ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=13f39c2f-e191-4100-b1ee-7316ac9c2451"
        
    try:
        url=webHookUrl
        headers = {"Content-Type":"application/json"}
        data = {'msgtype':'text','text':{"content":message}}
        res = requests.post(url,json=data,headers=headers)
    except Exception as e:
        print(e)
 