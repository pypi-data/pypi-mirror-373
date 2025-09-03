<%def name="render_item(elem)">
    % if elem.has_permission(_context, request, **bind_params) and elem.visible(_context, request):
        <%
        url = "#"
        active_class = "disabled"
        if elem.enabled(_context, request):
            url = elem.url(_context, request)
            active_class = ""
        if elem.selected(_context, request):
            active_class = "active"
        %>
        <li class="${active_class}">
            <a title="${elem.get_title(**bind_params)}" href="${url}">
                <span class="icon">${api.icon(elem.icon)}</span>
                <span>${elem.get_label(**bind_params)|n}</span>
            </a>
        </li>
    % endif
</%def>

<%def name="render_dropdown(elem)">
    % if elem.has_permission(_context, request, **bind_params) and elem.visible(_context, request):
        % if not elem.enabled(_context, request):
            ${render_item(elem)}
        % else:
            <%
            # défaut : menu fermé
            aria = "false"
            active_class = ""
            content_display = "hidden"
            tooltip = "Afficher le sous-menu"
            if elem.enabled(_context, request):
                # menu ouvert
                aria = "true"
                content_display = ""
                tooltip = "Masquer le sous-menu"
                if elem.selected(_context, request):
                    # menu ouvert et actif
                    active_class = "active"
            %>
            <li class="dropdown ${active_class}">
                <a href='javascript:void(0);' onclick='toggleCollapse( this );' aria-expanded='${aria}' title='${tooltip}' aria-label='${tooltip}' class='dropdown-toggle icon'>
                    <span class="icon">${api.icon(elem.icon)}</span>
                    <span>${elem.get_label(**bind_params)|n}</span>
                    ${api.icon('chevron-down','arrow')}
                </a>
                <ul class="nav subnav collapse" ${content_display}>
                % for item in elem.items:
                    ${render_item(item)}
                % endfor
                </ul>
            </li>
        % endif
    % endif
</%def>

% if menu_item.__type__ == 'dropdown':
    ${render_dropdown(menu_item)}
% else:
    ${render_item(menu_item)}
% endif
