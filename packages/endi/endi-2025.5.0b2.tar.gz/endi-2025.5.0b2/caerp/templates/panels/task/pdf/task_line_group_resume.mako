<%doc>
Renders a TaskLine object
</%doc>

<%namespace file="/base/utils.mako" import="format_text" />
% if title:
<table class='group_description'>
    <tbody>
        <tr>
            <td class="col_text rich_text">
                <strong>${title}</strong>
            </td>
        </tr>
    </tbody>
</table>
% endif
<table>
    <tbody class="table_head">
        <tr>
            % if columns['date']:
                <th scope="col" class="col_date date">Date de prestation</th>
            % endif
            <th scope="col" class="col_text description">Description</th>
            %if columns['units']:
                % if is_tva_on_margin_mode or (task.mode == 'ttc' and columns['ttc']):
                    <th scope="col" class="col_number price" title="Prix Unitaire">Prix Unit<span class="screen-reader-text">aire</span></th>
                % else:
                    <th scope="col" class="col_number price" title="Prix Unitaire Hors Taxes">P<span class="screen-reader-text">rix</span> U<span class="screen-reader-text">nitaire</span> H<span class="screen-reader-text">ors </span>T<span class="screen-reader-text">axes</span></th>
                % endif
                <th scope="col" class="col_number quantity" title="Quantité">Q<span class="screen-reader-text">uanti</span>té</th>
                <th scope="col" class="col_text unity">Unité</th>
            % endif
            % if is_tva_on_margin_mode:
                <th scope="col" class="col_number price_total">Prix</th>
            % else:
                <th scope="col" class="col_number price_total">Prix HT</th>
            % endif
            % if columns['tvas']:
                % if tva is not None:
                    <th scope="col" class='col_number tva' title="Taux de TVA"><span class="screen-reader-text">Taux de </span>Tva</th>
                % else:
                    <%doc> Ici on a plusieurs tva dans le produit composé mais on a masqué le détail </%doc>
                    <th scope="col" class='col_number tva' title="Taux de TVA"><span class="screen-reader-text">Taux de </span>Tva</th>
                % endif
            % endif 
            % if columns['ttc']:
                <th scope="col" class='col_number price'>Prix TTC</th>
            % endif
        </tr>
    </tbody>
    <tbody class="lines">
    % for description_line in description_lines:
        % if loop.first:
            <tr>
                <td class="col_text description rich_text">${format_text(description_line, False)}</td>
            % if columns['units']:
                <%doc>
                We display the unit ht value if :
                - we're in ht mode
                - we're in ttc mode with columns['ttc'] set to False
                </%doc>
                <td class="col_number price">${task.format_amount(unit_ht, trim=False, precision=5)}&nbsp;€</td>
                <td class="col_number quantity">${api.format_quantity(quantity)}</td>
                <td class="col_text unity">${unity}</td>
            % endif
                <td class="col_number price_total">
                    % if is_tva_on_margin_mode:
                        ${task.format_amount(total, trim=False, precision=5)}&nbsp;€
                    % else:
                        ${task.format_amount(total_ht, trim=False, precision=5)}&nbsp;€
                    % endif
                </td>
            % if columns['tvas']:
                <td class='col_number tva'>
                % if tva is not None:
                    ${task.format_amount(tva, precision=2)}&nbsp;%
                % else:
                    &nbsp;
                % endif
                </td>
            % endif
            % if columns['ttc']:
                <td class="col_number price">${task.format_amount(total, trim=False, precision=5)}&nbsp;€</td>
            % endif
            </tr>
        % else:
            <tr class='long_description'>
                <td class="col_text description rich_text">${format_text(description_line, False)}</td>
            % if columns['units']:
                <td class="col_number price"></td>
                <td class="col_number quantity"></td>
                <td class="col_text unity"></td>
            % endif
                <td class="col_number price_total"></td>
            % if columns['tvas']:
                    <td class="col_number tva"></td>
            % endif
            % if columns['ttc']:
                    <td class="col_number price"></td>
            % endif
            </tr>
        % endif
    % endfor
% if display_subtotal:
            <tr>
                <th scope="row" colspan='${columns['first_column_colspan']}' class='col_text align_right'>
                    % if columns['ttc'] or is_tva_on_margin_mode:
                        Sous-total
                    % else:
                        Sous-total HT
                    % endif
                </th>
                <th class='col_number price_total'>
                    % if is_tva_on_margin_mode:
                        ${task.format_amount(group.total_ttc(), trim=False, precision=5)}&nbsp;€
                    % else:
                        ${task.format_amount(group.total_ht(), trim=False, precision=5)}&nbsp;€
                    % endif
                </th>
                % if columns['tvas']:
                    <th class='col_number tva'>
                    &nbsp;
                    </th>
                % endif
                % if columns['ttc']:
                    <th class='col_number price'>
                        ${task.format_amount(group.total_ttc(), trim=False, precision=5)}&nbsp;€
                    </th>
                % endif
            </tr>
        <%doc>Ici on ne ferme pas le tableau, ce qui sera fait plus tard dans le template parent </%doc>
        </tbody>
    </table>
% endif
