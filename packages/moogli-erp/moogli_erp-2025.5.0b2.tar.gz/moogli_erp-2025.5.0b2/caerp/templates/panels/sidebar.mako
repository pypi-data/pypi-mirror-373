<nav class='navbar nav-tabs vertical-tabs sidebar-menu'>
<ul class='nav nav-left'>
% for menu_item in menu.items:
    ${request.layout_manager.render_panel(
      'sidebar_item',
      context=current,
      menu_item=menu_item,
      bind_params=menu.bind_params,
    )}
% endfor
</ul>
</nav>
