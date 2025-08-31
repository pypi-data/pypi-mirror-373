from .request_utils import *
from .make_request import *
class RPCClient:
    def __init__(self, rpc_url):
        self.rpc = rpc_url

    def rpc_call(self, method=None,params=None,jsonrpc=None,id=None,headers=None,get_post="POST",endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
        """
        Makes an RPC call using the provided method and parameters.
        """
        # Check if the response already exists in the database
        cached_response = fetch_response_data(method, params)
        if cached_response:
            return cached_response

        # If no cached response exists, proceed with the RPC call
        data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
        response = make_request(url, data, headers=headers, endpoint=endpoint,get_post=get_post, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)


        # Save the response to the database for future use
        session = dbConfig().session
        new_entry = ResponseData(signature=request_data['id'], method=method, params=json.dumps(params), response=json.dumps(response))
        session.add(new_entry)
        session.commit()

        return response
