"""
rbpop窗口管理器模块

提供弹窗窗口的统一管理，包括窗口生命周期、位置计算、队列处理等功能。
"""

from __future__ import annotations
import warnings
from typing import List, Optional

from PyQt6.QtCore import QTimer

from win.popped import PopWin


class WinManager:
    """
    弹窗窗口管理器
    
    负责管理多个弹窗窗口的生命周期，包括：
    - 窗口的添加、移除和排序
    - 窗口位置的自动计算（垂直堆叠）
    - 批量窗口的显示/隐藏控制
    - 窗口队列的延迟处理机制
    
    采用单例模式设计，全局只有一个实例管理所有弹窗。
    """
    
    _instance: Optional['WinManager'] = None
    
    def __init__(self):
        """初始化窗口管理器实例"""
        self._win_list: List[PopWin] = []  # 当前活跃的窗口列表
        self._pending_queue: List[PopWin] = []  # 待处理的窗口队列
        self._max_delay: int = 100  # 最大延迟时间(ms)
    
    @classmethod
    def get_instance(cls) -> 'WinManager':
        """
        获取全局窗口管理器实例（单例模式）
        
        Returns:
            WinManager: 全局唯一的窗口管理器实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ====================
    # 内部属性与工具方法
    # ====================
    
    @property
    def _offset(self) -> int:
        """
        计算当前所有窗口的总高度偏移量
        
        用于确定新窗口的垂直起始位置，实现窗口的垂直堆叠效果。
        返回值是所有已显示窗口高度的累加和。
        """
        total_height = 0
        for win in self._win_list:
            total_height += win.geometry().height()
        return total_height

    def _calculate_delay(self) -> int:
        """
        计算队列处理的延迟时间
        
        算法：延迟时间 = 最大延迟 / (队列长度 + 1)
        队列越长，延迟越短，趋近于0，避免同时显示过多窗口造成视觉混乱。
        
        Returns:
            int: 计算得到的延迟时间（毫秒）
        """
        queue_length = len(self._pending_queue)
        return int(self._max_delay / (queue_length + 1))

    def _start_windows(self) -> None:
        """启动所有已注册的窗口"""
        for win in self._win_list:
            win.Start()
            win.show()

    def _update_offsets_after_removal(self, removed_index: int, removed_height: int) -> None:
        """
        窗口移除后更新右侧窗口的偏移量
        
        当某个窗口被移除时，其右侧的所有窗口需要向上移动相应的高度，
        以保持窗口堆叠的连续性。
        
        Args:
            removed_index: 被移除窗口的索引位置
            removed_height: 被移除窗口的高度
        """
        # 获取被移除窗口右侧的所有窗口
        affected_windows = self._win_list[removed_index:]
        
        # 更新这些窗口的偏移量（向上移动）
        for win in affected_windows:
            win.offset -= removed_height

    def _process_next_pending(self) -> None:
        """
        处理待弹窗队列中的下一个窗口
        
        使用延迟机制避免窗口同时弹出，提升用户体验。
        延迟时间根据队列长度动态计算。
        """
        if not self._pending_queue:
            return

        delay = self._calculate_delay()
        QTimer.singleShot(delay, self._start_next_pending)

    def _start_next_pending(self) -> None:
        """
        启动队列中的下一个待处理窗口
        
        将窗口从待处理队列移动到活跃窗口列表，
        并触发显示流程。处理完成后继续处理队列中的下一个窗口。
        """
        if not self._pending_queue:
            return

        # 从队列头部取出窗口
        win = self._pending_queue.pop(0)
        
        # 计算当前偏移量（不包括新窗口）
        current_offset = self._offset
        
        # 添加到活跃窗口列表
        self._win_list.append(win)
        
        # 更新窗口偏移量并启动显示
        win.offset = current_offset
        win.Start()
        win.show()

        # 递归处理队列中的下一个窗口
        if self._pending_queue:
            self._process_next_pending()

    # ====================
    # 公开API方法
    # ====================
    
    def add_window(self, win: PopWin) -> None:
        """
        添加新窗口到管理器
        
        窗口不会立即显示，而是进入待处理队列，
        按照延迟机制逐步显示，避免视觉混乱。
        
        Args:
            win: 要添加的PopWin窗口实例
        """
        # 设置窗口的初始偏移量
        win.offset = self._offset
        
        # 添加到待处理队列
        self._pending_queue.append(win)
        
        # 配置窗口属性
        win._all = self._win_list
        win._on_death = lambda: self.remove_window(win)
        
        # 触发队列处理
        self._process_next_pending()

    def remove_window(self, win: PopWin) -> bool:
        """
        从管理器中移除指定窗口
        
        移除窗口后，会自动调整右侧窗口的位置，
        保持窗口堆叠的连续性。
        
        Args:
            win: 要移除的PopWin窗口实例
            
        Returns:
            bool: 移除成功返回True，未找到窗口返回False
        """
        # 查找窗口在列表中的索引
        try:
            index = self._win_list.index(win)
        except ValueError:
            return False

        # 获取被移除窗口的高度
        removed_height = win.geometry().height()
        
        # 从活跃窗口列表中移除
        self._win_list.pop(index)
        
        # 更新右侧窗口的偏移量
        self._update_offsets_after_removal(index, removed_height)
        
        return True

    def hide_all_windows(self) -> None:
        """隐藏所有已显示的窗口（窗口仍在内存中）"""
        for win in self._win_list:
            win.hide()

    def show_all_windows(self) -> None:
        """显示所有已隐藏的窗口"""
        for win in self._win_list:
            win.show()

    def get_window_count(self) -> int:
        """
        获取当前活跃的窗口数量
        
        Returns:
            int: 当前显示的窗口总数
        """
        return len(self._win_list)

    def is_empty(self) -> bool:
        """
        检查管理器是否为空（无活跃窗口）
        
        Returns:
            bool: 无窗口返回True，否则返回False
        """
        return len(self._win_list) == 0

    # ====================
    # 向后兼容的方法别名
    # ====================
    
    def add(self, win: PopWin) -> None:
        """
        已废弃：请使用add_window()方法
        
        将在未来版本中移除，建议使用新的API名称。
        """
        warnings.warn(
            "WinManager.add() 已废弃，请使用 WinManager.add_window()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.add_window(win)
    
    def remove(self, win: PopWin) -> bool:
        """
        已废弃：请使用remove_window()方法
        
        将在未来版本中移除，建议使用新的API名称。
        """
        warnings.warn(
            "WinManager.remove() 已废弃，请使用 WinManager.remove_window()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.remove_window(win)
    
    def hide_all(self) -> None:
        """
        已废弃：请使用hide_all_windows()方法
        
        将在未来版本中移除，建议使用新的API名称。
        """
        warnings.warn(
            "WinManager.hide_all() 已废弃，请使用 WinManager.hide_all_windows()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.hide_all_windows()
    
    def show_all(self) -> None:
        """
        已废弃：请使用show_all_windows()方法
        
        将在未来版本中移除，建议使用新的API名称。
        """
        warnings.warn(
            "WinManager.show_all() 已废弃，请使用 WinManager.show_all_windows()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.show_all_windows()
