"use strict";
(self["webpackChunkcarpo_student"] = self["webpackChunkcarpo_student"] || []).push([["lib_index_js"],{

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
/* harmony export */   DownloadSolutionButton: () => (/* binding */ DownloadSolutionButton),
/* harmony export */   GetQuestionButton: () => (/* binding */ GetQuestionButton),
/* harmony export */   RegisterButton: () => (/* binding */ RegisterButton),
/* harmony export */   ViewFeedbacksButton: () => (/* binding */ ViewFeedbacksButton),
/* harmony export */   ViewSubmissionStatusButton: () => (/* binding */ ViewSubmissionStatusButton),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _share_code__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./share-code */ "./lib/share-code.js");
/* harmony import */ var _raise_hand_help__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./raise-hand-help */ "./lib/raise-hand-help.js");
/* harmony import */ var _sse_notifications__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./sse-notifications */ "./lib/sse-notifications.js");








// import { GetSolutionButton } from './get-solutions'

/**
 * Initialization data for the carpo-student extension.
 */
const plugin = {
    id: 'carpo-student:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_2__.ISettingRegistry],
    activate: (app, nbTrack, settingRegistry) => {
        console.log('JupyterLab extension carpo-student is activated!');
        // Initialize SSE notifications
        // initializeNotifications();
        const cronTracker = [];
        const debounceTimers = new Map();
        const DEBOUNCE_DELAY = 10000; // 10 seconds delay after user stops typing
        // Debounced function to send code snapshot
        const sendDebouncedSnapshot = (cell, filename, problemId) => {
            const timerId = debounceTimers.get(filename);
            if (timerId) {
                clearTimeout(timerId);
            }
            const newTimerId = window.setTimeout(() => {
                const postBody = {
                    message: '',
                    code: cell.model.sharedModel.getSource(),
                    problem_id: problemId,
                    snapshot: 1
                };
                (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submissions', {
                    method: 'POST',
                    body: JSON.stringify(postBody)
                }).then(data => {
                    console.log('Snapshot sent (debounced).', data);
                }).catch(error => {
                    console.error('Failed to send snapshot:', error);
                });
            }, DEBOUNCE_DELAY);
            debounceTimers.set(filename, newTimerId);
            (0,_sse_notifications__WEBPACK_IMPORTED_MODULE_8__.initializeNotifications)();
        };
        nbTrack.currentChanged.connect(() => {
            // console.log("my tracker: ", tracker);
            const notebookPanel = nbTrack.currentWidget;
            const notebook = nbTrack.currentWidget.content;
            const filename = notebookPanel.context.path;
            // Disable if not inside Exercises directory
            if (!filename.includes('Exercises')) {
                return;
            }
            notebookPanel.context.ready.then(async () => {
                let currentCell = null;
                let currentCellCheckButton = null;
                nbTrack.activeCellChanged.connect(() => {
                    let question;
                    if (currentCell) {
                        notebook.widgets.map((c) => {
                            if (c.model.type === 'code' || c.model.type === 'markdown') {
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
                    const info = {
                        problem_id: parseInt(filename.split('/').pop().replace('ex', '').replace('.ipynb', ''))
                    };
                    // Get the message block referencing the active cell.
                    notebook.widgets.map((c, index) => {
                        // if (c.model.toJSON().source[0].startsWith('## Message to instructor:')) {
                        //   info.message = c.model.value.text;
                        // }
                        if (index === activeIndex) {
                            question = c.model.sharedModel.getSource();
                            if (question.includes('## PID ')) {
                                const newCheckButton = new _widget__WEBPACK_IMPORTED_MODULE_1__.CellCheckButton(cell, info);
                                cell.layout.addWidget(newCheckButton);
                                currentCellCheckButton = newCheckButton;
                                // Setup debounced snapshot sending when cell content changes
                                if (cronTracker.indexOf(filename) === -1) {
                                    // Listen for changes to cell content
                                    c.model.sharedModel.changed.connect(() => {
                                        sendDebouncedSnapshot(c, filename, info.problem_id);
                                    });
                                    cronTracker.push(filename);
                                }
                            }
                        }
                    });
                    currentCell = cell;
                });
            });
        });
        //  tell the document registry about your widget extension:
        app.docRegistry.addWidgetExtension('Notebook', new RegisterButton());
        app.docRegistry.addWidgetExtension('Notebook', new GetQuestionButton());
        app.docRegistry.addWidgetExtension('Notebook', new _raise_hand_help__WEBPACK_IMPORTED_MODULE_7__.RaiseHandHelpButton());
        // app.docRegistry.addWidgetExtension('Notebook', new ViewSubmissionStatusButton());
        app.docRegistry.addWidgetExtension('Notebook', new ViewFeedbacksButton());
        app.docRegistry.addWidgetExtension('Notebook', new DownloadSolutionButton());
        app.docRegistry.addWidgetExtension('Notebook', new _share_code__WEBPACK_IMPORTED_MODULE_6__.ShareCodeButton());
        // app.docRegistry.addWidgetExtension('Notebook', new viewProblemStatusExtension());
        // Add cleanup for notifications when the extension is deactivated
        // Note: JupyterFrontEnd doesn't have a disposed signal, so we'll handle cleanup
        // when the window is unloaded
        window.addEventListener('beforeunload', () => {
            (0,_sse_notifications__WEBPACK_IMPORTED_MODULE_8__.cleanupNotifications)();
        });
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('register', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: '',
                    body: 'Student ' + data.name + ' has been registered.',
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Registration Error', reason);
                console.error(`Failed to register user as Student.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'register-button',
            label: 'Register',
            onClick: register,
            tooltip: 'Register as a Student'
        });
        panel.toolbar.insertItem(10, 'register', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('question', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Get Problem Error', reason);
                console.error(`Failed to get active questions.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'get-question-button',
            label: 'GetProblem',
            onClick: getQuestion,
            tooltip: 'Get Latest Problem From Server'
        });
        panel.toolbar.insertItem(11, 'getQuestion', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('view_student_status', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                window.open(data.url, '_blank');
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('View Status Error', reason);
                console.error(`Failed to view student submission status.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'get-status-button',
            label: 'Status',
            onClick: viewStatus,
            tooltip: 'View your submissions status'
        });
        panel.toolbar.insertItem(13, 'viewStatus', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
// Currently disabled
class ViewFeedbacksButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        // Get the notebook filename as unique identifier
        const filename = context.path;
        const notebookName = filename.split('/').pop() || '';
        // Only show the feedback button for notebooks starting with 'ex'
        if (!notebookName.startsWith('ex')) {
            // Return an empty disposable for non-exercise notebooks
            return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => { });
        }
        const viewFeedbacks = () => {
            // Check if feedback widget already exists for this filename
            let floatingFeedback = ViewFeedbacksButton.feedbackWidgets.get(filename);
            if (!floatingFeedback) {
                // Create new feedback widget if it doesn't exist
                floatingFeedback = new _widget__WEBPACK_IMPORTED_MODULE_1__.FloatingFeedbackWidget(filename);
                ViewFeedbacksButton.feedbackWidgets.set(filename, floatingFeedback);
                // Add cleanup when widget is closed
                const originalClose = floatingFeedback.close.bind(floatingFeedback);
                floatingFeedback.close = () => {
                    originalClose();
                    ViewFeedbacksButton.feedbackWidgets.delete(filename);
                };
            }
            floatingFeedback.show();
        };
        // Setup cleanup when notebook panel is disposed
        const cleanupFeedback = () => {
            const filename = context.path;
            const widget = ViewFeedbacksButton.feedbackWidgets.get(filename);
            if (widget) {
                widget.close();
                ViewFeedbacksButton.feedbackWidgets.delete(filename);
            }
        };
        // Listen for panel disposal
        panel.disposed.connect(cleanupFeedback);
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'view-feedbacks-button',
            label: 'ViewFeedbacks',
            onClick: viewFeedbacks,
            tooltip: 'View feedback widget'
        });
        panel.toolbar.insertItem(13, 'viewFeedbacks', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
            // Clean up feedback widget when button is disposed
            const filename = context.path;
            const widget = ViewFeedbacksButton.feedbackWidgets.get(filename);
            if (widget) {
                widget.close();
                ViewFeedbacksButton.feedbackWidgets.delete(filename);
            }
        });
    }
}
ViewFeedbacksButton.feedbackWidgets = new Map();
// export class viewProblemStatusExtension
//   implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
// {
//   /**
//    * Create a new extension for the notebook panel widget.
//    *
//    * @param panel Notebook panel
//    * @param context Notebook context
//    * @returns Disposable on the added button
//    */
//   createNew(
//     panel: NotebookPanel,
//     context: DocumentRegistry.IContext<INotebookModel>
//   ): IDisposable {
//     const viewProblemStatus = () => {
//       requestAPI<any>('view_problem_list', {
//         method: 'GET'
//       })
//         .then(data => {
//           console.log(data);
//           window.open(data.url, '_blank');
//         })
//         .catch(reason => {
//           showErrorMessage('View Problem Status Error', reason);
//           console.error(`Failed to view problem status.\n${reason}`);
//         });
//     };
//     const button = new ToolbarButton({
//       className: 'get-status-button',
//       label: 'Problems',
//       onClick: viewProblemStatus,
//       tooltip: 'View all problem status'
//     });
//     panel.toolbar.insertItem(15, 'viewProblemStatus', button);
//     return new DisposableDelegate(() => {
//       button.dispose();
//     });
//   }
// }
class DownloadSolutionButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const downloadSolution = () => {
            const notebook = panel.content;
            const filename = context.path;
            // Only show for exercise notebooks
            if (!filename.includes('Exercises') || !filename.includes('ex')) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Invalid Notebook', 'Solution download is only available for exercise notebooks.');
                return;
            }
            // Extract problem_id from filename (e.g., ex001.ipynb -> 1)
            const match = filename.match(/ex(\d+)\.ipynb/);
            if (!match) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Invalid Filename', 'Cannot extract problem ID from notebook filename.');
                return;
            }
            const problemId = parseInt(match[1]);
            (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)(`solutions/problem/${problemId}`, {
                method: 'GET'
            })
                .then(data => {
                if (data.data.code) {
                    // Create a new code cell with the solution
                    const solutionCode = `# Solution for Problem ${problemId}\n${data.data.code}`;
                    // Move to the last cell first
                    notebook.activeCellIndex = notebook.widgets.length - 1;
                    // Insert a new code cell at the end of the notebook
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.insertBelow(notebook);
                    // Get the newly created cell (should be the last cell now)
                    const activeCell = notebook.activeCell;
                    if (activeCell && activeCell.model.type === 'code') {
                        // Set the source code
                        activeCell.model.sharedModel.setSource(solutionCode);
                    }
                    // Scroll to the new cell
                    notebook.scrollToItem(notebook.widgets.length - 1);
                    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                        title: 'Solution Downloaded',
                        body: `Solution for Problem ${problemId} has been added to your notebook.`,
                        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                    });
                }
                else {
                    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                        title: 'No Solution',
                        body: 'No solution available for this problem.',
                        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                    });
                }
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Download Solution Error', reason);
                console.error(`Failed to download solution.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'download-solution-button',
            label: 'GetSolution',
            onClick: downloadSolution,
            tooltip: 'Download solution for this exercise'
        });
        panel.toolbar.insertItem(14, 'downloadSolution', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/raise-hand-help.js":
/*!********************************!*\
  !*** ./lib/raise-hand-help.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RaiseHandHelpButton: () => (/* binding */ RaiseHandHelpButton)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



class RaiseHandHelpButton {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const raiseHand = () => {
            const notebook = panel.content;
            const filename = panel.context.path;
            const activeIndex = notebook.activeCellIndex;
            let codeBlock;
            const info = {
                problem_id: parseInt(filename.split('/').pop().replace('ex', '').replace('.ipynb', ''))
            };
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    codeBlock = c.model.sharedModel.getSource();
                }
            });
            if (!codeBlock.startsWith('## PID ')) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', 'Invalid cell selected. Use a specific problem cell block.');
                return;
            }
            const postBody = {
                message: info.message,
                code: codeBlock,
                problem_id: info.problem_id,
                snapshot: 1
            };
            console.log('Req body: ', postBody);
            (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('ask_for_help', {
                method: 'POST',
                body: JSON.stringify(postBody)
            })
                .then(data => {
                if (data.msg === 'Submission saved successfully.') {
                    data.msg = 'Code is sent to the instructor.';
                }
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', reason);
                console.error(`Failed to share code to server.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'raise-hand-button',
            label: 'AskForHelp',
            onClick: raiseHand,
            tooltip: 'Ask the instructor to help you.'
        });
        panel.toolbar.insertItem(12, 'AskForHelp', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ }),

/***/ "./lib/share-code.js":
/*!***************************!*\
  !*** ./lib/share-code.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ShareCodeButton: () => (/* binding */ ShareCodeButton)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _sse_notifications__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./sse-notifications */ "./lib/sse-notifications.js");




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
            let codeBlock;
            const info = {
                problem_id: parseInt(filename.split('/').pop().replace('ex', '').replace('.ipynb', ''))
            };
            notebook.widgets.map((c, index) => {
                // if (c.model.toJSON().source[0].text.startsWith('## Message to instructor:')) {
                //   info.message = c.model.value.text;
                // }
                if (index === activeIndex) {
                    // codeBlock = c.model.toJSON().source[0];
                    codeBlock = c.model.sharedModel.getSource();
                    console.log("content: ", codeBlock);
                }
            });
            if (!codeBlock.startsWith('## PID ')) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', 'Invalid cell selected. Use a specific problem cell block.');
                return;
            }
            const postBody = {
                message: info.message,
                code: codeBlock,
                problem_id: info.problem_id,
                snapshot: 2
            };
            // console.log('Req body: ', postBody);
            (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('submissions', {
                method: 'POST',
                body: JSON.stringify(postBody)
            })
                .then(data => {
                if (data.msg === 'Submission saved successfully.') {
                    data.msg = 'Code is sent to the instructor.';
                }
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Code Share Error', reason);
                console.error(`Failed to share code to server.\n${reason}`);
            });
            (0,_sse_notifications__WEBPACK_IMPORTED_MODULE_3__.initializeNotifications)();
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'share-code-button',
            label: 'ShareCode',
            onClick: shareCode,
            tooltip: 'Share your code to the instructor.'
        });
        panel.toolbar.insertItem(15, 'shareCode', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ }),

/***/ "./lib/sse-notifications.js":
/*!**********************************!*\
  !*** ./lib/sse-notifications.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   SSENotificationService: () => (/* binding */ SSENotificationService),
/* harmony export */   ToastNotification: () => (/* binding */ ToastNotification),
/* harmony export */   cleanupNotifications: () => (/* binding */ cleanupNotifications),
/* harmony export */   getSSEService: () => (/* binding */ getSSEService),
/* harmony export */   initializeNotifications: () => (/* binding */ initializeNotifications)
/* harmony export */ });
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
// import { URLExt } from '@jupyterlab/coreutils';
// import { ServerConnection } from '@jupyterlab/services';


async function fetchConfig() {
    try {
        const config = await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)('config', {
            method: 'GET'
        });
        return {
            server: config.server,
            id: config.id
        };
    }
    catch (error) {
        console.error('Failed to fetch config from API:', error);
        // Fallback values
        return {
            server: 'http://127.0.0.1:8081',
            id: '1'
        };
    }
}
class ToastNotification {
    static init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-notification-container';
            this.container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
        max-width: 400px;
      `;
            document.body.appendChild(this.container);
        }
    }
    static show(data) {
        this.init();
        const toast = document.createElement('div');
        const toastId = `toast-${++this.toastCounter}`;
        toast.id = toastId;
        toast.style.cssText = `
      background: ${this.getBackgroundColor(data.type)};
      color: white;
      padding: 12px 16px;
      margin-bottom: 8px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      pointer-events: auto;
      cursor: pointer;
      font-family: var(--jp-ui-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
      font-size: 13px;
      line-height: 1.4;
      min-width: 250px;
      max-width: 400px;
      word-wrap: break-word;
      opacity: 0;
      transform: translateX(100%);
      transition: all 0.3s ease-in-out;
      position: relative;
      border-left: 4px solid ${this.getBorderColor(data.type)};
    `;
        // Create toast content
        const content = document.createElement('div');
        if (data.title) {
            const title = document.createElement('div');
            title.style.cssText = `
        font-weight: 600;
        margin-bottom: 4px;
        font-size: 14px;
      `;
            title.textContent = data.title;
            content.appendChild(title);
        }
        const message = document.createElement('div');
        message.textContent = data.message;
        content.appendChild(message);
        // Add timestamp if provided
        if (data.timestamp) {
            const time = document.createElement('div');
            time.style.cssText = `
        font-size: 11px;
        opacity: 0.8;
        margin-top: 4px;
      `;
            time.textContent = new Date(data.timestamp).toLocaleTimeString();
            content.appendChild(time);
        }
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
      position: absolute;
      top: 8px;
      right: 8px;
      background: none;
      border: none;
      color: white;
      font-size: 16px;
      cursor: pointer;
      padding: 0;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0.7;
      transition: opacity 0.2s;
    `;
        closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
        closeBtn.onmouseout = () => closeBtn.style.opacity = '0.7';
        closeBtn.onclick = () => this.remove(toastId);
        toast.appendChild(content);
        toast.appendChild(closeBtn);
        // Add click to dismiss or open feedback widget
        toast.onclick = (e) => {
            if (e.target !== closeBtn) {
                if (data.filename) {
                    // Open feedback widget if filename is provided
                    this.openFeedbackWidget(data.filename);
                }
                this.remove(toastId);
            }
        };
        this.container.appendChild(toast);
        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (document.getElementById(toastId)) {
                this.remove(toastId);
            }
        }, 30000);
    }
    static getBackgroundColor(type) {
        switch (type) {
            case 'success': return '#4caf50';
            case 'warning': return '#ff9800';
            case 'error': return '#f44336';
            case 'info':
            default: return '#2196f3';
        }
    }
    static getBorderColor(type) {
        switch (type) {
            case 'success': return '#2e7d32';
            case 'warning': return '#f57c00';
            case 'error': return '#d32f2f';
            case 'info':
            default: return '#1976d2';
        }
    }
    static remove(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }
    static openFeedbackWidget(filename) {
        // Check if feedback widget already exists for this filename
        let floatingFeedback = this.feedbackWidgets.get(filename);
        if (!floatingFeedback) {
            // Create new feedback widget if it doesn't exist
            floatingFeedback = new _widget__WEBPACK_IMPORTED_MODULE_0__.FloatingFeedbackWidget(filename);
            this.feedbackWidgets.set(filename, floatingFeedback);
            // Add cleanup when widget is closed
            const originalClose = floatingFeedback.close.bind(floatingFeedback);
            floatingFeedback.close = () => {
                originalClose();
                this.feedbackWidgets.delete(filename);
            };
        }
        floatingFeedback.show();
    }
}
ToastNotification.container = null;
ToastNotification.toastCounter = 0;
ToastNotification.feedbackWidgets = new Map();
class SSENotificationService {
    constructor() {
        this.eventSource = null;
        this.isConnected = false;
        this.reconnectTimeout = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.baseReconnectDelay = 1000;
        // Initialize toast system
        ToastNotification.init();
    }
    async connect() {
        if (this.isConnected || this.eventSource) {
            return;
        }
        try {
            const config = await fetchConfig();
            const sseUrl = `${config.server}/events?user_id=${config.id}`;
            this.eventSource = new EventSource(sseUrl);
            this.eventSource.onopen = () => {
                console.log('SSE connection established to /events');
                this.isConnected = true;
                this.reconnectAttempts = 0;
            };
            this.eventSource.onmessage = (event) => {
                try {
                    // Try to parse as JSON first
                    const data = JSON.parse(event.data);
                    // Handle different message formats
                    let notificationData;
                    console.log(data);
                    if (data && data.student_id === Number(config.id)) {
                        // Derive filename from problem_id if available for Feedbackpanel toggle
                        const filename = data.problem_id ? `Exercises/ex${String(data.problem_id).padStart(3, '0')}.ipynb` : undefined;
                        notificationData = {
                            message: `You have new ${data.event_type}. Click to View`,
                            type: 'info',
                            title: 'New Feedback',
                            timestamp: data.timestamp,
                            filename: filename
                        };
                        ToastNotification.show(notificationData);
                        // If the feedbackpanel is open, hit refresh
                        if (filename) {
                            const existingWidget = ToastNotification.feedbackWidgets.get(filename);
                            if (existingWidget) {
                                existingWidget.refreshFeedback();
                            }
                        }
                    }
                }
                catch (error) {
                    console.error('Failed to parse SSE message:', error);
                    // Show raw message if JSON parsing fails
                    // ToastNotification.show({
                    //   message: event.data,
                    //   type: 'info',
                    //   title: 'New Event',
                    //   timestamp: new Date().toISOString()
                    // });
                }
            };
            this.eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                this.isConnected = false;
                this.handleConnectionError();
            };
            // Listen for specific notification events
            this.eventSource.addEventListener('notify', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    ToastNotification.show(data);
                }
                catch (error) {
                    console.error('Failed to parse notify event:', error);
                }
            });
        }
        catch (error) {
            console.error('Failed to establish SSE connection:', error);
            this.handleConnectionError();
        }
    }
    handleConnectionError() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isConnected = false;
        // Show error notification
        ToastNotification.show({
            message: 'Lost connection to /events endpoint',
            type: 'warning',
            title: 'SSE Connection Lost'
        });
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts);
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            this.reconnectTimeout = window.setTimeout(async () => {
                await this.connect();
            }, delay);
        }
        else {
            ToastNotification.show({
                message: 'Failed to reconnect to /events after multiple attempts',
                type: 'error',
                title: 'SSE Connection Failed'
            });
        }
    }
    disconnect() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isConnected = false;
        this.reconnectAttempts = 0;
    }
    isConnectionActive() {
        return this.isConnected;
    }
}
// Global instance
let sseService = null;
function getSSEService() {
    if (!sseService) {
        sseService = new SSENotificationService();
    }
    return sseService;
}
async function initializeNotifications() {
    const service = getSSEService();
    await service.connect();
}
function cleanupNotifications() {
    if (sseService) {
        sseService.disconnect();
        sseService = null;
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
/* harmony export */   CellCheckButton: () => (/* binding */ CellCheckButton),
/* harmony export */   FeedbackWidgetComponent: () => (/* binding */ FeedbackWidgetComponent),
/* harmony export */   FloatingFeedbackWidget: () => (/* binding */ FloatingFeedbackWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _sse_notifications__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./sse-notifications */ "./lib/sse-notifications.js");






const ShareButton = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { type: "button", onClick: () => onClick(), className: "cellButton" },
    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon.resolveReact, { icon: icon, className: "cellButton-icon", tag: "span", width: "15px", height: "15px" })));
const CodeCellButtonComponent = ({ cell, info }) => {
    const shareCode = async () => {
        if (isNaN(info.problem_id)) {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Code Share Error', 'Invalid code block. Use specific problem notebook.');
            return;
        }
        const postBody = {
            message: info.message,
            code: cell.model.sharedModel.getSource(),
            problem_id: info.problem_id,
            snapshot: 2
        };
        // console.log('From widget: ', postBody);
        (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('submissions', {
            method: 'POST',
            body: JSON.stringify(postBody)
        })
            .then(data => {
            if (data.msg === 'Submission saved successfully.') {
                data.msg = 'Code is sent to the instructor.';
            }
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                title: '',
                body: data.msg,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
            });
        })
            .catch(reason => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Code Share Error', reason);
            console.error(`Failed to share code to server.\n${reason}`);
        });
        (0,_sse_notifications__WEBPACK_IMPORTED_MODULE_4__.initializeNotifications)();
    };
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(ShareButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.fileUploadIcon, onClick: () => shareCode() })));
};
class FloatingFeedbackWidget {
    constructor(filename) {
        this.isDragging = false;
        this.isResizing = false;
        this.resizeCorner = null;
        this.dragOffset = { x: 0, y: 0 };
        this.resizeOffset = { x: 0, y: 0 };
        this.position = { x: 0, y: 50 }; // Will be calculated in setupContainer
        this.size = { width: 550, height: 400 };
        this.minSize = { width: 250, height: 200 };
        this.isLoading = false;
        this.panelId = filename || `feedback-${Date.now()}`;
        this.filename = filename || 'Unknown';
        this.node = document.createElement('div');
        this.setupContainer();
        this.setupEventListeners();
        this.createContent();
        this.fetchFeedbackContent();
    }
    setupContainer() {
        // Find the main content container similar to StickyLand
        this.container = document.querySelector('#jp-main-content-panel');
        if (!this.container) {
            this.container = document.querySelector('#main-panel');
        }
        if (!this.container) {
            this.container = document.body;
        }
        // Calculate bottom-right position
        const containerWidth = this.container.clientWidth || window.innerWidth;
        const containerHeight = this.container.clientHeight || window.innerHeight;
        this.position.x = containerWidth - this.size.width - 20; // 20px margin from right edge
        this.position.y = containerHeight - this.size.height - 40;
        ; // 20px from bottom
        // Setup the floating window styles
        this.node.classList.add('floating-feedback-window');
        // Use filename as unique identifier, sanitize for valid DOM ID
        const sanitizedId = this.panelId.replace(/[^a-zA-Z0-9-_]/g, '-');
        this.node.id = `floating-feedback-${sanitizedId}`;
        this.node.style.position = 'absolute';
        this.node.style.left = `${this.position.x}px`;
        this.node.style.top = `${this.position.y}px`;
        this.node.style.width = `${this.size.width}px`;
        this.node.style.height = `${this.size.height}px`;
        this.node.style.zIndex = '1000';
        this.node.style.backgroundColor = '#ffffff';
        this.node.style.border = '1px solid #0078d4';
        this.node.style.borderRadius = '8px';
        this.node.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        this.node.style.display = 'flex';
        this.node.style.flexDirection = 'column';
        this.node.style.overflow = 'hidden';
        this.node.style.fontFamily = 'var(--jp-ui-font-family)';
        this.node.style.fontSize = '13px';
        this.node.style.resize = 'none'; // Disable browser default resize
        // Add resize handle
        this.createResizeHandle();
    }
    createContent() {
        var _a;
        // Create header
        const header = document.createElement('div');
        header.classList.add('feedback-header');
        header.style.padding = '12px';
        header.style.backgroundColor = '#0078d4';
        header.style.color = 'white';
        header.style.cursor = 'grab';
        header.style.userSelect = 'none';
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.borderRadius = '8px 8px 0 0';
        const title = document.createElement('span');
        // Extract just the filename from the full path
        const displayName = ((_a = this.filename.split('/').pop()) === null || _a === void 0 ? void 0 : _a.replace('.ipynb', '')) || 'Unknown';
        title.textContent = `📝 Feedback On ${displayName}`;
        title.style.fontWeight = '600';
        title.style.fontSize = '14px';
        // Create button container for refresh and close buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '4px';
        // Refresh button
        const refreshButton = document.createElement('button');
        refreshButton.textContent = '🔄';
        refreshButton.style.background = 'none';
        refreshButton.style.border = 'none';
        refreshButton.style.color = 'white';
        refreshButton.style.fontSize = '14px';
        refreshButton.style.cursor = 'pointer';
        refreshButton.style.padding = '0';
        refreshButton.style.width = '20px';
        refreshButton.style.height = '20px';
        refreshButton.style.borderRadius = '50%';
        refreshButton.style.display = 'flex';
        refreshButton.style.alignItems = 'center';
        refreshButton.style.justifyContent = 'center';
        refreshButton.title = 'Refresh feedback';
        refreshButton.addEventListener('click', () => this.refreshFeedback());
        refreshButton.addEventListener('mouseenter', () => {
            refreshButton.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        });
        refreshButton.addEventListener('mouseleave', () => {
            refreshButton.style.backgroundColor = 'transparent';
        });
        // Close button
        const closeButton = document.createElement('button');
        closeButton.textContent = '×';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.style.color = 'white';
        closeButton.style.fontSize = '18px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.padding = '0';
        closeButton.style.width = '20px';
        closeButton.style.height = '20px';
        closeButton.style.borderRadius = '50%';
        closeButton.style.display = 'flex';
        closeButton.style.alignItems = 'center';
        closeButton.style.justifyContent = 'center';
        closeButton.title = 'Close feedback';
        closeButton.addEventListener('click', () => this.close());
        closeButton.addEventListener('mouseenter', () => {
            closeButton.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        });
        closeButton.addEventListener('mouseleave', () => {
            closeButton.style.backgroundColor = 'transparent';
        });
        buttonContainer.appendChild(refreshButton);
        buttonContainer.appendChild(closeButton);
        header.appendChild(title);
        header.appendChild(buttonContainer);
        // Create content area
        const content = document.createElement('div');
        content.classList.add('feedback-content');
        content.style.flex = '1';
        content.style.padding = '4px';
        content.style.overflow = 'auto';
        content.style.backgroundColor = '#ffffff';
        this.contentElement = content;
        this.node.appendChild(header);
        this.node.appendChild(content);
    }
    createResizeHandle() {
        const corners = [
            { corner: 'nw', top: '0', left: '0', cursor: 'nw-resize', title: 'Resize from top-left' },
            { corner: 'ne', top: '0', right: '0', cursor: 'ne-resize', title: 'Resize from top-right' },
            { corner: 'sw', bottom: '0', left: '0', cursor: 'sw-resize', title: 'Resize from bottom-left' },
            { corner: 'se', bottom: '0', right: '0', cursor: 'se-resize', title: 'Resize from bottom-right' }
        ];
        corners.forEach(({ corner, cursor, title, ...position }) => {
            const resizeHandle = document.createElement('div');
            resizeHandle.classList.add('feedback-resize-handle', `resize-${corner}`);
            resizeHandle.dataset.corner = corner;
            resizeHandle.style.position = 'absolute';
            resizeHandle.style.width = '15px';
            resizeHandle.style.height = '15px';
            resizeHandle.style.cursor = cursor;
            resizeHandle.style.opacity = '0.7';
            resizeHandle.style.zIndex = '10';
            resizeHandle.title = title;
            // Set position based on corner
            Object.entries(position).forEach(([key, value]) => {
                if (value !== undefined) {
                    resizeHandle.style[key] = value;
                }
            });
            // Corner-specific styling
            const gradientMap = {
                'nw': 'linear-gradient(315deg, transparent 30%, #0078d4 30%, #0078d4 60%, transparent 60%)',
                'ne': 'linear-gradient(225deg, transparent 30%, #0078d4 30%, #0078d4 60%, transparent 60%)',
                'sw': 'linear-gradient(45deg, transparent 30%, #0078d4 30%, #0078d4 60%, transparent 60%)',
                'se': 'linear-gradient(135deg, transparent 30%, #0078d4 30%, #0078d4 60%, transparent 60%)'
            };
            resizeHandle.style.background = gradientMap[corner];
            resizeHandle.style.backgroundSize = '8px 8px';
            // Add hover effect
            resizeHandle.addEventListener('mouseenter', () => {
                resizeHandle.style.opacity = '1';
            });
            resizeHandle.addEventListener('mouseleave', () => {
                resizeHandle.style.opacity = '0.7';
            });
            this.node.appendChild(resizeHandle);
        });
    }
    async fetchFeedbackContent() {
        this.isLoading = true;
        this.showLoadingState();
        try {
            // Extract problem ID from filename (e.g., "ex001.ipynb" -> "1")
            const problemId = this.extractProblemId(this.filename);
            const resp = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)(`widget-feedback?problem_id=${problemId}`, {
                method: 'GET'
            });
            this.showFeedbackContent(resp.data || 'No feedback available');
        }
        catch (error) {
            console.error('Failed to fetch feedback:', error);
            this.showErrorState(error);
        }
        finally {
            this.isLoading = false;
        }
    }
    extractProblemId(filename) {
        // Extract filename from path (e.g., "Exercises/ex001.ipynb" -> "ex001.ipynb")
        const basename = filename.split('/').pop() || '';
        // Extract number from filename (e.g., "ex001.ipynb" -> "001")
        const match = basename.match(/ex(\d+)\.ipynb$/);
        if (match) {
            return parseInt(match[1], 10); // Convert "001" to 1
        }
        // Fallback to 1 if no match found
        return 1;
    }
    showLoadingState() {
        this.contentElement.innerHTML = '';
        const loadingDiv = document.createElement('div');
        loadingDiv.style.textAlign = 'center';
        loadingDiv.style.color = '#666';
        loadingDiv.style.fontSize = '13px';
        loadingDiv.style.padding = '20px';
        loadingDiv.innerHTML = '🔄 Loading feedback...';
        this.contentElement.appendChild(loadingDiv);
    }
    showFeedbackContent(data) {
        this.contentElement.innerHTML = '';
        // Handle array of feedback objects
        if (Array.isArray(data)) {
            this.createChatMessages(data);
        }
        else {
            // Handle single feedback object or no data
            const feedbackDiv = document.createElement('div');
            feedbackDiv.style.fontSize = '14px';
            feedbackDiv.style.color = '#666';
            feedbackDiv.style.textAlign = 'center';
            feedbackDiv.style.padding = '20px';
            feedbackDiv.textContent = 'No feedback available';
            this.contentElement.appendChild(feedbackDiv);
        }
    }
    createChatMessages(feedbackArray) {
        const chatContainer = document.createElement('div');
        chatContainer.style.display = 'flex';
        chatContainer.style.flexDirection = 'column';
        chatContainer.style.gap = '12px';
        chatContainer.style.padding = '8px';
        feedbackArray.forEach((feedback, index) => {
            const messageDiv = this.createChatMessage(feedback, index);
            chatContainer.appendChild(messageDiv);
        });
        this.contentElement.appendChild(chatContainer);
    }
    createChatMessage(feedback, index) {
        const messageContainer = document.createElement('div');
        messageContainer.style.display = 'flex';
        messageContainer.style.flexDirection = 'column';
        messageContainer.style.marginBottom = '8px';
        // Message bubble
        const messageBubble = document.createElement('div');
        messageBubble.style.backgroundColor = '#e3f2fd';
        messageBubble.style.border = '1px solid #2196f3';
        messageBubble.style.borderRadius = '12px';
        messageBubble.style.padding = '12px';
        messageBubble.style.fontSize = '13px';
        messageBubble.style.lineHeight = '1.4';
        messageBubble.style.wordWrap = 'break-word';
        messageBubble.style.maxWidth = '100%';
        messageBubble.style.position = 'relative';
        // Feedback content
        if (feedback.code) {
            const feedbackContent = document.createElement('pre');
            feedbackContent.style.marginBottom = '12px';
            feedbackContent.style.fontSize = '13px';
            feedbackContent.style.lineHeight = '1.4';
            feedbackContent.style.color = '#333';
            feedbackContent.style.whiteSpace = "pre-wrap";
            feedbackContent.innerHTML = feedback.code;
            messageBubble.appendChild(feedbackContent);
        }
        // Footer with star rating and timestamp
        const footer = document.createElement('div');
        footer.style.display = 'flex';
        footer.style.justifyContent = 'space-between';
        footer.style.alignItems = 'center';
        footer.style.marginTop = '8px';
        footer.style.paddingTop = '4px';
        footer.style.borderTop = '1px solid #eee';
        // Upvote/Downvote on the left
        const votingButtons = this.createVotingButtons(feedback.id || `${index}`);
        footer.appendChild(votingButtons);
        // Timestamp on the right
        const timestamp = document.createElement('div');
        timestamp.style.fontSize = '11px';
        timestamp.style.color = '#666';
        timestamp.style.opacity = '0.7';
        if (feedback.feedback_at) {
            // Format timestamp nicely
            const date = new Date(feedback.feedback_at);
            const timeString = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            timestamp.textContent = timeString;
        }
        else {
            timestamp.textContent = `Message ${index + 1}`;
        }
        footer.appendChild(timestamp);
        messageBubble.appendChild(footer);
        messageContainer.appendChild(messageBubble);
        return messageContainer;
    }
    showErrorState(error) {
        this.contentElement.innerHTML = '';
        const errorDiv = document.createElement('div');
        errorDiv.style.color = '#d73a49';
        errorDiv.style.fontSize = '13px';
        errorDiv.style.padding = '20px';
        errorDiv.style.textAlign = 'center';
        const errorMessage = (error === null || error === void 0 ? void 0 : error.message) || error || 'Failed to load feedback';
        errorDiv.innerHTML = `⚠️ Error loading feedback<br><small>${errorMessage}</small>`;
        const retryButton = document.createElement('button');
        retryButton.textContent = '🔄 Retry';
        retryButton.style.marginTop = '10px';
        retryButton.style.padding = '5px 10px';
        retryButton.style.backgroundColor = '#0078d4';
        retryButton.style.color = 'white';
        retryButton.style.border = 'none';
        retryButton.style.borderRadius = '4px';
        retryButton.style.cursor = 'pointer';
        retryButton.style.fontSize = '12px';
        retryButton.addEventListener('click', () => this.fetchFeedbackContent());
        errorDiv.appendChild(document.createElement('br'));
        errorDiv.appendChild(retryButton);
        this.contentElement.appendChild(errorDiv);
    }
    setupEventListeners() {
        this.node.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', () => this.handleMouseUp());
    }
    handleMouseDown(e) {
        const target = e.target;
        // Check for resize handle
        if (target.classList.contains('feedback-resize-handle')) {
            this.isResizing = true;
            this.resizeCorner = target.dataset.corner;
            const rect = this.node.getBoundingClientRect();
            // Set resize offset based on corner
            switch (this.resizeCorner) {
                case 'nw':
                    this.resizeOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top };
                    break;
                case 'ne':
                    this.resizeOffset = { x: e.clientX - (rect.left + rect.width), y: e.clientY - rect.top };
                    break;
                case 'sw':
                    this.resizeOffset = { x: e.clientX - rect.left, y: e.clientY - (rect.top + rect.height) };
                    break;
                case 'se':
                    this.resizeOffset = { x: e.clientX - (rect.left + rect.width), y: e.clientY - (rect.top + rect.height) };
                    break;
            }
            e.preventDefault();
            e.stopPropagation();
            return;
        }
        // Check for header (drag functionality)
        if (target.classList.contains('feedback-header') || target.closest('.feedback-header')) {
            this.isDragging = true;
            const rect = this.node.getBoundingClientRect();
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            this.node.style.cursor = 'grabbing';
            const header = this.node.querySelector('.feedback-header');
            if (header)
                header.style.cursor = 'grabbing';
        }
    }
    handleMouseMove(e) {
        if (this.isResizing && this.resizeCorner) {
            const containerRect = this.container.getBoundingClientRect();
            const mouseX = e.clientX - containerRect.left;
            const mouseY = e.clientY - containerRect.top;
            let newX = this.position.x;
            let newY = this.position.y;
            let newWidth = this.size.width;
            let newHeight = this.size.height;
            switch (this.resizeCorner) {
                case 'nw':
                    // Top-left corner: resize from top-left
                    newWidth = Math.max(this.minSize.width, this.position.x + this.size.width - (mouseX - this.resizeOffset.x));
                    newHeight = Math.max(this.minSize.height, this.position.y + this.size.height - (mouseY - this.resizeOffset.y));
                    newX = Math.min(this.position.x + this.size.width - this.minSize.width, mouseX - this.resizeOffset.x);
                    newY = Math.min(this.position.y + this.size.height - this.minSize.height, mouseY - this.resizeOffset.y);
                    break;
                case 'ne':
                    // Top-right corner: resize from top-right
                    newWidth = Math.max(this.minSize.width, mouseX - this.position.x - this.resizeOffset.x);
                    newHeight = Math.max(this.minSize.height, this.position.y + this.size.height - (mouseY - this.resizeOffset.y));
                    newY = Math.min(this.position.y + this.size.height - this.minSize.height, mouseY - this.resizeOffset.y);
                    break;
                case 'sw':
                    // Bottom-left corner: resize from bottom-left
                    newWidth = Math.max(this.minSize.width, this.position.x + this.size.width - (mouseX - this.resizeOffset.x));
                    newHeight = Math.max(this.minSize.height, mouseY - this.position.y - this.resizeOffset.y);
                    newX = Math.min(this.position.x + this.size.width - this.minSize.width, mouseX - this.resizeOffset.x);
                    break;
                case 'se':
                    // Bottom-right corner: resize from bottom-right
                    newWidth = Math.max(this.minSize.width, mouseX - this.position.x - this.resizeOffset.x);
                    newHeight = Math.max(this.minSize.height, mouseY - this.position.y - this.resizeOffset.y);
                    break;
            }
            // Apply boundary constraints
            newX = Math.max(0, Math.min(newX, this.container.clientWidth - newWidth));
            newY = Math.max(0, Math.min(newY, this.container.clientHeight - newHeight));
            newWidth = Math.min(newWidth, this.container.clientWidth - newX);
            newHeight = Math.min(newHeight, this.container.clientHeight - newY);
            this.position = { x: newX, y: newY };
            this.size = { width: newWidth, height: newHeight };
            this.node.style.left = `${newX}px`;
            this.node.style.top = `${newY}px`;
            this.node.style.width = `${newWidth}px`;
            this.node.style.height = `${newHeight}px`;
            return;
        }
        if (this.isDragging) {
            const containerRect = this.container.getBoundingClientRect();
            const newX = Math.max(0, Math.min(this.container.clientWidth - this.size.width, e.clientX - containerRect.left - this.dragOffset.x));
            const newY = Math.max(0, Math.min(this.container.clientHeight - this.size.height, e.clientY - containerRect.top - this.dragOffset.y));
            this.position = { x: newX, y: newY };
            this.node.style.left = `${newX}px`;
            this.node.style.top = `${newY}px`;
        }
    }
    handleMouseUp() {
        if (this.isDragging) {
            this.isDragging = false;
            this.node.style.cursor = 'default';
            const header = this.node.querySelector('.feedback-header');
            if (header)
                header.style.cursor = 'grab';
        }
        if (this.isResizing) {
            this.isResizing = false;
            this.resizeCorner = null;
        }
    }
    show() {
        if (!this.node.parentElement) {
            this.container.appendChild(this.node);
            // Recalculate position in case container size changed
            const containerWidth = this.container.clientWidth || window.innerWidth;
            this.position.x = containerWidth - this.size.width - 20;
            this.node.style.left = `${this.position.x}px`;
        }
        this.node.style.display = 'flex';
        // Refresh feedback content when shown
        if (!this.isLoading) {
            this.fetchFeedbackContent();
        }
    }
    close() {
        if (this.node.parentElement) {
            this.node.parentElement.removeChild(this.node);
        }
    }
    hide() {
        this.node.style.display = 'none';
    }
    refreshFeedback() {
        if (!this.isLoading) {
            this.fetchFeedbackContent();
        }
    }
    createVotingButtons(feedbackId) {
        const voteContainer = document.createElement('div');
        voteContainer.style.display = 'flex';
        voteContainer.style.gap = '8px';
        voteContainer.style.alignItems = 'center';
        voteContainer.dataset.feedbackId = feedbackId;
        // Create upvote button
        const upvoteBtn = document.createElement('button');
        upvoteBtn.textContent = '👍';
        upvoteBtn.style.fontSize = '16px';
        upvoteBtn.style.cursor = 'pointer';
        upvoteBtn.style.border = 'none';
        upvoteBtn.style.background = 'none';
        upvoteBtn.style.padding = '2px 4px';
        upvoteBtn.style.borderRadius = '4px';
        upvoteBtn.style.transition = 'background-color 0.2s ease';
        upvoteBtn.dataset.vote = '1';
        // Create downvote button
        const downvoteBtn = document.createElement('button');
        downvoteBtn.textContent = '👎';
        downvoteBtn.style.fontSize = '16px';
        downvoteBtn.style.cursor = 'pointer';
        downvoteBtn.style.border = 'none';
        downvoteBtn.style.background = 'none';
        downvoteBtn.style.padding = '2px 4px';
        downvoteBtn.style.borderRadius = '4px';
        downvoteBtn.style.transition = 'background-color 0.2s ease';
        downvoteBtn.dataset.vote = '-1';
        // Add hover effects
        upvoteBtn.addEventListener('mouseenter', () => {
            upvoteBtn.style.backgroundColor = 'rgba(34, 197, 94, 0.2)'; // Light green
        });
        upvoteBtn.addEventListener('mouseleave', () => {
            if (voteContainer.dataset.currentVote !== '1') {
                upvoteBtn.style.backgroundColor = 'transparent';
            }
        });
        downvoteBtn.addEventListener('mouseenter', () => {
            downvoteBtn.style.backgroundColor = 'rgba(239, 68, 68, 0.2)'; // Light red
        });
        downvoteBtn.addEventListener('mouseleave', () => {
            if (voteContainer.dataset.currentVote !== '-1') {
                downvoteBtn.style.backgroundColor = 'transparent';
            }
        });
        // Add click handlers
        upvoteBtn.addEventListener('click', () => {
            this.setVote(voteContainer, 1, feedbackId);
        });
        downvoteBtn.addEventListener('click', () => {
            this.setVote(voteContainer, -1, feedbackId);
        });
        voteContainer.appendChild(upvoteBtn);
        voteContainer.appendChild(downvoteBtn);
        // Load existing vote if any
        this.loadExistingVote(voteContainer, feedbackId);
        return voteContainer;
    }
    updateVoteButtons(container, vote) {
        const upvoteBtn = container.querySelector('[data-vote="1"]');
        const downvoteBtn = container.querySelector('[data-vote="-1"]');
        // Reset both buttons
        upvoteBtn.style.backgroundColor = 'transparent';
        downvoteBtn.style.backgroundColor = 'transparent';
        // Highlight the selected vote
        if (vote === 1) {
            upvoteBtn.style.backgroundColor = 'rgba(34, 197, 94, 0.3)'; // Green for upvote
        }
        else if (vote === -1) {
            downvoteBtn.style.backgroundColor = 'rgba(239, 68, 68, 0.3)'; // Red for downvote
        }
    }
    setVote(container, vote, feedbackId) {
        const currentVote = parseInt(container.dataset.currentVote || '0');
        // If clicking the same vote, remove it (toggle off)
        if (currentVote === vote) {
            container.dataset.currentVote = '0';
            this.updateVoteButtons(container, 0);
            localStorage.removeItem(`feedback_vote_${feedbackId}`);
            console.log(`Removed vote for feedback ${feedbackId}`);
            // Save removal to server (vote = 0)
            this.saveVoteToServer(feedbackId, 0);
        }
        else {
            // Set new vote
            container.dataset.currentVote = vote.toString();
            this.updateVoteButtons(container, vote);
            // Store vote in localStorage for persistence
            const storageKey = `feedback_vote_${feedbackId}`;
            localStorage.setItem(storageKey, vote.toString());
            console.log(`${vote === 1 ? 'Upvoted' : 'Downvoted'} feedback ${feedbackId}`);
            // Save vote to server
            this.saveVoteToServer(feedbackId, vote);
        }
    }
    loadExistingVote(container, feedbackId) {
        const storageKey = `feedback_vote_${feedbackId}`;
        const existingVote = localStorage.getItem(storageKey);
        if (existingVote) {
            const vote = parseInt(existingVote);
            container.dataset.currentVote = vote.toString();
            this.updateVoteButtons(container, vote);
        }
    }
    async saveVoteToServer(feedbackId, vote) {
        try {
            const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)(`feedback-ratings`, {
                method: 'PUT',
                body: JSON.stringify({ id: feedbackId, rating: vote })
            });
            console.log('Vote saved to server:', response);
        }
        catch (error) {
            console.error('Failed to save vote to server:', error);
            // Could show a toast notification here if needed
        }
    }
}
// Keep the ReactWidget for backward compatibility if needed
const FeedbackWidget = () => {
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#f8f9fa',
            fontFamily: 'var(--jp-ui-font-family)',
            fontSize: '13px'
        } },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
                padding: '12px',
                backgroundColor: '#0078d4',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                borderBottom: '1px solid #ccc'
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("span", { style: { fontWeight: '600', fontSize: '14px' } }, "\uD83D\uDCDD Feedback")),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
                flex: 1,
                padding: '16px',
                overflow: 'auto',
                backgroundColor: '#ffffff'
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("p", { style: { margin: '0 0 12px 0', fontSize: '14px', color: '#333' } }, "Your feedback will appear here..."))));
};
class FeedbackWidgetComponent extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor() {
        super();
        this.addClass('jp-FeedbackWidget');
        this.id = 'carpo-feedback-widget';
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_1___default().createElement(FeedbackWidget, null);
    }
}
class CellCheckButton extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(cell, info) {
        super();
        this.cell = null;
        this.info = null;
        this.cell = cell;
        this.info = info;
        this.addClass('jp-CellButton');
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(CodeCellButtonComponent, { cell: this.cell, info: this.info }));
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.645f26d5c0758a65bf9e.js.map