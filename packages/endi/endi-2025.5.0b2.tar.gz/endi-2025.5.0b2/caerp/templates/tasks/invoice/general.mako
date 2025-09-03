<%inherit file="/tasks/general.mako" />

<%block name='before_summary'>
<div id="task_general_tab">

    <% invoice=request.context %>
        <div class="separate_bottom content_vertical_padding">
            % if invoice.estimation:
            <h4>
                Devis de référence :
                <a href="${api.task_url(invoice.estimation, suffix='/general')}">
                    ${invoice.estimation.get_short_internal_number()}
                </a>
            </h4>
            % endif
            <div class='alert'>
                Cette facture est rattachée à l’année fiscale ${invoice.financial_year}
                % if api.has_permission('context.set_treasury_invoice'):
                <a href="${api.task_url(invoice, suffix='/set_treasury')}" class="btn icon unstyled"
                    title="Modifier l’année fiscale" aria-label="Modifier l’année fiscale">
                    ${api.icon('pen')}
                    Modifier
                </a>
                % endif
            </div>
        </div>
        % if invoice.cancelinvoices:
        <div class="separate_bottom">
            <ul>
                % for cancelinvoice in invoice.cancelinvoices:
                <li>
                    L’avoir (${api.format_cancelinvoice_status(cancelinvoice, full=False)}): \
                    <a href="${api.task_url(cancelinvoice)}">
                        L'avoir ${cancelinvoice.name}
                        % if cancelinvoice.official_number:
                        &nbsp;<small>( ${cancelinvoice.official_number} )</small>
                        % endif
                    </a> a été généré depuis cette facture.
                </li>
                % endfor
            </ul>
        </div>
        % endif
</div>
</%block>
<%block name='after_summary'>
    <% invoice = request.context %>
    
    % if invoice.paid_status != 'resulted':
        <dl class="dl-horizontal">
            <dt>Montant restant dû</dt>
            <dd class="topay">${api.format_amount(invoice.topay(), precision=5)}&nbsp;€ </dd>    
        </dl>
    % endif
    
    % if invoice.internal and \
        invoice.supplier_invoice and \
        api.has_permission('company.view', invoice.supplier_invoice):
    <dl class='dl-horizontal'>
        <dt>Facture interne</dt>
        <dd>
            <a href='${request.route_path("/supplier_invoices/{id}", id=invoice.supplier_invoice_id)}' title="Voir la facture fournisseur" aria-label="Voir la facture fournisseur">
                Voir la facture fournisseur associée
            </a>
        </dd>
    </dl>
    % endif
    % if hasattr(next, 'invoice_more_data'):
        ${next.invoice_more_data()}
    % endif
</%block>
