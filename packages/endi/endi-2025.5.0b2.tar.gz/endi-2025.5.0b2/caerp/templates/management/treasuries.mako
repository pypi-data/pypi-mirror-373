<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>

<%block name="headtitle">
    <h1>${title} <small>(${nb_results} enseignes au ${api.format_date(treasuries_date)})</small></h1>
</%block>

<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <div role='group'></div>
        <div role='group'>
            <a class='btn' href='${export_xls_url}' title="Export au format Excel (xlsx) dans une nouvelle fenêtre" aria-label="Export au format Excel (xlsx) dans une nouvelle fenêtre">
                ${api.icon('file-excel')} Excel
            </a>
            <a class='btn' href='${export_ods_url}' title="Export au format Open Document (ods) dans une nouvelle fenêtre" aria-label="Export au format Open Document (ods) dans une nouvelle fenêtre">
                ${api.icon('file-spreadsheet')} ODS
            </a>
        </div>
    </div>
</div>
</%block>

<%block name='content'>

<div class='search_filters'>
    ${form|n}
</div>

<div>
    <div class="table_container scroll_hor">
        <button class="fullscreen_toggle small" title="Afficher le tableau en plein écran" aria-label="Afficher le tableau en plein écran" onclick="toggleTableFullscreen(this);return false;">
            ${api.icon('expand')}
            ${api.icon('compress')}
            <span>Plein écran</span>
        </button>
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_text">Analytique</th>
                    <th scope="col" class="col_text min14">Enseigne(s)</th>
                    % for header in treasury_headers:
                    <th scope="col" class="col_number" title="${header}">
                        ${header}
                    </th>
                    % endfor
                </tr>
            </thead>
            <tbody>
                % for code_ana, companies, treasury_values in treasury_data:
                    <tr>
                        <th scope="row" class="col_text">${code_ana}</th>
                        <th scope="row" class="col_text min14">
                            % if len(companies) == 1:
                                <% company = companies[0] %>
                                <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                                <a href="${company_url}">${company.full_label}</a> 
                                <small>${company_list_badges(company)}</small>
                            % else :
                                <ul>
                                % for company in companies:
                                    <li>
                                        <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                                        <a href="${company_url}">${company.full_label}</a> 
                                        <small>${company_list_badges(company)}</small>
                                    </li>
                                % endfor
                                </ul>
                            % endif
                        </th>
                        % for value in treasury_values:
                        <td class="col_number">
                            ${api.format_float(value, 2)}&nbsp;€
                        </td>
                        % endfor
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>

</%block>
