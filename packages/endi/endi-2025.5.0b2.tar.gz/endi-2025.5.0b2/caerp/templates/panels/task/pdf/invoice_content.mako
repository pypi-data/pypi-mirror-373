<%doc>
	invoice panel template
</%doc>
<%inherit file="/panels/task/pdf/content.mako" />
<%namespace file="/base/utils.mako" import="format_text" />

<%def name="table(title, datas, css='')">
	<div class='pdf_mention_block'>
		<h4 class="title ${css}">${title}</h4>
		<p class='content'>${format_text(datas)}</p>
	</div>
</%def>

<%block name='information'>
<div class="pdf_information">
	<div class="info_cols">
		<div class="document_info">
			<h1>Facture N<span class="screen-reader-text">umér</span><sup>o</sup> <strong>${task.official_number}</strong></h1>
			% if task.estimation is not None:
				<strong>Facture associée au devis&nbsp;:</strong> ${task.estimation.internal_number}<br />
			% endif
		</div>
		<div class="customer_info">
			% if task.customer.registration:
				<div>
					<strong>N<span class="screen-reader-text">umér</span><sup>o</sup> d'identification&nbsp;: </strong>
					${task.customer.registration}
				</div>
			% endif
			% if task.customer.tva_intracomm:
				<div>
					<strong>N<span class="screen-reader-text">umér</span><sup>o</sup> de TVA intracommunautaire&nbsp;: </strong>
					${task.customer.tva_intracomm}
				</div>
			% endif
		</div>
	</div>
	<strong>Objet : </strong>${format_text(task.description)}<br />
	% if config.get('coop_invoiceheader'):
		<div class="coop_header">${format_text(config['coop_invoiceheader'])}</div>
	% endif
</div>
</%block>

<%block name="notes_and_conditions">
<div class="notes_group">
	% if  task.start_date or task.end_date or task.first_visit:
	<div class='pdf_mention_block options'>
		## DATE DE PREMIERE VISITE
		% if task.first_visit:
			<div class='first_visit'>
				<p class="content"><strong>${custom_labels.get('first_visit', "Date de première visite")} :</strong> le ${api.format_date(task.first_visit, False)}</p>
			</div>
		% endif	
		## DATE DE DEBUT DES PRESTATIONS
		% if task.start_date:
			<div class='start_date'>
				<p class="content"><strong>${custom_labels.get('start_date', "Date de début de prestation")} :</strong> le ${api.format_date(task.start_date, False)}</p>
			</div>
		% endif
		## DATE DE FIN DES PRESTATIONS
		% if task.end_date:
			<div class='end_date'>
				<p class="content"><strong>${custom_labels.get('end_date', "Date de fin de prestation")} :</strong> ${task.end_date}</p>
			</div>
		% endif
	</div>
	% endif
	## LIEU D’EXECUTION
	% if task.workplace:
	<div class='pdf_mention_block workplace'>
		<h4>${custom_labels.get('workplace', "Lieu d’exécution")}</h4>
		<p class="content">${format_text(task.workplace)}</p>
	</div>
	% endif
</div>
% if show_previous_invoice:
<div class='pdf_mention_block'>
	<h4 class="title">Factures émises précédemment</h4>
	<table class='payment_schedule'>
		<thead>
			<th scope='col' class='col_date'>Date</th>
			<th scope='col' class='col_text'>Numéro de facture</th>
			<th scope='col' class="col_number price">Prix HT</th>
			<th scope='col' class="col_number price">Prix TTC</th>
		</thead>
		% for invoice in task.business.invoices:
			% if invoice.id == task.id:
				<% break %>
			% else:
				<tr>
					<td class='col_date'>${api.format_date(invoice.date)}</td>
					<td class='col_text'>Facture n°${invoice.official_number}</td>
					<td class='col_number price'>${invoice.format_amount(invoice.total_ht(), precision=5)}&nbsp;€</td>
					<td class='col_number price'>${invoice.format_amount(invoice.total(), precision=5)}&nbsp;€</td>
				</tr>
			% endif		
		% endfor
	</table>
</div>
% endif
## CONDITIONS DE PAIEMENT
%if task.payment_conditions:
	${table("Conditions de paiement", task.payment_conditions)}
% endif
</%block>
