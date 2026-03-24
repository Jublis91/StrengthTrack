from __future__ import annotations

import csv

from typing import Optional
from PySide6 import QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


from database import (
    delete_test_entry as db_delete_test_entry,
    delete_weight_entry as db_delete_weight_entry,
    get_test_entries,
    get_test_entries_for_name,
    get_user_profile,
    get_weight_entries,
    get_weight_entries_asc,
    get_workout_exercises,
    get_workout_programs,
    save_test_entry,
    save_user,
    save_weight_entry,
    save_workout_exercise,
    save_workout_program,
    update_test_entry as db_update_test_entry,
    update_weight_entry as db_update_weight_entry,
)


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StrengthTrack")

        self.editing_weight_entry_id: Optional[int] = None
        self.editing_test_entry_id: Optional[int] = None
        self.selected_program_id: Optional[int] = None

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
        self.program_name_input = QtWidgets.QLineEdit()
        self.exercise_day_input = QtWidgets.QLineEdit()
        self.exercise_name_input = QtWidgets.QLineEdit()
        self.exercise_sets_input = QtWidgets.QLineEdit()
        self.exercise_reps_input = QtWidgets.QLineEdit()
        self.exercise_extra_weight_input = QtWidgets.QLineEdit()
        self.exercise_note_input = QtWidgets.QLineEdit()

        self.test_results_list = QtWidgets.QListWidget()
        self.weight_table = QtWidgets.QTableWidget()
        self.program_list = QtWidgets.QListWidget()
        self.exercise_list = QtWidgets.QListWidget()

        self.progress_test_selector = QtWidgets.QComboBox()
        self.progress_test_selector.addItems(["punnerrukset", "leuanvedot", "lankku", "kyykyt", "muu"])


        self.weight_date_input.setCalendarPopup(True)
        self.weight_date_input.setDate(QtCore.QDate.currentDate())
        self.test_date_input.setCalendarPopup(True)
        self.test_date_input.setDate(QtCore.QDate.currentDate())

    def _create_buttons(self) -> None:
        self.home_button = QtWidgets.QPushButton("Etusivu")
        self.profile_button = QtWidgets.QPushButton("Profiili")
        self.weight_button = QtWidgets.QPushButton("Paino")
        self.tests_button = QtWidgets.QPushButton("Testit")
        self.workout_button = QtWidgets.QPushButton("Treeniohjelmat")
        self.progress_button = QtWidgets.QPushButton("Kehitys")

        self.save_profile_button = QtWidgets.QPushButton("Tallenna profiili")
        self.save_weight_button = QtWidgets.QPushButton("Tallenna paino")
        self.save_test_button = QtWidgets.QPushButton("Tallenna testi")
        self.save_program_button = QtWidgets.QPushButton("Luo ohjelma")
        self.save_exercise_button = QtWidgets.QPushButton("Lisää liike")

        self.delete_weight_button = QtWidgets.QPushButton("Poista valittu paino")
        self.delete_test_button = QtWidgets.QPushButton("Poista valittu testi")
        self.edit_weight_button = QtWidgets.QPushButton("Muokkaa valittua painoa")
        self.update_weight_button = QtWidgets.QPushButton("Päivitä paino")
        self.edit_test_button = QtWidgets.QPushButton("Muokkaa valittua testiä")
        self.update_test_button = QtWidgets.QPushButton("Päivitä testi")

        self.refresh_graphs_button = QtWidgets.QPushButton("Päivitä graafit")
        self.export_weight_csv_button = QtWidgets.QPushButton("Vie painodata CSV")
        self.export_tests_csv_button = QtWidgets.QPushButton("Vie testidata CSV")


    def _create_pages(self) -> None:
        self.home_label = QtWidgets.QLabel("Profiilia ei löytynyt")
        self.home_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.home_label.setWordWrap(True)

        self.selected_program_label = QtWidgets.QLabel("Valittu ohjelma: ei valintaa")

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
        tests_page_layout.addWidget(QtWidgets.QLabel("Testitulokset"))
        tests_page_layout.addWidget(self.test_results_list)
        self.tests_page.setLayout(tests_page_layout)

        self.workout_page = QtWidgets.QWidget()
        self.workout_page.setLayout(self._build_workout_layout())

        self.weight_figure = Figure(figsize=(5, 3))
        self.weight_canvas = FigureCanvasQTAgg(self.weight_figure)
        self.bmi_figure = Figure(figsize=(5, 3))
        self.bmi_canvas = FigureCanvasQTAgg(self.bmi_figure)
        self.test_figure = Figure(figsize=(5, 3))
        self.test_canvas = FigureCanvasQTAgg(self.test_figure)

        self.progress_page = QtWidgets.QWidget()
        self.progress_page.setLayout(self._build_progress_layout())


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
        form_layout.addRow(QtWidgets.QLabel("Nimi"), self.name_input)
        form_layout.addRow(QtWidgets.QLabel("Pituus (cm)"), self.height_input)
        form_layout.addRow(QtWidgets.QLabel("Aloituspaino (kg)"), self.start_weight_input)
        form_layout.addRow(QtWidgets.QLabel("Tavoite"), self.goal_input)
        form_layout.addRow(self.save_profile_button)
        return form_layout

    def _build_weight_form(self) -> QtWidgets.QFormLayout:
        weight_form_layout = QtWidgets.QFormLayout()
        weight_form_layout.addRow(QtWidgets.QLabel("Päivä"), self.weight_date_input)
        weight_form_layout.addRow(QtWidgets.QLabel("Paino (kg)"), self.weight_input)
        weight_form_layout.addRow(QtWidgets.QLabel("Huomio"), self.weight_note_input)
        weight_form_layout.addRow(self.save_weight_button)
        return weight_form_layout

    def _build_tests_form(self) -> QtWidgets.QFormLayout:
        tests_form_layout = QtWidgets.QFormLayout()
        tests_form_layout.addRow(QtWidgets.QLabel("Päivä"), self.test_date_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Testi"), self.test_name_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Tulos"), self.test_result_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Yksikkö"), self.test_unit_input)
        tests_form_layout.addRow(QtWidgets.QLabel("Huomio"), self.test_comment_input)
        tests_form_layout.addRow(self.save_test_button)
        return tests_form_layout
    
    def _build_workout_form(self) -> QtWidgets.QFormLayout:
        workout_form_layout = QtWidgets.QFormLayout()
        workout_form_layout.addRow(QtWidgets.QLabel("Program name"), self.program_name_input)
        workout_form_layout.addRow(self.save_program_button)
        return workout_form_layout
    
    def _build_workout_layout(self) -> QtWidgets.QVBoxLayout:
        layout = QtWidgets.QVBoxLayout()

        program_form = QtWidgets.QFormLayout()
        program_form.addRow(QtWidgets.QLabel("Ohjelman nimi"), self.program_name_input)
        program_form.addRow(self.save_program_button)

        exercise_form = QtWidgets.QFormLayout()
        exercise_form.addRow(QtWidgets.QLabel("Päivä"), self.exercise_day_input)
        exercise_form.addRow(QtWidgets.QLabel("Liike"), self.exercise_name_input)
        exercise_form.addRow(QtWidgets.QLabel("Sarjat"), self.exercise_sets_input)
        exercise_form.addRow(QtWidgets.QLabel("Toistot"), self.exercise_reps_input)
        exercise_form.addRow(QtWidgets.QLabel("Lisäpaino"), self.exercise_extra_weight_input)
        exercise_form.addRow(QtWidgets.QLabel("Huomio"), self.exercise_note_input)
        exercise_form.addRow(self.save_exercise_button)

        layout.addLayout(program_form)
        layout.addWidget(QtWidgets.QLabel("Treeniohjelmat"))
        layout.addWidget(self.program_list)
        layout.addWidget(self.selected_program_label)
        layout.addLayout(exercise_form)
        layout.addWidget(QtWidgets.QLabel("Ohjelman liikkeet"))
        layout.addWidget(self.exercise_list)

        return layout

    def _build_progress_layout(self) -> QtWidgets.QVBoxLayout:
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Painokehitys"))
        layout.addWidget(self.weight_canvas)
        layout.addWidget(QtWidgets.QLabel("BMI-kehitys"))
        layout.addWidget(self.bmi_canvas)
        layout.addWidget(QtWidgets.QLabel("Testituloksen kehitys"))
        layout.addWidget(self.progress_test_selector)
        layout.addWidget(self.test_canvas)
        layout.addWidget(self.refresh_graphs_button)
        layout.addWidget(self.export_weight_csv_button)
        layout.addWidget(self.export_tests_csv_button)
        layout.addStretch()
        return layout


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
        menu_widget.setFixedWidth(160)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(menu_widget, 1)
        main_layout.addWidget(self.pages, 4)
        return main_layout

    def _configure_weight_table(self) -> None:
        self.weight_table.setColumnCount(4)
        self.weight_table.setHorizontalHeaderLabels(["ID", "Päivä", "Paino (kg)", "Huomio"])
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
        self.save_program_button.clicked.connect(self.save_program)
        self.save_exercise_button.clicked.connect(self.save_exercise)

        self.save_profile_button.clicked.connect(self.save_profile)
        self.save_weight_button.clicked.connect(self.save_weight)
        self.save_test_button.clicked.connect(self.save_test)
        self.save_program_button.clicked.connect(self.save_program)

        self.delete_test_button.clicked.connect(self.delete_test_entry)
        self.delete_weight_button.clicked.connect(self.delete_weight_entry)
        self.edit_weight_button.clicked.connect(self.edit_weight_entry)
        self.update_weight_button.clicked.connect(self.update_weight_entry)
        self.edit_test_button.clicked.connect(self.edit_test_entry)
        self.update_test_button.clicked.connect(self.update_test_entry)

        self.program_list.itemSelectionChanged.connect(self.select_program)

        self.refresh_graphs_button.clicked.connect(self.refresh_graphs)
        self.progress_test_selector.currentTextChanged.connect(self.refresh_test_graph)
        self.export_weight_csv_button.clicked.connect(self.export_weight_csv)
        self.export_tests_csv_button.clicked.connect(self.export_tests_csv)


    def _show_validation_error(self, message: str) -> None:
        QtWidgets.QMessageBox.warning(self, "Virheellinen syöte", message)

    def _show_success(self, message: str) -> None:
        QtWidgets.QMessageBox.information(self, "Onnistui", message)


    def _parse_float(self, field: QtWidgets.QLineEdit, label: str, required: bool = True) -> Optional[float]:
        text = field.text().strip()
        if not text:
            if required:
                self._show_validation_error(f"{label} on pakollinen.")

            return None

        try:
            return float(text)
        except ValueError:
            self._show_validation_error(f"{label} täytyy olla numero.")
            return None

    def _parse_int(self, field: QtWidgets.QLineEdit, label: str, required: bool = True) -> Optional[int]:
        text = field.text().strip()
        if not text:
            if required:
                self._show_validation_error(f"{label} on pakollinen.")
            return None

        try:
            return int(text)
        except ValueError:
            self._show_validation_error(f"{label} täytyy olla kokonaisluku.")

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
        self.load_programs()
        self.pages.setCurrentWidget(self.workout_page)

    def show_progress_page(self) -> None:
        self.refresh_graphs()
        self.pages.setCurrentWidget(self.progress_page)

    def save_profile(self) -> None:
        name = self.name_input.text().strip()
        goal = self.goal_input.text().strip()

        if not name:
            self._show_validation_error("Nimi on pakollinen.")
            return

        height_cm = self._parse_float(self.height_input, "Height")
        start_weight = self._parse_float(self.start_weight_input, "Start weight")
        if height_cm is None or start_weight is None:
            return

        save_user(name, height_cm, start_weight, goal)
        self.load_user_profile()
        self._show_success("Profiili tallennettu.")
        self.pages.setCurrentWidget(self.home_page)

    def load_user_profile(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self.home_label.setText("No profile saved yet.")
            return

        _, name, height_cm, start_weight, goal = profile
        weight_change = self._get_latest_weight_change(profile[0])
        test_change = self._get_latest_test_change(profile[0])
        bmi_text = self._get_latest_bmi(profile[0], height_cm)
        self.home_label.setText(
            f"Nimi: {name}\n"
            f"Pituus: {height_cm} cm\n"
            f"Aloituspaino: {start_weight} kg\n"
            f"Tavoite: {goal}\n\n"
            f"Nykyinen BMI: {bmi_text}\n"
            f"Viimeisin painomuutos: {weight_change}\n"
            f"Viimeisin BMI-muutos: {bmi_change}\n"
            f"Viimeisin testimuutos: {test_change}"

        )

    def _get_latest_weight_change(self, user_id: int) -> str:
        rows = get_weight_entries(user_id)
        if len(rows) < 2:
            return "ei tarpeeksi dataa"
        latest = rows[0][2]
        previous = rows[1][2]
        delta = latest - previous
        sign = "+" if delta > 0 else ""
        return f"{sign}{delta:.1f} kg"

    def _get_latest_test_change(self, user_id: int) -> str:
        rows = get_test_entries(user_id)
        if not rows:
            return "ei testituloksia"

        latest = rows[0]
        latest_test_name = latest[2]
        same_test_rows = [r for r in rows if r[2] == latest_test_name]
        if len(same_test_rows) < 2:
            return f"{latest_test_name}: ei vertailudataa"

        delta = same_test_rows[0][3] - same_test_rows[1][3]
        sign = "+" if delta > 0 else ""
        return f"{latest_test_name}: {sign}{delta:.1f}"

    def _calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        height_m = height_cm / 100
        return weight_kg / (height_m * height_m)

    def _get_latest_bmi(self, user_id: int, height_cm: float) -> str:
        if height_cm <= 0:
            return "ei saatavilla"

        rows = get_weight_entries(user_id)
        if not rows:
            return "ei painodataa"

        bmi_value = self._calculate_bmi(rows[0][2], height_cm)
        return f"{bmi_value:.1f}"

    def _get_latest_bmi_change(self, user_id: int, height_cm: float) -> str:
        if height_cm <= 0:
            return "ei saatavilla"

        rows = get_weight_entries(user_id)
        if len(rows) < 2:
            return "ei tarpeeksi dataa"

        latest_bmi = self._calculate_bmi(rows[0][2], height_cm)
        previous_bmi = self._calculate_bmi(rows[1][2], height_cm)
        delta = latest_bmi - previous_bmi
        sign = "+" if delta > 0 else ""
        return f"{sign}{delta:.1f}"

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
        self.load_user_profile()
        self._show_success("Paino tallennettu.")


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
        self.load_user_profile()
        self._show_success("Painomerkintä poistettu.")


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
        self.load_user_profile()
        self._show_success("Painomerkintä päivitetty.")


    def save_test(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self._show_validation_error("Save profile before adding tests.")
            return

        result_value = self._parse_float(self.test_result_input, "Result")
        if result_value is None:
            return
        
        unit = self.test_unit_input.text().strip()
        if not unit:
            self._show_validation_error("Yksikkö on pakollinen.")
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
        self.load_user_profile()
        self._show_success("Testitulos tallennettu.")


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
        self.load_user_profile()
        self._show_success("Testitulos poistettu.")


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
        
        unit = self.test_unit_input.text().strip()
        if not unit:
            self._show_validation_error("Yksikkö on pakollinen.")
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

        self.load_user_profile()
        self._show_success("Testitulos päivitetty.")

    def save_program(self) -> None:
        name = self.program_name_input.text().strip()
        if not name:
            self._show_validation_error("Ohjelman nimi on pakollinen.")
            return

        self.selected_program_id = save_workout_program(name)
        self.program_name_input.clear()
        self.load_programs()
        self._show_success("Treeniohjelma luotu.")

    def load_programs(self) -> None:
        self.program_list.clear()
        for program_id, name, created_at in get_workout_programs():
            text = f"{name} ({created_at})"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, program_id)
            self.program_list.addItem(item)

    def select_program(self) -> None:
        item = self.program_list.currentItem()
        if item is None:
            self.selected_program_id = None
            self.selected_program_label.setText("Valittu ohjelma: ei valintaa")
            self.exercise_list.clear()
            return

        self.selected_program_id = int(item.data(QtCore.Qt.UserRole))
        self.selected_program_label.setText(f"Valittu ohjelma: {item.text()}")
        self.load_exercises_for_selected_program()

    def save_exercise(self) -> None:
        if self.selected_program_id is None:
            self._show_validation_error("Valitse ensin treeniohjelma listasta.")
            return

        day_name = self.exercise_day_input.text().strip()
        exercise_name = self.exercise_name_input.text().strip()
        if not day_name or not exercise_name:
            self._show_validation_error("Päivä ja liike ovat pakollisia.")
            return

        sets = self._parse_int(self.exercise_sets_input, "Sarjat")
        reps = self._parse_int(self.exercise_reps_input, "Toistot")
        extra_weight = self._parse_float(self.exercise_extra_weight_input, "Lisäpaino", required=False)
        note = self.exercise_note_input.text().strip()
        if sets is None or reps is None:
            return

        save_workout_exercise(
            self.selected_program_id,
            day_name,
            exercise_name,
            sets,
            reps,
            extra_weight,
            note,
        )

        self.exercise_day_input.clear()
        self.exercise_name_input.clear()
        self.exercise_sets_input.clear()
        self.exercise_reps_input.clear()
        self.exercise_extra_weight_input.clear()
        self.exercise_note_input.clear()

        self.load_exercises_for_selected_program()
        self._show_success("Liike lisätty ohjelmaan.")

    def load_exercises_for_selected_program(self) -> None:
        self.exercise_list.clear()
        if self.selected_program_id is None:
            return

        rows = get_workout_exercises(self.selected_program_id)
        for _, day_name, exercise_name, sets, reps, extra_weight, note in rows:
            lisapaino_txt = f", lisäpaino {extra_weight}" if extra_weight is not None else ""
            note_txt = f" ({note})" if note else ""
            self.exercise_list.addItem(
                f"{day_name}: {exercise_name}, {sets} x {reps}{lisapaino_txt}{note_txt}"
            )

    def refresh_graphs(self) -> None:
        self.refresh_weight_graph()
        self.refresh_bmi_graph()
        self.refresh_test_graph()

    def refresh_weight_graph(self) -> None:
        self.weight_figure.clear()
        ax = self.weight_figure.add_subplot(111)

        profile = get_user_profile()
        if profile is None:
            ax.set_title("Ei profiilia")
            self.weight_canvas.draw()
            return

        rows = get_weight_entries_asc(profile[0])
        if not rows:
            ax.set_title("Ei painodataa")
            self.weight_canvas.draw()
            return

        dates = [row[0] for row in rows]
        weights = [row[1] for row in rows]
        ax.plot(dates, weights, marker="o")
        ax.set_title("Painon kehitys")
        ax.set_xlabel("Päivä")
        ax.set_ylabel("Paino (kg)")
        ax.tick_params(axis="x", rotation=45)
        self.weight_figure.tight_layout()
        self.weight_canvas.draw()

    def refresh_test_graph(self) -> None:
        self.test_figure.clear()
        ax = self.test_figure.add_subplot(111)

        profile = get_user_profile()
        if profile is None:
            ax.set_title("Ei profiilia")
            self.test_canvas.draw()
            return

        test_name = self.progress_test_selector.currentText()
        rows = get_test_entries_for_name(profile[0], test_name)
        if not rows:
            ax.set_title(f"Ei dataa testille: {test_name}")
            self.test_canvas.draw()
            return

        dates = [row[0] for row in rows]
        results = [row[1] for row in rows]
        unit = rows[-1][2] or ""
        ax.plot(dates, results, marker="o", color="green")
        ax.set_title(f"{test_name} kehitys")
        ax.set_xlabel("Päivä")
        ax.set_ylabel(f"Tulos {unit}".strip())
        ax.tick_params(axis="x", rotation=45)
        self.test_figure.tight_layout()
        self.test_canvas.draw()

    def refresh_bmi_graph(self) -> None:
        self.bmi_figure.clear()
        ax = self.bmi_figure.add_subplot(111)

        profile = get_user_profile()
        if profile is None:
            ax.set_title("Ei profiilia")
            self.bmi_canvas.draw()
            return

        height_cm = profile[2]
        if height_cm <= 0:
            ax.set_title("Virheellinen pituus")
            self.bmi_canvas.draw()
            return

        rows = get_weight_entries_asc(profile[0])
        if not rows:
            ax.set_title("Ei painodataa BMI:lle")
            self.bmi_canvas.draw()
            return

        dates = [row[0] for row in rows]
        bmi_values = [self._calculate_bmi(row[1], height_cm) for row in rows]
        ax.plot(dates, bmi_values, marker="o", color="purple")
        ax.set_title("BMI kehitys")
        ax.set_xlabel("Päivä")
        ax.set_ylabel("BMI")
        ax.tick_params(axis="x", rotation=45)
        self.bmi_figure.tight_layout()
        self.bmi_canvas.draw()

    def export_weight_csv(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self._show_validation_error("Profiilia ei löydy.")
            return

        rows = get_weight_entries(profile[0])
        if not rows:
            self._show_validation_error("Ei painodataa vietäväksi.")
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Tallenna painodata CSV",
            "painodata.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "paiva", "paino", "huomio"])
            writer.writerows(rows)

        self._show_success("Painodata vietiin CSV-tiedostoon.")

    def export_tests_csv(self) -> None:
        profile = get_user_profile()
        if profile is None:
            self._show_validation_error("Profiilia ei löydy.")
            return

        rows = get_test_entries(profile[0])
        if not rows:
            self._show_validation_error("Ei testidataa vietäväksi.")
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Tallenna testidata CSV",
            "testidata.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "paiva", "testi", "tulos", "yksikko", "huomio"])
            writer.writerows(rows)

        self._show_success("Testidata vietiin CSV-tiedostoon.")
