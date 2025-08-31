from .request_utils import *
import aiohttp,asyncio
def run_async(coro):
    """
    Centralized function to run asynchronous coroutines, managing the event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        # If already in a running loop, schedule the coroutine
        return asyncio.ensure_future(coro)
    except RuntimeError:
        # No running event loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
def get_async_response(async_function, *args, **kwargs):
    """
    Run asynchronous function and return the result using run_async.
    """
    coro = async_function(*args, **kwargs)
    return run_async(coro)

async def async_get_response(response, raw_response=False, response_result=None, load_nested_json=True,status_code=False):
    status = response.status
    if not raw_response:
        response_json = None
        if response.content_type == 'application/json':
            try:
                # Extract the JSON content from the response
                response_json = await response.json()  # Correct usage with parentheses
            except Exception as e:
                print(f"Failed to decode JSON response: {e}")
                response_json = await response.text()  # Fallback to raw text if JSON fails

        if isinstance(response_json, dict) and response_result != False:
            response_json = response_json.get(response_result, response_json)
        
        if load_nested_json and response_json:
            response_json = load_inner_json(response_json)
        response = response_json
    if status_code:
        return (response,status)
    return response

async def getAsyncRequest(url, data=None, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url, data=data, headers=headers, endpoint=endpoint)
        async with session.get(**values) as response:
            return await async_get_response(response=response,status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
        
async def postAsyncRequest(url, data=None, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url, data=data, headers=headers, endpoint=endpoint)
        async with session.post(**values) as response:
            return await async_get_response(response=response,status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncMakeRequest(url, data=None, headers=None, get_post=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    if get_post.upper() == 'POST':
        return await postAsyncRequest(url, data=data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)
    elif get_post.upper() == 'GET':
        return await getAsyncRequest(url, data=data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)
    else:
        raise ValueError(f"Unsupported HTTP method: {get_post}")

async def asyncPostRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='POST', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

async def asyncGetRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='GET', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

async def asyncGetRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await asyncGetRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)

async def asyncPostRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True,auth=None):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await asyncPostRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json,auth=auth)
