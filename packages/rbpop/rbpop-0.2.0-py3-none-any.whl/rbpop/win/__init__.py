"""
rbpop窗口管理包

提供弹窗窗口的统一管理和显示功能。
"""

from __future__ import annotations
import warnings
import sys

from PyQt6.QtWidgets import QApplication
from win.popped import PopWin
from win.manager import WinManager

__all__ = ['QPop', 'WinManager']

# ====================
# 包初始化
# ====================

def QPop(pop_win_inst: PopWin) -> None:
    """
    全局函数：添加弹窗到管理器
    
    这是rbpop库的主要对外API，用于将弹窗窗口添加到系统管理器。
    需要调用者自己负责QApplication的创建和管理。
    
    特性：
    - 需要调用者确保QApplication实例已存在
    - 自动初始化全局窗口管理器（单例模式）
    - 使用延迟队列机制，避免窗口同时弹出造成视觉混乱
    
    Args:
        pop_win_inst: 要显示的PopWin窗口实例
        
    示例：
        >>> from PyQt6.QtWidgets import QApplication
        >>> from rbpop.win.popped import PopWin
        >>> app = QApplication([])  # 调用者负责创建QApplication
        >>> win = PopWin("标题", "内容")
        >>> QPop(win)  # 添加到管理器并显示
    """
    # 检查QApplication实例是否存在
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication实例不存在，请先创建QApplication实例")
    
    # 获取全局窗口管理器实例并添加窗口
    manager = WinManager.get_instance()
    manager.add_window(pop_win_inst)
