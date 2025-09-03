<%doc>
Render an action menu
</%doc>
% if elem.items:
    <ul class='nav nav-pills'>
    % for item in elem.items:
        <li>
        % if hasattr(item, 'panel_name'):
            ${request.layout_manager.render_panel(item.panel_name, context=item)}
        % elif hasattr(item, 'render'):
            ${item.render(request)|n}
        % else:
            ${item|n}
        % endif
        </li>
    % endfor
    </ul>
% endif
