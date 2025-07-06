import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QInputDialog, QMessageBox, QListWidget, QListWidgetItem,
    QFrame, QLabel, QScrollArea, QSpacerItem, QSizePolicy, QLayout, QToolButton
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from datetime import datetime
from tasks import load_tasks, save_tasks

# Helper to load SVG/PNG icons from res/
def load_icon(name: str) -> QIcon:
    base = os.path.join("res", name)
    for ext in (".svg", ".png"):
        path = base + ext
        if os.path.exists(path):
            return QIcon(path)
    return QIcon()

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=12):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect: QRect, test_only: bool):
        x, y = rect.x(), rect.y()
        lineHeight = 0
        for item in self._items:
            widget = item.widget()
            hint = item.sizeHint()
            if x + hint.width() > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + self.spacing()
                lineHeight = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x += hint.width() + self.spacing()
            lineHeight = max(lineHeight, hint.height())
        return y + lineHeight - rect.y()

class TaskCard(QFrame):
    def __init__(self, task: dict, parent_window: QMainWindow):
        super().__init__(parent_window)
        self.task = task
        self.parent_window = parent_window
        self.setObjectName("taskCard")
        # Square shape
        self.setFixedSize(180, 180)
        # Layout
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        # Description
        title = QLabel(task["desc"])
        title.setWordWrap(True)
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        v.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)

        # Created timestamp
        created_lbl = QLabel(f"Created: {task.get('created_at', '')}")
        created_lbl.setObjectName("timestamp")
        v.addWidget(created_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        # Completed timestamp (only if done)
        if task.get("completed_at"):
            comp_lbl = QLabel(f"Completed: {task['completed_at']}")
            comp_lbl.setObjectName("timestamp")
            v.addWidget(comp_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        v.addStretch()  # push buttons to bottom

        # Buttons row
        h = QHBoxLayout()
        h.setSpacing(6)
        h.setAlignment(Qt.AlignmentFlag.AlignRight)

        # -- DONE button as a checkbox --
        done_btn = QToolButton()
        done_btn.setObjectName("doneBtn")
        done_btn.setCheckable(True)
        done_btn.setChecked(bool(task.get("done", False)))
        # show icon only when checked
        icon = load_icon("done") if done_btn.isChecked() else QIcon()
        done_btn.setIcon(icon)
        done_btn.setFixedSize(24, 24)
        done_btn.clicked.connect(lambda _, b=done_btn: self._toggle_done(b))
        h.addWidget(done_btn)

        # -- EDIT button (icon only) --
        edit_btn = QPushButton()
        edit_btn.setObjectName("cardBtn")
        edit_btn.setIcon(load_icon("edit"))
        edit_btn.setFixedSize(24, 24)
        edit_btn.clicked.connect(lambda _, s=parent_window.on_card_edit: s(self))
        h.addWidget(edit_btn)

        # -- REMOVE button (icon only) --
        remove_btn = QPushButton()
        remove_btn.setObjectName("cardBtn")
        remove_btn.setIcon(load_icon("remove"))
        remove_btn.setFixedSize(24, 24)
        remove_btn.clicked.connect(lambda _, s=parent_window.on_card_remove: s(self))
        h.addWidget(remove_btn)

        v.addLayout(h)

    def _toggle_done(self, btn: QToolButton):
        # Update model
        idx = self.parent_window.model._tasks.index(self.task)
        self.parent_window.model.toggle_done(idx)
        # Toggle icon
        btn.setIcon(load_icon("done") if btn.isChecked() else QIcon())
        # Refresh cards to show completed_at
        self.parent_window.refresh_cards()



class TaskModel:
    def __init__(self, tasks=None):
        self._tasks = tasks or []

    def add_task(self, desc: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_id = max((t["id"] for t in self._tasks), default=0) + 1
        task = {
            "id": next_id,
            "desc": desc,
            "done": False,
            "created_at": now,
            "completed_at": None
        }
        self._tasks.append(task)
        save_tasks(self._tasks)

    def toggle_done(self, index: int):
        """
        Flip the done flag for task at `index`, stamp completed_at when done,
        or clear it when undoing.
        """
        if 0 <= index < len(self._tasks):
            task = self._tasks[index]
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Toggle
            task["done"] = not task.get("done", False)
            # Set or clear completed_at
            task["completed_at"] = now if task["done"] else None
            save_tasks(self._tasks)

    def remove_task(self, index: int):
        if 0 <= index < len(self._tasks):
            del self._tasks[index]
            save_tasks(self._tasks)

    def edit_task(self, index: int, new_desc: str):
        if 0 <= index < len(self._tasks):
            self._tasks[index]["desc"] = new_desc
            save_tasks(self._tasks)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do")
        self.setWindowIcon(load_icon("app"))
        self.setMinimumSize(800, 600)
        self.current_theme = "dark"

        # Central widget & root layout
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)

        # Sidebar (Add + Theme)
        sidebar = QVBoxLayout()
        root_layout.addLayout(sidebar, stretch=0)

        # Task area: scroll + container
        self.model = TaskModel(load_tasks())

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)  # remove white border
        root_layout.addWidget(self.scroll, stretch=1)

        # Card container using FlowLayout
        self.card_container = QWidget()
        self.card_container.setObjectName("cardContainer")
        self.card_layout = FlowLayout(self.card_container, margin=8, spacing=12)

        # Initially show cards (or placeholder)
        self.refresh_cards()

        # Fill sidebar
        add_btn = QPushButton("➕ Add Task")
        add_btn.clicked.connect(self.on_add_task)
        sidebar.addWidget(add_btn)

        theme_btn = QPushButton("🌗 Toggle Theme")
        theme_btn.clicked.connect(self.toggle_theme)
        sidebar.addWidget(theme_btn)

        sidebar.addStretch()

    def refresh_cards(self):
        """Populate the scroll area with either task cards or an empty placeholder."""
        tasks = self.model._tasks

        if not tasks:
            # Show placeholder widget
            placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_widget)
            placeholder_layout.setContentsMargins(0, 0, 0, 0)
            placeholder_layout.addStretch()

            placeholder = QLabel("No tasks yet\n\nClick ➕ to add one!")
            placeholder.setObjectName("emptyPlaceholder")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            placeholder_layout.addWidget(placeholder)
            placeholder_layout.addStretch()

            self.scroll.setWidget(placeholder_widget)
            return

        # Otherwise, show the card container
        self.scroll.setWidget(self.card_container)

        # Clear existing cards
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        # Add each TaskCard
        for task in tasks:
            card = TaskCard(task, parent_window=self)
            self.card_layout.addWidget(card)

    def on_add_task(self):
        text, ok = QInputDialog.getText(self, "Add Task", "Enter task description:")
        if ok and text.strip():
            self.model.add_task(text.strip())
            self.refresh_cards()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        qss = "style_light.qss" if self.current_theme == "light" else "style_dark.qss"
        try:
            with open(qss, "r") as f:
                QApplication.instance().setStyleSheet(f.read())
        except FileNotFoundError:
            pass

    def on_card_mark(self, card: TaskCard):
        idx = self.model._tasks.index(card.task)
        self.model.toggle_done(idx)
        self.refresh_cards()

    def on_card_edit(self, card: TaskCard):
        idx = self.model._tasks.index(card.task)
        current = card.task["desc"]
        new_desc, ok = QInputDialog.getText(
            self, "Edit Task", "New description:", text=current
        )
        if ok and new_desc.strip() and new_desc.strip() != current:
            self.model.edit_task(idx, new_desc.strip())
            self.refresh_cards()

    def on_card_remove(self, card: TaskCard):
        idx = self.model._tasks.index(card.task)
        confirm = QMessageBox.question(
            self, "Delete Task",
            f"Remove \"{card.task['desc']}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.remove_task(idx)
            self.refresh_cards()



def main():
    app = QApplication(sys.argv)
    # Load default (dark) theme
    try:
        with open("style_dark.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
