from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QLabel, QVBoxLayout, QLineEdit, QCheckBox,
                             QGroupBox, QPushButton, QGridLayout,
                             QTextEdit, QListWidget, QHBoxLayout,
                             QDialog, QFileDialog, QTreeWidget,
                             QTreeWidgetItem)
from rpg.gui.dialogs import DialogChangelog, DialogSubpackage, DialogImport
from pathlib import Path
from rpg.command import Command
import subprocess


class Wizard(QtWidgets.QWizard):
    ''' Main class that holds other pages, number of pages are in NUM_PAGES
        - to simply navigate between them
        - counted from 0 (PageGreetings) to 10 (PageFinal)
        - tooltips are from: https://fedoraproject.org/wiki/How_to_create_an_RPM_package '''

    NUM_PAGES = 10
    (PageGreetings, PageImport, PageScripts, PagePatches, PageRequires,
        PageScriplets, PageSubpackages, PageBuild, PageCopr,
        PageFinal) = range(NUM_PAGES)

    def __init__(self, base, parent=None):
        super(Wizard, self).__init__(parent)

        self.base = base
        self.setWindowTitle(self.tr("RPG"))
        self.setWizardStyle(self.ClassicStyle)

        # Setting pages to wizard
        self.setPage(self.PageImport, ImportPage(self))
        self.setPage(self.PageScripts, ScriptsPage(self))
        self.setPage(self.PagePatches, PatchesPage(self))
        self.setPage(self.PageRequires, RequiresPage(self))
        self.setPage(self.PageScriplets, ScripletsPage(self))
        self.setPage(self.PageSubpackages, SubpackagesPage(self))
        self.setPage(self.PageBuild, BuildPage(self))
        self.setPage(self.PageCopr, CoprPage(self))
        self.setPage(self.PageFinal, FinalPage(self))
        self.setStartId(self.PageImport)


class ImportPage(QtWidgets.QWizardPage):
    def __init__(self, Wizard, parent=None):
        super(ImportPage, self).__init__(parent)

        self.base = Wizard.base

        self.setTitle(self.tr("Beginning"))
        self.setSubTitle(self.tr("Fill in fields and import " +
                                 "tarball or folder with source code"))
        ''' Creating widgets and setting them to layout'''
        self.nameLabel = QLabel("Name<font color=\'red\'>*</font>")
        self.nameEdit = QLineEdit()
        self.nameEdit.setMinimumHeight(30)
        self.nameLabel.setBuddy(self.nameEdit)
        self.nameLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.nameLabel.setToolTip("The (base) name of the package, which should match the SPEC file name")

        self.versionLabel = QLabel("Version<font color=\'red\'>*</font>")
        self.versionEdit = QLineEdit()
        self.versionEdit.setMinimumHeight(30)
        self.versionLabel.setBuddy(self.versionEdit)
        self.versionLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.versionLabel.setToolTip("The upstream version number, usually numbers separated by dots (e.g. 1.7.4)")

        self.releaseLabel = QLabel("Release<font color=\'red\'>*</font>")
        self.releaseEdit = QLineEdit()
        self.releaseEdit.setMinimumHeight(30)
        self.releaseLabel.setBuddy(self.releaseEdit)
        self.releaseLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.releaseLabel.setToolTip("The initial value should normally be 1%{?dist}. Increment the number every time you release a new package")

        self.licenseLabel = QLabel("License<font color=\'red\'>*</font>")
        self.licenseEdit = QLineEdit()
        self.licenseEdit.setMinimumHeight(30)
        self.licenseLabel.setBuddy(self.licenseEdit)
        self.licenseLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.licenseLabel.setToolTip("The license, which must be an open source software license")

        self.summaryLabel = QLabel("Summary<font color=\'red\'>*</font>")
        self.summaryEdit = QLineEdit()
        self.summaryEdit.setMinimumHeight(30)
        self.summaryLabel.setBuddy(self.summaryEdit)
        self.summaryLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.summaryLabel.setToolTip("A brief, one-line summary of the package. Use American English")

        self.descriptionLabel = QLabel("Description<font color=\'red\'>*</font> ")
        self.descriptionEdit = QLineEdit()
        self.descriptionEdit.setMinimumHeight(30)
        self.descriptionLabel.setBuddy(self.descriptionEdit)
        self.descriptionLabel.setCursor(QtGui.
                                        QCursor(QtCore.Qt.WhatsThisCursor))
        self.descriptionLabel.setToolTip("A longer, multi-line description of the program")

        self.URLLabel = QLabel("URL: ")
        self.URLEdit = QLineEdit()
        self.URLEdit.setMinimumHeight(30)
        self.URLLabel.setBuddy(self.URLEdit)
        self.URLLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.URLLabel.setToolTip("The full URL for more information about the program (e.g. the project website)")

        self.importLabel = QLabel("Source<font color=\'red\'>*</font>")
        self.importEdit = QLineEdit()
        self.importEdit.setMinimumHeight(30)
        self.importLabel.setBuddy(self.importEdit)
        self.importLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.importLabel.setToolTip("Pristine source package (e.g. tarballs) and patches")
        self.importEdit.textChanged.connect(self.checkPath)
        self.importEdit.setMinimumHeight(34)

        self.importButton = QPushButton("Import")
        self.importButton.setMinimumHeight(45)
        self.importButton.setMinimumWidth(115)
        self.importButton.clicked.connect(self.importPath)

        # Making mandatory fields:
        self.registerField("Name*", self.nameEdit)
        self.registerField("Summary*", self.summaryEdit)
        self.registerField("Version*", self.versionEdit)
        self.registerField("Release*", self.releaseEdit)
        self.registerField("License*", self.licenseEdit)
        self.registerField("Source*", self.importEdit)
        self.registerField("Description*", self.descriptionEdit)

        mainLayout = QVBoxLayout()
        grid = QGridLayout()
        grid.addWidget(self.importLabel, 0, 0, 1, 1)
        grid.addWidget(self.importEdit, 0, 1, 1, 1)
        grid.addWidget(self.importButton, 0, 2, 1, 1)
        grid.addWidget(self.nameLabel, 1, 0, 1, 1)
        grid.addWidget(self.nameEdit, 1, 1, 1, 3)
        grid.addWidget(self.versionLabel, 2, 0, 1, 1)
        grid.addWidget(self.versionEdit, 2, 1, 1, 3)
        grid.addWidget(self.releaseLabel, 3, 0, 1, 1)
        grid.addWidget(self.releaseEdit, 3, 1, 1, 3)
        grid.addWidget(self.licenseLabel, 4, 0, 1, 1)
        grid.addWidget(self.licenseEdit, 4, 1, 1, 3)
        grid.addWidget(self.summaryLabel, 5, 0, 1, 1)
        grid.addWidget(self.summaryEdit, 5, 1, 1, 3)
        grid.addWidget(self.descriptionLabel, 6, 0, 1, 1)
        grid.addWidget(self.descriptionEdit, 6, 1, 1, 3)
        grid.addWidget(self.URLLabel, 7, 0, 1, 1)
        grid.addWidget(self.URLEdit, 7, 1, 1, 3)
        mainLayout.addSpacing(40)
        mainLayout.addLayout(grid)
        self.setLayout(mainLayout)

    def checkPath(self):
        ''' Checks, if path to import is correct while typing'''
        path = Path(self.importEdit.text())
        if(path.exists()):
            self.importEdit.setStyleSheet("")
        else:
            self.importEdit.setStyleSheet("QLineEdit { border-style: solid;" +
                                          "border-width: 1px;" +
                                          "border-color: red;" +
                                          "border-radius: 3px;" +
                                          "background-color:" +
                                          "rgb(233,233,233);}")

    def importPath(self):
        ''' Returns path selected file or archive'''

        self.import_dialog = DialogImport()
        self.import_dialog.exec_()
        if (isinstance(self.import_dialog.filesSelected(), list)):
            path = self.import_dialog.filesSelected()
        else:
            path = self.import_dialog.selectedFiles()
        try:
            self.importEdit.setText(path[0])
        except IndexError:
            msq = "Source file or archive is not selected"

    def validatePage(self):
        ''' [Bool] Function that invokes just after pressing the next button
            {True} - user moves to next page
            {False}- user blocked on current page
            ###### Setting up RPG class references ###### '''

        # Verifying path
        path = Path(self.importEdit.text())
        if(path.exists()):
            self.base.spec.Name = self.nameEdit.text()
            self.base.spec.Version = self.versionEdit.text()
            self.base.spec.Release = self.releaseEdit.text()
            self.base.spec.License = self.licenseEdit.text()
            self.base.spec.URL = self.URLEdit.text()
            self.base.spec.Summary = self.summaryEdit.text()
            self.base.spec.description = self.descriptionEdit.text()
            self.base.spec.Source = self.importEdit.text().strip()
            self.base.process_archive_or_dir(self.base.spec.Source)
            self.base.run_raw_sources_analysis()
            self.importEdit.setStyleSheet("")
            return True
        else:
            self.importEdit.setStyleSheet("QLineEdit { border-style: solid;" +
                                          "border-width: 1px;" +
                                          "border-color: red;" +
                                          "border-radius: 3px;" +
                                          "background-color:" +
                                          "rgb(233,233,233);}")
            return False

    def nextId(self):
        ''' [int] Function that determines the next page after the current one
            - returns integer value and then checks, which value is page"
            in NUM_PAGES'''

        return Wizard.PagePatches


class ScriptsPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.prepareEdit.setText(str(self.base.spec.prep))
        self.buildEdit.setText(str(self.base.spec.build))
        self.installEdit.setText(str(self.base.spec.install))
        self.checkEdit.setText(str(self.base.spec.check))

    def __init__(self, Wizard, parent=None):
        super(ScriptsPage, self).__init__(parent)

        self.base = Wizard.base

        self.setTitle(self.tr("Scripts page"))
        self.setSubTitle(self.tr("Write scripts"))

        prepareLabel = QLabel("%prepare: ")
        self.prepareEdit = QTextEdit()
        prepareLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        prepareLabel.setToolTip("Script commands to prepare the program (e.g. to uncompress it) so that it will be ready for building. Typically this is just %autosetup; a common variation is %autosetup -n NAME if the source file unpacks into NAME")

        buildLabel = QLabel("%build: ")
        self.buildEdit = QTextEdit()
        buildLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        buildLabel.setToolTip("Script commands to build the program (e.g. to compile it) and get it ready for installing")

        installLabel = QLabel("%install: ")
        self.installEdit = QTextEdit()
        installLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        installLabel.setToolTip("Script commands to install the program")

        checkLabel = QLabel("%check: ")
        self.checkEdit = QTextEdit()
        checkLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        checkLabel.setToolTip("Script commands to test the program")

        buildArchLabel = QLabel("BuildArch: ")
        self.buildArchCheckbox = QCheckBox("noarch")
        buildArchLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        buildArchLabel.setToolTip("If you're packaging files that are architecture-independent (e.g. shell scripts, data files), then add BuildArch: noarch. The architecture for the binary RPM will then be noarch")

        grid = QGridLayout()
        grid.addWidget(prepareLabel, 0, 0)
        grid.addWidget(self.prepareEdit, 0, 1)
        grid.addWidget(buildLabel, 1, 0)
        grid.addWidget(self.buildEdit, 1, 1)
        grid.addWidget(installLabel, 2, 0)
        grid.addWidget(self.installEdit, 2, 1)
        grid.addWidget(checkLabel, 3, 0)
        grid.addWidget(self.checkEdit, 3, 1)
        grid.addWidget(buildArchLabel, 4, 0)
        grid.addWidget(self.buildArchCheckbox, 4, 1)
        self.setLayout(grid)

    def validatePage(self):
        self.base.spec.prep = Command(self.prepareEdit.toPlainText())
        self.base.spec.build = Command(self.buildEdit.toPlainText())
        self.base.spec.install = Command(self.installEdit.toPlainText())
        self.base.spec.check = Command(self.checkEdit.toPlainText())
        if self.buildArchCheckbox.isChecked():
            self.base.spec.BuildArch = "noarch"
        return True

    def nextId(self):
        return Wizard.PageRequires


class PatchesPage(QtWidgets.QWizardPage):
    def __init__(self, Wizard, parent=None):
        super(PatchesPage, self).__init__(parent)

        self.base = Wizard.base

        self.setTitle(self.tr("Patches, documents and changelog page"))
        self.setSubTitle(self.tr("\n"))

        self.addButton = QPushButton("+")
        self.removeButton = QPushButton("-")
        patchesLabel = QLabel("Patches")
        patchesLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        patchesLabel.setToolTip("Patches should make only one logical change each, so it's quite possible to have multiple patch files")
        self.listPatches = QListWidget()
        self.addButton.setMaximumWidth(68)
        self.addButton.setMaximumHeight(60)
        self.addButton.clicked.connect(self.openPatchesPageFileDialog)
        self.removeButton.setMaximumWidth(68)
        self.removeButton.setMaximumHeight(60)
        self.removeButton.clicked.connect(self.removeItemFromListWidget)

        documentationFilesLabel = QLabel("Documentation files ")
        documentationFilesLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        documentationFilesLabel.setToolTip("Documentation files that you wish to include")
        self.addDocumentationButton = QPushButton("+")
        self.addDocumentationButton.clicked.connect(self.openDocsFileDialog)
        self.addDocumentationButton.setMaximumWidth(68)
        self.addDocumentationButton.setMaximumHeight(60)
        self.removeDocumentationButton = QPushButton("-")
        self.removeDocumentationButton.setMaximumWidth(68)
        self.removeDocumentationButton.setMaximumHeight(60)
        self.openChangelogDialogButton = QPushButton("Changelog")
        self.openChangelogDialogButton.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        self.openChangelogDialogButton.setToolTip("Changes in the package. Do NOT put software's changelog at here.This changelog is for RPM itself")
        self.openChangelogDialogButton.clicked.connect(
            self.openChangeLogDialog)
        self.documentationFilesList = QListWidget()

        topLayout = QGridLayout()
        topLayout.addWidget(patchesLabel, 0, 2)
        topLayout.addWidget(self.addButton, 0, 0,)
        topLayout.addWidget(self.removeButton, 0, 1)
        topLayout.addWidget(self.listPatches, 1, 0, 1, 0)

        mainLayout = QVBoxLayout()
        upperLayout = QHBoxLayout()
        midleLayout = QHBoxLayout()
        lowerLayout = QHBoxLayout()
        upperLayout.addWidget(self.addDocumentationButton)
        upperLayout.addWidget(self.removeDocumentationButton)
        upperLayout.addWidget(documentationFilesLabel)
        midleLayout.addWidget(self.documentationFilesList)
        lowerLayout.addWidget(self.openChangelogDialogButton)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(upperLayout)
        mainLayout.addLayout(midleLayout)
        mainLayout.addLayout(lowerLayout)
        self.setLayout(mainLayout)

    def openChangeLogDialog(self):
        changelogWindow = QDialog()
        changelog = DialogChangelog(changelogWindow, self)
        changelog.exec_()

    def openDocsFileDialog(self):
        brows = QFileDialog()
        brows.getOpenFileName(self, "/home")

    def removeItemFromListWidget(self):
        self.item = self.listPatches.takeItem(self.listPatches.currentRow())
        self.item = None

    def openPatchesPageFileDialog(self):
        brows = QFileDialog()
        self.getPath = brows.getOpenFileName(self,
                                             "Choose patches",
                                             "/home",
                                             "All files (*)")
        self.newPath = self.getPath[0]
        self.listPatches.addItem(self.newPath)

    def validatePage(self):
        self.itemsCount = self.listPatches.count()
        self.pathes = []
        for i in range(0, self.itemsCount):
            self.pathes.append(self.listPatches.item(i).text())

        self.base.apply_patches(self.pathes)
        self.base.run_patched_sources_analysis()
        return True

    def nextId(self):
        return Wizard.PageScripts


class RequiresPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.bRequiresEdit.setText('\n'.join(self.base.spec.BuildRequires))
        self.requiresEdit.setText('\n'.join(self.base.spec.Requires))
        self.providesEdit.setText('\n'.join(self.base.spec.Provides))

    def __init__(self, Wizard, parent=None):
        super(RequiresPage, self).__init__(parent)

        self.base = Wizard.base

        self.setTitle(self.tr("Requires page"))
        self.setSubTitle(self.tr("Write requires and provides"))

        buildRequiresLabel = QLabel("BuildRequires: ")
        self.bRequiresEdit = QTextEdit()
        self.bRequiresEdit.setMaximumHeight(220)
        buildRequiresLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        buildRequiresLabel.setToolTip("A line-separated list of packages required for building (compiling) the program")

        requiresLabel = QLabel("Requires: ")
        self.requiresEdit = QTextEdit()
        self.requiresEdit.setMaximumHeight(220)
        requiresLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        requiresLabel.setToolTip("A line-separate list of packages that are required when the program is installed")

        providesLabel = QLabel("Provides: ")
        self.providesEdit = QTextEdit()
        providesLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        providesLabel.setToolTip("List virtual package names that this package provides")

        grid = QGridLayout()
        grid.addWidget(buildRequiresLabel, 0, 0)
        grid.addWidget(self.bRequiresEdit, 1, 0)
        grid.addWidget(requiresLabel, 2, 0)
        grid.addWidget(self.requiresEdit, 3, 0,)
        grid.addWidget(providesLabel, 4, 0)
        grid.addWidget(self.providesEdit, 5, 0)
        self.setLayout(grid)

    def validatePage(self):
        self.base.spec.BuildRequires = self.bRequiresEdit.toPlainText()
        self.base.spec.Requires = self.requiresEdit.toPlainText()
        self.base.spec.Provides = self.providesEdit.toPlainText()
        self.base.spec.BuildRequires = self.base.spec.BuildRequires.splitlines()
        self.base.spec.Requires = self.base.spec.Requires.splitlines()
        self.base.spec.Provides = self.base.spec.Provides.splitlines() 
        self.base.build_project()
        self.base.run_compiled_analysis()
        self.base.install_project()
        self.base.run_installed_analysis()
        return True

    def nextId(self):
        return Wizard.PageSubpackages


class ScripletsPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.pretransEdit.setText(str(self.base.spec.pretrans))
        self.preEdit.setText(str(self.base.spec.pre))
        self.postEdit.setText(str(self.base.spec.post))
        self.postunEdit.setText(str(self.base.spec.postun))
        self.preunEdit.setText(str(self.base.spec.preun))
        self.posttransEdit.setText(str(self.base.spec.posttrans))

    def __init__(self, Wizard, parent=None):
        super(ScripletsPage, self).__init__(parent)

        self.base = Wizard.base
        self.setTitle(self.tr("Scriplets page"))
        self.setSubTitle(self.tr("Write scriplets"))

        pretransLabel = QLabel("%pretrans: ")
        self.pretransEdit = QTextEdit()
        pretransLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        pretransLabel.setToolTip("At the start of transaction")

        preLabel = QLabel("%pre: ")
        self.preEdit = QTextEdit()
        preLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        preLabel.setToolTip("Before a packages is installed")

        postLabel = QLabel("%post: ")
        self.postEdit = QTextEdit()
        postLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        postLabel.setToolTip("After a packages is installed")

        postunLabel = QLabel("%postun: ")
        self.postunEdit = QTextEdit()
        postunLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        postunLabel.setToolTip("After a packages is uninstalled")

        preunLabel = QLabel("%preun: ")
        self.preunEdit = QTextEdit()
        preunLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        preunLabel.setToolTip("Before a packages is uninstalled")

        posttransLabel = QLabel("%posttrans: ")
        self.posttransEdit = QTextEdit()
        posttransLabel.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        posttransLabel.setToolTip("At the end of transaction")

        grid = QGridLayout()
        grid.addWidget(pretransLabel, 0, 0)
        grid.addWidget(self.pretransEdit, 0, 1)
        grid.addWidget(preLabel, 1, 0)
        grid.addWidget(self.preEdit, 1, 1,)
        grid.addWidget(postLabel, 2, 0)
        grid.addWidget(self.postEdit, 2, 1)
        grid.addWidget(postunLabel, 3, 0)
        grid.addWidget(self.postunEdit, 3, 1)
        grid.addWidget(preunLabel, 4, 0)
        grid.addWidget(self.preunEdit, 4, 1,)
        grid.addWidget(posttransLabel, 5, 0)
        grid.addWidget(self.posttransEdit, 5, 1)
        self.setLayout(grid)

    def validatePage(self):
        self.base.spec.pretrans = Command(self.pretransEdit.toPlainText())
        self.base.spec.pre = Command(self.preEdit.toPlainText())
        self.base.spec.post = Command(self.postEdit.toPlainText())
        self.base.spec.postun = Command(self.postunEdit.toPlainText())
        self.base.spec.preun = Command(self.preunEdit.toPlainText())
        self.base.spec.posttrans = Command(self.posttransEdit.toPlainText())
        return True

    def nextId(self):
        return Wizard.PageBuild


class SubpackagesPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.tree.addSubpackage(self.base.spec.Name)
        for a, b, c in self.base.spec.files:
            if ".lang" not in str(a):
                self.tree.addFileToSubpackage(self.
                                              tree.
                                              invisibleRootItem().child(0),
                                              a, "file")

    def __init__(self, Wizard, parent=None):
        super(SubpackagesPage, self).__init__(parent)

        self.base = Wizard.base
        self.tree = self.SubpackTreeWidget(self)

        self.setTitle(self.tr("Subpackages page"))
        self.setSubTitle(self.tr("Choose subpackages"))

        filesLabel = QLabel("Do not include: ")
        subpackagesLabel = QLabel("Packages: ")

        self.addPackButton = QPushButton("+")
        self.addPackButton.setMaximumWidth(68)
        self.addPackButton.setMaximumHeight(60)
        self.addPackButton.clicked.connect(self.openSubpackageDialog)

        self.removePackButton = QPushButton("-")
        self.removePackButton.setMaximumWidth(68)
        self.removePackButton.setMaximumHeight(60)
        self.removePackButton.clicked.connect(self.removeItem)

        self.transferButton = QPushButton("->")
        self.transferButton.setMaximumWidth(120)
        self.transferButton.setMaximumHeight(20)
        self.transferButton.clicked.connect(self.moveFileToTree)

        self.filesListWidget = QListWidget()
        mainLayout = QVBoxLayout()
        upperLayout = QHBoxLayout()
        lowerLayout = QHBoxLayout()
        upperLayout.addSpacing(150)
        upperLayout.addWidget(filesLabel)
        upperLayout.addSpacing(190)
        upperLayout.addWidget(subpackagesLabel)
        upperLayout.addWidget(self.addPackButton)
        upperLayout.addWidget(self.removePackButton)
        lowerLayout.addWidget(self.filesListWidget)
        lowerLayout.addWidget(self.transferButton)
        lowerLayout.addWidget(self.tree)
        mainLayout.addLayout(upperLayout)
        mainLayout.addLayout(lowerLayout)
        self.setLayout(mainLayout)

    def moveFileToTree(self):
        ''' Function to move items from left to right
            (depending on which and where selected)
            - trigered when user clicked [ -> ] button '''
        self.subpackageItems = self.tree.selectedItems()
        self.subpackageItem = self.subpackageItems[0]
        self.itemLeft = self.filesListWidget.takeItem(self.filesListWidget.
                                                      currentRow())
        for itemRight in self.tree.selectedItems():
            if (itemRight.parent() is None):
                self.tree.addFileToSubpackage(itemRight,
                                              self.itemLeft.text(), "file")
            else:
                self.tree.addFileToSubpackage(itemRight.parent(),
                                              self.itemLeft.text(), "file")
        self.itemLeft = None

    def removeItem(self):
        ''' Function to remove items (depending on which and where selected)
            - trigered when user clicked [ - ] button '''
        root = self.tree.invisibleRootItem()
        for item in self.tree.selectedItems():
            if (item.parent() is not None):
                self.filesListWidget.addItem(item.text(0))
            (item.parent() or root).removeChild(item)

    def openSubpackageDialog(self):
        subpackageWindow = QDialog()
        subpackage = DialogSubpackage(subpackageWindow, self)
        subpackage.exec_()

    def nextId(self):
        return Wizard.PageScriplets

    # Class for tree view (Subpackages generation)
    class SubpackTreeWidget(QTreeWidget):
        def __init__(self, Page):
            self.page = Page
            QtWidgets.QWidget.__init__(self)

            ''' TODO - drag and drop, someday'''
            #self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            self.setColumnCount = 1  # only one column in each row
            self.column = 1
            self.setHeaderHidden(True)  # make invisible -1 row (with name)
            self.header().setSectionResizeMode(3)

        def addSubpackage(self, Name):
            self.name = Name
            ''' Add new subpackage and make root it's parent '''
            self.addParent(self.invisibleRootItem(),
                           self.name,
                           self.name + " Subpackage")
            self.resizeColumnToContents(0)

        def addParent(self, parent, title, data):
            item = QTreeWidgetItem(parent, [title])
            item.setData(self.column, QtCore.Qt.UserRole, data)

            ''' Dropdown arrows near subpackages '''
            item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            item.setExpanded(True)  # To look like a tree (expanding items)
            self.resizeColumnToContents(0)
            return item

        def addFileToSubpackage(self, parent, title, data):
            item = QTreeWidgetItem(parent, [title])
            item.setData(self.column, QtCore.Qt.UserRole, data)
            self.resizeColumnToContents(0)
            return item


class BuildPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.buildLocationEdit.setText(str(self.base.rpm_path))
    def __init__(self, Wizard, parent=None):
        super(BuildPage, self).__init__(parent)

        self.base = Wizard.base

        self.Wizard = Wizard  # Main wizard of program
        self.nextPageIsFinal = True  # BOOL to determine which page is next one
        self.setTitle(self.tr("Build page"))
        self.setSubTitle(self.tr("Options to build"))

        self.buildToButton = QPushButton("Build to")
        self.buildToButton.clicked.connect(self.openBuildPathFileDialog)
        self.uploadToCOPR_Button = QPushButton("Upload to COPR")
        self.editSpecButton = QPushButton("Edit SPEC file")
        self.editSpecButton.clicked.connect(self.editSpecFile)
        self.uploadToCOPR_Button.clicked.connect(self.switchToCOPR)
        self.uploadToCOPR_Button.clicked.connect(self.Wizard.next)
        specWarningLabel = QLabel("* Edit SPEC file on your own risk")
        self.buildLocationEdit = QLineEdit()

        mainLayout = QVBoxLayout()
        midleLayout = QHBoxLayout()
        lowerLayout = QHBoxLayout()

        midleLayout.addWidget(self.editSpecButton)
        midleLayout.addWidget(specWarningLabel)
        midleLayout.addSpacing(330)
        midleLayout.addWidget(self.uploadToCOPR_Button)
        lowerLayout.addWidget(self.buildToButton)
        lowerLayout.addWidget(self.buildLocationEdit)

        mainLayout.addSpacing(60)
        mainLayout.addLayout(midleLayout)
        mainLayout.addSpacing(10)
        mainLayout.addLayout(lowerLayout)
        self.setLayout(mainLayout)

    def validatePage(self):
        self.base.write_spec()
        self.base.build_packages("fedora-21-x86_64")
        return True
        
    def editSpecFile(self):
        '''If user clicked Edit SPACE file, default text editor with the file is open'''
        subprocess.call(('xdg-open', str(self.base.spec_path)))

    def switchToCOPR(self):
        '''If user clicked uplodad to copr button, so next page is not final'''
        self.nextPageIsFinal = False

    def openBuildPathFileDialog(self):
        brows = QFileDialog()
        self.getPath = brows.getExistingDirectory(self,
                                                  "Select Directory",
                                                  "/home",
                                                  QFileDialog.ShowDirsOnly)
        self.buildLocationEdit.setText(self.getPath)

    def nextId(self):
        if (self.nextPageIsFinal):
            return Wizard.PageFinal
        else:
            self.nextPageIsFinal = True
            return Wizard.PageCopr


class CoprPage(QtWidgets.QWizardPage):
    def __init__(self, Wizard, parent=None):
        super(CoprPage, self).__init__(parent)

        self.base = Wizard.base

        self.setTitle(self.tr("Copr page"))
        self.setSubTitle(self.tr("COPR repository setting and uploading"))

        self.x86_CheckBox = QCheckBox("x86")
        self.x64_CheckBox = QCheckBox("x64")
        self.Fedora20_CheckBox = QCheckBox("Fedora 20")
        self.Fedora19_CheckBox = QCheckBox("Fedora 19")
        self.Fedora18_CheckBox = QCheckBox("Fedora 18")
        self.Fedora17_CheckBox = QCheckBox("Fedora 17")
        self.Fedora16_CheckBox = QCheckBox("Fedora 16")
        self.RHEL3_CheckBox = QCheckBox("RHEL 3")
        self.RHEL4_CheckBox = QCheckBox("RHEL 4")
        self.RHEL5_CheckBox = QCheckBox("RHEL 5")
        self.RHEL6_CheckBox = QCheckBox("RHEL 6")
        self.RHEL7_CheckBox = QCheckBox("RHEL 7")

        self.createCOPRButton = QPushButton("Create COPR repository")
        self.chooseCONFButton = QPushButton("Choose .conf file")
        self.chooseCONFButton.clicked.connect(self.openChooseCONFFileDialog)
        releaserLabel = QLabel("Releaser: ")
        self.releaserEdit = QLineEdit()
        projectNameLabel = QLabel("Project name: ")
        self.projectNameEdit = QLineEdit()

        self.releaserEdit.setMinimumHeight(30)
        releaserLabel.setBuddy(self.releaserEdit)

        self.projectNameEdit.setMinimumHeight(30)
        projectNameLabel.setBuddy(self.projectNameEdit)

        releaseBox = QGroupBox()
        archBox = QGroupBox()
        layoutReleaseBox = QGridLayout()
        layoutArchBox = QGridLayout()

        releaseBox.setTitle('Choose distribution')
        layoutReleaseBox.setColumnStretch(0, 1)
        layoutReleaseBox.setColumnStretch(1, 1)
        layoutReleaseBox.setColumnStretch(2, 1)
        layoutReleaseBox.setColumnStretch(3, 1)
        layoutReleaseBox.setColumnStretch(4, 1)
        layoutReleaseBox.addWidget(self.Fedora20_CheckBox, 0, 1)
        layoutReleaseBox.addWidget(self.Fedora19_CheckBox, 1, 1)
        layoutReleaseBox.addWidget(self.Fedora18_CheckBox, 2, 1)
        layoutReleaseBox.addWidget(self.Fedora17_CheckBox, 3, 1)
        layoutReleaseBox.addWidget(self.Fedora16_CheckBox, 4, 1)
        layoutReleaseBox.addWidget(self.RHEL7_CheckBox, 0, 3)
        layoutReleaseBox.addWidget(self.RHEL6_CheckBox, 1, 3)
        layoutReleaseBox.addWidget(self.RHEL5_CheckBox, 2, 3)
        layoutReleaseBox.addWidget(self.RHEL4_CheckBox, 3, 3)
        layoutReleaseBox.addWidget(self.RHEL3_CheckBox, 4, 3)
        releaseBox.setLayout(layoutReleaseBox)

        archBox.setTitle('Choose architecture')
        layoutArchBox.setColumnStretch(0, 1)
        layoutArchBox.setColumnStretch(1, 1)
        layoutArchBox.setColumnStretch(2, 1)
        layoutArchBox.setColumnStretch(3, 1)
        layoutArchBox.setColumnStretch(4, 1)
        layoutArchBox.addWidget(self.x64_CheckBox, 0, 1)
        layoutArchBox.addWidget(self.x86_CheckBox, 0, 3)
        archBox.setLayout(layoutArchBox)

        mainLayout = QVBoxLayout()
        upperLayout = QHBoxLayout()
        upper2Layout = QHBoxLayout()
        midleLayout = QHBoxLayout()
        lowerLayout = QGridLayout()
        upperLayout.addWidget(releaseBox)
        upper2Layout.addWidget(archBox)
        midleLayout.addSpacing(170)
        midleLayout.addWidget(self.createCOPRButton)
        midleLayout.addSpacing(50)
        midleLayout.addWidget(self.chooseCONFButton)
        midleLayout.addSpacing(170)
        lowerLayout.addWidget(releaserLabel, 0, 0)
        lowerLayout.addWidget(self.releaserEdit, 0, 1)
        lowerLayout.addWidget(projectNameLabel)
        lowerLayout.addWidget(self.projectNameEdit)
        mainLayout.addSpacing(30)
        mainLayout.addLayout(upperLayout)
        mainLayout.addSpacing(40)
        mainLayout.addLayout(upper2Layout)
        mainLayout.addLayout(midleLayout)
        mainLayout.addSpacing(30)
        mainLayout.addLayout(lowerLayout)
        self.setLayout(mainLayout)

    def openChooseCONFFileDialog(self):
        brows = QFileDialog()
        brows.getOpenFileName(self, "/home")

    def nextId(self):
        return Wizard.PageFinal


class FinalPage(QtWidgets.QWizardPage):
    def initializePage(self):
        self.buildPath = (str(self.base.srpm_path))
        self.finalLabel.setText("<html><head/><body><p align=\"center\"><span" +
                            "style=\" font-size:24pt;\">Thank you for " +
                            "using RPG!</span></p><p align=\"center\">" +
                            "<span style=\" font-size:24pt;\">Your" +
                            " package was built in:</span></p>"+
                            "<p align=\"center\">"+ self.buildPath +
                            "<p></body></html>")
    def __init__(self, Wizard, parent=None):
        super(FinalPage, self).__init__(parent)

        self.base = Wizard.base
        ''' On this page will be "Finish button" instead of "Next" '''
        FinalPage.setFinalPage(self, True)
        self.setTitle(self.tr("Final page"))
        self.setSubTitle(self.tr("Your package was successfully created"))
        self.finalLabel = QLabel()
        grid = QGridLayout()
        grid.addWidget(self.finalLabel, 0, 0)

        mainLayout = QVBoxLayout()
        mainLayout.addSpacing(190)
        mainLayout.addWidget(self.finalLabel)
        mainLayout.addSpacing(190)

        self.setLayout(mainLayout)

    def validatePage(self):
        print(self.base.spec)
        return True
