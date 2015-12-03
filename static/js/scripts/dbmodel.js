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
            transactions: [],
            murl: murl
        },
    });

  function load_model(id) {
      $.ajax(MAIN.get("murl"),
          { method: 'GET',
          success: function (data) { 
              var model = data['model'];
              var arch = data['model']['arch'];
              model.arch = arch;
              MAIN.set('model', model);
         }
        }
      );
    }


  load_model();


  jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
      window.document.location = $(this).data("href");
    });
  });

});
