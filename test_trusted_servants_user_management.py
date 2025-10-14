#!/usr/bin/env python3
"""
Test script for trusted servants user management functionality.
Tests create/update/delete user functionality with maximum privacy and anonymity.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class TrustedServantsUserManagementTester:
    """Test class for trusted servants user management."""
    
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.secretary_token = None
        self.test_users = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log test messages."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user."""
        try:
            # This would normally use magic link authentication
            # For testing, we'll simulate the token
            self.admin_token = "test_admin_token"
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            self.log("Admin authentication successful")
            return True
        except Exception as e:
            self.log(f"Admin authentication failed: {str(e)}", "ERROR")
            return False
    
    def authenticate_secretary(self) -> bool:
        """Authenticate as secretary user."""
        try:
            # This would normally use magic link authentication
            # For testing, we'll simulate the token
            self.secretary_token = "test_secretary_token"
            self.log("Secretary authentication successful")
            return True
        except Exception as e:
            self.log(f"Secretary authentication failed: {str(e)}", "ERROR")
            return False
    
    def test_create_user_basic(self) -> Optional[str]:
        """Test basic user creation."""
        self.log("Testing basic user creation...")
        
        user_data = {
            "preferred_name": "Test Member",
            "timezone": "America/Chicago",
            "language": "en",
            "show_sobriety_date": False,
            "show_in_directory": False,
            "allow_contact": False,
            "notification_preferences": {
                "email_notifications": False,
                "meeting_reminders": True,
                "service_updates": False,
                "marketing": False
            }
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/admin/users",
                json=user_data
            )
            
            if response.status_code == 200:
                user = response.json()
                self.test_users.append(user["id"])
                self.log(f"Basic user created successfully: {user['id']}")
                return user["id"]
            else:
                self.log(f"Basic user creation failed: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Basic user creation error: {str(e)}", "ERROR")
            return None
    
    def test_create_anonymous_user(self) -> Optional[str]:
        """Test anonymous user creation."""
        self.log("Testing anonymous user creation...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/trusted-servants/anonymous-user",
                params={"service_position": "secretary"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.test_users.append(result["user_id"])
                self.log(f"Anonymous user created successfully: {result['user_id']}")
                self.log(f"Privacy level: {result['privacy_level']}")
                return result["user_id"]
            else:
                self.log(f"Anonymous user creation failed: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Anonymous user creation error: {str(e)}", "ERROR")
            return None
    
    def test_update_user_privacy(self, user_id: str) -> bool:
        """Test user privacy settings update."""
        self.log(f"Testing user privacy update for {user_id}...")
        
        update_data = {
            "show_sobriety_date": False,
            "show_in_directory": False,
            "allow_contact": False,
            "notification_preferences": {
                "email_notifications": False,
                "meeting_reminders": False,
                "service_updates": False,
                "marketing": False
            }
        }
        
        try:
            response = self.session.put(
                f"{API_BASE}/admin/users/{user_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                user = response.json()
                self.log(f"User privacy updated successfully for {user_id}")
                return True
            else:
                self.log(f"User privacy update failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"User privacy update error: {str(e)}", "ERROR")
            return False
    
    def test_privacy_audit(self, user_id: str) -> bool:
        """Test privacy compliance audit."""
        self.log(f"Testing privacy audit for {user_id}...")
        
        try:
            response = self.session.get(
                f"{API_BASE}/trusted-servants/users/{user_id}/privacy-audit"
            )
            
            if response.status_code == 200:
                audit = response.json()
                self.log(f"Privacy audit completed for {user_id}")
                self.log(f"Privacy score: {audit['privacy_score']}/{audit['max_score']}")
                self.log(f"Privacy level: {audit['privacy_level']}")
                self.log(f"Privacy percentage: {audit['privacy_percentage']}%")
                return True
            else:
                self.log(f"Privacy audit failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Privacy audit error: {str(e)}", "ERROR")
            return False
    
    def test_get_privacy_compliant_users(self) -> bool:
        """Test getting privacy compliant users."""
        self.log("Testing privacy compliant users retrieval...")
        
        try:
            response = self.session.get(
                f"{API_BASE}/trusted-servants/privacy-compliant-users"
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"Retrieved {result['total_count']} privacy compliant users")
                self.log(f"Privacy compliant: {result['privacy_compliant']}")
                self.log(f"Data minimization: {result['data_minimization']}")
                return True
            else:
                self.log(f"Privacy compliant users retrieval failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Privacy compliant users retrieval error: {str(e)}", "ERROR")
            return False
    
    def test_anonymize_user_data(self, user_id: str) -> bool:
        """Test user data anonymization."""
        self.log(f"Testing user data anonymization for {user_id}...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/trusted-servants/users/{user_id}/anonymize",
                params={"preserve_audit": True}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"User data anonymized successfully for {user_id}")
                self.log(f"Privacy compliant: {result['privacy_compliant']}")
                self.log(f"Audit preserved: {result['preserve_audit']}")
                return True
            else:
                self.log(f"User data anonymization failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"User data anonymization error: {str(e)}", "ERROR")
            return False
    
    def test_soft_delete_user(self, user_id: str) -> bool:
        """Test soft delete user."""
        self.log(f"Testing soft delete for {user_id}...")
        
        try:
            response = self.session.delete(
                f"{API_BASE}/admin/users/{user_id}",
                params={"permanent": False}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"User soft deleted successfully: {result['message']}")
                self.log(f"Permanent: {result['permanent']}")
                return True
            else:
                self.log(f"User soft delete failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"User soft delete error: {str(e)}", "ERROR")
            return False
    
    def test_hard_delete_user(self, user_id: str) -> bool:
        """Test hard delete user with data anonymization."""
        self.log(f"Testing hard delete for {user_id}...")
        
        try:
            response = self.session.delete(
                f"{API_BASE}/admin/users/{user_id}",
                params={"permanent": True}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"User hard deleted successfully: {result['message']}")
                self.log(f"Permanent: {result['permanent']}")
                return True
            else:
                self.log(f"User hard delete failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"User hard delete error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests for trusted servants user management."""
        self.log("Starting trusted servants user management tests...")
        
        # Authenticate
        if not self.authenticate_admin():
            self.log("Cannot proceed without admin authentication", "ERROR")
            return False
        
        # Test basic user creation
        user_id_1 = self.test_create_user_basic()
        if not user_id_1:
            self.log("Basic user creation test failed", "ERROR")
            return False
        
        # Test anonymous user creation
        user_id_2 = self.test_create_anonymous_user()
        if not user_id_2:
            self.log("Anonymous user creation test failed", "ERROR")
            return False
        
        # Test user privacy update
        if not self.test_update_user_privacy(user_id_1):
            self.log("User privacy update test failed", "ERROR")
            return False
        
        # Test privacy audit
        if not self.test_privacy_audit(user_id_1):
            self.log("Privacy audit test failed", "ERROR")
            return False
        
        # Test getting privacy compliant users
        if not self.test_get_privacy_compliant_users():
            self.log("Privacy compliant users test failed", "ERROR")
            return False
        
        # Test data anonymization
        if not self.test_anonymize_user_data(user_id_1):
            self.log("Data anonymization test failed", "ERROR")
            return False
        
        # Test soft delete
        if not self.test_soft_delete_user(user_id_2):
            self.log("Soft delete test failed", "ERROR")
            return False
        
        # Test hard delete (this should be done last)
        if not self.test_hard_delete_user(user_id_1):
            self.log("Hard delete test failed", "ERROR")
            return False
        
        self.log("All trusted servants user management tests completed successfully!", "SUCCESS")
        return True
    
    def cleanup(self):
        """Clean up test data."""
        self.log("Cleaning up test data...")
        
        for user_id in self.test_users:
            try:
                # Try to delete the user if it still exists
                self.session.delete(f"{API_BASE}/admin/users/{user_id}")
                self.log(f"Cleaned up user {user_id}")
            except Exception as e:
                self.log(f"Cleanup error for user {user_id}: {str(e)}", "WARNING")


def main():
    """Main test function."""
    tester = TrustedServantsUserManagementTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n✅ All tests passed! Trusted servants user management is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the logs above.")
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
