<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='content'>

${searchform()}

<div>
    <div>
    	${records.item_count} Résultat(s)
    </div>
    <div class='alert alert-warning'>
        <span class="icon">${api.icon('danger')}</span>
        Lors de la clôture comptable (et principalement lors de la saisie des reports d’à-nouveaux) n’oubliez pas d’indiquer à MoOGLi que la clôture a été faite sans quoi les calculs des états de trésorerie seraient erronnés.<br />
        Voir dans le menu suivant : <a href='/admin/accounting/accounting_closure' target="_blank" title="Cet écran s’ouvrira dans une nouvelle fenêtre" aria-label="Cet écran s’ouvrira dans une nouvelle fenêtre">Configuration -> Configuration -> Module Comptabilité -> Clôtures comptables</a>.
    </div>
	<div class='alert alert-info'>
        <span class="icon">${api.icon('info-circle')}</span>
		Vous trouverez ci-dessous la liste des fichiers comptables ou synchronisations automatiques traités par MoOGLi.<br />
		Les écritures présentes dans les fichiers comptables ou dans les données synchronisées sont importées dans MoOGLi par un automate en "tâche de fond".<br /><br />
		Après le traitement, vous avez dû recevoir un e-mail de compte rendu à l'adresse d'administration configurée dans
		<a href="#" onclick="window.openPopup('/admin/main/contact');" title="Cet écran s’ouvrira dans une nouvelle fenêtre" aria-label="Cet écran s’ouvrira dans une nouvelle fenêtre">Configuration -> Configuration générale -> Adresse e-mail de contact MoOGLi</a><br /><br />
		Depuis les écritures importées, il est possible de générer des indicateurs :
		<ul>
			<li>
				<a href="/admin/accounting/treasury_measures" target="_blank" title="Cet écran s’ouvrira dans une nouvelle fenêtre" aria-label="Cet écran s’ouvrira dans une nouvelle fenêtre">
					Configuration-> Configuration du module Fichiers comptables -> Configuration des indicateurs de trésorerie
				</a>
				&nbsp;Pour les États de trésorerie (générés depuis la balance analytique)
			</li>
			<li>
				<a href="/admin/accounting/income_statement_measures" target="_blank" title="Cet écran s’ouvrira dans une nouvelle fenêtre" aria-label="Cet écran s’ouvrira dans une nouvelle fenêtre">
					Configuration-> Configuration du module Fichiers comptables -> Configuration des indicateurs de compte de résultat
				</a>
				&nbsp;Pour les Comptes de résultat (générés depuis le grand livre)
			</li>
		</ul><br />
		<strong>NB : </strong>
		<ul>
			<li>Dans le cas des fichiers déposés, les indicateurs sont générés automatiquement</li>
			<li>Dans le cas de la synchronisation automatique, la génération des indicateurs est à l'initiative de l'équipe comptable de la CAE.</li>
		</ul><br /><br />
		Depuis la liste ci-dessous, vous pouvez :
		<ul>
			<li>Supprimer les données importées et les indicateurs associés si une erreur s'est produite (données mal associées par exemple)</li>
			<li>Recalculer les indicateurs si vous avez modifié la configuration des indicateurs</li>
		</ul>
	</div>
    <div class='table_container'>
		% if records:
		<table class="hover_table">
			<thead>
				<tr>
					<th scope="col" class="col_text">Type de remontée</th>
					<th scope="col" class="col_text">${sortable("Date d'export", "date")}</th>
					<th scope="col" class="col_text">${sortable("Nom du fichier", "filename")}</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
			<tbody>
			% for entry in records:
				<tr class='tableelement' id='${entry.id}'>
					<td class="col_text">${entry.filetype_label}</td>
					<td class="col_text">
						% if entry.filetype != 'synchronized_accounting':
							Données du ${api.format_date(entry.date)}
							(Importées le ${api.format_date(entry.updated_at)})
						% else:
							Données mises à jour le ${api.format_date(entry.updated_at)}
						% endif
					</td>
					<td class="col_text">${entry.filename}</td>
					${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(entry))}
				</tr>
			% endfor
			</tbody>
		</table>
		% else:
		<table>
			<tbody>
				<tr>
					<td class='col_text'><em>Aucun fichier n’a été traité</em></td>
				</tr>
			</tbody>
		</table>
		% endif
    </div>
    ${pager(records)}
</div>
</%block>
