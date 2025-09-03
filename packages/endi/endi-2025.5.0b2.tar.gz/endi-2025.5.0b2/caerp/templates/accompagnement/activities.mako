<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name="actionmenucontent">
% if add_link is not None or api.has_permission('global.manage_activity'):
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
		% if add_link is not None:
		    ${request.layout_manager.render_panel(add_link.panel_name, context=add_link)}
		% endif
		% if api.has_permission('global.manage_activity'):
			<div role='group'>
				<%
				args = request.GET
				url_xlsx = request.route_path('activities.xlsx', _query=args)
				url_ods = request.route_path('activities.ods', _query=args)
				%>
				<a class='btn' href='${url_xlsx}' title="Exporter les éléments de la liste au format Excel (xlsx)" aria-label="Exporter les éléments de la liste au format Excel (xlsx)">
					${api.icon("file-excel")} Excel
				</a>
				<a class='btn' href='${url_ods}' title="Exporter les éléments de la liste au format Open Document (ods)" aria-label="Exporter les éléments de la liste au format Open Document (ods)">
					${api.icon("file-spreadsheet")} ODS
				</a>
			</div>
		% endif
	</div>
</div>
% endif
</%block>

<%block name='content'>

${searchform()}

% if last_closed_event is not UNDEFINED and last_closed_event is not None:
	<div class="content_vertical_padding">
		<h3>Dernières préconisations</h3>
		<blockquote>
			${api.clean_html(last_closed_event.action)|n}
			<footer>le ${api.format_date(last_closed_event.datetime)}</footer>
		</blockquote>
	</div>
% endif

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
					<th scope="col" class="col_datetime">${sortable("Horaire", "datetime")}</th>
					<th scope="col" class="col_text">${sortable("Accompagnateur", "conseillers")}</th>
					<th scope="col" class="col_text">Participant(s)</th>
					<th scope="col" class="col_text">Nature du Rdv</th>
					<th scope="col" class="col_text">Mode de Rdv</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
			<tbody>
		% else:
		<table>
			<tbody>
				<tr>
					<td class="col_text"><em>Aucun rendez-vous disponible</em></td>
				</tr>
		% endif
		% for activity in records:
			<% url = request.route_path('activity', id=activity.id) %>
			% if api.has_permission('context.view_activity', activity):
				% if api.has_permission('context.edit_activity', activity):
					<% tooltip_title = "Cliquer pour voir ou modifier les détails de ce rendez-vous" %>
				% else:
					<% tooltip_title = "Cliquer pour voir les détails de ce rendez-vous" %>
				% endif
				<% onclick = "document.location='{url}'".format(url=url) %>
			% else :
				<% tooltip_title = "" %>
				<% onclick= "javascript:void(0);" %>
			% endif
				<tr>
					<% status_icon = "clock" %>
					<% status_title = "Rendez-vous programmé" %>
					% if activity.status == "closed":
						<% status_icon = "check" %>
						<% status_title = "Rendez-vous terminé" %>
					% elif activity.status == "cancelled":
						<% status_icon = "times" %>
						<% status_title = "Rendez-vous annulé" %>
					% endif
					% if api.has_permission('context.view_activity', activity):
					<td class="col_status" onclick="${onclick}" title="${status_title} - ${tooltip_title}">
					% else:
					<td class="col_status" title="${status_title}">
					% endif
						<span class="icon status ${activity.status}">
							${api.icon(status_icon)}
						</span>
					</td>
					<td class="col_datetime" onclick="${onclick}" title="${tooltip_title}">
						${api.format_datetime(activity.datetime)}
					</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						<ul>
						% for conseiller in activity.conseillers:
							<li>${api.format_account(conseiller)}</li>
						% endfor
						</ul>
					</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						<ul>
						% for participant in activity.participants:
							<li>${api.format_account(participant)}</li>
						% endfor
						</ul>
					</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						% if activity.type_object is not None:
							${activity.type_object.label}
						% endif
					</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						${activity.mode}
					</td>
					<td 
						% if api.has_permission('context.edit_activity', activity):
						class="col_actions width_three"
						% else:
						class="col_actions width_one"
						% endif
						>
						% if api.has_permission('context.edit_activity', activity):
							<ul>
								<li>
									<% edit_url = request.route_path('activity', id=activity.id, _query=dict(action="edit")) %>
									${table_btn(edit_url, "Voir ou modifier", "Voir ou modifier le rendez-vous", icon='arrow-right')}
								</li>
								<li>
									<% pdf_url = request.route_path("activity.pdf", id=activity.id) %>
									${table_btn(pdf_url, "PDF", "Télécharger la fiche de rendez-vous au format PDF", icon='file-pdf')}
								</li>
								<li>
									<% del_url = request.route_path('activity', id=activity.id, _query=dict(action="delete")) %>
									${table_btn(del_url, "Supprimer", "Supprimer ce rendez-vous", icon='trash-alt', \
									onclick="return confirm('Êtes vous sûr de vouloir supprimer ce rendez-vous ?')", \
									css_class="negative", method='post')}
								</li>
							</ul>
						% else:
							${table_btn(url, "Voir", "Voir le rendez-vous", icon='arrow-right')}
						% endif
					</td>
				</tr>
			% endfor
			</tbody>
		</table>
    </div>
    ${pager(records)}
</div>
</%block>
