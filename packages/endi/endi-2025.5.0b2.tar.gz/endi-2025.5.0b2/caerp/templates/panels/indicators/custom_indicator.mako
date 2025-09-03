<tr>
	<td class="col_status" 
	title="${api.format_indicator_main_status(indicator)}" 
	aria-label="${api.format_indicator_main_status(indicator)}"
	>
		<span class='icon status ${api.indicator_status_css(indicator.main_status)}'>
			${api.icon(api.indicator_status_icon(indicator.main_status))}
		</span>
	</td>
	<td class="col_icon col_status"
        title="Cet indicateur est requis pour clôturer l'affaire"
        aria-label="Cet indicateur est requis pour clôturer l'affaire"
    >
		<span class="icon">
			${api.icon(api.custom_indicator_icon(indicator.name))}
		</span>
	</td>
	<td class="col_text">
    ${indicator.label}
    % if indicator.forced:
        <em>Cet indicateur a été forcé manuellement</em>
    % endif
	</td>
	<td class="col_actions width_two">
    % if api.has_permission('context.force_indicator', indicator):
		<a
			href="${force_url}"
			class='btn icon only negative'
			% if not indicator.forced:
			onclick="return confirm('Êtes-vous sûr de vouloir forcer cet indicateur (il apparaîtra désormais comme valide) ?');"
			title="Forcer cet indicateur"
			aria-label="Forcer cet indicateur"
			% else:
			title="Invalider cet indicateur"
			aria-label="Invalider cet indicateur"
			% endif
			>
				% if not indicator.forced:
				${api.icon('bolt')}
				% else:
				${api.icon('redo-alt')}
				% endif
		</a>
    % endif
	</td>
</tr>
