<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn" />
<%block name="mainblock">
    <ul>
        % for template in templates:
        <% url=request.current_route_path(_query=dict(template_id=template.id)) %>
            <li>
                <a href="${url}" class="icon">
                    ${api.icon('file-alt')}
                    ${template.description} (${template.name})
                </a>
            </li>
            % endfor
    </ul>
    % if templates == []:
    <div class='alert alert-info'>
        <span class="icon">${api.icon('info-circle')}</span>
        Vous devez déposer des modèles de document dans enDI pour pouvoir accéder à cet outil.
    </div>
    % endif
    % if api.has_permission('global.config_userdatas'):
    <div class='actions'>
        <a class='btn' href="${admin_url}">
            ${api.icon('plus')}
            Déposer un nouveau modèle de document
        </a>
    </div>
    % endif
    <div class='separate_top content_vertical_padding'>
        <h4>Documents générés depuis enDI</h4>
        <div class='alert alert-info'>
            <span class="icon">${api.icon('info-circle')}</span>
            Chaque fois qu’un utilisateur génère un document depuis cette page, une entrée est ajoutée à
            l’historique.<br />
            Si nécessaire, pour rendre plus pertinente cette liste, vous pouvez supprimer certaines entrées.
            </span>
        </div>
    </div>

    <div class='table_container'>
        <table class='hover_table'>
            <thead>
                <th scope="col" class="col_text">Nom du document</th>
                <th scope="col" class="col_text">Généré par</th>
                <th scope="col" class="col_date">Date</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            <tbody>
                % if template_history is not UNDEFINED and template_history:
                % for history in template_history:
                % if history.template is not None:
                <tr>
                    <td class="col_text">${history.template.description}</td>
                    <td class="col_text">${api.format_account(history.user)}</td>
                    <td class="col_text">${api.format_datetime(history.created_at)}</td>
                    ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(history))}
                </tr>
                % endif
                % endfor
                % else:
                <tr>
                    <td colspan='4' class="col_text"><em>Aucun document n’a été généré</em></td>
                </tr>
                % endif
            </tbody>
        </table>
    </div>
</%block>