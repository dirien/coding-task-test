"""Authentication module with proper credential validation."""

import hashlib


# In-memory user store with hashed passwords
# Format: {username: {"password_hash": hash, "user_id": id, "email": email}}
USER_STORE = {
    "alice": {
        "password_hash": hashlib.sha256("alice123".encode()).hexdigest(),
        "user_id": 1,
        "email": "alice@example.com"
    },
    "bob": {
        "password_hash": hashlib.sha256("bob456".encode()).hexdigest(),
        "user_id": 2,
        "email": "bob@example.com"
    }
}


def hash_password(password):
    """Hash a password using SHA-256.
    
    Args:
        password: Plain text password string
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password):
    """Authenticate a user with proper credential validation.
    
    Args:
        username: The username to authenticate
        password: The plain text password
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if not username or not password:
        return False
    
    user = USER_STORE.get(username)
    if not user:
        return False
    
    password_hash = hash_password(password)
    return password_hash == user["password_hash"]


def get_user(user_id):
    """Get user by ID.
    
    Args:
        user_id: The user ID to look up
        
    Returns:
        Dictionary with user information or None if not found
    """
    users = {
        1: {"id": 1, "name": "alice", "email": "alice@example.com"},
        2: {"id": 2, "name": "bob", "email": "bob@example.com"},
    }
    return users.get(user_id)


def add_user(username, password, email):
    """Add a new user to the user store.
    
    Args:
        username: The username for the new user
        password: The plain text password
        email: The user's email address
        
    Returns:
        True if user was added successfully, False if username already exists
    """
    if username in USER_STORE:
        return False
    
    user_id = max([user["user_id"] for user in USER_STORE.values()], default=0) + 1
    USER_STORE[username] = {
        "password_hash": hash_password(password),
        "user_id": user_id,
        "email": email
    }
    return True


def remove_user(username):
    """Remove a user from the user store.
    
    Args:
        username: The username to remove
        
    Returns:
        True if user was removed, False if user doesn't exist
    """
    if username in USER_STORE:
        del USER_STORE[username]
        return True
    return False
