<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <% config = request.config %>
        <% bank_remittance = request.context %>
        <% bank_label = "<em>Non défini</em>" %>
        <% bank_office = "<em>Non défini</em>" %>
        <% bank_account_number = "<em>Non défini</em>" %>
        % if bank_remittance.bank:
            <% bank_label = bank_remittance.bank.label %>
            <% bank_office = bank_remittance.bank.rib_bank_office %>
            <% bank_account_number = bank_remittance.bank.rib_account_number %>
        % endif
        <style>
            td { font-size: 10px; }
        </style>
    </head>
    <body class="caerp pdf_export">
        <h1 style="text-align:right;">Remise en banque n° ${bank_remittance.id}</h1>
        <div style="font-size:1.1em;">
            <p>
                <strong>Banque : </strong>${bank_label | n}<br/>
                Guichet : ${bank_office | n}
            </p>
            <p>
                <strong>Titulaire du compte : </strong>${config.get('cae_business_name')}<br/>
                <strong>Numéro de compte : </strong>${bank_account_number | n}
            </p>
            <p>
                <strong>Type de remise : </strong>${api.format_paymentmode(bank_remittance.payment_mode)}<br/>
                <strong>Date de la remise : </strong>
                    % if bank_remittance.remittance_date:
                        ${api.format_date(bank_remittance.remittance_date)}
                    % endif
            </p>
        </div>
        <br/>
        <div>
            <div class="table_container">
                <table>
                    <thead>
                        <th scope="col" class="col_text" style="width:75px;">Date</th>
                        <th scope="col" class="col_text">Banque</th>
                        <th scope="col" class="col_text">Emetteur</th>
                        <th scope="col" class="col_text">N<sup>o</sup> chèque</th>
                        <th scope="col" class="col_text">Réf. facture</th>
                        <th scope="col" class="col_text">Code interne</th>
                        <th scope="col" class="col_number">Montant</th>
                    </thead>
                    <tbody>
                        % for payment in bank_remittance.get_grouped_payments():
                            <tr>
                                <td class="col_text" style="text-align:center;">${api.format_date(payment["date"])}</td>
                                <td class="col_text" style="font-size:9px;">${payment["bank_label"]}</td>
                                <td class="col_text" style="font-size:9px;">${payment["issuer"]}</td>
                                <td class="col_text">${payment["check_number"]}</td>
                                <td class="col_text">${payment["invoice_ref"]}</td>
                                <td class="col_text">${payment["code_compta"]}</td>
                                <td class="col_number">${api.format_amount(payment["amount"], precision=5)}&nbsp;€</td>
                            </tr>
                        % endfor
                    </tbody>
                    <tfoot>
                        <tr class="row_recap">
                            <th scope="col" class="col_text" colspan="6">Total de la remise</th>
                            <th scope="col" class="col_number">${api.format_amount(bank_remittance.get_total_amount(), precision=5)}&nbsp;€</th>
                        </tr>
                    </tfoot>
                </table>
                <br/>
                <p>Nombre de pièces déposées : ${len(bank_remittance.get_grouped_payments())}</p>
            </div>
        </div>
    </body>
</html>
