"""
rbpop - 优雅的PyQt6弹窗管理库
"""

from rbpop.win import QPop
from rbpop.prefab.message import QPMsg, QPInfo, QPWarn, QPError

__all__ = ['QPop', 'QPMsg', 'QPInfo', 'QPWarn', 'QPError']

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)  # 创建QApplication实例
    QPop(QPMsg("Hello rbpop!", "测试", 3000))
    # 阻止程序退出
    sys.exit(app.exec())
    








