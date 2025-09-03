<div class="dash_elem">
    <h2>
        <span class='icon'>${api.icon('calendar-alt')}</span>
        <a href="${request.route_path('activities', _query=dict(__formid__='deform', conseiller_id=request.identity.id))}" title="Voir tous les Rendez-vous & Activités">
            <span>Rendez-vous & Activités à venir</span>
            ${api.icon('arrow-right')}
        </a>
    </h2>
    <div class='panel-body'>
        % if activities:
        <table class="hover_table">
        % else:
        <table>
        % endif
            <caption class="screen-reader-text">Liste de mes rendez-vous et activités à venir</caption>
            % if activities:
            <thead>
                <tr>
                    <th scope="col" class="col_date">Date</th>
                    <th scope="col" class="col_text">Participant</th>
                    <th scope="col" class="col_text">Mode</th>
                    <th scope="col" class="col_text">Nature du rendez-vous</th>
                </tr>
            </thead>
            % endif
            <tbody>
                % for activity in activities:
                    <tr class="clickable-row" data-href="${activity.url}" title="Voir le détail du rendez-vous ou de l’activité">
                        <td class="col_date">${api.format_datetime(activity.datetime)}</td>
                        <td class="col_text">
                            <ul>
                                % for participant in activity.participants:
                                    <li>${api.format_account(participant)}</li>
                                % endfor
                            </ul>
                        </td>
                        <td class="col_text">${activity.mode}</td>
                        <td class="col_text">${activity.type_object.label}</td>
                    </tr>
                % endfor
                % if not activities:
                    <tr><td class="col_text" colspan='4'><em>Aucune activité n'est prévue</em></td></tr>
                % endif
            </tbody>
        </table>
    </div>
</div>
