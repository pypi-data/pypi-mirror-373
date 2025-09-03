<%doc>
Page de tests javascript
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<h1 id="qunit-header">${title}</h1>
<h2 id="qunit-banner"></h2>
<div id="qunit-testrunner-toolbar"></div>
<h2 id="qunit-userAgent"></h2>
<ol id="qunit-tests"></ol>
<div id="qunit-fixture"></div>
</div>
</%block>
