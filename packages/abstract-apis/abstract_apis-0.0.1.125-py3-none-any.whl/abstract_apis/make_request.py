from .request_utils import *
import logging
# Suppress logs below WARNING level
logging.basicConfig(level=logging.WARNING)
def make_request(url, data=None,json_data=None, headers=None, get_post=None, endpoint=None,files=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None,logger=True):
    response = None
    values = get_values_js(url=url,endpoint=endpoint,data=data,headers=headers)
    get_post = str(get_post or ('POST' if data == None else 'GET')).upper()
    if get_post == 'POST':
        response = requests.post(**values)
    elif get_post == 'GET':
        response = requests.get(**values)
    else:
        raise ValueError(f"Unsupported HTTP method: {values.get('method')}")
    got_response = get_response(response, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
    
    got_status_code,got_retry_after = False,False
    if status_code or retry_after:
        if status_code:
            got_status_code = get_status_code(response)
        if retry_after:
            got_retry_after = get_retry_after(response)
        if got_status_code != False and got_retry_after == False :
            return got_response, got_status_code
        elif got_retry_after != False and got_status_code ==  False:
            return got_response,  got_retry_after
        return got_response, got_status_code, got_retry_after
    return got_response
def getRpcData(method=None,params=None,jsonrpc=None,id=None):
    return {
            "jsonrpc": jsonrpc or "2.0",
            "id": 0,
            "method": method,
            "params": params,
        }
def postRequest(url, data=None, headers=None, endpoint=None,request_file_path=None,files=None,status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None,**kwargs):
    if request_file_path:
        files = get_request_file(request_file_path)
    data = data or kwargs
    return make_request(url, data=data, headers=headers, endpoint=endpoint, get_post='POST',files=files, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

def getRequest(url, data=None, headers=None, endpoint=None,request_file_path=None,files=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None,**kwargs):
    if request_file_path:
        files = get_request_file(request_file_path)
    data = data or kwargs
    return make_request(url, data=data, headers=headers, endpoint=endpoint, get_post='GET', files=files, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

def getRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return getRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

def postRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, get_post='GET',endpoint=None, status_code=False, retry_after=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return make_request(url=url, data=data, headers=headers, endpoint=endpoint,get_post='POST', status_code=status_code, retry_after=retry_after, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)


