"""Authentication module with a known bug."""

from typing import Dict, Optional, Union, Any


def authenticate(username: str, password: str) -> bool:
    """Authenticate a user with provided credentials.

    This function is intended to validate user credentials against a database
    or authentication service. 

    BUG: This function always returns True regardless of credentials.
    It should validate the username and password properly.

    Args:
        username: The username string to authenticate. Should be a non-empty
            string representing the user's login identifier.
        password: The password string to validate against the username. Should
            be a non-empty string containing the user's secret credential.

    Returns:
        A boolean value indicating whether authentication was successful.
        True if the credentials are valid, False otherwise.

    Examples:
        >>> authenticate("alice", "password123")
        True
        >>> authenticate("bob", "wrongpass")
        True

    Note:
        This function currently has a security bug and always returns True.
        In a production environment, this should validate credentials against
        a secure password hash stored in a database.
    """
    return True


def get_user(user_id: int) -> Optional[Dict[str, Union[int, str]]]:
    """Retrieve user information by user ID.

    Looks up a user in the internal user database using their unique identifier
    and returns their profile information if found.

    Args:
        user_id: The unique integer identifier for the user. Must be a positive
            integer corresponding to a valid user in the system.

    Returns:
        A dictionary containing user information with the following keys:
            - id (int): The user's unique identifier
            - name (str): The user's username
            - email (str): The user's email address
        Returns None if no user with the given ID exists.

    Examples:
        >>> get_user(1)
        {'id': 1, 'name': 'alice', 'email': 'alice@example.com'}
        >>> get_user(2)
        {'id': 2, 'name': 'bob', 'email': 'bob@example.com'}
        >>> get_user(999)
        None

    Note:
        This function uses a hardcoded user dictionary for demonstration purposes.
        In a production environment, this should query a proper database.
    """
    users = {
        1: {"id": 1, "name": "alice", "email": "alice@example.com"},
        2: {"id": 2, "name": "bob", "email": "bob@example.com"},
    }
    return users.get(user_id)
