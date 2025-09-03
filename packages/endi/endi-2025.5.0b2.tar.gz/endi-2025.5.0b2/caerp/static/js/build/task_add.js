/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js":
/*!*******************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js ***!
  \*******************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var vee_validate__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! vee-validate */ "./node_modules/vee-validate/dist/vee-validate.mjs");
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @/helpers/utils */ "./src/helpers/utils.js");



/** A checkbox meant to be used in a multi-selection scenario
 *
 * This checkbox is meant to be used in a multi-checkbox scenario (typically with CheckboxList
 *
 * For standalone boolean checkbox, see BooleanCheckbox
 */

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'Checkbox',
  props: {
    modelValue: {
      type: null
    },
    label: String,
    description: {
      type: String,
      "default": ''
    },
    name: String,
    value: {
      type: [String, Number]
    },
    divCss: {
      type: String,
      "default": 'toggle'
    },
    editable: {
      type: Boolean,
      "default": true
    }
  },
  setup: function setup(__props, _ref) {
    var __expose = _ref.expose;
    __expose();
    var props = __props;
    var tagId = (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_1__.uniqueId)(props.name);

    // we are using toRefs to create reactive references to `name` and `value` props
    // this is important because vee-validate needs to know if any of these props change
    // https://vee-validate.logaretm.com/v4/guide/composition-api/caveats
    var _toRefs = (0,vue__WEBPACK_IMPORTED_MODULE_0__.toRefs)(props),
      name = _toRefs.name,
      value = _toRefs.value;
    var _useField = (0,vee_validate__WEBPACK_IMPORTED_MODULE_2__.useField)(name, undefined, {
        type: 'checkbox',
        checkedValue: value
      }),
      checked = _useField.checked,
      handleChange = _useField.handleChange;
    var __returned__ = {
      props: props,
      tagId: tagId,
      name: name,
      value: value,
      checked: checked,
      handleChange: handleChange,
      toRefs: vue__WEBPACK_IMPORTED_MODULE_0__.toRefs,
      get useField() {
        return vee_validate__WEBPACK_IMPORTED_MODULE_2__.useField;
      },
      get uniqueId() {
        return _helpers_utils__WEBPACK_IMPORTED_MODULE_1__.uniqueId;
      }
    };
    Object.defineProperty(__returned__, '__isScriptSetup', {
      enumerable: false,
      value: true
    });
    return __returned__;
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js":
/*!***********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js ***!
  \***********************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/helpers/utils */ "./src/helpers/utils.js");
/* harmony import */ var _InputLabel_vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./InputLabel.vue */ "./src/components/forms/InputLabel.vue");
/* harmony import */ var _Checkbox_vue__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./Checkbox.vue */ "./src/components/forms/Checkbox.vue");



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'CheckboxList',
  props: {
    name: String,
    label: String,
    modelValue: {
      type: null
    },
    options: {
      type: Array
    },
    description: {
      type: String
    },
    idKey: {
      type: String,
      "default": 'id'
    },
    labelKey: {
      type: String,
      "default": 'label'
    },
    editable: {
      type: Boolean,
      "default": true
    },
    required: {
      type: Boolean,
      "default": false
    }
  },
  setup: function setup(__props, _ref) {
    var __expose = _ref.expose;
    __expose();
    var props = __props;
    var tagId = (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_0__.uniqueId)(props.name);
    var __returned__ = {
      props: props,
      tagId: tagId,
      get uniqueId() {
        return _helpers_utils__WEBPACK_IMPORTED_MODULE_0__.uniqueId;
      },
      InputLabel: _InputLabel_vue__WEBPACK_IMPORTED_MODULE_1__["default"],
      Checkbox: _Checkbox_vue__WEBPACK_IMPORTED_MODULE_2__["default"]
    };
    Object.defineProperty(__returned__, '__isScriptSetup', {
      enumerable: false,
      value: true
    });
    return __returned__;
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js":
/*!************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js ***!
  \************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var vee_validate__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! vee-validate */ "./node_modules/vee-validate/dist/vee-validate.mjs");
/* harmony import */ var _helpers_form__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @/helpers/form */ "./src/helpers/form.js");
/* harmony import */ var _stores_project__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @/stores/project */ "./src/stores/project.js");
/* harmony import */ var _components_DebugContent_vue__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/components/DebugContent.vue */ "./src/components/DebugContent.vue");
/* harmony import */ var _components_forms_Input_vue__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @/components/forms/Input.vue */ "./src/components/forms/Input.vue");
/* harmony import */ var _components_forms_RadioChoice_vue__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @/components/forms/RadioChoice.vue */ "./src/components/forms/RadioChoice.vue");
/* harmony import */ var _components_forms_CheckboxList_vue__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @/components/forms/CheckboxList.vue */ "./src/components/forms/CheckboxList.vue");









/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'ProjectForm',
  props: {
    project: {
      type: Object
    },
    layout: {
      type: Object
    }
  },
  emits: ['saved', 'cancel', 'error'],
  setup: function setup(__props, _ref) {
    var __expose = _ref.expose,
      __emit = _ref.emit;
    __expose();
    var props = __props;
    var emit = __emit;

    // DEBUG est définie globalement par webpack
    var debug = true;
    // Récupération de la configuration du formulaire
    var configStore = (0,_stores_project__WEBPACK_IMPORTED_MODULE_2__.useProjectConfigStore)();
    var projectTypeOptions = configStore.getOptions('project_types');
    var invoicingModeOptions = (0,vue__WEBPACK_IMPORTED_MODULE_0__.ref)(configStore.getOptions('invoicing_modes'));
    var businessTypeOptions = (0,vue__WEBPACK_IMPORTED_MODULE_0__.ref)(configStore.getOptions('business_types'));
    var formConfigSchema = configStore.getSchema('default');

    // Construction du formulaire
    var formSchema = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_1__.buildYupSchema)(formConfigSchema);
    var initialValues = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_1__.getDefaults)(formSchema);
    // Formulaire vee-validate (se met à jour automatiquement en fonction du schéma)
    var _useForm = (0,vee_validate__WEBPACK_IMPORTED_MODULE_7__.useForm)({
        validationSchema: formSchema,
        initialValues: initialValues
      }),
      values = _useForm.values,
      handleSubmit = _useForm.handleSubmit,
      setFieldValue = _useForm.setFieldValue,
      isSubmitting = _useForm.isSubmitting;
    // Construction des callbacks submit/cancel
    var projectStore = (0,_stores_project__WEBPACK_IMPORTED_MODULE_2__.useProjectStore)();
    var onSubmitSuccess = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_1__.getSubmitModelCallback)(emit, projectStore.saveProject);
    var onSubmitError = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_1__.getSubmitErrorCallback)(emit);
    var onSubmit = handleSubmit(onSubmitSuccess, onSubmitError);
    var onCancel = function onCancel() {
      return emit('cancel');
    };

    // Gère le rafraichissement du formulaire en fonctoin du project_type_id
    function onProjectTypeChange() {
      var project_type_id = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      if (project_type_id === null) {
        project_type_id = values.project_type_id;
      }
      if (!project_type_id) {
        return;
      }
      console.log('Changement du type de dossier');
      var projectType = projectTypeOptions.find(function (item) {
        return item.id == parseInt(project_type_id);
      });
      if (projectType.name != 'default') {
        setFieldValue('mode', 'ht');
        invoicingModeOptions.value = [{
          name: 'ht'
        }];
      } else {
        invoicingModeOptions.value = configStore.getOptions('invoicing_modes');
      }
      businessTypeOptions.value = configStore.getOptions('business_types').filter(function (item) {
        return projectType.other_business_type_ids.includes(item.id);
      });
      setFieldValue('business_types', []);
    }
    // On le lance une première fois pour filter les options du formulaire en
    // fonction du type de projet par défaut.
    onProjectTypeChange();

    // Raccourci pour le rendu des champs : renvoie les attributs associés à un champ du formulaire
    var getData = function getData(fieldName) {
      return (0,_helpers_form__WEBPACK_IMPORTED_MODULE_1__.getFieldData)(formSchema, fieldName);
    };
    (0,vue__WEBPACK_IMPORTED_MODULE_0__.watch)(function () {
      return values.project_type_id;
    }, onProjectTypeChange);
    var Layout = props.layout;
    var __returned__ = {
      props: props,
      emit: emit,
      debug: debug,
      configStore: configStore,
      projectTypeOptions: projectTypeOptions,
      invoicingModeOptions: invoicingModeOptions,
      businessTypeOptions: businessTypeOptions,
      formConfigSchema: formConfigSchema,
      formSchema: formSchema,
      initialValues: initialValues,
      values: values,
      handleSubmit: handleSubmit,
      setFieldValue: setFieldValue,
      isSubmitting: isSubmitting,
      projectStore: projectStore,
      onSubmitSuccess: onSubmitSuccess,
      onSubmitError: onSubmitError,
      onSubmit: onSubmit,
      onCancel: onCancel,
      onProjectTypeChange: onProjectTypeChange,
      getData: getData,
      Layout: Layout,
      ref: vue__WEBPACK_IMPORTED_MODULE_0__.ref,
      watch: vue__WEBPACK_IMPORTED_MODULE_0__.watch,
      get useForm() {
        return vee_validate__WEBPACK_IMPORTED_MODULE_7__.useForm;
      },
      get getDefaults() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_1__.getDefaults;
      },
      get buildYupSchema() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_1__.buildYupSchema;
      },
      get getFieldData() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_1__.getFieldData;
      },
      get useProjectConfigStore() {
        return _stores_project__WEBPACK_IMPORTED_MODULE_2__.useProjectConfigStore;
      },
      get useProjectStore() {
        return _stores_project__WEBPACK_IMPORTED_MODULE_2__.useProjectStore;
      },
      DebugContent: _components_DebugContent_vue__WEBPACK_IMPORTED_MODULE_3__["default"],
      Input: _components_forms_Input_vue__WEBPACK_IMPORTED_MODULE_4__["default"],
      RadioChoice: _components_forms_RadioChoice_vue__WEBPACK_IMPORTED_MODULE_5__["default"],
      CheckboxList: _components_forms_CheckboxList_vue__WEBPACK_IMPORTED_MODULE_6__["default"],
      get getSubmitErrorCallback() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_1__.getSubmitErrorCallback;
      },
      get getSubmitModelCallback() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_1__.getSubmitModelCallback;
      }
    };
    Object.defineProperty(__returned__, '__isScriptSetup', {
      enumerable: false,
      value: true
    });
    return __returned__;
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js":
/*!*********************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js ***!
  \*********************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_slicedToArray__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/slicedToArray */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var _babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/helpers/esm/asyncToGenerator */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @babel/runtime/regenerator */ "./node_modules/@babel/runtime/regenerator/index.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var pinia__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! pinia */ "./node_modules/pinia/dist/pinia.mjs");
/* harmony import */ var _layouts_FormFlatLayout_vue__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @/layouts/FormFlatLayout.vue */ "./src/layouts/FormFlatLayout.vue");
/* harmony import */ var _stores_project__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @/stores/project */ "./src/stores/project.js");
/* harmony import */ var _ProjectForm_vue__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./ProjectForm.vue */ "./src/components/project/ProjectForm.vue");










// props attendu par le composant

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'ProjectFormComponent',
  props: {
    edit: {
      type: Boolean,
      "default": false
    },
    projectId: {
      type: Number || null,
      "default": null
    },
    url: {
      type: String,
      required: true
    },
    formConfigUrl: {
      type: String,
      required: true
    },
    layout: {
      type: Object,
      "default": _layouts_FormFlatLayout_vue__WEBPACK_IMPORTED_MODULE_4__["default"]
    }
  },
  emits: ['saved', 'cancel'],
  setup: function setup(__props, _ref) {
    return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().mark(function _callee2() {
      var _withAsyncContext2, _withAsyncContext3;
      var __expose, __emit, __temp, __restore, props, emit, isEdit, loading, formConfigStore, projectStore, preload, _storeToRefs, project, onSaved, onCancel, __returned__, _t, _t2, _t3, _t4, _t5, _t6, _t7, _t8, _t9, _t0, _t1, _t10, _t11;
      return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().wrap(function (_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            onCancel = function _onCancel() {
              console.log('Cancel Project add/edit');
              emit('cancel');
            };
            onSaved = function _onSaved(project) {
              emit('saved', project);
            };
            __expose = _ref.expose, __emit = _ref.emit;
            __expose();
            props = __props;
            emit = __emit;
            isEdit = !!props.projectId;
            loading = (0,vue__WEBPACK_IMPORTED_MODULE_3__.ref)(true);
            formConfigStore = (0,_stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectConfigStore)();
            formConfigStore.setUrl(props.formConfigUrl);
            projectStore = (0,_stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectStore)();
            preload = /*#__PURE__*/function () {
              var _ref2 = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().mark(function _callee() {
                var promises;
                return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().wrap(function (_context) {
                  while (1) switch (_context.prev = _context.next) {
                    case 0:
                      promises = [formConfigStore.loadConfig()];
                      if (isEdit) {
                        projectStore.setCurrentProjectId(props.projectId);
                        promises.push(projectStore.loadProject());
                      }
                      Promise.all(promises).then(function () {
                        return loading.value = false;
                      });
                    case 1:
                    case "end":
                      return _context.stop();
                  }
                }, _callee);
              }));
              return function preload() {
                return _ref2.apply(this, arguments);
              };
            }();
            _storeToRefs = (0,pinia__WEBPACK_IMPORTED_MODULE_7__.storeToRefs)(projectStore), project = _storeToRefs.item;
            ;
            _withAsyncContext2 = (0,vue__WEBPACK_IMPORTED_MODULE_3__.withAsyncContext)(function () {
              return preload();
            }), _withAsyncContext3 = (0,_babel_runtime_helpers_esm_slicedToArray__WEBPACK_IMPORTED_MODULE_0__["default"])(_withAsyncContext2, 2), __temp = _withAsyncContext3[0], __restore = _withAsyncContext3[1];
            _context2.next = 1;
            return __temp;
          case 1:
            __restore();
            _t = props;
            _t2 = emit;
            _t3 = isEdit;
            _t4 = loading;
            _t5 = formConfigStore;
            _t6 = projectStore;
            _t7 = preload;
            _t8 = project;
            _t9 = onSaved;
            _t0 = onCancel;
            _t1 = vue__WEBPACK_IMPORTED_MODULE_3__.ref;
            _t10 = _layouts_FormFlatLayout_vue__WEBPACK_IMPORTED_MODULE_4__["default"];
            _t11 = _ProjectForm_vue__WEBPACK_IMPORTED_MODULE_6__["default"];
            __returned__ = {
              props: _t,
              emit: _t2,
              isEdit: _t3,
              loading: _t4,
              formConfigStore: _t5,
              projectStore: _t6,
              preload: _t7,
              project: _t8,
              onSaved: _t9,
              onCancel: _t0,
              ref: _t1,
              get storeToRefs() {
                return pinia__WEBPACK_IMPORTED_MODULE_7__.storeToRefs;
              },
              FormFlatLayout: _t10,
              get useProjectConfigStore() {
                return _stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectConfigStore;
              },
              get useProjectStore() {
                return _stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectStore;
              },
              ProjectForm: _t11
            };
            Object.defineProperty(__returned__, '__isScriptSetup', {
              enumerable: false,
              value: true
            });
            return _context2.abrupt("return", __returned__);
          case 2:
          case "end":
            return _context2.stop();
        }
      }, _callee2);
    }))();
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=script&setup=true&lang=js":
/*!********************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=script&setup=true&lang=js ***!
  \********************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var _helpers_context_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @/helpers/context.js */ "./src/helpers/context.js");
/* harmony import */ var _components_TaskAddFormComponent_vue__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/TaskAddFormComponent.vue */ "./src/views/task/components/TaskAddFormComponent.vue");
/* harmony import */ var _stores_task__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/stores/task */ "./src/stores/task.js");




/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'App',
  setup: function setup(__props, _ref) {
    var __expose = _ref.expose;
    __expose();
    var options = (0,_helpers_context_js__WEBPACK_IMPORTED_MODULE_1__.collectOptions)();
    var redirectOnsave = function redirectOnsave(task) {
      var typeLabel = task.type_.replace('internal', '');
      window.location.replace('/' + typeLabel + 's/' + task.id);
    };
    var redirectOnCancel = function redirectOnCancel() {
      if (history.length > 1) {
        history.back();
      } else {
        window.location = '/';
      }
    };
    var __returned__ = {
      options: options,
      redirectOnsave: redirectOnsave,
      redirectOnCancel: redirectOnCancel,
      Suspense: vue__WEBPACK_IMPORTED_MODULE_0__.Suspense,
      get collectOptions() {
        return _helpers_context_js__WEBPACK_IMPORTED_MODULE_1__.collectOptions;
      },
      TaskAddFormComponent: _components_TaskAddFormComponent_vue__WEBPACK_IMPORTED_MODULE_2__["default"],
      get useTaskConfigStore() {
        return _stores_task__WEBPACK_IMPORTED_MODULE_3__.useTaskConfigStore;
      }
    };
    Object.defineProperty(__returned__, '__isScriptSetup', {
      enumerable: false,
      value: true
    });
    return __returned__;
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js":
/*!***************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js ***!
  \***************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/asyncToGenerator */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/regenerator */ "./node_modules/@babel/runtime/regenerator/index.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var vee_validate__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! vee-validate */ "./node_modules/vee-validate/dist/vee-validate.mjs");
/* harmony import */ var _helpers_form__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/helpers/form */ "./src/helpers/form.js");
/* harmony import */ var _stores_customer__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @/stores/customer */ "./src/stores/customer.js");
/* harmony import */ var _stores_project__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @/stores/project */ "./src/stores/project.js");
/* harmony import */ var _stores_task__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @/stores/task */ "./src/stores/task.js");
/* harmony import */ var _components_forms_Select2_vue__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @/components/forms/Select2.vue */ "./src/components/forms/Select2.vue");
/* harmony import */ var _components_forms_Input_vue__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @/components/forms/Input.vue */ "./src/components/forms/Input.vue");
/* harmony import */ var _components_Icon_vue__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @/components/Icon.vue */ "./src/components/Icon.vue");
/* harmony import */ var _layouts_FormModalLayout_vue__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @/layouts/FormModalLayout.vue */ "./src/layouts/FormModalLayout.vue");
/* harmony import */ var _components_customer_CustomerFormComponent_vue__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @/components/customer/CustomerFormComponent.vue */ "./src/components/customer/CustomerFormComponent.vue");
/* harmony import */ var _components_project_ProjectFormComponent_vue__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @/components/project/ProjectFormComponent.vue */ "./src/components/project/ProjectFormComponent.vue");















/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'TaskAddForm',
  props: {
    initialData: Object
  },
  emits: ['saved', 'cancel', 'error'],
  setup: function setup(__props, _ref) {
    var __expose = _ref.expose,
      __emit = _ref.emit;
    __expose();
    var props = __props;
    var emit = __emit;

    // La création se fait depuis un projet (ou depuis un client)
    var isFromProject = !!props.initialData.project_id;

    // Chargement de la configuration de la page
    var formConfigStore = (0,_stores_task__WEBPACK_IMPORTED_MODULE_6__.useTaskConfigStore)();
    // Urls utilisées pour
    //  - le chargement des clients
    //  - le lancement du formulaire d'ajout de client à la volée
    var customerUrl = formConfigStore.getOptions('customers_url');
    var customerConfigUrl = formConfigStore.getOptions('customers_config_url');
    var projectUrl = formConfigStore.getOptions('projects_url');
    var projectConfigUrl = formConfigStore.getOptions('projects_config_url');

    // Chargement des options des selects
    var customerStore = (0,_stores_customer__WEBPACK_IMPORTED_MODULE_4__.useCustomerStore)();
    var projectStore = (0,_stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectStore)();
    var taskStore = (0,_stores_task__WEBPACK_IMPORTED_MODULE_6__.useTaskStore)();
    function loadProjectOptions() {
      return _loadProjectOptions.apply(this, arguments);
    }
    function _loadProjectOptions() {
      _loadProjectOptions = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee4() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context4) {
          while (1) switch (_context4.prev = _context4.next) {
            case 0:
              _context4.next = 1;
              return projectStore.loadProjects(props.initialData.company_id, {
                fields: ['id', 'name'],
                related: ['customer_ids', 'phases', 'business_types']
              });
            case 1:
              return _context4.abrupt("return", _context4.sent);
            case 2:
            case "end":
              return _context4.stop();
          }
        }, _callee4);
      }));
      return _loadProjectOptions.apply(this, arguments);
    }
    function loadCustomerOptions() {
      return _loadCustomerOptions.apply(this, arguments);
    }
    function _loadCustomerOptions() {
      _loadCustomerOptions = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee5() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context5) {
          while (1) switch (_context5.prev = _context5.next) {
            case 0:
              _context5.next = 1;
              return customerStore.loadCustomers(props.initialData.company_id, {
                fields: ['id', 'label'],
                related: ['project_ids']
              });
            case 1:
              return _context5.abrupt("return", _context5.sent);
            case 2:
            case "end":
              return _context5.stop();
          }
        }, _callee5);
      }));
      return _loadCustomerOptions.apply(this, arguments);
    }
    var customersCollection = (0,vue__WEBPACK_IMPORTED_MODULE_2__.ref)([]);
    var projectsCollection = (0,vue__WEBPACK_IMPORTED_MODULE_2__.ref)([]);
    (0,vue__WEBPACK_IMPORTED_MODULE_2__.onMounted)(/*#__PURE__*/(0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee() {
      return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            _context.next = 1;
            return loadCustomerOptions();
          case 1:
            customersCollection.value = _context.sent;
            _context.next = 2;
            return loadProjectOptions();
          case 2:
            projectsCollection.value = _context.sent;
          case 3:
          case "end":
            return _context.stop();
        }
      }, _callee);
    })));

    // Configuration du schéma de formulaire et du Form vee-validate
    var jsonSchema = formConfigStore.getSchema('default');
    var formSchema = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_3__.buildYupSchema)(jsonSchema);
    var initialValues = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_3__.getDefaults)(formSchema);
    var _useForm = (0,vee_validate__WEBPACK_IMPORTED_MODULE_13__.useForm)({
        validationSchema: formSchema,
        initialValues: initialValues
      }),
      values = _useForm.values,
      handleSubmit = _useForm.handleSubmit,
      setFieldValue = _useForm.setFieldValue,
      isSubmitting = _useForm.isSubmitting;
    // **** Update des selects
    // update les options en fonction du projet ou du client sélectionné
    // helpers renvoyant les options
    /**
     * Fonction filtrant les dossiers à proposer
     */
    var projects = function projects() {
      // Getting the raw list in place of the ref's proxy value
      var _projects = (0,vue__WEBPACK_IMPORTED_MODULE_2__.toRaw)(projectsCollection.value);
      var result;
      if (isFromProject) {
        result = _projects;
      } else {
        var customer_id = parseInt(values.customer_id);
        if (!customer_id) {
          result = [];
        } else if (newCustomerId === customer_id) {
          // On vient d'ajouter ce client, on propose tous les projets.
          result = _projects;
        } else {
          var customerProjects = _projects.filter(function (project) {
            return project.customer_ids.includes(customer_id);
          });
          if (customerProjects.length === 0) {
            result = _projects;
          } else {
            var otherProjects = _projects.filter(function (project) {
              return !project.customer_ids.includes(customer_id);
            });
            result = [{
              text: 'Dossiers du client',
              children: customerProjects
            }];
            if (otherProjects.length > 0) {
              result.push({
                text: 'Autres dossiers',
                children: otherProjects
              });
            }
          }
        }
      }
      return result;
    };
    /**
     * Fonction filtrant les clients à proposer
     */
    var customers = function customers() {
      console.log('computing customers');
      var _customers = (0,vue__WEBPACK_IMPORTED_MODULE_2__.toRaw)(customersCollection.value);
      var result;
      if (!isFromProject) {
        result = _customers;
      } else {
        var project_id = parseInt(values.project_id);
        if (project_id) {
          var projectCustomers = _customers.filter(function (customer) {
            return customer.project_ids.includes(project_id);
          });
          if (projectCustomers.length === 0) {
            result = _customers;
          } else {
            var otherCustomers = _customers.filter(function (customer) {
              return !customer.project_ids.includes(project_id);
            });
            result = [{
              text: 'Clients du projet',
              children: projectCustomers
            }];
            if (otherCustomers.length > 0) {
              result.push({
                text: 'Autres clients',
                children: otherCustomers
              });
            }
          }
        } else {
          result = [];
        }
      }
      return result;
    };
    /**
     * Fonction filtrant les sous-dossiers à proposer
     */
    var phases = function phases() {
      console.log('computing phases');
      var result = [];
      if (values.project_id) {
        var project = projectStore.getByid(values.project_id);
        if (project) {
          result = project.phases;
        }
      }
      return result;
    };
    /**
     * Fonction filtrant les types d'affaire à proposer
     */
    var businessTypes = function businessTypes() {
      console.log('computing business types');
      var result = [];
      if (values.project_id) {
        var project = projectStore.getByid(values.project_id);
        if (project) {
          result = project.business_types;
        }
      }
      return result;
    };
    // Computed pour que les select s'updatent automatiquement
    var phaseOptions = (0,vue__WEBPACK_IMPORTED_MODULE_2__.computed)(function () {
      return phases();
    });
    var businessTypeOptions = (0,vue__WEBPACK_IMPORTED_MODULE_2__.computed)(function () {
      return businessTypes();
    });
    var customerOptions = (0,vue__WEBPACK_IMPORTED_MODULE_2__.computed)(function () {
      return customers();
    });
    var projectOptions = (0,vue__WEBPACK_IMPORTED_MODULE_2__.computed)(function () {
      return projects();
    });

    // Ref permettant de checker si l'on a juste ajouté un client
    //(dans ce cas on liste tous les projets)
    var newCustomerId = null;
    // Ref permettant de marquer que l'on va associer un projet à un client
    // lors de la validation
    var clientAlreadyInProject = (0,vue__WEBPACK_IMPORTED_MODULE_2__.ref)(true);

    /**
     *  Watcher pour updater les références quand le dossier change
     */
    (0,vue__WEBPACK_IMPORTED_MODULE_2__.watch)(function () {
      return values.project_id;
    }, function (newValue, prevValue) {
      console.log("project_id changed from ".concat(prevValue, " to ").concat(newValue));
      if (!newValue) {
        return;
      }
      var project = projectStore.getByid(newValue);
      // Client
      if (isFromProject) {
        if (project.customer_ids && project.customer_ids.length == 1) {
          setFieldValue('customer_id', project.customer_ids[0]);
        }
      }
      // Sous-dossier
      if (project.phases && project.phases.length == 1) {
        setFieldValue('phase_id', project.phases[0].id);
      }
      // Type d'affaire
      if (project.default_business_type_id) {
        setFieldValue('business_type_id', project.default_business_type_id);
      } else if (project.business_types && project.business_types.length == 1) {
        setFieldValue('business_type_id', project.business_types[0].id);
      }
    });
    /**
     * Watcher pour updater les références quand le client change
     */
    (0,vue__WEBPACK_IMPORTED_MODULE_2__.watch)(function () {
      return values.customer_id;
    }, function (newValue, prevValue) {
      console.log("customer_id changed from ".concat(prevValue, " to ").concat(newValue));
      if (!newValue) {
        return;
      }
      var customer = customerStore.getByid(newValue);
      if (!isFromProject) {
        if (customer.project_ids && customer.project_ids.length == 1) {
          clientAlreadyInProject.value = true;
          setFieldValue('project_id', customer.project_ids[0]);
        } else if (customer.project_ids && customer.project_ids.length === 0) {
          clientAlreadyInProject.value = false;
          values.project_id = null;
        } else {
          clientAlreadyInProject.value = true;
          values.project_id = null;
        }
      }
    });
    /**
     * Fonction permettant d'ajouter un client à un dossier existant
     */
    function addCustomerToProject(_x, _x2) {
      return _addCustomerToProject.apply(this, arguments);
    } // Affichage des popups pour la création de projet / client
    function _addCustomerToProject() {
      _addCustomerToProject = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee6(project, customerId) {
        var customerIds, payload;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context6) {
          while (1) switch (_context6.prev = _context6.next) {
            case 0:
              if (!customerId) {
                _context6.next = 2;
                break;
              }
              projectStore.setCurrentProjectId(project.id);
              customerIds = [customerId];
              if (project.customer_ids) {
                customerIds = customerIds.concat(project.customer_ids);
              }
              payload = {
                id: project.id,
                customers: customerIds
              };
              _context6.next = 1;
              return projectStore.saveProject(payload);
            case 1:
              return _context6.abrupt("return", _context6.sent);
            case 2:
            case "end":
              return _context6.stop();
          }
        }, _callee6);
      }));
      return _addCustomerToProject.apply(this, arguments);
    }
    var showCustomerForm = (0,vue__WEBPACK_IMPORTED_MODULE_2__.ref)(false);
    var showProjectForm = (0,vue__WEBPACK_IMPORTED_MODULE_2__.ref)(false);
    var onCustomerAddClick = function onCustomerAddClick() {
      showCustomerForm.value = true;
    };
    var onHideCustomerForm = function onHideCustomerForm() {
      showCustomerForm.value = false;
    };
    var onProjectAddClick = function onProjectAddClick() {
      showProjectForm.value = true;
    };
    var onHideProjectForm = function onHideProjectForm() {
      showProjectForm.value = false;
    };

    /**
     * Callback après la création d'un nouveau client
     */
    var onCustomerSaved = /*#__PURE__*/function () {
      var _ref3 = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee2(customer) {
        var project_id, selectedProject;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context2) {
          while (1) switch (_context2.prev = _context2.next) {
            case 0:
              newCustomerId = customer.id;
              if (!isFromProject) {
                _context2.next = 2;
                break;
              }
              project_id = values.project_id;
              if (!project_id) {
                _context2.next = 1;
                break;
              }
              // On ajoute le client au projet déjà sélectionné
              selectedProject = projectStore.getByid(project_id);
              _context2.next = 1;
              return addCustomerToProject(selectedProject, customer.id);
            case 1:
              _context2.next = 3;
              break;
            case 2:
              delete values.project_id;
            case 3:
              showCustomerForm.value = false;
              _context2.next = 4;
              return loadCustomerOptions();
            case 4:
              customersCollection.value = _context2.sent;
              customerOptions.value = customers();
              // Hack pour ajouter le customer id dans le validateur du schéma de formulaire
              formSchema.fields.customer_id._whitelist.add(customer.id);
              setFieldValue('customer_id', customer.id);
            case 5:
            case "end":
              return _context2.stop();
          }
        }, _callee2);
      }));
      return function onCustomerSaved(_x3) {
        return _ref3.apply(this, arguments);
      };
    }();

    /**
     * Callback après la création de un nouveau dossier
     */
    var onProjectSaved = /*#__PURE__*/function () {
      var _ref4 = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee3(project) {
        var customerId;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context3) {
          while (1) switch (_context3.prev = _context3.next) {
            case 0:
              if (isFromProject) {
                _context3.next = 3;
                break;
              }
              customerId = values.customer_id;
              if (!customerId) {
                _context3.next = 2;
                break;
              }
              _context3.next = 1;
              return addCustomerToProject(project, customerId);
            case 1:
              newCustomerId = null;
            case 2:
              _context3.next = 4;
              break;
            case 3:
              delete values.customer_id;
            case 4:
              showProjectForm.value = false;
              _context3.next = 5;
              return loadProjectOptions();
            case 5:
              projectsCollection.value = _context3.sent;
              // Hack pour ajouter le project id dans le validateur du schéma de formulaire
              formSchema.fields.project_id._whitelist.add(project.id);
              setFieldValue('project_id', project.id);
            case 6:
            case "end":
              return _context3.stop();
          }
        }, _callee3);
      }));
      return function onProjectSaved(_x4) {
        return _ref4.apply(this, arguments);
      };
    }();

    // Props utilisées pour générer les champs
    // On utilise des variables intermédiaire pour
    // les mettre dans le bon ordre (dossier en premier ou client en premier)
    // ce que l'on ne peut pas faire dans le template
    var customerFieldProps = (0,vue__WEBPACK_IMPORTED_MODULE_2__.reactive)({
      fieldName: 'customer_id',
      labelKey: 'label',
      options: customerOptions,
      onAdd: onCustomerAddClick,
      title: 'Ajouter un client'
    });
    var projectFieldProps = (0,vue__WEBPACK_IMPORTED_MODULE_2__.reactive)({
      fieldName: 'project_id',
      labelKey: 'name',
      options: projectOptions,
      onAdd: onProjectAddClick,
      title: 'Ajouter un dossier'
    });
    var firstFieldProps, secondFieldProps;
    if (isFromProject) {
      // Projet en premier
      ;
      secondFieldProps = customerFieldProps;
      firstFieldProps = projectFieldProps;
    } else {
      // Client en premier
      ;
      firstFieldProps = customerFieldProps;
      secondFieldProps = projectFieldProps;
    }

    /**
     * Fonction lancée lorsque la validation des données par vee-validate
     * est réussie/en erreur
     */
    var onSubmitSuccess = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_3__.getSubmitModelCallback)(emit, taskStore.createTask);
    var onSubmitError = (0,_helpers_form__WEBPACK_IMPORTED_MODULE_3__.getSubmitErrorCallback)(emit);
    var onSubmit = handleSubmit(onSubmitSuccess, onSubmitError);
    var getData = function getData(fieldName) {
      return (0,_helpers_form__WEBPACK_IMPORTED_MODULE_3__.getFieldData)(formSchema, fieldName);
    };
    var __returned__ = {
      props: props,
      emit: emit,
      isFromProject: isFromProject,
      formConfigStore: formConfigStore,
      customerUrl: customerUrl,
      customerConfigUrl: customerConfigUrl,
      projectUrl: projectUrl,
      projectConfigUrl: projectConfigUrl,
      customerStore: customerStore,
      projectStore: projectStore,
      taskStore: taskStore,
      loadProjectOptions: loadProjectOptions,
      loadCustomerOptions: loadCustomerOptions,
      get customersCollection() {
        return customersCollection;
      },
      set customersCollection(v) {
        customersCollection = v;
      },
      get projectsCollection() {
        return projectsCollection;
      },
      set projectsCollection(v) {
        projectsCollection = v;
      },
      jsonSchema: jsonSchema,
      formSchema: formSchema,
      initialValues: initialValues,
      values: values,
      handleSubmit: handleSubmit,
      setFieldValue: setFieldValue,
      isSubmitting: isSubmitting,
      projects: projects,
      customers: customers,
      phases: phases,
      businessTypes: businessTypes,
      get phaseOptions() {
        return phaseOptions;
      },
      set phaseOptions(v) {
        phaseOptions = v;
      },
      get businessTypeOptions() {
        return businessTypeOptions;
      },
      set businessTypeOptions(v) {
        businessTypeOptions = v;
      },
      get customerOptions() {
        return customerOptions;
      },
      set customerOptions(v) {
        customerOptions = v;
      },
      get projectOptions() {
        return projectOptions;
      },
      set projectOptions(v) {
        projectOptions = v;
      },
      get newCustomerId() {
        return newCustomerId;
      },
      set newCustomerId(v) {
        newCustomerId = v;
      },
      get clientAlreadyInProject() {
        return clientAlreadyInProject;
      },
      set clientAlreadyInProject(v) {
        clientAlreadyInProject = v;
      },
      addCustomerToProject: addCustomerToProject,
      showCustomerForm: showCustomerForm,
      showProjectForm: showProjectForm,
      onCustomerAddClick: onCustomerAddClick,
      onHideCustomerForm: onHideCustomerForm,
      onProjectAddClick: onProjectAddClick,
      onHideProjectForm: onHideProjectForm,
      onCustomerSaved: onCustomerSaved,
      onProjectSaved: onProjectSaved,
      customerFieldProps: customerFieldProps,
      projectFieldProps: projectFieldProps,
      get firstFieldProps() {
        return firstFieldProps;
      },
      set firstFieldProps(v) {
        firstFieldProps = v;
      },
      get secondFieldProps() {
        return secondFieldProps;
      },
      set secondFieldProps(v) {
        secondFieldProps = v;
      },
      onSubmitSuccess: onSubmitSuccess,
      onSubmitError: onSubmitError,
      onSubmit: onSubmit,
      getData: getData,
      ref: vue__WEBPACK_IMPORTED_MODULE_2__.ref,
      watch: vue__WEBPACK_IMPORTED_MODULE_2__.watch,
      reactive: vue__WEBPACK_IMPORTED_MODULE_2__.reactive,
      computed: vue__WEBPACK_IMPORTED_MODULE_2__.computed,
      onMounted: vue__WEBPACK_IMPORTED_MODULE_2__.onMounted,
      toRaw: vue__WEBPACK_IMPORTED_MODULE_2__.toRaw,
      get useForm() {
        return vee_validate__WEBPACK_IMPORTED_MODULE_13__.useForm;
      },
      get buildYupSchema() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_3__.buildYupSchema;
      },
      get getFieldData() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_3__.getFieldData;
      },
      get getDefaults() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_3__.getDefaults;
      },
      get getSubmitErrorCallback() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_3__.getSubmitErrorCallback;
      },
      get getSubmitModelCallback() {
        return _helpers_form__WEBPACK_IMPORTED_MODULE_3__.getSubmitModelCallback;
      },
      get useCustomerStore() {
        return _stores_customer__WEBPACK_IMPORTED_MODULE_4__.useCustomerStore;
      },
      get useProjectStore() {
        return _stores_project__WEBPACK_IMPORTED_MODULE_5__.useProjectStore;
      },
      get useTaskConfigStore() {
        return _stores_task__WEBPACK_IMPORTED_MODULE_6__.useTaskConfigStore;
      },
      Select2: _components_forms_Select2_vue__WEBPACK_IMPORTED_MODULE_7__["default"],
      Input: _components_forms_Input_vue__WEBPACK_IMPORTED_MODULE_8__["default"],
      Icon: _components_Icon_vue__WEBPACK_IMPORTED_MODULE_9__["default"],
      FormModalLayout: _layouts_FormModalLayout_vue__WEBPACK_IMPORTED_MODULE_10__["default"],
      CustomerFormComponent: _components_customer_CustomerFormComponent_vue__WEBPACK_IMPORTED_MODULE_11__["default"],
      ProjectFormComponent: _components_project_ProjectFormComponent_vue__WEBPACK_IMPORTED_MODULE_12__["default"],
      get useTaskStore() {
        return _stores_task__WEBPACK_IMPORTED_MODULE_6__.useTaskStore;
      }
    };
    Object.defineProperty(__returned__, '__isScriptSetup', {
      enumerable: false,
      value: true
    });
    return __returned__;
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js":
/*!************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js ***!
  \************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_slicedToArray__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/slicedToArray */ "./node_modules/@babel/runtime/helpers/esm/slicedToArray.js");
/* harmony import */ var _babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/helpers/esm/asyncToGenerator */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @babel/runtime/regenerator */ "./node_modules/@babel/runtime/regenerator/index.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");
/* harmony import */ var _TaskAddForm_vue__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./TaskAddForm.vue */ "./src/views/task/components/TaskAddForm.vue");
/* harmony import */ var _stores_task__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @/stores/task */ "./src/stores/task.js");







/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
  __name: 'TaskAddFormComponent',
  props: {
    initialData: Object,
    url: String,
    formConfigUrl: String
  },
  emits: ['save', 'cancel'],
  setup: function setup(__props, _ref) {
    return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().mark(function _callee2() {
      var _withAsyncContext2, _withAsyncContext3;
      var __expose, __emit, __temp, __restore, props, emit, formConfigStore, loading, preload, taskStore, onSaved, onCancel, __returned__, _t, _t2, _t3, _t4, _t5, _t6, _t7, _t8, _t9, _t0;
      return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().wrap(function (_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            __expose = _ref.expose, __emit = _ref.emit;
            __expose();
            props = __props;
            emit = __emit;
            formConfigStore = (0,_stores_task__WEBPACK_IMPORTED_MODULE_5__.useTaskConfigStore)();
            formConfigStore.setUrl(props.formConfigUrl);
            loading = (0,vue__WEBPACK_IMPORTED_MODULE_3__.ref)(true);
            preload = /*#__PURE__*/function () {
              var _ref2 = (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_1__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().mark(function _callee() {
                var request;
                return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_2___default().wrap(function (_context) {
                  while (1) switch (_context.prev = _context.next) {
                    case 0:
                      request = formConfigStore.loadConfig();
                      request.then(function (config) {
                        loading.value = false;
                      });
                    case 1:
                    case "end":
                      return _context.stop();
                  }
                }, _callee);
              }));
              return function preload() {
                return _ref2.apply(this, arguments);
              };
            }();
            taskStore = (0,_stores_task__WEBPACK_IMPORTED_MODULE_5__.useTaskStore)();
            taskStore.setAddUrl(props.url);
            onSaved = function onSaved(task) {
              return emit('save', task);
            };
            onCancel = function onCancel() {
              return emit('cancel');
            };
            _withAsyncContext2 = (0,vue__WEBPACK_IMPORTED_MODULE_3__.withAsyncContext)(function () {
              return preload();
            }), _withAsyncContext3 = (0,_babel_runtime_helpers_esm_slicedToArray__WEBPACK_IMPORTED_MODULE_0__["default"])(_withAsyncContext2, 2), __temp = _withAsyncContext3[0], __restore = _withAsyncContext3[1];
            _context2.next = 1;
            return __temp;
          case 1:
            __restore();
            _t = props;
            _t2 = emit;
            _t3 = formConfigStore;
            _t4 = loading;
            _t5 = preload;
            _t6 = taskStore;
            _t7 = onSaved;
            _t8 = onCancel;
            _t9 = vue__WEBPACK_IMPORTED_MODULE_3__.ref;
            _t0 = _TaskAddForm_vue__WEBPACK_IMPORTED_MODULE_4__["default"];
            __returned__ = {
              props: _t,
              emit: _t2,
              formConfigStore: _t3,
              loading: _t4,
              preload: _t5,
              taskStore: _t6,
              onSaved: _t7,
              onCancel: _t8,
              ref: _t9,
              TaskAddForm: _t0,
              get useTaskConfigStore() {
                return _stores_task__WEBPACK_IMPORTED_MODULE_5__.useTaskConfigStore;
              },
              get useTaskStore() {
                return _stores_task__WEBPACK_IMPORTED_MODULE_5__.useTaskStore;
              }
            };
            Object.defineProperty(__returned__, '__isScriptSetup', {
              enumerable: false,
              value: true
            });
            return _context2.abrupt("return", __returned__);
          case 2:
          case "end":
            return _context2.stop();
        }
      }, _callee2);
    }))();
  }
});

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a":
/*!************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a ***!
  \************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  "class": "form-group"
};
var _hoisted_2 = ["for"];
var _hoisted_3 = ["id", "checked", "value", "name", "disabled"];
var _hoisted_4 = ["innerHTML"];
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", {
    "class": (0,vue__WEBPACK_IMPORTED_MODULE_0__.normalizeClass)($props.divCss)
  }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("label", {
    "for": $setup.tagId
  }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("input", {
    id: $setup.tagId,
    type: "checkbox",
    checked: $setup.checked,
    value: $setup.value,
    name: $setup.name,
    disabled: !$props.editable,
    onChange: _cache[0] || (_cache[0] = function () {
      return $setup.handleChange && $setup.handleChange.apply($setup, arguments);
    })
  }, null, 40 /* PROPS, NEED_HYDRATION */, _hoisted_3), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("span", null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)($props.label), 1 /* TEXT */)], 8 /* PROPS */, _hoisted_2)], 2 /* CLASS */), $props.description ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", {
    key: 0,
    "class": "help-block",
    innerHTML: $props.description
  }, null, 8 /* PROPS */, _hoisted_4)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true)]);
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade":
/*!****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade ***!
  \****************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  "class": "form-group String"
};
var _hoisted_2 = ["innerHTML"];
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["InputLabel"], {
    label: $props.label,
    required: $props.required,
    "tag-id": $setup.tagId
  }, null, 8 /* PROPS */, ["label", "required", "tag-id"]), ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.options, function (option, index) {
    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Checkbox"], {
      key: $props.name + '-' + index,
      label: option[$props.labelKey],
      name: $props.name,
      value: option[$props.idKey],
      editable: $props.editable,
      "div-css": "checkbox"
    }, null, 8 /* PROPS */, ["label", "name", "value", "editable"]);
  }), 128 /* KEYED_FRAGMENT */)), $props.description ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", {
    key: 0,
    "class": "help-block",
    innerHTML: $props.description
  }, null, 8 /* PROPS */, _hoisted_2)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true)]);
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2":
/*!*****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2 ***!
  \*****************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  "class": "deformFormFieldset"
};
var _hoisted_2 = {
  "class": "row form-row"
};
var _hoisted_3 = {
  "class": "col-md-12"
};
var _hoisted_4 = {
  "class": "row form-row"
};
var _hoisted_5 = {
  "class": "col-md-12"
};
var _hoisted_6 = {
  "class": "row form-row"
};
var _hoisted_7 = {
  "class": "col-md-12"
};
var _hoisted_8 = {
  "class": "row form-row"
};
var _hoisted_9 = {
  "class": "col-md-12"
};
var _hoisted_10 = ["disabled"];
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Layout"], {
    onSubmitForm: $setup.onSubmit,
    onClose: $setup.onCancel
  }, {
    title: (0,vue__WEBPACK_IMPORTED_MODULE_0__.withCtx)(function () {
      return [$props.project.id ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, {
        key: 0
      }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createTextVNode)("Modifier un dossier")], 64 /* STABLE_FRAGMENT */)) : ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, {
        key: 1
      }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createTextVNode)("Ajouter un dossier")], 64 /* STABLE_FRAGMENT */))];
    }),
    fields: (0,vue__WEBPACK_IMPORTED_MODULE_0__.withCtx)(function () {
      return [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("fieldset", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.normalizeProps)((0,vue__WEBPACK_IMPORTED_MODULE_0__.guardReactiveProps)($setup.getData('name'))), null, 16 /* FULL_PROPS */)])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_4, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_5, [$setup.projectTypeOptions.length > 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["RadioChoice"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
        key: 0
      }, $setup.getData('project_type_id'), {
        options: $setup.projectTypeOptions
      }), null, 16 /* FULL_PROPS */, ["options"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
        type: "hidden"
      }, $setup.getData('project_type_id')), null, 16 /* FULL_PROPS */)])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_6, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_7, [$setup.invoicingModeOptions.length > 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["RadioChoice"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
        key: 0
      }, $setup.getData('mode'), {
        options: $setup.invoicingModeOptions,
        inline: "",
        idKey: "value"
      }), null, 16 /* FULL_PROPS */, ["options"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)($setup.getData('mode'), {
        type: "hidden"
      }), null, 16 /* FULL_PROPS */)])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_8, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_9, [$setup.businessTypeOptions.length > 0 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["CheckboxList"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
        key: 0,
        options: $setup.businessTypeOptions
      }, $setup.getData('business_types'), {
        name: "business_types"
      }), null, 16 /* FULL_PROPS */, ["options"])) : ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
        key: 1
      }, $setup.getData('business_types'), {
        type: "hidden"
      }), null, 16 /* FULL_PROPS */))])])])];
    }),
    buttons: (0,vue__WEBPACK_IMPORTED_MODULE_0__.withCtx)(function () {
      return [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
        id: "deformsubmit",
        name: "submit",
        type: "submit",
        "class": "btn btn-primary",
        value: "submit",
        disabled: $setup.isSubmitting
      }, " Valider ", 8 /* PROPS */, _hoisted_10), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
        id: "deformcancel",
        name: "cancel",
        type: "button",
        "class": "btn btn-default",
        onClick: $setup.onCancel
      }, " Annuler "), $setup.debug ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["DebugContent"], {
        key: 0,
        debug: $setup.values
      }, null, 8 /* PROPS */, ["debug"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true)];
    }),
    _: 1 /* STABLE */
  }, 8 /* PROPS */, ["onSubmitForm"]);
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734":
/*!**************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734 ***!
  \**************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  key: 0
};
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return $setup.loading ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", _hoisted_1, "Chargement des informations")) : ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["ProjectForm"], {
    key: 1,
    project: $setup.project,
    layout: $props.layout,
    onSaved: $setup.onSaved,
    onCancel: $setup.onCancel
  }, null, 8 /* PROPS */, ["project", "layout"]));
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=template&id=0d237511":
/*!*************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=template&id=0d237511 ***!
  \*************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_toConsumableArray__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/toConsumableArray */ "./node_modules/@babel/runtime/helpers/esm/toConsumableArray.js");
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");


var _hoisted_1 = {
  "class": "limited_width width30"
};
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (0,vue__WEBPACK_IMPORTED_MODULE_1__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_1__.createBlock)(vue__WEBPACK_IMPORTED_MODULE_1__.Suspense, null, {
    fallback: (0,vue__WEBPACK_IMPORTED_MODULE_1__.withCtx)(function () {
      return (0,_babel_runtime_helpers_esm_toConsumableArray__WEBPACK_IMPORTED_MODULE_0__["default"])(_cache[0] || (_cache[0] = [(0,vue__WEBPACK_IMPORTED_MODULE_1__.createTextVNode)(" Loading... ", -1 /* CACHED */)]));
    }),
    "default": (0,vue__WEBPACK_IMPORTED_MODULE_1__.withCtx)(function () {
      return [(0,vue__WEBPACK_IMPORTED_MODULE_1__.createElementVNode)("div", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_1__.createVNode)($setup["TaskAddFormComponent"], {
        initialData: $setup.options.initial_data,
        url: $setup.options.api_url,
        formConfigUrl: $setup.options.form_config_url,
        onSaved: $setup.redirectOnsave,
        onCancel: $setup.redirectOnCancel
      }, null, 8 /* PROPS */, ["initialData", "url", "formConfigUrl"])])];
    }),
    _: 1 /* STABLE */
  });
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547":
/*!********************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547 ***!
  \********************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  "class": "deformFormFieldset"
};
var _hoisted_2 = {
  "class": "layout flex end_button"
};
var _hoisted_3 = {
  "class": "col-content"
};
var _hoisted_4 = {
  "class": "col-button"
};
var _hoisted_5 = ["title", "aria-label"];
var _hoisted_6 = {
  "class": "form-group layout flex end_button"
};
var _hoisted_7 = {
  "class": "col-content"
};
var _hoisted_8 = {
  "class": "col-button"
};
var _hoisted_9 = ["title", "aria-label"];
var _hoisted_10 = {
  "class": "btn-group"
};
var _hoisted_11 = ["disabled"];
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("form", {
    onSubmit: _cache[3] || (_cache[3] = function () {
      return $setup.onSubmit && $setup.onSubmit.apply($setup, arguments);
    })
  }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("fieldset", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.normalizeProps)((0,vue__WEBPACK_IMPORTED_MODULE_0__.guardReactiveProps)($setup.getData('name'))), null, 16 /* FULL_PROPS */), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Select2"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)($setup.getData($setup.firstFieldProps.fieldName), {
    name: $setup.firstFieldProps.fieldName,
    idKey: "id",
    labelKey: $setup.firstFieldProps.labelKey,
    options: $setup.firstFieldProps.options,
    modelValue: $setup.values[$setup.firstFieldProps.fieldName]
  }), null, 16 /* FULL_PROPS */, ["name", "labelKey", "options", "modelValue"])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_4, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
    type: "button",
    "class": "btn icon only",
    onClick: _cache[0] || (_cache[0] = function () {
      var _$setup$firstFieldPro;
      return $setup.firstFieldProps.onAdd && (_$setup$firstFieldPro = $setup.firstFieldProps).onAdd.apply(_$setup$firstFieldPro, arguments);
    }),
    title: $setup.firstFieldProps.title,
    "aria-label": $setup.firstFieldProps.title
  }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Icon"], {
    name: "plus"
  })], 8 /* PROPS */, _hoisted_5)])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_6, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_7, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Select2"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)($setup.getData($setup.secondFieldProps.fieldName), {
    name: $setup.secondFieldProps.fieldName,
    idKey: "id",
    labelKey: $setup.secondFieldProps.labelKey,
    options: $setup.secondFieldProps.options,
    modelValue: $setup.values[$setup.secondFieldProps.fieldName],
    description: $setup.clientAlreadyInProject ? null : 'Le client sera automatiquement associé à ce nouveau projet'
  }), null, 16 /* FULL_PROPS */, ["name", "labelKey", "options", "modelValue", "description"])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_8, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
    type: "button",
    "class": "btn icon only",
    onClick: _cache[1] || (_cache[1] = function () {
      var _$setup$secondFieldPr;
      return $setup.secondFieldProps.onAdd && (_$setup$secondFieldPr = $setup.secondFieldProps).onAdd.apply(_$setup$secondFieldPr, arguments);
    }),
    title: $setup.secondFieldProps.title,
    "aria-label": $setup.secondFieldProps.title
  }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createVNode)($setup["Icon"], {
    name: "plus"
  })], 8 /* PROPS */, _hoisted_9)])]), $setup.phaseOptions.length == 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
    key: 0,
    type: "hidden"
  }, $setup.getData('business_type_id')), null, 16 /* FULL_PROPS */)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), $setup.phaseOptions.length > 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Select2"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
    key: 1
  }, $setup.getData('phase_id'), {
    name: "phase_id",
    idKey: "id",
    labelKey: "name",
    options: $setup.phaseOptions,
    modelValue: $setup.values['phase_id']
  }), null, 16 /* FULL_PROPS */, ["options", "modelValue"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), $setup.businessTypeOptions.length == 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Input"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
    key: 2,
    type: "hidden"
  }, $setup.getData('business_type_id')), null, 16 /* FULL_PROPS */)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), $setup.businessTypeOptions.length > 1 ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["Select2"], (0,vue__WEBPACK_IMPORTED_MODULE_0__.mergeProps)({
    key: 3
  }, $setup.getData('business_type_id'), {
    name: "business_type_id",
    idKey: "id",
    labelKey: "label",
    options: $setup.businessTypeOptions,
    modelValue: $setup.values['business_type_id']
  }), null, 16 /* FULL_PROPS */, ["options", "modelValue"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true)]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("div", _hoisted_10, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
    id: "deformsubmit",
    name: "submit",
    type: "submit",
    "class": "btn btn-primary btn btn-primary",
    value: "submit",
    disabled: $setup.isSubmitting
  }, " Valider ", 8 /* PROPS */, _hoisted_11), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)("button", {
    id: "deformcancel",
    name: "cancel",
    type: "button",
    "class": "btn btn-default",
    onClick: _cache[2] || (_cache[2] = function () {
      return $setup.emit('cancel');
    })
  }, " Annuler ")])], 32 /* NEED_HYDRATION */), $setup.showCustomerForm ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["CustomerFormComponent"], {
    key: 0,
    edit: false,
    url: $setup.customerUrl,
    "form-config-url": $setup.customerConfigUrl,
    onCancel: $setup.onHideCustomerForm,
    onSaved: $setup.onCustomerSaved,
    layout: $setup.FormModalLayout
  }, null, 8 /* PROPS */, ["url", "form-config-url"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true), $setup.showProjectForm ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["ProjectFormComponent"], {
    key: 1,
    edit: false,
    url: $setup.projectUrl,
    "form-config-url": $setup.projectConfigUrl,
    onCancel: $setup.onHideProjectForm,
    onSaved: $setup.onProjectSaved,
    layout: $setup.FormModalLayout
  }, null, 8 /* PROPS */, ["url", "form-config-url"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)("v-if", true)]);
}

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26":
/*!*****************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26 ***!
  \*****************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* binding */ render)
/* harmony export */ });
/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ "./node_modules/vue/dist/vue.runtime.esm-bundler.js");

var _hoisted_1 = {
  key: 0
};
function render(_ctx, _cache, $props, $setup, $data, $options) {
  return $setup.loading ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)("div", _hoisted_1, "Chargement des informations")) : ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)($setup["TaskAddForm"], {
    key: 1,
    "initial-data": $props.initialData,
    onSave: $setup.onSaved,
    onCancel: $setup.onCancel
  }, null, 8 /* PROPS */, ["initial-data"]));
}

/***/ }),

/***/ "./src/stores/project.js":
/*!*******************************!*\
  !*** ./src/stores/project.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   useProjectConfigStore: () => (/* binding */ useProjectConfigStore),
/* harmony export */   useProjectStore: () => (/* binding */ useProjectStore)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/asyncToGenerator */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/regenerator */ "./node_modules/@babel/runtime/regenerator/index.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var pinia__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! pinia */ "./node_modules/pinia/dist/pinia.mjs");
/* harmony import */ var _formConfig__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./formConfig */ "./src/stores/formConfig.js");
/* harmony import */ var _api_index__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/api/index */ "./src/api/index.ts");
/* harmony import */ var _modelStore__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./modelStore */ "./src/stores/modelStore.ts");


/**
 * Stores used during project add/edit
 */




var useProjectConfigStore = (0,_formConfig__WEBPACK_IMPORTED_MODULE_2__["default"])('project');
var useProjectStore = (0,pinia__WEBPACK_IMPORTED_MODULE_5__.defineStore)('project', {
  state: function state() {
    return {
      loading: true,
      error: false,
      collection: [],
      projectId: null,
      item: {}
    };
  },
  actions: {
    setCurrentProjectId: function setCurrentProjectId(projectId) {
      this.projectId = projectId;
    },
    loadProject: function loadProject() {
      var _arguments = arguments,
        _this = this;
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee() {
        var projectId;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context) {
          while (1) switch (_context.prev = _context.next) {
            case 0:
              projectId = _arguments.length > 0 && _arguments[0] !== undefined ? _arguments[0] : null;
              projectId = projectId || _this.projectId;
              if (projectId) {
                _context.next = 1;
                break;
              }
              throw Error('no Id provided');
            case 1:
              _this.loading = true;
              return _context.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.load(projectId).then(function (item) {
                _this.loading = false;
                _this.error = false;
                _this.item = item;
                return item;
              })["catch"](_this.handleError));
            case 2:
            case "end":
              return _context.stop();
          }
        }, _callee);
      }))();
    },
    loadProjects: function loadProjects(companyId, options) {
      var _this2 = this;
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee2() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context2) {
          while (1) switch (_context2.prev = _context2.next) {
            case 0:
              _this2.loading = true;
              return _context2.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.getProjects(companyId, options).then(function (result) {
                var collection;
                if (options.pageOptions && result.length == 2) {
                  _this2.collectionMetaData = result[0];
                  collection = result[1];
                } else {
                  collection = result;
                }
                _this2.loading = false;
                _this2.error = '';
                _this2.collection = collection;
                return collection;
              })["catch"](_this2.handleError));
            case 1:
            case "end":
              return _context2.stop();
          }
        }, _callee2);
      }))();
    },
    handleError: function handleError(error) {
      var _this3 = this;
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee3() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context3) {
          while (1) switch (_context3.prev = _context3.next) {
            case 0:
              _this3.loading = false;
              _this3.error = error;
              return _context3.abrupt("return", Promise.reject(error));
            case 1:
            case "end":
              return _context3.stop();
          }
        }, _callee3);
      }))();
    },
    saveProject: function saveProject(data) {
      var _this4 = this;
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee4() {
        var projectId;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context4) {
          while (1) switch (_context4.prev = _context4.next) {
            case 0:
              projectId = _this4.projectId || data.id;
              if (!projectId) {
                _context4.next = 1;
                break;
              }
              return _context4.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.update(data, projectId));
            case 1:
              return _context4.abrupt("return", _this4.createProject(data));
            case 2:
            case "end":
              return _context4.stop();
          }
        }, _callee4);
      }))();
    },
    createProject: function createProject(data) {
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee5() {
        var configStore, companyId;
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context5) {
          while (1) switch (_context5.prev = _context5.next) {
            case 0:
              if (!data.id) {
                _context5.next = 1;
                break;
              }
              throw Error('Project already exists (has an id)');
            case 1:
              configStore = useProjectConfigStore();
              companyId = configStore.getOptions('company_id');
              if (companyId) {
                _context5.next = 2;
                break;
              }
              throw Error('Missing company_id');
            case 2:
              _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.setCompanyId(companyId);
              return _context5.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.create(data));
            case 3:
            case "end":
              return _context5.stop();
          }
        }, _callee5);
      }))();
    },
    updateProject: function updateProject(data, projectId) {
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee6() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context6) {
          while (1) switch (_context6.prev = _context6.next) {
            case 0:
              if (projectId) {
                _context6.next = 1;
                break;
              }
              throw Error('no Id provided');
            case 1:
              return _context6.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].projects.update(data, projectId));
            case 2:
            case "end":
              return _context6.stop();
          }
        }, _callee6);
      }))();
    }
  },
  getters: (0,_modelStore__WEBPACK_IMPORTED_MODULE_4__.collectionHelpers)('project')
});

/***/ }),

/***/ "./src/stores/task.js":
/*!****************************!*\
  !*** ./src/stores/task.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   useTaskConfigStore: () => (/* binding */ useTaskConfigStore),
/* harmony export */   useTaskStore: () => (/* binding */ useTaskStore)
/* harmony export */ });
/* harmony import */ var _babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime/helpers/esm/asyncToGenerator */ "./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @babel/runtime/regenerator */ "./node_modules/@babel/runtime/regenerator/index.js");
/* harmony import */ var _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _formConfig__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./formConfig */ "./src/stores/formConfig.js");
/* harmony import */ var _api_index__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @/api/index */ "./src/api/index.ts");
/* harmony import */ var pinia__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! pinia */ "./node_modules/pinia/dist/pinia.mjs");





var useTaskConfigStore = (0,_formConfig__WEBPACK_IMPORTED_MODULE_2__["default"])('task');
var useTaskStore = (0,pinia__WEBPACK_IMPORTED_MODULE_4__.defineStore)('task', {
  state: function state() {
    return {
      loading: true,
      error: false,
      item: {}
    };
  },
  actions: {
    setAddUrl: function setAddUrl(url) {
      _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].tasks.setCollectionUrl(url);
    },
    createTask: function createTask(data) {
      return (0,_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_0__["default"])(/*#__PURE__*/_babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().mark(function _callee() {
        return _babel_runtime_regenerator__WEBPACK_IMPORTED_MODULE_1___default().wrap(function (_context) {
          while (1) switch (_context.prev = _context.next) {
            case 0:
              if (!data.id) {
                _context.next = 1;
                break;
              }
              throw Error('Task already exists (has an id)');
            case 1:
              return _context.abrupt("return", _api_index__WEBPACK_IMPORTED_MODULE_3__["default"].tasks.create(data));
            case 2:
            case "end":
              return _context.stop();
          }
        }, _callee);
      }))();
    }
  }
});

/***/ }),

/***/ "./src/views/task/add.js":
/*!*******************************!*\
  !*** ./src/views/task/add.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @/helpers/utils */ "./src/helpers/utils.js");
/* harmony import */ var _App_vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./App.vue */ "./src/views/task/App.vue");


var app = (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_0__.startApp)(_App_vue__WEBPACK_IMPORTED_MODULE_1__["default"]);

/***/ }),

/***/ "./src/components/forms/Checkbox.vue":
/*!*******************************************!*\
  !*** ./src/components/forms/Checkbox.vue ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _Checkbox_vue_vue_type_template_id_33525b5a__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./Checkbox.vue?vue&type=template&id=33525b5a */ "./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a");
/* harmony import */ var _Checkbox_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./Checkbox.vue?vue&type=script&setup=true&lang=js */ "./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_Checkbox_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_Checkbox_vue_vue_type_template_id_33525b5a__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/components/forms/Checkbox.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/components/forms/CheckboxList.vue":
/*!***********************************************!*\
  !*** ./src/components/forms/CheckboxList.vue ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _CheckboxList_vue_vue_type_template_id_4d3bdade__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./CheckboxList.vue?vue&type=template&id=4d3bdade */ "./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade");
/* harmony import */ var _CheckboxList_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./CheckboxList.vue?vue&type=script&setup=true&lang=js */ "./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_CheckboxList_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_CheckboxList_vue_vue_type_template_id_4d3bdade__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/components/forms/CheckboxList.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/components/project/ProjectForm.vue":
/*!************************************************!*\
  !*** ./src/components/project/ProjectForm.vue ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _ProjectForm_vue_vue_type_template_id_1c2b07f2__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./ProjectForm.vue?vue&type=template&id=1c2b07f2 */ "./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2");
/* harmony import */ var _ProjectForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ProjectForm.vue?vue&type=script&setup=true&lang=js */ "./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_ProjectForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_ProjectForm_vue_vue_type_template_id_1c2b07f2__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/components/project/ProjectForm.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/components/project/ProjectFormComponent.vue":
/*!*********************************************************!*\
  !*** ./src/components/project/ProjectFormComponent.vue ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _ProjectFormComponent_vue_vue_type_template_id_d30ac734__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./ProjectFormComponent.vue?vue&type=template&id=d30ac734 */ "./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734");
/* harmony import */ var _ProjectFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ProjectFormComponent.vue?vue&type=script&setup=true&lang=js */ "./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_ProjectFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_ProjectFormComponent_vue_vue_type_template_id_d30ac734__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/components/project/ProjectFormComponent.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/views/task/App.vue":
/*!********************************!*\
  !*** ./src/views/task/App.vue ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _App_vue_vue_type_template_id_0d237511__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./App.vue?vue&type=template&id=0d237511 */ "./src/views/task/App.vue?vue&type=template&id=0d237511");
/* harmony import */ var _App_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./App.vue?vue&type=script&setup=true&lang=js */ "./src/views/task/App.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_App_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_App_vue_vue_type_template_id_0d237511__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/views/task/App.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/views/task/components/TaskAddForm.vue":
/*!***************************************************!*\
  !*** ./src/views/task/components/TaskAddForm.vue ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _TaskAddForm_vue_vue_type_template_id_265db547__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TaskAddForm.vue?vue&type=template&id=265db547 */ "./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547");
/* harmony import */ var _TaskAddForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TaskAddForm.vue?vue&type=script&setup=true&lang=js */ "./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_TaskAddForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_TaskAddForm_vue_vue_type_template_id_265db547__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/views/task/components/TaskAddForm.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/views/task/components/TaskAddFormComponent.vue":
/*!************************************************************!*\
  !*** ./src/views/task/components/TaskAddFormComponent.vue ***!
  \************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _TaskAddFormComponent_vue_vue_type_template_id_1ff3cb26__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26 */ "./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26");
/* harmony import */ var _TaskAddFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js */ "./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js");
/* harmony import */ var _node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../../../node_modules/vue-loader/dist/exportHelper.js */ "./node_modules/vue-loader/dist/exportHelper.js");




;
const __exports__ = /*#__PURE__*/(0,_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__["default"])(_TaskAddFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_1__["default"], [['render',_TaskAddFormComponent_vue_vue_type_template_id_1ff3cb26__WEBPACK_IMPORTED_MODULE_0__.render],['__file',"src/views/task/components/TaskAddFormComponent.vue"]])
/* hot reload */
if (false) {}


/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__exports__);

/***/ }),

/***/ "./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js":
/*!******************************************************************************!*\
  !*** ./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js ***!
  \******************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_Checkbox_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_Checkbox_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./Checkbox.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js":
/*!**********************************************************************************!*\
  !*** ./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js ***!
  \**********************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_CheckboxList_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_CheckboxList_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./CheckboxList.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js":
/*!***********************************************************************************!*\
  !*** ./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js ***!
  \***********************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./ProjectForm.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js":
/*!********************************************************************************************!*\
  !*** ./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js ***!
  \********************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./ProjectFormComponent.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/views/task/App.vue?vue&type=script&setup=true&lang=js":
/*!*******************************************************************!*\
  !*** ./src/views/task/App.vue?vue&type=script&setup=true&lang=js ***!
  \*******************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_App_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_App_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./App.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js":
/*!**************************************************************************************!*\
  !*** ./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js ***!
  \**************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddForm_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../../node_modules/babel-loader/lib/index.js!../../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./TaskAddForm.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js":
/*!***********************************************************************************************!*\
  !*** ./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js ***!
  \***********************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__["default"])
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddFormComponent_vue_vue_type_script_setup_true_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../../node_modules/babel-loader/lib/index.js!../../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=script&setup=true&lang=js");
 

/***/ }),

/***/ "./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a":
/*!*************************************************************************!*\
  !*** ./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a ***!
  \*************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_Checkbox_vue_vue_type_template_id_33525b5a__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_Checkbox_vue_vue_type_template_id_33525b5a__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./Checkbox.vue?vue&type=template&id=33525b5a */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/Checkbox.vue?vue&type=template&id=33525b5a");


/***/ }),

/***/ "./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade":
/*!*****************************************************************************!*\
  !*** ./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade ***!
  \*****************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_CheckboxList_vue_vue_type_template_id_4d3bdade__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_CheckboxList_vue_vue_type_template_id_4d3bdade__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./CheckboxList.vue?vue&type=template&id=4d3bdade */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/forms/CheckboxList.vue?vue&type=template&id=4d3bdade");


/***/ }),

/***/ "./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2":
/*!******************************************************************************!*\
  !*** ./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2 ***!
  \******************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectForm_vue_vue_type_template_id_1c2b07f2__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectForm_vue_vue_type_template_id_1c2b07f2__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./ProjectForm.vue?vue&type=template&id=1c2b07f2 */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectForm.vue?vue&type=template&id=1c2b07f2");


/***/ }),

/***/ "./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734":
/*!***************************************************************************************!*\
  !*** ./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734 ***!
  \***************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectFormComponent_vue_vue_type_template_id_d30ac734__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_ProjectFormComponent_vue_vue_type_template_id_d30ac734__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./ProjectFormComponent.vue?vue&type=template&id=d30ac734 */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/components/project/ProjectFormComponent.vue?vue&type=template&id=d30ac734");


/***/ }),

/***/ "./src/views/task/App.vue?vue&type=template&id=0d237511":
/*!**************************************************************!*\
  !*** ./src/views/task/App.vue?vue&type=template&id=0d237511 ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_App_vue_vue_type_template_id_0d237511__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_App_vue_vue_type_template_id_0d237511__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/babel-loader/lib/index.js!../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./App.vue?vue&type=template&id=0d237511 */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/App.vue?vue&type=template&id=0d237511");


/***/ }),

/***/ "./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547":
/*!*********************************************************************************!*\
  !*** ./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547 ***!
  \*********************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddForm_vue_vue_type_template_id_265db547__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddForm_vue_vue_type_template_id_265db547__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../../node_modules/babel-loader/lib/index.js!../../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./TaskAddForm.vue?vue&type=template&id=265db547 */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddForm.vue?vue&type=template&id=265db547");


/***/ }),

/***/ "./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26":
/*!******************************************************************************************!*\
  !*** ./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26 ***!
  \******************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   render: () => (/* reexport safe */ _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddFormComponent_vue_vue_type_template_id_1ff3cb26__WEBPACK_IMPORTED_MODULE_0__.render)
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_2_node_modules_vue_loader_dist_index_js_ruleSet_1_rules_6_use_0_TaskAddFormComponent_vue_vue_type_template_id_1ff3cb26__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../../node_modules/babel-loader/lib/index.js!../../../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!../../../../node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26 */ "./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[2]!./node_modules/vue-loader/dist/index.js??ruleSet[1].rules[6].use[0]!./src/views/task/components/TaskAddFormComponent.vue?vue&type=template&id=1ff3cb26");


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
/******/ 	/* webpack/runtime/create fake namespace object */
/******/ 	(() => {
/******/ 		var getProto = Object.getPrototypeOf ? (obj) => (Object.getPrototypeOf(obj)) : (obj) => (obj.__proto__);
/******/ 		var leafPrototypes;
/******/ 		// create a fake namespace object
/******/ 		// mode & 1: value is a module id, require it
/******/ 		// mode & 2: merge all properties of value into the ns
/******/ 		// mode & 4: return value when already ns object
/******/ 		// mode & 16: return value when it's Promise-like
/******/ 		// mode & 8|1: behave like require
/******/ 		__webpack_require__.t = function(value, mode) {
/******/ 			if(mode & 1) value = this(value);
/******/ 			if(mode & 8) return value;
/******/ 			if(typeof value === 'object' && value) {
/******/ 				if((mode & 4) && value.__esModule) return value;
/******/ 				if((mode & 16) && typeof value.then === 'function') return value;
/******/ 			}
/******/ 			var ns = Object.create(null);
/******/ 			__webpack_require__.r(ns);
/******/ 			var def = {};
/******/ 			leafPrototypes = leafPrototypes || [null, getProto({}), getProto([]), getProto(getProto)];
/******/ 			for(var current = mode & 2 && value; typeof current == 'object' && !~leafPrototypes.indexOf(current); current = getProto(current)) {
/******/ 				Object.getOwnPropertyNames(current).forEach((key) => (def[key] = () => (value[key])));
/******/ 			}
/******/ 			def['default'] = () => (value);
/******/ 			__webpack_require__.d(ns, def);
/******/ 			return ns;
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
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		// The chunk loading function for additional chunks
/******/ 		// Since all referenced chunks are already included
/******/ 		// in this file, this function is empty here.
/******/ 		__webpack_require__.e = () => (Promise.resolve());
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
/******/ 			"task_add": 0
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
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendor-vue"], () => (__webpack_require__("./src/views/task/add.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;
//# sourceMappingURL=task_add.js.map