<%doc>
Template recevant :

- icon : nom de l'icone
- title: titre de la page
- file_hint : libellé "voir le ..."
- dataset: itérable des données à présenter (Task/SupplierOrder/SupplierInvoice, héritant de Node)
</%doc>
<div class="dash_elem">
    <h2>
        <span class="icon">${api.icon( icon )}</span>
        <span>${title}</span>
    </h2>
    <div class='panel-body'>
        % if dataset:
        <table class="hover_table">
        % else:
        <table>
        %endif
            <caption class="screen-reader-text">Liste des ${title}</caption>
            % if dataset:
            <thead>
                <tr>
                    <th scope="col" class='col_text'>Nom</th>
                    <th scope="col" class='col_text'>Enseigne</th>
                    <th scope="col" class='col_date'><span class="no_tablet">Demandé </span>le</th>
                </tr>
            </thead>
            % endif
            <tbody>
                % for doc in dataset:
                    <% tooltip_title = file_hint %>
                    % if doc.name:
                    <% tooltip_title = "{} : « {} »".format(tooltip_title, doc.name) %>
                    % endif
                    <tr>
                        <td class="col_text"><a href="${doc.url}" title="${tooltip_title}" aria-label="${tooltip_title}">${doc.name}</a></td>
                        <td class="col_text clickable-cell" data-href="${doc.url}" title="${tooltip_title}">${doc.get_company().full_label}</td>
                        <td class="col_date clickable-cell" data-href="${doc.url}" title="${tooltip_title}">${api.format_date(doc.status_date)}</td>
                    </tr>
                % endfor
                % if not dataset:
                    <tr><td class="col_text" colspan="3">Aucun document en attente</td></tr>
                % endif
            </tbody>
        </table>
    </div>
</div>
