<%inherit file="${context['main_template'].uri}" />

<%block name='content'>
<div class='layout flex two_cols quarter_reverse'>
    <div>
        <h3>${title}</h3>
        <div>
            ${form|n}
        </div>
    </div>
    <div class='context_help'>
        <h4>Codes fournisseur utilisés</h4>
        <ul>
            % for supplier in suppliers:
                <li>${supplier.code.upper()} (${supplier.label})</li>
            % endfor
        </ul>
    </div>
</div>
</%block>
