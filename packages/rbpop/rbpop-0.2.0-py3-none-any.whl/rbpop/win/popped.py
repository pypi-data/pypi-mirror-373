from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer

QPOP_DEFAULT_SIZE = (360, 120)

class PopWin(QWidget):
    """
    弹窗基类 - 提供统一的动画显示和行为控制
    
    核心特性：
    - 淡入淡出动画效果
    - 自动定位到屏幕右下角
    - 鼠标悬停暂停动画
    - 支持弹窗组关联控制
    """
    
    # 内部使用常量
    _RESET_PATIENCE = 100  # 重置动画暂停的耐心值
    _MINIUM_DELTA = 1      # 最小移动像素阈值，避免微小抖动

    def __init__(self, ct: int, *, offset=0, all=None, 
                 on_death=None, size=None, slide_in=True, slide_duration=300):
        """
        弹窗基类构造函数
        
        参数说明：
        :param ct: 总显示时间(毫秒)，控制弹窗生命周期
        :param offset: 屏幕底边距偏移量(像素)，调整垂直位置
        :param all: 关联弹窗组，实现组合同步控制
        :param on_death: 关闭回调函数，弹窗销毁时触发
        :param size: 自定义窗口尺寸(width, height)，覆盖默认大小
        :param slide_in: 是否启用从右侧滑入动画，默认为True
        :param slide_duration: 滑入动画持续时间(毫秒)，默认为300ms
        """
        super().__init__(None)
        
        # 设置窗口尺寸
        if size is None:
            self.setFixedSize(*QPOP_DEFAULT_SIZE)
        else:
            self.setFixedSize(*size)
            
        # 初始化UI - 由子类实现
        self.initUI()
        
        # 设置窗口属性：置顶、无边框、SplashScreen
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.SplashScreen)

        # 动画参数计算
        self._pause = 0  # 动画参数
        self._start_opacity = self.windowOpacity()  # 记录初始透明度
        self._down_max = self._down_left = 30  # 下降阶段步数（淡出）
        self._patience = 20  # 耐心值（防止永久暂停）
        self._offset_value = offset   # 内部偏移量存储

        # 滑入动画参数
        self._slide_in = slide_in  # 是否启用滑入动画
        self._slide_duration = slide_duration  # 滑入动画持续时间(毫秒)
        self._slide_timer = None  # 滑入动画定时器
        
        # 创建定时器，用于动画控制
        self._oflag = False  # 启动标志，防止重复启动
        self._opacity_timer = QTimer(self)
        self._opacity_timer.setInterval(50)  # 20fps for fade out
        self._opacity_timer.timeout.connect(self._on_opacity_timeout)

        # 关联弹窗组管理
        self._all = all          # 关联弹窗组引用
        self._on_death = on_death  # 销毁回调
        self._patience = self._RESET_PATIENCE  # 重置耐心值

    @property
    def offset(self):
        """获取垂直偏移量"""
        return self._offset_value
    
    @offset.setter
    def offset(self, value: int) -> None:
        """设置窗口的垂直偏移量（从底部开始计算）"""
        if self._offset_value != value:
            self._offset_value = value
            # 直接移动到新的目标位置
            self._fit_to_right_bottom(1.0)

    # =============================================================================================
    # API 方法 - 子类可重写但应保持基本行为
    # =============================================================================================

    def initUI(self):
        """
        抽象方法 - 子类必须实现UI初始化
        
        实现要求：
        - 在此方法中完成所有控件的创建和布局
        - 设置合适的样式和初始状态
        - 属于关键扩展点，必须实现
        """
        raise NotImplementedError("子类必须实现initUI方法")

    def _start_slide_in_animation(self):
        """启动从右侧滑入的动画，仅处理位置移动"""
        if not self._slide_in:
            return
            
        # 计算滑入参数
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        
        # 目标位置：右下角
        target_y = available_geometry.bottom() - self.height() - self.offset
        self._slide_target_x = available_geometry.right() - self.width()
        
        # 起始位置：屏幕右侧外部
        self._slide_start_x = available_geometry.right() + 50  # 额外增加50像素确保完全在屏幕外
        
        # 设置初始位置
        self.move(self._slide_start_x, target_y)
        
        # 计算动画参数
        self._slide_total_steps = max(1, self._slide_duration // 16)  # 约60fps
        
        # 创建滑入动画定时器
        self._slide_timer = QTimer(self)
        self._slide_timer.setInterval(16)  # 约60fps
        self._slide_step = 0
        
        def slide_step():
            if self._slide_step >= self._slide_total_steps:
                self._slide_timer.stop()
                self._slide_timer.deleteLater()
                return
                
            # 计算当前进度 (0.0 - 1.0)
            progress = self._slide_step / self._slide_total_steps
            
            # 使用缓动函数使动画更自然
            eased_progress = 1 - pow(1 - progress, 3)  # 缓出效果
            
            # 计算当前X坐标
            current_x = int(self._slide_start_x + (self._slide_target_x - self._slide_start_x) * eased_progress)
            
            # 移动窗口（透明度保持不变）
            self.move(current_x, target_y)
            
            self._slide_step += 1
        
        self._slide_timer.timeout.connect(slide_step)
        self._slide_timer.start()
        
    def Start(self):
        """
        启动弹窗显示流程 - 核心API方法
        
        行为描述：
        - 首次调用开始动画序列
        - 支持滑入动画和淡出动画
        - 自动完成定位和定时器启动
        
        调用时机：对象创建后立即调用
        """
        if self._oflag:
            return  # 防止重复启动
            
        self._oflag = True
        
        if self._slide_in:
            # 启动滑入动画，然后启动淡出动画
            self._start_slide_in_animation()
            
            # 延迟启动淡出动画，等滑入完成
            QTimer.singleShot(self._slide_duration, self._start_fade_out)
        else:
            # 直接定位到最终位置并启动淡出
            self._fit_to_right_bottom()  # 初始定位
            self._start_fade_out()  # 直接启动淡出动画
            


    def closeEvent(self, event) -> None:
        """
        窗口关闭事件处理
        
        清理工作：
        - 触发销毁回调（如果存在）
        - 确保资源正确释放
        """
        if self._on_death:
            self._on_death()
        # 让事件正常处理，不立即销毁，让WinManager有时间处理位置更新
        event.accept()

    def enterEvent(self, event):
        """
        鼠标进入事件 - 暂停动画
        
        行为：
        - 增加暂停计数器
        - 同步暂停关联弹窗组
        """
        self._lock_animation()
        if self._all:
            for win in self._all:
                win._lock_animation()

    def leaveEvent(self, event):
        """
        鼠标离开事件 - 恢复动画
        
        行为：
        - 减少暂停计数器
        - 同步恢复关联弹窗组
        """
        self._unlock_animation()
        if self._all:
            for win in self._all:
                win._unlock_animation()

    # =============================================================================================
    # 内部实现 - 私有方法（_前缀）
    # =============================================================================================

    def _fit_to_right_bottom(self, ratio=1.0):
        """
        将窗口定位到屏幕右下角（任务栏上方）
        
        算法说明：
        - 获取屏幕可用区域（排除任务栏）
        - 计算任务栏高度作为偏移参考
        - 使用比例因子实现平滑移动
        - 包含最小移动阈值避免抖动
        
        :param ratio: 移动比例因子（0.0-1.0）
        """
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        screen_geometry = screen.geometry()

        # 计算任务栏高度 = 屏幕总高度 - 可用区域高度
        taskbar_height = screen_geometry.height() - available_geometry.height()

        # 获取当前窗口位置
        self_x, self_y = self.geometry().left(), self.geometry().top()

        # 计算目标位置：右下角，考虑任务栏和自定义偏移
        target_x = available_geometry.right() - self.width()
        target_y = available_geometry.bottom() - self.height() - self.offset

        # 计算移动增量（使用比例因子实现平滑移动）
        delta_x = int(ratio * (target_x - self_x))
        delta_y = int(ratio * (target_y - self_y))

        # X轴位置调整
        if abs(delta_x) > self._MINIUM_DELTA:
            # 正常移动模式
            target_x = self_x + delta_x
        elif abs(target_x - self_x) > self._MINIUM_DELTA:
            # 微小调整模式：使用平均值减少抖动
            target_x = int(0.5 * (self_x + target_x))

        # Y轴位置调整（逻辑同X轴）
        if abs(delta_y) > self._MINIUM_DELTA:
            target_y = self_y + delta_y
        elif abs(target_y - self_y) > self._MINIUM_DELTA:
            target_y = int(0.5 * (self_y + target_y))

        self.move(target_x, target_y)

    def _on_opacity_timeout(self):
        """
        淡出动画定时器回调 - 简化的淡出动画
        
        动画阶段：
        1. 淡出阶段：透明度逐渐减少（淡出）
        2. 结束阶段：关闭窗口
        
        状态管理：
        - 使用计数器管理淡出进度
        - 鼠标悬停时暂停动画
        """
        # 处理暂停状态（鼠标悬停）
        if self._pause > 0:
            # 耐心值递减，避免永久暂停
            if self._patience > 0:
                self._patience -= 1
            else:
                self._pause = 0  # 强制恢复动画
            return

        # 淡出阶段处理
        if self._down_left > 0:
            # 下降阶段：非线性透明度变化，早期更不透明，晚期更快速透明
            self._down_left -= 1
            
            # 计算当前在下降阶段的进度 (0.0 - 1.0)
            down_progress = 1.0 - (self._down_left / self._down_max)
            
            # 使用缓入曲线：早期变化慢，晚期变化快
            # 使用二次函数：progress^2，让透明度在后期加速下降
            eased_progress = down_progress * down_progress
            
            # 计算新的透明度：从初始透明度线性下降到最小透明度
            new_opacity = self._start_opacity - (self._start_opacity - 0.0) * eased_progress
            self.setWindowOpacity(max(0.0, new_opacity))
            
        else:
            # 动画结束：停止定时器并关闭窗口
            self._opacity_timer.stop()
            self.close()

    def _lock_animation(self):
        """锁定动画（暂停）"""
        self._pause += 1

    def _unlock_animation(self):
        """解锁动画（恢复）"""
        self._pause -= 1
        if self._pause < 0:
            self._pause = 0



    def _start_fade_out(self):
        """
        启动淡出动画
        
        在滑入动画完成后调用，开始淡出效果
        """
        self._start_opacity = self.windowOpacity()
        self._down_left = self._down_max
        self._opacity_timer.start()

    def _calculate_target_y(self) -> int:
        """计算目标Y坐标"""
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        return available_geometry.bottom() - self.height() - self.offset

