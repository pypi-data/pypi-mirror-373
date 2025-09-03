<%doc>
pager template
</%doc>
<%def name="pager(items)">
<div class="pager">
  <% link_attr={"class": "btn"} %>
  <% curpage_attr={"class": "current","title": "Page en cours","aria-label": "Page en cours"} %>
  <% dotdot_attr={"class": "spacer"} %>

  ${items.pager(format="$link_previous ~2~ $link_next",
  link_attr=link_attr,
  curpage_attr=curpage_attr,
  dotdot_attr=dotdot_attr)|n}
</div>
</%def>
<%def name="sortable(label, column, short_label=None)">
<% sort_column = request.GET.get("sort", "") %>
<% sort_direction = request.GET.get("direction", "asc") %>
%if (column == sort_column):
  <% css_class = "current " + sort_direction %>
%else:
  <% css_class = ""%>
%endif
%if sort_direction == "asc":
  <% direction = "desc" %>
  <% current_direction = "croissant" %>
  <% target_direction = "décroissant" %>
%else:
  <% direction = "asc" %>
  <% current_direction = "décroissant" %>
  <% target_direction = "croissant" %>
%endif
<% args_dict = dict(direction=direction, sort=column, current_direction=current_direction, target_direction=target_direction) %>

  %if column == sort_column:
  <% sort_direction_icon = "sort-" + str(sort_direction) %>
  <a href="${api.urlupdate(args_dict)}" class='icon ${css_class}' aria-label='Trié par ${label} (ordre ${current_direction}) - cliquer pour inverser l’ordre' title='Trié par ${label} (ordre ${current_direction}) - cliquer pour inverser l’ordre'>
    ${api.icon(sort_direction_icon,sort_direction)}
  %else:
  <a href="${api.urlupdate(args_dict)}" class='icon ${css_class}' aria-label='Trier par ${label} (ordre ${target_direction})' title='Trier par ${label} (ordre ${target_direction})'>
    ${api.icon('sort-arrow')}
  %endif
  %if short_label:
  ${short_label}
  %else:
  ${label}
  %endif
  </a>
</%def>
