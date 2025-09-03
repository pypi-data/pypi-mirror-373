<table class="top_align_table">
	<tbody>
    
        <tr>
	        <th scope="row">Devisé ${mode_label}</th>
	        <td class="col_number">
		        ${api.format_amount(total_estimated, precision=5)}&nbsp;€
	        </td>
        </tr>
        <tr>
	        <th scope="row" title="Total Facturé ${mode_label}">Facturé ${mode_label}</th>
	        <td class="col_number">
		        ${api.format_amount(total_income, precision=5)}&nbsp;€
	        </td>
        </tr>

        % if total_expenses > 0 or total_margin != total_income:
            <tr>
                <th scope="row" title="${tooltip_msg}" aria-label="${tooltip_msg}">
                    Dépenses ${mode_label}
                    <span class="icon">${api.icon(tooltip_icon)}</span>
                </th>
                <td class="col_number">
                    ${api.format_amount(total_expenses)}&nbsp;€
                </td>
            </tr>
            <tr>
                <th scope="row">Marge ${mode_label}</th>
                <td class="col_number">
                    ${api.format_amount(total_margin, precision=5)}&nbsp;€
                </td>
            </tr>
        % endif

        <tr>
	        <th scope="row">Restant dû</th>
	        <td class="col_number">
		        ${api.format_amount(total_topay, precision=5)}&nbsp;€
	        </td>
        </tr>

    </tbody>
</table>
