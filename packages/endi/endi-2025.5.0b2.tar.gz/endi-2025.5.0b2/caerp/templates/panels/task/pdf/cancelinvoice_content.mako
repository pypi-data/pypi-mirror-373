<%doc>
	cancel invoice panel template
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
			<h1>Avoir N<span class="screen-reader-text">umér</span><sup>o</sup> <strong>${task.official_number}</strong></h1>
		% if task.invoice:
			<strong>Référence&nbsp;:</strong> Facture N<span class="screen-reader-text">umér</span><sup>o</sup> ${task.invoice.official_number}
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
	<strong>Objet : </strong>${format_text(task.description)}
</div>
</%block>

<%block name="notes_and_conditions">
## CONDITIONS DE REMBOURSEMENT
%if task.payment_conditions:
	${table("Conditions de remboursement", task.payment_conditions)}
% endif
## MODE DE REMBOURSEMENT
% if 'coop_reimbursement' in config:
	${table("Mode de remboursement", config['coop_reimbursement'])}
%endif
</%block>
