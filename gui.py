import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from mendeley import client_library
from mendeley.api import API
import reference_resolver as rr
from pypub.utils import get_truncated_display_string as td

from mendeley_errors import *
from pypub_errors import *
from reference_resolver_errors import *


class Window(QWidget):
    """
    This is the main window of the application.

    --- Overview of Usage ---
    User inputs a DOI. The indicator button to the left of the text box will
    turn green if the DOI within the text field is in the user's library.
    From there, the user can get the references for the paper, which will appear
    in a large box below the buttons, or the user can open up the notes editor,
    which appears in a smaller, new window. The notes can be edited and saved.

    --- References List Features ---
     * Click once on a reference to expand it downward and view more information,
        including the full title, the journal it appears in, and its DOI.
     * Click twice on a reference to open up the notes editor for that reference
        (though the reference must first be in the user's library). If the reference
        is not already in the user's library, a pop-up window asks if they would
        like to add it.
     * Reference entry is highlighted in green if it exists in the user's library,
        red if the reference is not in the library, or grey if there is no DOI listed.
     * Right-click menu options:
        - Add to library
           The reference information and file is retrieved using a web scraper and
            added to the user's Mendeley library.
           Requires that the user has the appropriate permissions to access the file
            through the publisher, and that there is a web scraper in place for that
            specific publisher.
        - Look up references
           The DOI of the reference is searched for, and its references listed.
           Requires that the reference has a DOI.
        - Move to trash
           Moves the document and file from the user's Mendeley library to the trash.
           Requires that the document be in the user's library.


    TODOs:
     - Implement URL input capability, not just DOI
     - Possibly make the window tabbed with expanded functionality?
     - Fix the appearance of "in library" indicator next to text box
     - Implement reading the abstract of any paper

    """
    def __init__(self):
        super().__init__()
        #loading = LoadingPopUp()
        self.library = self.instantiate_library()
        self.api = API()
        #loading.close_window()
        self.initUI()
        self.data = Data()

    def initUI(self):

        # Make all widgets
        self.entryLabel = QLabel('Please enter a DOI or URL')
        self.indicator = QPushButton()
        self.textEntry = QLineEdit()
        self.doi_check = QRadioButton('DOI')
        self.doi_check.setChecked(True)
        self.url_check = QRadioButton('URL')
        self.get_references = QPushButton('Get References')
        self.open_notes = QPushButton('Open Notes')
        self.stacked_responses = QStackedWidget()
        self.ref_area = QScrollArea()

        # Set connections to functions
        self.textEntry.textChanged.connect(self.update_indicator)
        self.textEntry.returnPressed.connect(self.get_refs)
        self.get_references.clicked.connect(self.get_refs)
        self.open_notes.clicked.connect(self.show_main_notes_box)

        # Format indicator button
        #self.indicator.setFlat(True)
        self.indicator.setStyleSheet("background-color: rgba(0,0,0,0.25);")
        self.indicator.setAutoFillBackground(True)
        self.indicator.setFixedSize(20,20)
        self.indicator.setToolTip("Green if DOI found in library")
        self.setStyleSheet("""QToolTip {
                                    background-color: white;
                                    color: black;
                                    border: black solid 1px;
                                    }""")

        # Make scroll items widget
        self.ref_items = QWidget()
        items_layout = QVBoxLayout()
        items_layout.addStretch(1)
        self.ref_items.setLayout(items_layout)
        self.ref_items_layout = self.ref_items.layout()

        # Format scrollable reference area
        self.ref_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ref_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ref_area.setWidgetResizable(True)
        ref_layout = QVBoxLayout()
        self.ref_area.setLayout(ref_layout)
        self.ref_area_layout = self.ref_area.layout()
        self.ref_area.setWidget(self.ref_items)
        self.ref_area.hide()

        # Create a horizontal box to be added to vbox later
        # The radiobuttons having the same parent widget ensures
        # that they are part of a group and only one can be checked.
        checkboxes = QHBoxLayout()
        checkboxes.addWidget(self.doi_check)
        checkboxes.addWidget(self.url_check)
        checkboxes.addWidget(self.get_references)
        checkboxes.addWidget(self.open_notes)
        checkboxes.addStretch(1)

        # Create a horizontal box for indicator and textEntry
        textline = QHBoxLayout()
        textline.addWidget(self.indicator)
        textline.addWidget(self.textEntry)

        # Create a vertical box layout.
        # Populate with widgets and add stretch space at the bottom.
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.entryLabel)
        self.vbox.addLayout(textline)
        self.vbox.addLayout(checkboxes)
        self.vbox.addWidget(self.stacked_responses)
        self.vbox.addWidget(self.ref_area)
        self.vbox.addStretch(1)

        # Set layout to be the vertical box.
        self.setLayout(self.vbox)

        self.resize(500,600)
        _center(self)
        self.setWindowTitle('ScholarTools')
        self.show()

    # ++++++++++++++++++++++++++++++++++++++++++++
    # ============================================ All Functions
    # ++++++++++++++++++++++++++++++++++++++++++++
    def instantiate_library(self):
        return client_library.UserLibrary()

    def update_indicator(self):
        in_library = self.check_lib()
        if in_library:
            self.data.doc_response_json = self.library.get_document(self._get_doi(), return_json=True)
            self.indicator.setStyleSheet("background-color: rgba(0, 255, 0, 0.25);")
        else:
            self.data.doc_response_json = None
            self.indicator.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

    def check_lib(self):
        entered_doi = self._get_doi()
        self.populate_response_widget()

        if entered_doi == '':
            return False
        in_library = self.library.check_for_document(entered_doi)
        return in_library

    def _get_doi(self):
        """
        Right now, the URL option is not supported. To do this I'll
        need to implement link_to_doi and resolve_link in reference_resolver.
        """
        text = self.textEntry.text()

        if self.doi_check.isChecked():
            return text
        else:
            return text

    def populate_response_widget(self):
        if self.stacked_responses.count() < 3:
            self.stacked_responses.addWidget(QLabel('Please enter text above.'))
            self.stacked_responses.addWidget(QLabel('Found in library!'))
            self.stacked_responses.addWidget(QLabel('Not found in library.'))
            self.stacked_responses.hide()

    def get_refs(self):
        # Hide message from check_lib
        self.stacked_responses.hide()

        # Get DOI from text field and handle blank entry
        entered_doi = self._get_doi()
        self.populate_response_widget()

        if entered_doi == '':
            self.stacked_responses.setCurrentIndex(0)
            self.stacked_responses.show()
            return

        # Resolve DOI and get references
        try:
            paper_info = rr.resolve_doi(entered_doi)
            refs = paper_info.references
            self.populate_data(paper_info)
        except UnsupportedPublisherError:
            QMessageBox.warning(self, 'Warning', 'Unsupported Publisher')
            return

        # First clean up existing GUI window.
        # If there are widgets in the layout (i.e. from the last call to 'get_refs'),
        # delete all of those reference labels before adding more.
        _delete_all_widgets(self.ref_items_layout)

        for ref in refs:
            ref_label = self.ref_to_label(ref)
            self.ref_items_layout.insertWidget(self.ref_area_layout.count() - 1, ref_label)

        self.ref_area.show()

    def ref_to_label(self, ref):
        # Extract main display info
        ref_id = ref.get('ref_id')
        ref_title = ref.get('title')
        ref_author_list = ref.get('authors')
        ref_doi = ref.get('doi')
        ref_year = ref.get('year')
        if ref_year is None:
            ref_year = ref.get('date')

        # Format short and long author lists
        if ref_author_list is not None:
            ref_full_authors = '; '.join(ref_author_list)
            if len(ref_author_list) > 2:
                ref_first_authors = ref_author_list[0] + ', ' + ref_author_list[1] + ', et al.'
            else:
                ref_first_authors = ref_full_authors

        in_lib = 2

        # Build up string with existing info
        ref_small_text = ''
        ref_expanded_text = ''
        if ref_id is not None:
            ref_small_text = ref_small_text + str(ref_id)
            ref_expanded_text = ref_expanded_text + str(ref_id)
        if ref_author_list is not None:
            ref_small_text = ref_small_text + '. ' + ref_first_authors
            ref_expanded_text = ref_expanded_text + '. ' + ref_full_authors
        if ref.get('publication') is not None:
            ref_expanded_text = ref_expanded_text + '\n' + ref.get('publication')
        if ref_year is not None:
            ref_small_text = ref_small_text + ', ' + ref_year
            ref_expanded_text = ref_expanded_text + ', ' + ref_year
        if ref_title is not None:
            ref_small_text = ref_small_text + ', ' + ref_title
            ref_expanded_text = ref_expanded_text + '\n' + ref_title
        if ref_doi is not None:
            ref_expanded_text = ref_expanded_text + '\n' + ref_doi
            in_library = self.library.check_for_document(ref_doi)
            if in_library:
                in_lib = 1
            else:
                in_lib = 0

        ref_small_text = td(ref_small_text, 66)

        # Make label
        ref_label = ReferenceLabel(ref_small_text, self)
        ref_label.small_text = ref_small_text
        ref_label.expanded_text = ref_expanded_text
        ref_label.reference = ref
        ref_label.doi = ref.get('doi')

        # Connect click action to expanding the label
        ref_label.ClickFilter.clicked.connect(self.change_ref_label)
        ref_label.ClickFilter.doubleclicked.connect(self.show_ref_notes_box)

        # Save all labels in Data()
        self.data.small_ref_labels.append(ref_small_text)
        self.data.expanded_ref_labels.append(ref_expanded_text)

        # Make widget background color green if document is in library.
        # Red if not in library.
        # Neutral if there is no DOI
        if in_lib == 1:
            ref_label.setStyleSheet("background-color: rgba(0,255,0,0.25);")
        elif in_lib == 0:
            ref_label.setStyleSheet("background-color: rgba(255,0,0,0.25);")

        return ref_label

    def change_ref_label(self):
        clicked_label = self.sender().parent

        label_text = clicked_label.text()
        if label_text == clicked_label.small_text:
            clicked_label.setText(clicked_label.expanded_text)
        else:
            clicked_label.setText(clicked_label.small_text)

    def populate_data(self, info):
        self.data.entry = info.entry
        self.data.references = info.references
        self.data.doi = info.doi
        self.data.scraper_obj = info.scraper_obj
        self.data.idnum = info.idnum
        self.data.pdf_link = info.pdf_link
        self.data.url = info.url
        self.data.small_ref_labels = []
        self.data.expanded_ref_labels = []

    # ++++++++++++++++++++++++++++++++++++++++++++
    # ============================================ Reference Label Right-Click Functions
    # ++++++++++++++++++++++++++++++++++++++++++++
    def add_to_library(self, label, doi):
        if doi is None:
            QMessageBox.warning(self, 'Warning', 'No DOI found for this reference')
            return

        try:
            self.library.add_to_library(doi)
        except UnsupportedPublisherError:
            QMessageBox.warning(self, 'Warning', 'Publisher is not yet supported.\n'
                                                 'Document not added.')
            return
        self._update_document_status(doi, label, adding=True)

    def lookup_ref(self, doi):
        if doi is None:
            QMessageBox.warning(self, 'Warning', 'No DOI found for this reference')
            return
        self.textEntry.setText(doi)
        self.get_refs()

    def move_doc_to_trash(self, label):
        doi = label.doi
        doc_json = self.library.get_document(doi, return_json=True)
        if doc_json is None:
            QMessageBox.information(self, 'Information', 'Document is not in your library.')
            return
        doc_id = doc_json.get('id')
        self.api.documents.move_to_trash(doc_id)
        self._update_document_status(doi, label)

    def _update_document_status(self, doi, label, adding=False):
        self.library.sync()
        exists = self.library.check_for_document(doi)
        if exists:
            label.setStyleSheet("background-color: rgba(0,255,0,0.25);")
        else:
            label.setStyleSheet("background-color: rgba(255,0,0,0.25);")
            if adding:
                QMessageBox.warning(self, 'Warning', 'An error occurred during sync.\n'
                                    'Document may not have been added.')

    # ++++++++++++++++++++++++++++++++++++++++++++
    # ============================================ Notes Box Display Functions
    # ++++++++++++++++++++++++++++++++++++++++++++
    def show_ref_notes_box(self):
        label = self.sender().parent
        try:
            doc_response_json = self.library.get_document(label.doi, return_json=True)
        except DOINotFoundError:
            reply = QMessageBox.question(self,'Message', 'Document not found in library.\nWould you like to add it?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.add_to_library(label, label.doi, self.library)
                return
            else:
                return
        notes = doc_response_json.get('notes')
        self.nw = NotesWindow(parent=self, notes=notes, doc_json=doc_response_json)
        self.nw.show()

    def show_main_notes_box(self):
        notes = self.data.doc_response_json.get('notes')
        self.nw = NotesWindow(parent=self, notes=notes, doc_json=self.data.doc_response_json)
        self.nw.show()


class NotesWindow(QWidget):
    """
    This is the smaller window that appears displaying notes for a given reference.

    --- Features ---
    * Text box: Displays the current notes saved for a given document, and allows
       for editing.
    * Save button: Saves the changes made to the notes, and syncs with Mendeley.
    * Save and Close button: Saves the changes made to the notes, syncs, with
       Mendeley, and closes the notes window.
    * Prompting before exit: If the user attempts to close the window after
       making unsaved changes to the notes, a pop-up window appears asking
       to confirm the action without saving. Provides an option to save.

    TODOs:
     - Fix the prompt before exit (currently appears when closing the main
        window, even after the notes window is gone. Maybe this has to do
        with having closed the window but not terminating the widget process?)
     - Add informative window title to keep track of which paper is being
        commented on.
     - Add (automatic or voluntary) feature to input a little note saying something
        like "edited with reference to [original file that references this one]"

    """
    def __init__(self, parent=None, notes=None, doc_json=None):
        super(NotesWindow, self).__init__()
        self.parent = parent
        self.notes = notes
        self.doi = doc_json.get('doi')
        self.doc_id = doc_json.get('id')

        # TODO: Make an appropriate window title that says what article we're looking at the refs of.
        # This might require fixing api.documents.get() so it returns more things
        print(doc_json)
        print(doc_json.keys())
        print(doc_json.values())
        doc_title = doc_json.get('title')

        self.initUI()

    def initUI(self):
        self.saved = True

        # Make widgets
        self.notes_title = QLabel('Notes:')
        self.notes_box = QTextEdit()
        self.save_button = QPushButton('Save')
        self.save_and_close_button = QPushButton('Save and Close')
        self.saved_indicator = QLabel('Saved!')
        self.saved_indicator.hide()

        # Connect widgets
        self.save_button.clicked.connect(self.save)
        self.save_and_close_button.clicked.connect(self.save_and_close)
        self.notes_box.textChanged.connect(self.updated_text)

        if self.notes is not None:
            self.notes_box.setText(self.notes)

        hbox = QHBoxLayout()
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.save_and_close_button)

        # Make layout and add widgets
        vbox = QVBoxLayout()
        vbox.addWidget(self.notes_title)
        vbox.addWidget(self.notes_box)
        vbox.addWidget(self.saved_indicator)
        vbox.addStretch(1)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.show()

    def save(self):
        updated_notes = self.notes_box.getText()
        notes_dict = {"notes" : updated_notes}
        self.parent.api.documents.update(self.doc_id, notes_dict)
        self.parent.library.sync()
        self.saved = True

    def save_and_close(self):
        self.save()
        self.close()

    def updated_text(self):
        self.saved = False

    def closeEvent(self, QCloseEvent):
        if self.saved:
            QCloseEvent.accept()
            return
        else:
            reply = QMessageBox.question(self, 'Message', 'Notes have not been saved.\n'
                      'Are you sure you want to close notes?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


class ReferenceLabel(QLabel):
    """
    Custom extension of QLabel to allow several types of clicking functionality.
    """

    def __init__(self, text, parent):
        super().__init__()

        self.parent = parent

        self.metrics = QFontMetrics(self.font())
        elided = self.metrics.elidedText(text, Qt.ElideRight, self.width())

        self.setText(text)
        self.expanded_text = None
        self.small_text = None
        self.reference = None
        self.doi = None

        self.ClickFilter = ClickFilter(self)
        self.installEventFilter(self.ClickFilter)

        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setWordWrap(True)

    def contextMenuEvent(self, QContextMenuEvent):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: white;")
        add_to_lib = menu.addAction("Add to library")
        ref_lookup = menu.addAction("Look up references")
        move_to_trash = menu.addAction("Move to trash")
        action = menu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))
        if action == add_to_lib:
            self.parent.add_to_library(self, self.reference.get('doi'))
        elif action == ref_lookup:
            self.parent.lookup_ref(self.reference.get('doi'))
        elif action == move_to_trash:
            self.parent.move_doc_to_trash(self)


# This is meant to be a popup that appears when the GUI is launched
# to indicate that the library is being loaded. Not sure if this is
# necessary because the loading seems to happen quickly.
class LoadingPopUp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        message = QLabel('Loading Library...', self)
        message.move(50, 150)
        _center(self)
        self.show()

    def close_window(self):
        qApp.quit()


class Data(object):
    def __init__(self):
        self.references = None
        self.entry = None
        self.doi = None
        self.idnum = None
        self.scraper_obj = None
        self.url = None
        self.pdf_link = None
        self.doc_response_json = None
        self.small_ref_labels = []
        self.expanded_ref_labels = []


# Centering the widget
# frameGeometry gets the size of the widget I'm making.
# QDesktopWidget finds the size of the screen
# The self.move moves my widget's top left corner to the coords of the
# top left corner of the centered qr frame.
def _center(widget):
    qr = widget.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())

'''
def _clickable(widget):
    class Filter(QObject):
        clicked = pyqtSignal()
        doubleclicked = pyqtSignal()

        label = widget

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonPress:
                    # Start timer to determine if the mouse is being held
                    # down and the user is highlighting.
                    widget.click_timer.timeout.connect(self.set_highlighting)
                    widget.click_timer.start(250)
                # If the user is clicking without highlighting, send
                # the 'clicked' signal.
                if event.type() == QEvent.MouseButtonRelease:
                    widget.click_timer.stop()
                    if not widget.highlighting:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            # The developer can opt for .emit(obj) to get the object within the slot.
                            return True
                    widget.highlighting = False
            return False

        def set_highlighting(self):
            widget.highlighting = True

        def single_click(self):
            self.clicked.emit()

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked
'''


class ClickFilter(QObject):
    """
    This is the eventFilter for ReferenceLabel. It handles the click
    events and emits either 'clicked' (for a single click) or 'doubleclicked'
    (for a double click) signals that can be assigned to functions.
    """
    clicked = pyqtSignal()
    doubleclicked = pyqtSignal()

    def __init__(self, widget):
        super(ClickFilter, self).__init__()
        self.parent = widget
        self.highlighting = False

        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.set_highlighting)

        self.doubleclick_timer = QTimer()
        self.doubleclick_timer.setSingleShot(True)
        self.doubleclick_timer.timeout.connect(self.single_click)

    def eventFilter(self, widget, event):
        if event.type() == QEvent.MouseButtonPress:
            # Start timer to determine if the mouse is being held
            # down and the user is highlighting.
            self.click_timer.start(200)
        # If the user is clicking without highlighting, send
        # the 'clicked' signal.
        if event.type() == QEvent.MouseButtonRelease:
            self.click_timer.stop()
            if not self.highlighting:
                if self.doubleclick_timer.isActive():
                    if widget.rect().contains(event.pos()):
                        self.doubleclicked.emit()
                        self.doubleclick_timer.stop()
                        return True
                else:
                    self.doubleclick_timer.start(200)
            self.highlighting = False
        return False

    def set_highlighting(self):
        self.highlighting = True

    def single_click(self):
        self.clicked.emit()


def _layout_widgets(layout):
    """
    Returns a list of all of the widget items in a given layout.
    Ignores spacer items.
    """
    all_widgets = []
    for i in range(layout.count()):
        item = layout.itemAt(i).widget()
        if type(item) is not QSpacerItem:
            all_widgets.append(item)
    return all_widgets


def _delete_all_widgets(layout):
    if type(layout.itemAt(0)) == QSpacerItem:
        startIndex = 1
    else:
        startIndex = 0
    while layout.count() > 1:
        item = layout.itemAt(startIndex).widget()
        layout.removeWidget(item)
        item.deleteLater()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = Window()
    #nw = NotesWindow()
    #l = LoadingPopUp()

    sys.exit(app.exec_())