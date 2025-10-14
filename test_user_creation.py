#!/usr/bin/env python3
"""
Comprehensive test script for user creation in the trusted servants section.
Tests frontend, backend, and database integration.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.db.database import get_db, engine
from app.models.user import User, UserRole, ServiceAssignment, UserAuditLog
from app.models.group import TrustedServant
from app.schemas.user import UserCreate, UserResponse, UserProfileResponse
from app.api.endpoints.trusted_servants import router as trusted_servants_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.auth import router as auth_router
from app.services.admin_service import AdminService
from app.services.privacy_service import PrivacyService
from app.core.security import create_access_token
from fastapi import FastAPI
import pytest

# Create test app
app = FastAPI()
app.include_router(trusted_servants_router, prefix="/api/trusted-servants", tags=["trusted-servants"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

class UserCreationTester:
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_database_connection(self):
        """Test database connection and basic operations"""
        try:
            with Session(engine) as db:
                # Test basic query
                user_count = db.query(User).count()
                self.log_test("Database Connection", True, f"Connected successfully, {user_count} users in database")
                return True
        except Exception as e:
            self.log_test("Database Connection", False, f"Failed to connect: {str(e)}")
            return False
    
    def test_user_model_creation(self):
        """Test creating user objects directly in database"""
        try:
            with Session(engine) as db:
                # Create a test user
                test_user = User(
                    preferred_name="Test User",
                    timezone="America/Chicago",
                    language="en",
                    show_sobriety_date=False,
                    show_in_directory=True,
                    allow_contact=False,
                    role=UserRole.MEMBER,
                    is_active=True
                )
                
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                
                # Verify user was created
                assert test_user.id is not None
                assert test_user.preferred_name == "Test User"
                assert test_user.role == UserRole.MEMBER
                
                # Clean up
                db.delete(test_user)
                db.commit()
                
                self.log_test("User Model Creation", True, f"Created and deleted user with ID: {test_user.id}")
                return True
                
        except Exception as e:
            self.log_test("User Model Creation", False, f"Failed to create user: {str(e)}")
            return False
    
    def test_admin_service_user_creation(self):
        """Test user creation through AdminService"""
        try:
            with Session(engine) as db:
                admin_service = AdminService(db)
                
                # Create test user data
                user_create = UserCreate(
                    preferred_name="Admin Test User",
                    timezone="America/Chicago",
                    language="en",
                    show_sobriety_date=False,
                    show_in_directory=False,
                    allow_contact=False
                )
                
                # Create user
                new_user = asyncio.run(admin_service.create_user(
                    user_create=user_create,
                    created_by="test-admin-id",
                    role=UserRole.MEMBER
                ))
                
                # Verify user creation
                assert new_user.id is not None
                assert new_user.preferred_name == "Admin Test User"
                assert new_user.role == UserRole.MEMBER
                assert new_user.show_in_directory == False  # Privacy default
                
                # Clean up
                db.delete(new_user)
                db.commit()
                
                self.log_test("Admin Service User Creation", True, f"Created user via AdminService: {new_user.id}")
                return True
                
        except Exception as e:
            self.log_test("Admin Service User Creation", False, f"Failed: {str(e)}")
            return False
    
    def test_anonymous_user_creation(self):
        """Test creating anonymous user (no name provided)"""
        try:
            with Session(engine) as db:
                admin_service = AdminService(db)
                
                # Create user without preferred_name
                user_create = UserCreate(
                    timezone="America/Chicago",
                    language="en",
                    show_sobriety_date=False,
                    show_in_directory=False,
                    allow_contact=False
                )
                
                new_user = asyncio.run(admin_service.create_user(
                    user_create=user_create,
                    created_by="test-admin-id",
                    role=UserRole.MEMBER
                ))
                
                # Verify anonymous name was generated
                assert new_user.id is not None
                assert new_user.preferred_name is not None
                assert new_user.preferred_name.startswith("Member_")
                
                # Clean up
                db.delete(new_user)
                db.commit()
                
                self.log_test("Anonymous User Creation", True, f"Created anonymous user: {new_user.preferred_name}")
                return True
                
        except Exception as e:
            self.log_test("Anonymous User Creation", False, f"Failed: {str(e)}")
            return False
    
    def test_privacy_service(self):
        """Test privacy service functionality"""
        try:
            with Session(engine) as db:
                privacy_service = PrivacyService(db)
                
                # Create a test user
                test_user = User(
                    preferred_name="Privacy Test User",
                    timezone="America/Chicago",
                    language="en",
                    show_sobriety_date=True,
                    show_in_directory=False,
                    allow_contact=False,
                    role=UserRole.MEMBER,
                    is_active=True,
                    sobriety_date=date(2020, 1, 1)
                )
                
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                
                # Test privacy enforcement
                privacy_data = asyncio.run(privacy_service.enforce_privacy_settings(test_user))
                
                # Verify privacy settings are enforced
                assert privacy_data["preferred_name"] == "Anonymous"  # show_in_directory is False
                assert "sobriety_date" not in privacy_data  # sobriety_date should not be exposed
                assert privacy_data["contact_allowed"] == False
                
                # Clean up
                db.delete(test_user)
                db.commit()
                
                self.log_test("Privacy Service", True, "Privacy settings enforced correctly")
                return True
                
        except Exception as e:
            self.log_test("Privacy Service", False, f"Failed: {str(e)}")
            return False
    
    def test_trusted_servant_creation(self):
        """Test creating trusted servants"""
        try:
            with Session(engine) as db:
                # Create a trusted servant
                servant = TrustedServant(
                    name="Test Secretary",
                    position="secretary",
                    email="secretary@test.com",
                    description="Test secretary position",
                    is_active=True
                )
                
                db.add(servant)
                db.commit()
                db.refresh(servant)
                
                # Verify creation
                assert servant.id is not None
                assert servant.name == "Test Secretary"
                assert servant.position == "secretary"
                
                # Clean up
                db.delete(servant)
                db.commit()
                
                self.log_test("Trusted Servant Creation", True, f"Created trusted servant: {servant.name}")
                return True
                
        except Exception as e:
            self.log_test("Trusted Servant Creation", False, f"Failed: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints for user creation"""
        try:
            # First, create an admin user for authentication
            with Session(engine) as db:
                admin_user = User(
                    preferred_name="Test Admin",
                    role=UserRole.ADMIN,
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                
                # Create access token
                token = create_access_token(data={"sub": str(admin_user.id)})
                
                # Test user creation endpoint
                user_data = {
                    "preferred_name": "API Test User",
                    "timezone": "America/Chicago",
                    "language": "en",
                    "show_sobriety_date": False,
                    "show_in_directory": False,
                    "allow_contact": False
                }
                
                response = self.client.post(
                    "/api/trusted-servants/users",
                    json=user_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    user_response = response.json()
                    assert user_response["preferred_name"] == "API Test User"
                    
                    # Clean up
                    created_user = db.query(User).filter(User.id == user_response["id"]).first()
                    if created_user:
                        db.delete(created_user)
                    db.delete(admin_user)
                    db.commit()
                    
                    self.log_test("API User Creation", True, f"Created user via API: {user_response['id']}")
                    return True
                else:
                    self.log_test("API User Creation", False, f"API returned status {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            self.log_test("API User Creation", False, f"Failed: {str(e)}")
            return False
    
    def test_data_integrity(self):
        """Test data integrity and constraints"""
        try:
            with Session(engine) as db:
                # Test unique email constraint
                user1 = User(
                    email="test@example.com",
                    preferred_name="User 1",
                    role=UserRole.MEMBER,
                    is_active=True
                )
                user2 = User(
                    email="test@example.com",  # Same email
                    preferred_name="User 2",
                    role=UserRole.MEMBER,
                    is_active=True
                )
                
                db.add(user1)
                db.commit()
                db.refresh(user1)
                
                db.add(user2)
                try:
                    db.commit()
                    # Should not reach here due to unique constraint
                    self.log_test("Data Integrity", False, "Unique email constraint not enforced")
                    db.delete(user1)
                    db.delete(user2)
                    db.commit()
                    return False
                except Exception:
                    # Expected behavior - unique constraint violation
                    db.rollback()
                    db.delete(user1)
                    db.commit()
                    
                    self.log_test("Data Integrity", True, "Unique constraints enforced correctly")
                    return True
                    
        except Exception as e:
            self.log_test("Data Integrity", False, f"Failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🧪 Starting User Creation Tests")
        print("=" * 50)
        
        tests = [
            self.test_database_connection,
            self.test_user_model_creation,
            self.test_admin_service_user_creation,
            self.test_anonymous_user_creation,
            self.test_privacy_service,
            self.test_trusted_servant_creation,
            self.test_api_endpoints,
            self.test_data_integrity
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.log_test(test.__name__, False, f"Unexpected error: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! User creation system is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "results": self.test_results
        }

def main():
    """Main function to run the tests"""
    tester = UserCreationTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to test_results.json")
    
    return 0 if results["passed_tests"] == results["total_tests"] else 1

if __name__ == "__main__":
    sys.exit(main())
