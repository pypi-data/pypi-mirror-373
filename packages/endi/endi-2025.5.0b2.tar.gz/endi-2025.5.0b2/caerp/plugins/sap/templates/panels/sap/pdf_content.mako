<%doc>
    Attestation fiscale SAP
</%doc>
<%namespace file="caerp:templates/base/utils.mako" import="format_text" />
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="shortcut icon" href="" type="image/x-icon" />
        <meta name="description" comment="">
        <meta name="KEYWORDS" CONTENT="">
        <meta NAME="ROBOTS" CONTENT="INDEX,FOLLOW,ALL">
  </head>
  <body class='sap_attestation_view'>
      ${request.layout_manager.render_panel('sap_attestation_pdf_header', context=attestation)}
      <main class="task_view">
          <h2>Attestation destinée au centre des impôts</h2>
          <p>
              Je soussigné ${signee}, certifie que ${customer_name} a bénéficié
              de services à la personne.
          </p>
          <p>
            En ${attestation.year}, sa participation représente une somme
              totale de ${api.format_amount(attestation.amount, precision=5)} €,
              dont ${api.format_amount(attestation.cesu_amount, precision=5)} € au titre
              du CESU préfinancé.
          </p>
          <h3>Intervenant·e : ${attestation.company.name}</h3>
          <div class='row pdf_task_table'>
          	<table>
                <% prev_product_id = '' %>
				% for product_id, _lines in api.groupby(lines, 'product_id'):
				<tbody>
                        % for month, __lines in api.groupby(_lines, 'month_label'):
                            % for is_service, ___lines in api.groupby(__lines, 'is_service'):
                                <% sum_line = sum(___lines) %>
                                <tr class="${'sap_group' if prev_product_id != product_id else ''}">
                                    % if prev_product_id != product_id:
                                        <th class="col_text sap_group">
                                           ${sum_line.category}
                                        </th>
                                            % else:
                                         <td class="empty"></td>
                                    % endif
                                    <% prev_product_id = product_id %>

                                    % if loop.first:
                                        <td scope="row" class="col_text sap_month">${sum_line.month_label}</td>
                                            % else:
                                        <td class="empty"></td>
                                    % endif
                                    <td class="col_text sap_label">${sum_line.quantity_label}</td>
                                    <td class="col_number price_total">${api.format_amount(sum_line.amount, precision=5)} €</td>
                                </tr>
                            % endfor
                        % endfor
                </tbody>
                % endfor
            </table>
          </div>  <!-- row pdf_task_table -->
          <div class='pdf_spacer'><br></div>
          
          <div class='row pdf_task_table'>
          	<table>
				<tbody>
					<tr class="row_total">
						<th scope="row" colspan="3" class="col_text align_right">
							 Montant total des factures réglées en ${attestation.year} :
						</th>
						<td class='col_number price_total'>
							 ${api.format_amount(attestation.amount, precision=5)}&nbsp;€
						</td>
					</tr>
					<tr class="row_total">
						<th scope="row" colspan="3" class="col_text align_right">
							 Montant total payé en CESU préfinancés :
						</th>
						<td class='col_number price_total'>
							 ${api.format_amount(attestation.cesu_amount, precision=5)}&nbsp;€
						</td>
					</tr>
                </tbody>
            </table>
          </div>  <!-- row pdf_task_table -->

          <p>
            Les sommes perçues pour financer les services à la personne sont à déduire de la valeur indiquée précédemment.
          </p>
          <p>
            La déclaration engage la responsabilité du seul contribuable.
          </p>
          % if document_help :
          <div class='pdf_mention_block'>
            <h4>Comment déclarer ces sommes ?</h4>
            <p class="content document_help">${format_text(document_help)}</p>
          </div>
          % endif
          <div style="display: flex">
              <p class="sap_bottom_mention">
                  Fait pour valoir ce que de droit,
              </p>

              <p class="sap_bottom_signature">
                  Le ${api.format_date(attestation.updated_at)}<br />
                  ${signee}
                  % if has_signature:
                      <img src="${signature_url}" alt="signature manuscrite de ${signee}" />
                  % endif
              </p>
          </div>
      </main>
  </body>
</html>
