class BadRequest(Exception):
    '''
    Exception raised for bad requests.
    
    Returns: 
    {
        "error_msg": "string"
    }   
    '''
    pass

class NoUserOnApiKey(Exception):
    '''
    Exception raised when no user is found for the provided API key.
    
    Returns: 
    {
        "error_msg": "string"
    }   
    '''
    pass

class AccessDenied(Exception):
    '''
    Exception raised for access denied errors.
    
    Returns: 
    {
        "detail": "string"
    }   
    '''
    pass

class SystemError(Exception):
    '''
    Exception raised for system errors.

    Returns: 
    {
        "error_msg": "string"
    }
    '''
    pass

class SystemNotReady(Exception):
    '''
    Exception raised when the system is not ready.

    Returns: 
    {
        "error_msg": "string"
    }
    '''
    pass

class ContextItemNotFound(Exception):
    '''
    Exception raised when the context item is not found.

    Returns: 
    {
        "error_msg": "string"
    }
    '''
    pass
