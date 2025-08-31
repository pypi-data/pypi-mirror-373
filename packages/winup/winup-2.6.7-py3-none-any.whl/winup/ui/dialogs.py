from PySide6.QtWidgets import QMessageBox

def show_message(title: str, text: str, type: str = "info"):
    """
    Displays a simple modal dialog box.
    
    Args:
        title: The title of the message box window.
        text: The main text to display.
        type: The type of message. Can be 'info', 'warning', 'error', or 'question'.
    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    
    icon = {
        "info": QMessageBox.Information,
        "warning": QMessageBox.Warning,
        "error": QMessageBox.Critical,
        "question": QMessageBox.Question
    }.get(type.lower(), QMessageBox.NoIcon)
    
    msg_box.setIcon(icon)
    
    if type.lower() == 'question':
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    else:
        msg_box.setStandardButtons(QMessageBox.Ok)
        
    # Returns QMessageBox.Yes, QMessageBox.No, or QMessageBox.Ok
    return msg_box.exec() 