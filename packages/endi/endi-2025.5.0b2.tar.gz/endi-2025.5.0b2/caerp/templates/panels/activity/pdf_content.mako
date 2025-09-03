<%namespace file="caerp:templates/base/utils.mako" import="format_text" />
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="shortcut icon" href="" type="image/x-icon" />
        <meta name="description" comment="">
        <meta name="KEYWORDS" CONTENT="">
        <meta NAME="ROBOTS" CONTENT="INDEX,FOLLOW,ALL">
  </head>
  <body class="caerp activity_view pdf_export">
    ${request.layout_manager.render_panel('activity_pdf_header', context=request.context)}
    <main>
    <div><b>Date : </b> le ${api.format_date(activity.datetime)}</div>
    <div><b>Durée : </b> ${activity.duration}</div>

    <div class="pdf_title_block">
    <h2 class='upper'>${activity.action_label}</h2>
    <p>${activity.subaction_label}</p>
    <h1>${activity.type_object.label}</h1>
    </div>

    <div class="activity_people">
    <div>Accompagnateur : ${', '.join([api.format_account(conseiller) for conseiller in activity.conseillers])}</div>
    <% companies = set() %>
    <div>Participants :
    % for user in activity.sorted_participants:
    ${api.format_account(user)} ( ${"'".join([c.name for c in user.companies])} )
    % if not loop.last:
    ,
    % endif
    % endfor
        </div>
        </div>
        <% options = (\
                ("Objectifs du rendez-vous", "objectifs"), \
                ("Points abordés", "point"),\
                ("Plan d'action et préconisations", "action" ),\
                ("Documents produits", "documents" ),\
                )
        %>
        % for label, attr in options:
        <h3 class='activity-title' >${label}</h3>
        <div class="activity-content">
        % if getattr(activity, attr) is not None:
        ${api.clean_html(getattr(activity, attr))|n}
        % endif
        </div>
        % endfor
        <br />
        <br />
        <table>
        <tr>
        <td style="padding-bottom:50px; width:50%">
        <b>Signature Accompagnateur</b>
        </td>
        <td style="padding-bottom:50px; width:50%">
        <b>Signature Participant</b>
        </td>
        </tr>
        </table>

    </main>
   </body>
</html>
