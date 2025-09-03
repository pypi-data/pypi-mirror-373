<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

<div>
    <br />
    <div class="alert alert-info">
        <span class="icon">${api.icon('info-circle')}</span>
        Les exports réalisés avant l'apparition de la fonction
        d'enregistrement de l'historique des exports comptables
        en octobre 2021, ne sont pas affichés ici. Seuls ceux
        postérieurs à cette date y sont affichés.
	</div>
    ${searchform()}
    <div>
        <br />${records.item_count} résultat(s)<br /><br />
    </div>
    <div class='table_container'>
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_number">${sortable("Identifiant", "id")}</th>
                    <th scope="col" class="col_datetime">${sortable("Date et heure", "datetime")}</th>
	    			<th scope="col" class="col_text">${sortable("Type d'export", "export_type")}</th>
                    <th scope="col" class="col_text">${sortable("Exporté par", "user_id")}</th>
	    			<th scope="col" class="col_actions width_two"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
                % if records:
                    % for export_log in records:
                        <tr class='tableelement' id="${export_log.id}">
                            <td class="col_number">${export_log.id}</td>
                            <td
                            class="col_date">${api.format_datetime(export_log.datetime)}</td>
                            <td class="col_text">
                            <%
                                from caerp.views.export.utils import format_export_type
                                export_type = format_export_type(\
                                    export_log.export_type)
                            %>
                            ${export_type}</td>
                            <td class="col_text">${api.format_account(export_log.user)}</td>
                            <td class="col_actions width_one">
                                <a href="/files/${export_log.export_file_id}?action=download" class="btn icon only"
                                title="Re-télécharger cet export"
                                aria-label="Re-télécharger cet export">
                                    ${api.icon('download')}
                                </a>
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr>
                        <td colspan='9' class="col_text">
                            <em>Aucun export comptable n'a été enregistré</em>
                        </td>
                    </tr>
                % endif
            </tbody>
        </table>
	</div>
	${pager(records)}
</div>
</%block>

