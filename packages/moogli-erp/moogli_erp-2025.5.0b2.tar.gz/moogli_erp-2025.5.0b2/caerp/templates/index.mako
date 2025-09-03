<%inherit file="${context['main_template'].uri}" />
<%block name='content'>
<div class='entities_choice'>
	% if companies:
    <ul class="layout flex">
		% for company in companies:
			<li>
				<a href="${company.url}" title="Accéder à la gestion de ${company.name}">
            	% if company.logo_file:
				    <div class="thumbnail">
					    <img src="${api.img_url(company.logo_file)}" title="${company.name}" alt="Logo de ${company.name}" />
					</div>
            	% endif
    				<h2><span class="screen-reader-text">Accéder à la gestion de </span>${company.name}</h2>
	    			<p>
    					${company.goal}
    				</p>
				</a>
			</li>
		% endfor
	</ul>
	%else:
	<div class="alert alert-info">
		<span class="icon">${api.icon('info-circle')}</span>
		Aucune enseigne n’a été configurée pour ce compte
	<div>
	% endif
</div>
</%block>
