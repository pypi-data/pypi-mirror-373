<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="definition_list" />

<%block name='actionmenucontent'>
% if not request.is_popup:
<div class='main_toolbar action_tools'>
    <div class="layout flex main_actions">
    ${request.layout_manager.render_panel('action_buttons', links=actions)}
    </div>
</div>
% endif
</%block>

<%block name="content">
% if request.is_popup:
<div class="layout flex main_actions">
${request.layout_manager.render_panel('action_buttons', links=actions)}
</div>
% endif
<div class="limited_width width40">
    <div class='content_vertical_padding'>
    % if request.context.exported:
        <span class="icon status success">
            ${api.icon('check')}
        </span> ${money_flow_type} a été exporté vers la comptabilité
        % if hasattr(request.context, 'exports') and request.context.exports:
            <ul><br />
                % for export in request.context.exports:
                    <li>Exporté le ${api.format_datetime(export.datetime)} par
                    ${api.format_account(export.user)}</li>
                % endfor
            </ul>
        % endif
        
    % else:
        <span class="icon status neutral">
            ${api.icon('clock')}
        </span> ${money_flow_type} n’a pas encore été exporté vers la comptabilité
    % endif
    % if export_button not in (None, UNDEFINED):
            <div class='content_vertical_padding'>
                ${request.layout_manager.render_panel(export_button.panel_name, context=export_button)}
            </div>  
        % endif
    </div>
    <dl class="dl-horizontal">
    <dt>Paiement pour</dt>
    <dd>${document_number}</dd>
    </dl>
    <dl class="dl-horizontal">
        <dt>Date</dt><dd>${api.format_date(request.context.date)}</dd>
        <dt>Montant</dt><dd>${api.format_amount(request.context.amount, precision=request.context.precision)}&nbsp;&euro;</dd>
        % if hasattr(request.context, 'user'):
            <dt>Enregistré par</dt><dd>${api.format_account(request.context.user)}</dd>
        % endif
    </dl>
    <dl class="dl-horizontal">
        % if hasattr(request.context, 'bank'):
            <dt>Compte bancaire</dt>
            <dd>
                % if request.context.bank:
                    ${request.context.bank.label} (${request.context.bank.compte_cg})
                % else:
                    <em>Non renseignée</em>
                % endif
            </dd>
        % endif
        <dt>Mode de paiement</dt><dd>${request.context.mode}</dd>
        % if hasattr(request.context, 'issuer'):
            <dt>Emetteur</dt>
            <dd>
                % if request.context.issuer:
                    ${request.context.issuer}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        % endif
        % if hasattr(request.context, 'customer_bank'):
            <dt>Banque de l'émetteur</dt>
            <dd>
                % if request.context.customer_bank:
                    ${request.context.customer_bank.label}
                % else:
                    <em>Non renseignée</em>
                % endif
            </dd>
        % endif
        % if hasattr(request.context, 'bank_remittance_id'):
            % if hasattr(request.context, 'check_number'):
                ## Pour les encaissement on parle de remise
                <dt>Numéro de remise</dt>
            % else:
                ## Pour les paiements ES/frns on parle de référence
                <dt>Référence du paiement</dt>
            % endif
            <dd>
                % if request.context.bank_remittance_id:
                    ${request.context.bank_remittance_id}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        % endif
        % if hasattr(request.context, 'check_number'):
            <dt>Numéro de chèque</dt>
            <dd>
                % if request.context.check_number:
                    ${request.context.check_number}
                % else:
                    <em>Non renseigné</em>
                % endif
            </dd>
        % endif
    </dl>
    <dl class="dl-horizontal">
        % if hasattr(request.context, 'tva'):
            <dt>Tva liée</dt>
            <dd>
                % if request.context.tva:
                    ${request.context.tva.name}
                % else:
                    <em>Non renseignée</em>
                % endif
            </dd>
        % endif
    </dl>
</div>
</%block>
