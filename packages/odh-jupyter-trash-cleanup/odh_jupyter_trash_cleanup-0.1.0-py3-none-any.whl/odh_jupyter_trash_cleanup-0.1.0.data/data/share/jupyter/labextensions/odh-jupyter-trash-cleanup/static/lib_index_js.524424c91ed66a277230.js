"use strict";
(self["webpackChunkodh_jupyter_trash_cleanup"] = self["webpackChunkodh_jupyter_trash_cleanup"] || []).push([["lib_index_js"],{

/***/ "./lib/TrashIcon.js":
/*!**************************!*\
  !*** ./lib/TrashIcon.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   trashIcon: () => (/* binding */ trashIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _style_icons_trash_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../style/icons/trash.svg */ "./style/icons/trash.svg");


const trashIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'odh-jupyter-trash-cleanup:trash',
    svgstr: _style_icons_trash_svg__WEBPACK_IMPORTED_MODULE_1__
});


/***/ }),

/***/ "./lib/emptyTrashCommand.js":
/*!**********************************!*\
  !*** ./lib/emptyTrashCommand.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   emptyTrashCommand: () => (/* binding */ emptyTrashCommand)
/* harmony export */ });
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _TrashIcon__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./TrashIcon */ "./lib/TrashIcon.js");



const emptyTrashCommand = (translator) => {
    const trans = translator.load('odh_jupyter_trash_cleanup');
    return {
        label: trans.__('Empty Trash'),
        caption: trans.__('Empty Trash'),
        icon: _TrashIcon__WEBPACK_IMPORTED_MODULE_2__.trashIcon,
        execute: async () => {
            const result = await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                title: trans.__('Empty all items from Trash?'),
                body: trans.__('All items in the Trash will be permanently deleted.'),
                buttons: [
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.cancelButton({ label: trans.__('Cancel') }),
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: trans.__('Empty Trash') })
                ]
            });
            if (!result.button.accept) {
                return;
            }
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.promise((0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('empty-trash', { method: 'POST' }), {
                pending: {
                    message: trans.__('Emptying Trash...'),
                    options: { autoClose: false }
                },
                success: {
                    message: () => trans.__('Files successfully removed from trash.')
                },
                error: { message: () => trans.__('Error removing files from trash') }
            });
        }
    };
};


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'odh-jupyter-trash-cleanup', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _emptyTrashCommand__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./emptyTrashCommand */ "./lib/emptyTrashCommand.js");



const ODH_IDE_CLEAR_TRASH_COMMAND = 'odh-ide:clear-trash';
const ODH_IDE_CATEGORY = 'ODH IDE';
/**
 * Initialization data for the odh-jupyter-trash-cleanup extension.
 */
const plugin = {
    id: 'odh-jupyter-trash-cleanup:plugin',
    description: 'A JupyterLab extension to allow users to clean the trash from the JupyterLab UI',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.ITranslator],
    activate: (app, commandPalette, translator) => {
        console.log('JupyterLab extension odh-jupyter-trash-cleanup is activated!');
        const { commands } = app;
        commands.addCommand(ODH_IDE_CLEAR_TRASH_COMMAND, (0,_emptyTrashCommand__WEBPACK_IMPORTED_MODULE_2__.emptyTrashCommand)(translator));
        commandPalette.addItem({
            command: ODH_IDE_CLEAR_TRASH_COMMAND,
            category: ODH_IDE_CATEGORY,
            args: { origin: 'from palette' }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./style/icons/trash.svg":
/*!*******************************!*\
  !*** ./style/icons/trash.svg ***!
  \*******************************/
/***/ ((module) => {

module.exports = "﻿<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 640\"><!--!Font Awesome Free v7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path d=\"M232.7 69.9L224 96L128 96C110.3 96 96 110.3 96 128C96 145.7 110.3 160 128 160L512 160C529.7 160 544 145.7 544 128C544 110.3 529.7 96 512 96L416 96L407.3 69.9C402.9 56.8 390.7 48 376.9 48L263.1 48C249.3 48 237.1 56.8 232.7 69.9zM512 208L128 208L149.1 531.1C150.7 556.4 171.7 576 197 576L443 576C468.3 576 489.3 556.4 490.9 531.1L512 208z\"/></svg>";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.524424c91ed66a277230.js.map