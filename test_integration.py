#!/usr/bin/env python3
"""
Integration Test Suite
=====================
Test script to verify that all integration components work together properly.
Tests data sharing, cross-tool communication, and unified workflows.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import sys
import os
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import integration components
try:
    from unified_integration_manager import (
        integration_manager, ToolType, EventType, IntegrationEvent,
        SharedPhoneNumber, UnifiedSession
    )
    from integration_adapters import (
        telegram_adapter, sms_adapter, workflow_manager
    )
    from unified_styling import theme_manager, style_preferences
    print("✅ Successfully imported all integration components")
except ImportError as e:
    print(f"❌ Failed to import integration components: {e}")
    sys.exit(1)

class IntegrationTester:
    """Test suite for integration functionality"""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Integration Test Suite\n")
        print("=" * 60)
        
        # Test individual components
        self.test_integration_manager()
        self.test_phone_number_management()
        self.test_verification_codes()
        self.test_unified_sessions()
        self.test_shared_proxies()
        self.test_event_system()
        self.test_cross_tool_workflows()
        self.test_data_synchronization()
        self.test_styling_system()
        self.test_database_operations()
        
        # Print results
        self.print_test_results()
    
    def test_integration_manager(self):
        """Test integration manager initialization"""
        print("📋 Testing Integration Manager...")
        
        try:
            # Test manager is initialized
            assert integration_manager is not None
            self.record_test("Integration Manager", "Initialization", True)
            
            # Test database setup
            assert os.path.exists(integration_manager.db_path)
            self.record_test("Integration Manager", "Database Creation", True)
            
            # Test statistics
            stats = integration_manager.get_statistics()
            assert isinstance(stats, dict)
            self.record_test("Integration Manager", "Statistics Retrieval", True)
            
            print("✅ Integration Manager tests passed\n")
            
        except Exception as e:
            self.record_test("Integration Manager", "General", False, str(e))
            print(f"❌ Integration Manager test failed: {e}\n")
    
    def test_phone_number_management(self):
        """Test phone number management"""
        print("📱 Testing Phone Number Management...")
        
        try:
            # Create test phone number
            test_phone = SharedPhoneNumber(
                phone_number="+1 555 TEST",
                country_code="US",
                service="Telegram",
                provider="Test Provider",
                purchase_date=datetime.now(),
                status="available",
                cost=0.99
            )
            
            # Add phone number
            success = integration_manager.add_phone_number(test_phone)
            assert success
            self.record_test("Phone Management", "Add Phone Number", True)
            
            # Retrieve available numbers
            numbers = integration_manager.get_available_numbers("Telegram")
            assert len(numbers) > 0
            self.record_test("Phone Management", "Get Available Numbers", True)
            
            # Reserve number
            reserved = integration_manager.reserve_number("+1 555 TEST", "test_account")
            assert reserved
            self.record_test("Phone Management", "Reserve Number", True)
            
            print("✅ Phone Number Management tests passed\n")
            
        except Exception as e:
            self.record_test("Phone Management", "General", False, str(e))
            print(f"❌ Phone Number Management test failed: {e}\n")
    
    def test_verification_codes(self):
        """Test verification code management"""
        print("📩 Testing Verification Codes...")
        
        try:
            # Add verification code
            integration_manager.add_verification_code("+1 555 TEST", "123456", "Telegram")
            self.record_test("Verification Codes", "Add Code", True)
            
            # Retrieve codes
            codes = integration_manager.get_verification_codes("+1 555 TEST")
            assert len(codes) > 0
            assert codes[0]['code'] == "123456"
            self.record_test("Verification Codes", "Get Codes", True)
            
            # Mark code as used
            integration_manager.mark_code_used(codes[0]['id'])
            self.record_test("Verification Codes", "Mark Code Used", True)
            
            print("✅ Verification Codes tests passed\n")
            
        except Exception as e:
            self.record_test("Verification Codes", "General", False, str(e))
            print(f"❌ Verification Codes test failed: {e}\n")
    
    def test_unified_sessions(self):
        """Test unified session management"""
        print("🔗 Testing Unified Sessions...")
        
        try:
            # Create test session
            test_session = UnifiedSession(
                session_id="test_session_001",
                phone_number="+1 555 TEST",
                telegram_session_name="test_tg_session",
                sms_provider_data={"provider": "Test Provider"},
                proxy_settings={"host": "127.0.0.1", "port": 8080},
                created_at=datetime.now(),
                status="active"
            )
            
            # Create session
            success = integration_manager.create_unified_session(test_session)
            assert success
            self.record_test("Unified Sessions", "Create Session", True)
            
            # Retrieve session
            retrieved_session = integration_manager.get_unified_session("test_session_001")
            assert retrieved_session is not None
            assert retrieved_session.phone_number == "+1 555 TEST"
            self.record_test("Unified Sessions", "Get Session", True)
            
            print("✅ Unified Sessions tests passed\n")
            
        except Exception as e:
            self.record_test("Unified Sessions", "General", False, str(e))
            print(f"❌ Unified Sessions test failed: {e}\n")
    
    def test_shared_proxies(self):
        """Test shared proxy management"""
        print("🌐 Testing Shared Proxies...")
        
        try:
            # Add shared proxy
            success = integration_manager.add_shared_proxy(
                host="127.0.0.1",
                port=8080,
                username="testuser",
                password="testpass",
                proxy_type="socks5"
            )
            assert success
            self.record_test("Shared Proxies", "Add Proxy", True)
            
            # Get available proxies
            proxies = integration_manager.get_available_proxies()
            assert len(proxies) > 0
            self.record_test("Shared Proxies", "Get Proxies", True)
            
            print("✅ Shared Proxies tests passed\n")
            
        except Exception as e:
            self.record_test("Shared Proxies", "General", False, str(e))
            print(f"❌ Shared Proxies test failed: {e}\n")
    
    def test_event_system(self):
        """Test integration event system"""
        print("📡 Testing Event System...")
        
        try:
            # Create test event
            test_event = IntegrationEvent(
                event_type=EventType.SMS_CODE_RECEIVED,
                source_tool=ToolType.SMS_MARKETPLACE,
                data={
                    "phone_number": "+1 555 TEST",
                    "code": "789012",
                    "service": "Telegram"
                },
                timestamp=datetime.now()
            )
            
            # Emit event
            integration_manager.emit_event(test_event)
            self.record_test("Event System", "Emit Event", True)
            
            # Wait a moment for event processing
            time.sleep(0.5)
            
            # Check if event was stored in database
            conn = sqlite3.connect(integration_manager.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM integration_events WHERE event_type = ?", 
                         (EventType.SMS_CODE_RECEIVED.value,))
            count = cursor.fetchone()[0]
            conn.close()
            
            assert count > 0
            self.record_test("Event System", "Event Storage", True)
            
            print("✅ Event System tests passed\n")
            
        except Exception as e:
            self.record_test("Event System", "General", False, str(e))
            print(f"❌ Event System test failed: {e}\n")
    
    def test_cross_tool_workflows(self):
        """Test cross-tool workflow functionality"""
        print("⚙️ Testing Cross-Tool Workflows...")
        
        try:
            # Test workflow creation
            workflow_result = workflow_manager.create_telegram_account_full_workflow(
                auto_purchase=True,
                country='US'
            )
            
            assert workflow_result['status'] in ['starting', 'waiting_for_verification']
            self.record_test("Workflows", "Create TG Account Workflow", True)
            
            # Test workflow retrieval
            active_workflows = workflow_manager.get_active_workflows()
            assert len(active_workflows) > 0
            self.record_test("Workflows", "Get Active Workflows", True)
            
            # Test verification code handling in workflow
            if workflow_result.get('phone_number'):
                workflow_manager.handle_verification_code_in_workflow(
                    workflow_result['phone_number'], "999888"
                )
                self.record_test("Workflows", "Handle Verification", True)
            
            print("✅ Cross-Tool Workflows tests passed\n")
            
        except Exception as e:
            self.record_test("Workflows", "General", False, str(e))
            print(f"❌ Cross-Tool Workflows test failed: {e}\n")
    
    def test_data_synchronization(self):
        """Test data synchronization between tools"""
        print("🔄 Testing Data Synchronization...")
        
        try:
            # Test data export
            export_data = integration_manager.export_shared_data()
            assert isinstance(export_data, dict)
            assert 'phone_numbers' in export_data
            self.record_test("Data Sync", "Export Shared Data", True)
            
            # Test adapter synchronization
            test_numbers = [{
                'phone_number': '+1 555 SYNC',
                'country_code': 'US',
                'service': 'Telegram',
                'provider': 'Sync Test',
                'cost': 0.50
            }]
            
            sms_adapter.sync_purchased_numbers_to_integration(test_numbers)
            self.record_test("Data Sync", "SMS Adapter Sync", True)
            
            # Test codes synchronization
            test_codes = [{
                'phone_number': '+1 555 SYNC',
                'code': '555999',
                'service': 'Telegram'
            }]
            
            sms_adapter.sync_received_sms_codes(test_codes)
            self.record_test("Data Sync", "SMS Codes Sync", True)
            
            print("✅ Data Synchronization tests passed\n")
            
        except Exception as e:
            self.record_test("Data Sync", "General", False, str(e))
            print(f"❌ Data Synchronization test failed: {e}\n")
    
    def test_styling_system(self):
        """Test unified styling system"""
        print("🎨 Testing Styling System...")
        
        try:
            # Test theme manager
            assert theme_manager is not None
            themes = theme_manager.get_available_themes()
            assert len(themes) > 0
            self.record_test("Styling", "Theme Manager", True)
            
            # Test theme retrieval
            dark_theme = theme_manager.get_theme("dark_professional")
            assert "colors" in dark_theme
            assert "metrics" in dark_theme
            self.record_test("Styling", "Theme Retrieval", True)
            
            # Test font configuration
            title_font = theme_manager.get_font("title")
            assert isinstance(title_font, tuple)
            assert len(title_font) == 3
            self.record_test("Styling", "Font Configuration", True)
            
            # Test style preferences
            assert style_preferences is not None
            theme_for_telegram = style_preferences.get_theme_for_tool("telegram")
            assert theme_for_telegram is not None
            self.record_test("Styling", "Style Preferences", True)
            
            print("✅ Styling System tests passed\n")
            
        except Exception as e:
            self.record_test("Styling", "General", False, str(e))
            print(f"❌ Styling System test failed: {e}\n")
    
    def test_database_operations(self):
        """Test database operations and integrity"""
        print("🗄️ Testing Database Operations...")
        
        try:
            # Test database connection
            conn = sqlite3.connect(integration_manager.db_path, timeout=30)
            cursor = conn.cursor()
            
            # Test table existence
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            expected_tables = [
                'shared_phone_numbers',
                'verification_codes',
                'unified_sessions',
                'integration_events',
                'shared_proxies'
            ]
            
            for table in expected_tables:
                assert table in table_names
            
            self.record_test("Database", "Table Structure", True)
            
            # Test foreign key constraints
            cursor.execute("PRAGMA foreign_keys")
            fk_enabled = cursor.fetchone()[0]
            assert fk_enabled == 1
            self.record_test("Database", "Foreign Keys", True)
            
            # Test WAL mode
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            assert journal_mode.upper() == 'WAL'
            self.record_test("Database", "WAL Mode", True)
            
            conn.close()
            
            print("✅ Database Operations tests passed\n")
            
        except Exception as e:
            self.record_test("Database", "General", False, str(e))
            print(f"❌ Database Operations test failed: {e}\n")
    
    def record_test(self, category: str, test_name: str, success: bool, error: str = None):
        """Record test result"""
        result = {
            "category": category,
            "test": test_name,
            "success": success,
            "timestamp": datetime.now(),
            "error": error
        }
        
        self.test_results.append(result)
        
        if not success:
            self.failed_tests.append(result)
    
    def print_test_results(self):
        """Print comprehensive test results"""
        print("=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Count results by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0, "failed": 0}
            
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Print category summary
        for category, stats in categories.items():
            status = "✅" if stats["failed"] == 0 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} passed")
        
        # Overall summary
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        
        print(f"\n📊 OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   • {test['category']} - {test['test']}: {test['error']}")
        
        # Export results to file
        self.export_test_results()
        
        # Final status
        if len(self.failed_tests) == 0:
            print("\n🎉 ALL TESTS PASSED! Integration system is ready for use.")
        else:
            print(f"\n⚠️  {len(self.failed_tests)} test(s) failed. Please review before deployment.")
    
    def export_test_results(self):
        """Export test results to JSON file"""
        try:
            results_file = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(self.test_results),
                    "passed_tests": len(self.test_results) - len(self.failed_tests),
                    "failed_tests": len(self.failed_tests)
                },
                "results": [
                    {
                        "category": r["category"],
                        "test": r["test"],
                        "success": r["success"],
                        "timestamp": r["timestamp"].isoformat(),
                        "error": r["error"]
                    }
                    for r in self.test_results
                ]
            }
            
            with open(results_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"\n📁 Test results exported to: {results_file}")
            
        except Exception as e:
            print(f"\n⚠️  Failed to export test results: {e}")

def main():
    """Main test runner"""
    print("🔧 UNIFIED INTEGRATION TEST SUITE")
    print("=" * 60)
    print("Testing seamless integration between Telegram automation")
    print("and SMS marketplace tools with unified workflows.\n")
    
    tester = IntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()