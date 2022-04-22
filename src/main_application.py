import webbrowser
from enum import Enum, auto, IntEnum

from PIL import Image
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QFileDialog, QApplication, QMessageBox, QDialog
from bs4 import BeautifulSoup

from src import document_builder
from src.MainWidgets import FirstSetupWidget, QuestionOverviewWidget
from src.basic_config import app_version, check_for_update, display_name, is_bundled
from src.database import db
from src.datatypes import create_question_groups, create_questions_and_mchoice, Regeltest
from src.regeltestcreator import RegeltestSaveDialog, RegeltestSetup
from src.ui_mainwindow import Ui_MainWindow
from src.updater import UpdateChecker


class FilterMode(Enum):
    Include = auto()
    Exclude = auto()


class ApplicationMode(IntEnum):
    initial_setup = 0
    question_overview = 1
    self_test = 2
    regeltest_setup = 3


def load_dataset(parent: QWidget, reset_cursor=True) -> bool:
    def read_in(file_path: str):
        with open(file_path, 'r+', encoding='iso-8859-1') as file:
            soup = BeautifulSoup(file, "lxml")
        question_groups = create_question_groups(soup.find("gruppen"))
        questions, mchoice = create_questions_and_mchoice(soup("regelsatz"))
        return question_groups, questions, mchoice

    file_name = QFileDialog.getOpenFileName(parent, caption="Fragendatei öffnen", filter="DFB Regeldaten (*.xml)")
    if len(file_name) == 0 or file_name[0] == "":
        return False
    QApplication.setOverrideCursor(Qt.WaitCursor)
    datasets = read_in(file_name[0])
    db.clear_database()
    for dataset in datasets:
        db.fill_database(dataset)
    if reset_cursor:
        QApplication.restoreOverrideCursor()
    return True


def save_dataset(parent: QWidget):
    file_name = QFileDialog.getSaveFileName(parent, caption="Fragendatei speichern", filter="DFB Regeldaten (*.xml)")
    if len(file_name) == 0 or file_name[0] == "":
        return
    QApplication.setOverrideCursor(Qt.WaitCursor)
    dataset = "<?xml version=\"1.0\" encoding=\"iso-8859-1\" ?>\n\
<REGELTEST>\n<GRUPPEN>\n"
    for question_group in db.get_all_question_groups():
        dataset += question_group.export()
    dataset += "</GRUPPEN>\n"
    for question in db.get_question_multiplechoice():
        question_set = question[0].export()
        dataset += question_set[0]
        if question[1]:
            for mchoice in question[1]:
                dataset += mchoice.export()
        dataset += question_set[1]
    dataset += "</REGELTEST>"
    with open(file_name[0], "w+", encoding='iso-8859-1') as file:
        file.writelines(dataset)
    QApplication.restoreOverrideCursor()


def display_update_dialog(parent, releases):
    # new_version, description, url, download_url
    dialog = UpdateChecker(parent, releases, app_version.is_devrelease)
    dialog.exec()


def about_dialog():
    msg_box = QMessageBox()
    msg_box.setWindowTitle(f"Über {display_name}")
    msg_box.setText(f"<center><b>Regeltest-Creator</b></center>"
                    f"<center>v{app_version}</center><br>"
                    "<center>entwickelt von Jan Feil</center><br>"
                    "<a href=https://github.com/jfeil/RegeltestCreator>Weitere Informationen und Programmcode</a>")
    msg_box.exec()


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 1. Setup, 2. QuestionGroupList, 3. Self-Testing, 4. Regeltest-Setup
        self.first_setup = FirstSetupWidget(self)
        self.first_setup.action_done.connect(self.initialize)
        self.ui.stackedWidget.addWidget(self.first_setup)

        self.question_overview = QuestionOverviewWidget(self)
        self.ui.stackedWidget.addWidget(self.question_overview)

        # noinspection PyTypeChecker
        self.setWindowTitle(QCoreApplication.translate("MainWindow", f"{display_name} - {app_version}", None))
        self.ui.actionRegeldatensatz_einladen.triggered.connect(self.load_dataset)
        self.ui.actionAuf_Updates_pr_fen.triggered.connect(lambda: display_update_dialog(self, check_for_update()))
        self.ui.action_ber.triggered.connect(about_dialog)

        # self.ui.menuBearbeiten.setEnabled()
        self.ui.actionRegeltest_einrichten.setEnabled(False)
        # self.ui.actionNeue_Kategorie_erstellen.setEnabled(False)
        self.ui.actionRegeltest_l_schen.setEnabled(False)

        self.ui.regeltest_list.setAcceptDrops(True)
        self.ui.actionAnsicht_zur_cksetzen.triggered.connect(self.reset_ui)
        self.ui.actionRegeldatensatz_exportieren.triggered.connect(lambda: save_dataset(self))
        self.ui.actionNeue_Kategorie_erstellen.triggered.connect(self.add_question_group)

        self.ui.regeltest_list.model().rowsInserted.connect(self.regeltest_list_updated)
        self.ui.regeltest_list.model().rowsRemoved.connect(self.regeltest_list_updated)

        self.ui.add_questionlist.clicked.connect(self.setup_regeltest)
        self.ui.clear_questionlist.clicked.connect(self.clear_questionlist)

        self.ui.create_regeltest.clicked.connect(self.create_regeltest)

    def show(self) -> None:
        super(MainWindow, self).show()
        if not is_bundled:
            return
        releases = check_for_update()
        update_available = False
        if (app_version.is_devrelease and releases[1]) or (not app_version.is_devrelease and releases[0]):
            update_available = True
        if update_available:
            display_update_dialog(self, releases)

    def initialize(self):
        dataset = db.get_all_question_groups()
        if dataset:
            for question_group in dataset:
                self.question_overview.create_question_group_tab(question_group)
            self.set_mode(ApplicationMode.question_overview, reset=True)
        else:
            self.set_mode(ApplicationMode.initial_setup, reset=True)

    def load_dataset(self):
        load_dataset(self, reset_cursor=False)
        self.question_overview.reset()
        QApplication.restoreOverrideCursor()

    def add_question_group(self):
        self.question_overview.add_question_group()
        self.set_mode(ApplicationMode.question_overview)

    def reset_ui(self):
        self.set_mode(ApplicationMode(self.ui.stackedWidget.currentIndex()), reset=True)

    def set_mode(self, mode: ApplicationMode, reset=False):
        if self.ui.stackedWidget.currentIndex() == int(mode) and not reset:
            return

        self.ui.stackedWidget.setCurrentIndex(int(mode))

        if mode == ApplicationMode.initial_setup:
            self.ui.actionAnsicht_zur_cksetzen.setDisabled(True)
        else:
            self.ui.actionAnsicht_zur_cksetzen.setDisabled(False)

        if mode == ApplicationMode.question_overview:
            self.ui.regeltest_creator.show()
        else:
            self.ui.regeltest_creator.close()

    def clear_questionlist(self):
        self.ui.regeltest_list.clear()
        self.ui.regeltest_list.questions.clear()
        self.regeltest_list_updated()

    def regeltest_list_updated(self):
        self.ui.regeltest_stats.setText(
            f"{self.ui.regeltest_list.count()} Fragen selektiert ({self.ui.regeltest_list.count() * 2} Punkte)")

    def setup_regeltest(self):
        regeltest_setup = RegeltestSetup(self)
        if regeltest_setup.exec():
            for question in regeltest_setup.collect_questions():
                self.ui.regeltest_list.add_question(question)

    def create_regeltest(self):
        questions = []
        for signature in self.ui.regeltest_list.questions:
            questions += [db.get_question(signature)]
        settings = RegeltestSaveDialog(self)
        settings.ui.title_edit.setFocus()
        result = settings.exec()
        output_path = settings.ui.output_edit.text()
        if result == QDialog.Accepted:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if settings.ui.icon_path_edit.text():
                icon = Image.open(settings.ui.icon_path_edit.text())
            else:
                icon = None
            db.add_object(Regeltest(title=settings.ui.title_edit.text(), description="", icon=icon.tobytes(),
                                    questions=questions))
            document_builder.create_document(questions, output_path, settings.ui.title_edit.text(),
                                             icon=icon)
            QApplication.restoreOverrideCursor()
            webbrowser.open_new(output_path)
