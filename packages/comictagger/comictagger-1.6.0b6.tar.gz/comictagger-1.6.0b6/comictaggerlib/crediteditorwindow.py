"""A PyQT4 dialog to edit credits"""

#
# Copyright 2012-2014 ComicTagger Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import logging
import operator

import natsort
from PyQt6 import QtCore, QtWidgets, uic

from comicapi import utils
from comicapi.genericmetadata import Credit
from comictaggerlib.ui import ui_path

logger = logging.getLogger(__name__)


class CreditEditorWindow(QtWidgets.QDialog):
    ModeEdit = 0
    ModeNew = 1

    def __init__(self, parent: QtWidgets.QWidget, mode: int, credit: Credit) -> None:
        super().__init__(parent)

        with (ui_path / "crediteditorwindow.ui").open(encoding="utf-8") as uifile:
            uic.loadUi(uifile, self)

        self.mode = mode

        if self.mode == self.ModeEdit:
            self.setWindowTitle("Edit Credit")
        else:
            self.setWindowTitle("New Credit")

        # Add the entries to the role combobox
        self.cbRole.addItem("")
        self.cbRole.addItem("Artist")
        self.cbRole.addItem("Colorist")
        self.cbRole.addItem("Cover Artist")
        self.cbRole.addItem("Editor")
        self.cbRole.addItem("Inker")
        self.cbRole.addItem("Letterer")
        self.cbRole.addItem("Penciller")
        self.cbRole.addItem("Plotter")
        self.cbRole.addItem("Scripter")
        self.cbRole.addItem("Translator")
        self.cbRole.addItem("Writer")
        self.cbRole.addItem("Other")

        self.cbLanguage.addItem("", "")
        for f in natsort.humansorted(utils.languages().items(), operator.itemgetter(1)):
            self.cbLanguage.addItem(f[1], f[0])

        self.leName.setText(credit.person)

        if credit.role is not None and credit.role != "":
            i = self.cbRole.findText(credit.role)
            if i == -1:
                self.cbRole.setEditText(credit.role)
            else:
                self.cbRole.setCurrentIndex(i)

        if credit.language != "":
            i = (
                self.cbLanguage.findData(credit.language, QtCore.Qt.ItemDataRole.UserRole)
                if self.cbLanguage.findData(credit.language, QtCore.Qt.ItemDataRole.UserRole) > -1
                else self.cbLanguage.findText(credit.language)
            )
            if i == -1:
                self.cbLanguage.setEditText(credit.language)
            else:
                self.cbLanguage.setCurrentIndex(i)

        self.cbPrimary.setChecked(credit.primary)

    def get_credit(self) -> Credit:
        lang = self.cbLanguage.currentData() or self.cbLanguage.currentText()
        return Credit(self.leName.text(), self.cbRole.currentText(), self.cbPrimary.isChecked(), lang)

    def accept(self) -> None:
        if self.leName.text() == "":
            QtWidgets.QMessageBox.warning(self, "Whoops", "You need to enter a name for a credit.")
        else:
            QtWidgets.QDialog.accept(self)
