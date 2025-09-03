% if activities:
    <div class='message neutral'>
        <p>
            <span class="icon" role="presentation">${api.icon('info-circle')}</span>
            Vous avez ${len(activities)} rendez-vous programmés&nbsp;:
        </p>
        <ul class='list_count activities layout flex two_cols'>
        % for activity in activities[:5]:
            <li>
                <a href="${activity.url}">
                    <span class='activity_time'>${api.format_datetime(activity.datetime)}</span>
                    <span>${', '.join(api.format_account(p) for p in activity.participants)}</span>
                </a>
            </li>
            % endfor
        </ul>
    </div>
% endif

