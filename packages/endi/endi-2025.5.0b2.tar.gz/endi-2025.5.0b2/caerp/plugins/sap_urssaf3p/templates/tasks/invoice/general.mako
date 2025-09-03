<%inherit file="/tasks/invoice/general.mako" />

<%block name='invoice_more_data'>
    <h3>
        Avance immédiate
        <img alt="Logo URSSAF" src="${request.static_url('caerp:static/svg/urssaf_logo.svg')}" width="110" height="34" />
    </h3>
    <dl class='dl-horizontal'>
        <dt>Statut</dt>
        <dd>
            % if urssaf_payment_request:
                % if urssaf_payment_request.should_watch:
                    <span class='icon status caution' title="Demande de paiement en cours, le statut peut encore être modifié">
                        ${api.icon('clock')}
                    </span>
                % else:
                    <span class='icon status valid' title="Demande de paiement terminée">
                        ${api.icon('check')}
                    </span>
                % endif
            % endif
            ${urssaf_global_status}
        </dd>
        % if urssaf_payment_request:
            % if urssaf_payment_request.urssaf_reject_message:
                <dt>Infos rejet</dt>
                <dd>
                    ${urssaf_payment_request.urssaf_reject_message}
                </dd>
            % endif
            % if urssaf_payment_request.urssaf_transfer_message:
                <dt>Infos virement</dt>
                <dd>
                    ${urssaf_payment_request.urssaf_transfer_message}
                </dd>
            % endif
        % endif
    </dl>
</%block>
