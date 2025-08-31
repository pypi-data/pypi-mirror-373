"use strict";
(self["webpackChunkcarpo_teacher"] = self["webpackChunkcarpo_teacher"] || []).push([["lib_index_js"],{

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
/* harmony export */   ArchiveProblemButtonExtension: () => (/* binding */ ArchiveProblemButtonExtension),
/* harmony export */   GoToApp: () => (/* binding */ GoToApp),
/* harmony export */   PublishProblemButtonExtension: () => (/* binding */ PublishProblemButtonExtension),
/* harmony export */   RegisterButton: () => (/* binding */ RegisterButton),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   fooIcon: () => (/* binding */ fooIcon)
/* harmony export */ });
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _upload_solution__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./upload-solution */ "./lib/upload-solution.js");









const CommandIds = {
    /**
     * Command to run a code cell.
     */
    mainMenuRegister: 'jlab-carpo:main-register',
    mainMenuGotoApp: 'jlab-carpo:main-goto-app',
    mainMenuAbout: 'jlab-carpo:main-about',
};
class RegistrationWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Widget {
    constructor() {
        super();
        this.node.innerHTML = `
      <div style="padding: 20px; font-family: var(--jp-ui-font-family);">
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px; font-weight: 500;">Name:</label>
          <input type="text" id="name-input" style="width: 100%; padding: 8px; border: 1px solid var(--jp-border-color1); border-radius: 3px; font-size: 13px;" placeholder="Enter your name" />
        </div>
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px; font-weight: 500;">Server URL:</label>
          <input type="url" id="server-url-input" placeholder="http://127.0.0.1:8081" style="width: 100%; padding: 8px; border: 1px solid var(--jp-border-color1); border-radius: 3px; font-size: 13px;" placeholder="Enter server URL" />
        </div>
        <div style="margin-bottom: 15px;">
          <label style="display: block; margin-bottom: 5px; font-weight: 500;">App URL:</label>
          <input type="url" id="app-url-input" placeholder="http://127.0.0.1:8080" style="width: 100%; padding: 8px; border: 1px solid var(--jp-border-color1); border-radius: 3px; font-size: 13px;" placeholder="Enter app URL" />
        </div>
      </div>
    `;
        this.nameInput = this.node.querySelector('#name-input');
        this.serverUrlInput = this.node.querySelector('#server-url-input');
        this.appUrlInput = this.node.querySelector('#app-url-input');
    }
    getValue() {
        return {
            name: this.nameInput.value,
            serverUrl: this.serverUrlInput.value,
            appUrl: this.appUrlInput.value
        };
    }
}
const fooIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.LabIcon({
    name: 'barpkg:foo',
    svgstr: `<svg fill="#000000" height="200px" width="200px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 488.9 488.9" xml:space="preserve"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <path d="M411.448,100.9l-94.7-94.7c-4.2-4.2-9.4-6.2-14.6-6.2h-210.1c-11.4,0-20.8,9.4-20.8,20.8v330.8c0,11.4,9.4,20.8,20.8,20.8 h132.1v95.7c0,11.4,9.4,20.8,20.8,20.8s20.8-9.4,20.8-19.8v-96.6h132.1c11.4,0,19.8-9.4,19.8-19.8V115.5 C417.748,110.3,415.648,105.1,411.448,100.9z M324.048,70.4l39.3,38.9h-39.3V70.4z M378.148,331.9h-112.3v-82.8l17.7,16.3 c10,10,25,3.1,28.1-1c7.3-8.3,7.3-21.8-1-29.1l-52-47.9c-8.3-7.3-20.8-7.3-28.1,0l-52,47.9c-8.3,8.3-8.3,20.8-1,29.1 c8.3,8.3,20.8,8.3,29.1,1l17.7-16.3v82.8h-111.4V41.6h169.6v86.3c0,11.4,9.4,20.8,20.8,20.8h74.9v183.2H378.148z"></path> </g> </g></svg>`
});
/**
 * Initialization data for the carpo-teacher extension.
 */
const plugin = {
    id: 'carpo-teacher:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ICommandPalette],
    optional: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__.IFileBrowserFactory],
    activate: (app, nbTrack, palette, browserFactory, docManager) => {
        console.log('JupyterLab extension carpo-teacher is activated!');
        const { commands } = app;
        const RegisterMenu = CommandIds.mainMenuRegister;
        commands.addCommand(RegisterMenu, {
            label: 'Register',
            caption: 'Register user to server.',
            execute: async (args) => {
                try {
                    const registrationWidget = new RegistrationWidget();
                    const result = await (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                        title: 'Registration Information',
                        body: registrationWidget,
                        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Register' })]
                    });
                    if (!result.button.accept) {
                        return;
                    }
                    const formData = registrationWidget.getValue();
                    // Validate that all fields are filled
                    if (!formData.name || !formData.serverUrl || !formData.appUrl) {
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Registration Error', 'Please fill in all required fields.');
                        return;
                    }
                    // Send POST request with collected information
                    (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('register', {
                        method: 'POST',
                        body: JSON.stringify(formData)
                    })
                        .then(data => {
                        console.log('Registration successful:', data);
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                            title: 'Registration Successful',
                            body: `User ${formData.name} has been registered successfully.`,
                            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                        });
                    })
                        .catch(reason => {
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Registration Error', reason);
                        console.error(`Failed to register user.\n${reason}`);
                    });
                }
                catch (error) {
                    console.error('Registration dialog error:', error);
                    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Registration Error', 'Failed to collect registration information.');
                }
            }
        });
        // Add the command to the command palette
        const category = 'Extension Examples';
        palette.addItem({
            command: RegisterMenu,
            category: category,
            args: { origin: 'from the palette' }
        });
        const GotoAppMenu = CommandIds.mainMenuGotoApp;
        commands.addCommand(GotoAppMenu, {
            label: 'Go to App',
            caption: 'Open the web app.',
            execute: (args) => {
                console.log("Args: ", args);
                (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('view_app', {
                    method: 'GET'
                })
                    .then(data => {
                    console.log(data);
                    window.open(data.url, "_blank");
                })
                    .catch(reason => {
                    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('View App Status Error', reason);
                    console.error(`Failed to view app status.\n${reason}`);
                });
            }
        });
        // Add the command to the command palette
        palette.addItem({
            command: GotoAppMenu,
            category: category,
            args: { origin: 'from the palette' }
        });
        const AboutMenu = CommandIds.mainMenuAbout;
        commands.addCommand(AboutMenu, {
            label: 'About Carpo',
            caption: 'Carpo Information',
            execute: (args) => {
                const content = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Widget();
                content.node.innerHTML = `
          <h3>How to use carpo:</h3>
          <ol>
            <li><strong>To Register </strong>: Input name, ServerUrl and AppUrl </li>
            <li><strong>Publish</strong>: To publish active cell as an exercise.</li>
            <li><strong>Unpublish</strong>: To publish an exercise.</li>
            <li><strong>UploadSolution</strong>: To upload exercise solution.</li>
          </ol>
        `;
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: 'About Carpo',
                    body: content,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            }
        });
        // Add the command to the command palette
        palette.addItem({
            command: AboutMenu,
            category: category,
            args: { origin: 'from the palette' }
        });
        // Depreciated
        nbTrack.currentChanged.connect(() => {
            // const notebookPanel = nbTrack.currentWidget;
            // const notebook = nbTrack.currentWidget.content;
            // / If current Notebook is not inside Exercises/problem_ directory, disable all functionality.
            if (!nbTrack.currentWidget.context.path.includes("problem_")) {
                return;
            }
        });
        //  tell the document registry about your widget extension:
        // app.docRegistry.addWidgetExtension('Notebook', new RegisterButton());
        // app.docRegistry.addWidgetExtension('Notebook', new GoToApp());
        app.docRegistry.addWidgetExtension('Notebook', new PublishProblemButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new ArchiveProblemButtonExtension());
        app.docRegistry.addWidgetExtension('Notebook', new _upload_solution__WEBPACK_IMPORTED_MODULE_7__.GetSolutionButton());
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('register', {
                method: 'GET'
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: '',
                    body: "Instructor " + data.name + " has been registered.",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Registration Error', reason);
                console.error(`Failed to register user as Instructor.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'register-button',
            label: 'Register',
            onClick: register,
            tooltip: 'Register as a Teacher',
        });
        panel.toolbar.insertItem(10, 'register', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
class GoToApp {
    createNew(panel, context) {
        const viewWebApp = () => {
            (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('view_app', {
                method: 'GET'
            })
                .then(data => {
                // console.log(data);
                window.open(data.url, "_blank");
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('View App Status Error', reason);
                console.error(`Failed to view app status.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'get-app-button',
            label: 'App',
            onClick: viewWebApp,
            tooltip: 'Go to the web app',
        });
        panel.toolbar.insertItem(11, 'viewWebApp', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
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
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.clearAllOutputs(panel.content);
            const notebook = panel.content;
            const activeIndex = notebook.activeCellIndex;
            var problem;
            var format;
            var header;
            var time_limit;
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    problem = c.model.sharedModel.getSource();
                    format = c.model.type;
                }
            });
            if (problem.includes("#PID:")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Publish Question Error', "Problem already published.");
                return;
            }
            if (!problem) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Publish Question Error', "Problem is empty.");
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
            (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('problem', {
                method: 'POST',
                body: JSON.stringify(postBody)
            })
                .then(data => {
                // console.log(data)
                notebook.widgets.map((c, index) => {
                    if (index === activeIndex) {
                        c.model.sharedModel.setSource("#PID:" + data.id + "\n" + problem);
                    }
                });
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: 'New Questions Published',
                    body: 'Problem ' + data.id + " is published.",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Publish Question Error', reason);
                console.error(`Failed to publish question to the server.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'publish-problem-button',
            label: 'Publish',
            onClick: publishProblem,
            tooltip: 'Publish New Problem.',
        });
        panel.toolbar.insertItem(10, 'publishNewProblem', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
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
            _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookActions.clearAllOutputs(panel.content);
            const notebook = panel.content;
            const activeIndex = notebook.activeCellIndex;
            var problem;
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    problem = c.model.sharedModel.getSource();
                }
            });
            if (!problem.includes("#PID:")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Unpublish Question Error', "Active problem not found.");
                return;
            }
            var problem_id = parseInt((problem.split("\n")[0]).split("#PID:")[1]);
            let body = {
                "problem_id": problem_id
            };
            (0,_handler__WEBPACK_IMPORTED_MODULE_0__.requestAPI)('problem', {
                method: 'DELETE',
                body: JSON.stringify(body)
            })
                .then(data => {
                console.log(data);
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showDialog)({
                    title: 'Question Unpublished',
                    body: 'Problem id ' + problem_id + ' is  unpublished.',
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.showErrorMessage)('Unpublish Question Error', reason);
                console.error(`Failed to unpublish question.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'archive-problem-button',
            label: 'Unpublish',
            onClick: archiveProblem,
            tooltip: 'Unpublish the problem.',
        });
        panel.toolbar.insertItem(11, 'archivesProblem', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/upload-solution.js":
/*!********************************!*\
  !*** ./lib/upload-solution.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   GetSolutionButton: () => (/* binding */ GetSolutionButton)
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
        const uploadSolution = () => {
            const notebook = panel.content;
            const activeIndex = notebook.activeCellIndex;
            var code_block;
            var solution;
            notebook.widgets.map((c, index) => {
                if (index === activeIndex) {
                    code_block = c.model.sharedModel.getSource();
                }
            });
            if (!code_block.includes("#PID:")) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Upload Solution Error', "Active problem not found.");
                return;
            }
            var problem_id = parseInt((code_block.split("\n")[0]).split("#PID:")[1]);
            solution = code_block.split('\n').slice(1).join('\n').trim();
            let body = {
                "problem_id": problem_id,
                "code": solution
            };
            (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('solution', {
                method: 'POST',
                body: JSON.stringify(body)
            })
                .then(data => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
                    title: 'Solution Uploaded',
                    body: 'Solution uploaded for ProblemID ' + problem_id + '.',
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton({ label: 'Ok' })]
                });
            })
                .catch(reason => {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showErrorMessage)('Upload Solution Error', reason);
                console.error(`Failed to upload solution to problem.\n${reason}`);
            });
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'upload-solution-button',
            label: 'UploadSolution',
            onClick: uploadSolution,
            tooltip: 'Upload solutions to the problem.',
        });
        panel.toolbar.insertItem(12, 'getSolutions', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.f7d1294a5b7123ce3525.js.map