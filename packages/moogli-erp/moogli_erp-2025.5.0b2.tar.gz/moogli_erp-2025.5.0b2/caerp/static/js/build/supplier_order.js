var supplier_order;
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./src/supplier_order/components/App.js":
/*!**********************************************!*\
  !*** ./src/supplier_order/components/App.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _tools_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../tools.js */ "./src/tools.js");
/* harmony import */ var _views_MainView_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../views/MainView.js */ "./src/supplier_order/views/MainView.js");
/* harmony import */ var _Controller_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Controller.js */ "./src/supplier_order/components/Controller.js");
/* harmony import */ var _Router_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./Router.js */ "./src/supplier_order/components/Router.js");
/* harmony import */ var _base_components_ConfigBus_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../base/components/ConfigBus.js */ "./src/base/components/ConfigBus.js");
/* harmony import */ var _common_components_ExpenseTypeService_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../common/components/ExpenseTypeService.js */ "./src/common/components/ExpenseTypeService.js");








var AppClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_7___default().Application.extend({
  region: "#js-main-area",
  onBeforeStart: function onBeforeStart(app, options) {
    console.log("AppClass.onBeforeStart");
    this.rootView = new _views_MainView_js__WEBPACK_IMPORTED_MODULE_2__["default"]();
    this.controller = new _Controller_js__WEBPACK_IMPORTED_MODULE_3__["default"]({
      rootView: this.rootView
    });
    this.router = new _Router_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      controller: this.controller
    });
    console.log("AppClass.onBeforeStart finished");
    _common_components_ExpenseTypeService_js__WEBPACK_IMPORTED_MODULE_6__["default"].setFormConfig(_base_components_ConfigBus_js__WEBPACK_IMPORTED_MODULE_5__["default"].form_config);
  },
  onStart: function onStart(app, options) {
    this.showView(this.rootView);
    console.log("Starting the history");
    (0,_tools_js__WEBPACK_IMPORTED_MODULE_1__.hideLoader)();
    backbone__WEBPACK_IMPORTED_MODULE_0___default().history.start();
  }
});
var App = new AppClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (App);

/***/ }),

/***/ "./src/supplier_order/components/Controller.js":
/*!*****************************************************!*\
  !*** ./src/supplier_order/components/Controller.js ***!
  \*****************************************************/
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


var Controller = backbone_marionette__WEBPACK_IMPORTED_MODULE_1___default().Object.extend({
  initialize: function initialize(options) {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    console.log("Controller.initialize");
    this.rootView = options["rootView"];
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Controller);

/***/ }),

/***/ "./src/supplier_order/components/Facade.js":
/*!*************************************************!*\
  !*** ./src/supplier_order/components/Facade.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var _tools_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../tools.js */ "./src/tools.js");
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");
/* harmony import */ var _common_models_NodeFileCollection_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../common/models/NodeFileCollection.js */ "./src/common/models/NodeFileCollection.js");
/* harmony import */ var _models_TotalModel_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../models/TotalModel.js */ "./src/supplier_order/models/TotalModel.js");
/* harmony import */ var _models_SupplierOrderModel_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../models/SupplierOrderModel.js */ "./src/supplier_order/models/SupplierOrderModel.js");
/* harmony import */ var _models_SupplierOrderLineCollection_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../models/SupplierOrderLineCollection.js */ "./src/supplier_order/models/SupplierOrderLineCollection.js");
/* harmony import */ var _base_components_FacadeModelApiMixin__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../base/components/FacadeModelApiMixin */ "./src/base/components/FacadeModelApiMixin.js");
/* harmony import */ var _common_models_StatusLogEntryCollection__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../common/models/StatusLogEntryCollection */ "./src/common/models/StatusLogEntryCollection.js");









var FacadeClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default().Object.extend(_base_components_FacadeModelApiMixin__WEBPACK_IMPORTED_MODULE_6__["default"]).extend({
  channelName: "facade",
  radioEvents: {
    "changed:line": "computeLineTotal",
    "changed:totals": "computeFundingTotals",
    "changed:order.cae_percentage": "computeFundingTotals"
  },
  radioRequests: {
    "get:collection": "getCollectionRequest",
    "get:model": "getModelRequest",
    "is:valid": "isDataValid",
    "save:all": "saveAll"
  },
  initialize: function initialize(options) {
    this.models = {};
    this.collections = {};
  },
  start: function start() {
    console.log("Starting the facade");
    var deferred = (0,_tools_js__WEBPACK_IMPORTED_MODULE_0__.ajax_call)(this.url);
    return deferred.then(this.setupModels.bind(this));
  },
  setup: function setup(options) {
    console.log("Facade.setup");
    console.table(options);
    this.mergeOptions(options, ["edit"]);
    this.url = options["context_url"];
  },
  setupModels: function setupModels(context_datas) {
    this.models.total = new _models_TotalModel_js__WEBPACK_IMPORTED_MODULE_3__["default"]();
    var lines = context_datas["lines"];
    this.collections.lines = new _models_SupplierOrderLineCollection_js__WEBPACK_IMPORTED_MODULE_5__["default"](lines);
    this.collections.attachments = new _common_models_NodeFileCollection_js__WEBPACK_IMPORTED_MODULE_2__["default"](context_datas["attachments"]);
    this.collections.status_history = new _common_models_StatusLogEntryCollection__WEBPACK_IMPORTED_MODULE_7__["default"](context_datas.status_history);
    this.models.supplierOrder = new _models_SupplierOrderModel_js__WEBPACK_IMPORTED_MODULE_4__["default"](context_datas);
    this.setModelUrl("supplierOrder", AppOption["context_url"]);
    this.computeLineTotal();
    this.computeFundingTotals();
  },
  computeLineTotal: function computeLineTotal() {
    var collection = this.collections.lines;
    var datas = {};
    datas["ht"] = collection.total_ht();
    datas["tva"] = collection.total_tva();
    datas["ttc"] = collection.total();
    var channel = this.getChannel();
    channel.trigger("change:lines");
    this.models.total.set(datas);

    // Refresh funding totals as totals changed
    this.computeFundingTotals();
  },
  computeFundingTotals: function computeFundingTotals() {
    var order = this.models.supplierOrder;
    var datas = {};
    var ttc = this.models.total.get("ttc");
    var caePercentage = order.get("cae_percentage");
    datas["ttc_cae"] = (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.getPercent)(ttc, caePercentage);
    datas["ttc_worker"] = ttc - datas["ttc_cae"];
    this.models.total.set(datas);
  }
});
var Facade = new FacadeClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Facade);

/***/ }),

/***/ "./src/supplier_order/components/Router.js":
/*!*************************************************!*\
  !*** ./src/supplier_order/components/Router.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var marionette_approuter__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! marionette.approuter */ "./node_modules/marionette.approuter/lib/marionette.approuter.esm.js");

var Router = marionette_approuter__WEBPACK_IMPORTED_MODULE_0__["default"].extend({
  appRoutes: {}
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Router);

/***/ }),

/***/ "./src/supplier_order/models/SupplierOrderLineCollection.js":
/*!******************************************************************!*\
  !*** ./src/supplier_order/models/SupplierOrderLineCollection.js ***!
  \******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _SupplierOrderLineModel_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SupplierOrderLineModel.js */ "./src/supplier_order/models/SupplierOrderLineModel.js");
/* harmony import */ var _base_models_BaseLineCollection_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/models/BaseLineCollection.js */ "./src/base/models/BaseLineCollection.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");


var SupplierOrderLineCollection = _base_models_BaseLineCollection_js__WEBPACK_IMPORTED_MODULE_1__["default"].extend({
  model: _SupplierOrderLineModel_js__WEBPACK_IMPORTED_MODULE_0__["default"],
  validate: function validate() {
    console.log("Validating");
    var result = {};
    this.each(function (model) {
      var res = model.validate();
      if (res) {
        _.extend(result, res);
      }
    });
    if (this.models.length == 0) {
      result["lines"] = "Veuillez ajouter au moins un produit";
      this.trigger("validated:invalid", this, {
        lines: "Veuillez ajouter au moins un produit"
      });
    }
    return result;
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineCollection);

/***/ }),

/***/ "./src/supplier_order/models/SupplierOrderLineModel.js":
/*!*************************************************************!*\
  !*** ./src/supplier_order/models/SupplierOrderLineModel.js ***!
  \*************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _base_models_BaseLineModel_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../base/models/BaseLineModel.js */ "./src/base/models/BaseLineModel.js");

var SupplierOrderLineModel = _base_models_BaseLineModel_js__WEBPACK_IMPORTED_MODULE_0__["default"].extend();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineModel);

/***/ }),

/***/ "./src/supplier_order/models/SupplierOrderModel.js":
/*!*********************************************************!*\
  !*** ./src/supplier_order/models/SupplierOrderModel.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _base_models_BaseModel_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/models/BaseModel.js */ "./src/base/models/BaseModel.js");
/* harmony import */ var _base_models_DuplicableMixin_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../base/models/DuplicableMixin.js */ "./src/base/models/DuplicableMixin.js");



var SupplierOrderModel = _base_models_BaseModel_js__WEBPACK_IMPORTED_MODULE_1__["default"].extend(_base_models_DuplicableMixin_js__WEBPACK_IMPORTED_MODULE_2__["default"]).extend({
  props: ["id", "name", "cae_percentage", "supplier_id"],
  validation: {
    name: {
      required: true
    },
    cae_percentage: {
      required: true
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderModel);

/***/ }),

/***/ "./src/supplier_order/models/TotalModel.js":
/*!*************************************************!*\
  !*** ./src/supplier_order/models/TotalModel.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);

var TotalModel = backbone__WEBPACK_IMPORTED_MODULE_0___default().Model.extend({
  isLocalModel: true
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (TotalModel);

/***/ }),

/***/ "./src/supplier_order/supplier_order.js":
/*!**********************************************!*\
  !*** ./src/supplier_order/supplier_order.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _backbone_tools_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../backbone-tools.js */ "./src/backbone-tools.js");
/* harmony import */ var _components_App_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/App.js */ "./src/supplier_order/components/App.js");
/* harmony import */ var _components_Facade_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/Facade.js */ "./src/supplier_order/components/Facade.js");
/* harmony import */ var _common_components_ValidationLimitToolbarAppClass__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../common/components/ValidationLimitToolbarAppClass */ "./src/common/components/ValidationLimitToolbarAppClass.js");
/* harmony import */ var _common_components_ExpenseTypeService_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../common/components/ExpenseTypeService.js */ "./src/common/components/ExpenseTypeService.js");
/* harmony import */ var _common_components_StatusHistoryApp_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../common/components/StatusHistoryApp.js */ "./src/common/components/StatusHistoryApp.js");
/* global AppOption; */







var ToolbarApp = new _common_components_ValidationLimitToolbarAppClass__WEBPACK_IMPORTED_MODULE_4__["default"]();
jquery__WEBPACK_IMPORTED_MODULE_0___default()(function () {
  (0,_backbone_tools_js__WEBPACK_IMPORTED_MODULE_1__.applicationStartup)(AppOption, _components_App_js__WEBPACK_IMPORTED_MODULE_2__["default"], _components_Facade_js__WEBPACK_IMPORTED_MODULE_3__["default"], {
    actionsApp: ToolbarApp,
    statusHistoryApp: _common_components_StatusHistoryApp_js__WEBPACK_IMPORTED_MODULE_6__["default"],
    customServices: [_common_components_ExpenseTypeService_js__WEBPACK_IMPORTED_MODULE_5__["default"]]
  });
});

/***/ }),

/***/ "./src/supplier_order/views/MainView.js":
/*!**********************************************!*\
  !*** ./src/supplier_order/views/MainView.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_16___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_16__);
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var common_views_StatusFormPopupView_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! common/views/StatusFormPopupView.js */ "./src/common/views/StatusFormPopupView.js");
/* harmony import */ var _models_SupplierOrderLineModel_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../models/SupplierOrderLineModel.js */ "./src/supplier_order/models/SupplierOrderLineModel.js");
/* harmony import */ var _SupplierOrderLineTableView_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./SupplierOrderLineTableView.js */ "./src/supplier_order/views/SupplierOrderLineTableView.js");
/* harmony import */ var _SupplierOrderLineFormPopupView_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./SupplierOrderLineFormPopupView.js */ "./src/supplier_order/views/SupplierOrderLineFormPopupView.js");
/* harmony import */ var _SupplierOrderFormView_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./SupplierOrderFormView.js */ "./src/supplier_order/views/SupplierOrderFormView.js");
/* harmony import */ var _SupplierOrderLineDuplicateFormView_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./SupplierOrderLineDuplicateFormView.js */ "./src/supplier_order/views/SupplierOrderLineDuplicateFormView.js");
/* harmony import */ var _TotalView_js__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./TotalView.js */ "./src/supplier_order/views/TotalView.js");
/* harmony import */ var base_views_MessageView_js__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! base/views/MessageView.js */ "./src/base/views/MessageView.js");
/* harmony import */ var base_views_LoginView_js__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! base/views/LoginView.js */ "./src/base/views/LoginView.js");
/* harmony import */ var common_views_NodeFileCollectionView_js__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! common/views/NodeFileCollectionView.js */ "./src/common/views/NodeFileCollectionView.js");
/* harmony import */ var backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! backbone-tools.js */ "./src/backbone-tools.js");
/* harmony import */ var math_js__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! math.js */ "./src/math.js");
/* harmony import */ var tools_js__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! tools.js */ "./src/tools.js");
/* harmony import */ var base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! base/views/ErrorView.js */ "./src/base/views/ErrorView.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* provided dependency */ var $ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");

















var MainView = backbone_marionette__WEBPACK_IMPORTED_MODULE_16___default().View.extend({
  className: "container-fluid page-content",
  template: __webpack_require__(/*! ./templates/MainView.mustache */ "./src/supplier_order/views/templates/MainView.mustache"),
  regions: {
    modalRegion: ".modalRegion",
    files: ".files",
    supplierOrderForm: ".supplier-order",
    linesRegion: ".lines-region",
    totals: ".totals",
    messages: {
      el: ".messages-container",
      replaceElement: true
    },
    errors: ".group-errors"
  },
  childViewEvents: {
    "line:add": "onLineAdd",
    "line:edit": "onLineEdit",
    "line:delete": "onLineDelete",
    "order:modified": "onDataModified",
    "line:duplicate": "onLineDuplicate",
    "status:change": "onStatusChange"
  },
  onDataModified: function onDataModified(name, value) {
    if (name == "supplier_id") {
      this.onSupplierModified(value);
    }
    var totals = this.facade.request("get:model", "total");
    var order = this.facade.request("get:model", "supplierOrder");
    var ttc = totals.get("ttc");
    var ttc_cae = (0,math_js__WEBPACK_IMPORTED_MODULE_13__.getPercent)(ttc, order.get("cae_percentage"));
    var ttc_worker = ttc - ttc_cae;
    totals.set("ttc_cae", ttc_cae);
    totals.set("ttc_worker", ttc_worker);
  },
  onSupplierModified: function onSupplierModified(supplier_id) {
    /* jQuery hack to update supplier static part
     * defined in supplier_order.mako
     */
    var suppliers = this.config.request("get:options", "suppliers");
    var supplier = _.find(suppliers, function (x) {
      return x.value == supplier_id;
    });
    var elA = $("[data-backbone-var=supplier_id]");
    elA.text(supplier.label);
    elA.attr("href", "/suppliers/".concat(supplier_id));
  },
  initialize: function initialize() {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_1___default().channel("facade");
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_1___default().channel("config");
    this.listenTo(this.facade, "status:change", this.onStatusChange);
  },
  showSupplierOrderForm: function showSupplierOrderForm() {
    var edit = this.config.request("get:form_section", "general")["edit"];
    var model = this.facade.request("get:model", "supplierOrder");
    var view = new _SupplierOrderFormView_js__WEBPACK_IMPORTED_MODULE_6__["default"]({
      model: model,
      edit: edit
    });
    this.showChildView("supplierOrderForm", view);
  },
  onLineAdd: function onLineAdd(childView) {
    var model = new _models_SupplierOrderLineModel_js__WEBPACK_IMPORTED_MODULE_3__["default"]({});
    this.showLineForm(model, true, "Ajouter un achat");
  },
  onLineEdit: function onLineEdit(childView) {
    this.showLineForm(childView.model, false, "Modifier un achat");
  },
  showLineForm: function showLineForm(model, add, title) {
    var view = new _SupplierOrderLineFormPopupView_js__WEBPACK_IMPORTED_MODULE_5__["default"]({
      title: title,
      add: add,
      model: model,
      destCollection: this.facade.request("get:collection", "lines")
    });
    this.showChildView("modalRegion", view);
  },
  showDuplicateForm: function showDuplicateForm(model) {
    var view = new _SupplierOrderLineDuplicateFormView_js__WEBPACK_IMPORTED_MODULE_7__["default"]({
      model: model
    });
    this.showChildView("modalRegion", view);
  },
  onLineDuplicate: function onLineDuplicate(childView) {
    this.showDuplicateForm(childView.model);
  },
  onDeleteSuccess: function onDeleteSuccess() {
    (0,backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerSuccess)("Vos données ont bien été supprimées");
  },
  onDeleteError: function onDeleteError() {
    (0,backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerError)("Une erreur a été rencontrée lors de la " + "suppression de cet élément");
  },
  onLineDelete: function onLineDelete(childView) {
    var result = window.confirm("Êtes-vous sûr de vouloir supprimer cette ligne ?");
    if (result) {
      childView.model.destroy({
        success: this.onDeleteSuccess,
        error: this.onDeleteError
      });
    }
  },
  showFilesRegion: function showFilesRegion() {
    var edit = this.config.request("get:form_section", "general")["edit"];
    var collection = this.facade.request("get:collection", "attachments");
    var view = new common_views_NodeFileCollectionView_js__WEBPACK_IMPORTED_MODULE_11__["default"]({
      collection: collection,
      edit: edit
    });
    this.showChildView("files", view);
  },
  showLinesRegion: function showLinesRegion() {
    var section = this.config.request("get:form_section", "lines");
    var collection = this.facade.request("get:collection", "lines");
    var view = new _SupplierOrderLineTableView_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      collection: collection,
      section: section
    });
    this.showChildView("linesRegion", view);
  },
  showMessages: function showMessages() {
    var model = new (backbone__WEBPACK_IMPORTED_MODULE_0___default().Model)();
    var view = new base_views_MessageView_js__WEBPACK_IMPORTED_MODULE_9__["default"]({
      model: model
    });
    this.showChildView("messages", view);
  },
  showTotals: function showTotals() {
    var model = this.facade.request("get:model", "total");
    var view = new _TotalView_js__WEBPACK_IMPORTED_MODULE_8__["default"]({
      model: model
    });
    this.showChildView("totals", view);
  },
  showLogin: function showLogin() {
    var view = new base_views_LoginView_js__WEBPACK_IMPORTED_MODULE_10__["default"]({});
    this.showChildView("modalRegion", view);
  },
  onRender: function onRender() {
    this.showFilesRegion();
    this.showSupplierOrderForm();
    this.showLinesRegion();
    this.showTotals();
    this.showMessages();
  },
  _showStatusModal: function _showStatusModal(model) {
    console.log("Showing the status modal");
    var view = new common_views_StatusFormPopupView_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      action: model
    });
    this.showChildView("modalRegion", view);
  },
  formOk: function formOk() {
    console.log("Checking that form is OK");
    var result = true;
    var errors = this.facade.request("is:valid");
    if (!_.isEmpty(errors)) {
      console.log(errors);
      this.showChildView("errors", new base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_15__["default"]({
        errors: errors
      }));
      result = false;
    } else {
      this.detachChildView("errors");
    }
    return result;
  },
  onStatusChange: function onStatusChange(action_model) {
    var _this = this;
    console.log("Status changed asked");
    if (this.config.request("get:form_section", "general")["edit"]) {
      if (!action_model.get("status")) {
        return;
      }
      // Prior to any status change, we want to save and make sure it went OK
      (0,tools_js__WEBPACK_IMPORTED_MODULE_14__.showLoader)();
      if (action_model.get("status") != "draft") {
        console.log("Status is not draft");
        if (!this.formOk()) {
          document.body.scrollTop = document.documentElement.scrollTop = 0;
          (0,tools_js__WEBPACK_IMPORTED_MODULE_14__.hideLoader)();
          return;
        }
      }
      this.facade.request("save:all").then(function () {
        (0,tools_js__WEBPACK_IMPORTED_MODULE_14__.hideLoader)();
        _this._showStatusModal(action_model);
      }, function () {
        (0,tools_js__WEBPACK_IMPORTED_MODULE_14__.hideLoader)();
        (0,backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerError)("Erreur pendant la sauvegarde");
      });
    } else {
      this._showStatusModal(action_model);
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (MainView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderFormView.js":
/*!***********************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderFormView.js ***!
  \***********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! base/behaviors/FormBehavior.js */ "./src/base/behaviors/FormBehavior.js");
/* harmony import */ var widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! widgets/InputWidget.js */ "./src/widgets/InputWidget.js");
/* harmony import */ var widgets_PercentInputWidget_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/PercentInputWidget.js */ "./src/widgets/PercentInputWidget.js");
/* harmony import */ var widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! widgets/SelectWidget.js */ "./src/widgets/SelectWidget.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_4__);






var SupplierOrderFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default().View.extend({
  tagName: "div",
  behaviors: [base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_0__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierOrderFormView.mustache */ "./src/supplier_order/views/templates/SupplierOrderFormView.mustache"),
  regions: {
    name: ".name",
    advance_percent: ".advance_percent",
    supplier_id: ".supplier_id"
  },
  childViewEvents: {
    finish: "onFinish",
    change: "onChange"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_4___default().channel("config");
    this.suppliers_options = this.config.request("get:options", "suppliers");
  },
  onChange: function onChange(name, value) {
    this.model.set(name, value);
    this.triggerMethod("order:modified", name, value);
    this.triggerMethod("data:modified", name, value);
  },
  onFinish: function onFinish(name, value) {
    this.model.set(name, value);
    this.triggerMethod("order:modified", name, value);
    this.triggerMethod("data:persist", name, value);
  },
  showSupplierId: function showSupplierId() {
    var editable = this.config.request("get:form_section", "general:supplier_id")["edit"];
    var widget_params = {
      options: this.suppliers_options,
      title: "Fournisseur",
      field_name: "supplier_id",
      editable: editable,
      value: this.model.get("supplier_id")
    };
    if (!this.model.has("supplier_id")) {
      widget_params["placeholder"] = "Sélectionner";
    }
    var view = new widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__["default"](widget_params);
    this.showChildView("supplier_id", view);
  },
  showCaePercentage: function showCaePercentage() {
    var editable = this.config.request("get:form_section", "general:cae_percentage")["edit"];
    var view = new widgets_PercentInputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("cae_percentage"),
      title: "Part de paiement direct par la CAE",
      field_name: "cae_percentage",
      editable: editable
    });
    this.showChildView("advance_percent", view);
  },
  showName: function showName() {
    var editable = this.config.request("get:form_section", "general")["edit"];
    var view = new widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      value: this.model.get("name"),
      title: "Nom",
      field_name: "name",
      editable: editable
    });
    this.showChildView("name", view);
  },
  onRender: function onRender() {
    if (this.config.request("has:form_section", "general:cae_percentage")) {
      this.showCaePercentage();
    }
    if (this.config.request("has:form_section", "general:supplier_id")) {
      this.showSupplierId();
    }
    this.showName();
  },
  onSuccessSync: function onSuccessSync() {
    var facade = backbone_radio__WEBPACK_IMPORTED_MODULE_4___default().channel("facade");
    facade.trigger("navigate", "index");
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderFormView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineCollectionView.js":
/*!*********************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineCollectionView.js ***!
  \*********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _SupplierOrderLineView_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SupplierOrderLineView.js */ "./src/supplier_order/views/SupplierOrderLineView.js");
/* harmony import */ var _SupplierOrderLineEmptyView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierOrderLineEmptyView.js */ "./src/supplier_order/views/SupplierOrderLineEmptyView.js");



var SupplierOrderLineCollectionView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().CollectionView.extend({
  tagName: "tbody",
  // Bubble up child view events
  childViewTriggers: {
    edit: "line:edit",
    "delete": "line:delete",
    bookmark: "bookmark:add",
    duplicate: "line:duplicate"
  },
  childView: _SupplierOrderLineView_js__WEBPACK_IMPORTED_MODULE_0__["default"],
  emptyView: _SupplierOrderLineEmptyView_js__WEBPACK_IMPORTED_MODULE_1__["default"],
  emptyViewOptions: function emptyViewOptions() {
    return {
      colspan: 6,
      edit: this.getOption("section")["edit"]
    };
  },
  childViewOptions: function childViewOptions() {
    return this.getOption("section");
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineCollectionView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineDuplicateFormView.js":
/*!************************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineDuplicateFormView.js ***!
  \************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/behaviors/ModalBehavior.js */ "./src/base/behaviors/ModalBehavior.js");
/* harmony import */ var _widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../widgets/SelectWidget.js */ "./src/widgets/SelectWidget.js");
/* harmony import */ var _tools_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../tools.js */ "./src/tools.js");
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");






var SupplierOrderLineDuplicateFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default().View.extend({
  id: "supplierorderline-duplicate-form",
  behaviors: [_base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_1__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierOrderLineDuplicateFormView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineDuplicateFormView.mustache"),
  regions: {
    select: ".select"
  },
  ui: {
    cancel_btn: "button[type=reset]",
    form: "form"
  },
  events: {
    "submit @ui.form": "onSubmit",
    "click @ui.cancel_btn": "onCancelClick"
  },
  initialize: function initialize() {
    var channel = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    this.options = channel.request("get:options", "supplier_orders");
  },
  onCancelClick: function onCancelClick() {
    this.triggerMethod("modal:close");
  },
  templateContext: function templateContext() {
    var ht = this.model.getHT();
    var tva = this.model.getTva();
    var ttc = this.model.total();
    return {
      ht: (0,_math_js__WEBPACK_IMPORTED_MODULE_4__.formatAmount)(ht),
      tva: (0,_math_js__WEBPACK_IMPORTED_MODULE_4__.formatAmount)(tva),
      ttc: (0,_math_js__WEBPACK_IMPORTED_MODULE_4__.formatAmount)(ttc),
      type_id: this.model.get("type_id")
    };
  },
  onRender: function onRender() {
    var view = new _widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      options: this.options,
      title: "Commande fournisseur vers laquelle dupliquer",
      id_key: "id",
      field_name: "supplier_order_id",
      value: this.model.get("supplier_order_id")
    });
    this.showChildView("select", view);
  },
  onSubmit: function onSubmit(event) {
    event.preventDefault();
    var datas = (0,_tools_js__WEBPACK_IMPORTED_MODULE_3__.serializeForm)(this.getUI("form"));
    var request = this.model.duplicate(datas);
    var that = this;
    request.done(function () {
      that.triggerMethod("modal:close");
    });
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineDuplicateFormView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineEmptyView.js":
/*!****************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineEmptyView.js ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_0__);

var SupplierOrderLineEmptyView = backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default().View.extend({
  template: __webpack_require__(/*! ./templates/SupplierOrderLineEmptyView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineEmptyView.mustache"),
  templateContext: function templateContext() {
    var colspan = this.getOption("colspan");
    if (this.getOption("edit")) {
      colspan += 1;
    }
    return {
      colspan: colspan
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineEmptyView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineFormPopupView.js":
/*!********************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineFormPopupView.js ***!
  \********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../base/behaviors/ModalBehavior.js */ "./src/base/behaviors/ModalBehavior.js");
/* harmony import */ var _SupplierOrderLineFormView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierOrderLineFormView.js */ "./src/supplier_order/views/SupplierOrderLineFormView.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_2__);




// import BookMarkCollectionView from './BookMarkCollectionView.js';

var SupplierOrderLineFormPopupView = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().View.extend({
  behaviors: [_base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_0__["default"]],
  id: "supplierorderline-form-popup-modal",
  template: __webpack_require__(/*! ./templates/SupplierOrderLineFormPopupView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineFormPopupView.mustache"),
  regions: {
    main: {
      el: ".form-child",
      replaceElement: true
    }
  },
  ui: {
    /* override ModalBehavior.ui.modalbody selector that has no match otherwise,
    because its .modal_content_layout is outside my own template (sub-sub-template)
    */
    modalbody: "header"
  },
  childViewEvents: {
    "success:sync": "onSuccessSync"
  },
  // Here we bind the child FormBehavior with our ModalBehavior
  // Like it's done in the ModalFormBehavior
  childViewTriggers: {
    "cancel:form": "modal:close"
  },
  initialize: function initialize() {
    this.add = this.getOption("add");
  },
  onSuccessSync: function onSuccessSync() {
    if (this.add) {
      this.triggerMethod("modal:notifySuccess");
    } else {
      this.triggerMethod("modal:close");
    }
  },
  onModalAfterNotifySuccess: function onModalAfterNotifySuccess() {
    this.triggerMethod("line:add");
  },
  onModalBeforeClose: function onModalBeforeClose() {
    this.model.rollback();
  },
  refreshForm: function refreshForm() {
    this.showForm();
  },
  showForm: function showForm() {
    var view = new _SupplierOrderLineFormView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      model: this.model,
      destCollection: this.getOption("destCollection"),
      title: this.getOption("title"),
      add: this.add
    });
    this.showChildView("main", view);
  },
  templateContext: function templateContext() {
    return {
      title: this.getOption("title"),
      add: this.add
    };
  },
  onRender: function onRender() {
    this.refreshForm();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineFormPopupView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineFormView.js":
/*!***************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineFormView.js ***!
  \***************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone-validation */ "./node_modules/backbone-validation/dist/backbone-validation-amd.js");
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_validation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! base/behaviors/FormBehavior.js */ "./src/base/behaviors/FormBehavior.js");
/* harmony import */ var widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/InputWidget.js */ "./src/widgets/InputWidget.js");
/* harmony import */ var widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! widgets/SelectWidget.js */ "./src/widgets/SelectWidget.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../tools */ "./src/tools.js");







var SupplierOrderLineFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().View.extend({
  id: "mainform-container",
  className: "modal_overflow",
  behaviors: [base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_1__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierOrderLineFormView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineFormView.mustache"),
  regions: {
    // 'date': '.date',
    type_id: ".type_id",
    description: ".description",
    ht: ".ht",
    tva: ".tva"
  },
  // Bubble up child view events
  //
  childViewTriggers: {
    change: "data:modified"
  },
  onBeforeSync: _tools__WEBPACK_IMPORTED_MODULE_5__.showLoader,
  onFormSubmitted: _tools__WEBPACK_IMPORTED_MODULE_5__.hideLoader,
  initialize: function initialize() {
    this.channel = backbone_radio__WEBPACK_IMPORTED_MODULE_4___default().channel("config");
    this.type_options = this.getTypeOptions();
    var facade = backbone_radio__WEBPACK_IMPORTED_MODULE_4___default().channel("facade");
    this.listenTo(facade, "bind:validation", this.bindValidation);
    this.listenTo(facade, "unbind:validation", this.unbindValidation);
  },
  bindValidation: function bindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().bind(this);
  },
  unbindValidation: function unbindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().unbind(this);
  },
  getTypeOptions: function getTypeOptions() {
    return this.channel.request("get:typeOptions", "purchase");
  },
  onRender: function onRender() {
    var view;
    view = new widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("description"),
      title: "Description",
      field_name: "description"
    });
    this.showChildView("description", view);
    var ht_editable = this.channel.request("get:form_section", "lines:ht")["edit"];
    view = new widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("ht"),
      title: "Montant HT",
      field_name: "ht",
      addon: "€",
      required:  true && ht_editable,
      editable: ht_editable
    });
    this.showChildView("ht", view);
    var tva_editable = this.channel.request("get:form_section", "lines:tva")["edit"];
    view = new widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("tva"),
      title: "Montant TVA",
      field_name: "tva",
      addon: "€",
      required:  true && tva_editable,
      editable: tva_editable
    });
    this.showChildView("tva", view);
    view = new widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__["default"]({
      value: this.model.get("type_id"),
      title: "Type de dépense",
      field_name: "type_id",
      options: this.type_options,
      id_key: "id"
    });
    this.showChildView("type_id", view);
  },
  templateContext: function templateContext() {
    return {
      title: this.getOption("title"),
      add: this.getOption("add")
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineFormView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineTableView.js":
/*!****************************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineTableView.js ***!
  \****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone-validation */ "./node_modules/backbone-validation/dist/backbone-validation-amd.js");
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_validation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _SupplierOrderLineCollectionView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierOrderLineCollectionView.js */ "./src/supplier_order/views/SupplierOrderLineCollectionView.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! base/views/ErrorView.js */ "./src/base/views/ErrorView.js");





var SupplierOrderLineTableView = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  template: __webpack_require__(/*! ./templates/SupplierOrderLineTableView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineTableView.mustache"),
  regions: {
    lines: {
      el: "tbody",
      replaceElement: true
    },
    errors: ".group-errors"
  },
  ui: {
    add_btn: "button.add",
    total_ht: ".total_ht",
    total_tva: ".total_tva",
    total_ttc: ".total_ttc"
  },
  triggers: {
    "click @ui.add_btn": "line:add"
  },
  childViewTriggers: {
    "line:edit": "line:edit",
    "line:delete": "line:delete",
    "line:duplicate": "line:duplicate"
  },
  initialize: function initialize(options) {
    var channel = backbone_radio__WEBPACK_IMPORTED_MODULE_2___default().channel("facade");
    this.totalmodel = channel.request("get:model", "total");
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_2___default().channel("config");
    this.listenTo(channel, "change:lines", this.showTotals.bind(this));
    this.collection = options["collection"];
    this.listenTo(this.collection, "validated:invalid", this.showErrors);
    this.listenTo(this.collection, "validated:valid", this.hideErrors.bind(this));
    this.listenTo(channel, "bind:validation", this.bindValidation);
    this.listenTo(channel, "unbind:validation", this.unbindValidation);
  },
  bindValidation: function bindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().bind(this);
  },
  unbindValidation: function unbindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().unbind(this);
  },
  showErrors: function showErrors(model, errors) {
    this.detachChildView("errors");
    this.showChildView("errors", new base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_3__["default"]({
      errors: errors
    }));
    this.$el.addClass("error");
  },
  hideErrors: function hideErrors(model) {
    this.detachChildView("errors");
    this.$el.removeClass("error");
  },
  showTotals: function showTotals() {
    // this.getUI("total_ht").html(
    //     formatAmount(this.totalmodel.get('ht'))
    // );
    // this.getUI("total_tva").html(
    //     formatAmount(this.totalmodel.get('tva'))
    // );
    // this.getUI("total_ttc").html(
    //     formatAmount(this.totalmodel.get('ttc'))
    // );
  },
  templateContext: function templateContext() {
    return {
      edit: this.getOption("section")["edit"],
      add: this.getOption("section")["add"]
    };
  },
  onRender: function onRender() {
    var view = new _SupplierOrderLineCollectionView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      collection: this.collection,
      section: this.getOption("section")
    });
    this.showChildView("lines", view);
  },
  onAttach: function onAttach() {
    this.showTotals();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineTableView);

/***/ }),

/***/ "./src/supplier_order/views/SupplierOrderLineView.js":
/*!***********************************************************!*\
  !*** ./src/supplier_order/views/SupplierOrderLineView.js ***!
  \***********************************************************/
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
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");



__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ "./node_modules/jquery-ui/ui/effects/effect-highlight.js");
var SupplierOrderLineView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().View.extend({
  tagName: "tr",
  ui: {
    edit: "button.edit",
    "delete": "button.delete",
    duplicate: "button.duplicate"
  },
  triggers: {
    "click @ui.edit": "edit",
    "click @ui.delete": "delete",
    "click @ui.duplicate": "duplicate"
  },
  modelEvents: {
    change: "render"
  },
  template: __webpack_require__(/*! ./templates/SupplierOrderLineView.mustache */ "./src/supplier_order/views/templates/SupplierOrderLineView.mustache"),
  templateContext: function templateContext() {
    var total = this.model.total();
    var config = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("config");
    var order_ids = config.request("get:options", "supplier_orders");
    console.log(config);
    return {
      edit: this.getOption("edit"),
      "delete": this.getOption("delete"),
      duplicate: this.getOption("add") && order_ids.length > 0,
      total: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(total),
      ht_label: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ht")),
      tva_label: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("tva"))
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierOrderLineView);

/***/ }),

/***/ "./src/supplier_order/views/TotalView.js":
/*!***********************************************!*\
  !*** ./src/supplier_order/views/TotalView.js ***!
  \***********************************************/
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
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");



var TotalView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().View.extend({
  tagName: "div",
  template: __webpack_require__(/*! ./templates/TotalView.mustache */ "./src/supplier_order/views/templates/TotalView.mustache"),
  modelEvents: {
    "change:ttc": "render",
    "change:ht": "render",
    "change:tva": "render",
    "change:ttc_cae": "render",
    "change:ttc_worker": "render"
  },
  templateContext: function templateContext() {
    return {
      ht: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ht")),
      tva: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("tva")),
      ttc: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc")),
      ttc_cae: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc_cae")),
      ttc_worker: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc_worker"))
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (TotalView);

/***/ }),

/***/ "./src/supplier_order/views/templates/MainView.mustache":
/*!**************************************************************!*\
  !*** ./src/supplier_order/views/templates/MainView.mustache ***!
  \**************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"files separate_top content_vertical_padding\"></div>\n<div class=\"separate_top\">\n    <div class='messages-container'></div>\n    <div class='group-errors'></div>\n    <div class='totals grand-total'></div>\n    <div class='form-section'>\n        <div class='content'>\n            <div class='form-section'>\n                <div class='content'>\n                    <div class=\"supplier-order\">\n                    </div>\n                    <div class='lines-region'>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n<section id=\"supplierorderline_form\" class=\"modalRegion modal_view size_middle\"></section>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderFormView.mustache":
/*!***************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderFormView.mustache ***!
  \***************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"separate_top content_vertical_padding\">\n    <h3>Propriétés de la commande</h3>\n    <form class=\"form\">\n        <div class=\"form-section\">\n            <div class=\"layout flex two_cols\">\n                <div class='advance_percent'></div>\n                <div class='name'></div>\n            </div>\n            <div class=\"row form-row\">\n                <div class='col-md-6 supplier_id'></div>\n            </div>\n        </div>\n    </form>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineDuplicateFormView.mustache":
/*!****************************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineDuplicateFormView.mustache ***!
  \****************************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<div role=\"dialog\" id=\"supplierorderline-forms\" aria-modal=\"true\" aria-labelledby=\"supplierorderline-forms_title\">\n    <form>\n        <div class=\"modal_layout\">\n            <header>\n                <button tabindex='-1' type=\"button\" class=\"icon only unstyled close\" title=\"Fermer cette fenêtre\" aria-label=\"Fermer cette fenêtre\">\n                    <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n                </button>\n                <h2 id=\"supplierorderline-forms_title\">Dupliquer une ligne de commande fournisseur</h2>\n            </header>\n            <div class=\"modal_content_layout\">\n                <div class=\"modal_content\">\n                    <div class='separate_bottom'>\n                        <h3>Ligne</h3>\n                        "
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":14,"column":24},"end":{"line":14,"column":39}}}) : helper)))
    + "<br />\n                        <div class='expense_totals'>\n                            <div class=\"layout flex two_cols\">\n                                <div>\n                                    <p>HT&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht") || (depth0 != null ? lookupProperty(depth0,"ht") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht","hash":{},"data":data,"loc":{"start":{"line":18,"column":49},"end":{"line":18,"column":59}}}) : helper))) != null ? stack1 : "")
    + "</p>\n                                </div>\n                            </div>\n                            <div class=\"layout flex two_cols\">\n                                <div>\n                                    <p>TVA&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva") || (depth0 != null ? lookupProperty(depth0,"tva") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva","hash":{},"data":data,"loc":{"start":{"line":23,"column":50},"end":{"line":23,"column":61}}}) : helper))) != null ? stack1 : "")
    + "</p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class='select layout'></div>\n                </div>\n                <footer>\n                    <button\n                        class='btn btn-success btn-primary'\n                        type='submit'\n                        value='submit'>\n                        Dupliquer\n                    </button>\n                    <button\n                        class='btn'\n                        type='reset'\n                        value='submit'>\n                        Annuler\n                    </button>\n                </footer>\n            </div>\n        </div><!-- /.modal_layout -->\n    </form>\n</div><!-- /#supplierorderline-forms -->\n\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineEmptyView.mustache":
/*!********************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineEmptyView.mustache ***!
  \********************************************************************************/
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

  return "<td colspan='"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"colspan") || (depth0 != null ? lookupProperty(depth0,"colspan") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"colspan","hash":{},"data":data,"loc":{"start":{"line":1,"column":13},"end":{"line":1,"column":26}}}) : helper)))
    + "'><em>Aucun achat n’a été renseigné</em></td>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineFormPopupView.mustache":
/*!************************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineFormPopupView.mustache ***!
  \************************************************************************************/
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

  return "<div role=\"dialog\" id=\"supplierorderline-forms\" aria-modal=\"true\" aria-labelledby=\"supplierorderline-forms_title\">\n    <div class=\"modal_layout\">\n        <header>\n            <button tabindex='-1' type=\"button\" class=\"icon only unstyled close\"\n                    title=\"Fermer cette fenêtre\"\n            >\n                <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n            </button>\n            <h2 id=\"supplierorderline-forms_title\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":9,"column":51},"end":{"line":9,"column":62}}}) : helper)))
    + "</h2>\n        </header>\n        <div class=\"form-child\"><!-- replaced by child view --></div>\n    </div>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineFormView.mustache":
/*!*******************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineFormView.mustache ***!
  \*******************************************************************************/
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

  return "<form class='modal_content_layout layout'>\n    <div class=\"modal_content\">\n        <div class='row form-row'>\n            <div class='date required col-md-6'></div>\n            <div class='category col-md-6'></div>\n        </div>\n        <div class='row form-row'>\n            <div class='type_id required col-md-12'></div>\n        </div>\n        <div class='row form-row'>\n            <div class='description required col-md-12'></div>\n        </div>\n        <div class='row form-row'>\n            <div class='ht col-md-6'></div>\n            <div class='tva col-md-6'></div>\n        </div>\n        <div class='row form-row'>\n            <div class='business_link col-md-12'></div>\n        </div>\n    </div>\n    <footer>\n        <button class='btn btn-success btn-primary' type='submit' value='submit' formnovalidate>\n            "
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":23,"column":12},"end":{"line":23,"column":23}}}) : helper)))
    + "\n        </button>\n        <button class='btn btn-default secondary-action' type='reset' value='submit'>\n            Fermer\n        </button>\n    </footer>\n</form>";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineTableView.mustache":
/*!********************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineTableView.mustache ***!
  \********************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    return "					<th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "				<tr>\n					<td class=\"col_actions\" colspan=\"5\">\n						<button class='btn add'>\n							<svg><use href=\"/static/icons/icones.svg#plus\"></use></svg>Ajouter un achat\n						</button>\n					</td>\n				</tr>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.hooks.blockHelperMissing, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class=\"content_vertical_padding separate_top\">\n    <h2>Détail de la commande</h2>\n	<div class='group-errors'></div>\n	<div class=\"table_container\">\n		<table class=\"opa hover_table\">\n			<thead>\n				<th scope=\"col\" class=\"col_text\">Description</th>\n                <th scope=\"col\" class=\"col_number\" title=\"Montant Hors Taxes\"><span class=\"screen-reader-text\">Montant </span>H<span class=\"screen-reader-text\">ors </span>T<span class=\"screen-reader-text\">axes</span></th>\n                <th scope=\"col\" class=\"col_number\" title=\"Taux de TVA\"><span class=\"screen-reader-text\">Taux de </span>TVA</th>\n				<th scope=\"col\" class=\"col_number\">Total TTC</th>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"edit") || (depth0 != null ? lookupProperty(depth0,"edit") : depth0)) != null ? helper : alias2),(options={"name":"edit","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":11,"column":4},"end":{"line":13,"column":13}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"edit")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  buffer += "			</thead>\n			<tbody class='lines'>\n			</tbody>\n			<tfoot>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"add") || (depth0 != null ? lookupProperty(depth0,"add") : depth0)) != null ? helper : alias2),(options={"name":"add","hash":{},"fn":container.program(3, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":18,"column":4},"end":{"line":26,"column":12}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"add")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "			</tfoot>\n		</table>\n	</div>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/SupplierOrderLineView.mustache":
/*!***************************************************************************!*\
  !*** ./src/supplier_order/views/templates/SupplierOrderLineView.mustache ***!
  \***************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.hooks.blockHelperMissing, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<td class='col_actions width_three'>\n	<ul>\n		<li>\n            <button class='btn icon only edit' title='Modifier' aria-label='Modifier'>\n                <svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n            </button>\n        </li>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"duplicate") || (depth0 != null ? lookupProperty(depth0,"duplicate") : depth0)) != null ? helper : alias2),(options={"name":"duplicate","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":13,"column":8},"end":{"line":19,"column":22}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"duplicate")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  stack1 = ((helper = (helper = lookupProperty(helpers,"delete") || (depth0 != null ? lookupProperty(depth0,"delete") : depth0)) != null ? helper : alias2),(options={"name":"delete","hash":{},"fn":container.program(4, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":20,"column":8},"end":{"line":26,"column":19}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"delete")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </ul>\n</td>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "		<li>\n            <button class='btn icon only duplicate' title='Dupliquer' aria-label='Dupliquer'>\n                <svg><use href=\"/static/icons/icones.svg#copy\"></use></svg></button>\n            </button>\n        </li>\n";
},"4":function(container,depth0,helpers,partials,data) {
    return "		<li>\n            <button class='btn icon only negative delete'>\n                <svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg>\n            </button>\n        </li>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<td class=\"col_text\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":1,"column":21},"end":{"line":1,"column":38}}}) : helper)))
    + "</td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht_label") || (depth0 != null ? lookupProperty(depth0,"ht_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht_label","hash":{},"data":data,"loc":{"start":{"line":2,"column":23},"end":{"line":2,"column":39}}}) : helper))) != null ? stack1 : "")
    + "</td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva_label") || (depth0 != null ? lookupProperty(depth0,"tva_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva_label","hash":{},"data":data,"loc":{"start":{"line":3,"column":23},"end":{"line":3,"column":40}}}) : helper))) != null ? stack1 : "")
    + "</td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"total") || (depth0 != null ? lookupProperty(depth0,"total") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"total","hash":{},"data":data,"loc":{"start":{"line":4,"column":23},"end":{"line":4,"column":36}}}) : helper))) != null ? stack1 : "")
    + "</td>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"edit") || (depth0 != null ? lookupProperty(depth0,"edit") : depth0)) != null ? helper : alias2),(options={"name":"edit","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":5,"column":0},"end":{"line":29,"column":9}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"edit")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"useData":true});

/***/ }),

/***/ "./src/supplier_order/views/templates/TotalView.mustache":
/*!***************************************************************!*\
  !*** ./src/supplier_order/views/templates/TotalView.mustache ***!
  \***************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<div class=\"layout flex\">\n    <div>\n        <h4 class=\"content_vertical_padding\">Règlements</h4>\n    	<table class=\"top_align_table\">\n    		<tbody>\n    			<tr>\n    				<th scope=\"row\">CAE</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc_cae") || (depth0 != null ? lookupProperty(depth0,"ttc_cae") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc_cae","hash":{},"data":data,"loc":{"start":{"line":8,"column":31},"end":{"line":8,"column":46}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    			<tr>\n    				<th scope=\"row\">Entrepreneur</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc_worker") || (depth0 != null ? lookupProperty(depth0,"ttc_worker") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc_worker","hash":{},"data":data,"loc":{"start":{"line":12,"column":31},"end":{"line":12,"column":49}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    		</tbody>\n    	</table>\n    </div>\n	<div>\n    	<h4 class=\"content_vertical_padding\">Totaux</h4>\n    	<table class=\"top_align_table\">\n    		<tbody>\n    			<tr>\n    				<th scope=\"row\">Total HT</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht") || (depth0 != null ? lookupProperty(depth0,"ht") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht","hash":{},"data":data,"loc":{"start":{"line":23,"column":31},"end":{"line":23,"column":41}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    			<tr>\n    				<th scope=\"row\">Total TVA</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva") || (depth0 != null ? lookupProperty(depth0,"tva") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva","hash":{},"data":data,"loc":{"start":{"line":27,"column":31},"end":{"line":27,"column":42}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    			<tr>\n    				<th scope=\"row\">Total TTC</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc") || (depth0 != null ? lookupProperty(depth0,"ttc") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc","hash":{},"data":data,"loc":{"start":{"line":31,"column":31},"end":{"line":31,"column":42}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    		</tbody>\n    	</table>\n	</div>\n</div>\n";
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
/******/ 			"supplier_order": 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendor"], () => (__webpack_require__("./src/supplier_order/supplier_order.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	supplier_order = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=supplier_order.js.map