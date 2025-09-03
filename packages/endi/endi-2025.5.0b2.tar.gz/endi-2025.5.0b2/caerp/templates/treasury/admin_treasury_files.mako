<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
    % if errors:
        % if "mails" in errors:
            <div class="alert alert-danger">
                <span class="icon">${api.icon('danger')}</span> 
                Veuillez sélectionner au moins un fichier à envoyer
                % if force == False:
                    (si vous désirez forcer l'envoi de documents, vous devez cocher l'option "Forcer l'envoi des documents déjà expédiés ?")
                % endif
            </div>
        % endif
        % if "mail_subject" in errors or "mail_message" in errors:
            <div class="alert alert-danger">
                <span class="icon">${api.icon('danger')}</span> 
                Le sujet et le contenu du mail ne peuvent être vide
            </div>
        % endif

    % endif
    <form accept-charset="utf-8" enctype="multipart/form-data" method="POST" action="">
        <div class="content_vertical_padding">
            <div class="alert alert-info">
                <span class="icon">${api.icon('info-circle')}</span> 
                Depuis cette interface, vous pouvez envoyer des documents par e-mail.
                <ul>
                    <li>Sélectionner les documents que vous voulez envoyer</li>
                    <li>Composer votre message</li>
                    <li>Envoyer</li>
                </ul>
            </div>

            <table class="table_hover">
                <caption>Sélection des documents</caption>
                <thead>
                    <th scope="col" class="col_select">
                        <div class="checkbox">
                            <label title="Tout sélectionner">
                                <input type="checkbox" id="check_all"></input>
                                <span></span>
                                <span class="screen-reader-text">Tout sélectionner</span>
                            </label>
                        </div>
                    </th>
                    <th scope="col" class="col_text">Enseigne</th>
                    <th scope="col" class="col_text">Adresse de l’enseigne</th>
                    <th scope="col" class="col_text">Nom du fichier</th>
                    <th scope="col">Déjà envoyé ?</th>
                </thead>
                <tbody>
                    <input type="hidden" name="__start__" value="mails:sequence" />
            % for data in datas.values():
                % for file_dict in data:
                    <tr>
                        <% file_obj = file_dict['file'] %>
                        <% filename = file_obj.name %>
                        <% id_ = file_dict['company'].id %>
                        <td class="col_select">
                            % if file_dict['company'].email:
                            <div class="checkbox">
                                <input type="hidden" name="__start__" value="mail:mapping"/>
                                <input type="hidden" name="company_id" value="${file_dict['company'].id}" />
                                <label title="Sélectionner cette ligne" aria-label="Sélectionner cette ligne">
                                    <input type="checkbox"
                                        name="attachment"
                                        value="${filename}"
                                        % if {'company_id': id_, 'attachment': filename} in mails:
                                            checked
                                        % endif
                                    />
                                    <span></span>
                                </label>
                            <input type="hidden" name="__end__" value="mail:mapping"/>
                            % else:
                            <span class="icon" title="e-mail non renseigné" aria-label="e-mail non renseigné">
                                ${api.icon('exclamation-circle','caution')}
                            </span>
                            % endif
                        </td>
                        <td class="col_text">${file_dict['company'].name}</td>
                        <td class="col_text">${file_dict['company'].email}</td>
                        <td class="col_text">
                            <a href="${file_obj.url(request, company_id=id_)}" title="Visualisez le fichier" aria-label="Visualisez le fichier">
                                ${filename}&nbsp;
                                <span class="icon">${api.icon('file-pdf')}</span>
                            </a>
                        </td>
                        <td>
                            % if file_obj.is_in_mail_history(file_dict['company']):
                                <span class="icon" title="Déjà envoyé" aria-label="Déjà envoyé">${api.icon('check')}</span>
                            % endif
                        </td>
                    </tr>
                % endfor
            % endfor
                <input type="hidden" name="__end__" value="mails:sequence" />
                </tbody>
            </table>
            <div class="separate_top content_vertical_padding">
                <div class="form-group">
                    <label for="subject">Objet de l’e-mail</label>
                    <input type='text' name="mail_subject" value="${mail_subject}" class="form-control" placeholder="Sujet de l’e-mail"></input>
                </div>
                <div class="form-group">
                    <label for="mail_message">Message</label>
                    <textarea name="mail_message" class="form-control">${mail_message}</textarea>
                    <span class="help-block">Le contenu du message (les variables entre {} seront remplacées par les variables correspondantes):
                        <ul class='list-unstyled'>
                            <li>{company.name} : Nom de l'enseigne</li>
                            <li>{company.employees[0].lastname} : Nom du premier employé de l'enseigne</li>
                            <li>{company.employees[0].firstname} : Prénom du premier employé de l'enseigne</li>
                            <li>{month} : mois du bulletin de salaire</li>
                            <li>{year} : année du bulletin de salaire</li>
                        </ul>
                    </span>
                </div>
                <div class="checkbox">
                    <label>
                        <input type="checkbox" value="force" name="force"
                        % if force:
                            checked
                        % endif
                        />
                        <span>Forcer l’envoi des documents déjà expédiés&nbsp;?</span>
                    </label>
                    <p class="help-block">
                        Si vous ne cochez pas cette case seul les documents qui \
                        n’ont pas encore été expédiés seront envoyés.
                    </p>
                </div>
            </div>
        </div>
        <div class="content_vertical_padding">
            <div class="form-actions">
                <button class="btn btn-primary"
                    type="submit"
                    name="submit"
                    title="Envoyer ces documents par mail"
                    aria-label="Envoyer ces documents par mail">
                        ${api.icon('arrow-right')}
                        Envoyer
                </button>
            </div>
        </div>
    </form>
</%block>
<%block name="footerjs">
$('#check_all').change(
    function(){
    $('input[name=attachment]').prop('checked', this.checked);
    }
);
</%block>
