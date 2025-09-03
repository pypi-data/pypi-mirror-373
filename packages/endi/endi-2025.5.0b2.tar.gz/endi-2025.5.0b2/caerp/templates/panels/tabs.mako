<ul class="nav nav-tabs" role="tablist" aria-label="Onglets">
    % for menu_item in menu.items:
        ${request.layout_manager.render_panel('tabs_item', context=current, menu_item=menu_item, bind_params=menu.bind_params)}
    % endfor
</ul>