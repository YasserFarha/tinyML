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
            transaction: [],
            trans_id: trans_id,
            turl: turl,
            tdurl: tdurl,
            murl: murl,
            mdurl: mdurl,
            cpage : 1
        },
    });

    setInterval(function() { load_transaction(MAIN, trans_id, function(data) {
            MAIN.set('transaction', data['transaction']);
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
        load_transaction(MAIN, trans_id, function(data) {
            MAIN.set('transaction', data['transaction']);
        });
    });
    MAIN.on("page_nxt", function(e) {
        MAIN.set('cpage', MAIN.get('cpage')+1);
        load_transaction(MAIN, trans_id, function(data) {
            MAIN.set('transaction', data['transaction']);
        });
    });


    load_transaction(MAIN, trans_id, function(data) {
        MAIN.set('transaction', data['transaction']);
    });


});
