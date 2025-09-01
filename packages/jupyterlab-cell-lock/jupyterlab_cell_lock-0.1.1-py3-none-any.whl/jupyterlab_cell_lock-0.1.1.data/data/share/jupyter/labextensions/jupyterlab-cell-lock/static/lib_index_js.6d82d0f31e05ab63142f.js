"use strict";
(self["webpackChunkjupyterlab_cell_lock"] = self["webpackChunkjupyterlab_cell_lock"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);




const plugin = {
    id: 'metadata-editor:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    activate: (app, tracker) => {
        console.log('jupyterlab_cell_lock extension activated!');
        const toggleCellMetadata = (editable, deletable, tracker) => {
            var _a;
            const current = tracker.currentWidget;
            if (!current) {
                console.warn('No active notebook.');
                return;
            }
            const cells = (_a = current.content.model) === null || _a === void 0 ? void 0 : _a.cells;
            if (!cells) {
                return;
            }
            // JupyterLab may omit "editable"/"deletable" when they are true,
            // as this is the default. To handle this correctly, the extension treats
            // missing values as true so the comparison logic works as expected.
            const asBool = (v) => (typeof v === 'boolean' ? v : true);
            let count = 0;
            for (let i = 0; i < cells.length; i++) {
                const cell = cells.get(i);
                const curEditable = asBool(cell.getMetadata('editable'));
                const curDeletable = asBool(cell.getMetadata('deletable'));
                if (curEditable !== editable || curDeletable !== deletable) {
                    cell.setMetadata('editable', editable);
                    cell.setMetadata('deletable', deletable);
                    count++;
                }
            }
            const action = editable ? 'unlocked' : 'locked';
            const message = editable
                ? 'editable and deletable.'
                : 'read-only and undeletable.';
            const dialogBody = count === 0
                ? `All cells were already ${action}.`
                : `${count} cell${count > 1 ? 's' : ''} ${count > 1 ? 'were' : 'was'} successfully ${action}. All cells are now ${message}`;
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                title: `Cells ${action}`,
                body: dialogBody,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()]
            });
        };
        // Define the lock command
        const lockCommand = 'metadata-editor:lock-cells';
        app.commands.addCommand(lockCommand, {
            label: 'Make All Cells Read-Only & Undeletable',
            execute: () => {
                toggleCellMetadata(false, false, tracker);
            }
        });
        // Define the unlock command
        const unlockCommand = 'metadata-editor:unlock-cells';
        app.commands.addCommand(unlockCommand, {
            label: 'Make All Cells Editable & Deletable',
            execute: () => {
                toggleCellMetadata(true, true, tracker);
            }
        });
        // Add toolbar buttons
        tracker.widgetAdded.connect((_, notebookPanel) => {
            const lockButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
                label: 'Lock all cells',
                icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.lockIcon,
                onClick: () => {
                    app.commands.execute(lockCommand);
                },
                tooltip: 'Lock all cells (read-only & undeletable)'
            });
            const unlockButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
                label: 'Unlock all cells',
                icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.editIcon,
                onClick: () => {
                    app.commands.execute(unlockCommand);
                },
                tooltip: 'Unlock all cells (editable & deletable)'
            });
            notebookPanel.toolbar.insertItem(10, 'lockCells', lockButton);
            notebookPanel.toolbar.insertItem(11, 'unlockCells', unlockButton);
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.6d82d0f31e05ab63142f.js.map