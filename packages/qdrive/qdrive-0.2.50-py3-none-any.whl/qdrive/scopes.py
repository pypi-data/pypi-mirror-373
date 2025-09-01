from etiket_client.python_api.scopes import (
    get_scope_by_uuid, get_scope_by_name, get_selected_scope,
    get_scopes as get_scopes_API)
from etiket_client.local.models.scope import ScopeReadWithUsers
from etiket_client.remote.authenticate import validate_login_status
from etiket_client.settings.user_settings import user_settings

from prettytable import PrettyTable

import uuid, typing

def get_scopes() -> 'ScopeList':
    '''
    Retrieve a list of scopes that the user has access to.

    Returns:
        ScopeList: A list of scopes with a custom representation.
    '''
    validate_login_status()
    return ScopeList(get_scopes_API())

def get_scope(scope_name : typing.Union[str, uuid.UUID]) -> ScopeReadWithUsers:
    '''
    Get a scope by name or UUID.

    Args:
        scope_name (str | uuid.UUID): The name or UUID of the scope.

    Returns:
        ScopeReadWithUsers: The scope object.

    Raises:
        TypeError: If the provided scope_name is of an invalid type.
    '''
    # also accept a uuid that is a string
    if isinstance(scope_name, str):
        try:
            scope_name = uuid.UUID(scope_name)
        except ValueError:
            pass
    
    if isinstance(scope_name, uuid.UUID):
        return get_scope_by_uuid(scope_name)
    elif isinstance(scope_name, str):
        return get_scope_by_name(scope_name)
    else:
        raise TypeError(f"Invalid type for scope_name ({type(scope_name)}).")

def set_default_scope(scope_name : typing.Union[str, uuid.UUID, ScopeReadWithUsers]) -> None:
    '''
    Set the default scope for the user.

    Args:
        scope_name (str | uuid.UUID | ScopeReadWithUsers): The name, UUID, or Scope object to set as default.

    Raises:
        TypeError: If the provided scope_name is of an invalid type.
    '''
    validate_login_status()
    if isinstance(scope_name, uuid.UUID):
        scope = get_scope_by_uuid(scope_name)
    elif isinstance(scope_name, str):
        scope = get_scope_by_name(scope_name)
    elif isinstance(scope_name, ScopeReadWithUsers):
        scope = scope_name
    else:
        raise TypeError(f"Invalid type for scope_name ({type(scope_name)}).")
    user_settings.load()
    user_settings.current_scope = str(scope.uuid)
    user_settings.write()
    print(f"Default scope set to {scope_name}")
    
def get_default_scope() -> ScopeReadWithUsers:
    '''
    Get the current default scope from user settings.

    Returns:
        ScopeReadWithUsers: The default scope object.
    '''
    validate_login_status()
    return get_selected_scope()
    
class ScopeList(list):
    '''
    A custom list to hold scope objects with a pretty-print representation.
    '''  
    def __repr__(self):
        table = PrettyTable()
        table.field_names = ["UUID", "Name"]
        
        for scope in self:
            table.add_row([scope.uuid, scope.name])
        
        return table.get_string()