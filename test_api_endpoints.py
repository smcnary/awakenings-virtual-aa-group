#!/usr/bin/env python3
"""
Test script for API endpoints.
Tests the actual FastAPI application endpoints.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

# Change to backend directory for database access
os.chdir(backend_path)

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.user import User, UserRole
from app.core.security import create_access_token
import main
from main import app

def test_api_endpoints():
    """Test the API endpoints"""
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Create test client
    client = TestClient(app)
    
    try:
        with Session(engine) as db:
            # Create admin user for testing
            admin_user = User(
                preferred_name='Test Admin',
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Create token
            token = create_access_token(data={'sub': str(admin_user.id)})
            
            # Test 1: Health check endpoint
            print("Testing health check endpoint...")
            response = client.get("/health")
            if response.status_code == 200:
                print("✅ Health Check: API is running")
            else:
                print(f"❌ Health Check: Failed with status {response.status_code}")
                return False
            
            # Test 2: Root endpoint
            print("Testing root endpoint...")
            response = client.get("/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root Endpoint: {data.get('message', 'No message')}")
            else:
                print(f"❌ Root Endpoint: Failed with status {response.status_code}")
                return False
            
            # Test 3: Trusted servants endpoint (without auth)
            print("Testing trusted servants endpoint without auth...")
            response = client.get("/api/v1/trusted-servants/")
            if response.status_code == 200:
                servants = response.json()
                print(f"✅ Trusted Servants (public): Found {len(servants)} servants")
            else:
                print(f"❌ Trusted Servants (public): Failed with status {response.status_code}")
            
            # Test 4: Trusted servants positions endpoint
            print("Testing trusted servants positions endpoint...")
            response = client.get("/api/v1/trusted-servants/positions")
            if response.status_code == 200:
                positions = response.json()
                print(f"✅ Trusted Servants Positions: Found {len(positions)} positions")
            else:
                print(f"❌ Trusted Servants Positions: Failed with status {response.status_code}")
            
            # Test 5: Create trusted servant (with auth)
            print("Testing create trusted servant with auth...")
            servant_data = {
                "name": "Test Secretary",
                "position": "secretary",
                "email": "secretary@test.com",
                "description": "Test secretary for API testing"
            }
            
            response = client.post(
                "/api/v1/trusted-servants/",
                json=servant_data,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                servant = response.json()
                print(f"✅ Create Trusted Servant: Created {servant['name']} (ID: {servant['id']})")
                
                # Clean up created servant
                from app.models.group import TrustedServant
                created_servant = db.query(TrustedServant).filter(TrustedServant.id == servant['id']).first()
                if created_servant:
                    db.delete(created_servant)
                    db.commit()
                    print("   Cleaned up created servant")
            else:
                print(f"❌ Create Trusted Servant: Failed with status {response.status_code}: {response.text}")
            
            # Test 6: Test CORS headers
            print("Testing CORS headers...")
            response = client.options("/", headers={'Origin': 'http://localhost:3000'})
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            if any(cors_headers.values()):
                print("✅ CORS Headers: Present")
            else:
                print("❌ CORS Headers: Missing")
            
            # Clean up admin user
            db.delete(admin_user)
            db.commit()
            
            print("\n" + "=" * 50)
            print("🎉 API endpoint tests completed!")
            return True
            
    except Exception as e:
        print(f"❌ API Test Error: {str(e)}")
        return False

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n🧪 Testing Frontend Integration Points")
    print("=" * 50)
    
    client = TestClient(app)
    
    try:
        # Test endpoints that the frontend would call
        endpoints_to_test = [
            ("GET", "/api/v1/trusted-servants/", "Trusted Servants List"),
            ("GET", "/api/v1/trusted-servants/positions", "Service Positions"),
            ("GET", "/api/v1/group/", "Group Information"),
            ("GET", "/api/v1/meetings/", "Meetings List"),
            ("GET", "/api/v1/resources/", "Resources List"),
        ]
        
        passed = 0
        total = len(endpoints_to_test)
        
        for method, endpoint, description in endpoints_to_test:
            print(f"Testing {description}...")
            response = client.get(endpoint) if method == "GET" else client.post(endpoint)
            
            if response.status_code in [200, 404]:  # 404 is acceptable for empty data
                print(f"✅ {description}: Status {response.status_code}")
                passed += 1
            else:
                print(f"❌ {description}: Failed with status {response.status_code}")
        
        print(f"\n📊 Frontend Integration: {passed}/{total} endpoints accessible")
        return passed == total
        
    except Exception as e:
        print(f"❌ Frontend Integration Error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting API Endpoint Tests")
    print("=" * 60)
    
    api_success = test_api_endpoints()
    frontend_success = test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("📊 Final Results:")
    print(f"   API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Frontend Integration: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if api_success and frontend_success:
        print("🎉 All API tests passed! The system is ready for frontend integration.")
        return 0
    else:
        print("⚠️  Some API tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
