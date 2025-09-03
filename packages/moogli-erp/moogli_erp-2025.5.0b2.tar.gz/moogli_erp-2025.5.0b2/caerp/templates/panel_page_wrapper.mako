<%doc>
    Wrap a given panel
    Should be returned from an ajax call
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
${request.layout_manager.render_panel(panel_name)}
</%block>
