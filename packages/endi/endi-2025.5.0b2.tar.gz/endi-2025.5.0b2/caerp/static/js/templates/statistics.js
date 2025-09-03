(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['andcriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":21,"column":21},"end":{"line":21,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":21,"column":32},"end":{"line":21,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":21,"column":67},"end":{"line":21,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":8,"column":11},"end":{"line":8,"column":22}}}) : helper)))
    + "</legend>\n			<div class='alert alert-info'>\n				<ol>\n				<li>Configurer vos critères</li>\n				<li>Créer une clause 'ET'</li>\n				<li>Sélectionner les critères à utiliser dans la clause 'ET'</li>\n				</ol>\n			</div>\n			<div class='row form-row'>\n				<div class='form-group col-md-12'>\n					<label for=\"criteria\">Combiner les critères</label>\n					<select multiple name='criteria' class='form-control'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"criteria_options") || (depth0 != null ? lookupProperty(depth0,"criteria_options") : depth0)) != null ? helper : alias2),(options={"name":"criteria_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":20,"column":6},"end":{"line":22,"column":28}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"criteria_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['boolcriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":15,"column":21},"end":{"line":15,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":32},"end":{"line":15,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":15,"column":67},"end":{"line":15,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<input type='hidden' name='key' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":41},"end":{"line":7,"column":48}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":9,"column":11},"end":{"line":9,"column":22}}}) : helper)))
    + "</legend>\n			<div class='row form-row'>\n				<div class='form-group col-md-6'>\n					<label for=\"method\">Compter les éléments</label>\n					<select name='method'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"method_options") || (depth0 != null ? lookupProperty(depth0,"method_options") : depth0)) != null ? helper : alias2),(options={"name":"method_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":14,"column":6},"end":{"line":16,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"method_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['criterion.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<td class=\"col_text\">\n"
    + ((stack1 = ((helper = (helper = lookupProperty(helpers,"model_label") || (depth0 != null ? lookupProperty(depth0,"model_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"model_label","hash":{},"data":data,"loc":{"start":{"line":2,"column":0},"end":{"line":2,"column":19}}}) : helper))) != null ? stack1 : "")
    + "\n</td>\n<td class='col_actions width_two'>\n    <ul>\n    	<li>\n			<a class='btn icon only' href='#"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"edit_url") || (depth0 != null ? lookupProperty(depth0,"edit_url") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"edit_url","hash":{},"data":data,"loc":{"start":{"line":7,"column":35},"end":{"line":7,"column":49}}}) : helper)))
    + "' title=\"Modifier cette entrée\" aria-label=\"Modifier cette entrée\">\n				<svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n			</a>\n    	</li>\n    	<li>\n			<a class='btn icon only negative remove' title='Supprimer cette entrée' aria-label='Supprimer cette entrée'>\n				<svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg>\n			</a>\n    	</li>\n    </ul>\n</td>\n";
},"useData":true});
templates['criterion_list.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<h4>Critères composant l’entrée statistique</h4>\n<div class=\"table_container\">\n	<table class=\"hover_table\">\n		<thead>\n			<tr>\n				<th scope=\"col\" class=\"col_text\">Intitulé</th>\n				<th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n			</tr>\n		</thead>\n		<tbody>\n		</tbody>\n		<tfoot>\n			<tr>\n				<td class=\"col_actions\" colspan=\"2\">\n					<ul>\n						<li>\n							<a href=\"javascript:void(0);\" class='btn btn-primary add'>\n								Ajouter\n							</a>\n						</li>\n						<li>\n							<a href=\"javascript:void(0);\" class='btn add-or'>\n								Ajouter une clause 'OU'\n							</a>\n						</li>\n						<li>\n							<a href=\"javascript:void(0);\" class='btn add-and'>\n								Ajouter une clause 'ET'\n							</a>\n						</li>\n					</ul>\n				</td>    	\n			</tr>\n		</tfoot>\n	</table>\n</div>\n\n";
},"useData":true});
templates['criterion_type_select.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "    <option data-type='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":7,"column":23},"end":{"line":7,"column":31}}}) : helper)))
    + "' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":40},"end":{"line":7,"column":47}}}) : helper)))
    + "'>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":7,"column":49},"end":{"line":7,"column":58}}}) : helper)))
    + "</option>\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<form >\n    <div class=\"form-group\">\n    <label for='type_id'>Champs de gestion sociale</label>\n    <div class='controls'>\n    <select>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"columns") || (depth0 != null ? lookupProperty(depth0,"columns") : depth0)) != null ? helper : container.hooks.helperMissing),(options={"name":"columns","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":6,"column":4},"end":{"line":8,"column":16}}}),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),options) : helper));
  if (!lookupProperty(helpers,"columns")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </select>\n    <span class='help-block'>Le champ sur lequel ce critère statistique va porter</span>\n    </div>\n    </div>\n    <button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Valider</button>\n    <button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n</form>\n";
},"useData":true});
templates['datecriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":15,"column":21},"end":{"line":15,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":32},"end":{"line":15,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":15,"column":67},"end":{"line":15,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<input type='hidden' name='key' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":41},"end":{"line":7,"column":48}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":9,"column":11},"end":{"line":9,"column":22}}}) : helper)))
    + "</legend>\n			<div class='row form-row'>\n				<div class='form-group col-md-4'>\n					<label for=\"method\">Compter les éléments</label>\n					<select name='method'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"method_options") || (depth0 != null ? lookupProperty(depth0,"method_options") : depth0)) != null ? helper : alias2),(options={"name":"method_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":14,"column":6},"end":{"line":16,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"method_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n				<div class=\"form-group col-md-4\">\n					<label  for='altdate1'>Date 1</label>\n					<input class=\"form-control\" name=\"altdate1\" type=\"text\" autocomplete=\"off\">\n					<input class=\"form-control\" name=\"search1\" type=\"hidden\">\n				</div>\n				<div class=\"form-group col-md-4\">\n					<label  for='altdate'>Date 2</label>\n					<input class=\"form-control\" name=\"altdate2\" type=\"text\" autocomplete=\"off\">\n					<input class=\"form-control\" name=\"search2\" type=\"hidden\">\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['entry.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<td class=\"col_text\">\n"
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":2,"column":0},"end":{"line":2,"column":11}}}) : helper)))
    + "\n</td>\n<td class='col_actions width_three'>\n    <ul>\n		<li>\n			<a class='btn icon only' href='#entries/"
    + alias4(((helper = (helper = lookupProperty(helpers,"id") || (depth0 != null ? lookupProperty(depth0,"id") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"id","hash":{},"data":data,"loc":{"start":{"line":7,"column":43},"end":{"line":7,"column":49}}}) : helper)))
    + "/edit' title=\"Modifier cette entrée\" aria-label=\"Modifier cette entrée\">\n				<svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n			</a>\n		</li>\n		<li>\n			<button class='btn icon only csv_export' title='Exporter les éléments correspondant à cette entrée statistiques' aria-label='Exporter les éléments correspondant à cette entrée statistiques'>\n				<svg><use href=\"/static/icons/icones.svg#file-export\"></use></svg>\n			</button>\n		</li>\n		<li>\n			<a class='btn icon only negative remove' title='Supprimer cette entrée' aria-label='Supprimer cette entrée'>\n				<svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg>\n			</a>\n		</li>\n    </ul>\n</td>\n";
},"useData":true});
templates['entry_form.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<form>\n    <div class=\"form-group\">\n        <label class='control-label' for=\"title\">Intitulé de l’entrée statistique <b class='required'>*</b></label>\n        <input type=\"text\" name='title' class=\"form-control\" id=\"title\" placeholder=\"Titre\" value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":4,"column":99},"end":{"line":4,"column":108}}}) : helper)))
    + "'>\n    </div>\n    <div class=\"form-group\">\n        <label class='control-label' for=\"title\">Description de l’entrée statistique</label>\n        <textarea name='description' class=\"form-control\" id=\"title\" placeholder=\"Description\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":8,"column":95},"end":{"line":8,"column":110}}}) : helper)))
    + "</textarea>\n    </div>\n    <button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Valider</button>\n    <button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n</form>\n";
},"useData":true});
templates['entry_list.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<hr />\n<h3>Entrées statistiques</h3>\n<div class=\"table_container\">\n    <table class=\"\">\n        <thead>\n        	<tr>\n				<th scope=\"col\" class=\"col_text\"><span class=\"screen-reader-text\">Intitulé</span></th>\n				<th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n        	</tr>\n        </thead>\n        <tbody>\n        </tbody>\n    </table>\n</div>\n";
},"useData":true});
templates['full_entry_form.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<section id=\"customer_add_form\" class=\"modal_view size_middle\">\n    <div role=\"dialog\" id=\"customer-forms\" aria-modal=\"true\" aria-labelledby=\"customer-forms_title\">\n        <div class=\"modal_layout\">\n            <header>\n                <button class=\"icon only unstyled close\" title=\"Fermer cette fenêtre\" aria-label=\"Fermer cette fenêtre\" onclick=\"toggleModal('customer_add_form'); return false;\">\n                    <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n                </button>\n                <h2 id=\"customer-forms_title\">Entrée statistique <em>"
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":8,"column":69},"end":{"line":8,"column":80}}}) : helper)))
    + "</em></h2>\n            </header>\n            <div class=\"modal_content_layout\">\n                <div class=\"modal_content\">\n                    <div>\n                        <p>\n                        "
    + alias4(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":14,"column":24},"end":{"line":14,"column":39}}}) : helper)))
    + "\n                        </p>\n                    </div>\n                    <div id='entry_list_header'>\n                        <form id='entry_edit_form' style='display:none' class='well'>\n                            <button type=\"button\" class=\"icon only unstyled close\">\n                                <svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n                            </button>\n                            <fieldset>\n                                <legend>Édition</legend>\n                                <div class='row form-row'>\n                                    <div class=\"form-group col-md-6\">\n                                        <label class='control-label' for=\"title\">Intitulé de l’entrée statistique <b class='required'>*</b></label>\n                                        <input type=\"text\" name='title' class=\"form-control\" id=\"title\" placeholder=\"Titre\" value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":27,"column":131},"end":{"line":27,"column":140}}}) : helper)))
    + "'>\n                                        <span class='help-block'>\n                                            Sera utilisé dans le fichier de sortie\n                                        </span>\n                                    </div>\n                                    <div class=\"form-group col-md-6\">\n                                        <label class='control-label' for=\"title\">Description de l’entrée statistique</label>\n                                        <textarea name='description' class=\"form-control\" id=\"title\" placeholder=\"Description\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"description") || (depth0 != null ? lookupProperty(depth0,"description") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"description","hash":{},"data":data,"loc":{"start":{"line":34,"column":127},"end":{"line":34,"column":142}}}) : helper)))
    + "</textarea>\n                                    </div>\n                                </div>\n                            </fieldset>\n                            <button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Valider</button>\n                            <button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n                        </form>\n                    </div>\n                    <div id='criteria'></div>\n                    <div id='criterion-form' class='sub_modal'></div>\n                </div>\n                <footer>\n                    <button class='btn edit' title=\"Modifier le titre de l’entrée statistique\">\n                        <svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n                        Modifier\n                    </button>\n                    <button class='btn csv_export' title='Exporter les éléments correspondant à cette entrée statistiques'>\n                        <svg><use href=\"/static/icons/icones.svg#file-export\"></use></svg>\n                        Exporter\n                    </button>\n                </footer>\n           </div>\n        </div>\n    </div>\n</section>";
},"useData":true});
templates['numbercriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":15,"column":21},"end":{"line":15,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":32},"end":{"line":15,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":15,"column":67},"end":{"line":15,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<input type='hidden' name='key' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":41},"end":{"line":7,"column":48}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":9,"column":11},"end":{"line":9,"column":22}}}) : helper)))
    + "</legend>\n			<div class='row form-row'>\n				<div class='form-group col-md-4'>\n					<label for=\"method\">Compter les éléments</label>\n					<select name='method'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"method_options") || (depth0 != null ? lookupProperty(depth0,"method_options") : depth0)) != null ? helper : alias2),(options={"name":"method_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":14,"column":6},"end":{"line":16,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"method_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n				<div class=\"form-group col-md-4\">\n					<label  for='search1'>Valeur 1</label>\n					<input class=\"form-control\" name=\"search1\" type=\"text\" value=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"search1") || (depth0 != null ? lookupProperty(depth0,"search1") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"search1","hash":{},"data":data,"loc":{"start":{"line":21,"column":67},"end":{"line":21,"column":80}}}) : helper)))
    + "\"/>\n				</div>\n				<div class=\"form-group col-md-4\">\n					<label  for='search2'>Valeur 2</label>\n					<input class=\"form-control\" name=\"search2\" type=\"text\" value=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"search2") || (depth0 != null ? lookupProperty(depth0,"search2") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"search2","hash":{},"data":data,"loc":{"start":{"line":25,"column":67},"end":{"line":25,"column":80}}}) : helper)))
    + "\"/>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['optrelcriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":15,"column":21},"end":{"line":15,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":32},"end":{"line":15,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":15,"column":67},"end":{"line":15,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, alias5=container.hooks.blockHelperMissing, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<input type='hidden' name='key' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":41},"end":{"line":7,"column":50}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":9,"column":11},"end":{"line":9,"column":22}}}) : helper)))
    + "</legend>\n			<div class='row form-row'>\n				<div class='form-group col-md-6'>\n					<label for=\"method\">Compter les éléments</label>\n					<select name='method' class='form-control'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"method_options") || (depth0 != null ? lookupProperty(depth0,"method_options") : depth0)) != null ? helper : alias2),(options={"name":"method_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":14,"column":6},"end":{"line":16,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"method_options")) { stack1 = alias5.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  buffer += "					</select>\n				</div>\n				<div class=\"form-group col-md-6\">\n					<label  for='searches'>Parmi</label>\n					<select multiple name='searches' class='form-control'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"optrel_options") || (depth0 != null ? lookupProperty(depth0,"optrel_options") : depth0)) != null ? helper : alias2),(options={"name":"optrel_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":22,"column":6},"end":{"line":24,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"optrel_options")) { stack1 = alias5.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['orcriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":21,"column":21},"end":{"line":21,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":21,"column":32},"end":{"line":21,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":21,"column":67},"end":{"line":21,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":8,"column":11},"end":{"line":8,"column":22}}}) : helper)))
    + "</legend>\n			<div class='alert alert-info'>\n				<ol>\n				<li>Configurer vos critères</li>\n				<li>Créer une clause 'OU'</li>\n				<li>Sélectionner les critères à utiliser dans la clause 'OU'</li>\n				</ol>\n			</div>\n			<div class='row form-row'>\n				<div class='form-group col-md-12'>\n					<label for=\"criteria\">Combiner les critères</label>\n					<select multiple name='criteria' class='form-control'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"criteria_options") || (depth0 != null ? lookupProperty(depth0,"criteria_options") : depth0)) != null ? helper : alias2),(options={"name":"criteria_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":20,"column":6},"end":{"line":22,"column":28}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"criteria_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
templates['sheet_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var helper, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<h2>\n    "
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : (container.nullContext || {}),{"name":"title","hash":{},"data":data,"loc":{"start":{"line":3,"column":4},"end":{"line":3,"column":15}}}) : helper)))
    + "\n    <button class='btn icon only unstyled edit' title=\"Modifier le titre de la feuille de statistiques\" aria-label=\"Modifier le titre de la feuille de statistiques\">\n    <svg><use href=\"/static/icons/icones.svg#pen\"></use></svg>\n    </button>\n</h2>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "    style='display:none'\n";
},"5":function(container,depth0,helpers,partials,data) {
    return "        Modifier\n";
},"7":function(container,depth0,helpers,partials,data) {
    return "        Enregistrer\n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"title") : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":1,"column":0},"end":{"line":8,"column":7}}})) != null ? stack1 : "")
    + "<form class=\"form-inline\"\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"title") : depth0),{"name":"if","hash":{},"fn":container.program(3, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":10,"column":0},"end":{"line":12,"column":7}}})) != null ? stack1 : "")
    + ">\n  <div class=\"form-group\">\n    <label class='control-label' for=\"title\">Intitulé de la feuille de statistique</label>\n    <input type=\"text\" name='title' class=\"form-control\" id=\"title\" placeholder=\"Titre\" value='"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"title") || (depth0 != null ? lookupProperty(depth0,"title") : depth0)) != null ? helper : container.hooks.helperMissing),(typeof helper === "function" ? helper.call(alias1,{"name":"title","hash":{},"data":data,"loc":{"start":{"line":16,"column":95},"end":{"line":16,"column":104}}}) : helper)))
    + "'>\n  </div>\n    <button class=\"btn btn-primary submit\" type=\"submit\">\n"
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"title") : depth0),{"name":"if","hash":{},"fn":container.program(5, data, 0),"inverse":container.program(7, data, 0),"data":data,"loc":{"start":{"line":19,"column":4},"end":{"line":23,"column":11}}})) != null ? stack1 : "")
    + "    </button>\n</form>\n";
},"useData":true});
templates['stringcriterion_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "						<option value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":15,"column":21},"end":{"line":15,"column":30}}}) : helper)))
    + "' ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"selected") || (depth0 != null ? lookupProperty(depth0,"selected") : depth0)) != null ? helper : alias2),(options={"name":"selected","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":15,"column":32},"end":{"line":15,"column":66}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":15,"column":67},"end":{"line":15,"column":76}}}) : helper)))
    + "</option>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "selected";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div class='well'>\n	<form name='criterion'>\n		<button type=\"button\" class=\"icon only unstyled close\" title=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":85},"end":{"line":3,"column":96}}}) : helper)))
    + "\" aria-label=\"Fermer le formulaire "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":3,"column":131},"end":{"line":3,"column":142}}}) : helper)))
    + "\">\n			<svg><use href=\"/static/icons/icones.svg#times\"></use></svg>\n		</button>\n		<input type='hidden' name='type' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"type") || (depth0 != null ? lookupProperty(depth0,"type") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"type","hash":{},"data":data,"loc":{"start":{"line":6,"column":42},"end":{"line":6,"column":52}}}) : helper)))
    + "' />\n		<input type='hidden' name='key' value='"
    + alias4(((helper = (helper = lookupProperty(helpers,"key") || (depth0 != null ? lookupProperty(depth0,"key") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"key","hash":{},"data":data,"loc":{"start":{"line":7,"column":41},"end":{"line":7,"column":48}}}) : helper)))
    + "' />\n		<fieldset>\n			<legend>"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":9,"column":11},"end":{"line":9,"column":22}}}) : helper)))
    + "</legend>\n			<div class='row form-row'>\n				<div class='form-group col-md-6'>\n					<label for=\"method\">Compter les éléments</label>\n					<select name='method'>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"method_options") || (depth0 != null ? lookupProperty(depth0,"method_options") : depth0)) != null ? helper : alias2),(options={"name":"method_options","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":14,"column":6},"end":{"line":16,"column":26}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"method_options")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "					</select>\n				</div>\n				<div class=\"form-group col-md-6\">\n					<label  for='search1'>Valeur</label>\n					<input class=\"form-control\" name=\"search1\" type=\"text\" value=\""
    + alias4(((helper = (helper = lookupProperty(helpers,"search1") || (depth0 != null ? lookupProperty(depth0,"search1") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"search1","hash":{},"data":data,"loc":{"start":{"line":21,"column":67},"end":{"line":21,"column":78}}}) : helper)))
    + "\"/>\n				</div>\n			</div>\n		</fieldset>\n		<div class=\"form-actions\">\n			<button type=\"submit\" class=\"btn btn-primary btn-success\" name='submit'>Créer</button>\n			<button type=\"reset\" class=\"btn btn-danger\" name=\"cancel\">Annuler</button>\n		</div>\n	</form>\n</div>\n";
},"useData":true});
})();