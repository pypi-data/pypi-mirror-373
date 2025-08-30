import warnings
import sys
warnings.filterwarnings("ignore", category=DeprecationWarning)

# QApplication警告相关工具
_QAPP_WARNING_ENABLED = True

# 导出变量供外部使用
__all__ = [
    'QApplicationWarning',
    'disable_qapp_warning', 
    'enable_qapp_warning',
    '_filter_qapp_warning',
    '_QAPP_WARNING_ENABLED'
]

class QApplicationWarning(Warning):
    """QApplication自动创建警告类"""
    pass

def _filter_qapp_warning(message, category, filename, lineno, file=None, line=None):
    """警告过滤器，允许用户关闭QApplication警告"""
    if category is QApplicationWarning and not _QAPP_WARNING_ENABLED:
        return False
    return True

# 注册警告过滤器
warnings.showwarning = _filter_qapp_warning

def disable_qapp_warning():
    """禁用QApplication自动创建警告"""
    global _QAPP_WARNING_ENABLED
    _QAPP_WARNING_ENABLED = False

def enable_qapp_warning():
    """启用QApplication自动创建警告"""
    global _QAPP_WARNING_ENABLED
    _QAPP_WARNING_ENABLED = True


