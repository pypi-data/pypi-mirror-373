<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class='row'>
    <% keys = list(datas.keys()) %>
    <% keys.sort() %>
    % for year in keys:
    <% months = datas[year] %>
    % if year in current_years:
    <% 
        section_hidden = ''
        expanded = 'true'
        tooltip = 'Masquer cette année'
    %>
    %else:
    <% 
        section_hidden = 'hidden'
        expanded = 'false'
        tooltip = 'Afficher cette année'
    %>
    %endif
    <div class='collapsible panel panel-default page-block'>
        <h2 class='collapse_title panel-heading'>
            <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded='${expanded}' title='${tooltip}' aria-label='${tooltip}'>
                <span class="icon">${api.icon('folder-open')}</span>
                ${year}
            </a>
        </h2>
        <div class='panel-body' ${section_hidden}>
            <table class="hover_table">
                <thead>
                	<tr>
						<th scope="col" class="col_text">Mois</th>
						<th scope="col" class="col_number">Nombre de fichiers</th>
						<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                	</tr>
                </thead>
                <tbody>
                <% month_names = list(months.keys()) %>
                <% month_names.sort(key=lambda m:int(m)) %>
                % for month in month_names:
                    <% month_datas = months[month] %>
                    <tr>
                        <td class="col_text">${month_datas['label']}</td>
                        <td class="col_number">${month_datas['nbfiles']} fichier(s)</td>
                        <td class="col_actions width_one">
                        	<a href="${month_datas['url']}" class="btn icon only" title="Administrer" aria-label="Administrer">
                        		${api.icon('pen')}
                        	</a>
                        </td>
                    </tr>
                % endfor
            % if not months:
                    <tr><td colspan='3' class="col_text" tabindex='0'><em>Aucun document n’est disponible</em></td></tr>
            % endif
                </tbody>
            </table>
        </div>
    </div>
    % endfor
    % if not keys:
    <div class='panel panel-default page-block'>
        <div class='panel-body' tabindex='0'><em>Aucun document n’est disponible</em></div>
    </div>
    % endif
</div>
</%block>
