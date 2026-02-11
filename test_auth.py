"""Unit tests for the authentication module."""

import unittest
import hashlib
from auth import (
    authenticate, 
    get_user, 
    hash_password, 
    add_user, 
    remove_user,
    USER_STORE
)


class TestAuthentication(unittest.TestCase):
    """Test cases for authentication functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset USER_STORE to default state
        USER_STORE.clear()
        USER_STORE.update({
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
        })
    
    def test_authenticate_valid_credentials_alice(self):
        """Test authentication with valid credentials for alice."""
        result = authenticate("alice", "alice123")
        self.assertTrue(result, "Should return True for valid credentials")
    
    def test_authenticate_valid_credentials_bob(self):
        """Test authentication with valid credentials for bob."""
        result = authenticate("bob", "bob456")
        self.assertTrue(result, "Should return True for valid credentials")
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        result = authenticate("alice", "wrongpassword")
        self.assertFalse(result, "Should return False for invalid password")
    
    def test_authenticate_invalid_username(self):
        """Test authentication with non-existent username."""
        result = authenticate("charlie", "somepassword")
        self.assertFalse(result, "Should return False for non-existent user")
    
    def test_authenticate_empty_username(self):
        """Test authentication with empty username."""
        result = authenticate("", "password")
        self.assertFalse(result, "Should return False for empty username")
    
    def test_authenticate_empty_password(self):
        """Test authentication with empty password."""
        result = authenticate("alice", "")
        self.assertFalse(result, "Should return False for empty password")
    
    def test_authenticate_none_username(self):
        """Test authentication with None as username."""
        result = authenticate(None, "password")
        self.assertFalse(result, "Should return False for None username")
    
    def test_authenticate_none_password(self):
        """Test authentication with None as password."""
        result = authenticate("alice", None)
        self.assertFalse(result, "Should return False for None password")
    
    def test_authenticate_case_sensitive_username(self):
        """Test that username is case-sensitive."""
        result = authenticate("Alice", "alice123")
        self.assertFalse(result, "Username should be case-sensitive")
    
    def test_authenticate_case_sensitive_password(self):
        """Test that password is case-sensitive."""
        result = authenticate("alice", "Alice123")
        self.assertFalse(result, "Password should be case-sensitive")


class TestHashPassword(unittest.TestCase):
    """Test cases for password hashing."""
    
    def test_hash_password_consistency(self):
        """Test that hashing the same password produces the same hash."""
        password = "testpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertEqual(hash1, hash2, "Same password should produce same hash")
    
    def test_hash_password_different_passwords(self):
        """Test that different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        self.assertNotEqual(hash1, hash2, "Different passwords should produce different hashes")
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        result = hash_password("test")
        self.assertIsInstance(result, str, "Hash should be a string")
    
    def test_hash_password_correct_algorithm(self):
        """Test that hash uses SHA-256."""
        password = "test"
        expected = hashlib.sha256(password.encode()).hexdigest()
        result = hash_password(password)
        self.assertEqual(result, expected, "Should use SHA-256 hashing")


class TestGetUser(unittest.TestCase):
    """Test cases for get_user functionality."""
    
    def test_get_user_valid_id_1(self):
        """Test getting user with ID 1."""
        user = get_user(1)
        self.assertIsNotNone(user, "Should return user data")
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["name"], "alice")
        self.assertEqual(user["email"], "alice@example.com")
    
    def test_get_user_valid_id_2(self):
        """Test getting user with ID 2."""
        user = get_user(2)
        self.assertIsNotNone(user, "Should return user data")
        self.assertEqual(user["id"], 2)
        self.assertEqual(user["name"], "bob")
        self.assertEqual(user["email"], "bob@example.com")
    
    def test_get_user_invalid_id(self):
        """Test getting user with non-existent ID."""
        user = get_user(999)
        self.assertIsNone(user, "Should return None for non-existent user")
    
    def test_get_user_none_id(self):
        """Test getting user with None as ID."""
        user = get_user(None)
        self.assertIsNone(user, "Should return None for None ID")


class TestAddUser(unittest.TestCase):
    """Test cases for add_user functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset USER_STORE to default state
        USER_STORE.clear()
        USER_STORE.update({
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
        })
    
    def test_add_user_success(self):
        """Test successfully adding a new user."""
        result = add_user("charlie", "charlie789", "charlie@example.com")
        self.assertTrue(result, "Should return True when user is added")
        self.assertIn("charlie", USER_STORE, "User should be in USER_STORE")
        self.assertTrue(
            authenticate("charlie", "charlie789"),
            "New user should be able to authenticate"
        )
    
    def test_add_user_duplicate_username(self):
        """Test adding a user with existing username."""
        result = add_user("alice", "newpassword", "newalice@example.com")
        self.assertFalse(result, "Should return False for duplicate username")
        # Verify original user is unchanged
        self.assertTrue(
            authenticate("alice", "alice123"),
            "Original user credentials should remain unchanged"
        )
    
    def test_add_user_assigns_unique_id(self):
        """Test that new users get unique IDs."""
        add_user("charlie", "password", "charlie@example.com")
        charlie_id = USER_STORE["charlie"]["user_id"]
        self.assertEqual(charlie_id, 3, "New user should get next available ID")


class TestRemoveUser(unittest.TestCase):
    """Test cases for remove_user functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset USER_STORE to default state
        USER_STORE.clear()
        USER_STORE.update({
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
        })
    
    def test_remove_user_success(self):
        """Test successfully removing a user."""
        result = remove_user("alice")
        self.assertTrue(result, "Should return True when user is removed")
        self.assertNotIn("alice", USER_STORE, "User should be removed from USER_STORE")
        self.assertFalse(
            authenticate("alice", "alice123"),
            "Removed user should not be able to authenticate"
        )
    
    def test_remove_user_nonexistent(self):
        """Test removing a non-existent user."""
        result = remove_user("charlie")
        self.assertFalse(result, "Should return False for non-existent user")


class TestIntegration(unittest.TestCase):
    """Integration tests for the authentication module."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset USER_STORE to default state
        USER_STORE.clear()
        USER_STORE.update({
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
        })
    
    def test_full_user_lifecycle(self):
        """Test complete user lifecycle: add, authenticate, remove."""
        # Add a new user
        self.assertTrue(add_user("charlie", "charlie789", "charlie@example.com"))
        
        # Verify user can authenticate
        self.assertTrue(authenticate("charlie", "charlie789"))
        self.assertFalse(authenticate("charlie", "wrongpassword"))
        
        # Remove the user
        self.assertTrue(remove_user("charlie"))
        
        # Verify user can no longer authenticate
        self.assertFalse(authenticate("charlie", "charlie789"))
    
    def test_multiple_failed_authentications(self):
        """Test that multiple failed authentications don't affect subsequent valid ones."""
        # Multiple failed attempts
        self.assertFalse(authenticate("alice", "wrong1"))
        self.assertFalse(authenticate("alice", "wrong2"))
        self.assertFalse(authenticate("alice", "wrong3"))
        
        # Valid authentication should still work
        self.assertTrue(authenticate("alice", "alice123"))


if __name__ == "__main__":
    unittest.main()
