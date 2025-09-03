var statistics;
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./src/statistics/components/App.js":
/*!******************************************!*\
  !*** ./src/statistics/components/App.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _Router_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./Router.js */ "./src/statistics/components/Router.js");
/* harmony import */ var _tools_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../tools.js */ "./src/tools.js");
/* harmony import */ var _views_RootComponent_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../views/RootComponent.js */ "./src/statistics/views/RootComponent.js");
/* harmony import */ var _Controller_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./Controller.js */ "./src/statistics/components/Controller.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");






var AppClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default().Application.extend({
  channelName: "app",
  radioEvents: {
    navigate: "onNavigate",
    "show:modal": "onShowModal",
    "entry:delete": "onDelete",
    "entry:export": "onEntryExport",
    "entry:duplicate": "onEntryDuplicate",
    "criterion:delete": "onDelete"
  },
  region: "#js-main-area",
  onBeforeStart: function onBeforeStart(app, options) {
    console.log(" - AppClass : Initializing UI components");
    this.rootView = new _views_RootComponent_js__WEBPACK_IMPORTED_MODULE_3__["default"]();
    this.controller = new _Controller_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      rootView: this.rootView
    });
    this.router = new _Router_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      controller: this.controller
    });
  },
  onStart: function onStart(app, options) {
    this.showView(this.rootView);
    console.log(" - AppClass : Starting the js history");
    (0,_tools_js__WEBPACK_IMPORTED_MODULE_2__.hideLoader)();
    backbone__WEBPACK_IMPORTED_MODULE_0___default().history.start();
  },
  onEntryExport: function onEntryExport(model) {
    this.controller.showEntryExport(model);
  },
  onEntryDuplicate: function onEntryDuplicate(model) {
    this.controller.showEntryDuplicate(model);
  },
  onNavigate: function onNavigate(route_name, parameters) {
    console.log(" - AppClass.onNavigate : %s", route_name);
    var dest_route = route_name;
    if (!_.isUndefined(parameters)) {
      dest_route += "/" + parameters;
    }
    window.location.hash = dest_route;
    backbone__WEBPACK_IMPORTED_MODULE_0___default().history.loadUrl(dest_route);
  },
  onShowModal: function onShowModal(view) {
    this.controller.showModal(view);
  },
  onDelete: function onDelete(childView) {
    this.controller.modelDelete(childView);
  }
});
var App = new AppClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (App);

/***/ }),

/***/ "./src/statistics/components/Controller.js":
/*!*************************************************!*\
  !*** ./src/statistics/components/Controller.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../tools */ "./src/tools.js");
/* harmony import */ var _models_EntryModel__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../models/EntryModel */ "./src/statistics/models/EntryModel.js");




var Controller = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().Object.extend({
  initialize: function initialize(options) {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
    console.log("Controller.initialize");
    this.rootView = options["rootView"];
    this.productDefaults = this.config.request("get:options", "defaults");
  },
  index: function index() {
    console.log("Controller.index");
    this.rootView.index();
  },
  showModal: function showModal(view) {
    this.rootView.showModal(view);
  },
  editEntry: function editEntry(entryId) {
    var _this = this;
    var model = this.facade.request("get:entry", entryId);
    (0,_tools__WEBPACK_IMPORTED_MODULE_1__.showLoader)();
    var promise = this.facade.request("load:criteria", model);
    promise.then(function (collection) {
      (0,_tools__WEBPACK_IMPORTED_MODULE_1__.hideLoader)();
      _this.rootView.entryEdit(model, collection);
    });
  },
  addEntry: function addEntry() {
    var collection = this.facade.request("get:collection", "entries");
    var model = new _models_EntryModel__WEBPACK_IMPORTED_MODULE_2__["default"]();
    this.rootView.entryAdd(model, collection);
  },
  editEntryMainData: function editEntryMainData(modelId) {
    var collection = this.facade.request("get:collection", "entries");
    var model = collection.get(modelId);
    this.rootView.entryEditMainData(model, collection);
  },
  showEntryExport: function showEntryExport(model) {
    var url = model.exportUrl();
    window.openPopup(url);
  },
  showEntryDuplicate: function showEntryDuplicate(model) {
    this.rootView.showEntryDuplicateForm(model);
  },
  // Common model views
  _onModelDeleteSuccess: function _onModelDeleteSuccess() {
    var messagebus = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("message");
    messagebus.trigger("success", this, "Vos données ont bien été supprimées");
    this.app.trigger("navigate", "index");
  },
  _onModelDeleteError: function _onModelDeleteError() {
    var messagebus = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("message");
    messagebus.trigger("error", this, "Une erreur a été rencontrée lors de la " + "suppression de cet élément");
  },
  modelDelete: function modelDelete(childView) {
    console.log("Controller.modelDelete");
    var result = window.confirm("Êtes-vous sûr de vouloir supprimer cet élément ?");
    if (result) {
      childView.model.destroy({
        success: this._onModelDeleteSuccess.bind(this),
        error: this._onModelDeleteError.bind(this),
        wait: true
      });
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Controller);

/***/ }),

/***/ "./src/statistics/components/Facade.js":
/*!*********************************************!*\
  !*** ./src/statistics/components/Facade.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var statistics_models_SheetModel_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! statistics/models/SheetModel.js */ "./src/statistics/models/SheetModel.js");
/* harmony import */ var base_components_FacadeModelApiMixin_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! base/components/FacadeModelApiMixin.js */ "./src/base/components/FacadeModelApiMixin.js");
/* harmony import */ var statistics_models_EntryCollection_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! statistics/models/EntryCollection.js */ "./src/statistics/models/EntryCollection.js");
/* harmony import */ var statistics_models_criterion__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! statistics/models/criterion */ "./src/statistics/models/criterion/index.js");
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../tools */ "./src/tools.js");
/* provided dependency */ var $ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
/*
Global Api, handling all the model and collection fetch

facade = Radio.channel('facade');
facade.request('get:collection', 'sale_products');
*/







var FacadeClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().Object.extend(base_components_FacadeModelApiMixin_js__WEBPACK_IMPORTED_MODULE_2__["default"]).extend({
  radioEvents: {
    "criterion:add": "onAddCriterion"
  },
  radioRequests: {
    "get:model": "getModelRequest",
    "get:collection": "getCollectionRequest",
    "get:entry": "getEntry",
    "load:collection": "loadCollection",
    "is:valid": "isDatasValid",
    "load:criteria": "loadCriteriaCollection",
    "entry:duplicate": "onEntryDuplicate"
  },
  initialize: function initialize(options) {
    this.models = {};
    this.models["sheet"] = new statistics_models_SheetModel_js__WEBPACK_IMPORTED_MODULE_1__["default"]({});
    this.collections = {};
    var collection;
    collection = new statistics_models_EntryCollection_js__WEBPACK_IMPORTED_MODULE_3__["default"]();
    this.collections["entries"] = collection;
  },
  setup: function setup(options) {
    this.setModelUrl("sheet", options["context_url"]);
    this.setCollectionUrl("entries", options["entries_url"]);
  },
  getEntry: function getEntry(entryId) {
    console.log(" - Facade : Retrieving entry " + entryId);
    return this.collections["entries"].get(entryId);
  },
  loadCriteriaCollection: function loadCriteriaCollection(entry) {
    console.log(" - Facade : Retrieving the criteria defining the entry " + entry.get("id"));
    var col = this.collections["criteria"] = new statistics_models_criterion__WEBPACK_IMPORTED_MODULE_4__.CriteriaCollection();
    col.url = entry.criteria_url();
    return this.loadCollection("criteria");
  },
  onAddCriterion: function onAddCriterion(model) {
    var _this = this;
    model.url = this.collections.criteria.url;
    var channel = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    var request = model.save({
      wait: true,
      sort: true
    });
    request.then(function (result) {
      return _this.collections.criteria.fetch({
        reset: true,
        success: function success(result) {
          return channel.trigger("criterion:added");
        }
      });
    });
  },
  onEntryDuplicate: function onEntryDuplicate(model, sheetId) {
    var _this2 = this;
    var sameSheet = parseInt(model.get("sheet_id")) == parseInt(sheetId);
    var request = (0,_tools__WEBPACK_IMPORTED_MODULE_5__.ajax_call)(model.duplicateUrl(), {
      sheet_id: sheetId
    }, "POST");
    if (sameSheet) {
      request = request.then(function (result) {
        return _this2.collections.entries.fetch();
      });
    }
    return request;
  },
  start: function start() {
    /*
     * Fires initial One Page application Load
     */
    var modelRequest = this.loadModel("sheet");
    var collectionRequest = this.loadCollection("entries");
    return $.when(modelRequest, collectionRequest);
  }
});
var Facade = new FacadeClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Facade);

/***/ }),

/***/ "./src/statistics/components/Router.js":
/*!*********************************************!*\
  !*** ./src/statistics/components/Router.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var marionette_approuter__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! marionette.approuter */ "./node_modules/marionette.approuter/lib/marionette.approuter.esm.js");

var Router = marionette_approuter__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  appRoutes: {
    index: "index",
    "": "index",
    addentry: "addEntry",
    "editentry/:id": "editEntryMainData",
    "entries/:id": "editEntry"
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Router);

/***/ }),

/***/ "./src/statistics/components/StatService.js":
/*!**************************************************!*\
  !*** ./src/statistics/components/StatService.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var base_components_ConfigBus__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! base/components/ConfigBus */ "./src/base/components/ConfigBus.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_1__);
/* provided dependency */ var $ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
function _createForOfIteratorHelper(r, e) { var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (!t) { if (Array.isArray(r) || (t = _unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) { t && (r = t); var _n = 0, F = function F() {}; return { s: F, n: function n() { return _n >= r.length ? { done: !0 } : { done: !1, value: r[_n++] }; }, e: function e(r) { throw r; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var o, a = !0, u = !1; return { s: function s() { t = t.call(r); }, n: function n() { var r = t.next(); return a = r.done, r; }, e: function e(r) { u = !0, o = r; }, f: function f() { try { a || null == t["return"] || t["return"](); } finally { if (u) throw o; } } }; }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }



var StatServiceClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().Object.extend({
  channelName: "stat",
  radioRequests: {
    "find:column": "findModelColumn",
    "find:methods": "findMethods",
    "get:attributes": "_getAttributes",
    "get:relationships": "_getRelationships",
    "find:static_options": "findStaticOptions",
    "find:manytoone_options": "findManyToOneOptions"
  },
  _getColumnLevel: function _getColumnLevel(model_or_path) {
    var path = [];
    console.log("Looking for column level informations");
    console.log(model_or_path);
    if (Array.isArray(model_or_path)) {
      path = model_or_path;
    } else {
      var model = model_or_path;
      if (model && model.collection && model.collection.path) {
        path = model.collection.path;
      }
    }
    var result = this.columns;
    // On commence par descendre une éventuelle arborescence d'options
    if (!path) {
      path = [];
    } else if (!Array.isArray(path)) {
      path = [path];
    }
    var _iterator = _createForOfIteratorHelper(path),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        parent = _step.value;
        result = result.relationships[parent];
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    return result;
  },
  _clone: function _clone(options) {
    return JSON.parse(JSON.stringify(options));
  },
  _getAttributes: function _getAttributes(model_or_path) {
    var column_node = this._getColumnLevel(model_or_path);
    return this._clone(column_node.attributes);
  },
  _getRelationships: function _getRelationships(model_or_path) {
    var column_node = this._getColumnLevel(model_or_path);
    return this._clone(column_node.relationships);
  },
  findModelColumn: function findModelColumn(key) {
    var path = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
    /*
     * Find the Column of the model
     */
    console.log("Find the model for a given column %s %s", key, path);
    var parent_node = this._getColumnLevel(path);
    // On récupère le résultat
    var result;
    if (key in parent_node.attributes) {
      result = parent_node.attributes[key];
    } else if (parent_node.relationships && key in parent_node.relationships) {
      result = parent_node.relationships[key];
    } else {
      console.error("Erreur, il y a des anciennes options statistiques qui ne sont plus supportées %s", key);
    }
    console.log(result);
    return this._clone(result);
  },
  findMethods: function findMethods(type) {
    return this._clone(this.form_config.options.methods[type]);
  },
  findStaticOptions: function findStaticOptions(key) {
    return this._clone(this.form_config.options.static_opt_options[key]);
  },
  findManyToOneOptions: function findManyToOneOptions(key) {
    return this._clone(this.form_config.options.manytoone_options[key]);
  },
  setFormConfig: function setFormConfig(form_config) {
    this.form_config = form_config;
    this.columns = form_config.options.columns;
  },
  setup: function setup(form_config_url) {},
  start: function start() {
    this.setFormConfig(base_components_ConfigBus__WEBPACK_IMPORTED_MODULE_0__["default"].form_config);
    var result = $.Deferred();
    result.resolve(base_components_ConfigBus__WEBPACK_IMPORTED_MODULE_0__["default"].form_config, null, null);
    return result;
  }
});
var StatService = new StatServiceClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (StatService);

/***/ }),

/***/ "./src/statistics/models/EntryCollection.js":
/*!**************************************************!*\
  !*** ./src/statistics/models/EntryCollection.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _EntryModel_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EntryModel.js */ "./src/statistics/models/EntryModel.js");


var EntryCollection = backbone__WEBPACK_IMPORTED_MODULE_0___default().Collection.extend({
  model: _EntryModel_js__WEBPACK_IMPORTED_MODULE_1__["default"]
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryCollection);

/***/ }),

/***/ "./src/statistics/models/EntryModel.js":
/*!*********************************************!*\
  !*** ./src/statistics/models/EntryModel.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _base_models_BaseModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../base/models/BaseModel */ "./src/base/models/BaseModel.js");

var EntryModel = _base_models_BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  props: ["id", "title", "description", "sheet_id", "criteria"],
  defaults: {
    criteria: []
  },
  validation: {
    title: {
      required: true,
      msg: "est requis"
    }
  },
  exportUrl: function exportUrl() {
    return "/statistics/entries/" + this.get("id") + ".csv";
  },
  criteria_url: function criteria_url() {
    return this.url() + "/criteria";
  },
  duplicateUrl: function duplicateUrl() {
    return this.url() + "?action=duplicate";
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryModel);

/***/ }),

/***/ "./src/statistics/models/SheetModel.js":
/*!*********************************************!*\
  !*** ./src/statistics/models/SheetModel.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);

var SheetModel = backbone__WEBPACK_IMPORTED_MODULE_0___default().Model.extend({
  validation: {
    title: {
      required: true,
      msg: "est requis"
    }
  },
  exportUrl: function exportUrl() {
    return this.url() + ".csv";
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SheetModel);

/***/ }),

/***/ "./src/statistics/models/criterion/BaseModel.js":
/*!******************************************************!*\
  !*** ./src/statistics/models/criterion/BaseModel.js ***!
  \******************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var base_models_BaseModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! base/models/BaseModel */ "./src/base/models/BaseModel.js");

var BaseModel = base_models_BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  props: ["id", "key", "method", "type", "entry_id", "parent_id", "relationship"]
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (BaseModel);

/***/ }),

/***/ "./src/statistics/models/criterion/ClauseModel.js":
/*!********************************************************!*\
  !*** ./src/statistics/models/criterion/ClauseModel.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _BaseModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./BaseModel */ "./src/statistics/models/criterion/BaseModel.js");


/*
Model representing a criteria clause of type "and" / "or"
Bound its (children) criteria following the type clause
*/

var ClauseModel = _BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  // Define the props that should be set on your model
  props: ["children"],
  initialize: function initialize() {
    this.populate();
  },
  populate: function populate() {
    if (this.has("children")) {
      var subpath = this.collection.path.concat([]);
      if (this.has("key")) {
        subpath.push(this.get("key"));
      }
      this.children = new this.collection.__class__(this.get("children"), {
        path: subpath,
        url: this.collection.url
      });
    }
    this.children._parent = this;
    this.children.url = this.collection.url;
  }
});
ClauseModel.prototype.props = ClauseModel.prototype.props.concat(_BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].prototype.props);
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (ClauseModel);

/***/ }),

/***/ "./src/statistics/models/criterion/CommonModel.js":
/*!********************************************************!*\
  !*** ./src/statistics/models/criterion/CommonModel.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _BaseModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./BaseModel */ "./src/statistics/models/criterion/BaseModel.js");

var CommonModel = _BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  // Define the props that should be set on your model
  props: ["searches", "search1", "search2", "date_search1", "date_search2"]
});
CommonModel.prototype.props = CommonModel.prototype.props.concat(_BaseModel__WEBPACK_IMPORTED_MODULE_0__["default"].prototype.props);
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CommonModel);

/***/ }),

/***/ "./src/statistics/models/criterion/CriteriaCollection.js":
/*!***************************************************************!*\
  !*** ./src/statistics/models/criterion/CriteriaCollection.js ***!
  \***************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _CommonModel__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./CommonModel */ "./src/statistics/models/criterion/CommonModel.js");
/* harmony import */ var _OneToManyModel__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./OneToManyModel */ "./src/statistics/models/criterion/OneToManyModel.js");
/* harmony import */ var _ClauseModel__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./ClauseModel */ "./src/statistics/models/criterion/ClauseModel.js");




var modelMap = {
  manytoone: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  static_opt: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  or: _ClauseModel__WEBPACK_IMPORTED_MODULE_3__["default"],
  and: _ClauseModel__WEBPACK_IMPORTED_MODULE_3__["default"],
  onetomany: _OneToManyModel__WEBPACK_IMPORTED_MODULE_2__["default"],
  bool: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  string: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  date: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  multidate: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"],
  number: _CommonModel__WEBPACK_IMPORTED_MODULE_1__["default"]
};
var CriteriaCollection = backbone__WEBPACK_IMPORTED_MODULE_0___default().Collection.extend({
  initialize: function initialize(models, options) {
    options = options || {};
    if ("path" in options) {
      this.path = options["path"];
    } else {
      this.path = [];
    }
    if ("url" in options) {
      this.url = options["url"];
    }
  },
  model: function model(modelData, options) {
    var typ = modelData.type;
    if (!typ in modelMap) {
      console.error("Unknown model typ %s", typ);
    }
    return new modelMap[typ](modelData, options);
  }
});
CriteriaCollection.prototype.__class__ = CriteriaCollection;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CriteriaCollection);

/***/ }),

/***/ "./src/statistics/models/criterion/OneToManyModel.js":
/*!***********************************************************!*\
  !*** ./src/statistics/models/criterion/OneToManyModel.js ***!
  \***********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _ClauseModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./ClauseModel */ "./src/statistics/models/criterion/ClauseModel.js");

var OneToManyModel = _ClauseModel__WEBPACK_IMPORTED_MODULE_0__["default"].extend({});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (OneToManyModel);

/***/ }),

/***/ "./src/statistics/models/criterion/index.js":
/*!**************************************************!*\
  !*** ./src/statistics/models/criterion/index.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ClauseModel: () => (/* reexport safe */ _ClauseModel__WEBPACK_IMPORTED_MODULE_3__["default"]),
/* harmony export */   CommonModel: () => (/* reexport safe */ _CommonModel__WEBPACK_IMPORTED_MODULE_0__["default"]),
/* harmony export */   CriteriaCollection: () => (/* reexport safe */ _CriteriaCollection__WEBPACK_IMPORTED_MODULE_1__["default"]),
/* harmony export */   OneToManyModel: () => (/* reexport safe */ _OneToManyModel__WEBPACK_IMPORTED_MODULE_2__["default"])
/* harmony export */ });
/* harmony import */ var _CommonModel__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./CommonModel */ "./src/statistics/models/criterion/CommonModel.js");
/* harmony import */ var _CriteriaCollection__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./CriteriaCollection */ "./src/statistics/models/criterion/CriteriaCollection.js");
/* harmony import */ var _OneToManyModel__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./OneToManyModel */ "./src/statistics/models/criterion/OneToManyModel.js");
/* harmony import */ var _ClauseModel__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./ClauseModel */ "./src/statistics/models/criterion/ClauseModel.js");





/***/ }),

/***/ "./src/statistics/statistics.js":
/*!**************************************!*\
  !*** ./src/statistics/statistics.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(underscore__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _backbone_tools_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../backbone-tools.js */ "./src/backbone-tools.js");
/* harmony import */ var _components_App_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/App.js */ "./src/statistics/components/App.js");
/* harmony import */ var _components_StatService_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./components/StatService.js */ "./src/statistics/components/StatService.js");
/* harmony import */ var _components_Facade_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./components/Facade.js */ "./src/statistics/components/Facade.js");
/* global AppOption; */






jquery__WEBPACK_IMPORTED_MODULE_0___default()(function () {
  console.log(" # Page Loaded : starting the js code #");
  (0,_backbone_tools_js__WEBPACK_IMPORTED_MODULE_2__.applicationStartup)(AppOption, _components_App_js__WEBPACK_IMPORTED_MODULE_3__["default"], _components_Facade_js__WEBPACK_IMPORTED_MODULE_5__["default"], {
    customServices: [_components_StatService_js__WEBPACK_IMPORTED_MODULE_4__["default"]]
  });
});

/***/ }),

/***/ "./src/statistics/views/EntryAddForm.js":
/*!**********************************************!*\
  !*** ./src/statistics/views/EntryAddForm.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _base_behaviors_FormBehavior__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/behaviors/FormBehavior */ "./src/base/behaviors/FormBehavior.js");
/* harmony import */ var _widgets_InputWidget__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../widgets/InputWidget */ "./src/widgets/InputWidget.js");
/* harmony import */ var _widgets_TextAreaWidget__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../widgets/TextAreaWidget */ "./src/widgets/TextAreaWidget.js");





var template = __webpack_require__(/*! ./templates/EntryAddForm.mustache */ "./src/statistics/views/templates/EntryAddForm.mustache");
var EntryAddForm = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  template: template,
  className: "main_content",
  behaviors: [_base_behaviors_FormBehavior__WEBPACK_IMPORTED_MODULE_1__["default"]],
  regions: {
    title: ".field-title",
    description: ".field-description"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
  },
  onSuccessSync: function onSuccessSync() {
    var app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
    app.trigger("navigate", "entries/" + this.model.get("id"));
  },
  onCancelForm: function onCancelForm() {
    var app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
    if (this.getOption("add")) {
      app.trigger("navigate", "index");
    } else {
      app.trigger("navigate", "entries/" + this.model.get("id"));
    }
  },
  templateContext: function templateContext() {
    // Collect data sent to the template (model attributes are already transmitted)
    var title;
    if (this.getOption("add")) {
      title = "Ajouter une entrée statistique";
    } else {
      title = "Modifier une entrée statistique";
    }
    return {
      title: title
    };
  },
  onRender: function onRender() {
    console.log(this.model);
    this.showChildView("title", new _widgets_InputWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
      field_name: "title",
      label: "Intitulé de l'entrée statistique",
      description: "Intitulé de l'entrée statistique tel qu'il figurera dans l'export",
      required: true,
      value: this.model.get("title")
    }));
    this.showChildView("description", new _widgets_TextAreaWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      field_name: "description",
      label: "Description de l'entrée statistique",
      description: "Description de l'entrée statistique tel qu'elle figurera dans l'export",
      value: this.model.get("description"),
      required: false
    }));
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryAddForm);

/***/ }),

/***/ "./src/statistics/views/EntryCollectionView.js":
/*!*****************************************************!*\
  !*** ./src/statistics/views/EntryCollectionView.js ***!
  \*****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _EntryView__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EntryView */ "./src/statistics/views/EntryView.js");
/* harmony import */ var _EntryEmptyView__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./EntryEmptyView */ "./src/statistics/views/EntryEmptyView.js");




var EntryCollectionView = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().CollectionView.extend({
  childView: _EntryView__WEBPACK_IMPORTED_MODULE_1__["default"],
  emptyView: _EntryEmptyView__WEBPACK_IMPORTED_MODULE_2__["default"],
  tagName: "tbody",
  childViewTriggers: {
    "model:edit": "model:edit",
    "model:delete": "model:delete",
    "model:export": "model:export",
    "model:duplicate": "model:duplicate"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryCollectionView);

/***/ }),

/***/ "./src/statistics/views/EntryDuplicateForm.js":
/*!****************************************************!*\
  !*** ./src/statistics/views/EntryDuplicateForm.js ***!
  \****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(underscore__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _base_behaviors_ModalBehavior__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../base/behaviors/ModalBehavior */ "./src/base/behaviors/ModalBehavior.js");
/* harmony import */ var _widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../widgets/SelectWidget */ "./src/widgets/SelectWidget.js");





var template = __webpack_require__(/*! ./templates/EntryDuplicateForm.mustache */ "./src/statistics/views/templates/EntryDuplicateForm.mustache");
var Label = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  template: underscore__WEBPACK_IMPORTED_MODULE_1___default().template('<div class="alert alert-error"><%- message %></div>'),
  templateContext: function templateContext() {
    return {
      message: this.getOption("message")
    };
  }
});
var EntryDuplicateForm = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  behaviors: [_base_behaviors_ModalBehavior__WEBPACK_IMPORTED_MODULE_2__["default"]],
  template: template,
  regions: {
    message: ".message-container",
    sheets: ".field-sheets"
  },
  ui: {
    form: "form",
    submit: "button[type=submit]",
    cancel: "button[type=reset]"
  },
  events: {
    "click @ui.submit": "onSubmit",
    "submit @ui.form": "onSubmit",
    "click @ui.cancel": "onCancelForm"
  },
  childViewEvents: {},
  childViewTriggers: {},
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
  },
  onSubmit: function onSubmit(event) {
    var _this = this;
    event.preventDefault();
    var select = this.getChildView("sheets");
    var sheetId = select.getCurrentValue();
    if (!sheetId) {
      this.showChildView("message", new Label({
        message: "Veuillez choisir une feuille statistiques"
      }));
    } else {
      var request = this.facade.request("entry:duplicate", this.model, sheetId);
      request.then(function () {
        return _this.onSuccessSync();
      });
    }
  },
  onSuccessSync: function onSuccessSync() {
    this.triggerMethod("modal:close");
  },
  onCancelForm: function onCancelForm() {
    this.triggerMethod("modal:close");
  },
  templateContext: function templateContext() {
    // Collect data sent to the template (model attributes are already transmitted)
    return {
      title: "Dupliquer l'entrée statistique " + this.model.get("title")
    };
  },
  onRender: function onRender() {
    this.showChildView("sheets", new _widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      label: "Vers la feuille de statistiques",
      options: this.getOption("sheets"),
      field_name: "sheet",
      required: true,
      id_key: "id",
      label_key: "title",
      placeholder: ""
    }));
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryDuplicateForm);

/***/ }),

/***/ "./src/statistics/views/EntryEmptyView.js":
/*!************************************************!*\
  !*** ./src/statistics/views/EntryEmptyView.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_0__);

var template = __webpack_require__(/*! ./templates/EntryEmptyView.mustache */ "./src/statistics/views/templates/EntryEmptyView.mustache");
var EntryEmptyView = backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default().View.extend({
  template: template
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryEmptyView);

/***/ }),

/***/ "./src/statistics/views/EntryListComponent.js":
/*!****************************************************!*\
  !*** ./src/statistics/views/EntryListComponent.js ***!
  \****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _EntryCollectionView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EntryCollectionView.js */ "./src/statistics/views/EntryCollectionView.js");



var template = __webpack_require__(/*! ./templates/EntryListComponent.mustache */ "./src/statistics/views/templates/EntryListComponent.mustache");
var EntryListComponent = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().View.extend({
  template: template,
  regions: {
    list: {
      el: "tbody",
      replaceElement: true
    }
  },
  childViewEvents: {
    "model:edit": "onModelEdit",
    "model:delete": "onModelDelete",
    "model:export": "onModelExport",
    "model:duplicate": "onModelDuplicate"
  },
  childViewTriggers: {},
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
  },
  onRender: function onRender() {
    this.showChildView("list", new _EntryCollectionView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      collection: this.collection
    }));
  },
  onModelEdit: function onModelEdit(childView) {
    console.log("onModelEdit " + childView.model.get("id"));
    this.app.trigger("navigate", "/entries/" + childView.model.get("id"));
  },
  onModelDelete: function onModelDelete(childView) {
    this.app.trigger("entry:delete", childView);
  },
  onModelExport: function onModelExport(childView) {
    this.app.trigger("entry:export", childView.model);
  },
  onModelDuplicate: function onModelDuplicate(childView) {
    console.log("Duplicate");
    this.app.trigger("entry:duplicate", childView.model);
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryListComponent);

/***/ }),

/***/ "./src/statistics/views/EntryView.js":
/*!*******************************************!*\
  !*** ./src/statistics/views/EntryView.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var bootstrap__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! bootstrap */ "./node_modules/bootstrap/dist/js/npm.js");
/* harmony import */ var bootstrap__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(bootstrap__WEBPACK_IMPORTED_MODULE_1__);



var template = __webpack_require__(/*! ./templates/EntryView.mustache */ "./src/statistics/views/templates/EntryView.mustache");
var EntryView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().View.extend({
  tagName: "tr",
  template: template,
  regions: {},
  ui: {
    edit: "button.edit",
    "delete": "button.delete",
    csv_export: "button.csv_export",
    duplicate: "button.duplicate"
  },
  triggers: {
    "click @ui.edit": "model:edit",
    "click @ui.delete": "model:delete",
    "click @ui.csv_export": "model:export",
    "click @ui.duplicate": "model:duplicate"
  },
  childViewEvents: {},
  childViewTriggers: {},
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryView);

/***/ }),

/***/ "./src/statistics/views/RootComponent.js":
/*!***********************************************!*\
  !*** ./src/statistics/views/RootComponent.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _EntryListComponent__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./EntryListComponent */ "./src/statistics/views/EntryListComponent.js");
/* harmony import */ var _entryForm_EntryFormComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./entryForm/EntryFormComponent */ "./src/statistics/views/entryForm/EntryFormComponent.js");
/* harmony import */ var common_views_ActionToolbar_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! common/views/ActionToolbar.js */ "./src/common/views/ActionToolbar.js");
/* harmony import */ var _EntryAddForm__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./EntryAddForm */ "./src/statistics/views/EntryAddForm.js");
/* harmony import */ var _EntryDuplicateForm__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./EntryDuplicateForm */ "./src/statistics/views/EntryDuplicateForm.js");







var RootComponent = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().View.extend({
  template: __webpack_require__(/*! ./templates/RootComponent.mustache */ "./src/statistics/views/templates/RootComponent.mustache"),
  regions: {
    toolbar: "#toolbar",
    main: "#main",
    popup: ".entry-popup"
  },
  initialize: function initialize() {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
  },
  _showSheetToolbar: function _showSheetToolbar() {
    var actions = this.config.request("get:form_actions");
    actions["main"] = [{
      option: {
        url: "#addentry",
        label: "Ajouter une entrée",
        icon: "plus",
        title: "Ajouter une entrée statistiques",
        css: "btn btn-primary icon"
      },
      widget: "anchor"
    }];
    var view = new common_views_ActionToolbar_js__WEBPACK_IMPORTED_MODULE_3__["default"](actions);
    this.showChildView("toolbar", view);
  },
  _triggerEntryDelete: function _triggerEntryDelete(event) {
    console.log("Trigger entry delete");
    this.app.trigger("entry:delete", this.getChildView("main"));
  },
  _showEntryToolbar: function _showEntryToolbar(entry) {
    var _this = this;
    var actions = {
      main: [{
        option: {
          label: "Revenir à la liste",
          icon: "arrow-left",
          title: "Revenir à la liste des entrées",
          url: "#index",
          css: "btn icon"
        },
        widget: "anchor"
      }],
      more: [{
        option: {
          icon: "copy",
          title: "Dupliquer cette entrée statistiques",
          onclick: function onclick(event) {
            return _this.app.trigger("entry:duplicate", entry);
          },
          css: "btn icon only"
        },
        widget: "button"
      }, {
        option: {
          icon: "file-csv",
          title: "Exporter les données de gestion sociale associée à cette entrée",
          onclick: function onclick(event) {
            return _this.app.trigger("entry:export", entry);
          },
          css: "btn icon only"
        },
        widget: "button"
      }, {
        option: {
          icon: "trash-alt",
          title: "Supprimer cette entrée statistiques",
          onclick: function onclick(event) {
            return _this._triggerEntryDelete(event);
          },
          css: "btn icon only"
        },
        widget: "button"
      }]
    };
    console.log("Show entry toolbar");
    console.log(actions);
    var view = new common_views_ActionToolbar_js__WEBPACK_IMPORTED_MODULE_3__["default"](actions);
    this.showChildView("toolbar", view);
  },
  showEntryDuplicateForm: function showEntryDuplicateForm(entry) {
    var sheets = this.config.request("get:options", "sheet_list");
    var view = new _EntryDuplicateForm__WEBPACK_IMPORTED_MODULE_5__["default"]({
      model: entry,
      sheets: sheets
    });
    this.showChildView("popup", view);
  },
  _showEntryAdd: function _showEntryAdd(entry, entryCollection) {
    var view = new _EntryAddForm__WEBPACK_IMPORTED_MODULE_4__["default"]({
      model: entry,
      destCollection: entryCollection,
      add: true
    });
    this.showChildView("main", view);
  },
  _showEntryEditMainData: function _showEntryEditMainData(entry, entryCollection) {
    var view = new _EntryAddForm__WEBPACK_IMPORTED_MODULE_4__["default"]({
      model: entry,
      destCollection: entryCollection,
      add: false
    });
    this.showChildView("main", view);
  },
  _showEntryEdit: function _showEntryEdit(entry, criteriaCollection) {
    var view = new _entryForm_EntryFormComponent__WEBPACK_IMPORTED_MODULE_2__["default"]({
      model: entry,
      criteriaCollection: criteriaCollection
    });
    this.showChildView("main", view);
  },
  _showEntryList: function _showEntryList() {
    var collection = this.facade.request("get:collection", "entries");
    var view = new _EntryListComponent__WEBPACK_IMPORTED_MODULE_1__["default"]({
      collection: collection
    });
    this.showChildView("main", view);
  },
  entryAdd: function entryAdd(entry, entryCollection) {
    this._showEntryAdd(entry, entryCollection);
  },
  entryEdit: function entryEdit(entry, criteriaCollection) {
    this._showEntryToolbar(entry);
    this._showEntryEdit(entry, criteriaCollection);
  },
  entryEditMainData: function entryEditMainData(entry, entryCollection) {
    this._showEntryEditMainData(entry, entryCollection);
  },
  index: function index() {
    console.log("Index view");
    this._showSheetToolbar();
    this._showEntryList();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (RootComponent);

/***/ }),

/***/ "./src/statistics/views/entryForm/AddCriterionView.js":
/*!************************************************************!*\
  !*** ./src/statistics/views/entryForm/AddCriterionView.js ***!
  \************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/defineProperty */ "./node_modules/@babel/runtime/helpers/esm/defineProperty.js");
/* harmony import */ var _babel_runtime_helpers_esm_toConsumableArray__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/helpers/esm/toConsumableArray */ "./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var base_behaviors_ModalBehavior__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! base/behaviors/ModalBehavior */ "./src/base/behaviors/ModalBehavior.js");
/* harmony import */ var widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! widgets/SelectWidget */ "./src/widgets/SelectWidget.js");
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../../tools */ "./src/tools.js");


var _Mn$View$extend;





var template = __webpack_require__(/*! ./templates/AddCriterionView.mustache */ "./src/statistics/views/entryForm/templates/AddCriterionView.mustache");
var AddCriterionView = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().View.extend((_Mn$View$extend = {
  template: template,
  className: "main_content",
  behaviors: [base_behaviors_ModalBehavior__WEBPACK_IMPORTED_MODULE_3__["default"]]
}, (0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])(_Mn$View$extend, "template", template), "regions", {
  entityField: ".field-entity",
  keyField: ".field-key"
}), "ui", {
  form: "form",
  submit: "button[type=submit]",
  reset: "button[type=reset]"
}), "events", {
  "submit @ui.form": "onSubmitForm",
  "click @ui.reset": "onCancelClick",
  "click @ui.submit": "onSubmitForm"
}), "childViewEvents", {
  "finish:relationship": "onRelationshipFinish"
}), "childViewTriggers", {}), "initialize", function initialize(options) {
  this.statService = backbone_radio__WEBPACK_IMPORTED_MODULE_2___default().channel("stat");
  this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_2___default().channel("facade");
  this.mergeOptions(options, ["attributePath", "parentPath"]);
  console.log("Add Criterion form");
  console.log("Attribute tree path");
  console.log(this.attributePath);
  console.log(this.parentPath);
}), "getFieldValue", function getFieldValue(key) {
  /*
      Find the field value in the form object
   */
  var values = (0,_tools__WEBPACK_IMPORTED_MODULE_5__.serializeForm)(this.getUI("form"));
  var field_value;
  if (key in values) {
    field_value = values[key];
  }
  return field_value;
}), "getPath", function getPath(field_value) {
  /*
     Return the current path in the attribute tree for the given key
  */
  if (!field_value) {
    field_value = this.parentPath || this.getFieldValue("relationship");
  }
  var path = (0,_babel_runtime_helpers_esm_toConsumableArray__WEBPACK_IMPORTED_MODULE_1__["default"])(this.attributePath);
  if (field_value) {
    path.push(field_value);
  }
  return path;
}), "onSubmitForm", function onSubmitForm(event) {
  // On merge les données de formulaire avec le model tel qu'il a été initialisé
  // et les méta données de la colonne qui a été sélectionnée
  event.preventDefault();
  console.log("Submitting");
  var values = (0,_tools__WEBPACK_IMPORTED_MODULE_5__.serializeForm)(this.getUI("form"));
  var key = values["key"];
  var path = this.getPath();
  console.log("   Path of the current model %s", path);
  var column_def = this.statService.request("find:column", key, path);
  this.model.set(values);
  console.log(this.model.attributes);
  this.model.set(column_def);
  console.log(this.model.attributes);
  this.facade.trigger("criterion:add", this.model);
  this.trigger("modal:close");
}), (0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])((0,_babel_runtime_helpers_esm_defineProperty__WEBPACK_IMPORTED_MODULE_0__["default"])(_Mn$View$extend, "onCancelClick", function onCancelClick() {
  console.log("Cancel clicked");
  this.triggerMethod("reset:model");
  var eventName = "modal:close";
  this.triggerMethod(eventName);
}), "showKeySelect", function showKeySelect(relationship) {
  console.log("showKeySelect");
  var path = this.getPath(relationship);
  var options = this.statService.request("get:attributes", path);
  console.log(options);
  var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_4__["default"]({
    options: options,
    label: "Type de critère",
    id_key: "name",
    field_name: "key"
  });
  this.showChildView("keyField", view);
}), "onRelationshipFinish", function onRelationshipFinish(field_value) {
  /*
  Fired when the type of criterion was selected
  */
  console.log("onRelationshipFinish");
  var path = this.getPath(field_value);
  this.model.set("relationship", field_value);
  this.showKeySelect(field_value);
}), "onRender", function onRender() {
  console.log(this.statService);
  var options = Object.values(this.statService.request("get:relationships", this.attributePath));
  console.log(options);
  options.splice(0, 0, {
    label: "Entité",
    name: ""
  });
  var view_opts = {
    options: options,
    label: "Type de critère",
    id_key: "name",
    field_name: "relationship"
  };
  if (this.parentPath) {
    console.log("");
    view_opts["editable"] = false;
    view_opts["value"] = this.parentPath;
  }
  var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_4__["default"](view_opts);
  this.showChildView("entityField", view);
  this.showKeySelect();
})));
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (AddCriterionView);

/***/ }),

/***/ "./src/statistics/views/entryForm/ClauseCriteriaView.js":
/*!**************************************************************!*\
  !*** ./src/statistics/views/entryForm/ClauseCriteriaView.js ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _CombinationView__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./CombinationView */ "./src/statistics/views/entryForm/CombinationView.js");



var template = __webpack_require__(/*! ./templates/ClauseCriteriaView.mustache */ "./src/statistics/views/entryForm/templates/ClauseCriteriaView.mustache");
var ClauseCriteriaView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().View.extend({
  tagName: "li",
  template: template,
  regions: {
    children: {
      el: ".children",
      replaceElement: true
    },
    combination: ".combination"
  },
  childViewEvents: {
    "action:clicked": "onAddClick"
  },
  childViewTriggers: {
    "criterion:delete": "criterion:delete",
    "add:click": "add:click"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
  },
  templateContext: function templateContext() {
    // Collect data sent to the template (model attributes are already transmitted)
    return {};
  },
  onAddClick: function onAddClick(action_name) {
    /*
     * add click on ouvre une popup pour sélectionner le champ à traiter
     * on met le parent_id en mémoire dans un coin
     */
    if (action_name == "add") {
      console.log("ClauseCriteriaView.onAddClick");
      console.log(this.model);
      this.trigger("add:click", this.model);
    }
  },
  showCombination: function showCombination() {
    // Affichage du toggle ET/OU
    if (this.model.collection.indexOf(this.model) >= 1 && this.model.collection.path.length == 0) {
      var view = new _CombinationView__WEBPACK_IMPORTED_MODULE_1__["default"]({
        model: this.model.collection._parent
      });
      this.showChildView("combination", view);
    }
  },
  onRender: function onRender() {
    this.showCombination();
    if (this.model.children.length > 0) {
      this.showChildView("children", new this.__parentclass__({
        collection: this.model.children,
        parent: this
      }));
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (ClauseCriteriaView);

/***/ }),

/***/ "./src/statistics/views/entryForm/CombinationView.js":
/*!***********************************************************!*\
  !*** ./src/statistics/views/entryForm/CombinationView.js ***!
  \***********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);


var template = __webpack_require__(/*! ./templates/CombinationView.mustache */ "./src/statistics/views/entryForm/templates/CombinationView.mustache");
var CombinationView = backbone_marionette__WEBPACK_IMPORTED_MODULE_1___default().View.extend({
  template: template,
  regions: {},
  ui: {
    button: "input[type=radio]"
  },
  events: {
    "click @ui.button": "onClick"
  },
  modelEvents: {
    saved: "render"
  },
  childViewEvents: {
    "add:click": "onAddClick"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
  },
  onAddClick: function onAddClick() {
    console.log("CombinationView.onAddClick");
    this.trigger("add:click", this.model);
  },
  onClick: function onClick(event) {
    var value = event.target.value;
    this.model.set({
      type: value
    });
    this.model.save({
      patch: true,
      wait: true
    });
  },
  templateContext: function templateContext() {
    return {
      is_and_clause: this.model.get("type") == "and",
      is_or_clause: this.model.get("type") == "or"
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CombinationView);

/***/ }),

/***/ "./src/statistics/views/entryForm/CommonCriteriaView.js":
/*!**************************************************************!*\
  !*** ./src/statistics/views/entryForm/CommonCriteriaView.js ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! base/models/ButtonModel */ "./src/base/models/ButtonModel.js");
/* harmony import */ var widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/ButtonWidget */ "./src/widgets/ButtonWidget.js");
/* harmony import */ var widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! widgets/SelectWidget */ "./src/widgets/SelectWidget.js");
/* harmony import */ var widgets_DateWidget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! widgets/DateWidget */ "./src/widgets/DateWidget.js");
/* harmony import */ var widgets_InputWidget__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! widgets/InputWidget */ "./src/widgets/InputWidget.js");
/* harmony import */ var _CombinationView__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./CombinationView */ "./src/statistics/views/entryForm/CombinationView.js");








var template = __webpack_require__(/*! ./templates/CommonCriteriaView.mustache */ "./src/statistics/views/entryForm/templates/CommonCriteriaView.mustache");
var CommonCriteriaView = backbone_marionette__WEBPACK_IMPORTED_MODULE_7___default().View.extend({
  template: template,
  tagName: "li",
  regions: {
    combination: ".combination",
    selector: ".form-group.selector",
    method: ".form-group.method",
    search1: ".form-group.search1",
    search2: ".form-group.search2",
    deleteButton: {
      el: ".delbutton-container",
      replaceElement: true
    },
    addButton: ".addbutton-container"
  },
  ui: {
    form: "form"
  },
  events: {
    "submit @ui.form": "onFormSubmit"
  },
  childViewEvents: {
    finish: "onFieldSelect",
    "action:clicked": "onActionClicked"
  },
  childViewTriggers: {},
  modelEvents: {
    saved: "onModelSaved"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.service = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("stat");
    this.attributes = this.service.request("get:attributes", this.model);
  },
  templateContext: function templateContext() {
    // Collect data sent to the template (model attributes are already transmitted)
    return {
      label: this.service.request("find:label", this.model)
    };
  },
  onFormSubmit: function onFormSubmit(event) {
    event.preventDefault();
    document.activeElement.blur();
  },
  onActionClicked: function onActionClicked(action_name) {
    /*
     * add click on ouvre une popup pour sélectionner le champ à traiter
     * on met le parent_id en mémoire dans un coin
     */
    console.log("CommonCriteriaView.onActionClicked '%s'", action_name);
    if (action_name == "add") {
      this.triggerMethod("add:click", this.model);
    } else if (action_name == "delete") {
      this.triggerMethod("criterion:delete", this.model);
    }
  },
  onModelSaved: function onModelSaved(field) {},
  showSelector: function showSelector() {
    /* 
    Show the selector for the field name
    */
    var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      title: "Champ",
      options: this.attributes,
      id_key: "name",
      value: this.model.get("key"),
      field_name: "key"
    });
    this.showChildView("selector", view);
  },
  showMethod: function showMethod() {
    /* 
    Show the selector for the filter method
    */
    console.log("showMethod");
    console.log(this.model);
    var methods = this.service.request("find:methods", this.model.get("type"));
    var add_default = false;
    if (!this.model.get("method")) {
      add_default = true;
    }
    var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      title: "Filtre",
      options: methods,
      value: this.model.get("method"),
      field_name: "method",
      placeholder: add_default ? "" : undefined
    });
    this.showChildView("method", view);
  },
  _showStaticOptFields: function _showStaticOptFields() {
    var options = this.service.request("find:static_options", this.model.get("key"));
    var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      title: "Valeur",
      value: this.model.get("searches"),
      field_name: "searches",
      options: options,
      placeholder: "",
      multiple: true
    });
    this.showChildView("search1", view);
  },
  _showManyToOneFields: function _showManyToOneFields() {
    var options = this.service.request("find:manytoone_options", this.model.get("key"));
    var view = new widgets_SelectWidget__WEBPACK_IMPORTED_MODULE_3__["default"]({
      title: "Valeur",
      value: this.model.get("searches"),
      field_name: "searches",
      options: options,
      placeholder: "",
      multiple: true
    });
    this.showChildView("search1", view);
  },
  _showStringField: function _showStringField() {
    var view = new widgets_InputWidget__WEBPACK_IMPORTED_MODULE_5__["default"]({
      title: "Libellé",
      value: this.model.get("search1"),
      field_name: "search1"
    });
    this.showChildView("search1", view);
  },
  _showNumberField: function _showNumberField() {
    var method = this.model.get("method");
    var label = "Valeur à comparer";
    if (["bw", "nbw"].includes(method)) {
      label = "Entre";
    }
    var view = new widgets_InputWidget__WEBPACK_IMPORTED_MODULE_5__["default"]({
      title: "",
      ariaLabel: label,
      value: this.model.get("search1"),
      field_name: "search1"
    });
    this.showChildView("search1", view);
    if (["bw", "nbw"].includes(method)) {
      var view2 = new widgets_InputWidget__WEBPACK_IMPORTED_MODULE_5__["default"]({
        title: "Et",
        value: this.model.get("search2"),
        field_name: "search2"
      });
      this.showChildView("search2", view2);
    }
  },
  _showDateField: function _showDateField() {
    var method = this.model.get("method");
    if (["dr", "ndr"].includes(method)) {
      var label1 = "Entre le";
      var label2 = "Et le";
      var view1 = new widgets_DateWidget__WEBPACK_IMPORTED_MODULE_4__["default"]({
        title: label1,
        value: this.model.get("date_search1"),
        field_name: "date_search1"
      });
      this.showChildView("search1", view1);
      var view2 = new widgets_DateWidget__WEBPACK_IMPORTED_MODULE_4__["default"]({
        title: label2,
        value: this.model.get("date_search2"),
        field_name: "date_search2"
      });
      this.showChildView("search2", view2);
    }
  },
  showSearches: function showSearches() {
    /*
        Show the search fields (date range, option selection)
    */
    this.detachChildView("search1");
    this.detachChildView("search2");
    if (!this.model.get("method") || ["nll", "nnll"].includes(this.model.get("method"))) {
      return;
    }
    var fieldType = this.model.get("type");
    if (fieldType == "static_opt") {
      this._showStaticOptFields();
    } else if (fieldType == "manytoone") {
      this._showManyToOneFields();
    } else if (fieldType == "string") {
      this._showStringField();
    } else if (fieldType == "number") {
      this._showNumberField();
    } else if (fieldType == "date") {
      this._showDateField();
    }
    // field_type + method -> show field
  },
  onFieldSelect: function onFieldSelect(field_name, field_value) {
    var _this = this;
    if (this.model.get(field_name) == field_value) {
      return;
    }
    var new_vals = {};
    new_vals[field_name] = field_value;
    var callback;
    if (field_name == "key") {
      var field = this.attributes[field_value];
      new_vals["type"] = field["type"];
      callback = function callback() {
        _this.showMethod();
        _this.showFields();
      };
    } else if (field_name == "method") {
      callback = function callback() {
        _this.showFields();
      };
    }
    this.model.save(new_vals, {
      wait: true,
      patch: true,
      success: callback
    });
  },
  showFields: function showFields() {
    this.showSelector();
    this.showMethod();
    this.showSearches();
  },
  showButtons: function showButtons() {
    /*
     * Show Delete and optionnal Add button
     */
    var model = new base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__["default"]({
      label: "Supprimer",
      showLabel: false,
      action: "delete",
      icon: "trash-alt"
    });
    var button = new widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
      model: model,
      surroundingTagName: "div",
      surroundingCss: "actions"
    });
    this.showChildView("deleteButton", button);

    // On affiche le bouton d'ajout que si le parent n'est pas une relation onetomany et si le parent a plusieurs enfants
    if (this.model.collection.path == 0 && this.model.collection.length > 1) {
      var _model = new base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__["default"]({
        label: "Ajouter un critère à ce niveau de la hiérarchie",
        showLabel: false,
        icon: "plus",
        action: "add"
      });
      var _button = new widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
        model: _model,
        surroundingTagName: "div",
        surroundingCss: "actions"
      });
      this.showChildView("addButton", _button);
    } else {
      this.$el.find("ul").hide();
    }
  },
  showCombination: function showCombination() {
    // Affichage du toggle ET/OU
    if (this.model.collection.indexOf(this.model) >= 1 && this.model.collection.path.length == 0) {
      var view = new _CombinationView__WEBPACK_IMPORTED_MODULE_6__["default"]({
        model: this.model.collection._parent
      });
      this.showChildView("combination", view);
    }
  },
  onRender: function onRender() {
    this.showButtons();
    this.showCombination();
    this.showFields();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CommonCriteriaView);

/***/ }),

/***/ "./src/statistics/views/entryForm/CriteriaCollectionView.js":
/*!******************************************************************!*\
  !*** ./src/statistics/views/entryForm/CriteriaCollectionView.js ***!
  \******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(underscore__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../../base/models/ButtonModel */ "./src/base/models/ButtonModel.js");
/* harmony import */ var _widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../../../widgets/ButtonWidget */ "./src/widgets/ButtonWidget.js");
/* harmony import */ var _ClauseCriteriaView__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./ClauseCriteriaView */ "./src/statistics/views/entryForm/ClauseCriteriaView.js");
/* harmony import */ var _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./CommonCriteriaView */ "./src/statistics/views/entryForm/CommonCriteriaView.js");
/* harmony import */ var _OneToManyCriteriaView__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./OneToManyCriteriaView */ "./src/statistics/views/entryForm/OneToManyCriteriaView.js");









var modelToViewMapping = {
  string: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  date: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  multidate: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  number: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  static_opt: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  bool: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  manytoone: _CommonCriteriaView__WEBPACK_IMPORTED_MODULE_6__["default"],
  or: _ClauseCriteriaView__WEBPACK_IMPORTED_MODULE_5__["default"],
  and: _ClauseCriteriaView__WEBPACK_IMPORTED_MODULE_5__["default"],
  onetomany: _OneToManyCriteriaView__WEBPACK_IMPORTED_MODULE_7__["default"]
};
var CriteriaEmptyView = backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default().View.extend({
  template: underscore__WEBPACK_IMPORTED_MODULE_2___default().template("<div></div>")
});
var CriteriaCollectionView = backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default().CollectionView.extend({
  tagName: "ul",
  emptyView: CriteriaEmptyView,
  childViewTriggers: {
    "action:clicked": "action:clicked",
    "add:click": "add:click",
    "criterion:delete": "criterion:delete"
  },
  collectionEvents: {
    fetch: "render"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_1___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_1___default().channel("facade");
  },
  childView: function childView(model) {
    var view = modelToViewMapping[model.get("type")];
    view.prototype.__parentclass__ = CriteriaCollectionView;
    return view;
  },
  onRender: function onRender() {
    var model = new _base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_3__["default"]({
      label: "Ajouter un critère à ce niveau de la hiérarchie",
      showLabel: false,
      icon: "plus",
      event: "add:click"
    });
    var button = new _widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_4__["default"]({
      model: model,
      surroundingTagName: "li"
    });
    console.log("Add the add button to the collection view");
    this.addChildView(button, this.children.length);
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (CriteriaCollectionView);

/***/ }),

/***/ "./src/statistics/views/entryForm/EntryFormComponent.js":
/*!**************************************************************!*\
  !*** ./src/statistics/views/entryForm/EntryFormComponent.js ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! base/models/ButtonModel */ "./src/base/models/ButtonModel.js");
/* harmony import */ var widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/ButtonWidget */ "./src/widgets/ButtonWidget.js");
/* harmony import */ var _AddCriterionView__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./AddCriterionView */ "./src/statistics/views/entryForm/AddCriterionView.js");
/* harmony import */ var statistics_models_criterion_BaseModel__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! statistics/models/criterion/BaseModel */ "./src/statistics/models/criterion/BaseModel.js");
/* harmony import */ var _CriteriaCollectionView__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./CriteriaCollectionView */ "./src/statistics/views/entryForm/CriteriaCollectionView.js");







var template = __webpack_require__(/*! ./templates/EntryFormComponent.mustache */ "./src/statistics/views/entryForm/templates/EntryFormComponent.mustache");

/*
  Component in charge of the configuration of a statistic entry and its criteria

  Criteria are a tree of criterion

    Some criteria are clauses (AND/OR)
    Other are Surrounding criteria on a related table (One TO many relationship)
    Latest are common (string/number, selectionnable options ...)

*/

var EntryFormComponent = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().View.extend({
  template: template,
  regions: {
    editButton: {
      el: ".edit-btn-container",
      replaceElement: true
    },
    criteria: ".criteria-container",
    popup: ".popup"
  },
  childViewEvents: {
    "edit:entry:click": "onEditClicked",
    "add:click": "onAddClicked",
    "criterion:delete": "onCriterionDelete"
  },
  initialize: function initialize(options) {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.listenTo(this.facade, "criterion:added", this.renderList.bind(this));
    console.log(options);
    this.mergeOptions(options, ["criteriaCollection"]);
    console.log(this.criteriaCollection);
  },
  onButtonClicked: function onButtonClicked(keyname) {
    if (keyname == "editentry") {
      this.onEditClicked();
    } else {
      this.onAddClicked(this.getRootCriterion());
    }
  },
  onEditClicked: function onEditClicked() {
    var app = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("app");
    app.trigger("navigate", "editentry/" + this.model.get("id"));
  },
  getRootCriterion: function getRootCriterion() {
    return this.criteriaCollection.models[0];
  },
  onAddClicked: function onAddClicked(parentModel) {
    console.log("EntryFormComponent");
    parentModel = parentModel || this.getRootCriterion();
    var model = new statistics_models_criterion_BaseModel__WEBPACK_IMPORTED_MODULE_4__["default"]({
      parent_id: parentModel.get("id"),
      entry_id: this.model.get("id")
    });
    var parentPath;
    if (parentModel.get("type") === "onetomany") {
      parentPath = parentModel.get("key");
    }
    var view = new _AddCriterionView__WEBPACK_IMPORTED_MODULE_3__["default"]({
      model: model,
      attributePath: parentModel.collection.path,
      parentPath: parentPath
    });
    this.showChildView("popup", view);
  },
  onCriterionDelete: function onCriterionDelete(model) {
    var _this = this;
    var result = window.confirm("Êtes-vous sûr de vouloir supprimer cet élément ?");
    if (result) {
      model.destroy({
        wait: true,
        success: function success() {
          return _this.criteriaCollection.fetch({
            reset: true,
            success: function success() {
              return _this.render();
            }
          });
        }
      });
    }
  },
  renderList: function renderList() {
    this.showChildView("criteria", new _CriteriaCollectionView__WEBPACK_IMPORTED_MODULE_5__["default"]({
      collection: this.getRootCriterion().children
    }));
  },
  renderAddButton: function renderAddButton() {
    var model = new base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__["default"]({
      label: "Nouveau critère",
      css: "btn icon",
      icon: "plus",
      event: "add:click"
    });
    var view = new widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
      model: model
    });
    this.showChildView("criteria", view);
  },
  onRender: function onRender() {
    this.showChildView("editButton", new widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
      model: new base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__["default"]({
        label: "edit",
        showLabel: false,
        css: "btn icon only unstyled",
        icon: "pen",
        event: "edit:entry:click"
      })
    }));
    if (this.getRootCriterion().children.length > 0) {
      this.renderList();
    } else {
      this.renderAddButton();
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (EntryFormComponent);

/***/ }),

/***/ "./src/statistics/views/entryForm/OneToManyCriteriaView.js":
/*!*****************************************************************!*\
  !*** ./src/statistics/views/entryForm/OneToManyCriteriaView.js ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! base/models/ButtonModel */ "./src/base/models/ButtonModel.js");
/* harmony import */ var widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/ButtonWidget */ "./src/widgets/ButtonWidget.js");
/* harmony import */ var _CombinationView__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./CombinationView */ "./src/statistics/views/entryForm/CombinationView.js");





var template = __webpack_require__(/*! ./templates/OneToManyCriteriaView.mustache */ "./src/statistics/views/entryForm/templates/OneToManyCriteriaView.mustache");
var OneToManyCriteriaView = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  tagName: "li",
  template: template,
  regions: {
    children: {
      el: ".children",
      replaceElement: true
    },
    combination: ".combination",
    deleteButton: {
      el: ".delbutton-container",
      replaceElement: true
    }
  },
  childViewEvents: {
    "add:click": "onAddClick",
    "action:clicked": "onActionClicked"
  },
  childViewTriggers: {
    "criterion:delete": "criterion:delete"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.statService = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("stat");
    this.relationshipConfig = this.statService.request("find:column", this.model.get("key"), this.model.collection.path);
    console.log(this.relationshipConfig);
  },
  onAddClick: function onAddClick() {
    /*
     * add click on ouvre une popup pour sélectionner le champ à traiter
     * on met le parent_id en mémoire dans un coin
     */
    console.log("ClauseCriteriaView.onAddClick");
    console.log(this.model);
    this.trigger("add:click", this.model);
  },
  onActionClicked: function onActionClicked(action_name) {
    /*
     * add click on ouvre une popup pour sélectionner le champ à traiter
     * on met le parent_id en mémoire dans un coin
     */
    console.log("OneToMany.onActionClicked");
    if (action_name == "delete") {
      this.trigger("criterion:delete", this.model);
    } else if (action_name == "add") {
      this.trigger("add:click", this.model);
    }
  },
  templateContext: function templateContext() {
    // Collect data sent to the template (model attributes are already transmitted)
    return {
      label: this.relationshipConfig["label"]
    };
  },
  showButtons: function showButtons() {
    /*
     * Show Delete and optionnal Add button
     */
    var model = new base_models_ButtonModel__WEBPACK_IMPORTED_MODULE_1__["default"]({
      label: "Supprimer",
      showLabel: false,
      action: "delete",
      icon: "trash-alt"
    });
    var button = new widgets_ButtonWidget__WEBPACK_IMPORTED_MODULE_2__["default"]({
      model: model,
      surroundingTagName: "div",
      surroundingCss: "actions"
    });
    this.showChildView("deleteButton", button);
  },
  onRender: function onRender() {
    this.showButtons();
    console.log(this.model);
    if (this.model.collection.indexOf(this.model) >= 1 && this.model.collection.path.length == 0) {
      var view = new _CombinationView__WEBPACK_IMPORTED_MODULE_3__["default"]({
        model: this.model.collection._parent
      });
      this.showChildView("combination", view);
    }
    if (this.model.children.length > 0) {
      this.showChildView("children", new this.__parentclass__({
        collection: this.model.children,
        parent: this
      }));
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (OneToManyCriteriaView);

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/AddCriterionView.mustache":
/*!****************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/AddCriterionView.mustache ***!
  \****************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<section id=\"work_form\" class=\"size_middle\">\n    <form>\n    <div role=\"dialog\" id=\"work-forms\" aria-modal=\"true\" aria-labelledby=\"work-forms_title\">\n        <div class='modal_layout'>\n            <header>\n                <button class=\"icon only unstyled close\" title=\"Fermer cette fenêtre\" aria-label=\"Fermer cette fenêtre\"  type='button'>\n                    <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n                </button>\n                <h2>Ajouter un critère</h2>\n            </header>\n            <div class=\"modal_content_layout\">\n                <input type='hidden' name='parent_id' value='"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"parent_id") || (depth0 != null ? lookupProperty(depth0,"parent_id") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"parent_id","hash":{},"data":data,"loc":{"start":{"line":12,"column":61},"end":{"line":12,"column":74}}}) : helper)))
    + "' />\n                <div class='modal_content'>\n                    <div class='message-container'></div>\n                    <div class='errors'></div>\n                    <fieldset>\n                        <div class='field-entity'></div>\n                        <div class='field-key'></div>\n                    </fieldset>\n                </div>\n                <footer>\n                    <button\n                        class='btn btn-primary'\n                        type='submit'\n                        value='submit'>\n                        Valider\n                    </button>\n                    <button\n                        class='btn'\n                        type='reset'\n                        value='submit'\n                        title=\"Annuler et fermer cette fenêtre\">\n                        Annuler\n                    </button>\n                </footer>\n            </div>\n        </div>\n    </div>\n    </form>\n</section>\n";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/ClauseCriteriaView.mustache":
/*!******************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/ClauseCriteriaView.mustache ***!
  \******************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class='combination'>\n</div>\n<div class='children'>\n</div>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/CombinationView.mustache":
/*!***************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/CombinationView.mustache ***!
  \***************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    return "                checked=\"checked\" \n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=depth0 != null ? depth0 : (container.nullContext || {}), lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<fieldset class=\"icon_choice\" title=\"Combinaison des critères\">\n    <div class=\"layout flex\">\n        <h6 class=\"screen-reader-text\">\n            Combinaison des critères\n        </h6>\n        <label>\n            <input \n                type=\"radio\"\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"is_and_clause") : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":9,"column":16},"end":{"line":11,"column":23}}})) != null ? stack1 : "")
    + "                value='and'\n                class=\"visuallyhidden\">\n            <span>\n                et\n            </span>\n        </label>\n        <label>\n            <input \n                type=\"radio\" \n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"is_or_clause") : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":21,"column":16},"end":{"line":23,"column":23}}})) != null ? stack1 : "")
    + "                value='or'\n                class=\"visuallyhidden\">\n            <span>\n                ou\n            </span>\n        </label>\n    </div>\n</fieldset>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/CommonCriteriaView.mustache":
/*!******************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/CommonCriteriaView.mustache ***!
  \******************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<form>\n    <fieldset>\n        <div class='combination'>\n        </div>\n        <div class='layout flex'>\n        <div class='form-group selector'></div>\n            <div class='form-group method'></div>\n            <div class='form-group search1'></div>\n            <div class='form-group search2'></div>\n        </div>\n    </fieldset>\n    <div class='delbutton-container'></div>\n    <ul><li class='add_line addbutton-container'></li></ul>\n</form>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/EntryFormComponent.mustache":
/*!******************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/EntryFormComponent.mustache ***!
  \******************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<div class='tree_view with_actions first_level'>\n   <h1>\n       "
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":3,"column":7},"end":{"line":3,"column":16}}}) : helper)))
    + "\n        <span class='edit-btn-container'></span>\n   </h1>\n   <p>"
    + alias4(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":6,"column":6},"end":{"line":6,"column":21}}}) : helper)))
    + "</p>\n    <form>\n        <h2 class='title'>Choix des critères</h2>\n        <div class='search_filters content vertical_padding criteria-container'>\n        </div>\n    </form>\n</div>  \n<div class='popup'></div>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/entryForm/templates/OneToManyCriteriaView.mustache":
/*!*********************************************************************************!*\
  !*** ./src/statistics/views/entryForm/templates/OneToManyCriteriaView.mustache ***!
  \*********************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<fieldset>\n    <div class='combination'></div>\n    <div class='layout flex'>\n    <div class='form-group'>\n        <label for=\"criterion_type\">Type de critère</label>\n        <select disabled id=\"criterion_type\">\n            <option>"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"label","hash":{},"data":data,"loc":{"start":{"line":7,"column":20},"end":{"line":7,"column":29}}}) : helper)))
    + "</option>\n        </select>\n    </div>\n    </div>\n\n</fieldset>\n    <div class='delbutton-container'></div>\n\n<div class='children'>\n</div>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/EntryAddForm.mustache":
/*!**************************************************************!*\
  !*** ./src/statistics/views/templates/EntryAddForm.mustache ***!
  \**************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<form name=\"current\">\n	<div class='limited_width width40'>\n		<div class='message-container'></div>\n		<div class='errors'></div>\n		<fieldset>\n			<h2 class=\"title\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":6,"column":21},"end":{"line":6,"column":32}}}) : helper)))
    + "</h2>\n			<div class='field-title'></div>\n			<div class='field-description'></div>\n		</fieldset>\n\n        <div class=\"layout flex main_actions\">\n            <div role='group'>\n                <button class='btn btn-primary icon' type='submit' value='submit'>\n                    <svg><use href=\"/static/icons/icones.svg#save\"></use></svg>Enregistrer\n                </button>\n                <button class='icon' type='reset' value='submit' title=\"Annuler et revenir en arrière\" aria-label=\"Annuler et revenir en arrière\">\n                    <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>Annuler\n                </button>\n            </div>\n            <div class='resume'></div>\n        </div>\n    </div>\n</form>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/EntryDuplicateForm.mustache":
/*!********************************************************************!*\
  !*** ./src/statistics/views/templates/EntryDuplicateForm.mustache ***!
  \********************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<section id=\"work_form\" class=\"size_middle\">\n    <form name=\"current\">\n        <div role=\"dialog\" id=\"work-forms\" aria-modal=\"true\" aria-labelledby=\"work-forms_title\">\n            <div class='modal_layout'>\n                <header>\n                    <button class=\"icon only unstyled close\" title=\"Fermer cette fenêtre\"\n                        aria-label=\"Fermer cette fenêtre\" type='button'>\n                        <svg>\n                            <use href=\"/static/icons/icones.svg#times\"></use>\n                        </svg>\n                    </button>\n                    <h2>"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":12,"column":24},"end":{"line":12,"column":33}}}) : helper)))
    + "</h2>\n                </header>\n                <div class=\"modal_content_layout\">\n                    <div class='modal_content'>\n                        <div class='message-container'></div>\n                        <div class='errors'></div>\n                        <fieldset>\n                            <div class='field-sheets'></div>\n                        </fieldset>\n                    </div>\n                    <footer>\n                        <button class='btn btn-primary icon' type='submit' value='submit'>\n                            <svg>\n                                <use href=\"/static/icons/icones.svg#save\"></use>\n                            </svg>Dupliquer\n                        </button>\n                        <button class='icon' type='reset' value='submit' title=\"Annuler et revenir en arrière\"\n                            aria-label=\"Annuler et revenir en arrière\">\n                            <svg>\n                                <use href=\"/static/icons/icones.svg#times\"></use>\n                            </svg>Annuler\n                        </button>\n                    </footer>\n                </div>\n            </div>\n        </div>\n    </form>\n</section>\n";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/EntryEmptyView.mustache":
/*!****************************************************************!*\
  !*** ./src/statistics/views/templates/EntryEmptyView.mustache ***!
  \****************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div>Aucune entrée statistiques n'a été saisie</div>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/EntryListComponent.mustache":
/*!********************************************************************!*\
  !*** ./src/statistics/views/templates/EntryListComponent.mustache ***!
  \********************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<h3>Entrées statistiques</h3>\n<div class=\"table_container\">\n    <table class='top_align_table hover_table'>\n        <thead>\n            <tr>\n                <th scope=\"col\" class=\"col_text\"><span class=\"screen-reader-text\">Intitulé</span></th>\n                <th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n            </tr>\n        </thead>\n        <tbody></tbody>\n    </table>\n</div>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/EntryView.mustache":
/*!***********************************************************!*\
  !*** ./src/statistics/views/templates/EntryView.mustache ***!
  \***********************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<td class='col_text'>"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":1,"column":21},"end":{"line":1,"column":30}}}) : helper)))
    + "</td>\n<td class='col_actions width_four'>\n    <button class='btn icon only edit'>\n        <svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n    </button>\n    <button class='btn icon only duplicate'>\n        <svg><use href=\"/static/icons/icones.svg#copy\"></use></svg>\n    </button>\n    <button class='btn icon only csv_export'>\n        <svg><use href=\"/static/icons/icones.svg#file-csv\"></use></svg>\n    </button>\n    <button class='btn icon only negative delete'>\n        <svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg>\n    </button>\n\n</td>";
},"useData":true});

/***/ }),

/***/ "./src/statistics/views/templates/RootComponent.mustache":
/*!***************************************************************!*\
  !*** ./src/statistics/views/templates/RootComponent.mustache ***!
  \***************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"main_toolbar\" id=\"toolbar\"></div>\n<div class=\"content_vertical_padding\" id='main'>\n    <div id='entries' class='content_vertical_padding'></div>\n</div>\n<div class='entry-popup'></div>";
},"useData":true});

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			loaded: false,
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/node module decorator */
/******/ 	(() => {
/******/ 		__webpack_require__.nmd = (module) => {
/******/ 			module.paths = [];
/******/ 			if (!module.children) module.children = [];
/******/ 			return module;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript && document.currentScript.tagName.toUpperCase() === 'SCRIPT')
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"statistics": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkenDI"] = self["webpackChunkenDI"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendor"], () => (__webpack_require__("./src/statistics/statistics.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	statistics = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=statistics.js.map