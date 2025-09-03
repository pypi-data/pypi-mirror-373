from shared.log_util import log_error, log_info
from shared.browser_manager import reset_playwright_cache


def format_exception_message(msg: str, e: Exception) -> str:
    """
    统一处理异常返回信息
    
    Args:
        msg: 异常提示信息
        e: 异常对象
    
    Returns:
        格式化后的异常信息
    """
    error_str = str(e)
    log_error(f"format_exception_message:{msg} exception: {error_str}")
    
    # 浏览器关闭异常
    if "Target page, context or browser has been closed" in error_str:
        log_info("准备清除本地浏览器缓存")
        reset_playwright_cache()
        return f"{msg}: 浏览器已经关闭，需要调用浏览器打开方法重新打开浏览器。"
    
    # 默认返回原始异常信息
    return f"{msg}: {error_str}"