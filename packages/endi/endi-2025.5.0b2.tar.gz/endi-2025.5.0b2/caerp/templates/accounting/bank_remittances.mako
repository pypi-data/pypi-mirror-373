<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        % if records:
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col" class="col_text" title="Numéro de remise">${sortable("Remise", "id")}</th>
                    <th scope="col" class="col_date">${sortable("Créée le", "created_at")}</th>
                    <th scope="col" class="col_text" title="Mode de paiement">Mode<span class="screen-reader-text"> de paiement</span></th>
                    <th scope="col" class="col_text no_mobile">Compte bancaire</th>
                    <th scope="col" class="col_number"><span class="screen-reader-text">Nombre d'</span>Encaissements</th>
                    <th scope="col" class="col_number">Montant total</th>
                    <th scope="col" class="col_date" title="Date de dépôt">${sortable("Dépôt", "remittance_date")}</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
        % else:
        <table>
        	<tbody>
				<tr>
					<td class="col_text">
						<em>Aucune remise en banque enregistrée</em>
					</td>
				</tr>
        % endif
            <tbody>
				% for bank_remittance in records:
					<% url = request.route_path("/accounting/bank_remittances/{id}", id=bank_remittance.id) %>
					<% onclick = "document.location='{url}'".format(url=url) %>
					<% tooltip_title = "Cliquer pour voir ou modifier la remise « " + bank_remittance.id + " »" %>
					<% bank_label = "<em>Non défini</em>" %>
					% if bank_remittance.bank:
						<% bank_label = bank_remittance.bank.label %>
					% endif
					<tr class='tableelement' id="${bank_remittance.id}">
						% if bank_remittance.closed:
							<% status = "valid" %>
							<% status_label = "Remise clôturée" %>
							<% status_icon = "lock" %>
						% else:
							<% status = "wait" %>
							<% status_label = "Remise ouverte" %>
							<% status_icon = "lock-open" %>
						% endif
						<td class="col_status" onclick="${onclick}" title="${status_label} - ${tooltip_title}" >
							<span class="icon status ${status}">
								${api.icon(status_icon)}
							</span>
						</td>
						<td class="col_text" onclick="${onclick}" title="${tooltip_title}" >${bank_remittance.id}</td>
						<td class="col_date" onclick="${onclick}" title="${tooltip_title}" >${api.format_date(bank_remittance.created_at)}</td>
						<td class="col_text" onclick="${onclick}" title="${tooltip_title}" >${api.format_paymentmode(bank_remittance.payment_mode)}</td>
						<td class="col_text no_mobile" onclick="${onclick}" title="${tooltip_title}">${bank_label | n}</td>
						<td class="col_number" onclick="${onclick}" title="${tooltip_title}" >${len(bank_remittance.payments)}</td>
						<td class="col_number" onclick="${onclick}" title="${tooltip_title}" >${api.format_amount(bank_remittance.get_total_amount(), precision=5)}&nbsp;€</td>
						<td class="col_date" onclick="${onclick}" title="${tooltip_title}" >${api.format_date(bank_remittance.remittance_date)}</td>
						<td class="col_actions width_one">
							<a href="${url}" class="btn icon only" title="Voir ou modifier cette remise" aria-label="Voir ou modifier cette remise">
								${api.icon('arrow-right')} 
							</a>
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
$(function(){
    $('input[name=search]').focus();
});
</%block>
