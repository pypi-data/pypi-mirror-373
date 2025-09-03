<%inherit file="${context['main_template'].uri}" />
<%block name="headtitle">
    <h1>
        <span class="icon invalid">${api.icon('warning')}</span> ${title}
    </h1>
</%block>
<%block name="content">
    <div class="content_vertical_double_padding align_center">
        <h2 class="content_vertical_double_padding">
            Votre navigateur n'est pas compatible avec MoOGLi
        </h2>
        <p class="content_vertical_double_padding">
            <big>༼ ༎ຶ ෴ ༎ຶ༽</big>
        </p>
        <p class="content_vertical_double_padding">
            Malheureusement votre navigateur <strong>${browser_name}</strong> version <strong>${browser_version}</strong> ne supporte pas certaines technologies modernes requises par l’application.
        </p>
        <p class="content_vertical_double_padding">
            % if browser_name == "Firefox":
                Vous pouvez essayer de le mettre à jour en téléchargeant la dernière version depuis le site : 
            % else:
                Il est conseillé d'utiliser le navigateur <strong>Firefox</strong> pour utiliser MoOGLi. Vous pouvez le télécharger depuis le site : 
            % endif
            <a href="https://www.mozilla.org/fr/firefox/browsers/" target="_blank">https://www.mozilla.org/fr/firefox/browsers/</a>
        </p>
        <hr />
        <p class="content_vertical_double_padding">
            <small><strong>Informations techniques : </strong>${user_agent}</small>
        </p>
    </div>

    <div class="content_vertical_double_padding align_center collapsible">
        <h2 class="title collapse_title">
            <a href="javascript:void(0);" onclick="toggleCollapse( this );" aria-expanded="false" title="Afficher le moyen d’accéder quand même à MoOGLi" aria-label="Afficher le moyen d’accéder quand même à MoOGLi">
                <small>> Accéder quand même à MoOGLi</small>
            </a>
        </h2>
        <div class="collapse_content" hidden>
            <div class="content">
                <form action="/login" method="post" class="content_vertical_double_padding">
                    <div>
                        <p>Si vous souhaitez malgré tout accéder à MoOGLi, bien que cela pourrait entrainer des erreurs, vous pouvez outrepasser le contrôle de support du navigateur.</p>
                    </div>
                    <div>
                        <label for="force_support">
                            <input type="checkbox" name="force_support" id="force_support" required /> 
                            Je comprend qu'en poursuivant l'utilisation de MoOGLi avec ce navigateur des problèmes pourraient survenir sur certaines pages
                        </label>
                    </div>
                    <div>
                        <button type="submit" class="btn">Accéder à MoOGLi</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</%block>
