
var Popup = Backbone.Marionette.Region.extend({
  /*
   *  Popup object as a marionette region
   *
   *  Avoids problems with zombie views
   */
  el: "#popup",
  constructor: function () {
    _.bindAll(this, "closeModal", "reset", "onShow", "getEl", 'onEmpty');
    Backbone.Marionette.Region.prototype.constructor.apply(this, arguments);
  },
  closefunc: function () {
    // By default, we redirect to the index
    CaerpApp.router.navigate("index", { trigger: true });
  },
  getEl: function (selector) {
    var $el = $(selector);
    return $el;
  },
  onShow: function (view) {
    /*
     * Popup the element with a custom close function
     */
    var window_height = $(window).height();
    var window_width = $(window).width();
    var this_ = this;
    this.$el.dialog({
      //autoOpen: true,
      //height:"auto",
      //width: "auto",
      resizable: false,
      modal: true,
      fluid: true,
      position: ['center', 'middle'],
      maxHeight: window_height * 0.9,
      maxWidth: window_width * 0.9,
      title: this_.title,
      hide: "fadeOut",
      open: function (event, ui) {
        /*
        //$(this).css('height','auto');
        // Get the content width
        var content_width = $(this).children().first().width();
        var window_ratio = window_width * 0.8;

        // Get the best width to use between window's or content's
        var dialog_width = Math.min(content_width + 50, window_ratio);
        var dialog = $(this).parent();
        dialog.width(dialog_width);

        // We need to set the left attr
        var padding = (window_width - dialog_width) / 2.0;
        dialog.css('left', padding + 'px');

        // Fix dialog height if content is too big for the current window
        if (dialog.height() > $(window).height()) {
            dialog.height($(window).height()*0.9);
        }
        // Show close button (jquery + bootstrap problem)
        var closeBtn = $('.ui-dialog-titlebar-close');
        closeBtn.addClass("ui-button ui-widget ui-state-default " +
          "ui-corner-all ui-button-icon-only");
        closeBtn.html('<span class="ui-button-icon-primary ui-icon ' +
        'ui-icon-closethick"></span><span class="ui-button-text">Close</span>');
        closeBtn.on("click.redirect", this_.closefunc);
        */
      }
    });
    this.$el.dialog('open');
  },
  onEmpty: function () {
    this.closeModal();
  },
  closeModal: function () {
    if (this.$el.dialog("isOpen")) {
      this.$el.dialog("close");
    }
  }
});
