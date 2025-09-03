<%doc>
	estimation panel template
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
			<h1>${api.overridable_label('estimation', task)} N<span class="screen-reader-text">umér</span><sup>o</sup> <strong>${task.internal_number}</strong></h1>
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
	<strong>Objet : </strong>${format_text(task.description)}
	% if config.get('coop_estimationheader'):
		<div class="coop_header">${format_text(config['coop_estimationheader'])}</div>
	% endif
</div>
</%block>

<%block name="notes_and_conditions">
<div class="notes_group">
	% if task.validity_duration or task.start_date or task.end_date or task.first_visit:
	<div class='pdf_mention_block options'>
	## DATE DE PREMIERE VISITE
		% if task.first_visit:
			<div class='first_visit'>
				<p class="content"><strong>${custom_labels.get('first_visit', "Date de première visite")} :</strong> le ${api.format_date(task.first_visit, False)}</p>
			</div>
		% endif
		## LIMITE DE VALIDITE DU DEVIS
		% if task.validity_duration:
			<div class='validity_duration'>
				<p class="content"><strong>${custom_labels.get('validity_duration', "Durée de validité du devis")} :</strong> ${task.validity_duration}</p>
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
## CONDITIONS DE PAIEMENT
% if task.paymentDisplay != "NONE":
	% if task.paymentDisplay == "ALL":
		<% colspan = 3 %>
	% elif task.paymentDisplay == "ALL_NO_DATE":
		<% colspan = 2 %>
	%else:
		<% colspan = 1 %>
	% endif
	<div class='pdf_mention_block payment_conditions'>
		<h4>Conditions de paiement</h4>
		<div>
			<p>
				${task.payment_conditions}<br />
				% if task.deposit > 0 :
					Un acompte, puis paiement en ${task.get_nb_payment_lines()} fois.
				%else:
					Paiement en ${task.get_nb_payment_lines()} fois.
				%endif
			</p>
			% if task.paymentDisplay in ("ALL", "ALL_NO_DATE"):
			## AFFICHAGE DU DETAIL DU PAIEMENT
			<div>
				<table class='payment_schedule'>
					<tbody>
							## L’acompte à la commande
							% if task.deposit > 0 :
								<tr>
									<td
										% if task.paymentDisplay == "ALL":
											colspan='2'
										% endif
										class='col_text'
										>Acompte à la commande</td>
									<td class='col_number price'>${task.format_amount(task.deposit_amount_ttc(), precision=5)}&nbsp;€</td>
									% if columns['tvas']:
										<td class='col_number tva'>&nbsp;</td>
									% endif
									% if columns['ttc']:
										<td class="col_number price">&nbsp;</td>
									% endif
								</tr>
							% endif
							## Les paiements intermédiaires
							% for line in task.payment_lines[:-1]:
								<tr>
									% if task.paymentDisplay == "ALL":
										<td class='col_date'>${api.format_date(line.date)}</td>
									% endif
									<td class='col_text'>${line.description}</td>
								
									<td class='col_number price'>${task.format_amount(line.amount, precision=5)}&nbsp;€</td>
		
									% if columns['tvas']:
										<td class='col_number tva'>&nbsp;</td>
									% endif
									% if columns['ttc']:
										<td class="col_number price">&nbsp;</td>
									% endif
								</tr>
							% endfor
							## Le solde (qui doit être calculé séparément pour être sûr de tomber juste)
							<tr>
								% if task.paymentDisplay == "ALL":
									<td scope='row' class='col_date'>
										${api.format_date(task.payment_lines[-1].date)}
									</td>
								% endif
								<td scope='row' class='col_text'>
									${format_text(task.payment_lines[-1].description)}
								</td>
								<td class='col_number price'>
									${task.format_amount(task.sold(), precision=5)}&nbsp;€
								</td>
								% if columns['tvas']:
									<td class='col_number tva'>&nbsp;</td>
								% endif
								% if columns['ttc']:
									<td class="col_number price">&nbsp;</td>
								% endif
							</tr>
					</tbody>
				</table>
			</div>
			% endif
		</div>
	</div>
%else:
	%if task.payment_conditions:
		${table("Conditions de paiement", task.payment_conditions)}
	% endif
% endif
</%block>

<%block name="end_document">
<div class="pdf_sign_block">
	<div class="pdf_sign_block_width">
		<h4>${api.overridable_label('signed_agreement', task)}</h4>
		%if task.internal_number:
		<p class='reference'><small>${api.overridable_label('estimation', task)} N<span class="screen-reader-text">umér</span><sup>o</sup> ${task.internal_number}</small></p>
		% endif
		<p class='date'>Le :</p>
		<p class="signature"><em>Signature</em></p>
	</div>
</div>
</%block>
