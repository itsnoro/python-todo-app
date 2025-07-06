# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
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

    def headerData(self, section: int, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
        return ["ID", "Description", "Done"][section]

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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
