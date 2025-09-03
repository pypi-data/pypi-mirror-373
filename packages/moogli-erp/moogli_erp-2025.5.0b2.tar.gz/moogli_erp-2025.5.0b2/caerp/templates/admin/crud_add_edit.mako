<%doc>
    :param str form: Html formatted form

    :param str warn_msg: optionnal warning message
    :param str help_msg: optionnal help message
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class="limited_width width40">
	${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
	${form|n}
</div>
</%block>
