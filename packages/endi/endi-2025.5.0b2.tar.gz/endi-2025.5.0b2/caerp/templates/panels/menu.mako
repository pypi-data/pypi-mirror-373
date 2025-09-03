<%def name="render_item(elem)">
    <li
    % if elem['selected']:
        class="current_item"
    % endif
    >
    % if elem.get("title"):
        <a title='${elem.get("title")}' aria-label='${elem.get("title")}' href="${elem.get('href')}">
    % else:
        <a href="${elem.get('href')}">
    % endif
            ${elem.get('label', "")}
        </a>
    </li>
</%def>

<%def name="render_subitem(elem)">
    <li
    % if elem['selected']:
        class="current_item"
    % endif
    >
    % if elem.get("title"):
        <a title='${elem.get("title")}' aria-label='${elem.get("title")}' href="${elem.get('href')}">
    % else:
        <a href="${elem.get('href')}">
    % endif
            ${elem.get('label', "")}
            % if elem.get('icon'):
                <span class="icon">${api.icon(elem['icon'])}</span>
            % endif
        </a>
    </li>
</%def>

<%def name="render_static(elem)">
    ${elem['html']|n}
</%def>

<%def name="render_dropdown(elem)">
    <li>
        <button class="icon" onclick="toggleMenu( this );" aria-expanded="false" title="Afficher le sous-menu ${elem.get('label', '')}">
            ${elem.get('label', '')}
            ${api.icon('chevron-down','menu_arrow')}
        </button>
        <ul>
            % for item in elem['items']:
                % if item['__type__'] == 'item':
                    ${render_subitem(item)}
                % elif item['__type__'] == 'static':
                    ${render_static(item)}
                % endif
            % endfor
        </ul>
    </li>
</%def>

% if usermenu is not UNDEFINED:
    <div class="user_menu">
        <div class="layout flex" id="user_menu_wrapper">
            <span class="user_avatar">
                % if request.identity.photo_file:
                    <img src="${api.img_url(request.identity.photo_file)}" 
                        title="${api.format_account(request.identity)}" 
                        alt="Photo de ${api.format_account(request.identity)}" 
                        width="256" height="256" />
                % else:
                    ${api.icon('user')}
                % endif
            </span>
            <button class="icon edit" id="user_menu_display_btn" onclick="toggleOpen( this.parentNode, this );" title="Afficher le menu utilisateur" aria-label="Afficher le menu utilisateur" aria-expanded="false" accesskey="U">
                ${request.identity.lastname} ${request.identity.firstname}
                ${api.icon('chevron-down','menu_arrow')}
            </button>
        </div>
        <nav id="user_menu" role="navigation" tabindex="-1" aria-labelledby="user_menu_title">
            <h2 id="user_menu_title" class="screen-reader-text">Menu utilisateur</h2>
            <ul>
                % for item in usermenu['items']:
                    % if item['__type__'] == 'item':
                        ${render_subitem(item)}
                    % elif item['__type__'] == 'static':
                        ${render_static(item)}
                    % endif
                % endfor
            </ul>
        </nav>
    </div>
% endif

% if menu is not UNDEFINED and menu is not None:
    <nav id="target_menu" role="navigation" tabindex="-1" accesskey="M" aria-labelledby="target_menu_title">
        <h2 id="target_menu_title" class="screen-reader-text">Menu principal</h2>
        <ul
        % if hasattr(elem, "css"):
            class="single_menu ${menu_css}"
        % else:
            class="single_menu"
        % endif
        >
            % for item in menu['items']:
                % if item['__type__'] == 'item':
                    ${render_item(item)}
                % elif item['__type__'] == 'static':
                    ${render_static(item)}
                % elif item['__type__'] == 'dropdown':
                    ${render_dropdown(item)}
                % endif
            % endfor
        </ul>
    </nav>
% endif

% if submenu is not UNDEFINED:
    <nav id="target_submenu" role="navigation" tabindex="-1" aria-labelledby="target_submenu_title">
        <h2 id="target_submenu_title" class="screen-reader-text">Menu de l’enseigne</h2>
        <ul
        % if hasattr(elem, "css"):
            class="single_menu ${submenu.css}"
        % else:
            class="single_menu"
        % endif
        >
            % for item in submenu['items']:
                % if item['__type__'] == 'item':
                    ${render_item(item)}
                % elif item['__type__'] == 'static':
                    ${render_static(item)}
                % elif item['__type__'] == 'dropdown':
                    ${render_dropdown(item)}
                % endif
            % endfor
        </ul>
    </nav>
% endif
