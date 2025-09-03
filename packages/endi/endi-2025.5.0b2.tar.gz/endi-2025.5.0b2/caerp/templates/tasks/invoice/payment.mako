<%inherit file="${context['main_template'].uri}" />

<%block name='mainblock'>
<div id="invoice_payments_tab">
<% invoice = request.context %>
% if invoice.paid_status != 'resulted':
            <dl class="dl-horizontal">
                <dt>Montant restant dû</dt>
                <dd>${api.format_amount(invoice.topay(), precision=5)}&nbsp;€ </dd>    
            </dl>
        % endif
        % if api.has_permission('context.add_payment_invoice'):
        <div class="content_vertical_padding">
            <a class='btn btn-primary' href="${request.route_path('/invoices/{id}/addpayment', id=invoice.id)}">
                ${api.icon('plus-circle')}
                Enregistrer un encaissement
            </a>
        </div>
        <div class="content_vertical_padding separate_top">
        % else:
        <div class="content_vertical_padding">
        % endif
            <h3>Liste des encaissements</h3>
            % if invoice.payments:
                <% total_payments = 0 %>
                <div class="table_container">
                    <table class="hover_table">
                        <thead>
                            <th scope="col" class="col_date">Date</th>
                            <th scope="col" class="col_text">Mode de règlement</th>
                            % if not invoice.internal:
                            <th scope="col" class="col_text">TVA</th>
                            <th scope="col" class="col_text">N° de remise</th>
                            % endif
                            <th scope="col" class="col_number">Montant</th>
                            <th scope="col" class="col_actions width_one" title="Actions"><span class="screen-reader-text">Actions</span></th>
                        </thead>
                        <tbody>
                            % for payment in invoice.payments:
                                <% url = request.route_path('payment', id=payment.id) %>
                                <tr>
                                    <td class="col_date">${api.format_date(payment.date)}</td>
                                    <td class="col_text">${api.format_paymentmode(payment.mode)}</td>
                                    % if not invoice.internal:
                                    <td class="col_text">
                                        % if payment.tva is not None:
                                            ${payment.tva.name}
                                        % endif
                                    </td>
                                    <td class="col_text">${payment.bank_remittance_id}</td>
                                    % endif
                                    <td class="col_number">${api.format_amount(payment.amount, precision=5)}&nbsp;€</td>
                                    <td class="col_actions width_one">
                                        <a href="${url}" class="btn icon only" title="Voir/Modifier cet encaissement" aria-label="Voir/Modifier cet encaissement">
                                            ${api.icon('arrow-right')}
                                        </a>
                                    </td>
                                </tr>
                                <% total_payments += payment.amount %>
                            % endfor
                        </tbody>
                        <tfoot>
                            <tr class="row_recap">
                                % if invoice.internal:
                                    <th scope="col" class="col_text">Total encaissé</th>
                                % else:
                                <th scope="col" class="col_text" colspan="4">Total encaissé</th>
                                % endif
                                <th scope="col" class="col_number">${api.format_amount(total_payments, precision=5)}&nbsp;€</th>
                                <th scope="col" class="col_actions width_one">&nbsp;</th>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            % else:
                <em>Aucun encaissement n’a été saisi</em>
            % endif
        </div>
        <div class="content_vertical_padding separate_top">
            <h3>Avoir(s)</h3>
            % if invoice.cancelinvoices:
                <% hasone = False %>
                <ul>
                    % for  cancelinvoice in invoice.cancelinvoices:
                        % if cancelinvoice.status == 'valid':
                            <% hasone = True %>
                            <li>
								L’avoir : \
								<a href="${api.task_url(cancelinvoice, suffix='/general')}">
									${cancelinvoice.get_short_internal_number()}
									(numéro ${cancelinvoice.official_number})
									d’un montant TTC de ${api.format_amount(cancelinvoice.ttc, precision=5)} €
								</a> a été généré depuis cette facture.
                            </li>
                        % endif
                    % endfor
                </ul>
                % if not hasone:
                    <em>Aucun avoir validé n’est associé à ce document</em>
                % endif
            % else:
                <em>Aucun avoir validé n’est associé à ce document</em>
            % endif
        </div>
    </div>
</div>
</%block>
