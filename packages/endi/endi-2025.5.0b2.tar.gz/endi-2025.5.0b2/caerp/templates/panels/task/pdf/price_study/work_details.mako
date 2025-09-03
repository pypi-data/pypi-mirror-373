<%namespace file="/base/utils.mako" import="format_text" />

<tbody>
% for description_line in description_lines:
    % if loop.first:
        <tr class="work_description">
            <td class='col_text description rich_text'>
            %if work.title != "":
                <h3 class="work_title">${work.title}</h3>
            % endif
            % if description_line != "":
                ${format_text(description_line, False)}
            % endif
            </td>
            % if columns['units']:
                <%doc>
                We display the unit ht value if :
                - we're in ht mode
                - we're in ttc mode with columns['ttc'] set to True
                </%doc>
                <td class="col_number price">${task.format_amount(unit_ht, trim=False, precision=5)}&nbsp;€</td>
                <td class="col_number quantity">${api.format_quantity(quantity)}</td>
                <td class="col_text unity">${unity}</td>
            % endif
            <td class="col_number price_total">
                ${task.format_amount(total_ht, trim=False, precision=5)}&nbsp;€
            </td>
            % if columns['tvas']:
                <td class="col_number tva">
                    ${task.format_amount(tva_value, precision=2)}&nbsp;%
                </td>
            % endif
            % if columns['ttc']:
                <td class="col_number price">
                ${task.format_amount(total, trim=False, precision=5)}&nbsp;€
                </td>
            % endif
        </tr>
    % else:
        <tr class='long_description'>
            <td class="col_text description rich_text">${format_text(description_line, False)}</td>
            % if columns['units']:
            <td></td>
            <td></td>
            <td></td>
            % endif
            <td></td>
            % if columns['tvas']:
            <td></td>
            % endif
            % if columns['ttc']:
            <td></td>
            % endif
        </tr>
    % endif
% endfor
</tbody>
<tbody class='lines'>
% for work_item in work.items:
${request.layout_manager.render_panel(
    'price_study_pdf_work_item',
    context=task,
    work_item=work_item,
    columns=columns,
    work=work
)}
% endfor
</tbody>