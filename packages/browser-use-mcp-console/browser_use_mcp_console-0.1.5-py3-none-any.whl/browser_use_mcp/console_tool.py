
"""
Browser-Use 控制台查看工具
通过注入脚本捕获所有页面的控制台输出
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from browser_use.controller.service import Controller
from browser_use.agent.views import ActionResult
from browser_use.browser.session import BrowserSession

# Controller实例将在异步函数中创建

# 控制台捕获脚本 - 会注入到每个页面
CONSOLE_CAPTURE_SCRIPT = """
(() => {
    // 避免重复初始化
    if (window.__browserUseConsoleCapture) return;
    
    window.__browserUseConsoleCapture = true;
    window.__browserUseConsoleLogs = [];
    
    // 保存原始console方法
    const originalConsole = {
        log: console.log,
        error: console.error,
        warn: console.warn,
        info: console.info,
        debug: console.debug
    };
    
    // 统一的捕获函数
    const captureLog = (type, args) => {
        try {
            // 转换参数为字符串
            const message = args.map(arg => {
                if (arg === undefined) return 'undefined';
                if (arg === null) return 'null';
                if (typeof arg === 'object') {
                    try {
                        return JSON.stringify(arg, null, 2);
                    } catch (e) {
                        return String(arg);
                    }
                }
                return String(arg);
            }).join(' ');
            
            // 存储日志
            window.__browserUseConsoleLogs.push({
                type: type,
                message: message,
                timestamp: new Date().toISOString(),
                url: window.location.href
            });
            
            // 限制存储数量，防止内存泄漏
            if (window.__browserUseConsoleLogs.length > 1000) {
                window.__browserUseConsoleLogs.shift();
            }
        } catch (e) {
            // 静默处理错误，避免影响原始功能
        }
    };
    
    // 重写console方法
    console.log = function(...args) {
        captureLog('log', args);
        originalConsole.log.apply(console, args);
    };
    
    console.error = function(...args) {
        captureLog('error', args);
        originalConsole.error.apply(console, args);
    };
    
    console.warn = function(...args) {
        captureLog('warning', args);
        originalConsole.warn.apply(console, args);
    };
    
    console.info = function(...args) {
        captureLog('info', args);
        originalConsole.info.apply(console, args);
    };
    
    console.debug = function(...args) {
        captureLog('debug', args);
        originalConsole.debug.apply(console, args);
    };
    
    // 捕获未处理的错误
    window.addEventListener('error', (event) => {
        captureLog('error', [`未捕获的错误: ${event.message} at ${event.filename}:${event.lineno}:${event.colno}`]);
    });
    
    // 捕获Promise拒绝
    window.addEventListener('unhandledrejection', (event) => {
        captureLog('error', [`未处理的Promise拒绝: ${event.reason}`]);
    });
    
    // 标记初始化完成
    console.debug('[Console Tool] 控制台捕获已初始化');
})();
"""

# 参数模型
class ViewConsoleParams(BaseModel):
    """查看控制台日志的参数"""
    filter_type: str | None = Field(
        default=None,
        description="过滤日志类型：log, error, warning, info, debug"
    )
    limit: int = Field(
        default=50,
        description="返回的最大日志条数",
        ge=1,
        le=500
    )
    clear_after: bool = Field(
        default=False,
        description="查看后是否清空已捕获的日志"
    )


# Action 1: 初始化控制台捕获
def register_init_console_capture(controller: Controller):
    @controller.registry.action(
        '初始化控制台捕获 - 开始捕获所有页面的console输出（必须先调用）',
        param_model=None
    )
    async def init_console_capture(browser_session: BrowserSession) -> ActionResult:
        """
        初始化控制台捕获功能
        必须在测试开始前调用一次，之后所有页面都会自动捕获日志
        """
        try:
            # 确保browser context已初始化
            if not browser_session.browser_context:
                await browser_session.start()
            
            # 注入init script到browser context
            # 这样所有新创建的页面都会自动执行这个脚本
            await browser_session.browser_context.add_init_script(CONSOLE_CAPTURE_SCRIPT)
            
            # 对当前已存在的页面也注入脚本
            if browser_session.browser_context.pages:
                for page in browser_session.browser_context.pages:
                    try:
                        await page.evaluate(CONSOLE_CAPTURE_SCRIPT)
                    except Exception:
                        # 忽略已关闭的页面
                        pass
            
            return ActionResult(
                extracted_content="✅ 控制台捕获已初始化，所有页面的console输出都会被记录",
                include_in_memory=True
            )
            
        except Exception as e:
            return ActionResult(
                error=f"初始化控制台捕获失败: {str(e)}",
                include_in_memory=True
            )


# Action 2: 查看控制台日志
def register_view_console_logs(controller: Controller):
    @controller.registry.action(
        '查看控制台日志 - 获取当前页面捕获的所有console输出',
        param_model=ViewConsoleParams
    )
    async def view_console_logs(
        params: ViewConsoleParams,
        browser_session: BrowserSession
    ) -> ActionResult:
        """
        查看当前页面的控制台日志
        可以过滤类型、限制数量、清空日志
        """
        try:
            # 获取当前页面
            page = await browser_session.get_current_page()
            if not page:
                return ActionResult(
                    error="没有活动的页面",
                    include_in_memory=True
                )
            
            # 从页面获取捕获的日志
            logs = []
            try:
                logs = await page.evaluate("window.__browserUseConsoleLogs || []")
            except Exception as e:
                # 如果页面还没有注入脚本，返回空
                pass
            
            # 过滤日志类型
            if params.filter_type:
                logs = [log for log in logs if log.get('type') == params.filter_type]
            
            # 限制数量（取最新的）
            if len(logs) > params.limit:
                logs = logs[-params.limit:]
            
            # 格式化输出
            if not logs:
                output = "📋 控制台无输出"
                if params.filter_type:
                    output += f"（过滤: {params.filter_type}）"
            else:
                output = f"📋 控制台日志（共 {len(logs)} 条）：\n"
                output += "=" * 60 + "\n"
                
                for i, log in enumerate(logs, 1):
                    timestamp = log.get('timestamp', 'unknown')
                    log_type = log.get('type', 'unknown').upper()
                    message = log.get('message', '')
                    url = log.get('url', '')
                    
                    # 简化时间戳显示
                    if 'T' in timestamp:
                        time_part = timestamp.split('T')[1].split('.')[0]
                    else:
                        time_part = timestamp
                    
                    output += f"\n{i}. [{log_type}] {time_part}\n"
                    if url and url != page.url:
                        output += f"   📍 {url}\n"
                    output += f"   {message}\n"
            
            # 清空日志（如果需要）
            if params.clear_after and logs:
                await page.evaluate("window.__browserUseConsoleLogs = []")
                output += "\n\n✅ 日志已清空"
            
            return ActionResult(
                extracted_content=output,
                console_logs=logs,  # 返回原始数据供Agent分析
                include_in_memory=True
            )
            
        except Exception as e:
            return ActionResult(
                error=f"查看控制台日志失败: {str(e)}",
                include_in_memory=True
            )

