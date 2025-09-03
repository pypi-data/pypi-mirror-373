
var ActivityModule = CaerpApp.module('ActivityModule',
  function (ActivityModule, CaerpApp, Backbone, Marionette, $, _) {
    ActivityModule.Router = Marionette.AppRouter.extend({
      appRoutes: {
        "events/:id": "get_events"
      }
    });
    ActivityModule.Controller = {
      initialized: false,
      element: '#event_container',

      initialize: function () {
        if (!this.initialized) {
          this.$element = $(this.element);
          this.initialized = true;
          _.bindAll(this, 'displayList');
        }
      },
      setNbItemsSelectBehaviour: function () {
        $('#number_of_events').unbind('change.events');
        _.bindAll(this, 'get_events');
        var this_ = this;
        $('#number_of_events').bind("change.events",
          function () {
            this_.get_events(1);
          }
        );
      },
      index: function () {
        this.initialize();
        this.setNbItemsSelectBehaviour();
      },
      get_events: function (id) {
        this.initialize();
        this.refresh_list(id);
      },
      refresh_list: function (page_num) {
        url = '?action=events_html';
        var items_per_page = $('#number_of_events').val();
        postdata = {
          'events_page_nb': page_num,
          'events_per_page': items_per_page
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
    ActivityModule.on('start', function () {
      ActivityModule.router = new ActivityModule.Router({
        controller: ActivityModule.Controller
      });
      ActivityModule.Controller.index();
    });
  });

$(function () {
  CaerpApp.start();
});
