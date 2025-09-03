<%inherit file="/base/formpage.mako" />
<%block name='footerjs'>
var AppOptions = AppOptions || {};
AppOptions['company_id'] = "${request.context.get_company_id()}"
</%block>
