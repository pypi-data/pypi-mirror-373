<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />
<%block name='content'>
<div class='layout flex two_cols quarter_reverse'>
    <div>
        <h3>
        ${title}
        </h3>
        <div>
        ${form|n}
        </div>
    </div>
    <div class='context_help'>
        <h4>
            Codes dossier utilisés
        </h4>
        <ul>
            ## "_project" to avoid collision with "project" in template context
            % for _project in project_codes:
                <li>
                ${_project.code.upper()} (${_project.name})
                </li>
            % endfor
        </ul>
    </div>
</div>
</%block>
