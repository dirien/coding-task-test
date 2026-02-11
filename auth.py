"""Authentication module with a known bug."""


def authenticate(username, password):
    """Authenticate a user.

    BUG: This function always returns True regardless of credentials.
    It should validate the username and password properly.
    """
    return True


def get_user(user_id):
    """Get user by ID."""
    users = {
        1: {"id": 1, "name": "alice", "email": "alice@example.com"},
        2: {"id": 2, "name": "bob", "email": "bob@example.com"},
    }
    return users.get(user_id)


def hello():
    """Return a greeting message."""
    return "Hello from CodingTask Chat UI"
