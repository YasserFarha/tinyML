$(function() {
    var MAIN = new Ractive({
        el: '#target',
        template: '#template',
        delimiters: ['{%', '%}'],
        tripleDelimiters: ['{%%', '%%}'],
        data: {
            logged_in: logged_in,
            user_id: user_id,
			current_tab: "input",
            models : [],
            transaction: {},
			opage: 1, opsize: 25,
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
		 on_trs_load(data);
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

    if(MAIN.get('current_tab') === 'input') {
      $("#input-payload-panel").toggleClass("is-active");
      $("#input-payload-tab").toggleClass("is-active");
    }
    else if(MAIN.get('current_tab') === 'output') {
      $("#output-payload-panel").toggleClass("is-active");
      $("#output-payload-tab").toggleClass("is-active");
    }
    else {
      $("#logs-panel").toggleClass("is-active");
      $("#logs-tab").toggleClass("is-active");
    }
     
     MAIN.on("set_input_panel", function(e) { 
         MAIN.set('current_tab', "input");
     });
     MAIN.on("set_ouput_panel", function(e) { 
         MAIN.set('current_tab', "output");
     });
     MAIN.on("set_logs_panel", function(e) { 
         MAIN.set('current_tab', "output");
     });

    MAIN.on("trs_prev", function(e) {
        console.log("prev request : " + MAIN.get('tprev'));
        if(MAIN.get('tprev') < 0) {
            return;
        }
        MAIN.set('trans_id', MAIN.get('tprev'));
        load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
            console.log(data);
			changeUrlParam('tid', MAIN.get('trans_id'))
            MAIN.set('transaction', data['transaction']);
            MAIN.set('tnext', data['tnext']);
            MAIN.set('tprev', data['tprev']);
        });
    });
    MAIN.on("trs_nxt", function(e) {
        console.log("prev request : " + MAIN.get('tnext'));
        if(MAIN.get('tnext') < 0) {
            return;
        }
        MAIN.set('trans_id', MAIN.get('tnext'));
        load_transaction(MAIN, MAIN.get('trans_id'), function(data) {
            console.log(data);
			changeUrlParam('tid', MAIN.get('trans_id'))
            MAIN.set('transaction', data['transaction']);
            MAIN.set('tnext', data['tnext']);
            MAIN.set('tprev', data['tprev']);
        });
    });

	function on_trs_load(data) {
        console.log(data);
        MAIN.set('transaction', data['transaction']);
		var trs = MAIN.get('transaction');
		var opage = MAIN.get('opage');
		var opsize = MAIN.get('opsize');
		if(trs.tclass == "predict") {
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.predictions_short = trs.output_payload.predictions.slice(start, end)
			MAIN.set('transaction', trs);
		}
		if(trs.tclass == "train") {
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.epochs_short = trs.output_payload.epochs.slice(start, end)
			MAIN.set('transaction', trs);
		}
        MAIN.set('tnext', data['tnext']);
        MAIN.set('tprev', data['tprev']);
    };


    load_transaction(MAIN, MAIN.get('trans_id'), function(data) { on_trs_load(data); });

    MAIN.on("opage_nxt", function(e) {
		MAIN.set('opage', MAIN.get('opage')+1);
		var trs = MAIN.get('transaction');
		var opage = MAIN.get('opage');
		var opsize = MAIN.get('opsize');
		if(trs.tclass == "predict") {
			if(MAIN.get('opage')*MAIN.get('opsize') >= trs.output_payload.predictions.length)  {
				MAIN.set('opage', MAIN.get('opage')-1);
				return;
			}
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.predictions_short = trs.output_payload.predictions.slice(start, end)
			MAIN.set('transaction', trs);
		}
		if(trs.tclass == "train") {
			if((MAIN.get('opage')-1)*MAIN.get('opsize') >= trs.output_payload.epochs.length)  {
				MAIN.set('opage', MAIN.get('opage')-1);
				return;
			}
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.epochs_short = trs.output_payload.epochs.slice(start, end)
			MAIN.set('transaction', trs);
		}
	});
    MAIN.on("opage_prev", function(e) {
		if(MAIN.get('opage') <= 1) 
			return;
		MAIN.set('opage', MAIN.get('opage')-1);
		var trs = MAIN.get('transaction');
		var opage = MAIN.get('opage');
		var opsize = MAIN.get('opsize');
		if(trs.tclass == "predict") {
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.predictions_short = trs.output_payload.predictions.slice(start, end)
			MAIN.set('transaction', trs);
		}
		if(trs.tclass == "train") {
			start = (opage-1)*opsize;
			end = start+opsize;
			trs.output_payload.epochs_short = trs.output_payload.epochs.slice(start, end)
			MAIN.set('transaction', trs);
		}
	});


});
