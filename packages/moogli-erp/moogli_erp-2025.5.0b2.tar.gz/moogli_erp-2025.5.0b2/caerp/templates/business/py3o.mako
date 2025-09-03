<%inherit file="${context['main_template'].uri}" />
<%block name="mainblock">

<div id="business_py3o_tab">
    % if help_message is not UNDEFINED and help_message is not None:
        <div class='alert alert-info'>
            <span class="icon">${api.icon('info-circle')}</span>
            ${help_message | n}
        </div>
    % endif

    <br/>

    % if templates == []:
        <div class='alert alert-warning'>
            <span class="icon">${api.icon('exclamation-triangle')}</span>
            Aucun modèle de document disponible pour ce type d'affaire.
        </div>
    % else:
        <ul>
        % for template in templates:
            <% url = request.current_route_path(_query=dict(file=template.file_type_id)) %>
            <li>
                <a href="${url}" class="icon">
                    ${api.icon('file-alt')}
                    ${template.file_type.label} &nbsp; ( ${template.file.description} )
                </a>
            </li>
        % endfor
        </ul>
    % endif
</div>

</%block>
