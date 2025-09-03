<%inherit file="${context['main_template'].uri}" />
<%block name="content">
<div id='js-main-area'></div>
</%block>

<%block name="footerjs">
AppOption = {};
% for key, value in js_app_options.items():
AppOption["${key}"] = "${value}"
% endfor;
</%block>
