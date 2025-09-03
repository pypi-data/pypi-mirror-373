<%inherit file="${context['main_template'].uri}" />
<%block name="headtitle">
    <h1>
        <span class="icon caution">${api.icon('warning')}</span> Page non trouvée <small>(erreur 404)</small>
    </h1>
</%block>
<%block name="content">
    <div class="content_vertical_double_padding">
        <div class="alert alert-warning">
            <p>
                La page demandée n’a pas pu être trouvée, cela peut arriver :
            </p>
            <ul class="content_vertical_padding">
                <li>En cas de saisie erronée</li>
                <li>Suite à une mise à jour</li>
                <li>Après la suppression ou l’inactivation d’un contenu…</li>
            </ul>
            <p>
                <strong>Nous vous invitons à <a href="/">passer par la page d’accueil</a></strong> ou le menu pour retrouver votre chemin.
            </p>
            <p class="content_vertical_padding">
                Si vous accédez à cette page depuis un marque-page, nous vous invitons à mettre ce dernier à jour ou à le recréer.
            </p>
        </div>
    </div>
</%block>
