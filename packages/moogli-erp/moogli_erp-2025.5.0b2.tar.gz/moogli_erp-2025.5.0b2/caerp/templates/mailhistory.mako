<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name="content">

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="top_align_table hover_table">
            <thead>
                <tr>
                    <th scope="col">Identifiant</th>
                    <th scope="col" class="col_text">Enseigne</th>
                    <th scope="col" class="col_text">Période</th>
                    <th scope="col" class="col_text">Nom du fichier</th>
                    <th scope="col" class="col_date">Envoyé le</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
                % for mail in records:
                    <tr>
                        <td>${mail.id}</td>
                        <td class="col_text">${mail.company.full_label}</td>
                        <td class="col_text">${api.month_name(int(mail.month))} ${mail.year}</td>
                        <td class="col_text">${mail.filename}</td>
                        <td class="col_date">${api.format_datetime(mail.send_at)}</td>
                        <td class="col_actions width_one">
                            <%utils:post_action_btn url="${request.route_path('mail', id=mail.id)}"
                              _class="btn btn-success"
                            >
                                Renvoyer
                            </%utils:post_action_btn>
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
