from functools import wraps
from flask import request, current_app, jsonify
from .exceptions import AuthError

def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)
            try:
                # Get the require_auth decorator from AuthManager
                user = current_app.auth_manager.get_current_user()
                if not user:
                    raise AuthError('User not authenticated', 401)

                auth_decorator = current_app.auth_manager.require_auth
                
                # Apply the AuthManager's decorator and get the result
                decorated_func = auth_decorator(f)
                
                # Check roles if specified
                if roles and not any(role in user['roles'] for role in roles):
                    raise AuthError('Insufficient permissions', 403)
                    
                # Now execute the function
                return decorated_func(*args, **kwargs)
            except AuthError as e:
                response = jsonify(e.to_dict())
                response.status_code = e.status_code
                return response
        return decorated
    return decorator 