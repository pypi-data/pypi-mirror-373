<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>
<div class='text_block separate_top'>
    <h2>Historique des états de trésorerie</h2>
</div>

${searchform()}

% if records is not None:
    <div>
        <div>
            ${records.item_count} Résultat(s)
        </div>
        <div class='table_container limited_width width40'>
            <table class="top_align_table hover_table">
                <thead>
                    <tr>
                        <th scope="col" class="col_text">${sortable("Enseigne", "company")}</th>
                        <th scope="col" class="col_number">${highlight_entry.label | n}</th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % if records:
                        % for record in records:
                            <tr>
                                <td class="col_text">${record.company.full_label}</td>
                                <td class="col_number">
                                    <% first_measure = record.get_measure_by_type(highlight_entry.id) %>
                                    % if first_measure is not None:
                                        ${api.format_amount(first_measure.value, precision=0)}&nbsp;€
                                    % else:
                                        -
                                    % endif
                                </td>
                                ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(record))}
                            </tr>
                        % endfor
                    % else:
                        <tr>
                            <td colspan='3' class="col_text">Aucun état n'a été généré</td>
                        </tr>
                    % endif
                </tbody>
            </table>
            ${pager(records)}
        </div>
    </div>
% endif
</%block>
