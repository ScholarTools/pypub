import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from mendeley import client_library
import reference_resolver as rr
from pypub.utils import get_truncated_display_string as td

from mendeley_errors import *
from pypub_errors import *
from reference_resolver_errors import *


class Window(QWidget):
    def __init__(self):
        super().__init__()
        #loading = LoadingPopUp()
        self.library = self.instantiate_library()
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
        self.check_in_library = QPushButton('Check in Library')
        self.get_references = QPushButton('Get References')
        self.stacked_responses = QStackedWidget()
        self.ref_area = QScrollArea()

        # Set connections to functions
        self.textEntry.returnPressed.connect(self.get_refs)
        self.check_in_library.clicked.connect(self.check_lib)
        self.get_references.clicked.connect(self.get_refs)

        # Make scroll items widget
        self.ref_items = QWidget()
        items_layout = QVBoxLayout()
        items_layout.addStretch(1)
        #items_layout.addWidget(QLabel('hello, world'))
        self.ref_items.setLayout(items_layout)
        self.ref_items_layout = self.ref_items.layout()

        # Format scrollable reference area
        self.ref_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ref_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ref_area.setWidgetResizable(True)
        ref_layout = QVBoxLayout()
        self.ref_area.setLayout(ref_layout)
        self.ref_area_layout = self.ref_area.layout()
        #self.ref_area.setFixedHeight(340)
        self.ref_area.setWidget(self.ref_items)
        self.ref_area.hide()

        # Create a horizontal box to be added to vbox later
        # The radiobuttons having the same parent widget ensures
        # that they are part of a group and only one can be checked.
        checkboxes = QHBoxLayout()
        checkboxes.addWidget(self.doi_check)
        checkboxes.addWidget(self.url_check)
        checkboxes.addWidget(self.check_in_library)
        checkboxes.addWidget(self.get_references)
        checkboxes.addStretch(1)

        action_buttons = QHBoxLayout()
        action_buttons.addWidget(self.check_in_library)
        action_buttons.addWidget(self.get_references)
        action_buttons.addStretch(1)

        # Create a horizontal box for indicator and textEntry
        textline = QHBoxLayout()
        self.indicator.setFlat(True)
        self.indicator.setStyleSheet("background-color: rgba(0,255,0,0.25);")
        self.indicator.setAutoFillBackground(True)
        self.indicator.setFixedSize(20,20)
        #textline.addStretch(1)
        textline.addWidget(self.indicator)
        textline.addWidget(self.textEntry)



        # Create a vertical box layout.
        # Populate with widgets and add stretch space at the bottom.
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.entryLabel)
        #self.vbox.addWidget(self.textEntry)
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

    # Make sure only one box (DOI or URL) is checked
    # NO LONGER NEEDED BECAUSE RADIO BUTTONS EXIST
    def checkbox_manage(self, state):
        sender = self.sender()
        # State == 2 means the box is checked
        # State == 0 means the box is unchecked
        if state == 2:
            if sender.text() == 'DOI':
                self.url_check.setCheckState(0)
            else:
                self.doi_check.setCheckState(0)


    # Functions
    # ---------------------------
    def instantiate_library(self):
        return client_library.UserLibrary()

    def check_lib(self):
        entered_doi = self.get_doi()
        self.populate_response_widget()

        if entered_doi == '':
            self.stacked_responses.setCurrentIndex(0)
            self.stacked_responses.show()
            return
        in_library = self.library.check_for_document(entered_doi)
        if in_library:
            self.stacked_responses.setCurrentIndex(1)
            self.stacked_responses.show()
            return
        else:
            self.stacked_responses.setCurrentIndex(2)
            self.stacked_responses.show()
            return

    def get_doi(self):
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

    def get_refs(self):
        # Hide message from check_lib
        self.stacked_responses.hide()

        # Get DOI from text field and handle blank entry
        entered_doi = self.get_doi()
        self.populate_response_widget()

        if entered_doi == '':
            self.stacked_responses.setCurrentIndex(0)
            self.stacked_responses.show()
            return

        # Resolve DOI and get references
        try:
            refs = rr.resolve_doi(entered_doi).references
            self.data.references = refs
        except UnsupportedPublisherError:
            QMessageBox.warning(self, 'Warning', 'Unsupported Publisher')
            return

        if entered_doi != '10.1002/biot.201400046':
            import pdb
            #pdb.set_trace()

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
        ref_label = ReferenceLabel(ref_small_text)
        ref_label.small_text = ref_small_text
        ref_label.expanded_text = ref_expanded_text
        ref_label.reference = ref
        ref_label.library = self.library

        # Connect click action to expanding the label
        ref_label.ClickFilter.clicked.connect(self.change_ref_label)
        ref_label.ClickFilter.doubleclicked.connect(self.show_notes_box)

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

    def change_color(self):
        clicked_label = self.sender().parent
        clicked_label.setStyleSheet("background-color: rgba(0,0,255,0.25);")


    # TODO: Incorporate fetching, editing, and re-saving notes. Sync these with Mendeley
    def show_notes_box(self):
        self.nw = NotesWindow()
        self.nw.show()


class NotesWindow(QWidget):
    def __init__(self, parent=None):
        super(NotesWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # Make widgets
        self.notes_title = QLabel('Notes:')
        self.notes_box = QTextEdit()

        # Make layout and add widgets
        vbox = QVBoxLayout()
        vbox.addWidget(self.notes_title)
        vbox.addWidget(self.notes_box)

        self.setLayout(vbox)

        self.show()


class ReferenceLabel(QLabel):

    def __init__(self, text):
        super().__init__()

        self.metrics = QFontMetrics(self.font())
        elided = self.metrics.elidedText(text, Qt.ElideRight, self.width())

        self.setText(text)
        self.expanded_text = None
        self.small_text = None
        self.reference = None
        self.library = None

        self.ClickFilter = ClickFilter(self)
        self.installEventFilter(self.ClickFilter)

        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #self.setWordWrap(True)

    '''
    def resizeEvent(self, QResizeEvent):
        elided = self.metrics.elidedText(self.text, Qt.ElideRight, self.width())
        self.setText(elided)
    '''

    def contextMenuEvent(self, QContextMenuEvent):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: white;")
        addAction = menu.addAction("Add to library")
        action = menu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))
        if action == addAction:
            _add_to_library(self, self.reference.get('doi'), self.library)



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
        self.small_ref_labels = []
        self.expanded_ref_labels = []


# TODO: Change this so it makes a message window instead of crashing
def _add_to_library(label, doi, library):
    if doi is None:
        raise KeyError('No DOI for this reference.')

    library.add_to_library(doi)
    library.sync()
    added = library.check_for_document(doi)
    if added:
        label.setStyleSheet("background-color: rgba(0,255,0,0.25);")
    else:
        new_text = label.expanded_text + '\n' + 'Could not be added to library.'
        label.setText(new_text)


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