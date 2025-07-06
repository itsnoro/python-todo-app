# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QInputDialog
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
from tasks import load_tasks

class TaskModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._tasks = load_tasks()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._tasks)

    def columnCount(self, parent=QModelIndex()):
        return 5  # ID, Desc, Done, Created, Completed

    def headerData(self, section, orientation, role):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return ["ID", "Description", "Done", "Created At", "Completed At"][section]

    def data(self, index, role):
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
        elif col == 3:
            return task.get("created_at", "")
        elif col == 4:
            return task.get("completed_at", "")
        return None

    def add_task(self, desc: str):
        from tasks import save_tasks
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_id = max((t["id"] for t in self._tasks), default=0) + 1
        task = {
            "id": next_id,
            "desc": desc,
            "done": False,
            "created_at": now,
            "completed_at": None
        }
        self.beginInsertRows(QModelIndex(), len(self._tasks), len(self._tasks))
        self._tasks.append(task)
        self.endInsertRows()
        save_tasks(self._tasks)
    
    def toggle_done(self, row: int):
        from tasks import save_tasks
        if row < 0 or row >= len(self._tasks):
            return
        task = self._tasks[row]
        task["done"] = not task.get("done", False)

        if task["done"]:
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            task["completed_at"] = None

        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount()))
        save_tasks(self._tasks)

    def remove_task(self, row: int):
        from tasks import save_tasks
        if 0 <= row < len(self._tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self.endRemoveRows()
            save_tasks(self._tasks)

    def edit_task(self, row: int, new_desc: str):
        from tasks import save_tasks
        if 0 <= row < len(self._tasks):
            self._tasks[row]["desc"] = new_desc
            self.dataChanged.emit(self.index(row, 1), self.index(row, 1))
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
        remove_btn = QPushButton("🗑 Remove Task")
        remove_btn.clicked.connect(self.on_remove_task)
        button_layout.addWidget(remove_btn)
        edit_btn = QPushButton("✏ Edit Task")
        edit_btn.clicked.connect(self.on_edit_task)
        button_layout.addWidget(edit_btn)



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

    def on_remove_task(self):
        index = self.view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No selection", "Please select a task to remove.")
            return

        row = index.row()
        task_id = self.model._tasks[row]["id"]
        task_desc = self.model._tasks[row]["desc"]

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove task [{task_id}]: \"{task_desc}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.model.remove_task(row)
            self.view.clearSelection()

    def on_edit_task(self):
        index = self.view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No selection", "Please select a task to edit.")
            return

        row = index.row()
        current_desc = self.model._tasks[row]["desc"]

        new_desc, ok = QInputDialog.getText(
            self,
            "Edit Task",
            "Edit the task description:",
            text=current_desc
        )

        if ok and new_desc.strip() and new_desc.strip() != current_desc:
            self.model.edit_task(row, new_desc.strip())
            self.view.clearSelection()
  


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
