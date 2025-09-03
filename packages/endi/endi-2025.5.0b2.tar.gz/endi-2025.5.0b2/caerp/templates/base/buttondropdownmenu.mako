% if elem.items:
    <div class="btn-group" role='group'>
        <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
            % if elem.icon:
                ${api.icon(elem.icon)}&nbsp;
            % endif
            ${elem.name}&nbsp;
            ${api.icon('chevron-down','menu_arrow')}
        </button>
        <ul class="dropdown-menu" role="menu">
            % for item in elem.items:
                % if item.permitted(request.context, request):
                    <li>${item.render(request)|n}</li>
                % endif
            % endfor
        </ul>
    </div>
% endif
