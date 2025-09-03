<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
% if check_messages is not None:
    <div class='row form-row'>
        <div class='col-md-6 col-md-offset-3'>
            <h2>${check_messages['title']}</h2>
        </div>
    </div>
    <p class='text-danger'>
    % for message in check_messages['errors']:
        <b>*</b> ${message|n}<br />
    % endfor
    </p>
    <button onclick="window.location.reload()" type='button'>
        ${api.icon('redo-alt')}
        Rafraîchir
    </button>
% endif
</%block>

