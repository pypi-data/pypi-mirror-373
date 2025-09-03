<%inherit file="/base/formpage.mako" />
<%namespace file="/base/utils.mako" import="format_text" />
<%block name='beforecontent'>
    % if duplicate_accounts is not UNDEFINED:
	<h2>
	Confirmez l’ajout
	</h2>
	<div class="alert alert-warning">
		<div class='row'>
			<span class="icon">${api.icon('exclamation-circle')}</span> 
			Vous allez ajouter le compte
			<strong>${appstruct['lastname']}
			${appstruct['firstname']}
			(${appstruct['email']})</strong>. Il existe des comptes
			avec des noms ou des adresses de courriels
			similaires.<br /><br />
			Après avoir vérifié que le compte n’existe pas encore
			dans enDI, vous pouvez confirmer l’ajout d'un
			nouveau compte.
			<br />
			<div class="content_vertical_padding">
				<button
					class="btn btn-primary btn-success"
					onclick="submitForm('#${confirm_form_id}');">
					Confirmer l’ajout
				</button>
				<a href="${back_url}"
					class="btn negative btn-danger"
					>
					Annuler la saisie
				</a>
			</div>
			<br />
			<div class="content_vertical_padding">
				<h3>Liste des comptes similaires</h3>
				<ul>
				% for account in duplicate_accounts:
					<li>
						<a href="#" onclick="openPopup('${request.route_path(user_view_route, id=account.id)}')" title="Voir ce compte dans une nouvelle fenêtre" aria-label="Voir ce compte dans une nouvelle fenêtre">
							${api.format_account(account)} (${account.email})
						</a>
					</li>
				% endfor
				</ul>
			</div>
		</div>
	</div>
    % endif
</%block>
