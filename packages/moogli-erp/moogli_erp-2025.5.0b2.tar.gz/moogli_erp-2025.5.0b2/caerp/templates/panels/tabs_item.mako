% if menu_item.has_permission(_context, request, **bind_params) and menu_item.visible(_context, request):

    % if menu_item.enabled(_context, request):
        <% url = menu_item.url(_context, request) %>
    % else:
        <% url = "#" %>
    % endif

    % if menu_item.selected(_context, request):
        <li role="presentation" class="active">
            <a href="${url}" title="${menu_item.title}" aria-controls="${menu_item.name}_tab" role="tab" aria-selected="true" id="${menu_item.name}">
    % elif not menu_item.enabled(_context, request):
        <li role="presentation" class="disabled">
            <a href="${url}" title="${menu_item.title}" aria-controls="${menu_item.name}_tab" role="tab" aria-selected="false" id="${menu_item.name}" tabindex="-1">
    % else:
        <li role="presentation">
            <a href="${url}" title="${menu_item.title}" aria-controls="${menu_item.name}_tab" role="tab" aria-selected="false" id="${menu_item.name}" tabindex="-1">
    % endif
    
        % if menu_item.icon:
                <span class="icon">${api.icon(menu_item.icon)}</span>&nbsp;
        % endif
                <span>${menu_item.get_label(**bind_params)|n}</span>
            </a>
        </li>

% endif
