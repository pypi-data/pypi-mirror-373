<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="top_align_table hover_table">
            % if records:
            <thead>
                <th scope="col" class="col_status col_text"></th>
                <th scope="col">${sortable("Demandé le", "status_date")}</th>
                <th scope="col" class="col_text">${sortable("Enseigne", "company")}</th>
                <th scope="col" class="col_text">${sortable("Nom", "name")}</th>
                <th scope="col" class="col_text">${sortable("Fournisseur", "supplier")}</th>
                <th scope="col" class="col_number">HT</th>
                <th scope="col" class="col_number">TVA</th>
                <th scope="col" class="col_number">TTC</th>
                <th scope="col" class="col_number" title="Part réglée par la CAE">${sortable("Part CAE", "cae_percentage")}</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if records:
                    % for supplier_order in records:
                        <% company = supplier_order.company %>
                        <% url = request.route_path('/supplier_orders/{id}', id=supplier_order.id, _query={'come_from': request.current_route_path()}) %>
                        <% tooltip_title = "Cliquer pour voir cette commande" %>

                        <tr class='tableelement' id="${supplier_order.id}">
                            <td class="col_status" title="${api.format_status(supplier_order)}">
                                <span class="icon status ${supplier_order.status}">
                                    ${api.icon(api.status_icon(supplier_order))}
                                </span>
                            </td>
                            <td class="col_date">${api.format_date(supplier_order.status_date)}</td>
                            <td class="col_text">
                                <a href="${request.route_path('/companies/{id}', id=company.id)}" title="Cliquer pour voir l'enseigne « ${company.full_label} »" aria-label="Cliquer pour voir l'enseigne « ${company.full_label} »">${company.full_label}</a>
                            </td>
                            <td class="col_text">
                                <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${supplier_order.name}</a>
                            </td>
                            <td class="col_text">${supplier_order.supplier.label}</td>
                            <td class="col_number">${api.format_amount(supplier_order.total_ht)}&nbsp;€</td>
                            <td class="col_number">${api.format_amount(supplier_order.total_tva)}&nbsp;€</td>
                            <td class="col_number">${api.format_amount(supplier_order.total)}&nbsp;€</td>
                            <td class="col_number">${supplier_order.cae_percentage}&nbsp;%</td>
                            <td class="col_actions width_one">
                                <a class="btn icon only" href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${api.icon("arrow-right")}</a>
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr><td class='col_text' colspan='10'>
                        <em>
                        % if '__formid__' in request.GET:
                            Aucune commande fournisseur en attente de validation correspondant à ces critères
                        % else:
                            Aucune commande fournisseur en attente de validation
                        % endif
                        </em>
                    </td></tr>
                % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
