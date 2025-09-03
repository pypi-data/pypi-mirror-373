<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>

% if records:
<table class="hover_table">
    <thead>
        <tr>
            <th scope="col" class="col_status col_text"></th>
            % if is_admin_view:
                <th scope="col" class="col_text">${sortable("Enseigne", "company_id")}</th>
            % endif
            <th scope="col" class="col_date">${sortable("Créé le", "created_at")}</th>
            <th scope="col" class="col_text">${sortable("Nom", "name")}</th>
            % if not is_supplier_view:
                <th scope="col" class="col_text">${sortable("Fournisseur", "supplier")}</th>
            % endif
            <th scope="col" class="col_number">HT</th>
            <th scope="col" class="col_number">TVA</th>
            <th scope="col" class="col_number">TTC</th>
            <th scope="col" class="col_number" title="Part réglée par la CAE">${sortable("Part CAE", "cae_percentage")}</th>
            <th scope="col" class="col_text">${sortable("Facture fournisseur", "supplier_invoice")}</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </tr>
    </thead>
    <tbody>
% else:
<table>
    <tbody>
        <tr>
            <td class='col_text'>
                <em>
                % if is_search_filter_active:
                    Aucune commande fournisseur correspondant à ces critères.
                % else:
                    Aucune commande fournisseur pour l’instant.
                % endif
                </em>
            </td>
        </tr>
% endif
    % for supplier_order in records:
        <tr class='tableelement' id="${supplier_order.id}">
            <% url = request.route_path("/supplier_orders/{id}", id=supplier_order.id) %>
            <% onclick = "document.location='{url}'".format(url=url) %>
            <% tooltip_title = "Cliquer pour voir ou modifier la commande « " + supplier_order.name + " »" %>
            <td class="col_status" onclick="${onclick}" title="${api.format_status(supplier_order)} - ${tooltip_title}">
                <span class="icon status ${supplier_order.status}">
                    ${api.icon(api.status_icon(supplier_order))}
                </span>
            </td>
            % if is_admin_view:
                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                    <% company_url = request.route_path('/companies/{id}', id=supplier_order.company.id) %>
                    % if api.has_permission('company.view', supplier_order.company):
                        <a href="${company_url}">${supplier_order.company.full_label | n}</a>
                        % if api.has_permission('global.company_view', supplier_order.company):
                            ${company_list_badges(supplier_order.company)}
                        % endif
                    % else:
                        ${supplier_order.company.full_label | n}
                    % endif
                </td>
            % endif
            <td class="col_date" onclick="${onclick}"title="${tooltip_title}">${api.format_date(supplier_order.created_at)}</td>
            <td class="col_text">
                <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">
                    ${supplier_order.name}
                    <!-- Si admin et commande auto-validée
                    <br>
                    <span class="icon tag positive">                        		
                        ${api.icon("user-check")}
                        Auto-validé
                    </span>
                    -->
                </a>
            </td>
            % if not is_supplier_view:
                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${supplier_order.supplier.label}</td>
            % endif
            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                ${api.format_amount(supplier_order.total_ht)}&nbsp;€
            </td>
            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                ${api.format_amount(supplier_order.total_tva)}&nbsp;€
            </td>
            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                ${api.format_amount(supplier_order.total)}&nbsp;€
            </td>
            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                ${supplier_order.cae_percentage}&nbsp;%
            </td>
            <td class="col_text">
                % if supplier_order.supplier_invoice:
                    <a href="${request.route_path('/supplier_invoices/{id}', id=supplier_order.supplier_invoice_id)}" title="Cliquer pour voir la facture fournisseur" aria-label="Cliquer pour voir la facture fournisseur">
                        ${supplier_order.supplier_invoice.remote_invoice_number}
                        % if supplier_order.supplier_invoice.paid_status == 'resulted':
                            (soldée)
                        % elif supplier_order.supplier_invoice.status == 'valid':
                            (validée)
                        % else:
                            (brouillon)
                        % endif
                    </a>
                % else:
                    aucune
                % endif
            </td>
            ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(supplier_order))}
        </tr>
    % endfor
    </tbody>
</table>
