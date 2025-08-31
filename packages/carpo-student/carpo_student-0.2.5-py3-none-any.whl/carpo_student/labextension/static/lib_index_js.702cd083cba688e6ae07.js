"use strict";
(self["webpackChunkcarpo_student"] = self["webpackChunkcarpo_student"] || []).push([["lib_index_js"],{

/***/ "./lib/get-solutions.js":
/*!******************************!*\
  !*** ./lib/get-solutions.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "GetSolutionButton": () => (/* binding */ GetSolutionButton)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



class GetSolutionButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const getSolutions = () => {
            (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('solution', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Get Solution Error', reason);
                console.error(`Failed to get problem solutions.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'get-solution-button',
            label: 'GetSolutions',
            onClick: getSolutions,
            tooltip: 'Download solutions to problems.',
        });
        panel.toolbar.insertItem(14, 'getSolutions', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'carpo-student', // API Namespace
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
/* harmony export */   "GetFeedbackButton": () => (/* binding */ GetFeedbackButton),
/* harmony export */   "GetQuestionButton": () => (/* binding */ GetQuestionButton),
/* harmony export */   "RegisterButton": () => (/* binding */ RegisterButton),
/* harmony export */   "ViewSubmissionStatusButton": () => (/* binding */ ViewSubmissionStatusButton),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   "viewProblemStatusExtension": () => (/* binding */ viewProblemStatusExtension)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _share_code__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./share-code */ "./lib/share-code.js");
/* harmony import */ var _get_solutions__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./get-solutions */ "./lib/get-solutions.js");








/**
 * Initialization data for the carpo-student extension.
 */
const plugin = {
    id: 'carpo-student:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__.ISettingRegistry],
    activate: (app, nbTrack, settingRegistry) => {
        console.log('JupyterLab extension carpo-student is activated!');
        // var interval => (); 
        var counter = 0;
        nbTrack.currentChanged.connect(() => {
            console.log("my counter: ", counter);
            const notebookPanel = nbTrack.currentWidget;
            const notebook = nbTrack.currentWidget.content;
            const filename = notebookPanel.context.path;
            // Disable Code Share functionality if inside Feedback directory
            if (filename.includes("Feedback")) {
                return;
            }
            // Disable if not inside Exercises directory
            if (!filename.includes("Exercises")) {
                return;
            }
            notebookPanel.context.ready.then(async () => {
                let currentCell = null;
                let currentCellCheckButton = null;
                nbTrack.activeCellChanged.connect(() => {
                    var question;
                    if (currentCell) {
                        notebook.widgets.map((c) => {
                            if (c.model.type == 'code' || c.model.type == 'markdown') {
                                const currentLayout = c.layout;
                                currentLayout.widgets.map(w => {
                                    if (w === currentCellCheckButton) {
                                        currentLayout.removeWidget(w);
                                    }
                                });
                            }
                        });
                    }
                    const cell = notebook.activeCell;
                    const activeIndex = notebook.activeCellIndex;
                    var info = {
                        problem_id: parseInt((filename.split("/").pop()).replace("ex", "").replace(".ipynb", ""))
                    };
                    // Get the message block referencing the active cell.
                    notebook.widgets.map((c, index) => {
                        if (c.model.value.text.startsWith("## Message to instructor:")) {
                            info.message = c.model.value.text;
                        }
                        if (index == activeIndex) {
                            question = c.model.value.text;
                            if (question.includes("## PID ")) {
                                const newCheckButton = new _widget__WEBPACK_IMPORTED_MODULE_4__.CellCheckButton(cell, info);
                                cell.layout.addWidget(newCheckButton);
                                currentCellCheckButton = newCheckButton;
                                // Send code snapshot to the server:
                                if (counter == 0) {
                                    setInterval(function () {
                                        // console.log("Update: ", c.model.value.text)
                                        let postBody = {
                                            "message": "",
                                            "code": c.model.value.text,
                                            "problem_id": info.problem_id,
                                            "snapshot": 1
                                        };
                                        // console.log("From widget: ", postBody)
                                        (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('submissions', {
                                            method: 'POST',
                                            body: JSON.stringify(postBody)
                                        })
                                            .then(data => {
                                            console.log("Snapshot sent.", data);
                                        });
                                    }, 10000);
                                    counter++;
                                }
                            }
                        }
                    });
                    // const newCheckButton: CellCheckButton = new CellCheckButton(cell,info);
                    // if (question.includes("## PID ")){
                    //   (cell.layout as PanelLayout).addWidget(newCheckButton);
                    //   currentCellCheckButton = newCheckButton;
                    // }
                    // Set the current cell and button for future
                    // reference
                    currentCell = cell;
                });
            });
        });
        //  tell the document registry about your widget extension:
        app.docRegistry.addWidgetExtension('Notebook', new RegisterButton());
        app.docRegistry.addWidgetExtension('Notebook', new GetQuestionButton());
        app.docRegistry.addWidgetExtension('Notebook', new _share_code__WEBPACK_IMPORTED_MODULE_6__.ShareCodeButton());
        app.docRegistry.addWidgetExtension('Notebook', new GetFeedbackButton());
        app.docRegistry.addWidgetExtension('Notebook', new _get_solutions__WEBPACK_IMPORTED_MODULE_7__.GetSolutionButton());
        app.docRegistry.addWidgetExtension('Notebook', new ViewSubmissionStatusButton());
        // app.docRegistry.addWidgetExtension('Notebook', new viewProblemStatusExtension());
    }
};
class RegisterButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const register = () => {
            // NotebookActions.clearAllOutputs(panel.content);
            // const notebook = panel.content;
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('register', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: '',
                    body: "Student " + data.name + " has been registered.",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Registration Error', reason);
                console.error(`Failed to register user as Student.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'register-button',
            label: 'Register',
            onClick: register,
            tooltip: 'Register as a Student',
        });
        panel.toolbar.insertItem(10, 'register', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class GetQuestionButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const getQuestion = () => {
            // NotebookActions.clearAllOutputs(panel.content);
            // const notebook = panel.content;
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('question', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Get Problem Error', reason);
                console.error(`Failed to get active questions.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'get-question-button',
            label: 'GetProblem',
            onClick: getQuestion,
            tooltip: 'Get Latest Problem From Server',
        });
        panel.toolbar.insertItem(11, 'getQuestion', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class GetFeedbackButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const getFeedback = () => {
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('feedback', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                }).then(result => {
                    if (result.button.accept && data['hard-reload'] == 1) {
                        window.location.reload();
                    }
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Get Feedback Error', reason);
                console.error(`Failed to fetch recent feedbacks.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'get-feedback-button',
            label: 'GetFeedback',
            onClick: getFeedback,
            tooltip: 'Get Feedback to your Submission',
        });
        panel.toolbar.insertItem(13, 'getFeedback', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class ViewSubmissionStatusButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const viewStatus = () => {
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('view_student_status', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                window.open(data.url, "_blank");
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('View Status Error', reason);
                console.error(`Failed to view student submission status.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'get-status-button',
            label: 'Status',
            onClick: viewStatus,
            tooltip: 'View your submissions status',
        });
        panel.toolbar.insertItem(14, 'viewStatus', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
// Currently disabled
class viewProblemStatusExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const viewProblemStatus = () => {
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('view_problem_list', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                window.open(data.url, "_blank");
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('View Problem Status Error', reason);
                console.error(`Failed to view problem status.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'get-status-button',
            label: 'Problems',
            onClick: viewProblemStatus,
            tooltip: 'View all problem status',
        });
        panel.toolbar.insertItem(15, 'viewProblemStatus', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/share-code.js":
/*!***************************!*\
  !*** ./lib/share-code.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ShareCodeButton": () => (/* binding */ ShareCodeButton)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



class ShareCodeButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const shareCode = () => {
            const notebook = panel.content;
            const filename = panel.context.path;
            const activeIndex = notebook.activeCellIndex;
            var codeBlock;
            var info = {
                problem_id: parseInt((filename.split("/").pop()).replace("ex", "").replace(".ipynb", ""))
            };
            notebook.widgets.map((c, index) => {
                if (c.model.value.text.startsWith("## Message to instructor:")) {
                    info.message = c.model.value.text;
                }
                if (index == activeIndex) {
                    codeBlock = c.model.value.text;
                }
            });
            if (!codeBlock.startsWith("## PID ")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', "Invalid cell selected. Use a specific problem cell block.");
                return;
            }
            let postBody = {
                "message": info.message,
                "code": codeBlock,
                "problem_id": info.problem_id,
                "snapshot": 2
            };
            console.log("Req body: ", postBody);
            (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('submissions', {
                method: 'POST',
                body: JSON.stringify(postBody)
            })
                .then(data => {
                if (data.msg === "Submission saved successfully.") {
                    if (info.message.length > 27) {
                        data.msg = 'Code & message is sent to the instructor.';
                    }
                    else {
                        data.msg = 'Code is sent to the instructor.';
                    }
                }
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'Ok' })]
                });
                // Keep checking for new feedback.
                // This setInterval will be cleared once the feedback is downloaded (after reload())
                // setInterval(function(){
                //     // console.log("Checking for feedback...")
                //     requestAPI<any>('feedback',{
                //     method: 'GET'
                //     })
                //     .then(data => {
                //         // console.log(data);
                //         if (data['hard-reload'] != -1) {
                //         showDialog({
                //             title:'',
                //             body: data.msg,
                //             buttons: [Dialog.okButton({ label: 'Ok' })]
                //         }).then( result => {
                //             if (result.button.accept ) {
                //                 window.location.reload();
                //             }
                //         })
                //         }
                //     })
                //     .catch(reason => {
                //         showErrorMessage('Get Feedback Error', reason);
                //         console.error(
                //         `Failed to fetch recent feedbacks.\n${reason}`
                //         );
                //     });
                // }, 60000);
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', reason);
                console.error(`Failed to share code to server.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'share-code-button',
            label: 'ShareCode',
            onClick: shareCode,
            tooltip: 'Share your code to the instructor.',
        });
        panel.toolbar.insertItem(12, 'shareCode', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CellCheckButton": () => (/* binding */ CellCheckButton)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");





const ShareButton = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { type: "button", onClick: () => onClick(), className: "cellButton" },
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: icon, className: "cellButton-icon", tag: "span", width: "15px", height: "15px" })));
const CodeCellButtonComponent = ({ cell, info, }) => {
    const shareCode = async () => {
        if (isNaN(info.problem_id)) {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)('Code Share Error', "Invalid code block. Use specific problem notebook.");
            return;
        }
        // clear message skeleton
        info.message = info.message.replace("## Message to instructor: ", "");
        let postBody = {
            "message": info.message,
            "code": cell.model.value.text,
            "problem_id": info.problem_id,
            "snapshot": 2
        };
        console.log("From widget: ", postBody);
        (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submissions', {
            method: 'POST',
            body: JSON.stringify(postBody)
        })
            .then(data => {
            if (data.msg === "Submission saved successfully.") {
                if (info.message.length > 27) {
                    data.msg = 'Code & message is sent to the instructor.';
                }
                else {
                    data.msg = 'Code is sent to the instructor.';
                }
            }
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: '',
                body: data.msg,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Ok' })]
            });
            // Keep checking for new feedback.
            // This setInterval will be cleared once the feedback is downloaded (after reload())
            // setInterval(function(){
            //     // console.log("Checking for feedback...")
            //     requestAPI<any>('feedback',{
            //     method: 'GET'
            //     })
            //     .then(data => {
            //         // console.log(data);
            //         if (data['hard-reload'] != -1) {
            //         showDialog({
            //             title:'',
            //             body: data.msg,
            //             buttons: [Dialog.okButton({ label: 'Ok' })]
            //         }).then( result => {
            //             if (result.button.accept ) {
            //                 window.location.reload();
            //             }
            //         })
            //         }
            //     })
            //     .catch(reason => {
            //         showErrorMessage('Get Feedback Error', reason);
            //         console.error(
            //         `Failed to fetch recent feedbacks.\n${reason}`
            //         );
            //     });
            // }, 60000);
        })
            .catch(reason => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)('Code Share Error', reason);
            console.error(`Failed to share code to server.\n${reason}`);
        });
    };
    return (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_2___default().createElement(ShareButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.fileUploadIcon, onClick: () => (shareCode)() })));
};
class CellCheckButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(cell, info) {
        super();
        this.cell = null;
        this.info = null;
        this.cell = cell;
        this.info = info;
        this.addClass('jp-CellButton');
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_2___default().createElement(CodeCellButtonComponent, { cell: this.cell, info: this.info });
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.702cd083cba688e6ae07.js.map