"use strict";
(self["webpackChunkjupyterchatz"] = self["webpackChunkjupyterchatz"] || []).push([["style_index_js"],{

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/* 聊天窗口容器 */
.jp-AIChat-widget {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 300px;
}

.jp-AIChat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--jp-layout-color1);
  color: var(--jp-content-font-color1);
}

/* 聊天头部 */
.jp-AIChat-header {
  padding: 8px 16px;
  border-bottom: 1px solid var(--jp-border-color1);
  background-color: var(--jp-layout-color2);
}

.jp-AIChat-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

/* 聊天消息区域 */
.jp-AIChat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 欢迎消息 */
.jp-AIChat-welcome {
  text-align: center;
  margin: auto;
  color: var(--jp-content-font-color2);
}

/* 消息样式 */
.jp-AIChat-message {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 8px;
  word-break: break-word;
  line-height: 1.5;
}

/* 用户消息 */
.jp-AIChat-userMessage {
  align-self: flex-end;
  background-color: var(--jp-brand-color1);
  color: white;
}

/* AI助手消息 */
.jp-AIChat-assistantMessage {
  align-self: flex-start;
  background-color: var(--jp-layout-color2);
  border: 1px solid var(--jp-border-color1);
}

/* 消息内容 */
.jp-AIChat-messageContent {
  font-size: 13px;
}

/* 加载动画 */
.jp-AIChat-loading {
  position: relative;
  min-width: 60px;
}

.jp-AIChat-loading:after {
  content: '...';
  animation: dots 1.5s steps(5, end) infinite;
}

@keyframes dots {
  0%, 20% {
    content: '.';
  }
  40% {
    content: '..';
  }
  60%, 100% {
    content: '...';
  }
}

/* 输入区域 */
.jp-AIChat-inputArea {
  display: flex;
  padding: 12px;
  border-top: 1px solid var(--jp-border-color1);
  background-color: var(--jp-layout-color1);
}

/* 文本输入框 */
.jp-AIChat-input {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 8px 12px;
  border: 1px solid var(--jp-border-color1);
  border-radius: 4px;
  background-color: var(--jp-layout-color0);
  color: var(--jp-content-font-color1);
  font-size: 13px;
  resize: none;
  outline: none;
  font-family: var(--jp-code-font-family);
}

.jp-AIChat-input:focus {
  border-color: var(--jp-brand-color1);
}

/* 发送按钮 */
.jp-AIChat-sendButton {
  margin-left: 8px;
  padding: 0 16px;
  height: 40px;
  border: none;
  border-radius: 4px;
  background-color: var(--jp-brand-color1);
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.jp-AIChat-sendButton:hover {
  background-color: var(--jp-brand-color0);
}

.jp-AIChat-sendButton:disabled {
  background-color: var(--jp-layout-color3);
  cursor: not-allowed;
}

/* 代码块样式 */
.jp-AIChat-codeBlock {
  margin: 8px 0;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--jp-border-color2);
  background-color: var(--jp-layout-color0);
}

.jp-AIChat-codeHeader {
  background-color: var(--jp-layout-color2);
  padding: 4px 8px;
  border-bottom: 1px solid var(--jp-border-color1);
  font-size: 11px;
  color: var(--jp-content-font-color2);
}

.jp-AIChat-codeLanguage {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.jp-AIChat-codeContent {
  margin: 0;
  padding: 12px;
  background-color: var(--jp-layout-color0);
  overflow-x: auto;
  font-family: var(--jp-code-font-family);
  font-size: 12px;
  line-height: 1.4;
  color: var(--jp-content-font-color1);
}

.jp-AIChat-codeContent code {
  background: none;
  padding: 0;
  border: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

/* 文本内容样式 */
.jp-AIChat-textContent {
  line-height: 1.6;
}

.jp-AIChat-textContent strong {
  font-weight: 600;
  color: var(--jp-content-font-color1);
}`, "",{"version":3,"sources":["webpack://./style/base.css"],"names":[],"mappings":"AAAA,WAAW;AACX;EACE,aAAa;EACb,sBAAsB;EACtB,YAAY;EACZ,gBAAgB;AAClB;;AAEA;EACE,aAAa;EACb,sBAAsB;EACtB,YAAY;EACZ,yCAAyC;EACzC,oCAAoC;AACtC;;AAEA,SAAS;AACT;EACE,iBAAiB;EACjB,gDAAgD;EAChD,yCAAyC;AAC3C;;AAEA;EACE,SAAS;EACT,eAAe;EACf,gBAAgB;AAClB;;AAEA,WAAW;AACX;EACE,OAAO;EACP,gBAAgB;EAChB,aAAa;EACb,aAAa;EACb,sBAAsB;EACtB,SAAS;AACX;;AAEA,SAAS;AACT;EACE,kBAAkB;EAClB,YAAY;EACZ,oCAAoC;AACtC;;AAEA,SAAS;AACT;EACE,aAAa;EACb,sBAAsB;EACtB,cAAc;EACd,iBAAiB;EACjB,kBAAkB;EAClB,sBAAsB;EACtB,gBAAgB;AAClB;;AAEA,SAAS;AACT;EACE,oBAAoB;EACpB,wCAAwC;EACxC,YAAY;AACd;;AAEA,WAAW;AACX;EACE,sBAAsB;EACtB,yCAAyC;EACzC,yCAAyC;AAC3C;;AAEA,SAAS;AACT;EACE,eAAe;AACjB;;AAEA,SAAS;AACT;EACE,kBAAkB;EAClB,eAAe;AACjB;;AAEA;EACE,cAAc;EACd,2CAA2C;AAC7C;;AAEA;EACE;IACE,YAAY;EACd;EACA;IACE,aAAa;EACf;EACA;IACE,cAAc;EAChB;AACF;;AAEA,SAAS;AACT;EACE,aAAa;EACb,aAAa;EACb,6CAA6C;EAC7C,yCAAyC;AAC3C;;AAEA,UAAU;AACV;EACE,OAAO;EACP,gBAAgB;EAChB,iBAAiB;EACjB,iBAAiB;EACjB,yCAAyC;EACzC,kBAAkB;EAClB,yCAAyC;EACzC,oCAAoC;EACpC,eAAe;EACf,YAAY;EACZ,aAAa;EACb,uCAAuC;AACzC;;AAEA;EACE,oCAAoC;AACtC;;AAEA,SAAS;AACT;EACE,gBAAgB;EAChB,eAAe;EACf,YAAY;EACZ,YAAY;EACZ,kBAAkB;EAClB,wCAAwC;EACxC,YAAY;EACZ,eAAe;EACf,eAAe;EACf,iCAAiC;AACnC;;AAEA;EACE,wCAAwC;AAC1C;;AAEA;EACE,yCAAyC;EACzC,mBAAmB;AACrB;;AAEA,UAAU;AACV;EACE,aAAa;EACb,kBAAkB;EAClB,gBAAgB;EAChB,yCAAyC;EACzC,yCAAyC;AAC3C;;AAEA;EACE,yCAAyC;EACzC,gBAAgB;EAChB,gDAAgD;EAChD,eAAe;EACf,oCAAoC;AACtC;;AAEA;EACE,gBAAgB;EAChB,yBAAyB;EACzB,qBAAqB;AACvB;;AAEA;EACE,SAAS;EACT,aAAa;EACb,yCAAyC;EACzC,gBAAgB;EAChB,uCAAuC;EACvC,eAAe;EACf,gBAAgB;EAChB,oCAAoC;AACtC;;AAEA;EACE,gBAAgB;EAChB,UAAU;EACV,YAAY;EACZ,oBAAoB;EACpB,kBAAkB;EAClB,cAAc;AAChB;;AAEA,WAAW;AACX;EACE,gBAAgB;AAClB;;AAEA;EACE,gBAAgB;EAChB,oCAAoC;AACtC","sourcesContent":["/* 聊天窗口容器 */\n.jp-AIChat-widget {\n  display: flex;\n  flex-direction: column;\n  height: 100%;\n  min-width: 300px;\n}\n\n.jp-AIChat-container {\n  display: flex;\n  flex-direction: column;\n  height: 100%;\n  background-color: var(--jp-layout-color1);\n  color: var(--jp-content-font-color1);\n}\n\n/* 聊天头部 */\n.jp-AIChat-header {\n  padding: 8px 16px;\n  border-bottom: 1px solid var(--jp-border-color1);\n  background-color: var(--jp-layout-color2);\n}\n\n.jp-AIChat-header h3 {\n  margin: 0;\n  font-size: 14px;\n  font-weight: 600;\n}\n\n/* 聊天消息区域 */\n.jp-AIChat-messages {\n  flex: 1;\n  overflow-y: auto;\n  padding: 16px;\n  display: flex;\n  flex-direction: column;\n  gap: 16px;\n}\n\n/* 欢迎消息 */\n.jp-AIChat-welcome {\n  text-align: center;\n  margin: auto;\n  color: var(--jp-content-font-color2);\n}\n\n/* 消息样式 */\n.jp-AIChat-message {\n  display: flex;\n  flex-direction: column;\n  max-width: 85%;\n  padding: 8px 12px;\n  border-radius: 8px;\n  word-break: break-word;\n  line-height: 1.5;\n}\n\n/* 用户消息 */\n.jp-AIChat-userMessage {\n  align-self: flex-end;\n  background-color: var(--jp-brand-color1);\n  color: white;\n}\n\n/* AI助手消息 */\n.jp-AIChat-assistantMessage {\n  align-self: flex-start;\n  background-color: var(--jp-layout-color2);\n  border: 1px solid var(--jp-border-color1);\n}\n\n/* 消息内容 */\n.jp-AIChat-messageContent {\n  font-size: 13px;\n}\n\n/* 加载动画 */\n.jp-AIChat-loading {\n  position: relative;\n  min-width: 60px;\n}\n\n.jp-AIChat-loading:after {\n  content: '...';\n  animation: dots 1.5s steps(5, end) infinite;\n}\n\n@keyframes dots {\n  0%, 20% {\n    content: '.';\n  }\n  40% {\n    content: '..';\n  }\n  60%, 100% {\n    content: '...';\n  }\n}\n\n/* 输入区域 */\n.jp-AIChat-inputArea {\n  display: flex;\n  padding: 12px;\n  border-top: 1px solid var(--jp-border-color1);\n  background-color: var(--jp-layout-color1);\n}\n\n/* 文本输入框 */\n.jp-AIChat-input {\n  flex: 1;\n  min-height: 40px;\n  max-height: 120px;\n  padding: 8px 12px;\n  border: 1px solid var(--jp-border-color1);\n  border-radius: 4px;\n  background-color: var(--jp-layout-color0);\n  color: var(--jp-content-font-color1);\n  font-size: 13px;\n  resize: none;\n  outline: none;\n  font-family: var(--jp-code-font-family);\n}\n\n.jp-AIChat-input:focus {\n  border-color: var(--jp-brand-color1);\n}\n\n/* 发送按钮 */\n.jp-AIChat-sendButton {\n  margin-left: 8px;\n  padding: 0 16px;\n  height: 40px;\n  border: none;\n  border-radius: 4px;\n  background-color: var(--jp-brand-color1);\n  color: white;\n  font-size: 13px;\n  cursor: pointer;\n  transition: background-color 0.2s;\n}\n\n.jp-AIChat-sendButton:hover {\n  background-color: var(--jp-brand-color0);\n}\n\n.jp-AIChat-sendButton:disabled {\n  background-color: var(--jp-layout-color3);\n  cursor: not-allowed;\n}\n\n/* 代码块样式 */\n.jp-AIChat-codeBlock {\n  margin: 8px 0;\n  border-radius: 6px;\n  overflow: hidden;\n  border: 1px solid var(--jp-border-color2);\n  background-color: var(--jp-layout-color0);\n}\n\n.jp-AIChat-codeHeader {\n  background-color: var(--jp-layout-color2);\n  padding: 4px 8px;\n  border-bottom: 1px solid var(--jp-border-color1);\n  font-size: 11px;\n  color: var(--jp-content-font-color2);\n}\n\n.jp-AIChat-codeLanguage {\n  font-weight: 600;\n  text-transform: uppercase;\n  letter-spacing: 0.5px;\n}\n\n.jp-AIChat-codeContent {\n  margin: 0;\n  padding: 12px;\n  background-color: var(--jp-layout-color0);\n  overflow-x: auto;\n  font-family: var(--jp-code-font-family);\n  font-size: 12px;\n  line-height: 1.4;\n  color: var(--jp-content-font-color1);\n}\n\n.jp-AIChat-codeContent code {\n  background: none;\n  padding: 0;\n  border: none;\n  font-family: inherit;\n  font-size: inherit;\n  color: inherit;\n}\n\n/* 文本内容样式 */\n.jp-AIChat-textContent {\n  line-height: 1.6;\n}\n\n.jp-AIChat-textContent strong {\n  font-weight: 600;\n  color: var(--jp-content-font-color1);\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/api.js":
/*!*****************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/api.js ***!
  \*****************************************************/
/***/ ((module) => {



/*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
module.exports = function (cssWithMappingToString) {
  var list = [];

  // return the list of modules as css string
  list.toString = function toString() {
    return this.map(function (item) {
      var content = "";
      var needLayer = typeof item[5] !== "undefined";
      if (item[4]) {
        content += "@supports (".concat(item[4], ") {");
      }
      if (item[2]) {
        content += "@media ".concat(item[2], " {");
      }
      if (needLayer) {
        content += "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {");
      }
      content += cssWithMappingToString(item);
      if (needLayer) {
        content += "}";
      }
      if (item[2]) {
        content += "}";
      }
      if (item[4]) {
        content += "}";
      }
      return content;
    }).join("");
  };

  // import a list of modules into the list
  list.i = function i(modules, media, dedupe, supports, layer) {
    if (typeof modules === "string") {
      modules = [[null, modules, undefined]];
    }
    var alreadyImportedModules = {};
    if (dedupe) {
      for (var k = 0; k < this.length; k++) {
        var id = this[k][0];
        if (id != null) {
          alreadyImportedModules[id] = true;
        }
      }
    }
    for (var _k = 0; _k < modules.length; _k++) {
      var item = [].concat(modules[_k]);
      if (dedupe && alreadyImportedModules[item[0]]) {
        continue;
      }
      if (typeof layer !== "undefined") {
        if (typeof item[5] === "undefined") {
          item[5] = layer;
        } else {
          item[1] = "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {").concat(item[1], "}");
          item[5] = layer;
        }
      }
      if (media) {
        if (!item[2]) {
          item[2] = media;
        } else {
          item[1] = "@media ".concat(item[2], " {").concat(item[1], "}");
          item[2] = media;
        }
      }
      if (supports) {
        if (!item[4]) {
          item[4] = "".concat(supports);
        } else {
          item[1] = "@supports (".concat(item[4], ") {").concat(item[1], "}");
          item[4] = supports;
        }
      }
      list.push(item);
    }
  };
  return list;
};

/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/sourceMaps.js":
/*!************************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/sourceMaps.js ***!
  \************************************************************/
/***/ ((module) => {



module.exports = function (item) {
  var content = item[1];
  var cssMapping = item[3];
  if (!cssMapping) {
    return content;
  }
  if (typeof btoa === "function") {
    var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(cssMapping))));
    var data = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(base64);
    var sourceMapping = "/*# ".concat(data, " */");
    return [content].concat([sourceMapping]).join("\n");
  }
  return [content].join("\n");
};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js":
/*!****************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js ***!
  \****************************************************************************/
/***/ ((module) => {



var stylesInDOM = [];
function getIndexByIdentifier(identifier) {
  var result = -1;
  for (var i = 0; i < stylesInDOM.length; i++) {
    if (stylesInDOM[i].identifier === identifier) {
      result = i;
      break;
    }
  }
  return result;
}
function modulesToDom(list, options) {
  var idCountMap = {};
  var identifiers = [];
  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    var id = options.base ? item[0] + options.base : item[0];
    var count = idCountMap[id] || 0;
    var identifier = "".concat(id, " ").concat(count);
    idCountMap[id] = count + 1;
    var indexByIdentifier = getIndexByIdentifier(identifier);
    var obj = {
      css: item[1],
      media: item[2],
      sourceMap: item[3],
      supports: item[4],
      layer: item[5]
    };
    if (indexByIdentifier !== -1) {
      stylesInDOM[indexByIdentifier].references++;
      stylesInDOM[indexByIdentifier].updater(obj);
    } else {
      var updater = addElementStyle(obj, options);
      options.byIndex = i;
      stylesInDOM.splice(i, 0, {
        identifier: identifier,
        updater: updater,
        references: 1
      });
    }
    identifiers.push(identifier);
  }
  return identifiers;
}
function addElementStyle(obj, options) {
  var api = options.domAPI(options);
  api.update(obj);
  var updater = function updater(newObj) {
    if (newObj) {
      if (newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap && newObj.supports === obj.supports && newObj.layer === obj.layer) {
        return;
      }
      api.update(obj = newObj);
    } else {
      api.remove();
    }
  };
  return updater;
}
module.exports = function (list, options) {
  options = options || {};
  list = list || [];
  var lastIdentifiers = modulesToDom(list, options);
  return function update(newList) {
    newList = newList || [];
    for (var i = 0; i < lastIdentifiers.length; i++) {
      var identifier = lastIdentifiers[i];
      var index = getIndexByIdentifier(identifier);
      stylesInDOM[index].references--;
    }
    var newLastIdentifiers = modulesToDom(newList, options);
    for (var _i = 0; _i < lastIdentifiers.length; _i++) {
      var _identifier = lastIdentifiers[_i];
      var _index = getIndexByIdentifier(_identifier);
      if (stylesInDOM[_index].references === 0) {
        stylesInDOM[_index].updater();
        stylesInDOM.splice(_index, 1);
      }
    }
    lastIdentifiers = newLastIdentifiers;
  };
};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/insertBySelector.js":
/*!********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/insertBySelector.js ***!
  \********************************************************************/
/***/ ((module) => {



var memo = {};

/* istanbul ignore next  */
function getTarget(target) {
  if (typeof memo[target] === "undefined") {
    var styleTarget = document.querySelector(target);

    // Special case to return head of iframe instead of iframe itself
    if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
      try {
        // This will throw an exception if access to iframe is blocked
        // due to cross-origin restrictions
        styleTarget = styleTarget.contentDocument.head;
      } catch (e) {
        // istanbul ignore next
        styleTarget = null;
      }
    }
    memo[target] = styleTarget;
  }
  return memo[target];
}

/* istanbul ignore next  */
function insertBySelector(insert, style) {
  var target = getTarget(insert);
  if (!target) {
    throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
  }
  target.appendChild(style);
}
module.exports = insertBySelector;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/insertStyleElement.js":
/*!**********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/insertStyleElement.js ***!
  \**********************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function insertStyleElement(options) {
  var element = document.createElement("style");
  options.setAttributes(element, options.attributes);
  options.insert(element, options.options);
  return element;
}
module.exports = insertStyleElement;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js":
/*!**********************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js ***!
  \**********************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {



/* istanbul ignore next  */
function setAttributesWithoutAttributes(styleElement) {
  var nonce =  true ? __webpack_require__.nc : 0;
  if (nonce) {
    styleElement.setAttribute("nonce", nonce);
  }
}
module.exports = setAttributesWithoutAttributes;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/styleDomAPI.js":
/*!***************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/styleDomAPI.js ***!
  \***************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function apply(styleElement, options, obj) {
  var css = "";
  if (obj.supports) {
    css += "@supports (".concat(obj.supports, ") {");
  }
  if (obj.media) {
    css += "@media ".concat(obj.media, " {");
  }
  var needLayer = typeof obj.layer !== "undefined";
  if (needLayer) {
    css += "@layer".concat(obj.layer.length > 0 ? " ".concat(obj.layer) : "", " {");
  }
  css += obj.css;
  if (needLayer) {
    css += "}";
  }
  if (obj.media) {
    css += "}";
  }
  if (obj.supports) {
    css += "}";
  }
  var sourceMap = obj.sourceMap;
  if (sourceMap && typeof btoa !== "undefined") {
    css += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))), " */");
  }

  // For old IE
  /* istanbul ignore if  */
  options.styleTagTransform(css, styleElement, options.options);
}
function removeStyleElement(styleElement) {
  // istanbul ignore if
  if (styleElement.parentNode === null) {
    return false;
  }
  styleElement.parentNode.removeChild(styleElement);
}

/* istanbul ignore next  */
function domAPI(options) {
  if (typeof document === "undefined") {
    return {
      update: function update() {},
      remove: function remove() {}
    };
  }
  var styleElement = options.insertStyleElement(options);
  return {
    update: function update(obj) {
      apply(styleElement, options, obj);
    },
    remove: function remove() {
      removeStyleElement(styleElement);
    }
  };
}
module.exports = domAPI;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/styleTagTransform.js":
/*!*********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/styleTagTransform.js ***!
  \*********************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function styleTagTransform(css, styleElement) {
  if (styleElement.styleSheet) {
    styleElement.styleSheet.cssText = css;
  } else {
    while (styleElement.firstChild) {
      styleElement.removeChild(styleElement.firstChild);
    }
    styleElement.appendChild(document.createTextNode(css));
  }
}
module.exports = styleTagTransform;

/***/ }),

/***/ "./style/base.css":
/*!************************!*\
  !*** ./style/base.css ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleDomAPI.js */ "./node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertBySelector.js */ "./node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertStyleElement.js */ "./node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleTagTransform.js */ "./node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");
    
options.domAPI = (_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ }),

/***/ "./style/index.js":
/*!************************!*\
  !*** ./style/index.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _base_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./base.css */ "./style/base.css");



/***/ })

}]);
//# sourceMappingURL=style_index_js.bf362227005d44d58ca8.js.map