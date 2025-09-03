<!-- DEPENSES EN ATTENTE DE VALIDATION -->
<div class="dash_elem">
    <h2>
        <span class='icon'>${api.icon('credit-card')}</span>
        <a href="/expenses" title="Voir toutes les Notes de dépense">
            <span>Notes de dépense en attente de validation</span>
            ${api.icon('arrow-right')}
        </a>
    </h2>
    <div class='panel-body'>
        % if expenses:
        <table class="hover_table">
        % else:
        <table>
        % endif
            <caption class="screen-reader-text">Liste des notes de dépenses en attente de validation</caption>
            % if expenses:
            <thead>
                <tr>
                    <th scope="col" class="col_text">Période</th>
                    <th scope="col" class="col_text">Entrepreneur</th>
                    <th scope="col" class="col_date"><span class="no_tablet">Demandé </span>le</th>
                </tr>
            </thead>
            % endif
            <tbody>
                % for expense in expenses:
                    <%
                    tooltip_title = "Voir la note de dépenses : {} {} ".format(api.month_name(expense.month), expense.year)
                    if expense.title:
                        tooltip_title += "({}) ".format(expense.title)
                    tooltip_title += "pour {}".format(api.format_account(expense.user))
                    %>
                    <tr>
                        <td class="col_text"><a href="${expense.url}" title="${tooltip_title}" aria-label="${tooltip_title}">${api.month_name(expense.month).capitalize()} ${expense.year}</a></td>
                        <td class="col_text clickable-cell" data-href="${expense.url}" title="${tooltip_title}">${api.format_account(expense.user)}</td>
                        <td class="col_date clickable-cell" data-href="${expense.url}" title="${tooltip_title}">${api.format_date(expense.status_date)}</td>
                    </tr>
                % endfor
                % if not expenses:
                    <tr><td class="col_text" colspan='3'><em>Aucune note de dépenses en attente</em></td></tr>
                % endif
            </tbody>
        </table>
    </div>
</div>

