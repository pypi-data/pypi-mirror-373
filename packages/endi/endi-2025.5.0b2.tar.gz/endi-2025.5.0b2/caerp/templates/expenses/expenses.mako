<%namespace file="/base/utils.mako" import="table_btn"/>
<%inherit file="${context['main_template'].uri}" />

<%block name='actionmenucontent'>
% if not several_users and api.has_permission('context.add_expensesheet') and conf_msg is UNDEFINED and request.context.employees:
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        <a class='btn btn-primary' title="Ajouter une nouvelle note de dépenses" href='${request.route_path("user_expenses", id=request.context.id, uid=request.context.employees[0].id)}'>
            ${api.icon("plus")} 
            Ajouter<span class="no_mobile">&nbsp;une note de dépenses</span>
        </a>
    </div>
</div>
% endif
</%block>

<%block name="content">
% if conf_msg is not UNDEFINED:
    <div class="alert alert-danger">
        <span class="icon">${api.icon("plus")}</span>
        ${conf_msg}
    </div>
% else:
    % for year, values in expense_sheets.items():
    <div class='collapsible separate_block content_padding'>
        <h2 class='collapse_title'>
        <%
        if year == current_year:
            expanded = "true"
            tooltip = "Masquer les notes de dépenses de " + str(year)
        else:
            expanded = "false"
            tooltip = "Afficher les notes de dépenses de " + str(year)
        %>
            <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded="${expanded}" title="${tooltip}" aria-label="${tooltip}" class='separate_bottom'>
            	${api.icon('chevron-down','arrow')}
            	${year}
            </a>
        </h2>
        % if year == current_year:
        <div class="collapse_content content_vertical_padding">
        %else:
        <div class="collapse_content content_vertical_padding" hidden>
        %endif
            <div class="content">
            % for user, expenses in values.items():
	            <div class="content_vertical_padding">
	                <div class="form-section">
	                    <h2 class="title with_action">
	                        <div>
	                            Notes de dépenses de ${api.format_account(user)}
	                        </div>
	                        <div class="align_right">
	                        % if several_users and api.has_permission('context.add_expensesheet') and user in request.context.employees:
	                            <a class='btn icon icon_only_mobile icon_only_tablet' title="Ajouter une nouvelle note de dépenses pour  ${api.format_account(user)}" aria-label="Ajouter une nouvelle note de dépenses pour ${api.format_account(user)}"
	                            href='${request.route_path("user_expenses", id=request.context.id, uid=user.id)}'>
	                                ${api.icon("plus")}
	                                Ajouter
	                            </a>
	                        </div>
	                        % endif
	                    </h2>
	                    <div class="content">
	                        <div class='table_container'>
	                        % if not expenses:
	                            <table class="top_align_table">
	                                <tbody>
	                                    <tr>
	                                        <td class="col_text"><em>Aucune note de dépenses</em></td>
	                                    </tr>
	                                </tbody>
	                            </table>
	                        % else:
	                            <table class="hover_table top_align_table">
	                                <thead>
	                                    <th scope="col" class="col_status"><span class="screen-reader-text">Statut</span></th>
	                                    <th scope="col" class="col_text">Période et nom</th>
	                                    <th scope="col" class="col_number">HT</th>
	                                    <th scope="col" class="col_number">TVA</th>
	                                    <th scope="col" class="col_number">TTC</th>
	                                    <th scope="col" class="col_number">Kms</th>
	                                    <th scope="col" class="col_text">Paiements</th>
	                                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
	                                </thead>
	                                <tbody>
	                                    % if expenses:
	                                        <% total_ht = sum([km.total_ht for km in expenses]) %>
	                                        <% total_tva = sum([km.total_tva for km in expenses]) %>
	                                        <% total_ttc = sum([km.total for km in expenses]) %>
	                                        <% total_km = sum([km.total_km for km in expenses]) %>
	                                        <tr class="row_recap">
	                                            <th scope='row' colspan='2' class='col_text'>Total</th>
	                                            <td class='col_number'>${api.format_amount(total_ht)} €</td>
	                                            <td class='col_number'>${api.format_amount(total_tva)} €</td>
	                                            <td class='col_number'>${api.format_amount(total_ttc)} €</td>
	                                            <td class='col_number'>${api.remove_kms_training_zeros(api.format_amount(total_km))}</td>
	                                            <td colspan='2'></td>
	                                        </tr>
	                                    % endif
	                                    % for expense in expenses:
	                                        <% url = request.route_path('/expenses/{id}', id=expense.id) %>
	                                        <% onclick = "document.location='{url}'".format(url=url) %>
	                                        <% tooltip_title = "Cliquer pour voir cette note de dépenses" %>
	                                        <tr>
	                                            <td onclick="${onclick}"
	                                                class="col_status"
	                                                title="${api.format_expense_status(expense)} - ${tooltip_title}"
	                                                >
	                                                <span class="icon status ${expense.global_status}">
	                                                    ${api.icon(api.status_icon(expense))} 
	                                                </span>
	                                            </td>
	                                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
	                                                ${api.month_name(expense.month).capitalize()} ${expense.year}
	                                                % if expense.title:
	                                                    <br /><small>${expense.title}</small>
	                                                % endif
	                                            </td>
	                                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(expense.total_ht)} €</td>
	                                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(expense.total_tva)} €</td>
	                                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(expense.total)} €</td>
	                                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">
	                                                ${api.remove_kms_training_zeros(api.format_amount(expense.total_km))}
	                                            </td>
	                                            % if expense.payments:
	                                            <td class="col_text">
	                                            % else:
	                                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
	                                            % endif
	                                                % for payment in expense.payments:
	                                                    % if loop.first:
	                                                        <ul>
	                                                    % endif
	                                                            <% url = request.route_path('expense_payment', id=payment.id) %>
	                                                            <li>
	                                                            <a href="${url}" title="Cliquer pour voir le détail de ce paiement" aria-label="Cliquer pour voir le détail de ce paiement">
	                                                                <strong>${api.format_amount(payment.amount)}&nbsp;€</strong>
	                                                                le ${api.format_date(payment.date)} 
	                                                                <small>(${api.format_paymentmode(payment.mode)} enregistré par ${api.format_account(payment.user)})</small>
	                                                            </a>
	                                                            </li>
	                                                    % if loop.last:
	                                                        </ul>
	                                                    % endif
	                                                % endfor
                                                    % if expense.payments and expense.paid_status != "resulted":
                                                      <span class="topay"><small>Restant dû&nbsp;: </small><strong>${api.format_amount(expense.topay())}&nbsp;€</strong></span>
                                                    % endif
	                                            </td>
	                                            <td class="col_actions width_two">
	                                                <ul>
	                                                    <li>
	                                                        ${table_btn(request.route_path('/expenses/{id}', id=expense.id), "Voir", "Voir cette note de dépenses", "pen")}
	                                                    </li>
	                                                    <li>
	                                                        ${table_btn(request.route_path('/expenses/{id}.xlsx', id=expense.id), "Export", "Exporter cette note de dépenses au format xslx", "file-excel")}
	                                                    </li>
	                                                </ul>
	                                            </td>
	                                        </tr>
	                                    % endfor
	                                </tbody>
	                            </table>
	                        % endif
	                        </div>
	                    </div>
	                </div>
	            </div>
            % endfor
        	</div>
    	</div>
    </div>
    % endfor
% endif
</%block>
