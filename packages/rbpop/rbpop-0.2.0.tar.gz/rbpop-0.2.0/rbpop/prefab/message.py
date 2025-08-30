from win.manager import WinManager
from win.popped import PopWin
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

X_MARGIN, Y_MARGIN = 5, 3
BTNX_MARGIN, BTNY_MARGIN = 2, 1
TITLE_STYLE = {"font-family": "Consolas", "font-size": "16px", "font-weight": "bold"}
MESSAGE_STYLE = {"font-family": "Consolas", "font-size": "14px"}
COLOR_INFO = "rgb(140, 190, 122)"
COLOR_WARN = "rgb(195, 185, 72)"
COLOR_ERROR = "rgb(190, 140, 122)"


class CloseButton(QPushButton):
    def __init__(self, parent=None, back_color:str=None, color:str=None, border_color:str=None, *, border=0):
        super().__init__(parent)
        if back_color is None:
            back_color = 'red'
        self.back_color = back_color
        if color is None:
            color = 'black'
        self.font_color = color
        if border_color is None:
            border_color = 'black'
        self.border_color = border_color
        self.border_width = border
        self.initUI()

    def initUI(self):
        self.setFixedSize(16, 16)
        self.setText('X')
        style = ""
        style += f"background-color:{self.back_color};"
        style += f'font-family: "Consolas";'
        style += f'font-size: 12px;'
        style += f"font-weight:bold;"
        style += f"color:{self.font_color};"
        style += f"padding-left:0px;"
        style += f"padding-top:0px;"
        style += f"border-radius:8px;"
        style += f"border: {self.border_width}px solid {self.border_color};"


        self.setStyleSheet(style)

    def moveToCornor(self):
        parent = self.parent()
        if not parent:
            return

        size = parent.size()
        size.setWidth(size.width() - 2 * BTNX_MARGIN)
        size.setHeight(size.height() - 2 * BTNY_MARGIN)
        self.move(BTNX_MARGIN + size.width() - self.width(), BTNY_MARGIN)




def QSS_Str2Dict(qss_txt:str):
    _column_splits = qss_txt.split(';')
    qss_dict = {}
    for item in _column_splits:
        if not item:
            continue
        # find :
        _index = item.find(':')
        if _index == -1:
            raise ValueError(f"Unexpected qss: '{item}' in '{qss_txt}'")
        # split key and value
        key, value = item[:_index], item[_index + 1:]
        # remove blank start | end
        while key[0] in [' ', '\t']:
            key = key[1:]
        while key[-1] in [' ', '\t']:
            key = key[:-1]
        key = key.lower()

        qss_dict[key] = value
    return qss_dict

def QSS_Dict2Str(qss_dict:dict):
    txt = ""
    for k, v in qss_dict.items():
        txt += f"{k}:{v};"

    return txt


class QPMsg(PopWin):
    def __init__(self, msg:str, title=None, ct:int=4000, *, msg_style=None, title_style=None, close=False, slide_in=True, slide_duration=800, **kwargs):
        self.msg = msg
        self.msg_style = msg_style
        self.title = title
        self.title_style = title_style
        self.close_btn = close
        super(QPMsg, self).__init__(ct, slide_in=slide_in, slide_duration=slide_duration, **kwargs)

    def initUI(self):
        # self.setStyleSheet(f"background-color: {COLOR_INFO};")
        self.setWindowOpacity(0.85)

        self._rootL = QVBoxLayout(self)
        self._rootL.setContentsMargins(0, 0, 0, 0)
        self._rootL.setSpacing(0)

        self._headL = QHBoxLayout()
        self._headL.setContentsMargins(X_MARGIN, Y_MARGIN, X_MARGIN, Y_MARGIN)
        self._headL.setSpacing(0)
        self._rootL.addLayout(self._headL)


        # Add a title label
        if self.title is not None:
            self.lbl_title = QLabel(self)
            self.lbl_title.setText(str(self.title))
            self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
            title_qss = TITLE_STYLE.copy()
            if self.title_style is not None:
                title_qss.update(QSS_Str2Dict(str(self.title_style)))
            self.lbl_title.setStyleSheet(QSS_Dict2Str(title_qss))
            self._headL.addWidget(self.lbl_title)

        # Add a spacer
        self._headL.addStretch(1)

        # closebutton
        if self.close_btn:
            # self.btn_close = CloseButton(self, "rgb(195, 125, 105)", "rgb(50, 50, 50)")
            self.btn_close = CloseButton(self, "rgb(195, 195, 195)", "rgb(50, 50, 50)")
            # self.btn_close.moveToCornor()
            self.btn_close.clicked.connect(self.close)
            self._headL.addWidget(self.btn_close)


        # Add a msg label
        self._rootL.addStretch(1)
        self.lbl_msg = QLabel(self)
        self.lbl_msg.setText(self.msg)
        # Consolas 12, Center
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # fit widget
        # _size = self.size()
        # _size.setWidth(_size.width() - 2 * X_MARGIN)
        # _size.setHeight(_size.height() - 2 * Y_MARGIN)
        # self.lbl_msg.resize(_size)
        msg_qss = MESSAGE_STYLE.copy()
        if self.msg_style is not None:
            msg_qss.update(QSS_Str2Dict(str(self.msg_style)))
        self.lbl_msg.setStyleSheet(QSS_Dict2Str(msg_qss))
        self._rootL.addWidget(self.lbl_msg)
        self._rootL.addStretch(1)



class QPInfo(QPMsg):
    def initUI(self):
        super(QPInfo, self).initUI()
        self.setStyleSheet(f"background-color: {COLOR_INFO};")

class QPWarn(QPMsg):
    def initUI(self):
        super(QPWarn, self).initUI()
        self.setStyleSheet(f"background-color: {COLOR_WARN};")

class QPError(QPMsg):
    def initUI(self):
        super(QPError, self).initUI()
        self.setStyleSheet(f"background-color: {COLOR_ERROR};")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wm = WinManager()
    wm.add(QPInfo("This is a message. | 带有关闭按钮.", 'Information:', 5000, close=True))
    wm.add(QPWarn("This is a message. | 没有标题.", ct=6500))
    wm.add(QPError("This is a message. | 红色的标题.", 'Error:', 8000, title_style="color:red"))

    sys.exit(app.exec())

