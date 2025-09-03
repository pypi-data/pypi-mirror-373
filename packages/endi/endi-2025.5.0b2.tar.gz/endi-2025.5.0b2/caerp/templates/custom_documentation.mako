<%inherit file="${context['main_template'].uri}" />

% if api.has_permission('global.config_cae'):
<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
	<div class='layout flex main_actions'>
	  <a class='btn btn-primary' icon='plus' href='${request.route_path("custom_documentation_create")}'>
	 	  ${api.icon('plus')}
	   	Ajouter une documentation
	 	</a>
	</div>
</div>
</%block>
% endif

<%block name='content'>
<div class="limited_width width40">
  <h2>Documents déposés dans enDI</h2>
  <div class="table_container">
    % if records.count() == 0:
		<table>
		  <tbody>
		    <tr>
		      <td class="col_text">
		      	<em>Aucune documentation n’a été déposée</em>
		      </td>
		    </tr>
	    </tbody>
	  </table>
  	% else:
		<table class="hover_table">
		  <thead>
				<tr>
				  <th scope="col" class="col_icon" title="Type de ressource">Type<span class="screen-reader-text"> de ressource</span></th>
				  <th scope="col" class="col_text"> Description</th>
				  <th scope="col" class="col_date"> Déposé le</th>
				  % if api.has_permission('global.config_cae'):
		      <th scope="col" class="col_actions width_two" title="Actions">
						<span class="screen-reader-text">Actions</span>
				  </th>
				  % endif
				</tr>
		  </thead>
		  <tbody>
	      % for r in records:
	      % if r.document:
				<tr onclick="javascript:void(0);" title="Télécharger le fichier «&nbsp;${r.title}&nbsp;»">
				  <td class="col_icon col_status" title="Fichier ${r.document.mimetype} de ${api.human_readable_filesize(r.document.size)}">
						<span class="icon">${api.icon('file-pdf')}</span>
						<span class="screen-reader-text">Fichier ${r.document.mimetype} de ${api.human_readable_filesize(r.document.size)}</span>
				  </td>
				  <td class="col_text">
				  	<a href="${api.file_url(r.document)}?action=download;">${r.title}</a>
				  </td>
				  <td class="col_date">
				  	${api.format_date(r.updated_at)}
				  </td>
				  % if api.has_permission('global.config_cae'):
		        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(r))}
		      % endif
				</tr>
	      % else:
		    <tr onclick="javascript:void(0);" title="Voir le lien externe «&nbsp;${r.title}&nbsp;»">
				  <td class="col_icon col_status" title="Lien externe">
						<span class="icon">${api.icon('globe')}</span>
						<span class="screen-reader-text">Lien externe</span>
					</td>
					<td class="col_text">
						<a href="${r.uri}" target="_blank" title="Ce lien s’ouvrira dans une nouvelle fenêtre" aria-label="Ce lien s’ouvrira dans une nouvelle fenêtre">${r.title}</a>
					</td>
					<td class="col_date">
						${api.format_date(r.updated_at)}
					</td>
					% if api.has_permission('global.config_cae'):
			      ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(r))}
			    % endif
				</tr>
	      % endif
	      % endfor
		  </tbody>
		</table>
  % endif
  </div>
</div>
</%block>
