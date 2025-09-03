
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="company_list_badges" name="utils"/>
<%block name="mainblock">
<div>
    ${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
    <div class="layout flex full content_vertical_padding separate_bottom">
    	<div class="align_right">
			${request.layout_manager.render_panel('action_buttons', links=get_buttons())}
    	</div>
	</div>
    ${form|n}
</div>
</%block>
<%block name="footerjs">
    setAuthCheckBeforeSubmit('#deform');
</%block>
