<%inherit file="${context['main_template'].uri}" />

<%block name='content'>
    <div class="table_container content_vertical_double_padding">
        <h2>Favoris</h2>
        <% no_favorites = True %>
        <table>
            % for query in queries:
                % if query['favorite'] and not query['hidden']:
                    <tr>
                        <td class="col_text"><a href="dataqueries/${query['name']}">${query['label']}</a></td>
                        <td class="col_actions width_two">
                            <a class="btn icon only" href="dataqueries?favorite=0&query=${query['name']}" title="Retirer des favoris" aria-label="Retirer des favoris">${api.icon('star')}</a>
                            <a class="btn icon only" href="dataqueries?hidden=1&query=${query['name']}" title="Masquer" aria-label="Masquer">${api.icon('eye-slash')}</a>
                        </td>
                    </tr>
                    <% no_favorites = False %>
                % endif
            % endfor
        </table>
        % if no_favorites:
            <p><em>Aucune requête mise en favori</em></p>
        % endif
    </div>

    <hr />

    <div class="table_container content_vertical_double_padding">
        <table>
            % for query in queries:
                % if not query['favorite'] and not query['hidden']:
                    <tr>
                        <td class="col_text"><a href="dataqueries/${query['name']}">${query['label']}</a></td>
                        <td class="col_actions width_two">
                            <a class="btn icon only" href="dataqueries?favorite=1&query=${query['name']}" title="Mettre en favori" aria-label="Mettre en favori">${api.icon('star-empty')}</a>
                            <a class="btn icon only" href="dataqueries?hidden=1&query=${query['name']}" title="Masquer" aria-label="Masquer">${api.icon('eye-slash')}</a>
                        </td>
                    </tr>
                % endif
            % endfor
        </table>
    </div>

    <hr class="content_vertical_double_padding" />

    <div class="content_vertical_double_padding collapsible">
        <h4 class="collapse_title">
            <a href="javascript:void(0);" onclick='toggleCollapse( this );' aria-expanded="false" title="Afficher les requêtes masquées" aria-label="Afficher les requêtes masquées">
                <small>Requêtes masquées</small>
                ${api.icon('chevron-down','arrow')}
            </a>
        </h4>
        <div class="content_vertical_double_padding" hidden>
            <div class="content table_container">
                <% no_hidden = True %>
                <table>
                    % for query in queries:
                        % if query['hidden']:
                            <tr>
                                <td class="col_text min14"><a href="dataqueries/${query['name']}">${query['label']}</a></td>
                                <td class="col_actions width_two">
                                    <a class="btn icon only" href="dataqueries?hidden=0&query=${query['name']}" title="Afficher" aria-label="Afficher">${api.icon('eye')}</a>
                                </td>
                            </tr>
                            <% no_hidden = False %>
                        % endif
                    % endfor
                </table>
                % if no_hidden:
                    <p><em>Aucune requête masquée</em></p>
                % endif
            </div>
        </div>
    </div>

</%block>
