from __future__ import annotations

from typing import Optional

from PySide6 import QtCore, QtWidgets

from database import (
    delete_test_entry as db_delete_test_entry,
    delete_weight_entry as db_delete_weight_entry,
    get_test_entries,
    get_user_profile,
    get_weight_entries,
    save_test_entry,
    save_user,
    save_weight_entry,
    update_test_entry as db_update_test_entry,
    update_weight_entry as db_update_weight_entry,
)


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StrengthTrack")

        self.editing_weight_entry_id: Optional[int] = None
        self.editing_test_entry_id: Optional[int] = None

        self._create_inputs()
        self._create_buttons()
        self._create_pages()
        self._connect_signals()

        self.pages.setCurrentWidget(self.home_page)
        self.load_user_profile()

    def _create_inputs(self) -> None:
        self.name_input = QtWidgets.QLineEdit()
        self.height_input = QtWidgets.QLineEdit()
        self.start_weight_input = QtWidgets.QLineEdit()
        self.goal_input = QtWidgets.QLineEdit()

        self.weight_date_input = QtWidgets.QDateEdit()
        self.weight_input = QtWidgets.QLineEdit()
        self.weight_note_input = QtWidgets.QLineEdit()

        self.test_date_input = QtWidgets.QDateEdit()
        self.test_name_input = QtWidgets.QComboBox()
        self.test_name_input.addItems(["punnerrukset", "leuanvedot", "lankku", "kyykyt", "muu"])
        self.test_result_input = QtWidgets.QLineEdit()
        self.test_unit_input = QtWidgets.QLineEdit()
        self.test_comment_input = QtWidgets.QLineEdit()

        self.test_results_list = QtWidgets.QListWidget()
        self.weight_table = QtWidgets.QTableWidget()

        self.weight_date_input.setCalendarPopup(True)
        self.weight_date_input.setDate(QtCore.QDate.currentDate())
        self.test_date_input.setCalendarPopup(True)
        self.test_date_input.setDate(QtCore.QDate.currentDate())

    def _create_buttons(self) -> None:
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

    def _create_pages(self) -> None:
        self.home_label = QtWidgets.QLabel("No profile found")
        self.home_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.home_label.setWordWrap(True)

        self._configure_weight_table()

        self.home_page = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout()
        home_layout.addWidget(self.home_label)
        self.home_page.setLayout(home_layout)

        self.profile_page = QtWidgets.QWidget()
        self.profile_page.setLayout(self._build_profile_form())

        self.weight_page = QtWidgets.QWidget()
        weight_page_layout = QtWidgets.QVBoxLayout()
        weight_page_layout.addLayout(self._build_weight_form())
        weight_page_layout.addWidget(self.edit_weight_button)
        weight_page_layout.addWidget(self.update_weight_button)
        weight_page_layout.addWidget(self.delete_weight_button)
        weight_page_layout.addWidget(self.weight_table)
        self.weight_page.setLayout(weight_page_layout)

        self.tests_page = QtWidgets.QWidget()
        tests_page_layout = QtWidgets.QVBoxLayout()
        tests_page_layout.addLayout(self._build_tests_form())
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

        self.setLayout(self._build_main_layout())

    def _build_profile_form(self) -> QtWidgets.QFormLayout:
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(QtWidgets.QLabel("Name"), self.name_input)
        form_layout.addRow(QtWidgets.QLabel("Height (cm)"), self.height_input)
        form_layout.addRow(QtWidgets.QLabel("Start weight (kg)"), self.start_weight_input)
        form_layout.addRow(QtWidgets.QLabel("Goal"), self.goal_input)
        form_layout.addRow(self.save_profile_button)
        return form_layout

    def _build_weight_form(self) -> QtWidgets.QFormLayout:
        weight_form_layout = QtWidgets.QFormLayout()
        weight_form_layout.addRow(QtWidgets.QLabel("Date"), self.weight_date_input)
        weight_form_layout.addRow(QtWidgets.QLabel("Weight (kg)"), self.weight_input)
        weight_form_layout.addRow(QtWidgets.QLabel("Comment"), self.weight_note_input)
        weight_form_layout.addRow(self.save_weight_button)
        return weight_form_layout

    def _build_tests_form(self) -> QtWidgets.QFormLayout:
        tests_form_layout = QtWidgets.QFormLayout()
        tests_form_layout.addRow(QtWidgets.QLabel("Date"), self.test_date_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Test name"), self.test_name_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Result"), self.test_result_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Unit"), self.test_unit_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Comment"), self.test_comment_input)
        tests_form_layout.addRow(self.save_test_button)
        return tests_form_layout

    def _build_main_layout(self) -> QtWidgets.QHBoxLayout:
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
        return main_layout

    def _configure_weight_table(self) -> None:
        self.weight_table.setColumnCount(4)
        self.weight_table.setHorizontalHeaderLabels(["ID", "Date", "Weight (kg)", "Comment"])
        self.weight_table.hideColumn(0)
        self.weight_table.horizontalHeader().setStretchLastSection(True)
        self.weight_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.weight_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.weight_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def _connect_signals(self) -> None:
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

    def _show_validation_error(self, message: str) -> None:
        QtWidgets.QMessageBox.warning(self, "Invalid input", message)

    def _parse_float(self, field: QtWidgets.QLineEdit, label: str) -> Optional[float]:
        text = field.text().strip()
        if not text:
            self._show_validation_error(f"{label} is required.")
            return None

        try:
            return float(text)
        except ValueError:
            self._show_validation_error(f"{label} must be a number.")
            return None

    def show_front_page(self) -> None:
        self.load_user_profile()
        self.pages.setCurrentWidget(self.home_page)

    def show_profile_page(self) -> None:
        self.pages.setCurrentWidget(self.profile_page)

    def show_weight_page(self) -> None:
        self.load_weight_entries()
        self.pages.setCurrentWidget(self.weight_page)

    def show_tests_page(self) -> None:
        self.load_test_entries()
        self.pages.setCurrentWidget(self.tests_page)

    def show_workout_page(self) -> None:
        self.pages.setCurrentWidget(self.workout_page)

    def show_progress_page(self) -> None:
        self.pages.setCurrentWidget(self.progress_page)

    def save_profile(self) -> None:
        name = self.name_input.text().strip()
        goal = self.goal_input.text().strip()

        if not name:
            self._show_validation_error("Name is required.")
            return

        height_cm = self._parse_float(self.height_input, "Height")
        start_weight = self._parse_float(self.start_weight_input, "Start weight")
        if height_cm is None or start_weight is None:
            return

        save_user(name, height_cm, start_weight, goal)
        self.load_user_profile()
        self.pages.setCurrentWidget(self.home_page)

    def load_user_profile(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self.home_label.setText("No profile saved yet.")
            return

        _, name, height_cm, start_weight, goal = profile
        self.home_label.setText(
            f"Name: {name}\n"
            f"Height: {height_cm} cm\n"
            f"Start weight: {start_weight} kg\n"
            f"Goal: {goal}"
        )

    def save_weight(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self._show_validation_error("Save profile before adding weight entries.")
            return

        weight = self._parse_float(self.weight_input, "Weight")
        if weight is None:
            return

        user_id = profile[0]
        entry_date = self.weight_date_input.date().toString("yyyy-MM-dd")
        note = self.weight_note_input.text().strip()

        save_weight_entry(user_id, entry_date, weight, note)
        self.weight_input.clear()
        self.weight_note_input.clear()
        self.load_weight_entries()

    def load_weight_entries(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self.weight_table.setRowCount(0)
            return

        rows = get_weight_entries(profile[0])
        self.weight_table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            entry_id, entry_date, weight, note = row_data
            self.weight_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(entry_id)))
            self.weight_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(entry_date)))
            self.weight_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(str(weight)))
            self.weight_table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(note or ""))

    def delete_weight_entry(self) -> None:
        selected_row = self.weight_table.currentRow()
        if selected_row == -1:
            return

        item = self.weight_table.item(selected_row, 0)
        if item is None:
            return

        db_delete_weight_entry(int(item.text()))
        self.load_weight_entries()

    def edit_weight_entry(self) -> None:
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

    def update_weight_entry(self) -> None:
        if self.editing_weight_entry_id is None:
            return

        weight = self._parse_float(self.weight_input, "Weight")
        if weight is None:
            return

        entry_date = self.weight_date_input.date().toString("yyyy-MM-dd")
        note = self.weight_note_input.text().strip()

        db_update_weight_entry(self.editing_weight_entry_id, entry_date, weight, note)

        self.editing_weight_entry_id = None
        self.weight_input.clear()
        self.weight_note_input.clear()
        self.weight_date_input.setDate(QtCore.QDate.currentDate())
        self.load_weight_entries()

    def save_test(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self._show_validation_error("Save profile before adding tests.")
            return

        result_value = self._parse_float(self.test_result_input, "Result")
        if result_value is None:
            return

        user_id = profile[0]
        entry_date = self.test_date_input.date().toString("yyyy-MM-dd")
        test_name = self.test_name_input.currentText()
        unit = self.test_unit_input.text().strip()
        note = self.test_comment_input.text().strip()

        save_test_entry(user_id, entry_date, test_name, result_value, unit, note)

        self.test_name_input.setCurrentIndex(0)
        self.test_result_input.clear()
        self.test_unit_input.clear()
        self.test_comment_input.clear()
        self.test_date_input.setDate(QtCore.QDate.currentDate())
        self.load_test_entries()

    def load_test_entries(self) -> None:
        profile = get_user_profile()
        self.test_results_list.clear()
        if profile is None:
            return

        rows = get_test_entries(profile[0])
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

    def delete_test_entry(self) -> None:
        selected_item = self.test_results_list.currentItem()
        if selected_item is None:
            return

        entry_id = selected_item.data(QtCore.Qt.UserRole)
        if entry_id is None:
            return

        db_delete_test_entry(int(entry_id))
        self.load_test_entries()

    def edit_test_entry(self) -> None:
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

        test_name_index = self.test_name_input.findText(entry_data["test_name"])
        if test_name_index >= 0:
            self.test_name_input.setCurrentIndex(test_name_index)
        else:
            other_index = self.test_name_input.findText("muu")
            if other_index >= 0:
                self.test_name_input.setCurrentIndex(other_index)

        self.test_result_input.setText(str(entry_data["result_value"]))
        self.test_unit_input.setText(entry_data["unit"])
        self.test_comment_input.setText(entry_data["note"])
        self.editing_test_entry_id = int(entry_id)

    def update_test_entry(self) -> None:
        if self.editing_test_entry_id is None:
            return

        result_value = self._parse_float(self.test_result_input, "Result")
        if result_value is None:
            return

        entry_date = self.test_date_input.date().toString("yyyy-MM-dd")
        test_name = self.test_name_input.currentText()
        unit = self.test_unit_input.text().strip()
        note = self.test_comment_input.text().strip()

        db_update_test_entry(
            self.editing_test_entry_id,
            entry_date,
            test_name,
            result_value,
            unit,
            note,
        )

        self.editing_test_entry_id = None
        self.test_name_input.setCurrentIndex(0)
        self.test_result_input.clear()
        self.test_unit_input.clear()
        self.test_comment_input.clear()
        self.test_date_input.setDate(QtCore.QDate.currentDate())
        self.load_test_entries()
