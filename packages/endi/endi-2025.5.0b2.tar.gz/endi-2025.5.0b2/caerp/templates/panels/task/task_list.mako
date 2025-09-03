<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text"/>
<%namespace file="/base/utils.mako" import="format_filelist_ul" />

<% num_columns = len(columns) + 1 %>
% if datatype == "estimation":
  <% head_foot_colspan = num_columns - 4 %>
% else:
  <% head_foot_colspan = num_columns - 6 %>
% endif

<table class="top_align_table hover_table">
    % if records:
    <thead>
        % for column in columns:
            <th scope="col"
            % if column.css_class:
            class="${column.css_class}"
            % endif
            % if column.short_label and not column.sortable:
            title="${column.label | n}"
            % endif
            >
                % if column.sortable:
                    ${sortable(column.label, column.sort_key, column.short_label)}
                % elif column.short_label:
                    ${column.short_label | n}
                    <span class="screen-reader-text"> (${column.label | n})</span>
                % else:
                    ${column.label | n}
                % endif
            </th>
        % endfor
        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
    </thead>
    % endif
    <tbody>
        % if records:

            <tr class="row_recap">
                <th scope='row' colspan='${head_foot_colspan}' class='col_text'>Total</td>
                % if not tva_on_margin_display:
                    <td class='col_number'>${api.format_amount(totalht, precision=5)}&nbsp;€</td>
                    <td class='col_number'>${api.format_amount(totaltva, precision=5)}&nbsp;€</td>
                % endif
                <td class='col_number'>${api.format_amount(totalttc, precision=5)}&nbsp;€</td>
                <td colspan='3'></td>
            </tr>
            % for document in records:
                <% id_ = document.id %>
                <% internal_number = document.get_short_internal_number() %>
                <% name = document.name %>
                <% ht = document.ht %>
                <% tva = document.tva %>
                <% ttc = document.ttc %>
                <% status = document.global_status %>
                <% paid_status = getattr(document, 'paid_status', 'resulted') %>
                <% date = document.date %>
                % if datatype != "estimation":
                  <% official_number = document.official_number %>
                % else:
                  <% official_number = " " %>
                % endif
                % if is_admin_view:
                    <% company = document.get_company() %>
                    <% company_id = company.id %>
                    <% company_name = company.full_label %>
                % endif
                <% customer_id = document.customer.id %>
                <% customer_label = document.customer.label %>
                <% business_type = document.business_type %>
                <% url = api.task_url(document) %>
                <% onclick = "document.location='{url}'".format(url=url) %>
                <% tooltip_title = "Cliquer pour voir le document « " + document.name + " »" %>

                %if hasattr(document, "is_tolate"):
                  <% tolate='tolate-' + str(document.is_tolate()) %>
                %else:
                  <% tolate='tolate-False' %>
                %endif
                <tr class='status ${tolate} paid-status-${paid_status} status-${document.status}'>
                    <td class="col_status" title="${api.format_status(document)} - ${tooltip_title}" onclick="${onclick}">
                        <span class="icon status ${status}">
                            ${api.icon(api.status_icon(document))}
                        </span>
                    </td>
                    % if datatype != "estimation":
                        % if official_number:
                          <td class="col_text document_number" onclick="${onclick}" title="${tooltip_title}">
                            ${official_number}
                          </td>
                        % else:
                          <td class="col_text document_number" onclick="${onclick}" title="Ce document est un brouillon et n’a pas de numéro pour le moment - ${tooltip_title}">
                            <em><span class="screen-reader-text" title="Ce document est un "></span>Brouillon<span class="screen-reader-text"> et n’a pas de numéro pour le moment</span></em>
                          </td>
                        % endif
                    % endif
                    % if is_admin_view:
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${company_name}</td>
                    % endif
                    <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(date)}</td>
                    <td class="col_text">
                        <a href="${api.task_url(document)}" title="${tooltip_title}" aria-label="${tooltip_title}">
                           ${name} (<small>${internal_number}</small>)
                        </a>
                        ${request.layout_manager.render_panel('business_type_label', business_type)}
                        % if not is_admin_view:
                            <% description = document.description %>
                            <small class="description">${format_text(description)}</small>
                        % else:
                            % if document.auto_validated:
                            <span class="icon tag positive">
                                ${api.icon("user-check")}
                                Auto-validé
                            </span>
                            % endif
                       % endif
                    </td>
                    <td class="col_text invoice_company_name"><a href="${request.route_path("/customers/{id}", id=customer_id)}" title="Cliquer pour voir le client « ${customer_label} »" aria-label="Cliquer pour voir le client « ${customer_label} »">${customer_label}</a></td>
                    % if not tva_on_margin_display:
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}"><strong>${api.format_amount(ht, precision=5)}&nbsp;€</strong></td>
                        <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(tva, precision=5)}&nbsp;€</td>
                    % endif
                    <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(ttc, precision=5)}&nbsp;€</td>
                    % if datatype != "estimation":
                        <td class="col_text">
                            % if len(document.payments) == 1 and paid_status == 'resulted':
                                <% payment = document.payments[0] %>
                                <% url = request.route_path('payment', id=payment.id) %>
                                <a href="#!" onclick="window.openPopup('${url}')" title="Voir le détail de ce paiement dans une nouvelle fenêtre" aria-label="Voir le détail de ce paiement dans une nouvelle fenêtre">
                                    Le ${api.format_date(payment.date)}
                                    <small>(${api.format_paymentmode(payment.mode)})</small>
                                </a>
                            % elif len(document.payments) > 0:
                                <ul>
                                    % for payment in document.payments:
                                        <% url = request.route_path('payment', id=payment.id) %>
                                        <li>
                                            <a href="#!" onclick="window.openPopup('${url}')" title="Voir le détail de ce paiement dans une nouvelle fenêtre" aria-label="Voir le détail de ce paiement dans une nouvelle fenêtre">
                                                <strong>${api.format_amount(payment.amount, precision=5)}&nbsp;€</strong>
                                                le ${api.format_date(payment.date)}
                                                <small>(${api.format_paymentmode(payment.mode)})</small>
                                            </a>
                                        </li>
                                    % endfor
                                </ul>
                                % if document.paid_status != "resulted":
                                <span class="topay"><small>Restant dû&nbsp;: </small><strong>${api.format_amount(document.topay(), precision=5)}&nbsp;€</strong></span>
                                % endif
                            % endif
                            % if len(getattr(document, "valid_cancelinvoices", [])) > 0:
                                <ul>
                                    % for cancelinvoice in document.valid_cancelinvoices:
                                        <% url = api.task_url(cancelinvoice, suffix="/general") %>
                                        <li>
                                            <a href="#!" onclick="window.openPopup('${url}')" title="Cliquer ici pour voir l'avoir" aria-label="Cliquer ici pour voir l'avoir">
                                                Avoir ${cancelinvoice.official_number} de <strong>${api.format_amount(cancelinvoice.ttc, precision=5)}&nbsp;€</strong>
                                                le ${api.format_date(cancelinvoice.date)}
                                            </a>
                                        </li>
                                    % endfor
                                </ul>
                            % endif
                        </td>
                        <td class="col_text">
                            ${format_filelist_ul(document)}
                            % if hasattr(document, 'estimation_id') and document.estimation_id is not None:
                                ${format_filelist_ul(document.estimation)}
                            % elif hasattr(document, 'invoice_id') and document.invoice_id is not None:
                                ${format_filelist_ul(document.invoice)}
                            % endif
                        </td>
                    % endif
                        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(document))}
                </tr>
            % endfor
        % else:
            <tr>
                <td class='col_text' colspan='${num_columns}'><em>
                    % if datatype == "estimation":
                    Aucun devis
                    % else:
                    Aucune facture
                    % endif
                     ne correspond à ces critères
                </em></td>
            </tr>
        % endif
    </tbody>
    % if records:
    <tfoot>
        <tr class="row_recap">
            <th scope='row' colspan='${head_foot_colspan}' class='col_text'>Total</td>
            % if not tva_on_margin_display:
                <td class='col_number'>${api.format_amount(totalht, precision=5)}&nbsp;€</td>
                <td class='col_number'>${api.format_amount(totaltva, precision=5)}&nbsp;€</td>
            % endif
            <td class='col_number'>${api.format_amount(totalttc, precision=5)}&nbsp;€</td>
            <td colspan='3'></td>
        </tr>
    </tfoot>
    % endif
</table>
