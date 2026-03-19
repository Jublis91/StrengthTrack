import sys

from PySide6 import QtCore, QtWidgets
from database import (
    init_db,
    save_user,
    get_user_profile,
    save_weight_entry,
    save_test_entry,
    get_test_entries,
    get_weight_entries,
    delete_test_entry as db_delete_test_entry,
    delete_weight_entry as db_delete_weight_entry,
    update_weight_entry as db_update_weight_entry,
    update_test_entry as db_update_test_entry,
)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StrengthTrack")

        self.home_button = QtWidgets.QPushButton("Front page")
        self.profile_button = QtWidgets.QPushButton("Profile")
        self.weight_button = QtWidgets.QPushButton("Weight")
        self.tests_button = QtWidgets.QPushButton("Tests")
        self.workout_button = QtWidgets.QPushButton("Workout")
        self.progress_button = QtWidgets.QPushButton("Progress")

        self.save_profile_button = QtWidgets.QPushButton("Save profile")
        self.save_weight_button = QtWidgets.QPushButton("Save weight")
        self.save_test_button = QtWidgets.QPushButton("Save test")
        self.delete_weight_button = QtWidgets.QPushButton("Delete selected weight")
        self.delete_test_button = QtWidgets.QPushButton("Delete selected test")
        self.edit_weight_button = QtWidgets.QPushButton("Edit selected weight")
        self.update_weight_button = QtWidgets.QPushButton("Update weight")
        self.edit_test_button = QtWidgets.QPushButton("Edit selected test")
        self.update_test_button = QtWidgets.QPushButton("Update test")


        self.editing_weight_entry_id = None
        self.editing_test_entry_id = None

        self.name_input = QtWidgets.QLineEdit()
        self.height_input = QtWidgets.QLineEdit()
        self.start_weight_input = QtWidgets.QLineEdit()
        self.goal_input = QtWidgets.QLineEdit()

        self.weight_date_input = QtWidgets.QDateEdit()
        self.weight_input = QtWidgets.QLineEdit()
        self.weight_note_input = QtWidgets.QLineEdit()
        self.test_date_input = QtWidgets.QDateEdit()
        self.test_name_input = QtWidgets.QLineEdit()
        self.test_result_input = QtWidgets.QLineEdit()
        self.test_unit_input = QtWidgets.QLineEdit()
        self.test_comment_input = QtWidgets.QLineEdit()
        self.test_results_list = QtWidgets.QListWidget()

        self.weight_date_input.setCalendarPopup(True)
        self.weight_date_input.setDate(QtCore.QDate.currentDate())
        self.test_date_input.setCalendarPopup(True)
        self.test_date_input.setDate(QtCore.QDate.currentDate())

        self.home_label = QtWidgets.QLabel("No profile found")
        self.home_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.home_label.setWordWrap(True)

        name_label = QtWidgets.QLabel("Name")
        height_label = QtWidgets.QLabel("Height (cm)")
        start_weight_label = QtWidgets.QLabel("Start weight (kg)")
        goal_label = QtWidgets.QLabel("Goal")

        weight_date_label = QtWidgets.QLabel("Date")
        weight_value_label = QtWidgets.QLabel("Weight (kg)")
        weight_note_label = QtWidgets.QLabel("Comment")
        test_date_label = QtWidgets.QLabel("Date")
        test_name_label = QtWidgets.QLabel("Test name")
        test_result_label = QtWidgets.QLabel("Result")
        test_unit_label = QtWidgets.QLabel("Unit")
        test_comment_label = QtWidgets.QLabel("Comment")

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(name_label, self.name_input)
        form_layout.addRow(height_label, self.height_input)
        form_layout.addRow(start_weight_label, self.start_weight_input)
        form_layout.addRow(goal_label, self.goal_input)
        form_layout.addRow(self.save_profile_button)

        weight_form_layout = QtWidgets.QFormLayout()
        weight_form_layout.addRow(weight_date_label, self.weight_date_input)
        weight_form_layout.addRow(weight_value_label, self.weight_input)
        weight_form_layout.addRow(weight_note_label, self.weight_note_input)
        weight_form_layout.addRow(self.save_weight_button)

        tests_form_layout = QtWidgets.QFormLayout()
        tests_form_layout.addRow(test_date_label, self.test_date_input)
        tests_form_layout.addRow(test_name_label, self.test_name_input)
        tests_form_layout.addRow(test_result_label, self.test_result_input)
        tests_form_layout.addRow(test_unit_label, self.test_unit_input)
        tests_form_layout.addRow(test_comment_label, self.test_comment_input)
        tests_form_layout.addRow(self.save_test_button)

        self.weight_table = QtWidgets.QTableWidget()
        self.weight_table.setColumnCount(4)
        self.weight_table.setHorizontalHeaderLabels(["ID", "Date", "Weight (kg)", "Comment"])
        self.weight_table.hideColumn(0)
        self.weight_table.horizontalHeader().setStretchLastSection(True)
        self.weight_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.weight_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.weight_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.home_page = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout()
        home_layout.addWidget(self.home_label)
        self.home_page.setLayout(home_layout)

        self.profile_page = QtWidgets.QWidget()
        self.profile_page.setLayout(form_layout)

        self.weight_page = QtWidgets.QWidget()
        weight_page_layout = QtWidgets.QVBoxLayout()
        weight_page_layout.addLayout(weight_form_layout)
        weight_page_layout.addWidget(self.edit_weight_button)
        weight_page_layout.addWidget(self.update_weight_button)
        weight_page_layout.addWidget(self.delete_weight_button)
        weight_page_layout.addWidget(self.weight_table)
        self.weight_page.setLayout(weight_page_layout)

        self.tests_page = QtWidgets.QWidget()
        tests_page_layout = QtWidgets.QVBoxLayout()
        tests_page_layout.addLayout(tests_form_layout)
        tests_page_layout.addWidget(self.edit_test_button)
        tests_page_layout.addWidget(self.update_test_button)
        tests_page_layout.addWidget(self.delete_test_button)
        tests_page_layout.addWidget(QtWidgets.QLabel("Test results"))
        tests_page_layout.addWidget(self.test_results_list)
        self.tests_page.setLayout(tests_page_layout)

        self.workout_page = QtWidgets.QLabel("Workout Page", alignment=QtCore.Qt.AlignCenter)
        self.progress_page = QtWidgets.QLabel("Progress Page", alignment=QtCore.Qt.AlignCenter)

        self.pages = QtWidgets.QStackedWidget()
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.profile_page)
        self.pages.addWidget(self.weight_page)
        self.pages.addWidget(self.tests_page)
        self.pages.addWidget(self.workout_page)
        self.pages.addWidget(self.progress_page)

        menu_layout = QtWidgets.QVBoxLayout()
        menu_layout.addWidget(self.home_button)
        menu_layout.addWidget(self.profile_button)
        menu_layout.addWidget(self.weight_button)
        menu_layout.addWidget(self.tests_button)
        menu_layout.addWidget(self.workout_button)
        menu_layout.addWidget(self.progress_button)
        menu_layout.addStretch()

        menu_widget = QtWidgets.QWidget()
        menu_widget.setLayout(menu_layout)
        menu_widget.setFixedWidth(120)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(menu_widget, 1)
        main_layout.addWidget(self.pages, 3)

        self.setLayout(main_layout)

        self.home_button.clicked.connect(self.show_front_page)
        self.profile_button.clicked.connect(self.show_profile_page)
        self.weight_button.clicked.connect(self.show_weight_page)
        self.tests_button.clicked.connect(self.show_tests_page)
        self.workout_button.clicked.connect(self.show_workout_page)
        self.progress_button.clicked.connect(self.show_progress_page)
        self.save_profile_button.clicked.connect(self.save_profile)
        self.save_weight_button.clicked.connect(self.save_weight)
        self.save_test_button.clicked.connect(self.save_test)
        self.delete_test_button.clicked.connect(self.delete_test_entry)
        self.delete_weight_button.clicked.connect(self.delete_weight_entry)
        self.edit_weight_button.clicked.connect(self.edit_weight_entry)
        self.update_weight_button.clicked.connect(self.update_weight_entry)
        self.edit_test_button.clicked.connect(self.edit_test_entry)
        self.update_test_button.clicked.connect(self.update_test_entry)


        self.pages.setCurrentWidget(self.home_page)
        self.load_user_profile()

    def show_front_page(self):
        self.load_user_profile()
        self.pages.setCurrentWidget(self.home_page)

    def show_profile_page(self):
        self.pages.setCurrentWidget(self.profile_page)

    def show_weight_page(self):
        self.load_weight_entries()
        self.pages.setCurrentWidget(self.weight_page)

    def show_tests_page(self):
        self.load_test_entries()
        self.pages.setCurrentWidget(self.tests_page)

    def show_workout_page(self):
        self.pages.setCurrentWidget(self.workout_page)

    def show_progress_page(self):
        self.pages.setCurrentWidget(self.progress_page)

    def save_profile(self):
        name = self.name_input.text()
        height_cm = float(self.height_input.text())
        start_weight = float(self.start_weight_input.text())
        goal = self.goal_input.text()

        save_user(name, height_cm, start_weight, goal)
        self.load_user_profile()
        self.pages.setCurrentWidget(self.home_page)

    def load_user_profile(self):
        profile = get_user_profile()

        if profile is None:
            self.home_label.setText("No profile saved yet.")
            return

        user_id, name, height_cm, start_weight, goal = profile

        self.home_label.setText(
            f"Name: {name}\n"
            f"Height: {height_cm} cm\n"
            f"Start weight: {start_weight} kg\n"
            f"Goal: {goal}"
        )

    def save_weight(self):
        profile = get_user_profile()

        if profile is None:
            return

        user_id = profile[0]
        entry_date = self.weight_date_input.date().toString("yyyy-MM-dd")
        weight = float(self.weight_input.text())
        note = self.weight_note_input.text()

        save_weight_entry(user_id, entry_date, weight, note)
        self.load_weight_entries()

    def load_weight_entries(self):
        profile = get_user_profile()

        if profile is None:
            self.weight_table.setRowCount(0)
            return

        user_id = profile[0]
        rows = get_weight_entries(user_id)

        self.weight_table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            entry_id, entry_date, weight, note = row_data

            self.weight_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(entry_id)))
            self.weight_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(entry_date)))
            self.weight_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(str(weight)))
            self.weight_table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(note or ""))

    def delete_weight_entry(self):
        selected_row = self.weight_table.currentRow()

        if selected_row == -1:
            return

        item = self.weight_table.item(selected_row, 0)

        if item is None:
            return

        entry_id = int(item.text())
        db_delete_weight_entry(entry_id)
        self.load_weight_entries()

    def edit_weight_entry(self):
        selected_row = self.weight_table.currentRow()

        if selected_row == -1:
            return

        id_item = self.weight_table.item(selected_row, 0)
        date_item = self.weight_table.item(selected_row, 1)
        weight_item = self.weight_table.item(selected_row, 2)
        note_item = self.weight_table.item(selected_row, 3)

        if id_item is None or date_item is None or weight_item is None:
            return

        self.editing_weight_entry_id = int(id_item.text())

        date_value = QtCore.QDate.fromString(date_item.text(), "yyyy-MM-dd")
        if date_value.isValid():
            self.weight_date_input.setDate(date_value)

        self.weight_input.setText(weight_item.text())
        self.weight_note_input.setText(note_item.text() if note_item else "")

    def update_weight_entry(self):
        if self.editing_weight_entry_id is None:
            return

        entry_date = self.weight_date_input.date().toString("yyyy-MM-dd")
        weight = float(self.weight_input.text())
        note = self.weight_note_input.text()

        db_update_weight_entry(self.editing_weight_entry_id, entry_date, weight, note)

        self.editing_weight_entry_id = None
        self.weight_input.clear()
        self.weight_note_input.clear()
        self.weight_date_input.setDate(QtCore.QDate.currentDate())

        self.load_weight_entries()

    def save_test(self):
        profile = get_user_profile()

        if profile is None:
            return
        
        user_id = profile[0]
        entry_date = self.test_date_input.date().toString("yyyy-MM-dd")
        test_name = self.test_name_input.text()
        result_value = float(self.test_result_input.text())
        unit = self.test_unit_input.text()
        note = self.test_comment_input.text()

        save_test_entry(user_id, entry_date, test_name, result_value, unit, note)

        self.test_name_input.clear()
        self.test_result_input.clear()
        self.test_unit_input.clear()
        self.test_comment_input.clear()
        self.test_date_input.setDate(QtCore.QDate.currentDate())
        self.load_test_entries()

    def load_test_entries(self):
        profile = get_user_profile()

        self.test_results_list.clear()

        if profile is None:
            return

        user_id = profile[0]
        rows = get_test_entries(user_id)

        for entry_id, entry_date, test_name, result_value, unit, note in rows:
            unit_text = f" {unit}" if unit else ""
            note_text = f" ({note})" if note else ""
            entry_text = f"{entry_date} - {test_name}: {result_value}{unit_text}{note_text}"
            item = QtWidgets.QListWidgetItem(entry_text)
            item.setData(QtCore.Qt.UserRole, entry_id)
            item.setData(
                QtCore.Qt.UserRole + 1,
                {
                    "entry_date": entry_date,
                    "test_name": test_name,
                    "result_value": result_value,
                    "unit": unit or "",
                    "note": note or "",
                },
            )
            self.test_results_list.addItem(item)

    def delete_test_entry(self):
        selected_item = self.test_results_list.currentItem()

        if selected_item is None:
            return

        entry_id = selected_item.data(QtCore.Qt.UserRole)

        if entry_id is None:
            return

        db_delete_test_entry(int(entry_id))
        self.load_test_entries()
    
    def edit_test_entry(self):
        selected_item = self.test_results_list.currentItem()

        if selected_item is None:
            return

        entry_id = selected_item.data(QtCore.Qt.UserRole)
        if entry_id is None:
            return

        entry_data = selected_item.data(QtCore.Qt.UserRole + 1)
        if not isinstance(entry_data, dict):
            return

        date_value = QtCore.QDate.fromString(entry_data["entry_date"], "yyyy-MM-dd")
        if date_value.isValid():
            self.test_date_input.setDate(date_value)

        self.test_name_input.setText(entry_data["test_name"])
        self.test_result_input.setText(str(entry_data["result_value"]))
        self.test_unit_input.setText(entry_data["unit"])
        self.test_comment_input.setText(entry_data["note"])
        self.editing_test_entry_id = int(entry_id)

    def update_test_entry(self):
        if self.editing_test_entry_id is None:
            return

        entry_date = self.test_date_input.date().toString("yyyy-MM-dd")
        test_name = self.test_name_input.text()
        result_value = float(self.test_result_input.text())
        unit = self.test_unit_input.text()
        note = self.test_comment_input.text()

        db_update_test_entry(
            self.editing_test_entry_id,
            entry_date,
            test_name,
            result_value,
            unit,
            note,
        )

        self.editing_test_entry_id = None
        self.test_name_input.clear()
        self.test_result_input.clear()
        self.test_unit_input.clear()
        self.test_comment_input.clear()
        self.test_date_input.setDate(QtCore.QDate.currentDate())
        self.load_test_entries()





if __name__ == "__main__":
    init_db()

    app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())