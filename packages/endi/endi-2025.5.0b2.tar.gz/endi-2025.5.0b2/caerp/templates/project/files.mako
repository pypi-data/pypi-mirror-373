<%inherit file="${context['main_template'].uri}" />
<%block name='actionmenucontent'>
% if api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'>
            <a class='btn btn-primary icon' href="${layout.edit_url}">
                ${api.icon('pen')}
                Modifier le dossier
            </a>
        </div>
    </div>
</div>
% endif
</%block>



<%block name='mainblock'>
<div id="vue-file-app-container"></div>
</%block>
<%block name='footerjs'>
var AppOption = AppOption || {};
% for option, value in js_app_options.items():
${api.write_js_app_option(option, value)}
% endfor
</%block>