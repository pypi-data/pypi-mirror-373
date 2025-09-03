<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="format_filelist_table" />
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/utils.mako" import="show_tags_label" />
<%block name="content">
    <% workshop = request.context %>
	<h2>Détails</h2>
	% if workshop.files:
	    <div class="layout flex two_cols">
	% endif
    <div>
	% if workshop.description != '':
		<div class="content_vertical_padding">
			<h3>Description</h3>
			<p>${format_text(workshop.description)}</p>
		</div>
	% endif
    % if workshop.place != '':
		<div class="content_vertical_padding">
			<h3>Lieu</h3>
			<p>${workshop.place}</p>
		</div>
	% endif
		<div class="content_vertical_padding">
	        <h3>Personnes</h3>
			<dl class="dl-horizontal">
				<dt>
					<span class="icon">${api.icon('key')}</span>
					Enseigne
				</dt>
				<dd>
					% if workshop.company_manager:
						${workshop.company_manager.name}
					% else:
						Interne CAE
					% endif
				</dd>
				<dt>
					Anime(nt)
				</dt>
				<dd>
					% if workshop.trainers:
						${', '.join([i.label for i in workshop.trainers])}
					% else:
						<em>Non renseigné</em>
					% endif
				</dd>
				<dt>
					Participent
				</dt>
				<dd>${', '.join([i.label for i in workshop.participants])}</dd>
				<dt>
				  Nombre maximum
				</dt>
				<dd>
				  % if workshop.max_participants:
					${workshop.max_participants}
				  % else:
					<em>Pas de limite</em>
				  % endif
				</dd>
			</dl>
			% if workshop.tags:
            <p>${show_tags_label(workshop.tags)}</p>
        	% endif
		</div>
    </div>
    % if workshop.files:
        <div>
	    	<h3>Fichiers attachés</h3>
			<div>
				${format_filelist_table(workshop, delete=True)}
			</div>
		</div>
    </div>
    % endif

<%block name="after_details"></%block>
<%block name="details_modal"></%block>
</%block>
