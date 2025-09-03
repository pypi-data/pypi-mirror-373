<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_text" />

<%block name='beforecontent'>
<div class='main_toolbar nav_tools'>
    <ul class="nav nav-pills">
        <li>            
            <a title="Liste des requêtes statistiques" href="/dataqueries">
                Liste des requêtes statistiques
            </a>
        </li>
    </ul>
</div>
</%block>

<%block name='content'>
    <h1>${label}</h1>
    <div class="alert alert-info">${format_text(description, breaklines=False)}</div>
    <br />
    <div class="content_vertical_double_padding">
        <form name="query_generation" method="get">
            <strong>
            Exécuter la requête 
            % if start_date and end_date:
                du 
                <input type="date" name="start" value="${start_date}" class="hasDatepicker">
                au
                <input type="date" name="end" value="${end_date}" class="hasDatepicker">
            % elif start_date:
                au 
                <input type="date" name="start" value="${start_date}" class="hasDatepicker">
            % endif
            &nbsp;
            </strong>
            <button name="format" type="submit" class="btn btn-primary icon" value="display" title="Prévisualiser le résultat dans le navigateur" aria-label="Prévisualiser le résultat dans le navigateur">
                ${api.icon('eye')} Prévisualiser
            </button>
            <button name="format" type="submit" class="btn btn-primary icon" value="xls" title="Exporter le résultat au format Excel (xlsx)" aria-label="Exporter le résultat au format Excel (xlsx)">
                ${api.icon('file-excel')} Excel
            </button>
            <button name="format" type="submit" class="btn btn-primary icon" value="ods" title="Exporter le résultat au format ODS" aria-label="Exporter le résultat au format ODS">
                ${api.icon('file-spreadsheet')} ODS
            </button>
            <button name="format" type="submit" class="btn btn-primary icon" value="csv" title="Exporter le résultat au format csv" aria-label="Exporter le résultat au format csv">
                ${api.icon('file-csv')} CSV
            </button>
        </form>
    </div>
    % if data:
        <div>${len(data)} résultats</div>
        <div class="table_container">
            <button class="fullscreen_toggle small" title="Afficher le tableau en plein écran" aria-label="Afficher le tableau en plein écran" onclick="toggleTableFullscreen(this);return false;">
                ${api.icon('expand')}
                ${api.icon('compress')}
                <span>Plein écran</span>
            </button>
            <table class="spreadsheet_table">
                <thead>
                    % for header in headers:
                        <th class="col_text">${header}</th>
                    % endfor
                </thead>
                % for result in data:
                    <tr>
                        % for val in result:
                            <td class="col_text min8">${val|n}</td>
                        % endfor
                    </tr>
                % endfor
            </table>
        </div>
    % elif headers:
        <p><em>Aucun résultat</em></p>
    % endif
    <br/>
</%block>
