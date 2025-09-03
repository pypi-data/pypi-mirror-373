<%doc>
Search form layout template
</%doc>

<%def name="searchform()">
    % if form is not UNDEFINED and form:
        <div class='collapsible search_filters'>
            <h2 class='collapse_title'>
            <a href='javascript:void(0);' onclick='toggleCollapse( this );' aria-expanded='true' accesskey='R' title='Masquer les champs de recherche' aria-label='Masquer les champs de recherche'>
                <span class="icon">${api.icon('search')}</span>
                Recherche
                ${api.icon('chevron-down','arrow')}
            </a>
            % if '__formid__' in request.GET:
                <span class='help_text'>
                    <small><em>Des filtres sont actifs</em></small>
                </span>
                <span class='help_text'>
                    <a href="${request.current_route_path(_query={})}">
                        ${api.icon('times')}
                        Supprimer tous les filtres
                    </a>
                </span>
            % endif
            </h2>
            <div class='collapse_content'>
                <div>
                    ${form|n}
                </div>
            </div>
        </div>
    % endif
</%def>
