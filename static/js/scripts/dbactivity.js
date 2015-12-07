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
            tdurl: tdurl,
            murl: murl,
            mdurl: mdurl,
            cpage : 1
        },
    });
    setInterval(function() { 
        load_models(MAIN, 1, 6, function(data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
            }
            MAIN.set('models', data['models']);
            models = MAIN.get('models')
        });
     }, 2000);

    setInterval(function() { load_transactions(MAIN, MAIN.get('cpage'), 25, function(data) {
            MAIN.set('transactions', data['transactions']);
        });
	 }, 3000);

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

    MAIN.on("page_prev", function(e) {
        MAIN.set('cpage', MAIN.get('cpage')-1);
        load_transactions(MAIN, MAIN.get('cpage'), 25, function(data) {  
          MAIN.set('transactions', data['transactions']);
        });
    });
    MAIN.on("page_nxt", function(e) {
        MAIN.set('cpage', MAIN.get('cpage')+1);
          load_transactions(MAIN, MAIN.get('cpage'), 25, function(data) {  
            MAIN.set('transactions', data['transactions']);
          });
    });


  load_models(MAIN, 1, 6,  function (data) { 
        for(var i = 0; i < data['models'].length; i++) {
          data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
        }
        MAIN.set('models', data['models']);
        models = MAIN.get('models')
  });

  load_transactions(MAIN, MAIN.get('cpage'), 25, function(data) {  
    MAIN.set('transactions', data['transactions']);
  });


});
