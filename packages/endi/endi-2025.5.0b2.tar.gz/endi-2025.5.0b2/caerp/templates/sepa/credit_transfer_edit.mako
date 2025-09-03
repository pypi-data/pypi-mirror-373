<%inherit file="${context['main_template'].uri}" />

<%block name='content'>
<div id="vue-app"></div>
</%block>

<%block name='footerjs'>
var AppOption = AppOption || {};
% for option, value in js_app_options.items():
${api.write_js_app_option(option, value)}
%endfor

</%block>