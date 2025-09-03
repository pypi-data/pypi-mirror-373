# Whom Integration Library

Versatile Python library for Whom API integration, supporting multiple systems and web automation drivers.

## 🚀 Features

- **🔌 Multiple Drivers**: Support for Selenium and Playwright
- **🎯 Extensible Systems**: Modular architecture for different systems
- **⚡ Easy to Use**: Simple and intuitive API
- **🛡️ Error Handling**: Custom and robust exceptions
- **📚 Well Documented**: Complete examples and documentation

## 📦 Installation

### Basic Installation

```bash
pip install whom-integration
```

### Installation with Specific Drivers

```bash
# Install with all drivers
pip install "whom-integration[all]"
```

### Development Installation

```bash
# Install with development tools
pip install "whom-integration[dev]"

# Manual installation from source
git clone https://github.com/doc9/whom-integration.git
cd whom-integration
pip install -e .
```

### Driver Setup

After installation, you may need to set up the drivers:

```bash
# For Playwright
playwright install chromium

# For Selenium
# ChromeDriver is usually auto-installed via webdriver-manager
```

## 🎯 Quick Start

### Command Line Interface

The library includes a CLI for quick testing:

```bash
# Test ECAC with Playwright
whom-integration --system ecac --driver playwright --token YOUR_TOKEN --extension YOUR_EXTENSION

# Test PJE with Selenium
whom-integration --system pje --driver selenium --token YOUR_TOKEN --extension YOUR_EXTENSION

# Show help
whom-integration --help
```

### Example with Selenium

```python
from whom_integration import WhomClient, ECACSystem, SeleniumDriver

# Configure client
client = WhomClient(token="your_token", extension_id="your_extension_id")

# Create session
with client.create_session(ECACSystem, SeleniumDriver) as session:
    # Authenticate and connect
    session.authenticate_and_connect()
    
    # Execute workflow
    result = session.execute_workflow("default")
    
    print(f"Success: {result['success']}")
```

### Example with Playwright

```python
from whom_integration import WhomClient, ECACSystem, PlaywrightDriver


client = WhomClient(token="your_token", extension_id="your_extension_id")

with client.create_session(ECACSystem, PlaywrightDriver) as session:
    session.authenticate_and_connect()
    result = session.execute_workflow("default")
    print(f"Success: {result['success']}")

```

## 🏗️ Architecture

### Main Components

```
whom_integration/
├── __init__.py          # Main interface
├── core.py              # Client and session
├── drivers/             # Automation drivers
│   ├── base.py         # Abstract base class
│   ├── selenium_driver.py
│   └── playwright_driver.py
├── systems/             # Supported systems
│   ├── base.py         # Abstract base class
│   └── ecac_system.py  # ECAC system
│   └── pje_system.py  # PJE system
└── exceptions.py        # Custom exceptions
```

### Workflow

1. **Whom Client**: Manages API authentication
2. **Driver**: Controls the browser (Selenium/Playwright)
3. **System**: Implements target system specific logic
4. **Session**: Orchestrates the entire process

## 🔧 Configuration

### Basic Configuration

```python
from whom_integration import WhomClient

client = WhomClient(
    token="your_token_here",
    extension_id="your_extension_id_here",
    base_url="https://cloud.doc9.com.br"  # Optional
)
```

### Driver Configuration

```python
# Selenium
session = client.create_session(
    ECACSystem,
    SeleniumDriver,
    headless=False,
    window_size=(1920, 1080)
)

# Playwright
session = client.create_session(
    ECACSystem,
    PlaywrightDriver,
    headless=False,
    viewport={'width': 1920, 'height': 1080}
)
```

## 🎯 **Direct Access to Session Objects**

When you create a session, you have direct access to all available objects and methods:

### 📱 **Driver (Browser)**
```python
# Direct access to configured driver
session.driver.navigate("https://example.com")
session.driver.execute_script("alert('Hello!')")
session.driver.click_element("#button")
session.driver.wait_for_element(".class", timeout=10)
session.driver.get_page_title()
session.driver.get_current_url()

# For Playwright - direct access to page object
if hasattr(session.driver, 'page'):
    session.driver.page.fill("#input", "text")
    session.driver.page.screenshot(path="screenshot.png")
    session.driver.page.pdf(path="page.pdf")

# For Selenium - direct access to driver object
if hasattr(session.driver, 'driver'):
    session.driver.driver.find_element(By.ID, "element")
    session.driver.driver.execute_script("return document.title")
```

### 🖥️ **System Data**
```python
# System specific methods
redirect_url = session.system.get_redirect_url()
target_url = session.system.get_target_url()
js_commands = session.system.get_js_commands()
cookies = session.system.get_cookies()

# Execute custom workflows
result = session.system.execute_workflow("custom_workflow", param1="value")
```

### 📊 **Session Data**
```python
# Direct access to data returned by API
session_data = session.session_data

# Session cookies
cookies = session_data.get('cookies', [])

# Important URLs
entry_point = session_data.get('entry_point')
redirect_url = session_data.get('redirect')
target_url = session_data.get('url')

# JavaScript commands for execution
js_commands = session_data.get('js', [])

# Allowed domains
allowed_domains = session_data.get('domains', [])

# Elements to hide
hidden_elements = session_data.get('elements_to_hidden', {})

# Extra data
extra_data = session_data.get('extra', {})
```

## 🎯 Supported Systems

### 📊 **Driver Compatibility Table**

| System | Selenium | Playwright | Notes |
|---------|----------|------------|-------|
| **ECAC** | ❌ | ✅ | Federal Revenue System - only works with Playwright |
| **PJE** | ✅ | ❌ | Judiciary System - only works with Selenium |

## 🔄 Changelog

### v1.0.0
- ✅ Initial support for ECAC
- ✅ Initial support for PJE
- ✅ Selenium and Playwright drivers
- ✅ Intelligent proxy system
- ✅ Modular and extensible architecture
- ✅ Complete documentation
