<%doc>
Aide pour remplir les stats Nova pour les prestations de service àl a personne
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>


<%block name='content'>
    ${searchform()}
    <div>
        <div class='table_container'>
            <table>
                <thead>
                <tr>
                    <th colspan="2"></th>
                    <th scope='col' class='col_number'>Janvier</th>
                    <th scope='col' class='col_number'>Février</th>
                    <th scope='col' class='col_number'>Mars</th>
                    <th scope='col' class='col_number'>Avril</th>
                    <th scope='col' class='col_number'>Mai</th>
                    <th scope='col' class='col_number'>Juin</th>
                    <th scope='col' class='col_number'>Juillet</th>
                    <th scope='col' class='col_number'>Août</th>
                    <th scope='col' class='col_number'>Septembre</th>
                    <th scope='col' class='col_number'>Octobre</th>
                    <th scope='col' class='col_number'>Novembre</th>
                    <th scope='col' class='col_number'>Décembre</th>
                    <th scope='col' class='col_number'>TOTAL année</th>
                </tr>
                </thead>
                % for key, label, formatter in metrics:
                    <tbody>
                    <tr class="row_recap">
                        <th scope="row" colspan="2" class="col_number">${label}</th>
                        % for month in range(1, 13):
                            <td class="col_number">
                                % if month in months_summary:
                                    ${formatter(getattr(months_summary[month], key))|n}
                                % else:
                                    <span style="font-weight: normal">−</span>
                                % endif

                            </td>
                        % endfor
                        <td class="col_number">
                            ${formatter(getattr(year_summary, key))|n}
                        </td>
                    </tr>
                    <!-- detail by product -->
                        % for product_id, months_stats in products_stats.items():
                            <tr>
                                <td class="level_spacer"></td>
                                <th scope="row" class="col_number"
                                    style="font-weight: unset; font-style: italic"
                                >
                                    ${products_index[product_id]}
                                </th>
                                % for month in range(1, 13):
                                    <td class="col_number">
                                        % if month in months_stats:
                                            ${formatter(getattr(months_stats[month], key))|n}
                                        % else:
                                            −
                                        % endif
                                    </td>
                                % endfor
                                <td class="col_number">
                                    ${formatter(getattr(year_stats[product_id], key))|n}
                                </td>
                            </tr>
                        % endfor
                    </tbody>
                % endfor
            </table>
        </div>
    </div>
</%block>
