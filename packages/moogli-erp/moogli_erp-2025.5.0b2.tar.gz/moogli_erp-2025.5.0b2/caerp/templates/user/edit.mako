<%inherit file="${context['main_template'].uri}" />
<%block name="mainblock">
${request.layout_manager.render_panel('help_message_panel', parent_tmpl_dict=context.kwargs)}
% if before_form_elements not in (UNDEFINED, None):
<div class="col-md-12">
    % for element in before_form_elements:
        ${request.layout_manager.render_panel(element.panel_name, context=element)}
    % endfor
</div>
% endif
<div class="col-md-12">
    ${form|n}
</div>
</%block>
