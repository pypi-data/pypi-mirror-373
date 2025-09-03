(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['empty.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<td class='col_text' colspan='3'><em>Aucun congés n'a été saisi</em></td>\n";
},"useData":true});
templates['holiday.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<td class=\"col_date\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"alt_start_date") || (depth0 != null ? lookupProperty(depth0,"alt_start_date") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"alt_start_date","hash":{},"data":data,"loc":{"start":{"line":1,"column":21},"end":{"line":1,"column":41}}}) : helper)))
    + "</td>\n<td class=\"col_date\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"alt_end_date") || (depth0 != null ? lookupProperty(depth0,"alt_end_date") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"alt_end_date","hash":{},"data":data,"loc":{"start":{"line":2,"column":21},"end":{"line":2,"column":39}}}) : helper)))
    + "</td>\n<td class=\"col_actions width_two\">\n	<ul>\n		<li>\n			<a class='btn icon only edit' title='Modifier' aria-label='Modifier'><svg><use href=\"/static/icons/icones.svg#pen\"></use></svg></a>\n		</li>\n		<li>\n			<a class='btn icon only negative remove' title='Supprimer' aria-label='Supprimer'><svg><use href=\"/static/icons/icones.svg#trash-alt\"></use></svg></a>\n		</li>\n	</ul>\n</td>\n";
},"useData":true});
templates['holidayForm.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<form id='holidayForm' class='form' action='#' onsubmit='return false;'>\n<div class=\"form-group\">\n<label class=\"control-label\" for='alt_start_date'>Début</label>\n<div class='controls'>\n    <input name=\"alt_start_date\" class=\"input-small\" type=\"text\" autocomplete=\"off\">\n    <input name=\"start_date\" type=\"hidden\">\n</div>\n</div>\n<div class=\"form-group\">\n<label class=\"control-label\" for='alt_end_date'>Fin</label>\n<div class='controls'>\n    <input name=\"alt_end_date\" class=\"input-small\" type=\"text\" autocomplete=\"off\">\n    <input name=\"end_date\" type=\"hidden\">\n</div>\n</div>\n\n<div class=\"form-actions\">\n<button type=\"submit\" class=\"btn btn-primary\" name='submit'>Valider</button>\n<button type=\"reset\" class=\"btn\" name=\"cancel\">Annuler</button>\n</div>\n</form>\n";
},"useData":true});
templates['holidayList.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "    <div class='table_container limited_width width40'>\n        <table class=\"opa hover_table\">\n            <thead>\n            	<tr>\n					<th scope=\"col\" class=\"col_date\">Date de début</th>\n					<th scope=\"col\" class=\"col_date\">Date de fin</th>\n					<th scope=\"col\" class=\"col_actions\" title=\"Actions\"><span class=\"screen-reader-text\">Actions</span></th>\n            	</tr>\n            </thead>\n            <tbody>\n            </tbody>\n            <tfoot>\n            	<tr>\n            		<td class=\"col_actions\" colspan=\"3\">\n						<a href=\"javascript:void(0);\" class='btn btn-primary add' title=\"Déclarer un congés\" aria-label=\"Déclarer un congés\">\n							<svg><use href=\"/static/icons/icones.svg#plus\"></use></svg>Ajouter\n						</a>\n            		</td>\n            	</tr>\n            </tfoot>\n        </table>\n    </div>\n";
},"useData":true});
})();