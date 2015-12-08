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
            current_tab: "train",
            train_payload: default_tpayload(),
            predict_payload: default_ppayload(),
            eval_payload: default_epayload(),
            mdurl: mdurl,
            saved_labels: [],
            saved_input: [],
            turl: turl
        },
    });

      function on_model_load(data) { 
          var model = data['model'];
          var arch = JSON.parse(data['model']['arch']);
          model.arch = arch;
          MAIN.set('model', model);
     }


  function default_tpayload() {
    return {
        "max_epochs": 256,
        "max_batch_size": 1000,
        "input" : {
            "upload" : true,
            "name" : "",
            "save" : false,
            "data" : {}
        },
        "labels" : {
            "upload" : true,
            "name" : "",
            "save" : false,
            "data" : {}
        },
        "batch_size": 128,
        "nb_epoch": 100,
        "valid_split" : 15,
        "shuffle" : "batch"
    }
  }

  function default_epayload() {
    return {
        "input" : {
            "upload" : true,
            "name" : "",
            "save" : false,
            "data" : {}
        },
        "labels" : {
            "upload" : true,
            "name" : "",
            "save" : false,
            "data" : {}
        },
        "max_batch_size": 1000,
        "labels" : {},
        "batch_size": 128
    }
  }

  function default_ppayload() {
    return {
        "input" : {
            "upload" : true,
            "name" : "",
            "save" : false,
            "data" : {}
        },
        "max_batch_size": 1000,
        "batch_size": 128
    }
  }


  load_model(MAIN, model_id, on_model_load);
  load_transactions_id(MAIN, model_id, 1, 15,  function (data) { 
		  MAIN.set('transactions', data['transactions']);
   });
  setInterval(function() { load_model(MAIN, model_id, on_model_load); }, 2000);
  setInterval(function() { load_transactions_id(MAIN, model_id, 1, 15, function(data) {
        MAIN.set('transactions', data['transactions']);
    }); 
  }, 3000);


  MAIN.on("train_model", function(e) {
    var tp = MAIN.get('train_payload');
    var tfiles = $("#train-input-file").prop('files');
    var lfiles = $("#train-label-file").prop('files');
    console.log(tfiles);
    console.log(lfiles);

  });

  MAIN.on("edit_model", function(e) {                                                                                            
     window.document.location = create_url;
  });


    MAIN.on("clickrow", function(e) {
        id = $(e.node).data('href');
        window.document.location = id
    });

    MAIN.on("clearAll", function(e) {
        id = $(e.node).data('clear-id');
        if(id === "train") {
            tp = MAIN.get('train_payload');
            tpn = default_tpayload();
            tp.input = tpn.input;
            tp.labels = tpn.labels;
            tp = tpn;
            MAIN.set('train_payload', tp);
        }
        console.log(componentHandler.upgradeDom());
    });


    MAIN.on("go_activity", function(e) {
        window.document.location = "/tinyML/dashboard/activity?mid="+MAIN.get('model_id')
    });

  var vars = getUrlVars();                                                                                                        
  if(vars['tab'] && vars['tab'] === 'train' || vars['tab'] === 'predict') {
    MAIN.set('current_tab', vars['tab']);
  }

    if(MAIN.get('current_tab') === 'train') {
      $("#train-panel").toggleClass("is-active");
      $("#train-tab").toggleClass("is-active");
    }   
    else if(MAIN.get('current_tab') == 'eval'){
      $("#eval-panel").toggleClass("is-active");
      $("#eval-tab").toggleClass("is-active");
    }   
    else {
      $("#predict-panel").toggleClass("is-active");
      $("#predict-tab").toggleClass("is-active");
    }   
         
     MAIN.on("set_train_panel", function(e) { 
         MAIN.set('current_tab', "train");
     }); 
     MAIN.on("set_eval_panel", function(e) { 
         MAIN.set('current_tab', "eval");
     }); 
     MAIN.on("set_predict_panel", function(e) { 
         MAIN.set('current_tab', "predict");
     }); 

    MAIN.on("checkBox", function(e) {
        var mdl = {};
        type = $(e.node).data('box-name');
        if(type === "train-input-box") {
            MAIN.set('train_payload.input.save', !MAIN.get('train_payload.input.save')); 
        }
        if(type === "train-labels-box") {
            MAIN.set('train_payload.labels.save', !MAIN.get('train_payload.labels.save')); 
        }
    });


});
