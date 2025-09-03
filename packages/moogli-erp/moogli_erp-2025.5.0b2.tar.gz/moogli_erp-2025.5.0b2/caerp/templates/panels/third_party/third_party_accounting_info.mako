<div class='data_display'>
    <% datas = (
    ("Compte CG", third_party.compte_cg),
    ("Compte Tiers", third_party.compte_tiers),) %>
    <dl class="data_number">
        % for label, value in datas :
            <div>
                <dt>${label}</dt>
                <dd>
                    % if value:
                        ${value}
                    % else:
                        <em>Non renseigné</em>
                    % endif
                </dd>
            </div>
        % endfor
    </dl>
</div>
