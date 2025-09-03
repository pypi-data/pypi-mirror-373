<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>


<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
		${request.layout_manager.render_panel('action_buttons', links=stream_main_actions())}
  		${request.layout_manager.render_panel(
    		'menu_dropdown',
		    label="Exporter",
		    links=stream_more_actions(),
		    display_label=True,
			icon="file-export"
		)}
	</div>
</div>
</%block>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <% columns = 11 %>
        % if records:
        <table class="top_align_table hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col">${sortable("N° pièce", "official_number")}</th>
                    <th scope="col" class="col_text">${sortable("Entrepreneur", "name")}</th>
                    <th scope="col" class="col_text">${sortable("Période et nom", "month")}</th>
                    <th scope="col" class="col_number"><span class="screen-reader-text">Montant </span>HT</th>
                    <th scope="col" class="col_number">TVA</th>
                    <th scope="col" class="col_number">TTC</th>
                    <th scope="col" class="col_number">Kms</th>
                    <th scope="col" class="col_text">Paiements</th>
                    <th scope="col" class="col_text">Justificatifs</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
				<tr class="row_recap">
					<th scope='row' colspan='${columns - 7}' class='col_text'>Total</th>
					<td class='col_number'>${api.format_amount(total_ht)} €</td>
					<td class='col_number'>${api.format_amount(total_tva)} €</td>
					<td class='col_number'>${api.format_amount(total_ttc)} €</td>
					<td class='col_number'>${api.remove_kms_training_zeros(api.format_amount(total_km))}</td>
					<td colspan='${columns - 7}'></td>
				</tr>
        % else:
        <table class="top_align_table">
            <tbody>
            	<tr>
            		<td class="col_text">
            			<em>Aucune note de dépenses ne correspond à ces critères</em>
            		</td>
            	</tr>
        % endif
			% for id_, expense in records:
				<% url = request.route_path('/expenses/{id}', id=expense.id) %>
				<% onclick = "document.location='{url}'".format(url=url) %>
				<% tooltip_title = "Cliquer pour voir cette note de dépenses" %>
				<tr>
					<td class='col_status' title="${api.format_expense_status(expense)} - ${tooltip_title}" onclick="${onclick}">
						<span class="icon status ${expense.global_status}">
							${api.icon(api.status_icon(expense))}
						</span>
					</td>
					<td class="col_text document_number" onclick="${onclick}" title="${tooltip_title}">${expense.official_number}</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">${api.format_account(expense.user)} (${expense.company.name})</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						${api.month_name(expense.month).capitalize()} ${expense.year}
						% if expense.title:
							<br /><small>${expense.title}</small>
						% endif
					</td>
					<td class="col_number" onclick="${onclick}" title="${tooltip_title}"><strong>${api.format_amount(expense.total_ht)} €</strong></td>
					<td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(expense.total_tva)} €</td>
					<td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(expense.total, precision=2)} €</td>
					<td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.remove_kms_training_zeros(api.format_amount(expense.total_km))}</td>
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
					<td class="col_text">
						% if api.has_permission('context.set_justified_expensesheet', expense) and expense.status != 'valid':
							<div
								class="icon_choice layout flex expense-justify"
								data-toggle="buttons"
								data-href="${request.route_path('/api/v1/expenses/{id}', id=expense.id, _query={'action': 'justified_status'})}"
								>
								<label
									class="btn
									% if not expense.justified:
										active
									% endif
									"
									% if not expense.justified:
										title="En attente des justificatifs"
									% else:
										title="Changer le statut en : Justificatifs en attente"
									% endif
									>
									<input
										name="justified_${expense.id}"
										value="false"
										% if not expense.justified:
											checked="true"
										% endif
										autocomplete="off"
										type="radio"
										class="visuallyhidden">
									<span>
										${api.icon('clock')}
										<span>En attente</span>
										<span class="screen-reader-text">
											% if not expense.justified:
											 (En attente des justificatifs)
											% else:
											 (Cliquer pour changer le statut en : Justificatifs en attente)
											% endif
										</span>
									</span>
								</label>
								<label class="btn"
									% if not expense.justified:
										title="Changer le statut en : Justificatifs reçus"
									% else:
										title="Justificatifs reçus"
									% endif
									>
									<input
									name="justified_${expense.id}"
									value="true"
									% if expense.justified:
										checked="true"
									% endif
									autocomplete="off"
									type="radio"
									class="visuallyhidden">
									<span>
										${api.icon('check')}
										<span>Reçus<span>
										<span class="screen-reader-text">
											% if not expense.justified:
											 (Cliquer pour changer le statut en : Justificatifs reçus)
											% else:
											 (Justificatifs reçus)
											% endif
										</span>
									</span>
								</label>
							</div>
						% endif
					</td>
					<td
						% if api.has_permission('context.add_payment_expensesheet', expense):
						class="col_actions width_three"
						% else:
						class="col_actions width_two"
						% endif
						>
						<ul>
						% if api.has_permission('context.add_payment_expensesheet', expense):
							<li>
							<% onclick = "ExpenseList.payment_form(%s, '%s');" % (expense.id, api.format_amount(expense.topay(), grouping=False)) %>
							${table_btn('#popup-payment_form',
								"Paiement",
								"Saisir un paiement pour cette note de dépenses",
								icon='euro-circle',
								onclick=onclick)}
							</li>
						% endif
							<li>
							<% url = request.route_path('/expenses/{id}', id=expense.id) %>
							${table_btn(url, 'Modifier', "Voir cette note de dépenses", icon="arrow-right" )}
							</li>
							<li>
							<% url = request.route_path('/expenses/{id}.xlsx', id=expense.id) %>
							${table_btn(url, 'Excel', "Télécharger au format Excel", icon="file-excel" )}
							</li>
						</ul>
					</td>
				</tr>
			% endfor
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>

<%block name='footerjs'>
ExpenseList.popup_selector = "#${payment_formname}";
% for i in 'year', 'month', 'status', 'owner', 'items':
    $('#${i}-select').change(function(){$(this).closest('form').submit()});
% endfor
</%block>
