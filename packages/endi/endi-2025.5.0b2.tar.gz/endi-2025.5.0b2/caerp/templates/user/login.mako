<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" name="utils"/>
<%doc>
context : User
</%doc>
<%block name="mainblock">
% if login is None:
<div class='alert alert-warning'>
    <span class="icon">${api.icon('exclamation-circle')}</span>
    Ce compte ne dispose pas d’identifiant pour se connecter à enDI
</div>

<a
    class='btn btn-primary'
    href="${request.route_path('/users/{id}/login/add', id=request.context.id)}"
>
    ${api.icon('plus')}
    Créer des identifiants pour ce compte
</a>
% else:
<div class='user_dashboard'>
    % if api.has_permission('global.create_user'):
	<div class='separate_bottom'>
		Nom d’utilisateur : <strong>${login.login}</strong>
        
		% if login.active:
		<div class='alert alert-success'>
			<span class="icon">${api.icon('check')}</span>
			Cet identifiant est actif
		</div>
		% else:
		<div class='alert alert-danger'>
			<span class="icon">${api.icon('times')}</span>
			Cet identifiant n’est pas actif
		</div>
		% endif
	    <br /><small>
        % if last_connection is not None:
            Dernière connexion : le ${api.format_datetime(last_connection)}
        % else:
            Ne s'est jamais connecté.
        % endif
        </small>
        <div class="separate_bottom">
            <h3>Rôles</h3>
            <ul class="content_padding">
            % for group in login._groups:
            <li>${group.label}</li>
            % endfor
            </ul>
            % if login.account_type == 'entrepreneur':
            <h4>Montants maximum autorisés pour l’autovalidation</h4>
            <ul>
                <li>Devis : ${utils.show_amount_or_undefined_string(login.estimation_limit_amount)}</li>
                <li>Factures : ${utils.show_amount_or_undefined_string(login.invoice_limit_amount)}</li>
                <li>Commandes fournisseur : ${utils.show_amount_or_undefined_string(login.supplier_order_limit_amount)}</li>
                <li>Factures fournisseur : ${utils.show_amount_or_undefined_string(login.supplier_invoice_limit_amount)}</li>
            </ul>
        </div>
        % endif
    % endif

    % if api.has_permission('context.edit_user'):
        <a
            href="${request.route_path('/users/{id}/login/set_password', id=_context.id)}"
            class='btn btn-primary'
            >
            ${api.icon('lock')}
            Changer le mot de passe
        </a>
    % endif

    % if api.has_permission('global.create_user'):
        <% activate_url = request.route_path('/users/{id}/login/disable', id=request.context.id) %>
        % if login.active:
        <a
            href="${request.route_path('/users/{id}/login/edit', id=request.context.id)}"
            class='btn'
            title='Modifier l’identifiant, le mot de passe, les rôles et les montants'
            aria-label='Modifier l’identifiant, le mot de passe, les rôles et les montants'
            >
            ${api.icon('pen')}
            Modifier
        </a>

        <%utils:post_action_btn url="${activate_url}" icon="lock"
        _class="btn negative"
        title="Désactiver ce compte (cet utilisateur ne pourra plus se connecter)"
        aria-label="Désactiver ce compte (cet utilisateur ne pourra plus se connecter)"
        confirm="L'utilisateur ne pourra plus se connecter, ses enseignes seront désactivées. Continuer ?"
        >
            Désactiver
        </%utils:post_action_btn>
        % else:
        <%utils:post_action_btn url="${activate_url}" icon="check" 
        _class="btn"
        title="Activer ce compte (cet utilisateur pourra se connecter)"
        aria-label="Activer ce compte (cet utilisateur pourra se connecter)"
        >
            Activer
        </%utils:post_action_btn>
        % endif
        
    % endif
	</div>
% endif
</%block>
