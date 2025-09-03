var supplier_invoice;
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./src/supplier_invoice/components/App.js":
/*!************************************************!*\
  !*** ./src/supplier_invoice/components/App.js ***!
  \************************************************/
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
/* harmony import */ var _views_MainView_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../views/MainView.js */ "./src/supplier_invoice/views/MainView.js");
/* harmony import */ var _Controller_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Controller.js */ "./src/supplier_invoice/components/Controller.js");
/* harmony import */ var _Router_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./Router.js */ "./src/supplier_invoice/components/Router.js");
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

/***/ "./src/supplier_invoice/components/Controller.js":
/*!*******************************************************!*\
  !*** ./src/supplier_invoice/components/Controller.js ***!
  \*******************************************************/
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

/***/ "./src/supplier_invoice/components/Facade.js":
/*!***************************************************!*\
  !*** ./src/supplier_invoice/components/Facade.js ***!
  \***************************************************/
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
/* harmony import */ var _models_TotalModel_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../models/TotalModel.js */ "./src/supplier_invoice/models/TotalModel.js");
/* harmony import */ var _models_SupplierInvoiceModel_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../models/SupplierInvoiceModel.js */ "./src/supplier_invoice/models/SupplierInvoiceModel.js");
/* harmony import */ var _models_SupplierInvoiceLineCollection_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../models/SupplierInvoiceLineCollection.js */ "./src/supplier_invoice/models/SupplierInvoiceLineCollection.js");
/* harmony import */ var _base_components_FacadeModelApiMixin__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../../base/components/FacadeModelApiMixin */ "./src/base/components/FacadeModelApiMixin.js");
/* harmony import */ var _common_models_StatusLogEntryCollection__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../../common/models/StatusLogEntryCollection */ "./src/common/models/StatusLogEntryCollection.js");









var FacadeClass = backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default().Object.extend(_base_components_FacadeModelApiMixin__WEBPACK_IMPORTED_MODULE_6__["default"]).extend({
  radioEvents: {
    "changed:line": "computeLineTotal",
    "changed:totals": "computeFundingTotals"
  },
  radioRequests: {
    "get:collection": "getCollectionRequest",
    "get:totalmodel": "getTotalModelRequest",
    "get:model": "getModelRequest",
    "is:valid": "isDataValid",
    "save:all": "saveAll"
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
    this.datas = context_datas;
    this.models = {};
    this.collections = {};
    this.models.total = new _models_TotalModel_js__WEBPACK_IMPORTED_MODULE_3__["default"]();
    var lines = context_datas["lines"];
    this.collections["lines"] = new _models_SupplierInvoiceLineCollection_js__WEBPACK_IMPORTED_MODULE_5__["default"](lines);
    this.collections.attachments = new _common_models_NodeFileCollection_js__WEBPACK_IMPORTED_MODULE_2__["default"](context_datas["attachments"]);
    this.collections.status_history = new _common_models_StatusLogEntryCollection__WEBPACK_IMPORTED_MODULE_7__["default"](context_datas.status_history);
    this.models.supplierInvoice = new _models_SupplierInvoiceModel_js__WEBPACK_IMPORTED_MODULE_4__["default"](context_datas);
    this.setModelUrl("supplierInvoice", AppOption["context_url"]);
    this.listenTo(this.models.supplierInvoice, "saved", this.reloadLines);
    this.computeLineTotal();
  },
  reloadLines: function reloadLines(savedData) {
    // savedData is null when a global save is performed (save button)
    if (savedData) {
      var savedAttrs = Object.keys(savedData);
      if (savedAttrs.includes("supplier_orders")) {
        var this_ = this;
        this.models.supplierInvoice.fetch().then(function (context_data) {
          var lines = context_data["lines"];
          this_.collections["lines"].set(lines);
        });
      }
    }
  },
  computeLineTotal: function computeLineTotal() {
    var collection = this.collections["lines"];
    var datas = {};
    datas["ht"] = collection.total_ht();
    datas["tva"] = collection.total_tva();
    datas["ttc"] = collection.total();
    var channel = this.getChannel();
    this.models.total.set(datas);
    channel.trigger("change:lines");

    // Refresh totals model
    this.computeFundingTotals();
  },
  computeFundingTotals: function computeFundingTotals() {
    var invoice = this.models.supplierInvoice;
    var datas = {};
    var ttc = this.models.total.get("ttc");
    // For now, this is unique to invoice
    var caePercentage = invoice.get("cae_percentage");
    datas["ttc_cae"] = (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.getPercent)(ttc, caePercentage);
    datas["ttc_worker"] = ttc - datas["ttc_cae"];
    this.models.total.set(datas);
  }
});
var Facade = new FacadeClass();
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Facade);

/***/ }),

/***/ "./src/supplier_invoice/components/Router.js":
/*!***************************************************!*\
  !*** ./src/supplier_invoice/components/Router.js ***!
  \***************************************************/
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

/***/ "./src/supplier_invoice/models/SupplierInvoiceLineCollection.js":
/*!**********************************************************************!*\
  !*** ./src/supplier_invoice/models/SupplierInvoiceLineCollection.js ***!
  \**********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _SupplierInvoiceLineModel_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SupplierInvoiceLineModel.js */ "./src/supplier_invoice/models/SupplierInvoiceLineModel.js");
/* harmony import */ var _base_models_BaseLineCollection_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/models/BaseLineCollection.js */ "./src/base/models/BaseLineCollection.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");


var SupplierInvoiceLineCollection = _base_models_BaseLineCollection_js__WEBPACK_IMPORTED_MODULE_1__["default"].extend({
  model: _SupplierInvoiceLineModel_js__WEBPACK_IMPORTED_MODULE_0__["default"],
  validate: function validate() {
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineCollection);

/***/ }),

/***/ "./src/supplier_invoice/models/SupplierInvoiceLineModel.js":
/*!*****************************************************************!*\
  !*** ./src/supplier_invoice/models/SupplierInvoiceLineModel.js ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* harmony import */ var underscore__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(underscore__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _base_models_BaseLineModel_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../base/models/BaseLineModel.js */ "./src/base/models/BaseLineModel.js");


var SupplierInvoiceLineModel = _base_models_BaseLineModel_js__WEBPACK_IMPORTED_MODULE_1__["default"].extend({
  validation: function validation() {
    return underscore__WEBPACK_IMPORTED_MODULE_0___default().extend(SupplierInvoiceLineModel.__super__.validation, {
      type_id: {
        required: true,
        msg: "Veuillez saisir un type de dépense"
      }
    });
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineModel);

/***/ }),

/***/ "./src/supplier_invoice/models/SupplierInvoiceModel.js":
/*!*************************************************************!*\
  !*** ./src/supplier_invoice/models/SupplierInvoiceModel.js ***!
  \*************************************************************/
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
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");



var SupplierInvoiceModel = _base_models_BaseModel_js__WEBPACK_IMPORTED_MODULE_1__["default"].extend(_base_models_DuplicableMixin_js__WEBPACK_IMPORTED_MODULE_2__["default"]).extend({
  props: ["id", "date", "remote_invoice_number", "supplier_orders", "orders_total", "orders_cae_total", "orders_worker_total", "orders_total_ht", "orders_total_tva", "cae_percentage", "customer_id", "project_id", "business_id", "customer_label", "project_label", "business_label", "internal", "payments", "cae_payments", "user_payments", "payer_name", "payer_id", "supplier_name", "supplier_id"],
  defaults: {
    supplier_orders: [],
    business_label: "",
    project_label: "",
    customer_label: "",
    remote_invoice_number: ""
  },
  validation: {
    date: {
      required: true,
      msg: "La date est requise"
    },
    remote_invoice_number: {
      required: true,
      msg: "Le numéro de facture du fournisseur est requis"
    },
    payer_id: {
      required: function required(val, attr, computed) {
        return computed.cae_percentage < 100;
      },
      msg: "Préciser quel entrepreneur réalisera l'avance"
    },
    supplier_id: {
      required: true,
      msg: "Le fournisseur est requis"
    }
  },
  initialize: function initialize() {
    SupplierInvoiceModel.__super__.initialize.apply(this, arguments);
    this.on("change:supplier_orders", this.ensureTypesIsList, this);
  },
  ensureTypesIsList: function ensureTypesIsList() {
    var orders = this.get("supplier_orders");
    if (!_.isArray(orders)) {
      this.attributes["supplier_orders"] = [orders];
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceModel);

/***/ }),

/***/ "./src/supplier_invoice/models/TotalModel.js":
/*!***************************************************!*\
  !*** ./src/supplier_invoice/models/TotalModel.js ***!
  \***************************************************/
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

/***/ "./src/supplier_invoice/supplier_invoice.js":
/*!**************************************************!*\
  !*** ./src/supplier_invoice/supplier_invoice.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _backbone_tools_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../backbone-tools.js */ "./src/backbone-tools.js");
/* harmony import */ var _components_App_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/App.js */ "./src/supplier_invoice/components/App.js");
/* harmony import */ var _components_Facade_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/Facade.js */ "./src/supplier_invoice/components/Facade.js");
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

/***/ "./src/supplier_invoice/views/MainView.js":
/*!************************************************!*\
  !*** ./src/supplier_invoice/views/MainView.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_15___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_15__);
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var common_views_StatusFormPopupView_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! common/views/StatusFormPopupView.js */ "./src/common/views/StatusFormPopupView.js");
/* harmony import */ var _models_SupplierInvoiceLineModel_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../models/SupplierInvoiceLineModel.js */ "./src/supplier_invoice/models/SupplierInvoiceLineModel.js");
/* harmony import */ var _SupplierInvoiceLineTableView_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./SupplierInvoiceLineTableView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineTableView.js");
/* harmony import */ var _SupplierInvoiceLineFormPopupView_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./SupplierInvoiceLineFormPopupView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineFormPopupView.js");
/* harmony import */ var _SupplierInvoiceFormView_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./SupplierInvoiceFormView.js */ "./src/supplier_invoice/views/SupplierInvoiceFormView.js");
/* harmony import */ var _SupplierInvoiceLineDuplicateFormView_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./SupplierInvoiceLineDuplicateFormView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineDuplicateFormView.js");
/* harmony import */ var _TotalView_js__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./TotalView.js */ "./src/supplier_invoice/views/TotalView.js");
/* harmony import */ var base_views_MessageView_js__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! base/views/MessageView.js */ "./src/base/views/MessageView.js");
/* harmony import */ var base_views_LoginView_js__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! base/views/LoginView.js */ "./src/base/views/LoginView.js");
/* harmony import */ var common_views_NodeFileCollectionView_js__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! common/views/NodeFileCollectionView.js */ "./src/common/views/NodeFileCollectionView.js");
/* harmony import */ var _backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../../backbone-tools.js */ "./src/backbone-tools.js");
/* harmony import */ var _tools_js__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ../../tools.js */ "./src/tools.js");
/* harmony import */ var base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! base/views/ErrorView.js */ "./src/base/views/ErrorView.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");
/* provided dependency */ var $ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");
















var MainView = backbone_marionette__WEBPACK_IMPORTED_MODULE_15___default().View.extend({
  className: "container-fluid page-content",
  template: __webpack_require__(/*! ./templates/MainView.mustache */ "./src/supplier_invoice/views/templates/MainView.mustache"),
  regions: {
    modalRegion: ".modalRegion",
    supplierInvoiceForm: ".supplier-invoice",
    linesRegion: ".lines-region",
    files: ".files",
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
    "invoice:modified": "onDataModified",
    "line:duplicate": "onLineDuplicate",
    "status:change": "onStatusChange"
  },
  onDataModified: function onDataModified(name, value) {
    if (name == "supplier_id") {
      this.onSupplierModified(value);
    }
    var totals = this.facade.request("get:model", "total");
    var ttc = totals.get("ttc");
  },
  onSupplierModified: function onSupplierModified(supplier_id) {
    /* jQuery hack to update supplier static part
     * defined in supplier_invoice.mako
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
  showSupplierInvoiceForm: function showSupplierInvoiceForm() {
    var edit = this.config.request("get:form_section", "general")["edit"];
    var model = this.facade.request("get:model", "supplierInvoice");
    var view = new _SupplierInvoiceFormView_js__WEBPACK_IMPORTED_MODULE_6__["default"]({
      model: model,
      edit: edit
    });
    this.showChildView("supplierInvoiceForm", view);
  },
  onLineAdd: function onLineAdd(childView) {
    var model = new _models_SupplierInvoiceLineModel_js__WEBPACK_IMPORTED_MODULE_3__["default"]({});
    this.showLineForm(model, true, "Ajouter un achat");
  },
  onLineEdit: function onLineEdit(childView) {
    this.showLineForm(childView.model, false, "Modifier un achat");
  },
  showLineForm: function showLineForm(model, add, title) {
    var view = new _SupplierInvoiceLineFormPopupView_js__WEBPACK_IMPORTED_MODULE_5__["default"]({
      title: title,
      add: add,
      model: model,
      destCollection: this.facade.request("get:collection", "lines")
    });
    this.showChildView("modalRegion", view);
  },
  showDuplicateForm: function showDuplicateForm(model) {
    var view = new _SupplierInvoiceLineDuplicateFormView_js__WEBPACK_IMPORTED_MODULE_7__["default"]({
      model: model
    });
    this.showChildView("modalRegion", view);
  },
  onLineDuplicate: function onLineDuplicate(childView) {
    this.showDuplicateForm(childView.model);
  },
  onDeleteSuccess: function onDeleteSuccess() {
    (0,_backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerSuccess)("Vos données ont bien été supprimées");
  },
  onDeleteError: function onDeleteError() {
    (0,_backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerError)("Une erreur a été rencontrée lors de la " + "suppression de cet élément");
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
  showLinesRegion: function showLinesRegion() {
    var section = this.config.request("get:form_section", "lines");
    var collection = this.facade.request("get:collection", "lines");
    var view = new _SupplierInvoiceLineTableView_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      collection: collection,
      section: section
    });
    this.showChildView("linesRegion", view);
  },
  showFilesRegion: function showFilesRegion() {
    var collection = this.facade.request("get:collection", "attachments");
    var view = new common_views_NodeFileCollectionView_js__WEBPACK_IMPORTED_MODULE_11__["default"]({
      collection: collection,
      edit: this.edit
    });
    this.showChildView("files", view);
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
    this.showSupplierInvoiceForm();
    this.showLinesRegion();
    this.showTotals();
    this.showMessages();
  },
  _showStatusModal: function _showStatusModal(action_model) {
    var view = new common_views_StatusFormPopupView_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      action: action_model
    });
    this.showChildView("modalRegion", view);
  },
  formOk: function formOk() {
    var result = true;
    var errors = this.facade.request("is:valid");
    if (!_.isEmpty(errors)) {
      console.log(errors);
      this.showChildView("errors", new base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_14__["default"]({
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
    if (this.config.request("get:form_section", "general")["edit"]) {
      if (!action_model.get("status")) {
        return;
      }
      (0,_tools_js__WEBPACK_IMPORTED_MODULE_13__.showLoader)();
      if (action_model.get("status") != "draft") {
        if (!this.formOk()) {
          document.body.scrollTop = document.documentElement.scrollTop = 0;
          (0,_tools_js__WEBPACK_IMPORTED_MODULE_13__.hideLoader)();
          return;
        }
      }
      // Prior to any status change, we want to save and make sure it went OK

      this.facade.request("save:all").then(function () {
        (0,_tools_js__WEBPACK_IMPORTED_MODULE_13__.hideLoader)();
        _this._showStatusModal(action_model);
      }, function () {
        (0,_tools_js__WEBPACK_IMPORTED_MODULE_13__.hideLoader)();
        (0,_backbone_tools_js__WEBPACK_IMPORTED_MODULE_12__.displayServerError)("Erreur pendant la sauvegarde");
      });
    } else {
      this._showStatusModal(action_model);
    }
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (MainView);

/***/ }),

/***/ "./src/supplier_invoice/views/PaymentPartView.js":
/*!*******************************************************!*\
  !*** ./src/supplier_invoice/views/PaymentPartView.js ***!
  \*******************************************************/
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
/* harmony import */ var _date_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../date.js */ "./src/date.js");
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");
/* harmony import */ var _string_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../string.js */ "./src/string.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");






/** Block with details about part of the invoice
 *
 * CAE part or worker part
 */
var PaymentPartView = backbone_marionette__WEBPACK_IMPORTED_MODULE_4___default().View.extend({
  template: __webpack_require__(/*! ./templates/PaymentPartView.mustache */ "./src/supplier_invoice/views/templates/PaymentPartView.mustache"),
  initialize: function initialize() {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    var supplierInvoice = this.facade.request("get:model", "supplierInvoice");
    this.payments = this.getOption("payments");
    this.paymentsRecipient = supplierInvoice.get("supplier_name");
  },
  /*** Prepare payment for rendering into template
   */
  paymentTemplateContext: function paymentTemplateContext(payment) {
    var context = _.clone(payment);
    context.amount = (0,_math_js__WEBPACK_IMPORTED_MODULE_2__.formatAmount)(payment.amount);
    context.date = (0,_date_js__WEBPACK_IMPORTED_MODULE_1__.formatDate)(payment.date);
    return context;
  },
  templateContext: function templateContext() {
    var paymentWording = this.getOption("payment_wording");
    return {
      payments: this.payments.map(this.paymentTemplateContext),
      multiPayment: this.payments.length > 1,
      noPayment: this.payments.length < 1,
      paymentsRecipient: this.getOption("payments_recipient"),
      paymentWording: paymentWording,
      paymentWordingCapitalized: (0,_string_js__WEBPACK_IMPORTED_MODULE_3__.capitalize)(paymentWording)
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (PaymentPartView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceFormView.js":
/*!***************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceFormView.js ***!
  \***************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone-validation */ "./node_modules/backbone-validation/dist/backbone-validation-amd.js");
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_validation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! base/behaviors/FormBehavior.js */ "./src/base/behaviors/FormBehavior.js");
/* harmony import */ var widgets_DateWidget_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! widgets/DateWidget.js */ "./src/widgets/DateWidget.js");
/* harmony import */ var widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! widgets/InputWidget.js */ "./src/widgets/InputWidget.js");
/* harmony import */ var widgets_CheckboxListWidget_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! widgets/CheckboxListWidget.js */ "./src/widgets/CheckboxListWidget.js");
/* harmony import */ var widgets_PercentInputWidget_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! widgets/PercentInputWidget.js */ "./src/widgets/PercentInputWidget.js");
/* harmony import */ var widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! widgets/SelectWidget.js */ "./src/widgets/SelectWidget.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_7__);









var SupplierInvoiceFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_8___default().View.extend({
  tagName: "div",
  behaviors: [base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_1__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierInvoiceFormView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceFormView.mustache"),
  regions: {
    date: ".date",
    remote_invoice_number: ".remote_invoice_number",
    supplier_orders: ".supplier-orders",
    supplier_id: ".supplier_id",
    payer_id: ".payer_id",
    advance_percent: ".advance_percent"
  },
  childViewEvents: {
    finish: "onFinish",
    change: "onChange"
  },
  initialize: function initialize() {
    this.config = backbone_radio__WEBPACK_IMPORTED_MODULE_7___default().channel("config");
    this.orders_options = this.config.request("get:options", "supplier_orders");
    this.suppliers_options = this.config.request("get:options", "suppliers");
    this.payers_options = this.config.request("get:options", "payers");
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_7___default().channel("facade");
    this.listenTo(this.facade, "bind:validation", this.bindValidation);
    this.listenTo(this.facade, "unbind:validation", this.unbindValidation);
  },
  bindValidation: function bindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().bind(this);
  },
  unbindValidation: function unbindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().unbind(this);
  },
  onChange: function onChange(name, value) {
    this.model.set(name, value);
    this.triggerMethod("invoice:modified", name, value);
    this.triggerMethod("data:modified", name, value);
  },
  onFinish: function onFinish(name, value) {
    this.model.set(name, value);
    this.triggerMethod("invoice:modified", name, value);
    this.triggerMethod("data:persist", name, value);
  },
  showDatePicker: function showDatePicker() {
    var editable = this.config.request("get:form_section", "general:date")["edit"];
    var view = new widgets_DateWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("date"),
      title: "Date",
      description: "Date de la facture",
      field_name: "date",
      editable: editable,
      required: true
    });
    this.showChildView("date", view);
  },
  showRemoteInvoiceNumber: function showRemoteInvoiceNumber() {
    var editable = this.config.request("get:form_section", "general:remote_invoice_number")["edit"];
    var view = new widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_3__["default"]({
      value: this.model.get("remote_invoice_number"),
      title: "N° de facture du fournisseur",
      field_name: "remote_invoice_number",
      editable: editable,
      required: true
    });
    this.showChildView("remote_invoice_number", view);
  },
  showSupplierId: function showSupplierId() {
    var editable = this.config.request("get:form_section", "general:supplier_id")["edit"];
    var widget_params = {
      options: this.suppliers_options,
      title: "Fournisseur",
      field_name: "supplier_id",
      editable: editable,
      value: this.model.get("supplier_id"),
      required: true
    };
    if (!this.model.has("supplier_id")) {
      widget_params["placeholder"] = "Sélectionner";
    }
    var view = new widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_6__["default"](widget_params);
    this.showChildView("supplier_id", view);
  },
  showSupplierOrders: function showSupplierOrders() {
    var editable = this.config.request("get:form_section", "general:supplier_orders")["edit"];
    var supplier_id = this.model.get("supplier_id");
    var view = new widgets_CheckboxListWidget_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      value: this.model.get("supplier_orders"),
      title: "Commandes fournisseur associées",
      field_name: "supplier_orders",
      editable: editable,
      options: this.orders_options,
      togglable: true,
      multiple: true,
      id_key: "id",
      optionFilter: function optionFilter(option, currentOption) {
        // Keep only the orders from same supplier
        return currentOption == undefined && supplier_id && option.supplier_id == supplier_id || currentOption && option.supplier_id == currentOption.supplier_id;
      },
      addBtnIcon: "link",
      addBtnLabel: "Associer une commande",
      noOptionMessage: "Aucune commande fournisseur associée",
      removeItemConfirmationMsg: "Si vous rompez le lien vers cette " + "commande, toutes les lignes associées seront retirées de la" + " présente facture fournisseur."
    });
    this.showChildView("supplier_orders", view);
  },
  showPayerId: function showPayerId() {
    var editable = this.config.request("get:form_section", "general:payer_id")["edit"];
    var view = new widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_6__["default"]({
      options: this.payers_options,
      title: "Entrepreneur",
      editable: editable,
      field_name: "payer_id",
      placeholder: "Sélectionner",
      value: this.model.get("payer_id")
    });
    this.showChildView("payer_id", view);
  },
  showCaePercentage: function showCaePercentage() {
    var editable = this.config.request("get:form_section", "general:cae_percentage")["edit"];
    var view = new widgets_PercentInputWidget_js__WEBPACK_IMPORTED_MODULE_5__["default"]({
      value: this.model.get("cae_percentage"),
      title: "Part de paiement direct par la CAE",
      field_name: "cae_percentage",
      editable: editable
    });
    this.showChildView("advance_percent", view);
  },
  onRender: function onRender() {
    this.showDatePicker();
    this.showRemoteInvoiceNumber();
    if (this.config.request("has:form_section", "general:supplier_id")) {
      this.showSupplierId();
    }
    if (this.config.request("has:form_section", "general:supplier_orders")) {
      this.showSupplierOrders();
    }
    if (this.config.request("has:form_section", "general:payer_id")) {
      this.showPayerId();
    }
    if (this.config.request("has:form_section", "general:cae_percentage")) {
      this.showCaePercentage();
    }
  },
  onSuccessSync: function onSuccessSync() {
    var facade = backbone_radio__WEBPACK_IMPORTED_MODULE_7___default().channel("facade");
    facade.trigger("navigate", "index");
    this.render();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceFormView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineCollectionView.js":
/*!*************************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineCollectionView.js ***!
  \*************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _SupplierInvoiceLineView_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SupplierInvoiceLineView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineView.js");
/* harmony import */ var _SupplierInvoiceLineEmptyView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierInvoiceLineEmptyView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineEmptyView.js");



var SupplierInvoiceLineCollectionView = backbone_marionette__WEBPACK_IMPORTED_MODULE_2___default().CollectionView.extend({
  tagName: "tbody",
  // Bubble up child view events
  childViewTriggers: {
    edit: "line:edit",
    "delete": "line:delete",
    bookmark: "bookmark:add",
    duplicate: "line:duplicate"
  },
  childView: _SupplierInvoiceLineView_js__WEBPACK_IMPORTED_MODULE_0__["default"],
  emptyView: _SupplierInvoiceLineEmptyView_js__WEBPACK_IMPORTED_MODULE_1__["default"],
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineCollectionView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineDuplicateFormView.js":
/*!****************************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineDuplicateFormView.js ***!
  \****************************************************************************/
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






var SupplierInvoiceLineDuplicateFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default().View.extend({
  id: "supplierorderline-duplicate-form",
  behaviors: [_base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_1__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineDuplicateFormView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineDuplicateFormView.mustache"),
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
    this.options = channel.request("get:options", "supplier_invoices");
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
      title: "Facture fournisseur vers laquelle dupliquer",
      id_key: "id",
      field_name: "supplier_invoice_id",
      value: this.model.get("supplier_invoice_id")
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineDuplicateFormView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineEmptyView.js":
/*!********************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineEmptyView.js ***!
  \********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_0__);

var SupplierInvoiceLineEmptyView = backbone_marionette__WEBPACK_IMPORTED_MODULE_0___default().View.extend({
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineEmptyView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineEmptyView.mustache"),
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineEmptyView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineFormPopupView.js":
/*!************************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineFormPopupView.js ***!
  \************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../base/behaviors/ModalBehavior.js */ "./src/base/behaviors/ModalBehavior.js");
/* harmony import */ var _SupplierInvoiceLineFormView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierInvoiceLineFormView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineFormView.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_2__);




var SupplierInvoiceLineFormPopupView = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().View.extend({
  behaviors: [_base_behaviors_ModalBehavior_js__WEBPACK_IMPORTED_MODULE_0__["default"]],
  id: "supplierorderline-form-popup-modal",
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineFormPopupView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineFormPopupView.mustache"),
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
    var view = new _SupplierInvoiceLineFormView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineFormPopupView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineFormView.js":
/*!*******************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineFormView.js ***!
  \*******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../base/behaviors/FormBehavior.js */ "./src/base/behaviors/FormBehavior.js");
/* harmony import */ var _widgets_SelectBusinessWidget_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../widgets/SelectBusinessWidget.js */ "./src/widgets/SelectBusinessWidget.js");
/* harmony import */ var _widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../widgets/InputWidget.js */ "./src/widgets/InputWidget.js");
/* harmony import */ var _widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../widgets/SelectWidget.js */ "./src/widgets/SelectWidget.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../tools */ "./src/tools.js");
/* provided dependency */ var _ = __webpack_require__(/*! underscore */ "./node_modules/underscore/underscore.js");


// import DateWidget from '../../widgets/DateWidget.js';





var SupplierInvoiceLineFormView = backbone_marionette__WEBPACK_IMPORTED_MODULE_6___default().View.extend({
  id: "mainform-container",
  className: "modal_overflow",
  behaviors: [_base_behaviors_FormBehavior_js__WEBPACK_IMPORTED_MODULE_0__["default"]],
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineFormView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineFormView.mustache"),
  regions: {
    // 'date': '.date',
    type_id: ".type_id",
    description: ".description",
    ht: ".ht",
    tva: ".tva",
    business_link: ".business_link"
  },
  // Bubble up child view events
  //
  childViewTriggers: {
    change: "data:modified"
  },
  childViewEvents: {
    finish: "onChildChange"
  },
  onBeforeSync: _tools__WEBPACK_IMPORTED_MODULE_5__.showLoader,
  onFormSubmitted: _tools__WEBPACK_IMPORTED_MODULE_5__.hideLoader,
  initialize: function initialize() {
    this.channel = backbone_radio__WEBPACK_IMPORTED_MODULE_4___default().channel("config");
    this.type_options = this.getTypeOptions();
    this.customers_url = this.channel.request("get:options", "company_customers_url");
    this.projects_url = this.channel.request("get:options", "company_projects_url");
    this.businesses_url = this.channel.request("get:options", "company_businesses_url");
  },
  onChildChange: function onChildChange(field_name, value) {
    this.triggerMethod("data:modified", field_name, value);
  },
  getTypeOptions: function getTypeOptions() {
    return this.channel.request("get:typeOptions", "purchase");
  },
  onRender: function onRender() {
    var view;
    view = new _widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("description"),
      title: "Description",
      field_name: "description"
    });
    this.showChildView("description", view);
    var ht_editable = this.channel.request("get:form_section", "lines:ht")["edit"];
    view = new _widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("ht"),
      title: "Montant HT",
      field_name: "ht",
      addon: "€",
      required:  true && ht_editable,
      editable: ht_editable
    });
    this.showChildView("ht", view);
    var tva_editable = this.channel.request("get:form_section", "lines:tva")["edit"];
    view = new _widgets_InputWidget_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
      value: this.model.get("tva"),
      title: "Montant TVA",
      field_name: "tva",
      addon: "€",
      required:  true && tva_editable,
      editable: tva_editable
    });
    this.showChildView("tva", view);
    view = new _widgets_SelectWidget_js__WEBPACK_IMPORTED_MODULE_3__["default"]({
      value: this.model.get("type_id"),
      title: "Type de dépense",
      field_name: "type_id",
      options: this.type_options,
      placeholder: "",
      id_key: "id",
      required: true
    });
    this.showChildView("type_id", view);
    view = new _widgets_SelectBusinessWidget_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      title: "Client concerné",
      customers_url: this.customers_url,
      projects_url: this.projects_url,
      businesses_url: this.businesses_url,
      customer_value: this.model.get("customer_id"),
      project_value: this.model.get("project_id"),
      business_value: this.model.get("business_id"),
      customer_label: this.model.get("customer_label"),
      project_label: this.model.get("project_label"),
      business_label: this.model.get("business_label")
    });
    this.showChildView("business_link", view);
  },
  afterSerializeForm: function afterSerializeForm(datas) {
    var modifiedDatas = _.clone(datas);
    // Hack to allow setting those fields to null.
    // Otherwise $.serializeForm skips <select> with no value selected
    modifiedDatas["customer_id"] = this.model.get("customer_id");
    modifiedDatas["project_id"] = this.model.get("project_id");
    modifiedDatas["business_id"] = this.model.get("business_id");
    return modifiedDatas;
  },
  templateContext: function templateContext() {
    return {
      title: this.getOption("title"),
      add: this.getOption("add")
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineFormView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineTableView.js":
/*!********************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineTableView.js ***!
  \********************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! backbone-validation */ "./node_modules/backbone-validation/dist/backbone-validation-amd.js");
/* harmony import */ var backbone_validation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(backbone_validation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _SupplierInvoiceLineCollectionView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SupplierInvoiceLineCollectionView.js */ "./src/supplier_invoice/views/SupplierInvoiceLineCollectionView.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone.radio */ "./node_modules/backbone.radio/build/backbone.radio.js");
/* harmony import */ var backbone_radio__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone_radio__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");
/* harmony import */ var _base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../../base/views/ErrorView.js */ "./src/base/views/ErrorView.js");






var SupplierInvoiceLineTableView = backbone_marionette__WEBPACK_IMPORTED_MODULE_5___default().View.extend({
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineTableView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineTableView.mustache"),
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
    this.listenTo(channel, "change:lines", this.showTotals.bind(this));
    this.collection = options["collection"];
    this.listenTo(this.collection, "validated:invalid", this.showErrors);
    this.listenTo(this.collection, "validated:valid", this.hideErrors.bind(this));
    this.listenTo(channel, "bind:validation", this.bindValidation);
    this.listenTo(channel, "unbind:validation", this.unbindValidation);
  },
  bindValidation: function bindValidation() {
    console.log("bindValidation");
    console.log(this.model);
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().bind(this);
  },
  unbindValidation: function unbindValidation() {
    backbone_validation__WEBPACK_IMPORTED_MODULE_0___default().unbind(this);
  },
  showErrors: function showErrors(model, errors) {
    this.detachChildView("errors");
    this.showChildView("errors", new _base_views_ErrorView_js__WEBPACK_IMPORTED_MODULE_4__["default"]({
      errors: errors
    }));
    this.$el.addClass("error");
  },
  hideErrors: function hideErrors(model) {
    this.detachChildView("errors");
    this.$el.removeClass("error");
  },
  showTotals: function showTotals() {
    this.getUI("total_ht").html((0,_math_js__WEBPACK_IMPORTED_MODULE_3__.formatAmount)(this.totalmodel.get("ht")));
    this.getUI("total_tva").html((0,_math_js__WEBPACK_IMPORTED_MODULE_3__.formatAmount)(this.totalmodel.get("tva")));
    this.getUI("total_ttc").html((0,_math_js__WEBPACK_IMPORTED_MODULE_3__.formatAmount)(this.totalmodel.get("ttc")));
  },
  templateContext: function templateContext() {
    return {
      edit: this.getOption("section")["edit"],
      add: this.getOption("section")["add"]
    };
  },
  onRender: function onRender() {
    var view = new _SupplierInvoiceLineCollectionView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      collection: this.collection,
      section: this.getOption("section")
    });
    this.showChildView("lines", view);
  },
  onAttach: function onAttach() {
    this.showTotals();
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineTableView);

/***/ }),

/***/ "./src/supplier_invoice/views/SupplierInvoiceLineView.js":
/*!***************************************************************!*\
  !*** ./src/supplier_invoice/views/SupplierInvoiceLineView.js ***!
  \***************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! backbone.marionette */ "./node_modules/backbone.marionette/lib/backbone.marionette.js");
/* harmony import */ var backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(backbone_marionette__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");
/* harmony import */ var _common_views_BusinessLinkView_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../common/views/BusinessLinkView.js */ "./src/common/views/BusinessLinkView.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! backbone */ "./node_modules/backbone/backbone.js");
/* harmony import */ var backbone__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(backbone__WEBPACK_IMPORTED_MODULE_2__);




__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ "./node_modules/jquery-ui/ui/effects/effect-highlight.js");
var SupplierInvoiceLineView = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().View.extend({
  tagName: "tr",
  regions: {
    businessLink: {
      el: ".business-link"
    }
  },
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
  template: __webpack_require__(/*! ./templates/SupplierInvoiceLineView.mustache */ "./src/supplier_invoice/views/templates/SupplierInvoiceLineView.mustache"),
  templateContext: function templateContext() {
    var total = this.model.total();
    var type_ = this.model.getType();
    var label = "";
    if (type_) {
      label = type_.get("label");
    }
    var config = backbone__WEBPACK_IMPORTED_MODULE_2__.Radio.channel("config");
    var invoice_ids = config.request("get:options", "supplier_invoices");
    return {
      typelabel: label,
      edit: this.getOption("edit"),
      total: (0,_math_js__WEBPACK_IMPORTED_MODULE_0__.formatAmount)(total),
      ht_label: (0,_math_js__WEBPACK_IMPORTED_MODULE_0__.formatAmount)(this.model.get("ht")),
      tva_label: (0,_math_js__WEBPACK_IMPORTED_MODULE_0__.formatAmount)(this.model.get("tva")),
      duplicate: invoice_ids.length > 0,
      "delete": this.getOption("delete")
    };
  },
  onRender: function onRender() {
    var view = new _common_views_BusinessLinkView_js__WEBPACK_IMPORTED_MODULE_1__["default"]({
      customer_label: this.model.get("customer_label"),
      project_label: this.model.get("project_label"),
      business_label: this.model.get("business_label")
    });
    this.showChildView("businessLink", view);
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SupplierInvoiceLineView);

/***/ }),

/***/ "./src/supplier_invoice/views/TotalView.js":
/*!*************************************************!*\
  !*** ./src/supplier_invoice/views/TotalView.js ***!
  \*************************************************/
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
/* harmony import */ var _math_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../math.js */ "./src/math.js");
/* harmony import */ var _PaymentPartView_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./PaymentPartView.js */ "./src/supplier_invoice/views/PaymentPartView.js");




var TotalView = backbone_marionette__WEBPACK_IMPORTED_MODULE_3___default().View.extend({
  tagName: "div",
  template: __webpack_require__(/*! ./templates/TotalView.mustache */ "./src/supplier_invoice/views/templates/TotalView.mustache"),
  modelEvents: {
    "change:ttc": "render",
    "change:ht": "render",
    "change:tva": "render",
    "change:ttc_cae": "render",
    "change:ttc_worker": "render"
  },
  regions: {
    caePartRegion: ".cae-part-region",
    workerPartRegion: ".worker-part-region"
  },
  initialize: function initialize() {
    this.facade = backbone_radio__WEBPACK_IMPORTED_MODULE_0___default().channel("facade");
    this.supplierInvoice = this.facade.request("get:model", "supplierInvoice");
  },
  onRender: function onRender() {
    if (this.supplierInvoice.get("internal")) {
      var view = new _PaymentPartView_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
        payments: this.supplierInvoice.get("payments"),
        payment_wording: "paiement",
        payments_recipient: this.supplierInvoice.get("supplier_name")
      });
      this.showChildView("workerPartRegion", view);
    } else {
      var cae_percentage = this.supplierInvoice.get("cae_percentage");
      if (cae_percentage > 0) {
        var view = new _PaymentPartView_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
          payments: this.supplierInvoice.get("cae_payments"),
          payment_wording: "paiement",
          payments_recipient: this.supplierInvoice.get("supplier_name")
        });
        this.showChildView("caePartRegion", view);
      }
      if (cae_percentage < 100) {
        var view = new _PaymentPartView_js__WEBPACK_IMPORTED_MODULE_2__["default"]({
          payments: this.supplierInvoice.get("user_payments"),
          payment_wording: "remboursement",
          payments_recipient: this.supplierInvoice.get("payer_name")
        });
        this.showChildView("workerPartRegion", view);
      }
    }
  },
  templateContext: function templateContext() {
    var orders_total = this.supplierInvoice.get("orders_total");
    var invoice_total = this.model.get("ttc");
    var totals_mismatch = orders_total != invoice_total && orders_total > 0;
    return {
      ht: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ht")),
      tva: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("tva")),
      ttc: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc")),
      ttc_cae: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc_cae")),
      ttc_worker: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.model.get("ttc_worker")),
      orders_ttc_worker: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.supplierInvoice.get("orders_worker_total")),
      orders_ttc_cae: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.supplierInvoice.get("orders_cae_total")),
      orders_ht: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.supplierInvoice.get("orders_total_ht")),
      orders_tva: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.supplierInvoice.get("orders_total_tva")),
      orders_ttc: (0,_math_js__WEBPACK_IMPORTED_MODULE_1__.formatAmount)(this.supplierInvoice.get("orders_total")),
      cae_percentage: Number(this.supplierInvoice.get("cae_percentage")),
      worker_percentage: 100 - this.supplierInvoice.get("cae_percentage"),
      totals_mismatch: totals_mismatch,
      payments: this.supplierInvoice.get("payments")
    };
  }
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (TotalView);

/***/ }),

/***/ "./src/supplier_invoice/views/templates/MainView.mustache":
/*!****************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/MainView.mustache ***!
  \****************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"files separate_top content_vertical_padding\"></div>\n<div class=\"separate_top\">\n    <div class='messages-container'></div>\n    <div class='group-errors'></div>\n    <div class='totals grand-total'></div>\n    <div class='form-section'>\n        <div class='content'>\n            <div class='form-section'>\n                <div class='content'>\n                    <div class=\"supplier-invoice\"></div>\n                    <div class='lines-region'></div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>\n<section id=\"supplierinvoiceline_form\"\n         class=\"modalRegion modal_view size_middle\"></section>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/PaymentPartView.mustache":
/*!***********************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/PaymentPartView.mustache ***!
  \***********************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<p class=\"content_vertical_padding\">\n    <em>Aucun "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"paymentWording") || (depth0 != null ? lookupProperty(depth0,"paymentWording") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"paymentWording","hash":{},"data":data,"loc":{"start":{"line":3,"column":14},"end":{"line":3,"column":36}}}) : helper))) != null ? stack1 : "")
    + " effectué pour l’instant</em>\n</p>\n";
},"3":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return ((stack1 = lookupProperty(helpers,"if").call(depth0 != null ? depth0 : (container.nullContext || {}),(depth0 != null ? lookupProperty(depth0,"multiPayment") : depth0),{"name":"if","hash":{},"fn":container.program(4, data, 0),"inverse":container.program(8, data, 0),"data":data,"loc":{"start":{"line":6,"column":0},"end":{"line":33,"column":7}}})) != null ? stack1 : "")
    + "\n";
},"4":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "    <h5 class=\"content_vertical_padding\">\n	"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"paymentWordingCapitalized") || (depth0 != null ? lookupProperty(depth0,"paymentWordingCapitalized") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"paymentWordingCapitalized","hash":{},"data":data,"loc":{"start":{"line":8,"column":1},"end":{"line":8,"column":34}}}) : helper))) != null ? stack1 : "")
    + "s effectués à "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"paymentsRecipient") || (depth0 != null ? lookupProperty(depth0,"paymentsRecipient") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"paymentsRecipient","hash":{},"data":data,"loc":{"start":{"line":8,"column":48},"end":{"line":8,"column":73}}}) : helper))) != null ? stack1 : "")
    + " :\n    </h5>\n    <ul>\n"
    + ((stack1 = lookupProperty(helpers,"each").call(alias1,(depth0 != null ? lookupProperty(depth0,"payments") : depth0),{"name":"each","hash":{},"fn":container.program(5, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":11,"column":4},"end":{"line":19,"column":13}}})) != null ? stack1 : "")
    + "    </ul>\n";
},"5":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "	<li>\n		<a href=\"/supplier_payments/"
    + ((stack1 = alias1((depth0 != null ? lookupProperty(depth0,"id") : depth0), depth0)) != null ? stack1 : "")
    + "\">\n			<strong>"
    + ((stack1 = alias1((depth0 != null ? lookupProperty(depth0,"amount") : depth0), depth0)) != null ? stack1 : "")
    + "</strong>\n            le "
    + ((stack1 = alias1((depth0 != null ? lookupProperty(depth0,"date") : depth0), depth0)) != null ? stack1 : "")
    + "\n            <small>("
    + ((stack1 = alias1((depth0 != null ? lookupProperty(depth0,"mode") : depth0), depth0)) != null ? stack1 : "")
    + ((stack1 = lookupProperty(helpers,"if").call(depth0 != null ? depth0 : (container.nullContext || {}),(depth0 != null ? lookupProperty(depth0,"bank_remittance_id") : depth0),{"name":"if","hash":{},"fn":container.program(6, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":16,"column":37},"end":{"line":16,"column":109}}})) != null ? stack1 : "")
    + ")</small>\n		</a>\n	</li>\n";
},"6":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return " : "
    + ((stack1 = container.lambda((depth0 != null ? lookupProperty(depth0,"bank_remittance_id") : depth0), depth0)) != null ? stack1 : "");
},"8":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.lambda, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "    <p>\n        "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"paymentWordingCapitalized") || (depth0 != null ? lookupProperty(depth0,"paymentWordingCapitalized") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"paymentWordingCapitalized","hash":{},"data":data,"loc":{"start":{"line":23,"column":8},"end":{"line":23,"column":41}}}) : helper))) != null ? stack1 : "")
    + " effectué à "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"paymentsRecipient") || (depth0 != null ? lookupProperty(depth0,"paymentsRecipient") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"paymentsRecipient","hash":{},"data":data,"loc":{"start":{"line":23,"column":53},"end":{"line":23,"column":78}}}) : helper))) != null ? stack1 : "")
    + " :\n\n    <a href=\"/supplier_payments/"
    + ((stack1 = alias4(((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"id") : stack1), depth0)) != null ? stack1 : "")
    + "\">\n        <strong>"
    + ((stack1 = alias4(((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"amount") : stack1), depth0)) != null ? stack1 : "")
    + "</strong>\n        le "
    + ((stack1 = alias4(((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"date") : stack1), depth0)) != null ? stack1 : "")
    + " \n        <small>\n            ("
    + ((stack1 = alias4(((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"mode") : stack1), depth0)) != null ? stack1 : "")
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"bank_remittance_id") : stack1),{"name":"if","hash":{},"fn":container.program(9, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":29,"column":36},"end":{"line":29,"column":120}}})) != null ? stack1 : "")
    + ")\n        </small>\n    </a>\n    </p>\n";
},"9":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return " : "
    + ((stack1 = container.lambda(((stack1 = ((stack1 = (depth0 != null ? lookupProperty(depth0,"payments") : depth0)) != null ? lookupProperty(stack1,"0") : stack1)) != null ? lookupProperty(stack1,"bank_remittance_id") : stack1), depth0)) != null ? stack1 : "");
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return ((stack1 = lookupProperty(helpers,"if").call(depth0 != null ? depth0 : (container.nullContext || {}),(depth0 != null ? lookupProperty(depth0,"noPayment") : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(3, data, 0),"data":data,"loc":{"start":{"line":1,"column":0},"end":{"line":35,"column":7}}})) != null ? stack1 : "");
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceFormView.mustache":
/*!*******************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceFormView.mustache ***!
  \*******************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<div class=\"separate_top content_vertical_padding\">\n    <h3>Propriétés de la facture</h3>\n    <form class=\"form\">\n        <div class=\"form-section\">\n            <div class=\"row form-row\">\n                <div class=\"col-md-2\">\n                    <div class='date'></div>\n                </div>\n                <div class=\"col-md-4\">\n                  <div class='supplier_id'></div>\n                </div>\n                <div class=\"col-md-6\">\n                    <div class='remote_invoice_number'></div>\n                </div>\n            </div>\n            <div class=\"row form-row\">\n                <div class=\"col-md-2\">\n                    <div class=\"payer_id\"></div>\n                </div>\n                <div class=\"col-md-4\">\n                    <div class='advance_percent'></div>\n                </div>\n                <div class=\"col-md-6\">\n                    <div class='supplier-orders'></div>\n                </div>\n            </div>\n        </div>\n    </form>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineDuplicateFormView.mustache":
/*!********************************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineDuplicateFormView.mustache ***!
  \********************************************************************************************/
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

  return "<div role=\"dialog\" id=\"supplierinvoiceline-forms\" aria-modal=\"true\" aria-labelledby=\"supplierinvoiceline-forms_title\">\n    <form>\n        <div class=\"modal_layout\">\n            <header>\n                <button tabindex='-1' type=\"button\" class=\"icon only unstyled close\" title=\"Fermer cette fenêtre\" aria-label=\"Fermer cette fenêtre\">\n                    <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n                </button>\n                <h2 id=\"supplierinvoiceline-forms_title\">Dupliquer une ligne de facture fournisseur</h2>\n            </header>\n            <div class=\"modal_content_layout\">\n                <div class=\"modal_content\">\n                    <div class='separate_bottom'>\n                        <h3>Ligne</h3>\n                        "
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":14,"column":24},"end":{"line":14,"column":39}}}) : helper)))
    + "<br />\n                        <div class='expense_totals'>\n                            <div class=\"layout flex two_cols\">\n                                <div>\n                                    <p>HT&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht") || (depth0 != null ? lookupProperty(depth0,"ht") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht","hash":{},"data":data,"loc":{"start":{"line":18,"column":49},"end":{"line":18,"column":59}}}) : helper))) != null ? stack1 : "")
    + "</p>\n                                </div>\n                            </div>\n                            <div class=\"layout flex two_cols\">\n                                <div>\n                                    <p>TVA&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva") || (depth0 != null ? lookupProperty(depth0,"tva") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva","hash":{},"data":data,"loc":{"start":{"line":23,"column":50},"end":{"line":23,"column":61}}}) : helper))) != null ? stack1 : "")
    + "</p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class='select layout'></div>\n                </div>\n                <footer>\n                    <button\n                        class='btn btn-success btn-primary primary-action'\n                        type='submit'\n                        value='submit'>\n                        Dupliquer\n                    </button>\n                    <button\n                        class='btn btn-default secondary-action'\n                        type='reset'\n                        value='submit'>\n                        Annuler\n                    </button>\n                </footer>\n            </div>\n        </div><!-- /.modal_layout -->\n    </form>\n</div><!-- /.supplierinvoiceline-forms -->\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineEmptyView.mustache":
/*!************************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineEmptyView.mustache ***!
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

  return "<td colspan='"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"colspan") || (depth0 != null ? lookupProperty(depth0,"colspan") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"colspan","hash":{},"data":data,"loc":{"start":{"line":1,"column":13},"end":{"line":1,"column":26}}}) : helper)))
    + "'><em>Aucun achat n’a été renseigné</em></td>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineFormPopupView.mustache":
/*!****************************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineFormPopupView.mustache ***!
  \****************************************************************************************/
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

  return "<div role=\"dialog\" id=\"supplierinvoiceline-forms\" aria-modal=\"true\" aria-labelledby=\"supplierinvoiceline-forms_title\">\n    <div class=\"modal_layout\">\n        <header>\n            <button tabindex='-1' type=\"button\" class=\"icon only unstyled close\"\n                    title=\"Fermer cette fenêtre\"\n            >\n                <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n            </button>\n            <h2 id=\"supplierinvoiceline-forms_title\">"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":9,"column":53},"end":{"line":9,"column":64}}}) : helper)))
    + "</h2>\n        </header>\n        <div class=\"form-child\"><!-- replaced by child view --></div>\n    </div>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineFormView.mustache":
/*!***********************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineFormView.mustache ***!
  \***********************************************************************************/
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

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineTableView.mustache":
/*!************************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineTableView.mustache ***!
  \************************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    return "            <div class=\"align_right\">\n				<button class='btn btn-primary add'>\n					<svg><use href=\"/static/icons/icones.svg#plus\"></use></svg>Ajouter un achat\n				</button>\n            </div>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "					<th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n";
},"5":function(container,depth0,helpers,partials,data) {
    return "				        <td class=\"col_actions width_three\">&nbsp;</td>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.hooks.blockHelperMissing, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class=\"content_vertical_padding separate_top\">\n	\n    <div class=\"layout flex two_cols\">\n        <h2>Détail de la facture</h2>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"add") || (depth0 != null ? lookupProperty(depth0,"add") : depth0)) != null ? helper : alias2),(options={"name":"add","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":5,"column":8},"end":{"line":11,"column":10}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"add")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  buffer += "    </div>\n	<div class='group-errors'></div>\n	<div class=\"table_container\">\n		<table class=\"opa hover_table\">\n			<thead>\n				<th scope=\"col\" class=\"col_text\">Type de dépense</th>\n				<th scope=\"col\" class=\"col_text\">Description</th>\n                <th scope=\"col\" class=\"col_text\">Rattaché à…</th>\n                <th scope=\"col\" class=\"col_number\" title=\"Montant Hors Taxes\"><span class=\"screen-reader-text\">Montant </span>H<span class=\"screen-reader-text\">ors </span>T<span class=\"screen-reader-text\">axes</span></th>\n                <th scope=\"col\" class=\"col_number\" title=\"Taux de TVA\"><span class=\"screen-reader-text\">Taux de </span>TVA</th>\n				<th scope=\"col\" class=\"col_number\">Total TTC</th>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"edit") || (depth0 != null ? lookupProperty(depth0,"edit") : depth0)) != null ? helper : alias2),(options={"name":"edit","hash":{},"fn":container.program(3, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":23,"column":4},"end":{"line":25,"column":13}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"edit")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  buffer += "			</thead>\n			<tbody class='lines'>\n			</tbody>\n			<tfoot>\n                <tr class=\"row_recap\">\n				    <th scope='row' class='col_text' colspan=\"3\">Total</th>\n				    <td class='total_ht col_number'></td>\n				    <td class='total_tva col_number'></td>\n				    <td class='total_ttc col_number'></td>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"edit") || (depth0 != null ? lookupProperty(depth0,"edit") : depth0)) != null ? helper : alias2),(options={"name":"edit","hash":{},"fn":container.program(5, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":35,"column":8},"end":{"line":37,"column":17}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"edit")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n                </tr>\n			</tfoot>\n		</table>\n	</div>\n</div>\n";
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/SupplierInvoiceLineView.mustache":
/*!*******************************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/SupplierInvoiceLineView.mustache ***!
  \*******************************************************************************/
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
  "<td class='col_actions'>\n	<ul>\n		<li>\n            <button class='btn icon only edit' title='Modifier' aria-label='Modifier'>\n                <svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n            </button>\n        </li>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"delete") || (depth0 != null ? lookupProperty(depth0,"delete") : depth0)) != null ? helper : alias2),(options={"name":"delete","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":8},"end":{"line":21,"column":19}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"delete")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  stack1 = ((helper = (helper = lookupProperty(helpers,"duplicate") || (depth0 != null ? lookupProperty(depth0,"duplicate") : depth0)) != null ? helper : alias2),(options={"name":"duplicate","hash":{},"fn":container.program(4, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":22,"column":8},"end":{"line":28,"column":22}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"duplicate")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </ul>\n</td>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "		<li>\n            <button class='btn icon only negative delete'>\n                <svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg>\n            </button>\n        </li>\n";
},"4":function(container,depth0,helpers,partials,data) {
    return "		<li>\n            <button class='btn icon only duplicate' title='Dupliquer' aria-label='Dupliquer'>\n                <svg><use href=\"/static/icons/icones.svg#copy\"></use></svg></button>\n            </button>\n        </li>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<td class=\"col_text\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"typelabel") || (depth0 != null ? lookupProperty(depth0,"typelabel") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"typelabel","hash":{},"data":data,"loc":{"start":{"line":1,"column":21},"end":{"line":1,"column":36}}}) : helper)))
    + "</td>\n<td class=\"col_text\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":2,"column":21},"end":{"line":2,"column":38}}}) : helper)))
    + "</td>\n<td class=\"col_text\"><span class=\"business-link\"></span></td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht_label") || (depth0 != null ? lookupProperty(depth0,"ht_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht_label","hash":{},"data":data,"loc":{"start":{"line":4,"column":23},"end":{"line":4,"column":39}}}) : helper))) != null ? stack1 : "")
    + "</td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva_label") || (depth0 != null ? lookupProperty(depth0,"tva_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva_label","hash":{},"data":data,"loc":{"start":{"line":5,"column":23},"end":{"line":5,"column":40}}}) : helper))) != null ? stack1 : "")
    + "</td>\n<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"total") || (depth0 != null ? lookupProperty(depth0,"total") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"total","hash":{},"data":data,"loc":{"start":{"line":6,"column":23},"end":{"line":6,"column":36}}}) : helper))) != null ? stack1 : "")
    + "</td>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"edit") || (depth0 != null ? lookupProperty(depth0,"edit") : depth0)) != null ? helper : alias2),(options={"name":"edit","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":7,"column":0},"end":{"line":31,"column":9}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"edit")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"useData":true});

/***/ }),

/***/ "./src/supplier_invoice/views/templates/TotalView.mustache":
/*!*****************************************************************!*\
  !*** ./src/supplier_invoice/views/templates/TotalView.mustache ***!
  \*****************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var Handlebars = __webpack_require__(/*! ../../../../node_modules/handlebars/runtime.js */ "./node_modules/handlebars/runtime.js");
function __default(obj) { return obj && (obj.__esModule ? obj["default"] : obj); }
module.exports = (Handlebars["default"] || Handlebars).template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "		<h4 class=\"content_vertical_padding\">Part paiement CAE ("
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"cae_percentage") || (depth0 != null ? lookupProperty(depth0,"cae_percentage") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"cae_percentage","hash":{},"data":data,"loc":{"start":{"line":4,"column":58},"end":{"line":4,"column":80}}}) : helper))) != null ? stack1 : "")
    + "%) : "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc_cae") || (depth0 != null ? lookupProperty(depth0,"ttc_cae") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc_cae","hash":{},"data":data,"loc":{"start":{"line":4,"column":85},"end":{"line":4,"column":100}}}) : helper))) != null ? stack1 : "")
    + "</h4>\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"totals_mismatch") : depth0),{"name":"if","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":5,"column":12},"end":{"line":12,"column":19}}})) != null ? stack1 : "");
},"2":function(container,depth0,helpers,partials,data) {
    var stack1, helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "                <div class=\"space_bottom\">\n                    <span class=\"icon caution\">\n                        <svg><use href=\"/static/icons/icones.svg#exclamation-triangle\"></use></svg>\n                    </span>\n                    Validé en commande&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"orders_ttc_cae") || (depth0 != null ? lookupProperty(depth0,"orders_ttc_cae") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"orders_ttc_cae","hash":{},"data":data,"loc":{"start":{"line":10,"column":46},"end":{"line":10,"column":68}}}) : helper))) != null ? stack1 : "")
    + "\n                </div>\n";
},"4":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "   		<h4 class=\"content_vertical_padding\">Part paiement Entrepreneur ("
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"worker_percentage") || (depth0 != null ? lookupProperty(depth0,"worker_percentage") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"worker_percentage","hash":{},"data":data,"loc":{"start":{"line":17,"column":70},"end":{"line":17,"column":95}}}) : helper))) != null ? stack1 : "")
    + "%) : "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc_worker") || (depth0 != null ? lookupProperty(depth0,"ttc_worker") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc_worker","hash":{},"data":data,"loc":{"start":{"line":17,"column":100},"end":{"line":17,"column":118}}}) : helper))) != null ? stack1 : "")
    + "</h4>\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"totals_mismatch") : depth0),{"name":"if","hash":{},"fn":container.program(5, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":18,"column":12},"end":{"line":25,"column":19}}})) != null ? stack1 : "");
},"5":function(container,depth0,helpers,partials,data) {
    var stack1, helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "                    <div class=\"space_bottom\">\n                        <span class=\"icon caution\">\n                            <svg><use href=\"/static/icons/icones.svg#exclamation-triangle\"></use></svg>\n                        </span>\n                        Validé en commande&nbsp;: "
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"orders_ttc_worker") || (depth0 != null ? lookupProperty(depth0,"orders_ttc_worker") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"orders_ttc_worker","hash":{},"data":data,"loc":{"start":{"line":23,"column":50},"end":{"line":23,"column":75}}}) : helper))) != null ? stack1 : "")
    + "\n                    </div>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<div class=\"layout flex\">\n	<div>\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"cae_percentage") : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":3,"column":8},"end":{"line":13,"column":15}}})) != null ? stack1 : "")
    + "        <div class=\"cae-part-region\"></div>\n\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"worker_percentage") : depth0),{"name":"if","hash":{},"fn":container.program(4, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":16,"column":8},"end":{"line":26,"column":15}}})) != null ? stack1 : "")
    + "        <div class=\"worker-part-region\"></div>\n	</div>\n	<div>\n    	<h4 class=\"content_vertical_padding\">Totaux</h4>\n    	<table class=\"top_align_table\">\n    		<tbody>\n    			<tr>\n    				<th scope=\"row\">Total HT</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ht") || (depth0 != null ? lookupProperty(depth0,"ht") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ht","hash":{},"data":data,"loc":{"start":{"line":35,"column":31},"end":{"line":35,"column":41}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    			<tr>\n    				<th scope=\"row\">Total TVA</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"tva") || (depth0 != null ? lookupProperty(depth0,"tva") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"tva","hash":{},"data":data,"loc":{"start":{"line":39,"column":31},"end":{"line":39,"column":42}}}) : helper))) != null ? stack1 : "")
    + "</td>\n    			</tr>\n    			<tr>\n    				<th scope=\"row\">Total TTC</th>\n    				<td class=\"col_number\">"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"ttc") || (depth0 != null ? lookupProperty(depth0,"ttc") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"ttc","hash":{},"data":data,"loc":{"start":{"line":43,"column":31},"end":{"line":43,"column":42}}}) : helper))) != null ? stack1 : "")
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
/******/ 			"supplier_invoice": 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendor"], () => (__webpack_require__("./src/supplier_invoice/supplier_invoice.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	supplier_invoice = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=supplier_invoice.js.map