import os
from PySide import QtGui, QtCore
from ..i18n import translate
from .util import load_ui
from .shapewidget import ShapeWidget
from .toolproperties import ToolProperties, ToolAttributes
from .feedsandspeeds import FeedsAndSpeedsWidget

__dir__ = os.path.dirname(__file__)
ui_path = os.path.join(__dir__, "tooleditor.ui")

class ToolEditor(QtGui.QWidget):
    def __init__(self, db, serializer, tool, tool_no=None, parent=None):
        super(ToolEditor, self).__init__(parent)
        self.form = load_ui(ui_path)
        self.form.buttonBox.clicked.connect(self.form.close)

        self.db = db
        self.serializer = serializer
        self.tool = tool
        self.tool_no = tool_no
        self.default_title = self.form.windowTitle()

        nameWidget = QtGui.QLineEdit(tool.get_label())
        label = translate('btl', 'Tool name')
        nameWidget.setPlaceholderText(label)
        self.form.vBox.insertWidget(0, nameWidget)
        nameWidget.setFocus()
        nameWidget.textChanged.connect(tool.set_label)
        nameWidget.textChanged.connect(self._update)
        self._update()

        tool_tab_layout = self.form.toolTabLayout
        widget = ShapeWidget(tool.shape)
        tool_tab_layout.addWidget(widget)
        props = ToolProperties(tool, tool_no, parent=self.form)
        props.toolNoChanged.connect(self._on_tool_no_changed)
        tool_tab_layout.addWidget(props)

        if tool.supports_feeds_and_speeds():
            label = translate('btl', 'Feeds && Speeds')
            self.feeds = FeedsAndSpeedsWidget(db, serializer, tool, parent=self)
            self.feeds_tab_idx = self.form.tabWidget.insertTab(1, self.feeds, label)
        else:
            self.feeds = None
            self.feeds_tab_idx = None

        label = translate('btl', 'Attributes')
        attrs = ToolAttributes(tool, parent=self.form)
        attr_tab = self.form.tabWidget.addTab(attrs, label)

        self.form.tabWidget.setCurrentIndex(0)
        self.form.tabWidget.currentChanged.connect(self._on_tab_switched)
        self.form.lineEditCoating.setText(tool.get_coating())
        self.form.lineEditCoating.textChanged.connect(tool.set_coating)
        self.form.lineEditHardness.setText(tool.get_hardness())
        self.form.lineEditHardness.textChanged.connect(tool.set_hardness)
        self.form.lineEditMaterials.setText(tool.get_materials())
        self.form.lineEditMaterials.textChanged.connect(tool.set_materials)
        self.form.lineEditSupplier.setText(tool.get_supplier())
        self.form.lineEditSupplier.textChanged.connect(tool.set_supplier)

        self.form.plainTextEditNotes.setPlainText(tool.get_notes())
        self.form.plainTextEditNotes.textChanged.connect(self._on_notes_changed)

    def _update(self):
        title = self.default_title
        tool_name = self.tool.get_label()
        if tool_name:
            title = '{} - {}'.format(tool_name, title)
        self.form.setWindowTitle(title)

    def _on_tab_switched(self, index):
        if index == self.feeds_tab_idx:
            self.feeds.update()

    def _on_notes_changed(self):
        self.tool.set_notes(self.form.plainTextEditNotes.toPlainText())

    def _on_tool_no_changed(self, value):
        self.tool_no = value

    def show(self):
        return self.form.exec_()
