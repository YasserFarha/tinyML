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
            murl: murl
        },
    });

  function load_models() {
      $.ajax(MAIN.get("murl"),
          { method: 'POST', data: {'page' : 1,
                                   'page_size' : 20},
          success: function (data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
              data['models'][i].arch = JSON.parse(data['models'][i]["arch"]);

            }
            MAIN.set('models', data['models']);
            models = MAIN.get('models')
         }
        }
      );
    }

    MAIN.on("clickrow", function(e) {
        id = $(e.node).data('href');
        window.document.location = id
    });

  load_models();

  setInterval(load_models, 2000);

});
