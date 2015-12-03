$(function() {
    var MAIN = new Ractive({
        el: '#target',
        template: '#template',
        delimiters: ['{%', '%}'],
        tripleDelimiters: ['{%%', '%%}'],
        data: {
            logged_in: logged_in,
            user_id: user_id,
            models : [],
            transactions: [],
            turl: turl,
            murl: murl
        },
    });

  function load_models() {
      $.ajax(MAIN.get("murl"),
          { method: 'POST', data: {'page' : 1},
          success: function (data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
            }
            MAIN.set('models', data['models']);
            models = MAIN.get('models')
         }
        }
      );
    }

  function load_transactions() {
      $.ajax(MAIN.get("turl"),
          { method: 'POST', data: {'page' : 1},
          success: function (data) { 
            for(var i = 0; i < data['transactions'].length; i++) {
              data['transactions'][i]['uuid_short'] = data['transactions'][i]['uuid'].substring(0, 8)
            }
            MAIN.set('transactions', data['transactions']);
            console.log(data);
          }
        }
      );
    }


    MAIN.on("clickrow", function(e) {
        id = $(e.node).data('href');
        window.document.location = id
    });

    MAIN.on("go_create", function(e) {
        window.document.location = create_url;
    });

    MAIN.on("go_models", function(e) {
        window.document.location = models_url;
    });

  load_models();
  load_transactions();

});
