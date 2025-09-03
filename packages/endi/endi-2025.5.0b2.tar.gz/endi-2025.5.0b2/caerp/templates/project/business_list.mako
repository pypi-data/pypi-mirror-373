<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if api.has_permission("context.edit_project", layout.current_project_object):
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
	    <div role='group'>
	        <a class='btn btn-primary icon' href="${layout.edit_url}">
	            ${api.icon("pen")}
	            Modifier le dossier
	        </a>
	    </div>
	</div>
</div>
% endif
</%block>

<%block name='mainblock'>

${searchform()}
<div id="project_businesses_tab">
	% if api.has_permission('context.add_estimation') or api.has_permission('context.add_invoice'):
	<div class='content_vertical_padding separate_bottom_dashed'>
		% if api.has_permission('context.add_estimation'):
			<a class='btn btn-primary icon' href='${add_estimation_url}'>
				${api.icon('file-list')} Créer un devis
			</a>
		% endif
		% if api.has_permission('context.add_invoice'):
			<a class='btn btn-primary icon' href='${add_invoice_url}'>
				${api.icon('file-invoice-euro')} Créer une facture
			</a>
		% endif
	</div>
	% endif
    <div>
    	${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
		% if records:
		<table class="top_align_table hover_table">
			<thead>
				<tr>
					<th scope="col" class="col_date">${sortable("Créé le", "created_at")}</th>
					<th scope="col" class="col_text">${sortable("Nom", "name")}</th>
					<th scope="col" class="col_text">Documents</th>
					<th scope="col" class="col_number">CA ${tva_display_mode.upper()}</th>
                    <th scope="col" class="col_number">Marge ${tva_display_mode.upper()}</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
			<tbody>
		% else:
		<table class="top_align_table">
			<tbody>
				<tr>
					<td class="col_text"><em>Aucune affaire n’a été initiée pour l’instant</em></td>
				</tr>
		% endif
			% for id, business in records:
				<% url = request.route_path("/businesses/{id}", id=business.id) %>
				<% onclick = "document.location='{url}'".format(url=url) %>
				<% tooltip_title = "Cliquer pour voir ou modifier l’affaire « " + business.name + " »" %>
				<tr class='tableelement business-check-${business.file_requirement_service.get_status(business)}' onclick="${onclick}" title="${tooltip_title}">
					<td class="col_date">${api.format_date(business.created_at)}</td>
					<td class="col_text">${business.name}</td>
					<td class="col_text">
						<ul>
							% for estimation in business.estimations:
								<li>Devis : ${estimation.name}</li>
							% endfor
							% for invoice in business.invoices:
								<li>${api.format_task_type(invoice)}
									% if invoice.official_number:
										n<span class="screen-reader-text">umér</span><sup>o</sup> ${invoice.official_number}
									% endif
									: ${invoice.name}
								</li>
							% endfor
						</ul>
					</td>
					<td  onclick="${onclick}" class="col_number">
						${api.format_amount(business.get_total_income(column_name=tva_display_mode), precision=5)}&nbsp;€
					</td>
					<td onclick="${onclick}" class="col_number">
						${api.format_amount(business.get_total_margin(tva_on_margin=tva_on_margin), precision=5)}&nbsp;€
					</td>
					<td class='col_actions width_one'>
					   <a class='btn icon only' href="${request.route_path('/businesses/{id}', id=business.id)}" title="Voir ou modifier cette affaire" aria-label="Voir ou modifier cette affaire">
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
