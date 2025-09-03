(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['serverMessage.mustache'] = template({"1":function(container,depth0,helpers,partials,data) {
    return "class=\"alert alert-danger\">\n<span class=\"icon\"><svg><use href=\"/static/icons/icones.svg#danger\"></use></svg></span> \n";
},"3":function(container,depth0,helpers,partials,data) {
    return "class=\"alert alert-success\">\n<span class=\"icon\"><svg><use href=\"/static/icons/icones.svg#success\"></use></svg></span> \n";
},"compiler":[8,">= 4.3.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, options, alias1=depth0 != null ? depth0 : (container.nullContext || {}), alias2=container.hooks.helperMissing, alias3="function", alias4=container.hooks.blockHelperMissing, lookupProperty = container.lookupProperty || function(parent, propertyName) {
        if (Object.prototype.hasOwnProperty.call(parent, propertyName)) {
          return parent[propertyName];
        }
        return undefined
    }, buffer = 
  "<div\n";
  stack1 = ((helper = (helper = lookupProperty(helpers,"error") || (depth0 != null ? lookupProperty(depth0,"error") : depth0)) != null ? helper : alias2),(options={"name":"error","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data,"loc":{"start":{"line":2,"column":0},"end":{"line":5,"column":10}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"error")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  stack1 = ((helper = (helper = lookupProperty(helpers,"error") || (depth0 != null ? lookupProperty(depth0,"error") : depth0)) != null ? helper : alias2),(options={"name":"error","hash":{},"fn":container.noop,"inverse":container.program(3, data, 0),"data":data,"loc":{"start":{"line":6,"column":0},"end":{"line":9,"column":10}}}),(typeof helper === alias3 ? helper.call(alias1,options) : helper));
  if (!lookupProperty(helpers,"error")) { stack1 = alias4.call(depth0,stack1,options)}
  if (stack1 != null) { buffer += stack1; }
  return buffer + "<button class=\"icon only unstyled close\" data-dismiss=\"alert\" type=\"button\" title=\"Masquer ce message\" aria-label=\"Masquer ce message\"><svg><use href=\"/static/icons/icones.svg#times\"></use></svg></button>\n"
    + container.escapeExpression(((helper = (helper = lookupProperty(helpers,"msg") || (depth0 != null ? lookupProperty(depth0,"msg") : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"msg","hash":{},"data":data,"loc":{"start":{"line":11,"column":0},"end":{"line":11,"column":7}}}) : helper)))
    + "\n</div>\n";
},"useData":true});
})();