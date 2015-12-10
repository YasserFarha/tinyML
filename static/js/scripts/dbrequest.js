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
            transaction: {},
            trans_id: trans_id,
            turl: turl,
            tdurl: tdurl,
            murl: murl,
            mdurl: mdurl,
            tnext: -1, tprev: -1,
            cpage : 1
        },
    });

    setInterval(function() { load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
            console.log(data);
            MAIN.set('transaction', data['transaction']);
            MAIN.set('tnext', data['tnext']);
            MAIN.set('tprev', data['tprev']);
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
        console.log("prev request : " + MAIN.get('tprev'));
        if(MAIN.get('tprev') < 0) {
            return;
        }
        MAIN.set('trans_id', MAIN.get('tprev'));
        load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
            console.log(data);
            MAIN.set('transaction', data['transaction']);
            MAIN.set('tnext', data['tnext']);
            MAIN.set('tprev', data['tprev']);
        });
    });
    MAIN.on("page_nxt", function(e) {
        console.log("prev request : " + MAIN.get('tnext'));
        if(MAIN.get('tnext') < 0) {
            return;
        }
        MAIN.set('trans_id', MAIN.get('tnext'));
        load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
            console.log(data);
            MAIN.set('transaction', data['transaction']);
            MAIN.set('tnext', data['tnext']);
            MAIN.set('tprev', data['tprev']);
        });
    });


    load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
        console.log(data);
        MAIN.set('transaction', data['transaction']);
        MAIN.set('tnext', data['tnext']);
        MAIN.set('tprev', data['tprev']);
    });


});
