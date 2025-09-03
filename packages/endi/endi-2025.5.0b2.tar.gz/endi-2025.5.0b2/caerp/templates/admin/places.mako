<%doc>
    Admin page for CAE places
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text"/>
<%block name="afteradminmenu">
<div class='limited_width width40'>
  %if geojson is None:
  <div class='alert alert-info'>
    <span class="icon">${api.icon('info-circle')}</span>
    Aucun fichier de lieu trouvé
  </div>
  % else:
  <div class='alert alert-info'>
    <span class="icon">${api.icon('info-circle')}</span>
    La liste contient ${len(geojson["features"])}
    %if len(geojson["features"]) < 2:
      lieu
    %else:
      lieux
    %endif
  </div>
  <div>
    <ul class="places">
      %for place in geojson["features"]:
      <li>
        <strong>${place["properties"]["name"]}</strong>      
        %if "description" in place["properties"] and place["properties"]["description"]:
        <p>${place["properties"]["description"]}</p>
        %endif
      </li>
      %endfor
    </ul>
  </div>
  % endif
</%block>
<%block name='content'>
${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
% if not form is UNDEFINED:
<div class='content_vertical_padding separate_top limited_width width40'>
  <h2>Remplacer la liste</h2>
  <div class='alert alert-info'>
    <p>
      Téléversez un fichier au format geojson pour créer une nouvelle
      liste de lieux ressources.

      Vous pouvez créer ce fichier grâce à des outils comme <a href='https://vector.rocks/' target="_blank">Vector</a> puis
      le téléverser ci-dessous.
    </p>
    <p>
      Chaque entrée du fichier geojson peut contenir les propriétés suivante :
      <ul>
        <li><code>name : nom du lieu (obligatoire)</code></li>
        <li><code>description : description en une ou deux phrases du lieu (obligatoire)</code></li>
        <li><code>website : URL (optionnel)</code></li>
        <li><code>contact : contact sur place / contact utile (optionnel)</code></li>
      </ul>

      Un
      <a href="${request.static_url('caerp:static/demo-lieux-ressources.geojson')}"
         target="_blank"
         title="Cliquer pour récupérer un fichier exemple"
         aria-label="Cliquer pour récupérer un fichier exemple">exemple de fichier est disponible ici</a>
    </p>
  </div>
  <div>
    ${form|n}
  </div>
</div>
% endif
</%block>
