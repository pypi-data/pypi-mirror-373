
var AppOptions = AppOptions || {};


// A page size tt should get all items at once
// This views does not handle pagination
const REQUEST_SIZE_LIMIT = 10000;

var CustomerModel = Backbone.Model.extend({});
var ProjectModel = Backbone.Model.extend({});

/** Build a collection URL, optionally with filters
 *
 * @param filters obj with key-value filters to request API
 * @returns {string}
 */
function mkProjectsCollectionUrl(filters) {
    let company_id = AppOptions.company_id;
    console.log('AppOptions', AppOptions, company_id);
    let url = `/api/v1/companies/${company_id}/projects`;
    if (! filters) {
        filters = {};
    }
    // use no pagination on this view
    filters.items_per_page = REQUEST_SIZE_LIMIT;
    let qs = new URLSearchParams(filters);
    return `${url}?${qs.toString()}`;
}


var ProjectCollection = Backbone.Collection.extend({
    model: ProjectModel,
});

var TaskAddProxy = {
    /*
     *
     * Handle select updates in the task add and move forms
     */
    ui: {
        customer: 'select[name=customer_id]',
        hidden_customer: 'input[name=customer_id]',
        project: 'select[name=project_id]',
        project_form_group: '.item-project_id.form-group',
        project_help_text: '.item-project_id p.help-block',
        hidden_project: 'input[name=project_id]',
        phase: 'select[name=phase_id]',
        business_type: 'select[name=business_type_id]',
        submit: 'button[type=submit]'
    },
    templates: {
        option: _.template(
            "<option value='<%= id %>' <%= selected %>><%= label%></option>"
        ),
        project_input: _.template(
            "<input type='text' name='temp_project_label' " +
                "class='form-control'" +
                "value='<%= label %>' readonly>"
        ),
        default_phase: "<option value=''>Ne pas ranger dans un sous-dossier" +
            "</option>",
        project_help_text: _.template(
            "<p class='help-block'>" +
                "Ce client n'a aucun dossier pour l'instant, vous devez commencer par " +
                "<a href='<%= create_project_url %>'>lui créer un dossier</a>."+
            "</p>"),
    },
    el: '#deform',
    getProjectLabel: function(project){
        let name = project.get('name');
        let code =  project.get('code');
        if (code) {
            return `${name} (${code})`;
        } else {
            return name;
        }
    },
    updateProject: function(projects, current_id){
        /*
         * Update the project select
         */

        let findone = this.projectCollection.get(current_id);
        var selected = current_id;

        var options = "";
        if (projects && (projects.length > 0)){
            if (_.isUndefined(findone)){
                selected = projects.models[0].id;
            }
            for (var i = 0; i < projects.models.length; i++) {
                var project = projects.models[i];
                var tmpl_values = {
                    id: project.id,
                    selected: project.id==selected ? 'selected=1' : '',
                    label: this.getProjectLabel(project)
                }
                options += this.templates['option'](tmpl_values);
            }
            this.ui.project.html(options);
            // this.ui.project.effect('highlight', {}, 1200);
            this.enableForm(true);
            // If the previously selected project is still in the list we don't
            // change
            if (_.isUndefined(findone)){
                this.ui.project.change();
            }
            this.ui.project_help_text.hide();
        } else {
            this.showProjectHelpText();
            this.ui.project.html("");
            this.enableForm(false);
            this.ui.project.change();
        }
    },
    showProjectHelpText: function() {
        let company_id = AppOptions['company_id'];
        let customer_id = this.getCustomerId();
        let url = '/companies/'+ company_id +'/projects?action=add&customer=' + customer_id;

        let project_help_text_html = this.templates['project_help_text']({
            create_project_url: url,
        });

        this.ui.project_help_text.html(project_help_text_html);
        this.ui.project_help_text.show();
    },
    enableForm: function(value){
        this.ui.submit.attr('disabled', !value);
    },
    updatePhase: function(phases){
        var options = "";
        if (phases){
            options = this.templates.default_phase;
            for (var i = 0; i < phases.length; i++) {
                var phase = phases[i];
                options += this.templates.option(
                    {id: phase.id, label: phase.name, selected:''}
                );
            }
            this.ui.phase.html(options);
            // this.ui.phase.effect('highlight', {}, 1200);
        }
    },
    updateBusinessType: function(business_types){
        var options = "";
        if (business_types){
            var btypes_length = business_types.length;
            for (var i = 0; i < btypes_length; i++) {
                var business_type = business_types[i];
                if (btypes_length == 1){
                    business_type['selected'] = 'selected';
                } else {
                    business_type['selected'] = '';
                }
                options += this.templates.option(business_type);
            }
            this.ui.business_type.html(options);
            // this.ui.business_type.effect('highlight', {}, 1200);
        }
    },
    getProjectId: function(){
        /*
         * Return the current project selected id
         */
        let current_id;
        if (this.ui.project.length !== 0) {
            current_id = this.ui.project.children('option:selected').val();
        } else {
            current_id = this.ui.hidden_project.val();
        }
        return parseInt(current_id, 10);
    },
    findProject: function(){
        let project;
        var current_id = this.getProjectId();
        if (this.getCustomerId()) {
            project = this.projectCollection.get(current_id);
        } else {
            project = undefined;
        }
        return project;
    },
    getCustomerId: function(){
        var res;
        if (this.ui.customer.length > 0){
            res = this.ui.customer.children('option:selected').val();
        } else {
            res = this.ui.hidden_customer.val();
        }
        return parseInt(res, 10);
    },
    isCustomerSet() {
        return new Boolean(this.getCustomerId()).valueOf();
    },
    isProjectSet() {
        return new Boolean(this.getProjectId()).valueOf();
    },
    getPhaseId: function(){
        var current_id = this.ui.phase.children('option:selected').val();
        return parseInt(current_id, 10);
    },
    findPhase: function(){
        var project = this.findProject();
        var current_id = this.getPhaseId();
        var phase = project.phases.findWhere({id: current_id});
        return phase;
    },
    findPhase: function(){
        var project = this.findProject();
        var current_id = this.getPhaseId();
        var phase = project.phases.findWhere({id: current_id});
        return phase;
    },
    toggle_project:function(projects){
        if (!this.isCustomerSet()) {
            this.ui.project.parent().hide();
        } else {
            this.ui.project.parent().show();
            if (! _.isUndefined(projects)){
                $('input[name=temp_project_label]').remove();
                if (projects.length == 1){
                    var project = projects[0];
                    var label = this.getProjectLabel(project);
                    this.ui.project.after(
                        this.templates['project_input']({label: label})
                    );
                    this.ui.project.hide();
                }
                else {
                    this.ui.project.show();
                }
            }
        }
    },
    toggle_phase:function(phases){
        /*
         * Toggle phase visibility and disable it if necessary
         *
         * :param list phases: List of phase objects (not including the default
         * one : "Ne pas ranger ...")
         */
        var disabled = true;
        var visible = false;
        if (! _.isUndefined(phases)){
            if (phases.length >= 1){
                disabled = false;
                visible = true;
            }
        }
        this.ui.phase.attr('disabled', disabled);
        this.ui.phase.parent().toggle(visible);
    },
    toggle_business_type:function(business_types){
        /*
         * Only show business_type selector if needed (more than one option)
         */
        var disabled = true;
        var visible = true;

        if (! this.isProjectSet()) {
            visible = false;
        } else if (! _.isUndefined(business_types)){
            if (business_types.length <= 1){
                visible = false;
            }
            disabled = false;
        }
        this.ui.business_type.attr('disabled', disabled);
        this.ui.business_type.parent().toggle(visible);
    },
    initializeProjectCollection(customerId){
        if (customerId) {
            this.projectCollection = new ProjectCollection();
            this.projectCollection.url = mkProjectsCollectionUrl(
                {customer_id: customerId},
            );
           return this.projectCollection.fetch();
        }
    },
    customerChange: function(event){
        this.toggle_phase();
        this.toggle_project();
        this.toggle_business_type();
        let projects;
        var customerId = this.getCustomerId()
        var project_id = this.getProjectId();
        if (customerId) {
            const collectionRequest = this.initializeProjectCollection(customerId);
            collectionRequest.then(
                () => {
                this.updateProject(this.projectCollection, project_id);
                this.toggle_project(this.projectsCollection);
                }
            );
        }
    },
    projectChange: function(event){
        this.toggle_phase();
        this.toggle_business_type();
        var project = this.findProject();
        if (!_.isUndefined(project)){
            var phases = project.get('phases');
            this.updatePhase(phases);
            this.toggle_phase(phases);
            var business_types = project.get('business_types');
            this.updateBusinessType(business_types);
            this.toggle_business_type(business_types);
        } else {
            this.updatePhase([]);
            this.updateBusinessType([]);
        }
    },
    setupUi: function(){
        var this_ = this;
        this.$el = $(this.el);
        _.each(this.ui, function(value, key){
            this_.ui[key] = this_.$el.find(value);
        });
        if (this.ui.project.length > 0){
            this.ui.customer.off('change.customer');
            this.ui.customer.on(
                'change.customer',
                _.bind(this.customerChange, this)
            );
            this.ui.project.off('change.project');
            this.ui.project.on(
                'change.project',
                _.bind(this.projectChange, this)
            );
        }
        // Si aucun projet n'est défini
        // on a une liste de projets et qu'aucun n'est sélectionné
        // on laisse le user sélectionner le
        // projet avant d'afficher les affaires
        // (si on a pas une liste de projet c'est qu'on en a un seul)
        if (! this.isProjectSet()) {
            this.toggle_business_type([]);
        }
        if (this.ui.business_type.find('option').length <= 1) {
            this.toggle_business_type([]);
        }
        if (this.ui.phase.find('option').length <= 1) {
            this.toggle_phase([]);
        }
        this.toggle_project();

        if (this.ui.project_help_text.length == 0){
            this.ui.project_form_group.append(
                // Wrong link, but hidden anyway...
                this.templates['project_help_text'](create_project_url='#')
            );
            this.ui.project_help_text = this.ui.project_form_group.find('.help-block');
            this.ui.project_help_text.hide();
        }
    },
    setup: function(){
        this.setupUi();
        this.projectCollection = null;
        this.initializeProjectCollection(this.getCustomerId());
    }
};

$(function(){
    TaskAddProxy.setup();
});
