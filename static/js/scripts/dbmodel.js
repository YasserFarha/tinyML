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
            murl: murl,
            turl: turl
        },
    });

  function load_model(id) {
      $.ajax(MAIN.get("murl"),
          { method: 'GET', data : {"id" : MAIN.get('model_id')},
          success: function (data) { 
              var model = data['model'];
              var arch = data['model']['arch'];
              model.arch = arch;
              MAIN.set('model', model);
         }
        }
      );
    }

  function load_transactions(id) {
      console.log("loading trs");
      $.ajax(MAIN.get("turl"),
          { method: 'POST', data : {"mid" : id, page : 1, page_size : 10},
          success: function (data) { 
              console.log(data);
              MAIN.set('transactions', data['transactions']);
         }
        }
      );
    }

  function load_transactions(id, page, page_size, callback) {                                                                         
      $.ajax(MAIN.get("turl"),
          { method: 'POST', data: {'mid' : id, 'page' : page, 'page_size' : page_size},
          success: function (data) { 
            for(var i = 0; i < data['transactions'].length; i++) {
              data['transactions'][i]['uuid_short'] = data['transactions'][i]['uuid'].substring(0, 8)
            }   
            callback(data);
            console.log(data);
          }   
        }   
      );  
    }   



  load_model(model_id);
  load_transactions(model_id, 1, 15,  function (data) { 
		  console.log(data);
		  MAIN.set('transactions', data['transactions']);
   });
    setInterval(function() { load_model(model_id); }, 2000);
    setInterval(function() { load_transactions(model_id, 1, 15, function(data) {
            MAIN.set('transactions', data['transactions']);
        }); 
     }, 3000);





  jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
      window.document.location = $(this).data("href");
    });
  });

});
