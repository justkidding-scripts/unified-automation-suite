#!/usr/bin/env python3
"""
Integration Adapters
====================
Adapters to connect existing Telegram automation and SMS marketplace tools
to the unified integration system for seamless data sharing and workflows.

Author: Enhanced by AI Assistant
Version: 3.0.0
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from unified_integration_manager import (
    integration_manager, ToolType, EventType, IntegrationEvent,
    SharedPhoneNumber, UnifiedSession
)

class TelegramIntegrationAdapter:
    """Adapter to integrate existing Telegram automation with unified system"""
    
    def __init__(self, telegram_automation_instance=None):
        self.automation = telegram_automation_instance
        self.logger = logging.getLogger(__name__)
        
        # Register this tool with integration manager
        integration_manager.register_tool(ToolType.TELEGRAM, self)
        
        # Register event handlers
        self.setup_event_handlers()
        
        self.logger.info("Telegram Integration Adapter initialized")
    
    def setup_event_handlers(self):
        """Setup event handlers for integration"""
        integration_manager.register_event_handler(
            EventType.SMS_CODE_RECEIVED, self.on_sms_code_received
        )
        integration_manager.register_event_handler(
            EventType.NUMBER_PURCHASED, self.on_number_purchased
        )
    
    def on_sms_code_received(self, event: IntegrationEvent):
        """Handle SMS code received event"""
        try:
            phone_number = event.data.get('phone_number')
            code = event.data.get('code')
            service = event.data.get('service')
            
            if service == 'Telegram' and phone_number:
                self.logger.info(f"SMS code received for Telegram: {phone_number} -> {code}")
                
                # If there's an active Telegram account creation for this number,
                # automatically use this code
                self.auto_apply_verification_code(phone_number, code)
                
        except Exception as e:
            self.logger.error(f"Error handling SMS code event: {e}")
    
    def on_number_purchased(self, event: IntegrationEvent):
        """Handle number purchased event"""
        try:
            phone_data = event.data
            if phone_data.get('service') == 'Telegram':
                self.logger.info(f"New Telegram number available: {phone_data.get('phone_number')}")
                
                # Optionally auto-create account if auto-workflow is enabled
                # self.auto_create_account_if_enabled(phone_data)
                
        except Exception as e:
            self.logger.error(f"Error handling number purchased event: {e}")
    
    def auto_apply_verification_code(self, phone_number: str, code: str):
        """Auto-apply verification code to pending Telegram registration"""
        try:
            # This would integrate with the actual Telegram automation
            # to automatically apply the code during account creation
            self.logger.info(f"Auto-applying code {code} for {phone_number}")
            
            # Mark code as used in integration manager
            codes = integration_manager.get_verification_codes(phone_number, unused_only=True)
            for code_record in codes:
                if code_record['code'] == code:
                    integration_manager.mark_code_used(code_record['id'])
                    break
            
            # Emit account creation event if successful
            integration_manager.emit_event(IntegrationEvent(
                event_type=EventType.ACCOUNT_CREATED,
                source_tool=ToolType.TELEGRAM,
                data={
                    'phone_number': phone_number,
                    'verification_code': code,
                    'created_at': datetime.now().isoformat()
                },
                timestamp=datetime.now()
            ))
            
        except Exception as e:
            self.logger.error(f"Error auto-applying verification code: {e}")
    
    def sync_accounts_to_integration(self):
        """Sync Telegram accounts to integration manager"""
        try:
            if not self.automation:
                return
            
            # Sync existing accounts to unified system
            for account in self.automation.accounts:
                # Create unified session for each account
                session = UnifiedSession(
                    session_id=f"tg_{account.session_name}",
                    phone_number=account.phone_number,
                    telegram_session_name=account.session_name,
                    proxy_settings={
                        'host': account.proxy_host,
                        'port': account.proxy_port,
                        'username': account.proxy_username,
                        'password': account.proxy_password,
                        'type': account.proxy_type
                    } if account.proxy_host else None,
                    created_at=datetime.now(),
                    status='active' if account.is_active else 'inactive'
                )
                
                integration_manager.create_unified_session(session)
                
        except Exception as e:
            self.logger.error(f"Error syncing accounts to integration: {e}")
    
    def sync_proxies_to_integration(self):
        """Sync proxy settings to shared pool"""
        try:
            if not self.automation:
                return
            
            for account in self.automation.accounts:
                if account.proxy_host and account.proxy_port:
                    integration_manager.add_shared_proxy(
                        host=account.proxy_host,
                        port=account.proxy_port,
                        username=account.proxy_username,
                        password=account.proxy_password,
                        proxy_type=account.proxy_type
                    )
            
        except Exception as e:
            self.logger.error(f"Error syncing proxies to integration: {e}")
    
    def get_available_numbers_for_accounts(self, service: str = 'Telegram') -> List[SharedPhoneNumber]:
        """Get available phone numbers for Telegram account creation"""
        return integration_manager.get_available_numbers(service)
    
    def reserve_number_for_account(self, phone_number: str, account_id: str) -> bool:
        """Reserve a phone number for Telegram account creation"""
        return integration_manager.reserve_number(phone_number, account_id)
    
    def get_verification_codes_for_number(self, phone_number: str) -> List[Dict]:
        """Get verification codes for a phone number"""
        return integration_manager.get_verification_codes(phone_number, unused_only=True)

class SMSMarketplaceIntegrationAdapter:
    """Adapter to integrate SMS marketplace with unified system"""
    
    def __init__(self, marketplace_instance=None):
        self.marketplace = marketplace_instance
        self.logger = logging.getLogger(__name__)
        
        # Register this tool with integration manager
        integration_manager.register_tool(ToolType.SMS_MARKETPLACE, self)
        
        # Register event handlers
        self.setup_event_handlers()
        
        self.logger.info("SMS Marketplace Integration Adapter initialized")
    
    def setup_event_handlers(self):
        """Setup event handlers for integration"""
        integration_manager.register_event_handler(
            EventType.ACCOUNT_CREATED, self.on_account_created
        )
    
    def on_account_created(self, event: IntegrationEvent):
        """Handle Telegram account created event"""
        try:
            phone_number = event.data.get('phone_number')
            if phone_number:
                # Mark the phone number as verified/used
                self.mark_number_as_verified(phone_number)
                
        except Exception as e:
            self.logger.error(f"Error handling account created event: {e}")
    
    def mark_number_as_verified(self, phone_number: str):
        """Mark a phone number as verified in the system"""
        try:
            # Update phone number status in integration manager
            conn = sqlite3.connect(integration_manager.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE shared_phone_numbers 
                SET status = 'verified', updated_at = CURRENT_TIMESTAMP
                WHERE phone_number = ?
            """, (phone_number,))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Marked phone number {phone_number} as verified")
            
        except Exception as e:
            self.logger.error(f"Error marking number as verified: {e}")
    
    def sync_purchased_numbers_to_integration(self, numbers_data: List[Dict]):
        """Sync purchased numbers to integration manager"""
        try:
            for number_data in numbers_data:
                phone_number_obj = SharedPhoneNumber(
                    phone_number=number_data.get('phone_number', ''),
                    country_code=number_data.get('country_code', ''),
                    service=number_data.get('service', ''),
                    provider=number_data.get('provider', ''),
                    purchase_date=datetime.now(),
                    status='available',
                    cost=number_data.get('cost', 0.0)
                )
                
                integration_manager.add_phone_number(phone_number_obj)
                
        except Exception as e:
            self.logger.error(f"Error syncing purchased numbers: {e}")
    
    def sync_received_sms_codes(self, codes_data: List[Dict]):
        """Sync received SMS codes to integration manager"""
        try:
            for code_data in codes_data:
                integration_manager.add_verification_code(
                    phone_number=code_data.get('phone_number', ''),
                    code=code_data.get('code', ''),
                    service=code_data.get('service', '')
                )
                
        except Exception as e:
            self.logger.error(f"Error syncing SMS codes: {e}")
    
    def auto_purchase_number_for_telegram(self, service: str = 'Telegram', country: str = 'US') -> Dict:
        """Auto-purchase a number for Telegram use"""
        try:
            # This would integrate with the actual marketplace to purchase a number
            # For now, simulate the purchase
            
            phone_number = f"+1 555 {datetime.now().microsecond:04d}"
            
            # Create phone number object
            phone_number_obj = SharedPhoneNumber(
                phone_number=phone_number,
                country_code=country,
                service=service,
                provider='Auto-Purchase',
                purchase_date=datetime.now(),
                status='available',
                cost=0.25
            )
            
            # Add to integration manager
            success = integration_manager.add_phone_number(phone_number_obj)
            
            if success:
                return {
                    'status': 'success',
                    'phone_number': phone_number,
                    'cost': 0.25
                }
            else:
                return {'status': 'error', 'message': 'Failed to add number to system'}
                
        except Exception as e:
            self.logger.error(f"Error auto-purchasing number: {e}")
            return {'status': 'error', 'message': str(e)}

class CrossToolWorkflowManager:
    """Manager for cross-tool automated workflows"""
    
    def __init__(self):
        self.telegram_adapter = None
        self.sms_adapter = None
        self.logger = logging.getLogger(__name__)
        
        # Active workflows
        self.active_workflows: Dict[str, Dict] = {}
        
        self.logger.info("Cross-Tool Workflow Manager initialized")
    
    def set_adapters(self, telegram_adapter: TelegramIntegrationAdapter, 
                    sms_adapter: SMSMarketplaceIntegrationAdapter):
        """Set the tool adapters"""
        self.telegram_adapter = telegram_adapter
        self.sms_adapter = sms_adapter
    
    def create_telegram_account_full_workflow(self, auto_purchase: bool = True, 
                                           country: str = 'US') -> Dict:
        """Complete workflow: Purchase number -> Create TG account -> Handle verification"""
        workflow_id = f"full_tg_workflow_{int(datetime.now().timestamp())}"
        
        try:
            workflow_data = {
                'id': workflow_id,
                'type': 'telegram_account_creation',
                'status': 'starting',
                'steps': [],
                'started_at': datetime.now(),
                'phone_number': None,
                'account_id': None
            }
            
            self.active_workflows[workflow_id] = workflow_data
            
            # Step 1: Purchase/get available number
            if auto_purchase:
                result = self.sms_adapter.auto_purchase_number_for_telegram('Telegram', country)
                if result['status'] != 'success':
                    workflow_data['status'] = 'failed'
                    workflow_data['error'] = result.get('message', 'Failed to purchase number')
                    return workflow_data
                
                phone_number = result['phone_number']
                workflow_data['steps'].append(f"Purchased number: {phone_number}")
            else:
                # Use existing available number
                available_numbers = integration_manager.get_available_numbers('Telegram')
                if not available_numbers:
                    workflow_data['status'] = 'failed'
                    workflow_data['error'] = 'No available Telegram numbers'
                    return workflow_data
                
                phone_number = available_numbers[0].phone_number
                workflow_data['steps'].append(f"Using available number: {phone_number}")
            
            workflow_data['phone_number'] = phone_number
            
            # Step 2: Reserve number for account creation
            if not integration_manager.reserve_number(phone_number, workflow_id):
                workflow_data['status'] = 'failed'
                workflow_data['error'] = 'Failed to reserve phone number'
                return workflow_data
            
            workflow_data['steps'].append(f"Reserved number for workflow")
            
            # Step 3: Create unified session
            session = UnifiedSession(
                session_id=workflow_id,
                phone_number=phone_number,
                telegram_session_name=f"auto_session_{workflow_id}",
                created_at=datetime.now(),
                status='creating'
            )
            
            if not integration_manager.create_unified_session(session):
                workflow_data['status'] = 'failed'
                workflow_data['error'] = 'Failed to create unified session'
                return workflow_data
            
            workflow_data['steps'].append("Created unified session")
            workflow_data['status'] = 'waiting_for_verification'
            
            # Emit workflow started event
            integration_manager.emit_event(IntegrationEvent(
                event_type=EventType.ACCOUNT_CREATED,
                source_tool=ToolType.TELEGRAM,
                data={
                    'workflow_id': workflow_id,
                    'phone_number': phone_number,
                    'status': 'workflow_started'
                },
                timestamp=datetime.now()
            ))
            
            return workflow_data
            
        except Exception as e:
            self.logger.error(f"Error in full TG account workflow: {e}")
            workflow_data['status'] = 'failed'
            workflow_data['error'] = str(e)
            return workflow_data
    
    def handle_verification_code_in_workflow(self, phone_number: str, code: str):
        """Handle verification code received for active workflow"""
        try:
            # Find active workflow for this phone number
            active_workflow = None
            for workflow_id, workflow_data in self.active_workflows.items():
                if (workflow_data.get('phone_number') == phone_number and 
                    workflow_data.get('status') == 'waiting_for_verification'):
                    active_workflow = workflow_data
                    break
            
            if not active_workflow:
                self.logger.info(f"No active workflow found for {phone_number}")
                return
            
            # Apply verification code
            active_workflow['steps'].append(f"Received verification code: {code}")
            active_workflow['status'] = 'applying_verification'
            
            # This would integrate with actual Telegram client to apply the code
            # For now, simulate successful verification
            active_workflow['steps'].append("Successfully applied verification code")
            active_workflow['status'] = 'completed'
            active_workflow['completed_at'] = datetime.now()
            
            # Mark number as verified
            if self.sms_adapter:
                self.sms_adapter.mark_number_as_verified(phone_number)
            
            # Emit completion event
            integration_manager.emit_event(IntegrationEvent(
                event_type=EventType.ACCOUNT_CREATED,
                source_tool=ToolType.TELEGRAM,
                data={
                    'workflow_id': active_workflow['id'],
                    'phone_number': phone_number,
                    'status': 'workflow_completed',
                    'verification_code': code
                },
                timestamp=datetime.now()
            ))
            
            self.logger.info(f"Completed workflow for {phone_number}")
            
        except Exception as e:
            self.logger.error(f"Error handling verification in workflow: {e}")
    
    def get_active_workflows(self) -> Dict[str, Dict]:
        """Get all active workflows"""
        return self.active_workflows.copy()
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Cleanup old completed workflows"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            workflows_to_remove = []
            for workflow_id, workflow_data in self.active_workflows.items():
                if (workflow_data.get('status') in ['completed', 'failed'] and
                    workflow_data.get('completed_at', datetime.now()) < cutoff_time):
                    workflows_to_remove.append(workflow_id)
            
            for workflow_id in workflows_to_remove:
                del self.active_workflows[workflow_id]
                
            if workflows_to_remove:
                self.logger.info(f"Cleaned up {len(workflows_to_remove)} old workflows")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up workflows: {e}")

# Global instances
telegram_adapter = TelegramIntegrationAdapter()
sms_adapter = SMSMarketplaceIntegrationAdapter()
workflow_manager = CrossToolWorkflowManager()

# Set up workflow manager
workflow_manager.set_adapters(telegram_adapter, sms_adapter)

# Register SMS code handler for workflow automation
def on_sms_code_for_workflow(event: IntegrationEvent):
    """Handle SMS codes for active workflows"""
    phone_number = event.data.get('phone_number')
    code = event.data.get('code')
    if phone_number and code:
        workflow_manager.handle_verification_code_in_workflow(phone_number, code)

integration_manager.register_event_handler(EventType.SMS_CODE_RECEIVED, on_sms_code_for_workflow)