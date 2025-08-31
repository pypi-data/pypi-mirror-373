"use strict";
(self["webpackChunkcarpo_teacher"] = self["webpackChunkcarpo_teacher"] || []).push([["lib_index_js"],{

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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'carpo-teacher', // API Namespace
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
/* harmony export */   "AllSubmissionButtonExtension": () => (/* binding */ AllSubmissionButtonExtension),
/* harmony export */   "ArchiveProblemButtonExtension": () => (/* binding */ ArchiveProblemButtonExtension),
/* harmony export */   "NewSubmissionButtonExtension": () => (/* binding */ NewSubmissionButtonExtension),
/* harmony export */   "PublishProblemButtonExtension": () => (/* binding */ PublishProblemButtonExtension),
/* harmony export */   "RegisterButton": () => (/* binding */ RegisterButton),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   "viewProblemStatusExtension": () => (/* binding */ viewProblemStatusExtension)
/* harmony export */ });
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);




// import { Cell } from '@jupyterlab/cells';


/**
 * Initialization data for the carpo-teacher extension.
 */
const plugin = {
    id: 'carpo-teacher:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    optional: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_1__.IFileBrowserFactory],
    activate: (app, nbTrack, browserFactory, docManager) => {
        console.log('JupyterLab extension carpo-teacher is activated!');
        nbTrack.currentChanged.connect(() => {
            const notebookPanel = nbTrack.currentWidget;
            const notebook = nbTrack.currentWidget.content;
            // If current Notebook is not inside Carpo/problem_ directory, disable all functionality.
            if (!nbTrack.currentWidget.context.path.includes("problem_")) {
                return;
            }
            notebookPanel.context.ready.then(async () => {
                let currentCell = null;
                let currentCellCheckButton = null;
                nbTrack.activeCellChanged.connect(() => {
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
                    // const heading = cell.model.value.text.split("\n")[0].split(" ")
                    const submission_id = function (text) {
                        return Number(text.split("\n")[0].split(" ")[2]);
                    };
                    const problem_id = function (text) {
                        return Number(text.split("\n")[0].split(" ")[1]);
                    };
                    const student_id = function (text) {
                        return Number((text.split("\n")[0].split(" ")[0]).replace("#", ""));
                    };
                    var info = {
                        id: submission_id(cell.model.value.text),
                        problem_id: problem_id(cell.model.value.text),
                        student_id: student_id(cell.model.value.text),
                        code: cell.model.value.text.split("\n")[1],
                    };
                    var header;
                    // For feedback case: cell is markdown so loop over the notebook widgets to get code cell before the active cell index
                    if (cell.model.type == 'markdown') {
                        notebook.widgets.map((c, index) => {
                            if (index == activeIndex - 1) {
                                const code = c.model.value.text;
                                info.code = code;
                                info.id = submission_id(code);
                                info.student_id = student_id(code);
                                info.problem_id = problem_id(code);
                            }
                        });
                    }
                    header = cell.model.value.text.split("\n")[0];
                    if (header.match(/^#[0-9]+ [0-9]+ [0-9]+$/)) {
                        console.log("Submission Grading block.........");
                        const newCheckButton = new _widget__WEBPACK_IMPORTED_MODULE_4__.CellCheckButton(cell, info);
                        cell.layout.addWidget(newCheckButton);
                        currentCell = cell;
                        currentCellCheckButton = newCheckButton;
                    }
                    else {
                        const newFeedbackButton = new _widget__WEBPACK_IMPORTED_MODULE_4__.FeedbackButton(cell, info);
                        cell.layout.addWidget(newFeedbackButton);
                        currentCell = cell;
                        currentCellCheckButton = newFeedbackButton;
                    }
                    // if (question.includes("## PID ")){
                    //   (cell.layout as PanelLayout).addWidget(newCheckButton);
                    //   currentCellCheckButton = newCheckButton;
                    // }
                    // Set the current cell and button for future
                    // reference
                });
            });
        });
        //  tell the document registry about your widget extension:
        app.docRegistry.addWidgetExtension('Notebook', new RegisterButton());
        app.docRegistry.addWidgetExtension('Notebook', new NewSubmissionButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new AllSubmissionButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new PublishProblemButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new ArchiveProblemButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new viewProblemStatusExtension());
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('register', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: '',
                    body: "Teacher " + data.name + " has been registered.",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Registration Error', reason);
                console.error(`Failed to register user as Teacher.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'register-button',
            label: 'Register Carpo',
            onClick: register,
            tooltip: 'Register as a Teacher',
        });
        panel.toolbar.insertItem(10, 'register', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class NewSubmissionButtonExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const getSubmissions = () => {
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.clearAllOutputs(panel.content);
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('submissions', {
                method: 'GET'
            })
                .then(data => {
                if (data.Remaining != 0) {
                    var msg = "Notebook " + data.sub_file + " is placed in folder Problem_" + data.question + ". There are " + data.remaining + " submissions in the queue.";
                }
                else {
                    var msg = "You have got 0 submissions. Please check again later.\n";
                }
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: 'Submission Status',
                    body: msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
                console.log(data);
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Get Student Code Error', reason);
                console.error(`Failed to get student's code from the server. Please check your connection.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'sync-code-button',
            label: 'New Submission',
            onClick: getSubmissions,
            tooltip: 'Get new submissions from students.',
        });
        panel.toolbar.insertItem(11, 'getStudentsCode', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class AllSubmissionButtonExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const getGradedSubmissions = () => {
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.clearAllOutputs(panel.content);
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('graded_submissions', {
                method: 'GET'
            })
                .then(data => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: '',
                    body: data.msg,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
                console.log(data);
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Get Graded Submissions Error', reason);
                console.error(`Failed to get student's code from the server. Please check your connection.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'sync-code-button',
            label: 'Graded Subs',
            onClick: getGradedSubmissions,
            tooltip: 'Get all graded submissions.',
        });
        panel.toolbar.insertItem(12, 'getAllGradedSubmissions', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class PublishProblemButtonExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const publishProblem = () => {
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.clearAllOutputs(panel.content);
            const notebook = panel.content;
            const activeIndex = notebook.activeCellIndex;
            var problem;
            var format;
            var header;
            var time_limit;
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    problem = c.model.value.text;
                    format = c.model.type;
                }
            });
            if (problem.includes("#PID:")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Publish Question Error', "Problem already published.");
                return;
            }
            if (!problem) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Publish Question Error', "Problem is empty.");
                return;
            }
            header = problem.split('\n')[0];
            if (header.match(/[0-9]+[a-zA-Z]/)) {
                time_limit = header.match(/[0-9]+[a-zA-Z]/)[0];
            }
            let postBody = {
                "question": problem,
                "format": format,
                "time_limit": time_limit
            };
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('problem', {
                method: 'POST',
                body: JSON.stringify(postBody)
            })
                .then(data => {
                console.log(data);
                notebook.widgets.map((c, index) => {
                    if (index === activeIndex) {
                        c.model.value.text = "#PID:" + data.id + "\n" + problem;
                    }
                });
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: 'New Questions Published',
                    body: 'Problem ' + data.id + " is published.",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Publish Question Error', reason);
                console.error(`Failed to publish question to the server.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'publish-problem-button',
            label: 'Publish',
            onClick: publishProblem,
            tooltip: 'Publish New Problem.',
        });
        panel.toolbar.insertItem(13, 'publishNewProblem', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class ArchiveProblemButtonExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const archiveProblem = () => {
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.clearAllOutputs(panel.content);
            const notebook = panel.content;
            const activeIndex = notebook.activeCellIndex;
            var problem;
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    problem = c.model.value.text;
                }
            });
            if (!problem.includes("#PID:")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Unpublish Question Error', "Active problem not found.");
                return;
            }
            var problem_id = parseInt((problem.split("\n")[0]).split("#PID:")[1]);
            let body = {
                "problem_id": problem_id
            };
            (0,_handler__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('problem', {
                method: 'DELETE',
                body: JSON.stringify(body)
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showDialog)({
                    title: 'Question Unpublished',
                    body: 'Problem id ' + problem_id + ' is  unpublished.',
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)('Unpublish Question Error', reason);
                console.error(`Failed to unpublish question.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            className: 'archive-problem-button',
            label: 'Unpublish',
            onClick: archiveProblem,
            tooltip: 'Unpublish the problem.',
        });
        panel.toolbar.insertItem(14, 'archivesProblem', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
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

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CellCheckButton": () => (/* binding */ CellCheckButton),
/* harmony export */   "FeedbackButton": () => (/* binding */ FeedbackButton)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");





const GradeButton = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { type: "button", onClick: () => onClick(), className: "cellButton" },
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: icon, className: "cellButton-icon", tag: "span", width: "15px", height: "15px" })));
const ResetButton = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { type: "button", onClick: () => onClick(), className: "cellButton" },
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: icon, className: "cellButton-icon", tag: "span", width: "15px", height: "15px" })));
const SendButton = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { type: "button", onClick: () => onClick(), className: "cellButton" },
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon.resolveReact, { icon: icon, className: "cellButton-icon", tag: "span", width: "15px", height: "15px" })));
const CodeCellButtonComponent = ({ cell, info, }) => {
    const submitGrade = async (val) => {
        console.log("From widget: ", info);
        if (info.id == NaN) {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Grading Error',
                body: "Invalid Cell for grading.",
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Ok' })]
            });
            return;
        }
        let postBody = {
            "student_id": info.student_id,
            "submission_id": info.id,
            "problem_id": info.problem_id,
            "score": val ? 1 : 2
        };
        var status = val ? "Correct." : "Incorrect.";
        // console.log("Grade: ", postBody)
        (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submissions/grade', {
            method: 'POST',
            body: JSON.stringify(postBody)
        }).then(data => {
            var msg = "This submission is now graded as " + status;
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Grading Status',
                body: msg,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Ok' })]
            });
        })
            .catch(reason => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)('Submission Grade Error', reason);
            console.error(`Failed to grade the submission. \n${reason}`);
        });
    };
    const resetSubmission = async () => {
        (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submissions', {
            method: 'POST',
            body: JSON.stringify({ "submission_id": info.id, "problem_id": info.problem_id })
        }).then(data => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Grading Status Reset',
                body: data.msg,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Ok' })]
            });
        })
            .catch(reason => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)('Submission Reset Error', reason);
            console.error(`Failed to put back the submission. \n${reason}`);
        });
    };
    return (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", { className: 'grp' },
        react__WEBPACK_IMPORTED_MODULE_2___default().createElement(GradeButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.checkIcon, onClick: () => (submitGrade)(true) }),
        react__WEBPACK_IMPORTED_MODULE_2___default().createElement(GradeButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.closeIcon, onClick: () => (submitGrade)(false) }),
        react__WEBPACK_IMPORTED_MODULE_2___default().createElement(ResetButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.redoIcon, onClick: () => (resetSubmission)() })));
};
const MarkdownCellButtonComponent = ({ cell, info, }) => {
    const sendFeedback = async () => {
        let postBody = {
            "student_id": info.student_id,
            "submission_id": info.id,
            "problem_id": info.problem_id,
            "code": info.code,
            "message": info.message,
            "comment": cell.model.value.text
        };
        // console.log("Feedback: ", postBody)
        (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submissions/feedbacks', {
            method: 'POST',
            body: JSON.stringify(postBody)
        }).then(data => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Feedback Status',
                body: "Feedback is sent to the student.",
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: 'Ok' })]
            });
        })
            .catch(reason => {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)('Feedback Send Error', reason);
            console.error(`Failed to save feedback. \n${reason}`);
        });
    };
    return (react__WEBPACK_IMPORTED_MODULE_2___default().createElement(SendButton, { icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.saveIcon, onClick: () => (sendFeedback)() }));
};
class CellCheckButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(cell, info) {
        super();
        this.cell = null;
        this.info = null;
        this.cell = cell;
        this.info = info;
        this.addClass('jp-grpCellButton');
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_2___default().createElement(CodeCellButtonComponent, { cell: this.cell, info: this.info });
    }
}
class FeedbackButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(cell, info) {
        super();
        this.cell = null;
        this.info = null;
        this.cell = cell;
        this.info = info;
        this.addClass('jp-CellButton');
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_2___default().createElement(MarkdownCellButtonComponent, { cell: this.cell, info: this.info });
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.7d74b1f97a0b149a3046.js.map