<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

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
                    <th scope="col" class="col_text min10" rowspan="2">Salarié</th>
                    %for year, month in months:
                        <th scope="col" class="col_text align_center" colspan="2">
                            ${api.short_month_name(month)} ${str(year)[2:]}
                        </th>
                    %endfor
                    <th scope="col" class="col_text align_center" colspan="2">Total</th>
                </tr>
                <tr>
                    %for year, month in months:
                        <th scope="col" class="col_number" title="Nombre de kilomètres">
                            <small><span class="screen-reader-text">Nombre de </span>K<span class="screen-reader-text">ilo</span>m<span class="screen-reader-text">ètre</span>s</small>
                        </th>
                        <th scope="col" class="col_number"><small>Taux</small></th>
                    %endfor
                    <th scope="col" class="col_number" title="Total des kilomètres validés dans enDI en ${year}">
                        <span class="screen-reader-text">Total des </span>K<span class="screen-reader-text">ilo</span>m<span class="screen-reader-text">ètre</span>s<span class="screen-reader-text"> validés dans enDI en ${year}</span>
                    </th>
                    <th scope="col" class="col_number" title="Montant total des kilomètres remboursés en ${year}">
                        Montant <span class="screen-reader-text">total des kilomètres remboursés en ${year}</span>
                    </th>
                </tr>
                <tr class="row_recap">
                    <th class="col_text min10">TOTAL (${users.count()} salariés)</th>
                    <% total_kms = 0 %>
                    <% total_amount = 0 %>
                    %for month_kms, month_amount in aggregate_data:
                        <th scope="col" class="col_number">
                            ${api.remove_kms_training_zeros(api.format_amount(month_kms))}
                        </th>
                        <th scope="col" class="col_number">&nbsp;</th>
                        <% total_kms += month_kms %>
                        <% total_amount += month_amount %>
                    %endfor
                    <th scope="col" class="col_number">
                        ${api.remove_kms_training_zeros(api.format_amount(total_kms))}
                    </th>
                    <th scope="col" class="col_number">
                        ${api.format_amount(total_amount, precision=2)}&nbsp;€
                    </th>
                </tr>
            </thead>
            <tbody>
                % for user in users:
                    <tr>
                        <th scope="row" class="col_text min10">
                            ${api.format_account(user)}
                        </th>
                        <% total_kms = 0 %>
                        <% total_amount = 0 %>
                        % for nb_kms, amount, rate in kms_data[user.id]:
                            <td class="col_number">${api.remove_kms_training_zeros(api.format_amount(nb_kms))}</td>
                            <td class="col_number"><small>${rate}</small></td>
                            <% total_kms += nb_kms %>
                            <% total_amount += amount %>
                        % endfor
                        <th class="col_number">
                            ${api.remove_kms_training_zeros(api.format_amount(total_kms))}
                        </th>
                        <th class="col_number">
                            ${api.format_amount(total_amount, precision=2)}&nbsp;€
                        </th>
                    </tr>
                %endfor
            </tbody>
        </table>
    </div>
</div>
</%block>
