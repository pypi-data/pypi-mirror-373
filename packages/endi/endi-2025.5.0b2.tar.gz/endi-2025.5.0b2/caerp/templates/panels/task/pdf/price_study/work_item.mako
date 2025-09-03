<%doc>
Renders a TaskLine object
</%doc>

<%namespace file="/base/utils.mako" import="format_text" />

% for description_line in description_lines:
    % if loop.first:
        <%doc>
        La première ligne contient la première ligne de la description 
        et l'ensemble des données de facturation
        </%doc>
        <tr class='work_item'>
            <td class="col_text description rich_text">${format_text(description_line, False)}</td>
            % if columns['units']:
                <%doc>
                We display the unit ht value if :
                - we're in ht mode
                - we're in ttc mode with columns['ttc'] set to True
                </%doc>
                <td class="col_number price">${task.format_amount(unit_ht, trim=False, precision=5)}&nbsp;€</td>
                <%doc>
                Quantity can be displayed in a x b format or in classic a format, 
                quantiy formatting is handled python side
                </%doc>
                <td class="col_number quantity">${quantity|n}</td>
                <td class="col_text unity">${unity}</td>
            % endif
            <td class="col_number price_total">
                ${task.format_amount(total_ht, trim=False, precision=5)}&nbsp;€
            </td>
            % if columns['tvas']:
                <td class="col_number tva">
                </td>
            % endif
            % if columns['ttc']:
                <td class="col_number price">
                ${task.format_amount(total, trim=False, precision=5)}&nbsp;€
                </td>
            % endif
        </tr>
    % else:
        <%doc>
        Les lignes suivantes servent uniquement à afficher les autres lignes de la description
        </%doc>
        <tr class='work_item long_description'>
            <td class="col_text description rich_text">${format_text(description_line, False)}</td>
            % if columns['units'] == 1:
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