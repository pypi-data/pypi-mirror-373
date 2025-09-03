<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools' id='js_actions'></div>
</%block>

<%block name="content">
% if request.context.status == 'wait':
<div class='container-fluid beforeContent content_vertical_double_padding'>
	<h4>
	<span class="icon status wait">
		${api.icon('clock')}
	</span>
	${api.format_status(request.context)}
	</h4>
</div>
% endif
<div id='js-main-area' class='task-edit'></div>
</%block>
<%block name='footerjs'>
AppOption = {};
% for key, value in js_app_options.items():
AppOption["${key}"] = "${value}";
% endfor;
</%block>
