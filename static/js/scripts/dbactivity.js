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
			mid: -1,
            cpage : 1
        },
    });


  var vars = getUrlVars();                                                                                                        

  if(vars && vars['mid']) {
	MAIN.set('mid', vars['mid']);
  }

    setInterval(function() { 
        load_models(MAIN, 1, 6, function(data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
            }
            MAIN.set('models', data['models']);
            models = MAIN.get('models')
        });
     }, 2000);

    setInterval(loadtrs(function(data) {}), 3000);

    function loadtrs(callback) {
        console.log("loadtrs" + MAIN.get('mid'));
        if(MAIN.get('mid') > 0) {
            load_transactions_id(MAIN, parseInt(MAIN.get('mid')), MAIN.get('cpage'), 25, function(data) {
                if(data['transactions'].length > 0) {
                    MAIN.set('transactions', data['transactions']);
                }
                else {
                    callback(data) // # on fail reset page value
                }
            });
        }
        else { 
            load_transactions(MAIN, MAIN.get('cpage'), 25, function(data) {
                if(data['transactions'].length > 0) {
                    MAIN.set('transactions', data['transactions']);
                }
                else {
                    callback(data) // # on fail reset page value
                }
            });
        }
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

    MAIN.on("page_prev", function(e) {
        if(MAIN.get('cpage') <= 1)
            return 
        MAIN.set('cpage', MAIN.get('cpage')-1);
        loadtrs(function() { MAIN.set('cpage', MAIN.get('cpage')+1); });
    });
    MAIN.on("page_nxt", function(e) {
        MAIN.set('cpage', MAIN.get('cpage')+1);
        loadtrs(function() { MAIN.set('cpage', MAIN.get('cpage')-1); });
    });


  load_models(MAIN, 1, 6,  function (data) { 
        for(var i = 0; i < data['models'].length; i++) {
          data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
        }
        MAIN.set('models', data['models']);
        models = MAIN.get('models')
  });


  loadtrs(function() {});


});
