<%namespace file="/base/utils.mako" import="company_list_badges"/>

<table class="hover_table">
    % if records:
    <thead>
        <tr>
            <th scope="col" class="col_date">Créée le</th>
            <th scope="col" class="col_text">Intitulé de l'affaire</th>
            % if is_admin_view:
                <th scope="col" class="col_text">Enseigne</th>
            % endif
            % if not is_customer_list:
                <th scope="col" class="col_text">Client</th>
            % endif
            <th scope="col" class="col_text">Documents</th>
            <th scope="col" class="col_number">Devisé</th>
            <th scope="col" class="col_number">Facturé</th>
            <th scope="col" class="col_number">À&nbsp;facturer</th>
            <th scope="col" class="col_number">À&nbsp;encaisser</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </tr>
    </thead>
    % endif
    <tbody>
    % if records:
        <tr class="row_recap">
            <th scope='row' colspan='${total_colspan}' class='col_text'>Total</th>
            <th class='col_number'>${api.format_amount(total_estimated, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_invoiced, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_to_invoice, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_to_pay, precision=5)}&nbsp;€</th>
            <th scope='row' class='col_text'></th>
        </tr>
        % for id_, record in records:
            <% url = request.route_path('/businesses/{id}', id=record.id) %>
            <% onclick = "document.location='{url}'".format(url=url) %>
            <% tooltip_title = "Cliquer pour voir l'affaire « " + record.name + " »" %>
            <tr>
                <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(record.created_at)}</td>
                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                    ${record.name | n}<br/>
                    ${request.layout_manager.render_panel('business_type_label', record.business_type)}
                </td>
                % if is_admin_view:
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                        <% company = record.project.company %>
                        <% company_url = request.route_path('/companies/{id}', id=company.id) %>
                        % if api.has_permission('company.view', company):
                            <a href="${company_url}" title="Cliquer pour voir l'enseigne « ${company.name} »" aria-label="Cliquer pour voir l'enseigne « ${company.name} »">${company.full_label | n}</a>
                            % if api.has_permission('global.company_view', company):
                                ${company_list_badges(company)}
                            % endif
                        % else:
                            ${company.full_label | n}
                        % endif
                    </td>
                % endif
                % if not is_customer_list:
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                        % if record.tasks:
                            <% customer = record.tasks[0].customer %>
                            <% customer_url = request.route_path('/customers/{id}', id=customer.id) %>
                            <a href="${customer_url}" title="Cliquer pour voir le client « ${customer.label} »" aria-label="Cliquer pour voir le client « ${customer.label} »">${customer.label}</a>
                        % else:
                            <em>Cette affaire est vide</em>
                        % endif
                    </td>
                % endif
                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                    % if record.tasks:
                        <ul>
                        % for t in (t for t in record.tasks if t.status == "valid"):
                            % if t.official_number:
                                <% task_name = t.official_number %>
                            % else:
                                <% task_name = t.get_short_internal_number() %>
                            % endif
                            <li><a href="${api.task_url(t)}" title="${task_name}" aria-label="${task_name}">${task_name}</a></li>
                        % endfor
                        </ul>
                    % else:
                        <em>Cette affaire est vide</em>
                    % endif
                </td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                    ${api.format_amount(record.get_total_estimated('ttc'), precision=5)}&nbsp;€
                </td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                    ${api.format_amount(record.get_total_income('ttc'), precision=5)}&nbsp;€
                </td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                    ${api.format_amount(record.amount_to_invoice('ttc'), precision=5)}&nbsp;€
                </td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
                    ${api.format_amount(record.get_topay(), precision=5)}&nbsp;€
                </td>
                ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(record))}
            </tr>
        % endfor
        <tr class="row_recap">
            <th scope='row' colspan='${total_colspan}' class='col_text'>Total</th>
            <th class='col_number'>${api.format_amount(total_estimated, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_invoiced, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_to_invoice, precision=5)}&nbsp;€</th>
            <th class='col_number'>${api.format_amount(total_to_pay, precision=5)}&nbsp;€</th>
            <th scope='row' class='col_text'></th>
        </tr>
    % else:
        <tr>
            <td colspan="${nb_columns}" class="col_text"><em>Aucune affaire correspondant à ces critères</em></td>
        </tr>
    % endif
    </tbody>
</table>
