<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/utils.mako" import="show_project_type_and_business_types_labels"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if api.has_permission('context.add_project'):
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
		<a class='btn btn-primary' href="${add_url}">
			${api.icon("plus")} 
			Ajouter un dossier
		</a>
	</div>
</div>
% endif
</%block>

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
					<th scope="col" class="col_date">${sortable("Utilisé en dernier le", "max_date")}</th>
					<th scope="col" class="col_date">${sortable("Créé le", "created_at")}</th>
					<th scope="col">${sortable("Code", "code")}</th>
					<th scope="col" class="col_text">${sortable("Nom", "name")}</th>
					<th scope="col" class="col_text">Clients</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
			<tbody>
		% else:
		<table>
			<tbody>
				<tr>
					<td class='col_text'><em>Aucun dossier ne correspond à ces critères</em></td>
				</tr>
		% endif
			% for project in records:
				<tr class='tableelement' id="${project.id}">
					<% url = request.route_path("/projects/{id}", id=project.id) %>
					<% onclick = "document.location='{url}'".format(url=url) %>
					<% tooltip_title = "Cliquer pour voir ou modifier le dossier « " + project.name + " »" %>
					<td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(stream_max_date(project))}</td>

					<td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(project.created_at)}</td>
					<td onclick="${onclick}" title="${tooltip_title}">${project.code}</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						${project.name}
						% if project.archived:
							<br><small title="Ce dossier a été archivé"><span class='icon'>${api.icon("archive")} Dossier archivé</span></small><br />
						% endif
						${show_project_type_and_business_types_labels(project)}
						% if project.mode == "ttc":
							<br><span class="icon tag neutral">${api.icon("mode-ttc")} Mode TTC</span>
						%endif
					</td>
					<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
						% if len(project.customers) < 6:
							${', '.join((customer.label for customer in project.customers))}
						% else:
							${project.customers[0].label}, 
							${project.customers[1].label}, 
							${project.customers[2].label} 
							et ${len(project.customers)-3} autres clients
						% endif
					</td>
					<td class='col_actions width_one'>
						${request.layout_manager.render_panel(
                          'menu_dropdown',
                          label="Actions",
                          links=stream_actions(project),
                        )}
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
