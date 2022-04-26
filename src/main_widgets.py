from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING
from typing import Union, List, Tuple, Dict

from PySide6.QtCore import Signal, QSortFilterProxyModel
from PySide6.QtGui import QKeySequence, QShortcut, Qt
from PySide6.QtWidgets import QWidget, QListView, QMessageBox, QDialog, QDialogButtonBox, QListWidgetItem, \
    QTreeWidgetItem

from src import main_application
from src.database import db
from src.datatypes import Question
from src.datatypes import QuestionGroup
from src.dock_widgets import SelfTestDockWidget
from src.filter_editor import FilterEditor
from src.question_table import RuleSortFilterProxyModel, QuestionGroupTableView, QuestionGroupDataModel
from src.ui_first_setup_widget import Ui_FirstSetupWidget
from src.ui_question_group_editor import Ui_QuestionGroupEditor
from src.ui_question_overview_widget import Ui_QuestionOverviewWidget
from src.ui_self_test_widget import Ui_SelfTestWidget

if TYPE_CHECKING:
    from src.main_application import MainWindow


class EditorResult(Enum):
    Success = auto()
    Invalid = auto()
    Canceled = auto()


class QuestionGroupEditor(QDialog, Ui_QuestionGroupEditor):
    def __init__(self, id: int = 1, name: str = "", parent=None):
        super(QuestionGroupEditor, self).__init__(parent=parent)
        self.ui = Ui_QuestionGroupEditor()
        self.ui.setupUi(self)
        self.id = id
        self.name = name

    @property
    def id(self):
        return self.ui.question_group_id.value()

    @id.setter
    def id(self, value):
        self.ui.question_group_id.setValue(value)

    @property
    def name(self):
        return self.ui.question_group_name.text()

    @name.setter
    def name(self, value):
        self.ui.question_group_name.setText(value)


class QuestionOverviewWidget(QWidget, Ui_QuestionOverviewWidget):
    def __init__(self, main_window: MainWindow):
        super(QuestionOverviewWidget, self).__init__(main_window)
        self.ui = Ui_QuestionOverviewWidget()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.ui.tabWidget.clear()
        self.ui.tabWidget.setTabsClosable(True)
        self.ui.tabWidget.tabCloseRequested.connect(self.delete_question_group)
        self.ui.tabWidget.tabBarDoubleClicked.connect(self.rename_question_group)

        self.ui.filter_list.clear()
        left_shortcut = QShortcut(QKeySequence(QKeySequence.MoveToPreviousChar), self, None, None,
                                  Qt.WidgetWithChildrenShortcut)
        left_shortcut.activated.connect(self.last_question_group)

        right_shortcut = QShortcut(QKeySequence(QKeySequence.MoveToNextChar), self, None, None,
                                   Qt.WidgetWithChildrenShortcut)
        right_shortcut.activated.connect(self.next_question_group)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.ui.filter_list, None, None, Qt.WidgetShortcut)
        delete_shortcut.activated.connect(self.delete_selected_filter)
        self.ui.filter_list.setSelectionMode(QListView.ExtendedSelection)
        self.ui.filter_list.itemDoubleClicked.connect(self.add_filter)
        self.ui.add_filter.clicked.connect(self.add_filter)

        self.question_group_tabs = []  # type: List[Tuple[QuestionGroup, QSortFilterProxyModel, QuestionGroupDataModel]]
        self.questions = {}  # type: Dict[QTreeWidgetItem, str]

    def next_question_group(self):
        if self.ui.tabWidget.currentIndex() < self.ui.tabWidget.count() - 1:
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.currentIndex() + 1)

    def last_question_group(self):
        if self.ui.tabWidget.currentIndex() > 0:
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.currentIndex() - 1)

    def delete_selected_filter(self):
        selection_model = self.ui.filter_list.selectionModel()
        if not selection_model.hasSelection():
            return
        selected_rows = sorted([index.row() for index in selection_model.selectedRows()], reverse=True)
        for index in selected_rows:
            self.__delete_filter(index)
        self.refresh_column_filter()

    def __delete_filter(self, index):
        RuleSortFilterProxyModel.filters.pop(index)
        filter_item = self.ui.filter_list.takeItem(index)
        del filter_item

    def delete_question_group(self, index_tabwidget: int):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Fragengruppe löschen.")
        msgBox.setText("Möchtest du diese Fragengruppe wirklich löschen?<br>"
                       "Dies lässt sich nicht umkehren!")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Yes:
            question_group, _, _ = self.question_group_tabs[index_tabwidget]
            self.question_group_tabs.pop(index_tabwidget)
            db.delete(question_group)
            self.ui.tabWidget.removeTab(index_tabwidget)

        if not self.question_group_tabs:
            self.main_window.initialize()

    def create_question_group_tab(self, question_group: QuestionGroup):
        tab = QWidget()
        view = QuestionGroupTableView(tab)
        model = QuestionGroupDataModel(question_group, view)
        filter_model = RuleSortFilterProxyModel()
        filter_model.setSourceModel(model)
        view.setModel(filter_model)
        view.sortByColumn(0, Qt.AscendingOrder)
        self.question_group_tabs.append((question_group, filter_model, model))
        self.ui.tabWidget.addTab(tab, "")
        self._update_tabtitle(self.ui.tabWidget.indexOf(tab))

    def _question_group_editor(self, question_group: Union[QuestionGroup, None],
                               editor: QuestionGroupEditor) -> EditorResult:
        if editor.exec() == QDialog.Accepted:
            if question_group and question_group.id == editor.id:
                # ID was not changed -> update of title
                return EditorResult.Success
            if db.get_question_group(editor.id):
                QMessageBox(QMessageBox.Icon.Critical, "Fehler", "Fragengruppennummer existiert bereits!",
                            parent=self, ).exec()
                return EditorResult.Invalid
            return EditorResult.Success
        else:
            return EditorResult.Canceled

    def rename_question_group(self, index):
        if not self.question_group_tabs:
            return
        question_group, _, _ = self.question_group_tabs[index]
        editor = QuestionGroupEditor(id=question_group.id, name=question_group.name)
        result = self._question_group_editor(question_group, editor)
        while result == EditorResult.Invalid:
            result = self._question_group_editor(question_group, editor)
        if result == EditorResult.Success:
            question_group.id = editor.id
            question_group.name = editor.name
            self._update_tabtitle(index)
            db.commit()

    def add_question_group(self):
        editor = QuestionGroupEditor(id=db.get_new_question_group_id())
        result = self._question_group_editor(None, editor)
        while result == EditorResult.Invalid:
            result = self._question_group_editor(None, editor)
        if result == EditorResult.Success:
            if not self.question_group_tabs:
                self.ui.tabWidget.setTabsClosable(True)
                self.ui.add_filter.setDisabled(False)
                self.ui.tabWidget.clear()

            question_group = QuestionGroup(id=editor.id, name=editor.name)
            db.add_object(question_group)
            self.create_question_group_tab(question_group)

    def _update_tabtitle(self, index):
        question_group, _, _ = self.question_group_tabs[index]
        self.ui.tabWidget.setTabText(index, f"{question_group.id:02d} {question_group.name}")

    def add_filter(self, list_entry: Union[QListWidgetItem, bool] = False):
        if not list_entry or type(list_entry) == bool:
            # Add filter mode -> no list entry double_clicked
            current_configuration = None
            edit_mode = False
        else:
            # Edit mode -> Doubleclick on existing entry!
            index = self.ui.filter_list.indexFromItem(list_entry).row()
            current_configuration = RuleSortFilterProxyModel.filters[index][1]
            edit_mode = True
        first_ruletab = self.question_group_tabs[0][2]
        properties = {}
        for i in range(first_ruletab.columnCount()):
            properties.update(first_ruletab.headerData(i, Qt.Horizontal, Qt.UserRole))
        editor = FilterEditor(filter_configuration=properties, current_filter=current_configuration)
        editor.exec()
        if editor.result == QDialogButtonBox.ButtonRole.DestructiveRole:
            # Closed via Discard
            if not edit_mode:
                return
            else:
                self.__delete_filter(index)
        elif editor.result == QDialogButtonBox.ButtonRole.AcceptRole:
            # Closed via Save
            dict_key, filter_option, filter_value = editor.current_configuration()
            if not edit_mode:
                RuleSortFilterProxyModel.filters += [(editor.create_filter(), (dict_key, filter_option, filter_value))]
                self.ui.filter_list.addItem(
                    QListWidgetItem(f"{properties[dict_key].table_header} {filter_option} '{filter_value}'"))
            else:
                RuleSortFilterProxyModel.filters[index] = (
                    editor.create_filter(), (dict_key, filter_option, filter_value))
                list_entry.setText(f"{properties[dict_key].table_header} {filter_option} '{filter_value}'")
        elif editor.result == QDialogButtonBox.ButtonRole.RejectRole:
            # Closed via Cancel
            return
        elif editor.result is None:
            # Closed via X
            return
        else:
            raise ValueError(f"Invalid response {editor.result}")
        self.refresh_column_filter()

    def refresh_column_filter(self):
        for (_, filter_model, _) in self.question_group_tabs:
            filter_model = filter_model  # type: RuleSortFilterProxyModel
            filter_model.invalidateFilter()

    def create_ruletabs(self, question_groups: List[QuestionGroup]):
        self.ui.tabWidget.setTabsClosable(True)
        self.ui.add_filter.setDisabled(False)
        for question_group in question_groups:
            self.create_question_group_tab(question_group)

    def reset(self):
        for (_, _, model) in self.question_group_tabs:
            model.reset()


class FirstSetupWidget(QWidget, Ui_FirstSetupWidget):
    action_done = Signal()

    def __init__(self, main_window: MainWindow):
        super(FirstSetupWidget, self).__init__(main_window)
        self.ui = Ui_FirstSetupWidget()
        self.ui.setupUi(self)

        self.ui.create_button.clicked.connect(main_window.add_question_group)
        self.ui.import_button.clicked.connect(self.load_dataset)

    def load_dataset(self):
        main_application.load_dataset(self.parent())
        self.action_done.emit()


class SelfTestWidget(QWidget, Ui_SelfTestWidget):
    def __init__(self, main_window: MainWindow, dock_widget: SelfTestDockWidget):
        super(SelfTestWidget, self).__init__(main_window)
        self.ui = Ui_SelfTestWidget()
        self.ui.setupUi(self)

        self.main_window = main_window
        self.dock_widget = dock_widget
        self.ui.stackedWidget.setCurrentIndex(0)

        self._next_questions = []  # type: List[Question]
        self._previous_questions = []  # type: List[Question]
        self._current_question = None  # type: Union[Question, None]

        self.current_question = None  # type: Union[Question, None]

        self.next_questions = []
        self.dock_widget.changed.connect(self.selected_groups_changed)

        self.ui.next_button.pressed.connect(self.next_question)
        self.ui.previous_button.pressed.connect(self.previous_question)
        self.ui.switch_eval_button.pressed.connect(self.evaluate_question)
        self.ui.correct_button.pressed.connect(self.correct_answered)
        self.ui.incorrect_button.pressed.connect(self.incorrect_answered)

    @property
    def current_question(self):
        return self._current_question

    @current_question.setter
    def current_question(self, value):
        self._current_question = value
        if not value:
            self.ui.question_label_test.setText("Keine Frage verfügbar.")
        else:
            self.ui.question_label_test.setText(self._current_question.question)

    @property
    def previous_questions(self):
        return self._previous_questions

    @previous_questions.setter
    def previous_questions(self, value):
        self.ui.previous_button.setDisabled(not value)
        self._previous_questions = value

    @property
    def next_questions(self):
        return self._next_questions

    @next_questions.setter
    def next_questions(self, value):
        self._next_questions = value
        self.ui.switch_eval_button.setDisabled(not self.current_question)
        self.ui.user_answer_test.setDisabled(not self.current_question)

        self.ui.next_button.setDisabled(not self._next_questions)
        self.ui.user_answer_test.setText("")

    def next_question(self):
        if not self.next_questions:
            return
        if self.current_question:
            self.previous_questions += [self.current_question]
        self.current_question = self.next_questions[0]
        self.next_questions = self.next_questions[1:]

    def previous_question(self):
        if not self.previous_questions:
            return
        if self.current_question:
            self.next_questions = [self.current_question] + self.next_questions
        self.current_question = self.previous_questions[-1]
        self.previous_questions = self.previous_questions[:-1]

    def evaluate_question(self):
        self.ui.question_label_eval.setText(self.current_question.question)
        self.ui.correct_answer_eval.setText(self.current_question.answer_text)
        self.ui.user_answer_eval.setText(self.ui.user_answer_test.toPlainText())
        self.ui.stackedWidget.setCurrentIndex(1)

    def correct_answered(self):
        self.next_question()
        self.ui.stackedWidget.setCurrentIndex(0)

    def incorrect_answered(self):
        self.next_question()
        self.ui.stackedWidget.setCurrentIndex(0)

    def selected_groups_changed(self):
        questions = db.get_questions_by_foreignkey(self.dock_widget.get_question_groups())
        self.current_question = questions[0]
        self.next_questions = questions[1:]
        self.previous_questions = []
