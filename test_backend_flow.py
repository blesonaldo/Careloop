#!/usr/bin/env python3
"""
Test script to verify the complete backend flow logic for customer management and OpenAI integration
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, init_db
from app.controllers.customer_controller import CustomerController
from app.controllers.auth_controller import AuthController
from app.services.openai_service import OpenAIService
from app.schemas.customer import CustomerCreate, CustomerType

async def test_database_connection():
    """Test database connection and initialization"""
    print("🔍 Testing database connection...")
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_customer_crud():
    """Test customer CRUD operations"""
    print("\n🔍 Testing Customer CRUD operations...")
    
    try:
        # Get database session
        async for db in get_db():
            # Test user ID (assuming user exists)
            test_user_id = 16  # From the logs we saw user ID 16
            
            # Test customer creation
            import random
            unique_phone = f"+2348{random.randint(100000000, 999999999)}"
            unique_email = f"test{random.randint(1000, 9999)}@example.com"
            
            customer_data = CustomerCreate(
                name="Test Customer",
                phone_number=unique_phone,
                email=unique_email,
                customer_type=CustomerType.NEW
            )
            
            print("📝 Creating test customer...")
            created_customer = await CustomerController.create_customer(db, customer_data, test_user_id)
            print(f"✅ Customer created: ID={created_customer.id}, Name={created_customer.name}")
            
            # Test customer retrieval
            print("📖 Retrieving customer...")
            retrieved_customer = await CustomerController.get_customer_by_id(db, created_customer.id, test_user_id)
            print(f"✅ Customer retrieved: {retrieved_customer.name}")
            
            # Test customer listing
            print("📋 Listing customers...")
            customer_list = await CustomerController.get_customers(db, test_user_id, page=1, per_page=10)
            print(f"✅ Found {customer_list.total} customers")
            
            # Test customer update
            print("✏️ Updating customer...")
            from app.schemas.customer import CustomerUpdate
            update_data = CustomerUpdate(name="Updated Test Customer")
            updated_customer = await CustomerController.update_customer(db, created_customer.id, update_data, test_user_id)
            print(f"✅ Customer updated: {updated_customer.name}")
            
            # Test customer deletion
            print("🗑️ Deleting customer...")
            await CustomerController.delete_customer(db, created_customer.id, test_user_id)
            print("✅ Customer deleted successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Customer CRUD test failed: {e}")
        return False

async def test_openai_service():
    """Test OpenAI service for message generation"""
    print("\n🔍 Testing OpenAI message generation...")
    
    try:
        # Test OpenAI service
        openai_service = OpenAIService()
        
        # Test customer data
        test_customer = {
            'name': 'John Doe',
            'phone_number': '+2348155510541',
            'email': 'john@example.com',
            'customer_type': 'new',
            'has_purchased': False,
            'created_at': datetime.now().isoformat()
        }
        
        print("🤖 Generating follow-up message...")
        follow_up_message = await openai_service.generate_follow_up_message(
            customer=test_customer,
            user_name="Test User",
            user_business="Test Business"
        )
        print(f"✅ Follow-up message generated: {follow_up_message}")
        
        print("🤖 Generating sales message...")
        sales_message = await openai_service.generate_sales_message(
            customer=test_customer,
            product="Premium Package",
            user_name="Test User",
            user_business="Test Business"
        )
        print(f"✅ Sales message generated: {sales_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI service test failed: {e}")
        return False

async def test_auth_flow():
    """Test authentication flow"""
    print("\n🔍 Testing authentication flow...")
    
    try:
        async for db in get_db():
            # Test user retrieval
            test_user_id = 16
            user = await AuthController._get_user_by_id(db, test_user_id)
            
            if user:
                print(f"✅ User found: {user.full_name} ({user.email})")
                print(f"   Business: {user.business_name}")
                print(f"   Active: {user.is_active}")
                return True
            else:
                print("❌ Test user not found")
                return False
                
    except Exception as e:
        print(f"❌ Auth flow test failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoint structure"""
    print("\n🔍 Testing API endpoint structure...")
    
    try:
        # Import and test route definitions
        from app.routes.customer import router as customer_router
        from app.routes.message import router as message_router
        from app.routes.auth import router as auth_router
        
        print("✅ Customer routes loaded")
        print(f"   Routes: {[route.path for route in customer_router.routes]}")
        
        print("✅ Message routes loaded")
        print(f"   Routes: {[route.path for route in message_router.routes]}")
        
        print("✅ Auth routes loaded")
        print(f"   Routes: {[route.path for route in auth_router.routes]}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

async def test_frontend_simulation():
    """Simulate frontend API calls"""
    print("\n🔍 Testing frontend API simulation...")
    
    try:
        # Simulate the frontend flow
        print("📱 Simulating frontend flow:")
        print("   1. User logs in → gets auth token")
        print("   2. Frontend loads customers → GET /api/customers")
        print("   3. User selects customer → customer_id sent to backend")
        print("   4. User generates message → POST /api/messages/generate")
        print("   5. Message sent to WhatsApp → opens WhatsApp with message")
        
        # Test the actual API call structure
        test_payload = {
            "customer_id": 1,
            "message_type": "follow_up"
        }
        
        print(f"✅ Frontend payload structure: {json.dumps(test_payload, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend simulation test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Backend Flow Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Authentication Flow", test_auth_flow),
        ("Customer CRUD Operations", test_customer_crud),
        ("OpenAI Message Generation", test_openai_service),
        ("API Endpoint Structure", test_api_endpoints),
        ("Frontend Flow Simulation", test_frontend_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend flow is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Start the server: python main.py")
        print("   2. Open dashboard: http://localhost:8000/careloop-dashboard.html")
        print("   3. Login and test the complete flow")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
