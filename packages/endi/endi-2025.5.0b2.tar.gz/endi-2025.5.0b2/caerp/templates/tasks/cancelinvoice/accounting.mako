<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
    <% cancelinvoice = request.context %>
    <% url = request.route_path('/export/treasury/invoices/{id}', id=cancelinvoice.id, _query={'force': True}) %>
    % if cancelinvoice.exported:
        <div class='content_vertical_padding'>
            <span class='icon status success'>${api.icon('check')}</span>
            Cet avoir a été exporté vers la comptabilité.
        </div>
        % if cancelinvoice.exports:
        <div class='content_vertical_padding'>
            <ul>
                % for export in cancelinvoice.exports:
                <li>Exporté le ${api.format_datetime(export.datetime)}
                par ${api.format_account(export.user)}</li>
                % endfor
            </ul>
        </div>
        % endif
        <div class='content_vertical_padding'>
            <a href="${url}" class='btn'>
                ${api.icon('file-export')}
                Forcer la génération d’écritures pour cet avoir
            </a>
        </div>
    % else:
        <div class='separate_top content_vertical_padding'>
            <span class='icon status neutral'>${api.icon('clock')}</span>
            Cet avoir n’a pas encore été exporté vers la comptabilité
        </div>
        % if api.has_permission('global.manage_accounting'):
        <div class='content_vertical_padding'>
            <a href="${url}" class='btn btn-primary'>
                ${api.icon('file-export')}
                Générer les écritures pour cet avoir
            </a>
        </div>
        % endif
    % endif
</%block>