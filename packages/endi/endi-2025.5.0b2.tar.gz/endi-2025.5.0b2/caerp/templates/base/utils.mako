
<%def name="esc(datas)">
    <%text>${</%text>${datas}<%text>}</%text>\
</%def>


<%def name="format_text(data, breaklines=True)">
    <%doc>
        Replace \n with br for html output
    </%doc>
    % if data is not UNDEFINED and data is not None:
        <% text = data %>
        %if breaklines:
            <% text = text.replace('\n', '<br />') %>
        % else:
            <% text = text.replace('\n', '') %>
        %endif
        ${api.clean_html(text)|n}
    %endif
</%def>


<%def name="format_customer(customer, link=True)">
    <%doc>
        Render a customer
    </%doc>
    %if customer is not UNDEFINED and customer is not None:
        % if link:
            <a href="${request.route_path('/customers/{id}', id=customer.id)}"
                title="Voir le client « ${customer.label} »"
                aria-label="Voir le client « ${customer.label} »">
        % endif
        ${customer.label}
        % if link:
            </a>
        %endif
    %endif
</%def>


<%def name="format_supplier(supplier, link=True)">
    <%doc>
        Render a supplier
    </%doc>
    %if supplier is not UNDEFINED and supplier is not None:
        % if link:
            <a href="${request.route_path('supplier', id=supplier.id)}"
                title="Voir le fournisseur « ${supplier.label} »"
                aria-label="Voir le fournisseur « ${supplier.label} »">
        % endif
        ${supplier.label}
        % if link:
            </a>
        %endif
    %endif
</%def>


<%def name="format_project(project, link=True)">
    <%doc>
        Render a project
    </%doc>
    %if project is not UNDEFINED and project is not None:
        % if link:
            <a href="${request.route_path('/projects/{id}', id=project.id)}"
                title="Voir le dossier « ${project.name} »"
                aria-label="Voir le dossier « ${project.name} »">
        % endif
        ${project.name}
        % if link:
            </a>
        % endif
    %endif
</%def>


<%def name="format_mail(mail)">
    <%doc>
        Render an email address
    </%doc>
    % if mail is not UNDEFINED and mail is not None:
        <a href="mailto:${mail}" title="Envoyer un e-mail à cette adresse" aria-label="Envoyer un e-mail à cette adresse">
            <span class="icon">
                ${api.icon('envelope')}
            </span>${mail}
        </a>
    % endif
</%def>


<%def name="format_phone(phone, phone_type)">
    <%doc>
        Render a phone with a phone link
    </%doc>
    % if phone is not UNDEFINED and phone is not None:
        <a class="phone_link" href="tel://${phone}" title="Appeler ce numéro" aria-label="Appeler ce numéro">
        % if phone_type != 'none':
            <span class="icon">
            % if phone_type == 'desk':
                ${api.icon('phone')}
            % endif
            % if phone_type == 'mobile':
                ${api.icon('mobile-alt')}
            % endif
            % if phone_type == 'fax':
                ${api.icon('fax')}
            % endif
            </span>
        % endif
        ${phone}
        </a>
    % endif
</%def>


<%def name="format_address(obj, multiline=False)">
    <% separator = '<br />' if multiline else ', ' %>
    % if obj.address:
        ${obj.address}${separator if obj.city else ''  | n}
        ${obj.zip_code} ${obj.city.upper()}
    % endif
    % if obj.country and obj.country != 'France':
        % if multiline:
            ${separator | n}${obj.country}
        % else:
            (${obj.country})
        % endif
    % endif
</%def>

<%def name="format_filelist_table(parent_node, delete=False)">
    <%doc>Format the list of attached files as an <talbe> with authorized actions</%doc>
    % if parent_node is not None and parent_node.children:
        <div class="table_container">
            <table class="hover_table">
                <thead>
                    <tr>
                        <th scope="col" class="col_text">Description</th>
                        <th scope="col" class="col_number" title="Taille du fichier">Taille<span class="screen-reader-text"> du fichier</span></th>
                        <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                    </tr>
                </thead>
                <tbody>
                    % for child in parent_node.children:
                        <% dl_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='download')) %>
                        <% file_full_description = child.label %>
                        <% edit_url = request.route_path('/files/{id}', id=child.id) %>
                        <% action_count = 1 %>
                        <% action_width = 'width_one' %>
                        % if api.has_permission('context.edit_file', child):
                            <% action_count = action_count + 1 %>
                        % endif
                        % if delete and api.has_permission('context.delete_file', child):
                            <% action_count = action_count + 1 %>
                        % endif
                        % if action_count == 2 :
                            <% action_width = 'width_two' %>
                        % elif action_count == 3 :
                            <% action_width = 'width_three' %>
                        %endif
                        <tr>
                            <td class="col_text">
                                % if api.has_permission('context.view_file', child):
                                    <a href="javascript:void(0);" onclick="window.openPopup('${dl_url}');" title="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre" aria-label="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre">${file_full_description}</a>
                                % else:
                                    ${file_full_description}
                                % endif
                            </td>
                            <td class="col_number">${api.human_readable_filesize(child.size)}</td>
                            <td class="col_actions ${action_width}">
                                <ul>
                                    <li>
                                        <a href="#!" onclick="window.openPopup('${dl_url}')" class="btn icon only" title="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre" aria-label="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre">
                                            ${api.icon("download")}
                                        </a>
                                    </li>
                                    % if api.has_permission('context.edit_file', child):
                                        <li>
                                            <a href="#!" onclick="window.openPopup('${edit_url}');" class="btn icon only" title="Modifier le fichier « ${file_full_description} » dans une nouvelle fenêtre" aria-label="Modifier le fichier « ${file_full_description} » dans une nouvelle fenêtre">
                                                ${api.icon("pen")}
                                            </a>
                                        </li>
                                    % endif
                                    % if delete and api.has_permission('context.delete_file', child):
                                        <li>
                                            <% delete_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='delete')) %>
                                            <%self:post_action_btn url="${delete_url}" icon="trash-alt" _class="btn icon only negative"
                                            title="Supprimer le fichier ${file_full_description}" aria-label="Supprimer le fichier ${file_full_description}" onclick="return confirm('Supprimer le fichier ${file_full_description} ?');">
                                            </%self:post_action_btn>
                                        </li>
                                    % endif
                                </ul>
                            </td>
                        </tr>
                    % endfor
                    % if len(parent_node.files) == 0:
                        <tr>
                            <td class="col_text" colspan="4"><em>Aucun fichier</em></td>
                        </tr>
                    % endif
                </tbody>
            </table>
        </div>
    % endif
</%def>


<%def name="format_filelist_ul(parent_node)">
    <%doc>Format the list of attached files as an <ul> without actions</%doc>
    % if parent_node is not None and parent_node.files:
        <ul class="file_list">
            % for child in parent_node.files:
                <% dl_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='download')) %>
                <% file_full_description = child.label %>
                <li>
                    % if api.has_permission('context.view_file', child):
                        <a href="javascript:void(0);" onclick="window.openPopup('${dl_url}');" title="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre" aria-label="Télécharger le fichier « ${file_full_description} » dans une nouvelle fenêtre">${file_full_description}</a>
                    % else:
                        ${file_full_description}
                    % endif
                </li>
            % endfor
        </ul>
    % endif
</%def>


<%def name="format_filetable(documents)">
    % if documents != []:
    <table class="hover_table">
        <thead>
            <th scope="col" class="col_text">Description</th>
            <th scope="col" class="col_text">Nom du fichier</th>
            <th scope="col" class="col_date">Déposé le</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </thead>
    % else:
    <table>
    % endif
        <tbody>
            % for child in documents:
                <% dl_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='download')) %>
                <% onclick = "document.location='{dl_url}'".format(dl_url=dl_url) %>
                 <% tooltip_title = "Cliquer pour voir ou modifier ce document" %>
               <tr>
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${child.description}</td>
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${child.name}</td>
                    <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(child.updated_at)}</td>
                    <% actions_col_width = "width_one" %>
                    % if api.has_permission('context.edit_file', child) and api.has_permission('context.delete_file', child):
                        <% actions_col_width = "width_three" %>
                    % elif api.has_permission('context.edit_file', child) or api.has_permission('context.delete_file', child):
                        <% actions_col_width = "width_two" %>
                    %endif
                    <td class="col_actions ${actions_col_width}">
                        % if api.has_permission('context.edit_file', child):
                            <% edit_url = request.route_path('/files/{id}', id=child.id) %>
                            ${table_btn(edit_url, "Voir ou modifier", "Voir ou modifier ce document", icon="arrow-right", css_class="icon")}
                        % endif
                        ${table_btn(dl_url, "Télécharger", "Télécharger ce document", icon="download", css_class="icon")}
                        % if api.has_permission('context.delete_file', child):
                            <% message = "Ce document sera définitivement supprimé. Êtes-vous sûr de vouloir continuer ?" %>
                            <% del_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='delete')) %>
                            ${table_btn(del_url, "Supprimer", "Supprimer ce document", icon="trash-alt", css_class='icon negative',
                                onclick="return confirm('%s')" % message)}
                        % endif
                    </td>
                </tr>
            % endfor
            % if documents == []:
                <tr><td class="col_text" tabindex='0'><em>Aucun document n’est disponible</em></td></tr>
            % endif
        </tbody>
  </table>
</%def>


<%def name="company_disabled_msg()">
    <span class="icon tag caution">${api.icon('danger')} désactivée</span>
</%def>


<%def name="company_internal_msg()">
    <span class="icon tag neutral">${api.icon('info-circle')} interne</span>
</%def>


<%def name="login_disabled_msg()">
    <span class="icon tag caution">${api.icon('lock')} désactivé</span>
</%def>


<%def name="show_tags_label(tags)">
    <br /><span class="icon tag neutral">${api.icon('tag')}
    % for tag in tags:
        ${tag.label}
    % endfor
    </span>
</%def>


<%def name="company_list_badges(company)">
    % if not company.active:
        ${company_disabled_msg()}
    % endif
    % if company.internal:
        ${company_internal_msg()}
    % endif
</%def>


<%def name="show_project_type_and_business_types_labels(project)">
    % if project.project_type.label and project.project_type.label != "Dossier classique":
        <% business_types = [business_type.label for business_type in project.business_types] %>
        <br /><span class="icon tag neutral" title="${', '.join(business_types)}">${api.icon("tag")}  ${project.project_type.label}</span>
    % endif
</%def>


<%def name="post_action_btn(url, icon=None, **tag_attrs)">
    <%doc>
    :param tag_attrs: kwargs that are translated to HTML tag properties, with the following transformations :
      - _class → class
        - underscore are converted to dashes (ex: aria_role → aria-role)
    </%doc>
    <form class="btn-container" action="${url}" method="post">
        ${csrf_hidden_input()}
        <button
            % for k, v in tag_attrs.items():
            <% k = k.replace('_class', 'class').replace('_', '-') %>
            ${k}="${v}"
            % endfor
        >
            % if icon is not None:
                ${api.icon(icon)}
            % endif
            ${caller.body()}
        </button>
    </form>
</%def>


<%def name="table_btn(href, label, title, icon=None, onclick=None, icotext=None, css_class='', method='get')">
    % if method == 'get':
        <a href='${href}'
    % else: # POST
        <form method="post" action="${href}" class="btn-container">
            ${csrf_hidden_input()}
            <button
    % endif
        class='btn icon only ${css_class}' href='${href}' title="${title}" aria-label="${label}"
        % if onclick:
            onclick="${onclick}"
        % endif
    >
    %if icotext:
        <span>${api.clean_html(icotext)|n}</span>
    % endif
    %if icon:
        ${api.icon(icon)}
    %endif
    % if method == 'get':
        </a>
    % else: #POST
            </button>
        </form>
    % endif
</%def>


<%def name="dropdown_item(href, label, title, icon=None, onclick=None, icotext=None, disable=False)">
    <li
    % if disable:
        class='disabled'
    % endif
    >
        <a href='${href}' title="${title}" aria-label="${title}"
            % if onclick:
                onclick="${onclick.replace('\n', '\\n')|n}"
            % endif
            >
            %if icotext:
                <span>${api.clean_html(icotext)|n}</span>
            % endif
            %if icon:
                ${api.icon(icon)}
            %endif
            ${label}
        </a>
    </li>
</%def>


<%def name="definition_list(items)">
    <%doc>
        render a list of elements as a definition_list
        items should be an iterator of (label, values) 2-uple
    </%doc>
    <dl class="dl-horizontal">
        % for label, value in items:
            <dt>${label}</dt>
            <dd>${value}</dd>
        % endfor
    </dl>
</%def>


<%def name="csrf_hidden_input()">
    <input type="hidden" name="csrf_token" value="${get_csrf_token()}" />
</%def>

<%def name="show_amount_or_undefined_string(limit)">
    <%doc>
        render an amount or a string message
    </%doc>
    %if limit is not None:
        ${limit} € HT
    % else:
        <em>Non précisé (pas de limite)</em>
    % endif
</%def>

<%def name="format_js_appoptions(options)">
<%doc>Render the AppOption global object definition</%doc>
var AppOption = {}
% for key, value in options.items():
% if isinstance(value, bool):
AppOption["${key}"] = ${value and 'true' or 'false'};
% elif isinstance(value, (int, float)):
AppOption["${key}"] = ${value};
% else:
AppOption["${key}"] = "${value}";
% endif
% endfor
</%def>
