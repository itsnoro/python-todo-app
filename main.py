# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QInputDialog
from PyQt6.QtWidgets import QMessageBox
from tasks import load_tasks

class TaskModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._tasks = load_tasks()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        # We'll show: ID, Description, Done
        return 3

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        task = self._tasks[index.row()]
        col = index.column()
        if col == 0:
            return task['id']
        elif col == 1:
            return task['desc']
        elif col == 2:
            return "✓" if task.get('done') else ""
        return None
    def add_task(self, desc: str):
        from tasks import save_tasks
        # Generate new ID
        next_id = max((t["id"] for t in self._tasks), default=0) + 1
        task = {
            "id": next_id,
            "desc": desc,
            "done": False,
            "created_at": "",  # optional
            "completed_at": None
        }
        self.beginInsertRows(QModelIndex(), len(self._tasks), len(self._tasks))
        self._tasks.append(task)
        self.endInsertRows()
        save_tasks(self._tasks)

    def headerData(self, section: int, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return ["ID", "Description", "Done"][section]
    def toggle_done(self, row: int):
        from tasks import save_tasks
        if row < 0 or row >= len(self._tasks):
            return
        task = self._tasks[row]
        task['done'] = not task.get('done', False)
        self.dataChanged.emit(self.index(row, 0), self.index(row, 2))
        save_tasks(self._tasks)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do CLI → GUI")
        self.setMinimumSize(400, 300)

        # --- Model/View setup ---
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.model = TaskModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.resizeColumnsToContents()
        layout.addWidget(self.view)
        # Add Task Button
        button_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Task")
        add_btn.clicked.connect(self.on_add_task)
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)
        done_btn = QPushButton("✅ Mark as Done")
        done_btn.clicked.connect(self.on_mark_done)
        button_layout.addWidget(done_btn)

    def on_add_task(self):
        text, ok = QInputDialog.getText(self, "Add Task", "Enter task description:")
        if ok and text.strip():
            self.model.add_task(text.strip())
            self.view.resizeColumnsToContents()

    def on_mark_done(self):
        index = self.view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No selection", "Please select a task to mark as done.")
            return
        row = index.row()
        self.model.toggle_done(row)
        self.view.clearSelection()
        self.view.resizeColumnsToContents()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
