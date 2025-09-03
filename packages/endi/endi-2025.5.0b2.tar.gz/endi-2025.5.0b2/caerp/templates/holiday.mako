<%doc>
Template for holiday declarations
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class='row' style="padding-top:10px;">
    <div class='col-md-6 col-md-offset-3'>
        ${form|n}
    </div>
</div>
</%block>
