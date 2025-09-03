<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="hover_table">
            % if records:
            <thead>
                <tr>
                    <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                    <th scope="col" class="col_text">Intitulé de la formation</th>
                    <th scope="col" class="col_text">Enseigne</th>
                    <th scope="col" class="col_text">Client</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            % endif
            <tbody>
            % if records:
                % for id_, record in records:
                    <% url = request.route_path('/businesses/{id}', id=record.id) %>
                    <% onclick = "document.location='{url}'".format(url=url) %>
                    <% tooltip_title = "Cliquer pour voir la formation « " + record.name + " »" %>
                    <tr>
                        <td class="col_status"
                        % if record.status == 'success':
                        title="Documentation complète - ${tooltip_title}"
                        % else:
                        title="Des éléménts sont manquants - ${tooltip_title}"
                        % endif
                        onclick="${onclick}"
                        >
                            <span class='icon status ${record.status}'>${api.icon(record.status)}</span>
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${record.name | n}</td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${record.project.company.full_label | n}</td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            % if record.tasks:
                                ${record.tasks[0].customer.label | n}
                            % else:
                                <em>Cette formation est vide</em>
                            % endif
                        </td>
                        <td class="col_actions width_one">
                            ${request.layout_manager.render_panel(
                              'menu_dropdown',
                              label="Actions",
                              links=stream_actions(record),
                            )}
                        </td>
                    </tr>
                % endfor
            % else:
                <tr>
                    <td colspan="4" class="col_text"><em>Aucune formation disponible</em></td>
                </tr>
            % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
