"""
Helper functions to parse API calls.
"""
from anatools.lib.print import print_color


def errorhandler(self, response, call):
    responsedata = response.json()
    if self.verbose == 'debug': print(responsedata)
    try: 
        if responsedata['data'][call] is None: raise Exception()
        else: return responsedata['data'][call]
    except:
        if 'errors' in responsedata:
            error_message = responsedata['errors'][-1]['message']
            # Check for common token-related error messages (these are examples, adjust as needed)
            if isinstance(error_message, str): # Ensure error_message is a string
                lower_error_message = error_message.lower()
                if 'unauthorized' in lower_error_message or \
                   'invalid token' in lower_error_message or \
                   'token is invalid' in lower_error_message or \
                   'token expired' in lower_error_message or \
                   'authentication failed' in lower_error_message:
                    print_color("Authentication failed. The provided token may be invalid, expired, or you do not have permission for this operation.", 'ff0000')
                    # Optionally, raise a more specific AuthFailedError if it exists and is appropriate here
            raise Exception(error_message)
        else: raise Exception(f'There was an issue with the {call} API call.')