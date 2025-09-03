<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="top_align_table hover_table">
            % if records:
            <thead>
                <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                <th scope="col" class="col_date">${sortable("Demandé le", "status_date")}</th>
                <th scope="col" class="col_text">${sortable("Entrepreneur", "name")}</th>
                <th scope="col" class="col_text">${sortable("Période et nom", "month")}</th>
                <th scope="col" class="col_number">HT</th>
                <th scope="col" class="col_number">TVA</th>
                <th scope="col" class="col_number">TTC</th>
                <th scope="col" class="col_number">Kms</th>
                <th scope="col" class="col_text">Justificatifs</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if records:
			        % for id_, expense in records:
                        <% url = request.route_path('/expenses/{id}', id=expense.id, _query={'come_from': request.current_route_path()}) %>
                        <% tooltip_title = "Cliquer pour voir cette note de dépenses" %>

                        <tr class='status status-${expense.global_status}'>
                            <td class='col_status' title="${api.format_expense_status(expense)}">
                                <span class="icon status ${expense.global_status}">
                                    ${api.icon(api.status_icon(expense))}
                                </span>
                            </td>
                            <td class="col_date">${api.format_date(expense.status_date)}</td>
                            <td class="col_text">${api.format_account(expense.user)} (${expense.company.name})</td>
                            <td class="col_text">
                                ${api.month_name(expense.month).capitalize()} ${expense.year}
                                % if expense.title:
                                    <br /><small>${expense.title}</small>
                                % endif
                            </td>
                            <td class="col_number"><strong>${api.format_amount(expense.total_ht)} €</strong></td>
                            <td class="col_number">${api.format_amount(expense.total_tva)} €</td>
                            <td class="col_number">${api.format_amount(expense.total, precision=2)} €</td>
                            <td class="col_number">${api.remove_kms_training_zeros(api.format_amount(expense.total_km))}</td>
                            <td class="col_text">
                                % if api.has_permission('context.set_justified_expensesheet', expense) and expense.status != 'valid':
                                    <div
                                        class="icon_choice layout flex expense-justify"
                                        data-toggle="buttons"
                                        data-href="${request.route_path('/api/v1/expenses/{id}', id=expense.id, _query={'action': 'justified_status'})}"
                                        >
                                        <label
                                            class="btn
                                            % if not expense.justified:
                                                active
                                            % endif
                                            "
                                            % if not expense.justified:
                                                title="En attente des justificatifs"
                                            % else:
                                                title="Changer le statut en : Justificatifs en attente"
                                            % endif
                                            >
                                            <input
                                                name="justified_${expense.id}"
                                                value="false"
                                                % if not expense.justified:
                                                    checked="true"
                                                % endif
                                                autocomplete="off"
                                                type="radio"
                                                class="visuallyhidden">
                                            <span>
                                                ${api.icon('clock')}
                                                <span>En attente</span>
                                                <span class="screen-reader-text">
                                                    % if not expense.justified:
                                                     (En attente des justificatifs)
                                                    % else:
                                                     (Cliquer pour changer le statut en : Justificatifs en attente)
                                                    % endif
                                                </span>
                                            </span>
                                        </label>
                                        <label class="btn"
                                            % if not expense.justified:
                                                title="Changer le statut en : Justificatifs reçus"
                                            % else:
                                                title="Justificatifs reçus"
                                            % endif
                                            >
                                            <input
                                            name="justified_${expense.id}"
                                            value="true"
                                            % if expense.justified:
                                                checked="true"
                                            % endif
                                            autocomplete="off"
                                            type="radio"
                                            class="visuallyhidden">
                                            <span>
                                                ${api.icon('check')}
                                                <span>Reçus<span>
                                                <span class="screen-reader-text">
                                                    % if not expense.justified:
                                                     (Cliquer pour changer le statut en : Justificatifs reçus)
                                                    % else:
                                                     (Justificatifs reçus)
                                                    % endif
                                                </span>
                                            </span>
                                        </label>
                                    </div>
                                % endif
                            </td>
                            <td class="col_actions width_one">
                                <a class="btn icon only" href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${api.icon("arrow-right")}</a>
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr><td class='col_text' colspan='10'>
                        <em>
                        % if '__formid__' in request.GET:
                            Aucune note de dépenses en attente de validation correspondant à ces critères
                        % else:
                            Aucune note de dépenses en attente de validation
                        % endif
                        </em>
                    </td></tr>
                % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
