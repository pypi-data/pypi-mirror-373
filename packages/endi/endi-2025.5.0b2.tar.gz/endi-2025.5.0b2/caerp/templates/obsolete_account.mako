<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_mail" />
<%block name='content'>
<% account = request.identity %>
<div class="row form-row" style="margin-top:10px">
    <div class='col-md-5'>
        <div class="panel panel-default page-block">
            <dl class="dl-horizontal">
                %for label, value in (('Identifiant', account.login), ('Nom', account.lastname), ('Prénom', account.firstname)):
                    %if value:
                    <dt>${label}</dt>
                    <dd>${value}</dd>
                % endif
                % endfor
                <dt>E-mail</dt><dd>${format_mail(account.email)}</dd>
            </dl>
            <a href="${request.route_path('user', id=account.id, _query=dict(action='accountedit'))}" class="btn btn-primary icon">
                ${api.icon('pen')}
                Modifier
            </a>
        </div>
        <div class="panel panel-default page-block">
            % if len(account.companies) == 0:
                Vous n'êtes lié(e) à aucune enseigne
            % elif len(account.companies) == 1:
                <h3>Votre enseigne</h3>
            % else:
                <h3>Vos enseignes</h3>
            % endif
            <br />
            % for company in account.companies:
                <a href="${request.route_path('/companies/{id}', id=company.id , _query=dict(edit=True))}">
                    <strong>${company.name}</strong>
                    <br />
                    %if company.logo_id:
                        <img src="${api.img_url(company.logo_file)}" alt=""  width="250px" />
                    %endif
                </a>
                <p>
                ${company.goal}
                </p>
            % endfor
        </div>
    </div>
    <div class='col-md-5 col-md-offset-2'>
        <div class='panel panel-default page-block'>
        ${form|n}
        </div>
    </div>
</div>
</%block>
