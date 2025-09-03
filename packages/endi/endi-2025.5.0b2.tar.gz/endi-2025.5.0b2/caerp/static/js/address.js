
var ALREADY_LOADED = new Object();
var address_handler = {
  already_loaded: new Object(),
  fetch_customer: function(customer_id) {
    var this_ = this;
    return $.ajax({
         type: 'GET',
         url:"/customers/" + customer_id,
         dataType: 'json',
         success: function(data) {
           this_.already_loaded[customer_id] = data;
         },
         async: false
    });
  },
  getEl: function() {
    return $("select[name=customer_id]");
  },
  get: function(customer_id) {
    if (! (customer_id in this.already_loaded)){
      this.fetch_customer(customer_id);
    }
    return this.already_loaded[customer_id];
  },
  selected: function() {
    var customer_id = this.getEl().children('option:selected').val();
    if (customer_id !== ''){
      return this.get(customer_id);
    }else{
      return null;
    }
  },
  address: function(customer) {
    return customer.full_address;
  },
  set: function(customer) {
    var address_obj = $('textarea[name=address]');
    address_obj.val(this.address(customer));
  },
  change: function(){
    var customer_obj = this.selected();
    if (customer_obj !== null){
      this.set(customer_obj);
    }
  }
};
$(function(){
  address_handler.getEl().change(
    function(){
      address_handler.change();
    }
  );
});
