<li class="${li_css}"> 
% if plus_button:
    <button onclick="this.parentNode.classList.add('open');this.removeAttribute('onclick');this.setAttribute('disabled','disabled');" class="btn icon only" title="Ajouter une facture intermédiaire" aria-label="Ajouter une facture intermédiaire">
        ${api.icon('plus')}
    </button>
    % endif
    <blockquote class="${status_css} ${time_css}">
        <span class="icon status" role="presentation">
            ${api.icon('plus')}
        </span>
        <div>
            <h5>${title}</h5>
            <div class='layout flex'>
                <p>
                    ${description}
                </p>
                <div class="btn-container">
                ${request.layout_manager.render_panel(button.panel_name, context=button)}
                </div>
            </div>
        </div>
    </blockquote>
</li>