"use strict";
(self["webpackChunkjupyterchatz"] = self["webpackChunkjupyterchatz"] || []).push([["lib_index_js"],{

/***/ "./lib/components/ChatWidget.js":
/*!**************************************!*\
  !*** ./lib/components/ChatWidget.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ChatWidget: () => (/* binding */ ChatWidget)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _services_chatService__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../services/chatService */ "./lib/services/chatService.js");



/**
 * Markdown渲染组件
 */
const MarkdownRenderer = ({ content }) => {
    const renderMarkdown = (text) => {
        // 处理代码块
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        const parts = [];
        let lastIndex = 0;
        let match;
        while ((match = codeBlockRegex.exec(text)) !== null) {
            // 添加代码块前的文本
            if (match.index > lastIndex) {
                parts.push({
                    type: 'text',
                    content: text.slice(lastIndex, match.index)
                });
            }
            // 添加代码块
            parts.push({
                type: 'code',
                language: match[1] || 'text',
                content: match[2]
            });
            lastIndex = match.index + match[0].length;
        }
        // 添加剩余的文本
        if (lastIndex < text.length) {
            parts.push({
                type: 'text',
                content: text.slice(lastIndex)
            });
        }
        return parts;
    };
    const renderText = (text) => {
        // 处理粗体文本
        const boldRegex = /\*\*(.*?)\*\*/g;
        const parts = [];
        let lastIndex = 0;
        let match;
        while ((match = boldRegex.exec(text)) !== null) {
            // 添加粗体前的文本
            if (match.index > lastIndex) {
                parts.push(text.slice(lastIndex, match.index));
            }
            // 添加粗体文本
            parts.push(react__WEBPACK_IMPORTED_MODULE_0___default().createElement("strong", { key: match.index }, match[1]));
            lastIndex = match.index + match[0].length;
        }
        // 添加剩余的文本
        if (lastIndex < text.length) {
            parts.push(text.slice(lastIndex));
        }
        return parts.length > 0 ? parts : text;
    };
    const parts = renderMarkdown(content);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null, parts.map((part, index) => {
        if (part.type === 'code') {
            return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { key: index, className: "jp-AIChat-codeBlock" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-codeHeader" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { className: "jp-AIChat-codeLanguage" }, part.language)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("pre", { className: "jp-AIChat-codeContent" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("code", { className: `language-${part.language}` }, part.content))));
        }
        else {
            return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { key: index, className: "jp-AIChat-textContent" }, part.content.split('\n').map((line, i) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), { key: i },
                renderText(line),
                i < part.content.split('\n').length - 1 && react__WEBPACK_IMPORTED_MODULE_0___default().createElement("br", null))))));
        }
    })));
};
/**
 * 聊天React组件
 */
const ChatComponent = (props) => {
    const [messages, setMessages] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
    const [input, setInput] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('');
    const [isLoading, setIsLoading] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const chatService = new _services_chatService__WEBPACK_IMPORTED_MODULE_2__.ChatService({
        fileBrowserFactory: props.fileBrowserFactory,
        documentManager: props.documentManager,
        editorTracker: props.editorTracker,
        notebookTracker: props.notebookTracker
    });
    const messagesEndRef = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)(null);
    // 自动滚动到最新消息
    const scrollToBottom = () => {
        var _a;
        (_a = messagesEndRef.current) === null || _a === void 0 ? void 0 : _a.scrollIntoView({ behavior: 'smooth' });
    };
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        scrollToBottom();
    }, [messages]);
    // 发送消息
    const handleSendMessage = async () => {
        if (!input.trim())
            return;
        const userMessage = {
            role: 'user',
            content: input
        };
        // 更新UI显示用户消息
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        try {
            // 准备发送给API的消息历史
            const messageHistory = [...messages, userMessage];
            // 调用API获取回复
            const response = await chatService.sendMessage(messageHistory);
            // 更新UI显示AI回复
            const assistantMessage = {
                role: 'assistant',
                content: response
            };
            setMessages(prev => [...prev, assistantMessage]);
        }
        catch (error) {
            console.error('发送消息失败:', error);
            // 显示错误消息
            const errorMessage = {
                role: 'assistant',
                content: '抱歉，发生了错误。请稍后再试。'
            };
            setMessages(prev => [...prev, errorMessage]);
        }
        finally {
            setIsLoading(false);
        }
    };
    // 处理按键事件（回车发送）
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-container" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-header" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("h3", null, "AI \u52A9\u624B")),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-messages" },
            messages.length === 0 ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-welcome" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null, "\u6B22\u8FCE\u4F7F\u7528 AI \u52A9\u624B\uFF01\u8BF7\u8F93\u5165\u60A8\u7684\u95EE\u9898\u3002"))) : (messages.map((msg, index) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { key: index, className: `jp-AIChat-message ${msg.role === 'user' ? 'jp-AIChat-userMessage' : 'jp-AIChat-assistantMessage'}` },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-messageContent" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(MarkdownRenderer, { content: msg.content })))))),
            isLoading && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-message jp-AIChat-assistantMessage" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-messageContent jp-AIChat-loading" }, "\u601D\u8003\u4E2D..."))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { ref: messagesEndRef })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "jp-AIChat-inputArea" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("textarea", { className: "jp-AIChat-input", value: input, onChange: (e) => setInput(e.target.value), onKeyPress: handleKeyPress, placeholder: "\u8F93\u5165\u60A8\u7684\u95EE\u9898...", disabled: isLoading }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("button", { className: "jp-AIChat-sendButton", onClick: handleSendMessage, disabled: isLoading || !input.trim() }, "\u53D1\u9001"))));
};
/**
 * 聊天窗口部件
 */
class ChatWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    /**
     * 构造函数
     */
    constructor(options = {}) {
        super();
        this.addClass('jp-AIChat-widget');
        this.id = 'jupyterchatz-chat';
        this.title.label = 'AI 助手';
        this.title.closable = true;
        this.fileBrowserFactory = options.fileBrowserFactory;
        this.documentManager = options.documentManager;
        this.editorTracker = options.editorTracker;
        this.notebookTracker = options.notebookTracker;
        console.log('ChatWidget 构造函数中的服务:');
        console.log('- fileBrowserFactory:', this.fileBrowserFactory);
        console.log('- documentManager:', this.documentManager);
        console.log('- editorTracker:', this.editorTracker);
        console.log('- notebookTracker:', this.notebookTracker);
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(ChatComponent, { fileBrowserFactory: this.fileBrowserFactory, documentManager: this.documentManager, editorTracker: this.editorTracker, notebookTracker: this.notebookTracker });
    }
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
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/fileeditor */ "webpack/sharing/consume/default/@jupyterlab/fileeditor");
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _components_ChatWidget__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./components/ChatWidget */ "./lib/components/ChatWidget.js");









/**
 * 聊天窗口跟踪器
 */
const trackerNamespace = 'jupyterchatz-tracker';
/**
 * Initialization data for the jupyterchatz extension.
 */
const plugin = {
    id: 'jupyterchatz:plugin',
    description: 'JupyterLab的AI聊天助手扩展',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette],
    optional: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_2__.IMainMenu, _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_3__.IFileBrowserFactory, _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__.IDocumentManager, _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__.IEditorTracker, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__.INotebookTracker],
    activate: (app, palette, restorer, mainMenu, fileBrowserFactory, documentManager, editorTracker, notebookTracker) => {
        console.log('JupyterLab扩展jupyterchatz已激活!');
        console.log('插件激活时接收到的服务:');
        console.log('- fileBrowserFactory:', fileBrowserFactory);
        console.log('- documentManager:', documentManager);
        console.log('- editorTracker:', editorTracker);
        console.log('- notebookTracker:', notebookTracker);
        // 创建聊天窗口跟踪器
        const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: trackerNamespace
        });
        // 添加命令
        const command = 'jupyterchatz:open';
        app.commands.addCommand(command, {
            label: '打开AI助手',
            execute: () => {
                // 检查是否已经有聊天窗口打开
                let chatWidget = null;
                // 尝试获取现有窗口
                if (tracker.currentWidget) {
                    chatWidget = tracker.currentWidget;
                }
                if (chatWidget) {
                    app.shell.activateById(chatWidget.id);
                    return chatWidget;
                }
                // 创建新的聊天窗口，传递文件系统服务
                chatWidget = new _components_ChatWidget__WEBPACK_IMPORTED_MODULE_7__.ChatWidget({
                    fileBrowserFactory,
                    documentManager,
                    editorTracker,
                    notebookTracker
                });
                // 将窗口添加到右侧面板
                app.shell.add(chatWidget, 'right', { rank: 1000 });
                // 将窗口添加到跟踪器
                void tracker.add(chatWidget);
                return chatWidget;
            }
        });
        // 添加到命令面板
        palette.addItem({ command, category: 'AI助手' });
        // 添加到主菜单
        if (mainMenu) {
            // 添加到帮助菜单
            const helpMenu = mainMenu.helpMenu;
            helpMenu.addGroup([{ command }]);
        }
        // 恢复布局
        if (restorer) {
            void restorer.restore(tracker, {
                command,
                name: () => 'jupyterchatz'
            });
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/services/chatService.js":
/*!*************************************!*\
  !*** ./lib/services/chatService.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ChatService: () => (/* binding */ ChatService)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mcpService__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./mcpService */ "./lib/services/mcpService.js");



/**
 * AI聊天服务
 */
class ChatService {
    /**
     * 构造函数
     * @param options 服务选项
     */
    constructor(options = {}) {
        this.apiKey = 'sk-7W5ztpH97ea2RjWVC3BbC375Aa6d4bD98550EbFcBc7146Ec';
        this.apiUrl = 'https://api.aihubmix.com/v1/chat/completions';
        this.model = 'gpt-4o-mini';
        this.mcpServerUrl = 'http://localhost:8888'; // 修改为您的JupyterLab服务器地址
        this.fileBrowserFactory = options.fileBrowserFactory;
        this.documentManager = options.documentManager;
        this.editorTracker = options.editorTracker;
        this.notebookTracker = options.notebookTracker;
        // 初始化MCP服务
        this.initMCPService();
    }
    /**
     * 初始化MCP服务
     */
    async initMCPService() {
        try {
            // 创建MCP服务实例
            this.mcpService = new _mcpService__WEBPACK_IMPORTED_MODULE_2__.MCPService({
                serverUrl: this.mcpServerUrl,
                transport: 'stdio'
            }, this.notebookTracker);
            // 检查MCP服务器健康状态
            const isHealthy = await this.mcpService.checkHealth();
            if (isHealthy) {
                console.log('MCP服务器连接正常');
            }
            else {
                console.warn('MCP服务器连接异常，部分功能可能不可用');
            }
        }
        catch (error) {
            console.error('初始化MCP服务失败:', error);
        }
    }
    /**
     * 获取当前工作目录路径
     * @returns 当前工作目录路径
     */
    getCurrentDirectory() {
        console.log('获取当前工作目录...');
        // 首先尝试从 fileBrowserFactory 获取
        if (this.fileBrowserFactory) {
            try {
                console.log('尝试从 fileBrowserFactory 获取当前路径');
                const browser = this.fileBrowserFactory.tracker.currentWidget;
                if (browser) {
                    const path = browser.model.path;
                    console.log('从 fileBrowserFactory 获取的路径:', path);
                    return path;
                }
            }
            catch (error) {
                console.error('从 fileBrowserFactory 获取路径时出错:', error);
            }
        }
        else {
            console.warn('fileBrowserFactory 未定义');
        }
        // 如果 fileBrowserFactory 方法失败，尝试从 notebookTracker 获取
        if (this.notebookTracker && this.notebookTracker.currentWidget) {
            try {
                console.log('尝试从 notebookTracker 获取当前路径');
                const path = this.notebookTracker.currentWidget.context.path;
                // 获取目录部分（去掉文件名）
                const lastSlashIndex = path.lastIndexOf('/');
                if (lastSlashIndex >= 0) {
                    const dirPath = path.substring(0, lastSlashIndex);
                    console.log('从 notebookTracker 获取的目录路径:', dirPath);
                    return dirPath;
                }
                console.log('从 notebookTracker 获取的路径:', path);
                return ''; // 如果没有斜杠，说明文件在根目录
            }
            catch (error) {
                console.error('从 notebookTracker 获取路径时出错:', error);
            }
        }
        // 如果 notebookTracker 方法失败，尝试从 documentManager 获取
        if (this.documentManager) {
            try {
                console.log('尝试从 documentManager 获取当前路径');
                return this.documentManager.services.contents.localPath('');
            }
            catch (error) {
                console.error('从 documentManager 获取路径时出错:', error);
            }
        }
        // 如果都失败了，返回一个默认路径
        console.warn('无法获取当前路径，使用默认路径');
        return '';
    }
    /**
     * 获取当前目录下的文件列表
     * @returns 文件列表
     */
    async getCurrentDirectoryContents() {
        console.log('获取当前目录内容...');
        if (!this.documentManager) {
            console.warn('documentManager 未定义');
            return [];
        }
        try {
            // 获取当前路径
            const currentPath = this.getCurrentDirectory() || '';
            console.log('使用路径获取目录内容:', currentPath);
            // 直接使用 documentManager 获取目录内容
            const dirContents = await this.documentManager.services.contents.get(currentPath);
            if (!dirContents || !dirContents.content) {
                return [];
            }
            // 转换为文件信息数组
            return dirContents.content.map((item) => {
                return {
                    path: item.path,
                    name: item.name,
                    extension: item.type === 'directory' ? '' : _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.extname(item.name),
                    isDirectory: item.type === 'directory'
                };
            });
        }
        catch (error) {
            console.error('获取目录内容失败:', error);
            return [];
        }
    }
    /**
     * 获取当前打开的文件信息
     * @returns 当前打开的文件信息
     */
    getCurrentOpenedFile() {
        // 检查编辑器
        if (this.editorTracker && this.editorTracker.currentWidget) {
            const editor = this.editorTracker.currentWidget;
            const context = editor.context;
            const path = context.path;
            const model = editor.content.model;
            return {
                path: path,
                name: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.basename(path),
                extension: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.extname(path),
                content: model.toString(),
                isDirectory: false
            };
        }
        // 检查笔记本
        if (this.notebookTracker && this.notebookTracker.currentWidget) {
            const notebook = this.notebookTracker.currentWidget;
            const context = notebook.context;
            const path = context.path;
            // 获取笔记本内容（这里简化处理，只获取代码单元格）
            let content = '';
            const model = notebook.content.model;
            if (model) {
                for (let i = 0; i < model.cells.length; i++) {
                    const cell = model.cells.get(i);
                    if (cell.type === 'code') {
                        content += `# Cell ${i + 1}\n${cell.toString()}\n\n`;
                    }
                }
            }
            return {
                path: path,
                name: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.basename(path),
                extension: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.extname(path),
                content: content,
                isDirectory: false
            };
        }
        return null;
    }
    /**
     * 连接到当前打开的Notebook
     * @returns 连接结果
     */
    async connectToCurrentNotebook() {
        // 确保MCP服务初始化
        if (!this.mcpService) {
            console.log('初始化MCP服务...');
            this.mcpService = new _mcpService__WEBPACK_IMPORTED_MODULE_2__.MCPService({
                serverUrl: this.mcpServerUrl,
                transport: 'stdio'
            }, this.notebookTracker);
        }
        // 检查是否有打开的Notebook
        if (!this.notebookTracker || !this.notebookTracker.currentWidget) {
            console.warn('当前没有打开的Notebook');
            return false;
        }
        const notebook = this.notebookTracker.currentWidget;
        const path = notebook.context.path;
        console.log(`尝试连接到Notebook: ${path}`);
        try {
            // 连接到当前Notebook
            const connected = await this.mcpService.connect();
            if (connected) {
                console.log(`已成功连接到Notebook: ${path}`);
            }
            else {
                console.warn(`连接到Notebook ${path} 失败`);
            }
            return connected;
        }
        catch (error) {
            console.error('连接到Notebook时出错:', error);
            return false;
        }
    }
    /**
     * 读取指定文件的内容
     * @param path 文件路径
     * @returns 文件内容
     */
    async readFile(path) {
        if (!this.documentManager) {
            return null;
        }
        try {
            const contents = await this.documentManager.services.contents.get(path, { content: true });
            if (contents.type === 'file') {
                return contents.content;
            }
            return null;
        }
        catch (error) {
            console.error('读取文件失败:', error);
            return null;
        }
    }
    /**
     * 获取Notebook信息
     * @returns Notebook信息
     */
    async getNotebookInfo() {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const info = await this.mcpService.getNotebookInfo();
            if (!info) {
                return '无法获取Notebook信息';
            }
            return `**Notebook信息:**\n\n` +
                `- **文档ID:** ${info.document_id}\n` +
                `- **单元格总数:** ${info.total_cells}\n` +
                `- **单元格类型统计:** ${JSON.stringify(info.cell_types)}`;
        }
        catch (error) {
            console.error('获取Notebook信息失败:', error);
            return `获取Notebook信息失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 读取所有单元格
     * @returns 所有单元格信息
     */
    async readAllCells() {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const cells = await this.mcpService.readAllCells();
            if (!cells || cells.length === 0) {
                return '无法获取单元格或Notebook为空';
            }
            let result = `Notebook包含 ${cells.length} 个单元格:\n\n`;
            cells.forEach((cell, index) => {
                result += `**单元格 ${cell.index} (${cell.type}):**\n\n`;
                // 代码内容
                result += '```';
                // 根据单元格类型添加语言标识
                if (cell.type === 'code') {
                    result += 'python';
                }
                else if (cell.type === 'markdown') {
                    result += 'markdown';
                }
                result += '\n';
                // 确保单元格内容正确显示
                if (cell.source && cell.source.length > 0) {
                    // 如果source是数组，将其连接起来
                    result += cell.source.join('');
                }
                else {
                    result += '# 空单元格';
                }
                result += '\n```\n\n';
                // 输出内容
                if (cell.outputs && cell.outputs.length > 0) {
                    result += '**输出:**\n';
                    result += '```\n';
                    result += cell.outputs.join('\n');
                    result += '\n```\n\n';
                }
                else {
                    result += '**输出:** 无输出\n\n';
                }
            });
            return result;
        }
        catch (error) {
            console.error('读取所有单元格失败:', error);
            return `读取所有单元格失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 读取指定单元格
     * @param cellIndex 单元格索引
     * @returns 单元格信息
     */
    async readCell(cellIndex) {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const cell = await this.mcpService.readCell(cellIndex);
            if (!cell) {
                return `无法获取单元格 ${cellIndex}`;
            }
            let result = `**单元格 ${cell.index} (${cell.type}):**\n\n`;
            // 代码内容
            result += '```';
            // 根据单元格类型添加语言标识
            if (cell.type === 'code') {
                result += 'python';
            }
            else if (cell.type === 'markdown') {
                result += 'markdown';
            }
            result += '\n';
            // 确保单元格内容正确显示
            if (cell.source && cell.source.length > 0) {
                // 如果source是数组，将其连接起来
                result += cell.source.join('');
            }
            else {
                result += '# 空单元格';
            }
            result += '\n```\n\n';
            // 输出内容
            if (cell.outputs && cell.outputs.length > 0) {
                result += '**输出:**\n';
                result += '```\n';
                result += cell.outputs.join('\n');
                result += '\n```\n';
            }
            else {
                result += '**输出:** 无输出\n';
            }
            return result;
        }
        catch (error) {
            console.error(`读取单元格 ${cellIndex} 失败:`, error);
            return `读取单元格 ${cellIndex} 失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 添加Markdown单元格
     * @param content Markdown内容
     * @returns 操作结果
     */
    async appendMarkdownCell(content) {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const result = await this.mcpService.appendMarkdownCell(content);
            if (!result) {
                return '添加Markdown单元格失败';
            }
            return `成功添加Markdown单元格: ${result}`;
        }
        catch (error) {
            console.error('添加Markdown单元格失败:', error);
            return `添加Markdown单元格失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 添加并执行代码单元格
     * @param code 代码内容
     * @returns 执行结果
     */
    async appendExecuteCodeCell(code) {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const outputs = await this.mcpService.appendExecuteCodeCell(code);
            if (!outputs) {
                return '添加并执行代码单元格失败';
            }
            let result = '代码执行结果:\n\`\`\`\n';
            result += Array.isArray(outputs) ? outputs.join('\n') : outputs;
            result += '\n\`\`\`';
            return result;
        }
        catch (error) {
            console.error('添加并执行代码单元格失败:', error);
            return `添加并执行代码单元格失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 执行指定单元格
     * @param cellIndex 单元格索引
     * @returns 执行结果
     */
    async executeCell(cellIndex) {
        if (!this.mcpService) {
            return '未初始化MCP服务';
        }
        try {
            const outputs = await this.mcpService.executeCell(cellIndex);
            if (!outputs) {
                return `执行单元格 ${cellIndex} 失败`;
            }
            let result = `单元格 ${cellIndex} 执行结果:\n\`\`\`\n`;
            result += Array.isArray(outputs) ? outputs.join('\n') : outputs;
            result += '\n\`\`\`';
            return result;
        }
        catch (error) {
            console.error(`执行单元格 ${cellIndex} 失败:`, error);
            return `执行单元格 ${cellIndex} 失败: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
        }
    }
    /**
     * 发送聊天消息并获取响应
     * @param messages 聊天历史
     * @returns 返回AI的响应
     */
    async sendMessage(messages) {
        try {
            // 检查消息中是否包含特殊命令
            const lastMessage = messages[messages.length - 1];
            if (lastMessage.role === 'user') {
                const content = lastMessage.content.toLowerCase().trim();
                console.log('处理用户消息:', content);
                // 处理特殊命令
                if (content === '/pwd' || content === '/cwd' || content.includes('当前目录')) {
                    console.log('执行获取当前目录命令');
                    try {
                        const currentDir = this.getCurrentDirectory();
                        console.log('获取到的当前目录:', currentDir);
                        return `当前工作目录: ${currentDir || '未知'}`;
                    }
                    catch (error) {
                        console.error('获取当前目录时出错:', error);
                        return `获取当前目录时出错: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
                    }
                }
                if (content === '/ls' || content.includes('列出文件') || content.includes('显示文件列表')) {
                    console.log('执行列出文件命令');
                    try {
                        const files = await this.getCurrentDirectoryContents();
                        console.log('获取到的文件列表:', files);
                        if (files.length === 0) {
                            return '当前目录为空或无法访问目录内容。';
                        }
                        const fileList = files.map(file => `${file.isDirectory ? '[目录] ' : '[文件] '}${file.name}`).join('\\n');
                        return `当前目录 (${this.getCurrentDirectory() || '未知'}) 的内容:\\n${fileList}`;
                    }
                    catch (error) {
                        console.error('获取文件列表时出错:', error);
                        return `获取文件列表时出错: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
                    }
                }
                // 获取当前文件
                if (content === '/current' || content.includes('当前文件') || content.includes('显示当前文件')) {
                    console.log('执行获取当前文件命令');
                    try {
                        const currentFile = this.getCurrentOpenedFile();
                        console.log('获取到的当前文件:', currentFile);
                        if (!currentFile) {
                            return '当前没有打开的文件。';
                        }
                        let response = `当前打开的文件: ${currentFile.path}\n\n`;
                        if (currentFile.content) {
                            // 如果文件内容太长，只显示前1000个字符
                            const contentPreview = currentFile.content.length > 1000
                                ? currentFile.content.substring(0, 1000) + '...(内容已截断)'
                                : currentFile.content;
                            response += `文件内容:\n\`\`\`${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.extname(currentFile.name).substring(1)}\n${contentPreview}\n\`\`\``;
                        }
                        else {
                            response += '无法获取文件内容。';
                        }
                        return response;
                    }
                    catch (error) {
                        console.error('获取当前文件时出错:', error);
                        return `获取当前文件时出错: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
                    }
                }
                // 读取指定文件
                const readFileMatch = content.match(/\/read\s+(.+)/) || content.match(/读取文件\s+(.+)/);
                if (readFileMatch) {
                    console.log('执行读取指定文件命令');
                    try {
                        const filePath = readFileMatch[1].trim();
                        console.log('要读取的文件路径:', filePath);
                        const currentDir = this.getCurrentDirectory() || '';
                        console.log('当前目录:', currentDir);
                        const fullPath = filePath.startsWith('/') ? filePath : _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.join(currentDir, filePath);
                        console.log('完整文件路径:', fullPath);
                        const fileContent = await this.readFile(fullPath);
                        console.log('文件内容是否获取成功:', fileContent !== null);
                        if (fileContent === null) {
                            return `无法读取文件: ${fullPath}`;
                        }
                        // 如果文件内容太长，只显示前1000个字符
                        const contentPreview = fileContent.length > 1000
                            ? fileContent.substring(0, 1000) + '...(内容已截断)'
                            : fileContent;
                        return `文件 ${fullPath} 的内容:\n\`\`\`${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PathExt.extname(fullPath).substring(1)}\n${contentPreview}\n\`\`\``;
                    }
                    catch (error) {
                        console.error('读取指定文件时出错:', error);
                        return `读取指定文件时出错: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
                    }
                }
                // MCP相关命令
                // 连接到当前Notebook
                if (content === '/connect' || content.includes('连接notebook')) {
                    console.log('执行连接到当前Notebook命令');
                    try {
                        const connected = await this.connectToCurrentNotebook();
                        return connected
                            ? '已成功连接到当前Notebook'
                            : '连接到当前Notebook失败，请确保已打开Notebook并且MCP服务器正在运行';
                    }
                    catch (error) {
                        console.error('连接到当前Notebook时出错:', error);
                        return `连接到当前Notebook时出错: ${(error === null || error === void 0 ? void 0 : error.message) || '未知错误'}`;
                    }
                }
                // 获取Notebook信息
                if (content === '/notebook-info' || content.includes('notebook信息')) {
                    console.log('执行获取Notebook信息命令');
                    return await this.getNotebookInfo();
                }
                // 读取所有单元格
                if (content === '/cells' || content.includes('所有单元格')) {
                    console.log('执行读取所有单元格命令');
                    return await this.readAllCells();
                }
                // 读取指定单元格
                const readCellMatch = content.match(/\/cell\s+(\d+)/) || content.match(/单元格\s+(\d+)/);
                if (readCellMatch) {
                    const cellIndex = parseInt(readCellMatch[1]);
                    console.log(`执行读取单元格 ${cellIndex} 命令`);
                    return await this.readCell(cellIndex);
                }
                // 添加Markdown单元格
                const addMarkdownMatch = content.match(/\/add-markdown\s+(.+)/s) || content.match(/添加markdown\s+(.+)/s);
                if (addMarkdownMatch) {
                    const markdownContent = addMarkdownMatch[1].trim();
                    console.log('执行添加Markdown单元格命令');
                    return await this.appendMarkdownCell(markdownContent);
                }
                // 添加并执行代码单元格
                const addCodeMatch = content.match(/\/add-code\s+(.+)/s) || content.match(/添加代码\s+(.+)/s);
                if (addCodeMatch) {
                    const codeContent = addCodeMatch[1].trim();
                    console.log('执行添加并执行代码单元格命令');
                    return await this.appendExecuteCodeCell(codeContent);
                }
                // 执行指定单元格
                const execCellMatch = content.match(/\/exec\s+(\d+)/) || content.match(/执行单元格\s+(\d+)/);
                if (execCellMatch) {
                    const cellIndex = parseInt(execCellMatch[1]);
                    console.log(`执行单元格 ${cellIndex} 命令`);
                    return await this.executeCell(cellIndex);
                }
            }
            // 正常处理消息
            const response = await axios__WEBPACK_IMPORTED_MODULE_0___default().post(this.apiUrl, {
                model: this.model,
                messages: messages
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            if (response.data && response.data.choices && response.data.choices.length > 0) {
                return response.data.choices[0].message.content;
            }
            else {
                throw new Error('无效的API响应');
            }
        }
        catch (error) {
            console.error('AI聊天API调用失败:', error);
            return '抱歉，我无法连接到AI服务。请检查网络连接或API密钥是否有效。';
        }
    }
}


/***/ }),

/***/ "./lib/services/mcpService.js":
/*!************************************!*\
  !*** ./lib/services/mcpService.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   MCPService: () => (/* binding */ MCPService)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);

/**
 * MCP服务类
 */
class MCPService {
    constructor(config, notebookTracker) {
        this.isConnected = false;
        this.config = config;
        this.notebookTracker = notebookTracker;
    }
    /**
     * 检查MCP服务器健康状态
     */
    async checkHealth() {
        console.log('跳过MCP服务器健康检查，直接返回true');
        return true;
    }
    /**
     * 连接到MCP服务器
     */
    async connect() {
        try {
            console.log('尝试连接到MCP服务器...');
            console.log('MCP服务器URL:', this.config.serverUrl);
            console.log('传输方式:', this.config.transport);
            // 对于stdio模式，我们假设连接成功
            if (this.config.transport === 'stdio') {
                console.log('已成功连接到MCP服务器(stdio模式)');
                this.isConnected = true;
                return true;
            }
            // 对于HTTP模式，尝试连接
            const response = await axios__WEBPACK_IMPORTED_MODULE_0___default().post(`${this.config.serverUrl}/api/connect`);
            if (response.status === 200) {
                console.log('已成功连接到MCP服务器');
                this.isConnected = true;
                return true;
            }
            console.error('连接MCP服务器失败:', response.status);
            return false;
        }
        catch (error) {
            console.error('连接MCP服务器时出错:', error);
            return false;
        }
    }
    /**
     * 获取Notebook信息
     */
    async getNotebookInfo() {
        try {
            console.log('尝试获取Notebook信息...');
            if (!this.notebookTracker) {
                console.error('notebookTracker未定义');
                return null;
            }
            if (!this.notebookTracker.currentWidget) {
                console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
                return null;
            }
            const notebook = this.notebookTracker.currentWidget;
            const model = notebook.content.model;
            if (!model) {
                console.error('notebook.content.model未定义');
                return null;
            }
            const info = {
                path: notebook.context.path,
                name: notebook.context.path.split('/').pop(),
                cells: model.cells.length,
                type: 'notebook'
            };
            console.log('Notebook信息:', info);
            return info;
        }
        catch (error) {
            console.error('获取notebook信息失败:', error);
            return null;
        }
    }
    /**
     * 读取所有单元格
     */
    async readAllCells() {
        try {
            console.log('尝试读取所有单元格...');
            // 详细检查notebookTracker
            if (!this.notebookTracker) {
                console.error('notebookTracker未定义');
                return null;
            }
            // 详细检查currentWidget
            if (!this.notebookTracker.currentWidget) {
                console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
                return null;
            }
            const notebook = this.notebookTracker.currentWidget;
            console.log('notebook对象类型:', typeof notebook);
            // 详细检查content
            if (!notebook.content) {
                console.error('notebook.content未定义');
                return null;
            }
            // 详细检查model
            if (!notebook.content.model) {
                console.error('notebook.content.model未定义');
                return null;
            }
            const model = notebook.content.model;
            // 详细检查cells
            if (!model.cells) {
                console.error('model.cells未定义');
                return null;
            }
            console.log('单元格数量:', model.cells.length);
            // 如果没有单元格，返回空数组而不是null
            if (model.cells.length === 0) {
                console.warn('Notebook没有单元格');
                return [];
            }
            // 手动构建单元格信息
            const cells = [];
            for (let i = 0; i < model.cells.length; i++) {
                try {
                    const cell = model.cells.get(i);
                    if (!cell) {
                        console.warn(`无法获取单元格 ${i}`);
                        continue;
                    }
                    // 获取单元格内容
                    let source = [];
                    try {
                        // 详细调试单元格对象结构
                        console.log(`=== 单元格 ${i} 调试信息 ===`);
                        console.log('单元格对象:', cell);
                        console.log('单元格类型:', typeof cell);
                        console.log('单元格构造函数:', cell.constructor.name);
                        // 检查所有可枚举属性
                        console.log('可枚举属性:');
                        for (const key in cell) {
                            if (cell.hasOwnProperty(key)) {
                                console.log(`  ${key}:`, typeof cell[key], cell[key]);
                            }
                        }
                        // 检查所有属性（包括不可枚举的）
                        console.log('所有属性:');
                        const allProps = Object.getOwnPropertyNames(cell);
                        allProps.forEach(prop => {
                            try {
                                const value = cell[prop];
                                console.log(`  ${prop}:`, typeof value, value);
                            }
                            catch (e) {
                                console.log(`  ${prop}: [无法访问]`);
                            }
                        });
                        // 尝试不同的方法获取单元格内容
                        let content = '';
                        // 方法1: 尝试访问sharedModel.source
                        if (cell.sharedModel && cell.sharedModel.source) {
                            const source = cell.sharedModel.source;
                            content = Array.isArray(source) ? source.join('\n') : source;
                            console.log('使用方法1 (sharedModel.source) 获取内容:', content);
                        }
                        // 方法2: 尝试访问sharedModel.getSource()
                        else if (cell.sharedModel && typeof cell.sharedModel.getSource === 'function') {
                            try {
                                content = cell.sharedModel.getSource();
                                console.log('使用方法2 (sharedModel.getSource()) 获取内容:', content);
                            }
                            catch (e) {
                                console.log('sharedModel.getSource() 调用失败:', e);
                            }
                        }
                        // 方法3: 尝试访问value.text
                        else if (cell.value && cell.value.text) {
                            content = cell.value.text;
                            console.log('使用方法3 (value.text) 获取内容:', content);
                        }
                        // 方法4: 尝试访问source
                        else if (cell.source) {
                            content = Array.isArray(cell.source)
                                ? cell.source.join('\n')
                                : cell.source;
                            console.log('使用方法4 (source) 获取内容:', content);
                        }
                        // 方法5: 尝试访问text
                        else if (cell.text) {
                            content = cell.text;
                            console.log('使用方法5 (text) 获取内容:', content);
                        }
                        // 方法6: 尝试访问model
                        else if (cell.model && cell.model.value) {
                            content = cell.model.value.text || cell.model.value.source;
                            console.log('使用方法6 (model.value) 获取内容:', content);
                        }
                        // 方法7: 尝试使用toString()并检查是否为字符串
                        else {
                            const toStringResult = cell.toString();
                            console.log('toString()结果:', toStringResult, '类型:', typeof toStringResult);
                            if (typeof toStringResult === 'string' && toStringResult !== '[object Object]') {
                                content = toStringResult;
                            }
                            else {
                                console.warn(`单元格 ${i} toString()返回非字符串或[object Object]:`, typeof toStringResult);
                                content = `[单元格 ${i} 内容无法获取]`;
                            }
                        }
                        source = content ? content.split('\n') : [''];
                        console.log(`单元格 ${i} 最终内容:`, content.substring(0, 100) + (content.length > 100 ? '...' : ''));
                        console.log(`=== 单元格 ${i} 调试结束 ===`);
                    }
                    catch (e) {
                        console.error(`获取单元格 ${i} 内容失败:`, e);
                        source = [`[单元格 ${i} 内容获取失败]`];
                    }
                    // 获取单元格输出
                    let outputs = [];
                    if (cell.type === 'code') {
                        try {
                            console.log(`=== 单元格 ${i} 输出调试信息 ===`);
                            console.log('单元格对象:', cell);
                            console.log('单元格outputs属性:', cell.outputs);
                            console.log('outputs类型:', typeof cell.outputs);
                            console.log('outputs是否为数组:', Array.isArray(cell.outputs));
                            // 检查所有可能的输出相关属性
                            const outputProps = ['outputs', 'output', 'result', 'data'];
                            outputProps.forEach(prop => {
                                if (cell[prop] !== undefined) {
                                    console.log(`属性 ${prop}:`, cell[prop]);
                                }
                            });
                            // 尝试获取输出
                            if (cell.outputs) {
                                const cellOutputs = cell.outputs;
                                console.log(`单元格 ${i} outputs对象:`, cellOutputs);
                                console.log(`outputs构造函数:`, cellOutputs.constructor.name);
                                // 检查是否有list属性（ObservableList结构）
                                if (cellOutputs.list && cellOutputs.list._array) {
                                    console.log(`单元格 ${i} 找到list._array:`, cellOutputs.list._array);
                                    console.log(`list._array长度:`, cellOutputs.list._array.length);
                                    // 直接访问_array
                                    const outputArray = cellOutputs.list._array;
                                    console.log(`单元格 ${i} list._array内容:`, outputArray);
                                    for (let j = 0; j < outputArray.length; j++) {
                                        const output = outputArray[j];
                                        console.log(`输出 ${j} 详细信息:`, output);
                                        console.log(`输出 ${j} 类型:`, typeof output);
                                        console.log(`输出 ${j} 属性:`, Object.keys(output));
                                        // 检查这个output是否又是一个ObservableList
                                        if (output._array && Array.isArray(output._array)) {
                                            console.log(`输出 ${j} 是ObservableList，访问其_array:`, output._array);
                                            // 如果output本身是ObservableList，访问其_array
                                            for (let k = 0; k < output._array.length; k++) {
                                                const actualOutput = output._array[k];
                                                console.log(`实际输出 ${k} 详细信息:`, actualOutput);
                                                console.log(`实际输出 ${k} 类型:`, typeof actualOutput);
                                                console.log(`实际输出 ${k} 属性:`, Object.keys(actualOutput));
                                                // 处理实际的输出项
                                                if (actualOutput.data && actualOutput.data['text/plain']) {
                                                    outputs.push(actualOutput.data['text/plain']);
                                                    console.log(`从实际输出 data['text/plain'] 获取:`, actualOutput.data['text/plain']);
                                                }
                                                else if (actualOutput.text) {
                                                    outputs.push(actualOutput.text);
                                                    console.log(`从实际输出 text 获取:`, actualOutput.text);
                                                }
                                                else if (actualOutput.output_type === 'stream' && actualOutput.name === 'stdout') {
                                                    outputs.push(actualOutput.text || '');
                                                    console.log(`从实际输出 stream stdout 获取:`, actualOutput.text);
                                                }
                                                else if (actualOutput.output_type === 'error') {
                                                    outputs.push(`错误: ${actualOutput.ename}: ${actualOutput.evalue}`);
                                                    console.log(`从实际输出 error 获取:`, `错误: ${actualOutput.ename}: ${actualOutput.evalue}`);
                                                }
                                                else if (actualOutput.output_type === 'execute_result') {
                                                    if (actualOutput.data && actualOutput.data['text/plain']) {
                                                        outputs.push(actualOutput.data['text/plain']);
                                                        console.log(`从实际输出 execute_result data['text/plain'] 获取:`, actualOutput.data['text/plain']);
                                                    }
                                                    else if (actualOutput.data && actualOutput.data['text/html']) {
                                                        outputs.push(actualOutput.data['text/html']);
                                                        console.log(`从实际输出 execute_result data['text/html'] 获取:`, actualOutput.data['text/html']);
                                                    }
                                                    else {
                                                        outputs.push(`[执行结果但无文本数据]`);
                                                        console.log(`实际输出执行结果但无文本数据:`, actualOutput);
                                                    }
                                                }
                                                else {
                                                    console.error(`单元格 ${i} 实际输出 ${k} 发现未知类型:`, actualOutput.output_type, '完整对象:', actualOutput);
                                                    outputs.push(`[实际输出类型: ${actualOutput.output_type || 'undefined'}]`);
                                                }
                                            }
                                        }
                                        else {
                                            // 如果output不是ObservableList，直接处理
                                            console.log(`输出 ${j} 完整结构:`, JSON.stringify(output, null, 2));
                                            // 首先尝试从_raw属性获取数据
                                            if (output._raw) {
                                                console.log(`从_raw属性获取数据:`, output._raw);
                                                if (output._raw.output_type === 'stream' && output._raw.name === 'stdout') {
                                                    outputs.push(output._raw.text || '');
                                                    console.log(`从_raw stream stdout 获取输出:`, output._raw.text);
                                                }
                                                else if (output._raw.output_type === 'stream' && output._raw.name === 'stderr') {
                                                    outputs.push(`错误输出: ${output._raw.text || ''}`);
                                                    console.log(`从_raw stream stderr 获取输出:`, output._raw.text);
                                                }
                                                else if (output._raw.output_type === 'execute_result') {
                                                    if (output._raw.data && output._raw.data['text/plain']) {
                                                        outputs.push(output._raw.data['text/plain']);
                                                        console.log(`从_raw execute_result data['text/plain'] 获取输出:`, output._raw.data['text/plain']);
                                                    }
                                                    else if (output._raw.data && output._raw.data['text/html']) {
                                                        outputs.push(output._raw.data['text/html']);
                                                        console.log(`从_raw execute_result data['text/html'] 获取输出:`, output._raw.data['text/html']);
                                                    }
                                                    else {
                                                        outputs.push(`[执行结果但无文本数据]`);
                                                        console.log(`_raw执行结果但无文本数据:`, output._raw);
                                                    }
                                                }
                                                else if (output._raw.output_type === 'error') {
                                                    outputs.push(`错误: ${output._raw.ename}: ${output._raw.evalue}`);
                                                    console.log(`从_raw error 获取输出:`, `错误: ${output._raw.ename}: ${output._raw.evalue}`);
                                                }
                                                else {
                                                    console.log(`_raw未知输出类型:`, output._raw.output_type);
                                                    outputs.push(`[_raw输出类型: ${output._raw.output_type}]`);
                                                }
                                            }
                                            // 尝试从_text属性获取数据
                                            else if (output._text && output._text._text) {
                                                outputs.push(output._text._text);
                                                console.log(`从_text._text 获取输出:`, output._text._text);
                                            }
                                            // 尝试从_rawData属性获取数据
                                            else if (output._rawData) {
                                                console.log(`从_rawData属性获取数据:`, output._rawData);
                                                if (output._rawData['application/vnd.jupyter.stdout']) {
                                                    outputs.push(output._rawData['application/vnd.jupyter.stdout']);
                                                    console.log(`从_rawData stdout 获取输出:`, output._rawData['application/vnd.jupyter.stdout']);
                                                }
                                                else if (output._rawData['application/vnd.jupyter.stderr']) {
                                                    outputs.push(`错误输出: ${output._rawData['application/vnd.jupyter.stderr']}`);
                                                    console.log(`从_rawData stderr 获取输出:`, output._rawData['application/vnd.jupyter.stderr']);
                                                }
                                                else {
                                                    // 尝试获取第一个可用的数据
                                                    const keys = Object.keys(output._rawData);
                                                    if (keys.length > 0) {
                                                        outputs.push(output._rawData[keys[0]]);
                                                        console.log(`从_rawData ${keys[0]} 获取输出:`, output._rawData[keys[0]]);
                                                    }
                                                }
                                            }
                                            // 尝试从顶层属性获取数据
                                            else if (output.data && output.data['text/plain']) {
                                                outputs.push(output.data['text/plain']);
                                                console.log(`从 data['text/plain'] 获取输出:`, output.data['text/plain']);
                                            }
                                            else if (output.text) {
                                                outputs.push(output.text);
                                                console.log(`从 text 获取输出:`, output.text);
                                            }
                                            else if (output.output_type === 'stream' && output.name === 'stdout') {
                                                outputs.push(output.text || '');
                                                console.log(`从 stream stdout 获取输出:`, output.text);
                                            }
                                            else if (output.output_type === 'error') {
                                                outputs.push(`错误: ${output.ename}: ${output.evalue}`);
                                                console.log(`从 error 获取输出:`, `错误: ${output.ename}: ${output.evalue}`);
                                            }
                                            else if (output.output_type === 'execute_result') {
                                                // 处理执行结果
                                                if (output.data && output.data['text/plain']) {
                                                    outputs.push(output.data['text/plain']);
                                                    console.log(`从 execute_result data['text/plain'] 获取输出:`, output.data['text/plain']);
                                                }
                                                else if (output.data && output.data['text/html']) {
                                                    outputs.push(output.data['text/html']);
                                                    console.log(`从 execute_result data['text/html'] 获取输出:`, output.data['text/html']);
                                                }
                                                else {
                                                    outputs.push(`[执行结果但无文本数据]`);
                                                    console.log(`执行结果但无文本数据:`, output);
                                                }
                                            }
                                            else {
                                                // 尝试其他可能的属性
                                                if (output.value !== undefined) {
                                                    outputs.push(String(output.value));
                                                    console.log(`从 value 获取输出:`, output.value);
                                                }
                                                else if (output.result !== undefined) {
                                                    outputs.push(String(output.result));
                                                    console.log(`从 result 获取输出:`, output.result);
                                                }
                                                else {
                                                    // 如果所有方法都失败，打印整个 output 对象
                                                    console.error(`单元格 ${i} 输出 ${j} 所有方法都失败，完整输出对象:`, output);
                                                    outputs.push(`[单元格 ${i} 输出获取失败]`);
                                                    console.log(`所有方法都失败，添加默认消息:`, `[单元格 ${i} 输出获取失败]`);
                                                }
                                            }
                                        }
                                    }
                                }
                                // 检查是否有length属性（直接访问）
                                else if (cellOutputs.length !== undefined) {
                                    console.log(`单元格 ${i} 输出数量:`, cellOutputs.length);
                                    // 尝试不同的迭代方法
                                    try {
                                        // 方法1: 使用for循环
                                        for (let j = 0; j < cellOutputs.length; j++) {
                                            const output = cellOutputs.get ? cellOutputs.get(j) : cellOutputs[j];
                                            console.log(`输出 ${j} 详细信息:`, output);
                                            console.log(`输出 ${j} 类型:`, typeof output);
                                            console.log(`输出 ${j} 属性:`, Object.keys(output));
                                            // 尝试获取输出内容
                                            if (output.data && output.data['text/plain']) {
                                                outputs.push(output.data['text/plain']);
                                                console.log(`从 data['text/plain'] 获取输出:`, output.data['text/plain']);
                                            }
                                            else if (output.text) {
                                                outputs.push(output.text);
                                                console.log(`从 text 获取输出:`, output.text);
                                            }
                                            else if (output.output_type === 'stream' && output.name === 'stdout') {
                                                outputs.push(output.text || '');
                                                console.log(`从 stream stdout 获取输出:`, output.text);
                                            }
                                            else if (output.output_type === 'error') {
                                                outputs.push(`错误: ${output.ename}: ${output.evalue}`);
                                                console.log(`从 error 获取输出:`, `错误: ${output.ename}: ${output.evalue}`);
                                            }
                                            else {
                                                outputs.push(`[输出类型: ${output.output_type}]`);
                                                console.log(`未知输出类型:`, output.output_type);
                                            }
                                        }
                                    }
                                    catch (e) {
                                        console.log('for循环失败，尝试其他方法:', e);
                                        // 方法2: 尝试使用forEach
                                        try {
                                            if (typeof cellOutputs.forEach === 'function') {
                                                cellOutputs.forEach((output, index) => {
                                                    console.log(`输出 ${index} (forEach):`, output);
                                                    if (output.data && output.data['text/plain']) {
                                                        outputs.push(output.data['text/plain']);
                                                    }
                                                    else if (output.text) {
                                                        outputs.push(output.text);
                                                    }
                                                });
                                            }
                                        }
                                        catch (e2) {
                                            console.log('forEach失败:', e2);
                                        }
                                        // 方法3: 尝试使用toArray
                                        try {
                                            if (typeof cellOutputs.toArray === 'function') {
                                                const outputArray = cellOutputs.toArray();
                                                console.log('toArray结果:', outputArray);
                                                outputArray.forEach((output, index) => {
                                                    if (output.data && output.data['text/plain']) {
                                                        outputs.push(output.data['text/plain']);
                                                    }
                                                    else if (output.text) {
                                                        outputs.push(output.text);
                                                    }
                                                });
                                            }
                                        }
                                        catch (e3) {
                                            console.log('toArray失败:', e3);
                                        }
                                    }
                                }
                                else {
                                    console.log(`单元格 ${i} outputs没有list._array或length属性`);
                                }
                                if (outputs.length === 0) {
                                    console.log(`单元格 ${i} 没有找到有效输出`);
                                    outputs = ['[无输出]'];
                                }
                            }
                            else {
                                console.log(`单元格 ${i} 没有outputs属性`);
                                outputs = ['[无输出]'];
                            }
                            console.log(`单元格 ${i} 最终输出:`, outputs);
                            console.log(`=== 单元格 ${i} 输出调试结束 ===`);
                        }
                        catch (e) {
                            console.error(`获取单元格 ${i} 输出失败:`, e);
                            outputs = ['[输出获取失败]'];
                        }
                    }
                    const cellInfo = {
                        index: i,
                        type: cell.type,
                        source: source,
                        outputs: cell.type === 'code' ? outputs : undefined
                    };
                    cells.push(cellInfo);
                    console.log(`成功处理单元格 ${i}, 类型: ${cell.type}, 内容长度: ${source.length}`);
                }
                catch (cellError) {
                    console.error(`处理单元格 ${i} 时出错:`, cellError);
                }
            }
            console.log(`成功获取到 ${cells.length} 个单元格`);
            return cells;
        }
        catch (error) {
            console.error('读取所有单元格失败:', error);
            return null;
        }
    }
    /**
     * 读取特定单元格
     * @param cellIndex 单元格索引
     */
    async readCell(cellIndex) {
        try {
            console.log(`尝试读取单元格 ${cellIndex}...`);
            // 详细检查notebookTracker
            if (!this.notebookTracker) {
                console.error('notebookTracker未定义');
                return null;
            }
            // 详细检查currentWidget
            if (!this.notebookTracker.currentWidget) {
                console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
                return null;
            }
            const notebook = this.notebookTracker.currentWidget;
            // 详细检查content
            if (!notebook.content) {
                console.error('notebook.content未定义');
                return null;
            }
            // 详细检查model
            if (!notebook.content.model) {
                console.error('notebook.content.model未定义');
                return null;
            }
            const model = notebook.content.model;
            // 详细检查cells
            if (!model.cells) {
                console.error('model.cells未定义');
                return null;
            }
            console.log('单元格数量:', model.cells.length);
            if (model.cells.length === 0) {
                console.warn('Notebook没有单元格');
                return null;
            }
            if (cellIndex < 0 || cellIndex >= model.cells.length) {
                console.warn(`单元格索引 ${cellIndex} 超出范围 (0-${model.cells.length - 1})`);
                return null;
            }
            // 获取指定单元格
            const cell = model.cells.get(cellIndex);
            if (!cell) {
                console.error(`无法获取单元格 ${cellIndex}`);
                return null;
            }
            // 获取单元格内容
            let source = [];
            try {
                // 尝试不同的方法获取单元格内容
                let content = '';
                // 方法1: 尝试访问sharedModel.source
                if (cell.sharedModel && cell.sharedModel.source) {
                    const source = cell.sharedModel.source;
                    content = Array.isArray(source) ? source.join('\n') : source;
                    console.log('使用方法1 (sharedModel.source) 获取内容:', content);
                }
                // 方法2: 尝试访问sharedModel.getSource()
                else if (cell.sharedModel && typeof cell.sharedModel.getSource === 'function') {
                    try {
                        content = cell.sharedModel.getSource();
                        console.log('使用方法2 (sharedModel.getSource()) 获取内容:', content);
                    }
                    catch (e) {
                        console.log('sharedModel.getSource() 调用失败:', e);
                    }
                }
                // 方法3: 尝试访问value.text
                else if (cell.value && cell.value.text) {
                    content = cell.value.text;
                    console.log('使用方法3 (value.text) 获取内容:', content);
                }
                // 方法4: 尝试访问source
                else if (cell.source) {
                    content = Array.isArray(cell.source)
                        ? cell.source.join('\n')
                        : cell.source;
                    console.log('使用方法4 (source) 获取内容:', content);
                }
                // 方法5: 尝试访问text
                else if (cell.text) {
                    content = cell.text;
                    console.log('使用方法5 (text) 获取内容:', content);
                }
                // 方法6: 尝试使用toString()并检查是否为字符串
                else {
                    const toStringResult = cell.toString();
                    console.log('toString()结果:', toStringResult, '类型:', typeof toStringResult);
                    if (typeof toStringResult === 'string' && toStringResult !== '[object Object]') {
                        content = toStringResult;
                    }
                    else {
                        console.warn(`单元格 ${cellIndex} toString()返回非字符串或[object Object]:`, typeof toStringResult);
                        content = `[单元格 ${cellIndex} 内容无法获取]`;
                    }
                }
                source = content ? content.split('\n') : [''];
                console.log(`单元格 ${cellIndex} 内容:`, content.substring(0, 100) + (content.length > 100 ? '...' : ''));
            }
            catch (e) {
                console.error(`获取单元格 ${cellIndex} 内容失败:`, e);
                source = [`[单元格 ${cellIndex} 内容获取失败]`];
            }
            // 获取单元格输出
            let outputs = [];
            if (cell.type === 'code') {
                try {
                    // 尝试获取输出
                    if (cell.outputs && Array.isArray(cell.outputs)) {
                        const cellOutputs = cell.outputs;
                        console.log(`单元格 ${cellIndex} 输出数量:`, cellOutputs.length);
                        for (let j = 0; j < cellOutputs.length; j++) {
                            const output = cellOutputs[j];
                            console.log(`输出 ${j}:`, output);
                            // 尝试获取输出内容
                            if (output.data && output.data['text/plain']) {
                                outputs.push(output.data['text/plain']);
                            }
                            else if (output.text) {
                                outputs.push(output.text);
                            }
                            else if (output.output_type === 'stream' && output.name === 'stdout') {
                                outputs.push(output.text || '');
                            }
                            else if (output.output_type === 'error') {
                                outputs.push(`错误: ${output.ename}: ${output.evalue}`);
                            }
                            else {
                                outputs.push(`[输出类型: ${output.output_type}]`);
                            }
                        }
                    }
                    else {
                        console.log(`单元格 ${cellIndex} 没有输出或输出格式不正确`);
                        outputs = ['[无输出]'];
                    }
                }
                catch (e) {
                    console.error(`获取单元格 ${cellIndex} 输出失败:`, e);
                    outputs = ['[输出获取失败]'];
                }
            }
            const cellInfo = {
                index: cellIndex,
                type: cell.type,
                source: source,
                outputs: cell.type === 'code' ? outputs : undefined
            };
            console.log(`成功获取单元格 ${cellIndex}, 类型: ${cell.type}, 内容长度: ${source.length}`);
            return cellInfo;
        }
        catch (error) {
            console.error(`读取单元格 ${cellIndex} 失败:`, error);
            return null;
        }
    }
    /**
     * 添加Markdown单元格
     * @param cellSource Markdown内容
     */
    async appendMarkdownCell(cellSource) {
        try {
            console.log('添加Markdown单元格:', cellSource);
            console.log('注意：此功能需要进一步实现');
            return '功能暂未实现';
        }
        catch (error) {
            console.error('添加Markdown单元格失败:', error);
            return null;
        }
    }
    /**
     * 添加代码单元格
     * @param cellSource 代码内容
     */
    async appendExecuteCodeCell(cellSource) {
        try {
            console.log('添加代码单元格:', cellSource);
            console.log('注意：此功能需要进一步实现');
            return '功能暂未实现';
        }
        catch (error) {
            console.error('添加代码单元格失败:', error);
            return null;
        }
    }
    /**
     * 执行单元格
     * @param cellIndex 单元格索引
     * @param timeout 超时时间（秒）
     */
    async executeCell(cellIndex, timeout = 30) {
        try {
            console.log(`执行单元格 ${cellIndex}...`);
            console.log('注意：此功能需要进一步实现');
            return '功能暂未实现';
        }
        catch (error) {
            console.error(`执行单元格 ${cellIndex} 失败:`, error);
            return null;
        }
    }
    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return this.isConnected;
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.e12b3d5768e5b9bb66d0.js.map