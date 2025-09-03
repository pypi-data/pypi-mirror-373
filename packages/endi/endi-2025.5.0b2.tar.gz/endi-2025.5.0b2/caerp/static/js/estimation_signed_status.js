
var EstimationSignedStatus = {
    ui: {
        buttons: '.btn',
    },
    el: "div.signed_status_group",
    onClick: function(event){
        var value = $(event.currentTarget).find('input').val();
        ajax_request(this.url, {'submit': value}, 'POST', {success: this.refresh, error: this.refresh});
    },
    refresh: function(){
        window.location.reload();
    },
    setup: function(){
        var this_ = this;
        this.$el = $(this.el);
        this.url = this.$el.attr('data-url');
        _.each(this.ui, function(value, key){
            this_.ui[key] = this_.$el.find(value);
        });
        this.ui.buttons.on('click', _.bind(this.onClick, this));
    }
};

$(function(){
    EstimationSignedStatus.setup();
});
