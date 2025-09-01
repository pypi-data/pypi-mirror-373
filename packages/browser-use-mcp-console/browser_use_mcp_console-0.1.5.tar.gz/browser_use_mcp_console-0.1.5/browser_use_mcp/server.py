"""
MCP Server for browser automation with Console Tool Support.

This server provides browser automation capabilities through MCP protocol.
It supports console viewing capabilities for debugging web applications.
Uses stdio transport for communication with MCP clients.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
import psutil

# --- Set CWD and Path to Package Root ---
# This script now runs as part of an installed package
try:
    # Get the package directory
    package_root = Path(__file__).parent.resolve()
    # For auth_state.json, we'll use the current working directory
    working_dir = Path.cwd()
except Exception as e:
    print(f"Error setting up script environment: {e}", file=sys.stderr)
    sys.exit(1)

# --- Fix Windows encoding and disable telemetry ---
# Note: Don't wrap stdout in MCP server as it interferes with stdio communication
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
os.environ['BROWSER_USE_CLOUD_SYNC'] = 'false'

# --- Auto-detect browser (System Chrome/Edge or Playwright) ---
import platform
system = platform.system()
SYSTEM_BROWSER_PATH = None

if system == "Windows":
    # First, try to find system Chrome or Edge
    possible_browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
    ]

    for browser_path in possible_browsers:
        if os.path.exists(browser_path):
            SYSTEM_BROWSER_PATH = browser_path
            break

    # If no system browser found, try Playwright browsers
    if not SYSTEM_BROWSER_PATH and not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
        home = os.path.expanduser("~")
        ms_playwright_path = os.path.join(home, "AppData", "Local", "ms-playwright")
        if os.path.exists(ms_playwright_path):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = ms_playwright_path

elif system == "Darwin":  # macOS
    # Try system Chrome first
    possible_browsers = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]

    for browser_path in possible_browsers:
        if os.path.exists(browser_path):
            SYSTEM_BROWSER_PATH = browser_path
            break

    # Fallback to Playwright
    if not SYSTEM_BROWSER_PATH and not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
        home = os.path.expanduser("~")
        ms_playwright_path = os.path.join(home, "Library", "Caches", "ms-playwright")
        if os.path.exists(ms_playwright_path):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = ms_playwright_path

else:  # Linux
    # Try system Chrome/Chromium
    possible_browsers = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]

    for browser_path in possible_browsers:
        if os.path.exists(browser_path):
            SYSTEM_BROWSER_PATH = browser_path
            break

    # Fallback to Playwright
    if not SYSTEM_BROWSER_PATH and not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
        home = os.path.expanduser("~")
        ms_playwright_path = os.path.join(home, ".cache", "ms-playwright")
        if os.path.exists(ms_playwright_path):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = ms_playwright_path

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=r'D:\supie\202507\browser_use_mcp\server_log.txt',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Log browser detection
if SYSTEM_BROWSER_PATH:
    logger.info(f"✓ Using system browser: {SYSTEM_BROWSER_PATH}")
elif os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
    logger.info(f"✓ Using Playwright browsers from: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
else:
    logger.warning("⚠️ No browser detected. Playwright will try to download one automatically.")

# --- Main Application Imports ---
try:
    from mcp.server.fastmcp import FastMCP
    from browser_use import Agent, BrowserProfile
    from browser_use.browser.session import BrowserSession
    from browser_use.controller.service import Controller

    # Import console tool registration functions
    from browser_use_mcp.console_tool import register_init_console_capture, register_view_console_logs

    # Import subprocess for Chromium installation
    import subprocess

except ImportError as e:
    import traceback
    logger.error("Caught an ImportError. Full details below:")
    traceback.print_exc() # 打印完整的错误堆栈
    sys.exit(1)



# --- MCP Server Definition ---
mcp = FastMCP(
    name="BrowserUseAgent",
    instructions="Browser automation tool that can detect console logs and JavaScript errors. Use for testing websites, automating web tasks, and debugging frontend issues"
)

@mcp.tool(name="run_browser_tasks", description="Browser automation tool with integrated JavaScript console capture capabilities")
async def run_browser_tasks(
    tasks: list[str],
    model: str | None = None,
    headless: bool = False,
    max_steps: int = 100,
    use_vision=True
) -> str:
    """
    Executes browser automation tasks with automatic console capture.
    Single tasks run in one browser, multiple tasks run in parallel browsers.
    Console logs are automatically captured and can be viewed when needed.

    Args:
        tasks: List of task descriptions (always use list format, even for single task)
        model: LLM model to use
        headless: Whether to run browsers in headless mode
        max_steps: Maximum steps per task
        use_vision: Whether to enable visual page understanding (screenshots analysis)

    Returns:
        Summary of task results
    """

    if not tasks:
        return "No tasks provided"

    # Configure LLM
    # Support multiple LLM providers
    if os.getenv("OPENROUTER_API_KEY"):
        from browser_use.llm.openrouter.chat import ChatOpenRouter
        if model is None:
            model = "google/gemini-2.5-pro"  # OpenRouter default model
        llm = ChatOpenRouter(model=model, api_key=os.getenv("OPENROUTER_API_KEY"))
    elif os.getenv("OPENAI_API_KEY"):
        from browser_use.llm.openai.chat import ChatOpenAI
        if model is None:
            model = "gpt-4o-mini"  # OpenAI default model
        llm = ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY")),
    elif os.getenv("ANTHROPIC_API_KEY"):
        from browser_use.llm.anthropic.chat import ChatAnthropic
        if model is None:
            model = "claude-3-5-sonnet-20241022"  # Anthropic default model
        llm = ChatAnthropic(model=model, api_key=os.getenv("ANTHROPIC_API_KEY")),
    else:
        return "Error: No API key found. Please set one of: OPENROUTER_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY"

    storage_state_path = working_dir / 'auth_state.json'
    storage_state = str(storage_state_path) if storage_state_path.exists() else None

    if storage_state:
        logger.info(f"Using saved authentication state from: {storage_state}")

    # Use system browser if detected
    browser_config = {
        'headless': headless,
        'storage_state': storage_state,  # Use saved login state if exists
        'user_data_dir': None,  # Independent temp directory for each session
        'keep_alive': False,
        'enable_default_extensions': False,
        'browser_kwargs': {'timeout': 60000}
    }

    # If we detected a system browser, use it
    if SYSTEM_BROWSER_PATH:
        browser_config['executable_path'] = SYSTEM_BROWSER_PATH
        logger.info(f"Using system browser executable: {SYSTEM_BROWSER_PATH}")

    profile_template = BrowserProfile(**browser_config)

    agents = []
    for task in tasks:
        browser_session = BrowserSession(browser_profile=profile_template)

        controller = Controller()
        register_init_console_capture(controller)
        register_view_console_logs(controller)

        extend_system_message = """
Console logs are automatically captured in the background for all pages. You have access to:

**Tool Available**: 
- 'view_console_logs': Retrieve captured console outputs (errors, warnings, logs)

**When to Check Console**:
- If the task mentions debugging, testing, or checking for errors
- When encountering unexpected behavior or failed actions
- After form submissions, login attempts, or API calls
- If a page appears broken or unresponsive

**What's Captured**:
- All console.log/error/warn/info/debug outputs
- Unhandled JavaScript errors and Promise rejections
- Network errors and failed resource loads

**URL Navigation Tracking**:
You MUST track and report the complete URL navigation journey:
- Record the starting URL when you first navigate
- Note any redirects, auto-forwards, or URL changes that occur
- Document intermediate URLs during multi-step processes
- Report the final URL when task completes
- Format: "URL Journey: [initial_url] → [redirect_url] → [final_url]"
- Include this URL journey in your final report

**Result Reporting Requirements**:
When you use 'view_console_logs' and find errors/warnings:
- MUST include the specific error messages in your final report
- Format: List each error with its full message and location
- Don't just say "found errors" - provide the actual error text
- Example: "TypeError: Cannot read properties of undefined (reading 'data') at line 45"
- If no errors found after checking, report: "Console check: No errors detected"

Always include URL journey tracking in your final summary, even for simple single-page tasks.

Note: Console capture is automatic - you don't need to initialize it. Just use 'view_console_logs' when needed to check for issues.
"""

        agent = Agent(
            task=task,
            llm=llm,
            browser_session=browser_session,
            controller=controller,
            extend_system_message=extend_system_message,
            use_vision=use_vision
        )

        agents.append(agent)

    # Single task or multi-task execution mode
    execution_mode = "single" if len(agents) == 1 else "parallel"
    logger.info(f"Execution mode: {execution_mode} ({len(agents)} agent(s))")

    try:
        logger.info("Starting browser session(s)...")
        await asyncio.gather(*[agent.browser_session.start() for agent in agents])
        logger.info(f"{len(agents)} browser session(s) started")

        if execution_mode == "single":
            logger.info("Running single task...")
        else:
            logger.info(f"Running {len(tasks)} tasks in parallel...")

        results = await asyncio.gather(
            *[agent.run(max_steps=max_steps) for agent in agents],
            return_exceptions=True  # Continue other tasks even if one fails
        )
        logger.info("Task execution completed")

        task_results = []
        for i, (task, result) in enumerate(zip(tasks, results)):
            if isinstance(result, Exception):
                task_results.append(f"Task {i+1} '{task[:50]}...': Failed - {str(result)}")
            else:
                success = result.is_successful() if hasattr(result, 'is_successful') else False
                final = result.final_result() if hasattr(result, 'final_result') else "No result"
                task_results.append(f"Task {i+1} '{task[:50]}...': {'Success' if success else 'Completed'} - {final}")

        if len(tasks) == 1:
            return task_results[0] if task_results else "No result"
        else:
            return "\n".join([
                f"Executed {len(tasks)} tasks in parallel:",
                "=" * 50,
                *task_results
            ])

    except Exception as e:
        logger.error(f"Parallel execution failed: {e}", exc_info=True)
        return f"Parallel execution error: {e}"

    finally:
        logger.info("Task function finished. Starting immediate browser cleanup...")
        cleanup_count = 0
        for agent in agents:
            try:
                if hasattr(agent, 'browser_session') and agent.browser_session:
                    logger.info(f"Cleaning up browser session for agent: {agent}")

                    if hasattr(agent.browser_session, 'browser') and agent.browser_session.browser:
                        try:
                            agent.browser_session.browser.close()
                            cleanup_count += 1
                            logger.info("Browser closed via browser.close()")
                        except:
                            pass
            except Exception as e:
                logger.warning(f"Error cleaning up browser session: {e}")
        

        try:
            logger.info("Performing additional process-level cleanup...")
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 'msedge' in proc.info['name'].lower()):
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('--remote-debugging-port' in str(arg) for arg in cmdline):
                            logger.info(f"Found orphaned browser process PID: {proc.info['pid']}, terminating...")
                            proc.terminate()
                            cleanup_count += 1
                            try:
                                proc.wait(timeout=2)
                            except psutil.TimeoutExpired:
                                proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.warning(f"Error in process-level cleanup: {e}")
        
        logger.info(f"Immediate cleanup completed - {cleanup_count} browser sessions/processes handled.")


def main():
    """Runs the server using stdio transport for MCP clients."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


    logger.info("Starting Browser-Use MCP Server with Console Support...")
    logger.info("Browser cleanup handled by finally block in run_browser_tasks()")

    # Run server (stdio mode for uvx/Claude)
    mcp.run()

if __name__ == "__main__":
    main()

