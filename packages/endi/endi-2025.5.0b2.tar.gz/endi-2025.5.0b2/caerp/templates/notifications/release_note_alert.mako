<div class="alert alert-info">
    <p>
        Vous accédez pour la première fois à la nouvelle version d’enDI, voici la liste des nouveautés.
    </p>
    <p>
        Vous pouvez à tout moment retrouver ces informations dans le menu <strong>Aide</strong> &gt; <strong>Notes de version</strong>.
    </p>
</div>

<ul class="version_notes">
% for note in notes:
    <li>
        <h4>
            % if note["category"] == "bugfix":
                <span class="icon">${api.icon("wrench")}</span>
            % else:
                <span class="icon">${api.icon("star")}</span>
            % endif
            ${note["title"]}
            % for sponsor in note["sponsors"]:
                <span class="icon tag neutral" title="Financé par ${sponsor}">${api.icon("euro-sign")}<span class="screen-reader-text">Financé par</span> ${sponsor}</span>
            % endfor
        </h4>
        % for description in note["description"]:
            % if len(note["description"]) > 1:
                <p class="note_description">&bull; ${description}</p>
            % else:
                <p class="note_description">${description}</p>
            % endif
        % endfor
        % if "link" in note:
            <span class="icon">${api.icon("link")}</span>
            <a class="note_link" href="${note['link']['url']}" target="_blank">${note["link"]['title']}</a>
        % endif
    </li>
% endfor
</ul>
