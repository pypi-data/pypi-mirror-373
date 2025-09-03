<%inherit file="${context['main_template'].uri}" />
<%block name="content">
<div id='messageboxes'></div>
<div id="holidays"></div>
<div id="form-container"></div>
</%block>
<%block name="footerjs">
AppOptions = {};
AppOptions['loadurl'] = "${loadurl}";
</%block>
