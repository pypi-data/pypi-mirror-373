<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>

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

<div class="alert alert-info">
    <p>
        <span class="icon">${api.icon('info-circle')}</span> 
        Les montants de contribution affichés dans ce tableau sont issus des données remontées de la comptabilité. 
    </p><br/>
    <p>
        Ils correspondent au solde de tous les comptes configurés dans les modules de contribution de type "<em>Contribution</em>"
        (<a href="${config_modules_url}"> Modules de contribution </a> et <a href="${config_internal_modules_url}"> Modules de contribution internes</a>).</p>
</div>

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
                    <th scope="col" class="col_text min10">Enseigne</th>
                    %for year, month in months:
                        <th scope="col" class="col_number">
                            <small>${api.short_month_name(month)} ${str(year)[2:]}</small>
                        </th>
                    %endfor
                    <th scope="col" class="col_number">
                        <small>TOTAL</small>
                    </th>
                </tr>
                <tr class="row_recap">
                    <th class="col_text min10">TOTAL (${companies.count()} enseignes)</th>
                    %for month_value in aggregate_datas:
                        <th scope="col" class="col_number">
                            ${api.format_float(month_value, 2)}&nbsp;€
                        </th>
                    %endfor
                    <th scope="col" class="col_number">
                        ${api.format_float(sum(aggregate_datas), 2)}&nbsp;€
                    </th>
                </tr>
            </thead>
            <tbody>
                % for company in companies:
                    <tr>
                        <th scope="row" class="col_text min10">
                            <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                            <a href="${company_url}">${company.full_label}</a> 
                            <small>${company_list_badges(company)}</small>
                        </th>
                        % for month_value in contributions_datas[company.id]:
                            <td class="col_number">
                                ${api.format_float(month_value, 2)}&nbsp;€
                            </td>
                        % endfor
                        <th class="col_number">
                            ${api.format_float(sum(contributions_datas[company.id]), 2)}&nbsp;€
                        </th>
                    </tr>
                %endfor
            </tbody>
        </table>
    </div>
</div>
</%block>
