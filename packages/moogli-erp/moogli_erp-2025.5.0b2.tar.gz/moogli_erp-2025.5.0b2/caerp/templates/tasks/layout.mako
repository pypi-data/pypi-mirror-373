<%inherit file="/layouts/default.mako" />
<% task =  layout.current_task_object %>

<%block name="headtitle">
${request.layout_manager.render_panel('task_title_panel', title=layout.title)}
</%block>
<%block name='actionmenucontent'>
<div class='main_toolbar action_tools'>
    <div class='layout flex main_actions'>
        ${request.layout_manager.render_panel('action_buttons', links=layout.stream_main_actions())}
        ${request.layout_manager.render_panel('action_buttons', links=layout.stream_more_actions())}
    </div>
</div>
</%block>

<%block name='content'>
  
    <div class='tabs'>
		<%block name='rightblock'>
			${request.layout_manager.render_panel('tabs', layout.menu)}
		</%block>
    </div>
    <div class='tab-content'>
		<%block name='mainblock'>
  
		</%block>
   </div>
</%block>
<%block name='footerjs'>
% if js_app_options is not UNDEFINED:
var AppOption = AppOption || {};
% for option, value in js_app_options.items():
${api.write_js_app_option(option, value)}
% endfor
% endif
</%block>