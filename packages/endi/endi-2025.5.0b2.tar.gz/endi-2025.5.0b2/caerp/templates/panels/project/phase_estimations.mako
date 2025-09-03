<div class='header'>
    <h4>Devis</h4>
</div>

<div class="separate_bottom">
    <div class="table_container">
        <table class='hover_table'>
            % if estimations:
            <thead>
                <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                <th scope="col" class="col_text">Nom</th>
                <th scope="col" class="col_text">État</th>
                <th scope="col" class="col_text">Fichiers attachés</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
           <tbody>
                % if estimations:
                    % for estimation in estimations:
                        <% url = request.route_path('/estimations/{id}', id=estimation.id) %>
		                <% onclick = "document.location='{url}'".format(url=url) %>
                		<% tooltip_title = "Cliquer pour voir le devis « " + estimation.name + " »" %>
                        <tr>
                            <td class="col_status" title="${api.format_estimation_status(estimation)} - ${tooltip_title}" onclick="${onclick}">
                                <span class="icon status ${estimation.global_status}">
                                	${api.icon(api.status_icon(estimation))} 
                                </span>
                            </td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${estimation.name}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${api.format_status(estimation)}</td>
                            <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            % if estimation.invoices:
								<ul>
								% for invoice in estimation.invoices:
									<li>
										Facture ${invoice.name}
										% if invoice.official_number:
											&nbsp;(${invoice.official_number})
										% endif
									</li>
								% endfor
								</ul>
                            % endif
                            </td>
                            <td class="col_actions width_one">
                                ${request.layout_manager.render_panel(
                                  'menu_dropdown',
                                  label="Actions",
                                  links=stream_actions(request, estimation),
                                )}
                            </td>
                        </tr>
                    % endfor
                %else:
                    <tr>
                        <td colspan="5" class="col_text"><em>Aucun devis n’a été créé</em></td>
                    </tr>
                % endif
            </tbody>
            % if api.has_permission('context.add_estimation'):
                <tfoot>
                    <td colspan="5" class='col_actions'>
                        <a class='btn' href="${add_url}">
                            ${api.icon('plus')} 
                            Créer un devis
                        </a>
                    </td>
                </tfoot>
            % endif
        </table>
    </div>
</div>
