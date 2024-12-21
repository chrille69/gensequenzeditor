import logging
from PySide6.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout, QWidget

def logme(loggerfunc):
    def decorator(func):
        def wrapper(*args, **kwargs):
            argstr = ",".join([str(arg) for arg in args]+[str(k)+"="+str(v) for k,v in kwargs])
            loggerfunc(f'Enter {func.__name__}({argstr})')
            retval = func(*args, **kwargs)
            loggerfunc(f'Exit {func.__name__} mit {str(retval)}')
            return retval
        return wrapper
    return decorator


class TextLogHandler(logging.Handler):
    def __init__(self, textedit: QPlainTextEdit):
        super().__init__()
        self._textedit = textedit
        fmt = '%(asctime)s %(message)s'
        self.setFormatter(logging.Formatter(fmt))
    def emit(self, record):
        self._textedit.appendPlainText(self.format(record))


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._textedit = QPlainTextEdit()
        vboxlayout = QVBoxLayout()
        self.setLayout(vboxlayout)
        vboxlayout.addWidget(self._textedit)

        self._loghandler = TextLogHandler(self._textedit)

    @property
    def loghandler(self):
        return self._loghandler