<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_filetable" />
<%namespace file="/base/utils.mako" import="table_btn" />
<%block name='content'>
<div class='alert alert-info'>
	<span class="icon">${api.icon('info-circle')}</span>
	Retrouvez ici l’ensemble des documents sociaux ayant été associés à votre compte dans enDI.
</div>
<h3>Documents déposés dans enDI</h3>
<div class="table_container">
	${format_filetable(documents)}
</div>
</%block>
