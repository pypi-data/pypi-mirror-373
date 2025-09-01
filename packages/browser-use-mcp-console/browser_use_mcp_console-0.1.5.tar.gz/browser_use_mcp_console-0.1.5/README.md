# Browser-Use MCP Console

🤖 **智能浏览器自动化 + 控制台调试工具**

A powerful MCP server that enables AI assistants to control browsers and debug web applications by capturing console outputs in real-time.

## ✨ Key Features

- **🌐 Browser Automation** - AI-powered web automation using LLMs
- **🐛 Console Monitoring** - Automatic capture of JavaScript errors, warnings, and logs
- **⚡ Parallel Execution** - Run multiple browser tasks simultaneously
- **📝 Error Reporting** - Detailed console error messages in task results
- **🔧 Debug Support** - Perfect for testing and debugging web applications

## 🚀 Quick Start

### 1. Install the Package

```bash
pip install browser-use-mcp-console
```

Or use with Chinese mirror:
```bash
pip install browser-use-mcp-console -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. Get Your API Key

Choose one provider:
- **[OpenRouter](https://openrouter.ai)** - Recommended, supports multiple models
- **[OpenAI](https://platform.openai.com/api-keys)** - GPT models
- **[Anthropic](https://console.anthropic.com/account/keys)** - Claude models

### 3. Configure with Claude Desktop

```bash
# Using OpenRouter (Recommended)
claude mcp add browser-use \
  --scope user \
  --command "uvx" \
  --args "browser-use-mcp-console" \
  --env OPENROUTER_API_KEY=your-api-key-here

# Or using OpenAI
claude mcp add browser-use \
  --scope user \
  --command "uvx" \
  --args "browser-use-mcp-console" \
  --env OPENAI_API_KEY=your-api-key-here
```

### 4. Configure with Cursor (Optional)

Add to Cursor's MCP settings:
```json
{
  "mcpServers": {
    "browser-use": {
      "command": "uvx",
      "args": ["browser-use-mcp-console"],
      "env": {
        "OPENROUTER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## 📖 Usage Examples

After configuration, you can use natural language commands in Claude:

### Basic Web Automation
```
"Open Baidu Translate and translate 'Hello' to Chinese"
"Login to website with username admin and password 123456"
"Fill out the contact form on example.com"
```

### Debug & Testing
```
"Visit localhost:3000 and check for console errors"
"Test the login functionality and report any JavaScript errors"
"Click the submit button and monitor console output"
```

### Parallel Tasks
```
"Open three websites simultaneously: google.com, baidu.com, bing.com"
"Run multiple tests: login test, form validation test, API test"
```

## ⚙️ Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tasks` | list[str] | Required | Task descriptions (single or multiple) |
| `model` | str | Varies* | LLM model to use |
| `headless` | bool | False | Run browser in background |
| `max_steps` | int | 100 | Maximum actions per task |
| `use_vision` | bool | True | Enable visual page understanding |

*Default models:
- OpenRouter: `google/gemini-2.5-pro`
- OpenAI: `gpt-4o-mini`
- Anthropic: `claude-3-5-sonnet-20241022`

## 🔍 Console Monitoring Features

The key advantage of this MCP server is **automatic console capture**:

- **Automatic Error Detection** - Captures all JavaScript errors and unhandled Promise rejections
- **Detailed Error Reports** - Returns specific error messages with stack traces
- **Real-time Monitoring** - Console logs are captured as pages execute
- **Comprehensive Coverage** - Monitors console.log, console.error, console.warn, console.info

Example error report:
```
Task completed. Found console errors:
- TypeError: Cannot read properties of undefined (reading 'data') at app.js:45
- Unhandled Promise rejection: API timeout at fetch.js:89
```

## 🛠️ Troubleshooting

### Browser not opening?
- The server auto-detects Playwright browsers
- First run may download Chromium automatically
- Check `PLAYWRIGHT_BROWSERS_PATH` environment variable

### API key issues?
- Ensure your API key is valid and has credits
- OpenRouter users: Check your balance at openrouter.ai
- Try testing with a simple task first

### Console logs not showing?
- Console capture is automatic but viewing requires explicit checking
- The agent will check console when task mentions "debug", "test", or "errors"

## 📚 Development

```bash
# Clone repository
git clone https://github.com/yourusername/browser-use-mcp-console
cd browser-use-mcp-console

# Install in development mode
pip install -e .

# Run tests
python test_mcp_client.py
```

## 📄 License

MIT License

