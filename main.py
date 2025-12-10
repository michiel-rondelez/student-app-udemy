 # main.py
import sqlite3
from PyQt6.QtCore import Qt
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QGridLayout,
    QTableWidget, QTableWidgetItem, QDialog, QComboBox, QVBoxLayout, QToolBar, QStatusBar,QMessageBox
)
from PyQt6.QtGui import QAction, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # --- Menus ---
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add Student
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # About
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        # Search
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)
        search_action.setMenuRole(QAction.MenuRole.NoRole)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Id", "Name", "Course", "Mobile"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self, row, column):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)
    
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog(self)
        dialog.exec()

    def search(self):
        dialog = SearchDialog(self)
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QGridLayout()

        # Name input
        layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input, 0, 1)

        # Course dropdown
        layout.addWidget(QLabel("Course:"), 1, 0)
        self.course_input = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_input.addItems(courses)
        layout.addWidget(self.course_input, 1, 1)

        # Mobile input
        layout.addWidget(QLabel("Mobile:"), 2, 0)
        self.mobile_input = QLineEdit()
        layout.addWidget(self.mobile_input, 2, 1)

        # Add button
        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_student)
        layout.addWidget(add_button, 3, 0, 1, 2)

        self.setLayout(layout)


    def add_student(self):
        name = self.name_input.text()
        course = self.course_input.currentText()
        mobile = self.mobile_input.text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
            (name, course, mobile)
        )
        connection.commit()
        connection.close()

        self.parent().load_data()   # refresh table
        self.close()

class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = window.table.currentRow()

        student_name = window.table.item(index, 1).text()

        self.student_id = window.table.item(index, 0).text()

        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Enter student name")
        layout.addWidget(self.student_name)

        course_name = window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        mobile = window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Enter mobile number")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
            (
                self.student_name.text(),
                self.course_name.itemText(self.course_name.currentIndex()),
                self.mobile.text(),
                self.student_id
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()   # refresh table
        self.close()


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Student")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete this student?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)
        self.setLayout(layout)

    def delete_student(self):
        index = window.table.currentRow()
        self.student_id = window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (self.student_id,)
        )
        connection.commit()
        cursor.close()
        connection.close()
        window.load_data()   # refresh table
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Student deleted successfully!")
        confirmation_widget.exec()

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter student name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        search_text = self.student_name.text().strip()
        if not search_text:
            return

        parent = self.parent()  # MainWindow

        # --- Search in database ---
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM students WHERE name LIKE ?",
            (f"%{search_text}%",)
        )
        result_names = set(row[0].lower() for row in cursor.fetchall())
        connection.close()

        # --- Clear previous selection ---
        parent.table.clearSelection()

        # --- Highlight matching rows in table by name ---
        for row in range(parent.table.rowCount()):
            item = parent.table.item(row, 1)  # column 1 = Name
            if item and item.text().lower() in result_names:
                parent.table.selectRow(row)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.load_data()

    sys.exit(app.exec())
