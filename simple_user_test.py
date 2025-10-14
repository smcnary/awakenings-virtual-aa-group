#!/usr/bin/env python3
"""
Simple test script for user creation functionality.
Tests database operations and core services.
"""

import sys
import os
from datetime import datetime, date

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Change to backend directory for database access
os.chdir(backend_path)

from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.user import User, UserRole, ServiceAssignment, UserAuditLog
from app.models.group import TrustedServant
from app.schemas.user import UserCreate
from app.services.admin_service import AdminService
from app.services.privacy_service import PrivacyService
import asyncio

def test_database_connection():
    """Test database connection"""
    try:
        with Session(engine) as db:
            user_count = db.query(User).count()
            print(f"✅ Database Connection: Connected successfully, {user_count} users in database")
            return True
    except Exception as e:
        print(f"❌ Database Connection: Failed to connect: {str(e)}")
        return False

def test_user_model_creation():
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
            
            print(f"✅ User Model Creation: Created and deleted user with ID: {test_user.id}")
            return True
            
    except Exception as e:
        print(f"❌ User Model Creation: Failed to create user: {str(e)}")
        return False

def test_admin_service_user_creation():
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
            
            print(f"✅ Admin Service User Creation: Created user via AdminService: {new_user.id}")
            return True
            
    except Exception as e:
        print(f"❌ Admin Service User Creation: Failed: {str(e)}")
        return False

def test_anonymous_user_creation():
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
            
            print(f"✅ Anonymous User Creation: Created anonymous user: {new_user.preferred_name}")
            return True
            
    except Exception as e:
        print(f"❌ Anonymous User Creation: Failed: {str(e)}")
        return False

def test_privacy_service():
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
            assert "sobriety_date" in privacy_data  # sobriety_date should be exposed when show_sobriety_date=True
            assert privacy_data["contact_allowed"] == False
            
            # Clean up
            db.delete(test_user)
            db.commit()
            
            print("✅ Privacy Service: Privacy settings enforced correctly")
            return True
            
    except Exception as e:
        print(f"❌ Privacy Service: Failed: {str(e)}")
        return False

def test_trusted_servant_creation():
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
            
            print(f"✅ Trusted Servant Creation: Created trusted servant: {servant.name}")
            return True
            
    except Exception as e:
        print(f"❌ Trusted Servant Creation: Failed: {str(e)}")
        return False

def test_data_integrity():
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
            
            db.add(user1)
            db.commit()
            db.refresh(user1)
            
            # Try to create another user with the same email
            user2 = User(
                email="test@example.com",  # Same email
                preferred_name="User 2",
                role=UserRole.MEMBER,
                is_active=True
            )
            
            db.add(user2)
            try:
                db.commit()
                # Should not reach here due to unique constraint
                print("❌ Data Integrity: Unique email constraint not enforced")
                db.delete(user1)
                db.delete(user2)
                db.commit()
                return False
            except Exception:
                # Expected behavior - unique constraint violation
                db.rollback()
                db.delete(user1)
                db.commit()
                
                print("✅ Data Integrity: Unique constraints enforced correctly")
                return True
                
    except Exception as e:
        print(f"❌ Data Integrity: Failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Simple User Creation Tests")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_user_model_creation,
        test_admin_service_user_creation,
        test_anonymous_user_creation,
        test_privacy_service,
        test_trusted_servant_creation,
        test_data_integrity
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! User creation system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
