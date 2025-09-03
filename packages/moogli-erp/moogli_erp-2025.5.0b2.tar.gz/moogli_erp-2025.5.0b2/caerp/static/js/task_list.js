
var TaskModule = CaerpApp.module('TaskModule',
  function (TaskModule, CaerpApp, Backbone, Marionette, $, _) {
    TaskModule.Router = Marionette.AppRouter.extend({
      appRoutes: {
        "tasklist/:id": "get_tasks"
      }
    });
    TaskModule.Controller = {
      initialized: false,
      element: '#tasklist_container',

      initialize: function () {
        if (!this.initialized) {
          this.$element = $(this.element);
          this.initialized = true;
          _.bindAll(this, 'displayList');
        }
      },
      setNbItemsSelectBehaviour: function () {
        $('#number_of_tasks').unbind('change.tasks');
        _.bindAll(this, 'get_tasks');
        var this_ = this;
        $('#number_of_tasks').bind("change.tasks",
          function () {
            this_.get_tasks(1);
          }
        );
      },
      index: function () {
        this.initialize();
        this.setNbItemsSelectBehaviour();
      },
      get_tasks: function (id) {
        this.initialize();
        this.refresh_list(id);
      },
      refresh_list: function (page_num) {
        url = '?action=tasks_html';
        var items_per_page = $('#number_of_tasks').val();
        postdata = {
          'tasks_page_nb': page_num,
          'tasks_per_page': items_per_page
        };
        var this_ = this;
        $.ajax(
          url,
          {
            type: 'POST',
            data: postdata,
            dataType: 'html',
            success: function (data) {
              this_.displayList(data);
            },
            error: function () {
              displayServerError("Une erreur a été rencontrée lors de " +
                "la récupération des dernières activités");
            }
          }
        );
      },
      displayList: function (data) {
        this.$element.html(data);
        this.setNbItemsSelectBehaviour();
      }
    };
    TaskModule.on('start', function () {
      TaskModule.router = new TaskModule.Router(
        { controller: TaskModule.Controller }
      );
      TaskModule.Controller.index();
    });
  });

$(function () {
  CaerpApp.start();
});
