<div class='dash_elem'>
    <h2>
		<span class='icon'>${api.icon('chalkboard-teacher')}</span>
		<span>${title}</span>
    </h2>
    <div class='panel-body'>
        % if len(workshops) > 0:
            <p style="display: none;">
                Afficher <select id='number_of_workshops'>
                % for i in (5, 10, 15, 50):
                    <option value='${i}'
                    % if workshops.items_per_page == i:
                        selected=true
                    % endif
                    >
                        ${i}
                    </option>
                % endfor
                </select>
                éléments à la fois
            </p>
            <table class='hover_table'>
                <thead>
                    <th scope="col" class="col_date">Date</th>
                    <th scope="col" class="col_text">Intitulé</th>
                </thead>
                <tbody>
                    % for workshop in workshops:
                        <% url = request.route_path('workshop', id=workshop.id) %>
                        <% onclick = "document.location='{url}'".format(url=url) %>
                        <tr title="Cliquer pour voir le détail de l’atelier">
                            <td class="col_date" onclick="${onclick}">
                                ${api.format_datetime(workshop.datetime, with_linebreak=True)|n}
                            </td>
                            <td class="col_text">
                                <a href="${url}">${workshop.name}</a>
                            </td>
                        </tr>
                    % endfor
                </tbody>
            </table>
        % else:
            <div class="align_center content_vertical_double_padding"><em>Aucun atelier à venir</em></div>
        % endif
    </div>
</div>
