(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['item.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    };

  return "<a href=\"#/items/"
    + alias4(((helper = (helper = lookupProperty(helpers,"id") || (depth0 != null ? lookupProperty(depth0,"id") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"id","hash":{},"data":data,"loc":{"start":{"line":1,"column":17},"end":{"line":1,"column":25}}}) : helper)))
    + "/edit\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":1,"column":32},"end":{"line":1,"column":43}}}) : helper)))
    + "</a>\n";
},"useData":true});
templates['item_form.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.hooks.blockHelperMissing, alias5=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "            <th scope=\"col\" ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"is_reference") || (depth0 != null ? lookupProperty(depth0,"is_reference") : depth0)) != null ? helper : alias2),(options={"name":"is_reference","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":9,"column":28},"end":{"line":9,"column":85}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"is_reference")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  buffer += ">\n                "
    + alias5(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":10,"column":16},"end":{"line":10,"column":27}}}) : helper)))
    + " ("
    + alias5(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":10,"column":29},"end":{"line":10,"column":38}}}) : helper)))
    + ") ";
  stack1 = ((helper = (helper = lookupProperty(helpers,"is_reference") || (depth0 != null ? lookupProperty(depth0,"is_reference") : depth0)) != null ? helper : alias2),(options={"name":"is_reference","hash":{},"fn":container.program(4, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":10,"column":40},"end":{"line":10,"column":125}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"is_reference")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n            </th>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "class=\"status positive\"";
},"4":function(container,depth0,helpers,partials,data) {
    return "<span class='help-block'>Niveau de référence</span>";
},"6":function(container,depth0,helpers,partials,data) {
    return "positive";
},"8":function(container,depth0,helpers,partials,data) {
    return "caution";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<h3><small>Évaluation de la compétence&nbsp;:</small> "
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":1,"column":54},"end":{"line":1,"column":63}}}) : helper)))
    + "</h3>\n<h4><small>Pour l’échéance&nbsp;:</small> "
    + alias4(((helper = (helper = lookupProperty(helpers,"deadline_label") || (depth0 != null ? lookupProperty(depth0,"deadline_label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"deadline_label","hash":{},"data":data,"loc":{"start":{"line":2,"column":42},"end":{"line":2,"column":62}}}) : helper)))
    + "</h4>\n<form id=\"item_form\">\n<div class=\"table_container\">\n    <table>\n        <thead>\n            <th scope=\"col\" class=\"col_text\">Sous-compétence</th>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"scales") || (depth0 != null ? lookupProperty(depth0,"scales") : depth0)) != null ? helper : alias2),(options={"name":"scales","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":8,"column":12},"end":{"line":12,"column":23}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"scales")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "            <th scope=\"col\" class=\"col_text\">Argumentation, Preuves</th>\n        </thead>\n        <tbody>\n        </tbody>\n    </table>\n    <div class='content_padding align_center status_block "
    + ((stack1 = lookupProperty(helpers,"if").call(alias1,(depth0 != null ? lookupProperty(depth0,"is_ok_average") : depth0),{"name":"if","hash":{},"fn":container.program(6, data, 0),"inverse":container.program(8, data, 0),"data":data,"loc":{"start":{"line":18,"column":58},"end":{"line":18,"column":109}}})) != null ? stack1 : "")
    + "'>\n        Évaluation : "
    + alias4(((helper = (helper = lookupProperty(helpers,"average_level") || (depth0 != null ? lookupProperty(depth0,"average_level") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"average_level","hash":{},"data":data,"loc":{"start":{"line":19,"column":21},"end":{"line":19,"column":40}}}) : helper)))
    + "\n    </div>\n</div>\n<div class='form-group'>\n    <label for=\"comments\">Axes de progrès pour cette échéance</label>\n    <textarea name='progress' class='form-control'>"
    + alias4(((helper = (helper = lookupProperty(helpers,"progress") || (depth0 != null ? lookupProperty(depth0,"progress") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"progress","hash":{},"data":data,"loc":{"start":{"line":24,"column":51},"end":{"line":24,"column":65}}}) : helper)))
    + "</textarea>\n</div>\n<button type='button' class='btn btn-primary'>OK</button>\n</form>\n";
},"useData":true});
templates['item_list.mustache'] = template({"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<h4>Compétences à évaluer</h4>\n<ul class=\"nav nav-tabs vertical-tabs\">\n</ul>\n";
},"useData":true});
templates['subitem.mustache'] = template({"1":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var stack1, helper, options, alias1=container.escapeExpression, alias2=depth0 != null ? depth0 : (container.nullContext || {}), alias3=container.hooks.helperMissing, alias4="function", lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<td>\n	<div class=\"radio\">\n		<label>\n			<input\n				type=\"radio\"\n				name=\"subitem_"
    + alias1(container.lambda((depths[1] != null ? lookupProperty(depths[1],"id") : depths[1]), depth0))
    + "\"\n				";
  stack1 = ((helper = (helper = lookupProperty(helpers,"is_selected") || (depth0 != null ? lookupProperty(depth0,"is_selected") : depth0)) != null ? helper : alias3),(options={"name":"is_selected","hash":{},"fn":container.program(2, data, 0, blockParams, depths),"inverse":container.noop,"data":data,"loc":{"start":{"line":9,"column":4},"end":{"line":9,"column":43}}}),(typeof helper === alias4 ? helper.call(alias2,options) : helper));
  if (!lookupProperty(helpers,"is_selected")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n				value=\""
    + alias1(((helper = (helper = lookupProperty(helpers,"value") || (depth0 != null ? lookupProperty(depth0,"value") : depth0)) != null ? helper : alias3),(typeof helper === alias4 ? helper.call(alias2,{"name":"value","hash":{},"data":data,"loc":{"start":{"line":10,"column":11},"end":{"line":10,"column":22}}}) : helper)))
    + "\">\n				<span><span class=\"screen-reader-text\">"
    + alias1(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias3),(typeof helper === alias4 ? helper.call(alias2,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":11,"column":43},"end":{"line":11,"column":54}}}) : helper)))
    + "<span><span>\n			</input>\n		</label>\n	</div>\n</td>\n";
},"2":function(container,depth0,helpers,partials,data) {
    return "checked";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.escapeExpression, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<td class=\"col_text\">"
    + alias4(((helper = (helper = lookupProperty(helpers,"label") || (depth0 != null ? lookupProperty(depth0,"label") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"label","hash":{},"data":data,"loc":{"start":{"line":1,"column":21},"end":{"line":1,"column":30}}}) : helper)))
    + "</td>\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"scales") || (depth0 != null ? lookupProperty(depth0,"scales") : depth0)) != null ? helper : alias2),(options={"name":"scales","hash":{},"fn":container.program(1, data, 0, blockParams, depths),"inverse":container.noop,"data":data,"loc":{"start":{"line":2,"column":0},"end":{"line":16,"column":11}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"scales")) { stack1 = container.hooks.blockHelperMissing.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "<td class=\"col_text\">\n<div class='form-group'>\n    <textarea name='comments' class='form-control' label='Argumentation, preuves'>"
    + alias4(((helper = (helper = lookupProperty(helpers,"comments") || (depth0 != null ? lookupProperty(depth0,"comments") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"comments","hash":{},"data":data,"loc":{"start":{"line":19,"column":82},"end":{"line":19,"column":96}}}) : helper)))
    + "</textarea>\n</div>\n</td>\n";
},"useData":true,"useDepths":true});
})();