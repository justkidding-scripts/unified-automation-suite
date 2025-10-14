# 🚀 Unified Telegram & SMS Automation Suite

**Professional-grade integrated automation platform for Telegram and SMS operations**

---

## 🌟 Overview

The Unified Automation Suite is a comprehensive, enterprise-ready platform that seamlessly integrates:

- **Advanced Telegram Automation** - Multi-account management, scraping, messaging, inviting
- **SMS Marketplace Integration** - Phone number purchasing, verification code management
- **Invisible Member Detection** - Premium stealth scraping capabilities
- **Unified Workflows** - Automated phone-to-account creation pipelines
- **Cross-Tool Communication** - Real-time event sharing and data synchronization

## 🎯 Key Features

### 🔥 Premium Capabilities
- **Invisible Member Detection** - Advanced algorithms to detect hidden/stealth users
- **Automated Account Creation** - Seamless phone number to Telegram account workflows
- **Cross-Tool Data Sharing** - Phone numbers, proxies, and sessions shared between tools
- **Real-Time Event System** - Live communication between all components
- **Professional UI Themes** - Dark, light, and terminal themes with unified styling

### 📱 Telegram Automation
- Multi-account management with session rotation
- Advanced anti-detection scraping algorithms
- Bulk member inviting with smart delays
- Mass messaging with personalization
- Proxy rotation and health monitoring
- Export capabilities with full user data

### 💬 SMS Marketplace Integration
- Real-time phone number purchasing
- Automated verification code monitoring
- Database logging of all SMS activities
- Bulk operations support
- Multiple provider integration
- Cost tracking and wallet management

### 🔧 Technical Excellence
- SQLite database with WAL mode for performance
- Asyncio-based concurrent operations
- Event-driven architecture
- Plugin-ready modular design
- Comprehensive error handling and logging
- Professional code organization

---

## 📂 File Structure

```
unified_automation_suite/
├── README.md                          # This documentation
├── requirements.txt                   # Python dependencies
├── main.py                           # Main entry point
├── config.ini                        # Configuration template
│
├── Core Integration Files:
├── unified_integration_manager.py     # Central data sharing manager
├── integration_adapters.py           # Tool connection adapters
├── unified_launcher.py               # Professional launcher GUI
├── unified_styling.py                # Theme and styling system
│
├── Telegram Automation:
├── enhanced_telegram_gui.py          # Advanced Telegram GUI
├── enhanced_telegram_automation.py   # Core automation engine
├── Invisible_scraper.py              # Premium stealth scraping
├── selenium_scraper.py               # Web-based scraping fallback
│
└── Testing & Utilities:
    ├── test_integration.py           # Comprehensive test suite
    └── setup_environment.py          # Environment setup script
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or extract to your desired location
cd unified_automation_suite

# Install Python dependencies
pip install -r requirements.txt

# Run environment setup
python setup_environment.py

# Run integration tests (optional)
python test_integration.py
```

### 2. Configuration

Create your `config.ini` based on the template:

```ini
[telegram_accounts]
account_1_api_id = YOUR_API_ID
account_1_api_hash = YOUR_API_HASH
account_1_phone = +1234567890
account_1_session_name = session1

[sms_providers]
provider_1_name = SMS-Activate
provider_1_api_key = YOUR_API_KEY

[integration]
auto_workflows = true
cross_tool_sharing = true
theme = dark_professional
```

### 3. Launch Options

**Option A: Unified Launcher (Recommended)**
```bash
python unified_launcher.py
```

**Option B: Individual Tools**
```bash
# Telegram automation only
python enhanced_telegram_gui.py

# Integration test suite
python test_integration.py
```

**Option C: Main Entry Point**
```bash
python main.py
```

---

## 🔧 Core Components

### 🎯 Unified Integration Manager
The heart of the system that handles:
- **Data Synchronization** - Phone numbers, verification codes, sessions
- **Event Broadcasting** - Real-time communication between tools
- **Database Management** - SQLite with WAL mode for performance
- **Workflow Automation** - Cross-tool automated processes

### 🚀 Professional Launcher
Enterprise-grade launcher providing:
- **Tool Management** - Start/stop individual components
- **Real-Time Monitoring** - Live status and statistics
- **Integration Dashboard** - Cross-tool data visualization  
- **Workflow Templates** - Pre-built automation sequences

### 🎨 Unified Styling System
Professional theming with:
- **Multiple Themes** - Dark Professional, Light, Terminal Green
- **Consistent UI** - All tools use the same visual language
- **Customizable** - Per-tool theme preferences
- **Responsive** - Scales across different screen sizes

---

## ⚙️ Advanced Workflows

### 📱 Automated Account Creation
1. **Purchase Phone Number** → SMS Marketplace acquires number
2. **Create Telegram Account** → Uses purchased number automatically
3. **Receive Verification** → SMS codes auto-applied to registration
4. **Account Ready** → New account added to automation pool

### 🔍 Invisible Member Detection
Premium algorithm that detects:
- **Profile Analysis** - Missing photos, minimal names
- **Activity Patterns** - Hidden last-seen, suspicious online behavior  
- **Username Steganography** - Hidden meanings in usernames
- **Connection Analysis** - Contact relationships and mutual connections
- **Behavioral Fingerprinting** - User ID patterns and metadata

### 🔄 Data Synchronization
Real-time sharing of:
- **Phone Numbers** - Available across all tools
- **Verification Codes** - Automatically distributed where needed
- **Proxy Settings** - Shared pool with health monitoring
- **Session Data** - Unified account management

---

## 📊 Performance & Monitoring

### Real-Time Statistics
- **Phone Numbers**: Available, in-use, verified counts
- **Verification Codes**: Received, used, pending
- **Active Sessions**: Created, active, inactive
- **Proxy Pool**: Active, failed, response times

### Event Monitoring
- Live event stream showing cross-tool communication
- Performance metrics and health indicators
- Error tracking and resolution suggestions
- Workflow progress and completion status

### Database Analytics
- SQLite with WAL mode for concurrent access
- Foreign key constraints for data integrity
- Performance optimizations for large datasets
- Automated cleanup and maintenance

---

## 🛡️ Security Features

### Anti-Detection
- **Smart Delays** - Randomized timing patterns
- **Proxy Rotation** - Automatic IP switching
- **Session Management** - Distributed account usage
- **Rate Limiting** - Configurable operation limits
- **Stealth Scraping** - Multiple fallback methods

### Data Protection
- **Local Storage** - All data stays on your machine
- **Encrypted Sessions** - Telegram sessions protected
- **Secure Configuration** - API keys properly handled
- **Database Integrity** - WAL mode with transactions

---

## 🔌 Plugin Architecture

### Extensible Design
The suite is built with modularity in mind:

```python
# Example plugin integration
from unified_integration_manager import integration_manager, EventType

class MyCustomPlugin:
    def __init__(self):
        # Register for events
        integration_manager.register_event_handler(
            EventType.SMS_CODE_RECEIVED, 
            self.handle_sms_code
        )
    
    def handle_sms_code(self, event):
        # Custom SMS code processing
        pass
```

---

## 📈 Commercial Features

### Premium Capabilities
- **Invisible Member Detection** - Advanced stealth user identification
- **Automated Workflows** - Full phone-to-account pipelines  
- **Cross-Tool Integration** - Seamless data sharing
- **Professional UI** - Enterprise-grade interface
- **Performance Optimization** - High-speed concurrent operations

### Enterprise Ready
- **Scalable Architecture** - Handle thousands of accounts
- **Comprehensive Logging** - Full audit trails
- **Error Recovery** - Automatic retry and failover
- **Configuration Management** - Environment-specific settings
- **Professional Support** - Documentation and examples

---

## 🚨 Important Notes

### Legal Compliance
- Use responsibly and in compliance with Telegram's Terms of Service
- Respect rate limits and user privacy
- Obtain proper permissions for scraping activities
- Follow local laws regarding automated communications

### Performance Tips
- Use SSD storage for better database performance  
- Configure adequate proxy rotation
- Monitor memory usage with large datasets
- Regular database maintenance and cleanup

### Troubleshooting
- Check `unified_integration.log` for detailed error information
- Run `test_integration.py` to verify system health
- Use the database unlock feature if SQLite locks occur
- Refer to individual tool documentation for specific issues

---

## 🤝 Support & Development

### Getting Help
1. Check the logs in `unified_integration.log`
2. Run the test suite: `python test_integration.py`
3. Review configuration in `config.ini`
4. Check individual tool README files

### Development
The codebase follows professional standards:
- **Type Hints** - Full type annotations
- **Documentation** - Comprehensive docstrings
- **Error Handling** - Graceful failure recovery
- **Testing** - Automated test suite
- **Logging** - Detailed operation tracking

---

## 📋 Version History

### v3.0.0 - Unified Integration Release
- ✅ Complete integration between Telegram automation and SMS marketplace
- ✅ Real-time event system with cross-tool communication
- ✅ Unified launcher with professional monitoring dashboard
- ✅ Advanced invisible member detection algorithms
- ✅ Automated phone-to-account creation workflows
- ✅ Professional theming system with multiple themes
- ✅ Comprehensive test suite with 30+ test cases
- ✅ SQLite database with WAL mode for performance
- ✅ Plugin architecture for extensibility

### Previous Versions
- v2.0.0 - Enhanced Telegram automation
- v1.0.0 - Basic functionality

---

**🎉 Ready to dominate automation? Launch with `python unified_launcher.py`!**