import base64
import requests
# www.jfbym.com  注册后登录去用户中心
with open('img.png', 'rb') as f:
    b = base64.b64encode(f.read()).decode()  ## 图片二进制流base64字符串
def verify():
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "token": "MlGR4NhGZrep5kQM88ZkbfmMB5aDIUgbdQzxVY7nLqY",
        "type": "10110",
        "image": b,
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data).json()
    print(response)
if __name__ == '__main__':
    verify()