<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='afteractionmenu'>
% if current_grid is not None:
    <div class="search_filters limited_width width50">
        ${form|n}
    </div>

    <div class="text_block limited_width width50">
        <h2>
            ${current_grid.label | n}
        </h2>
    </div>

    % if current_grid.active_rows or current_grid.passive_rows:
        <% active_measures = current_grid.active_rows %>
        <% passive_measures = current_grid.passive_rows %>
        <div class="limited_width width50 layout flex two_cols">
            <div class="table_container">
                <table>
                    <tbody>
                        <tr class="row_recap">
                            <td colspan="2"><h3>Actif</h3></td>
                        </tr>
                    </tbody>
                    <tbody>
                    % for typ, value in active_measures:
                        % if typ.is_total:
                            <tr class="row_recap">
                        % else:
                            <tr>
                        % endif
                                <th scope="row" class="col_text">
                                ${typ.label | n}
                                </th>
                                <td class="col_number">${api.format_float(value, precision=2)|n}&nbsp;€</td>
                            </tr>
                    % endfor
                    </tbody>
                </table>
            </div>
            <div class="table_container">
                <table>
                    <tbody>
                        <tr class="row_recap">
                            <td colspan="2"><h3>Passif</h3></td>
                        </tr>
                    </tbody>
                    <tbody>
                    % for typ, value in passive_measures:
                        % if typ.is_total:
                            <tr class="row_recap">
                        % else:
                            <tr>
                        % endif
                                <th scope="row" class="col_text">
                                ${typ.label | n}
                                </th>
                                <td class="col_number">${api.format_float(value, precision=2)|n}&nbsp;€</td>
                            </tr>
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
    % else:
        <div class='alert' tabindex='0'><h4>Le bilan disponible est vide</h4></div>
    % endif
% else:
    <div class='alert' tabindex='0'><h4>Aucun bilan n’est disponible</h4></div>
% endif
</%block>

