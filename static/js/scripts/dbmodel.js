$(function() {

    var MAIN = new Ractive({
        el: '#target',
        template: '#template',
        delimiters: ['{%', '%}'],
        tripleDelimiters: ['{%%', '%%}'],
        data: {
            logged_in: logged_in,
            user_id: user_id,
            model : [],
			model_id : model_id,
            transactions: [],
            mdurl: mdurl,
            turl: turl
        },
    });

      function on_model_load(data) { 
          var model = data['model'];
          var arch = data['model']['arch'];
          model.arch = arch;
          MAIN.set('model', model);
     }


  load_model(MAIN, model_id, on_model_load);
  load_transactions_id(MAIN, model_id, 1, 15,  function (data) { 
		  console.log(data);
		  MAIN.set('transactions', data['transactions']);
   });
    setInterval(function() { load_model(MAIN, model_id, on_model_load); }, 2000);
    setInterval(function() { load_transactions_id(MAIN, model_id, 1, 15, function(data) {
            MAIN.set('transactions', data['transactions']);
        }); 
     }, 3000);


  MAIN.on("edit_model", function(e) {                                                                                            
     window.document.location = create_url;
  });


  jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
      window.document.location = $(this).data("href");
    });
  });

});
