<%namespace file="/base/utils.mako" import="format_text" />

<tr>
    <td colspan="${columns['first_column_colspan']}" class='col_text label rich_text'>
        ${format_text(label)}
    </td>
    <td class='col_number price'>
        ${task.format_amount(amount, trim=False, precision=5)}&nbsp;€
    </td>
    % if columns['tvas']:
        <td class='col_number tva'>&nbsp;</td>
    % endif
    % if columns['ttc']:
        <td class="col_number price">&nbsp; </td>
    % endif
</tr>
