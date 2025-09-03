<%doc>
    BPF edition for a given business and fiscal year
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/utils.mako" name="utils" />
<%block name='mainblock'>
<div id="bpf_data_tab">
        ${request.layout_manager.render_panel(
        'help_message_panel',
        parent_tmpl_dict=context.kwargs
    )}
	% if not is_creation_form:
		<div class='content_vertical_padding'>
			<p>
				Lorsqu’une formation est à cheval sur plusieurs années, il faut renseigner
				des données BPF pour chacune des années.
			</p>
		</div>
		<div class='content_vertical_padding layout flex two_cols'>
			<div>
				<p>
					% if len(bpf_datas_tuples) <= 1:
						Cette formation a des données BPF sur une seule année.
					% else:
						Cette formation a des données BPF sur ${len(bpf_datas_tuples)} années.
					% endif
				</p>
				<div class='content_vertical_padding'>
					${new_bpfdata_menu.render(request)|n}
				</div>
			</div>
			<div class='table_container'>
				<table class='hover_table'>
					<tbody>
					<tr>
						<th scope='col' class='col_date'>Année</th>
						<th scope='col' class='col_text'>Document cible</th>
						<th scope='col' class='col_actions' title='Actions'>
							<span class='screen-reader-text'>Actions</span>
						</th>
					</tr>
					% for bpf_data, edit_link, delete_link in bpf_datas_tuples:
						<tr class='${"selected" if context_model.id == bpf_data.id else ""}'>
							<td class='col_date'>
								BPF ${bpf_data.financial_year}
							</td>
							<td class='col_text'>
								Cerfa ${bpf_data.cerfa_version}
							</td>
							% if context_model.id != bpf_data.id:
							<% width_class = "width_two" %>
							% else:
							<% width_class = "width_one" %>
							% endif
							<td class='col_actions ${width_class}'>
								<ul>
									% if context_model.id != bpf_data.id:
									<li>
											${utils.table_btn(
										      edit_link,
										      f'Modifier les données pour {bpf_data.financial_year}',
										      f'Modifier les données pour {bpf_data.financial_year}',
										      'pen',
										  )}
									</li>
									% endif
									<li>
										${utils.table_btn(
										      delete_link,
										      f'Supprimer les données pour {bpf_data.financial_year}',
										      f'Supprimer les données pour {bpf_data.financial_year}',
										      'trash-alt',
													css_class="negative",
										      method='post',
										  )}
										</form>
									</li>
								</ul>
							</td>
						</tr>
					% endfor
					</tbody>
				</table>
			</div>
		</div>
	% endif
	<div class="separate_bottom content_vertical_padding">
		<h2>${title}</h2>
	</div>
	<div>
		<p>
			Ces données seront agrégées avec celles des autres formations de la même année pour produire le bilan pédagogique de formation.
		</p>
	    ${form|n}
	</div>
</div>

</%block>
<%block name='footerjs'>
    const subcontractFields = new SubContractFields(
      "[name='has_subcontract']",
      [
        "[name='has_subcontract_amount']",
        "[name='has_subcontract_hours']",
        "[name='has_subcontract_headcount']",
      ]
    )
    new TraineeTypeFields(
      "[name=trainee_type_id]",
      [
        ".item-trainee_types [name=total_hours]",
        ".item-trainee_types [name=headcount]",
      ]
    )

    const subContractTotalsLink = new SubContractTotalsLink(
      "[name='has_subcontract']",
      [
		{
		  src: "[name=headcount]",
		  target: "[name=has_subcontract_headcount]",
		},
		{
		  src: "[name=total_hours]",
		  target: "[name=has_subcontract_hours]",
		},
      ]
    )

    const subcontractSimplification = new SubcontractSimplification(
      "[name=is_subcontract]",
      [".hidden_if_is_subcontract"],
      [subcontractFields, subContractTotalsLink],
    )

    // When adding new element to the sequence, update dynamic/show display of the fields just added.
    $('.btn.deform-seq-add').click(() => subcontractSimplification.update())
</%block>
