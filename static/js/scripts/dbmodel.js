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
            turl: turl,
            train_url:train_url,
            eval_url:eval_url,
            predict_url:predict_url,
            user_data_url:user_data_url
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
            "size_KB": 0,
            "upload_name" : "",
            "select_ind" : 0,
            "select_id" : 0,
            "save" : false,
            "data" : {}
        },
        "labels" : {
            "upload" : true,
            "size_KB": 0,
            "upload_name" : "",
            "select_ind" : 0,
            "select_id" : 0,
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
            "size_KB": 0,
            "upload_name" : "",
            "select_ind" : 0,
            "select_id" : 0,
            "save" : false,
            "data" : {}
        },
        "labels" : {
            "upload" : true,
            "size_KB": 0,
            "upload_name" : "",
            "select_ind" : 0,
            "select_id" : 0,
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
            "size_KB": 0,
            "upload_name" : "",
            "select_ind" : 0,
            "select_id" : 0,
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


  get_all_user_data(MAIN, function(data) {
    console.log(data);
    MAIN.set('saved_input', data['inputs']);
    MAIN.set('saved_labels', data['labels']);
  });

  MAIN.on("train_model", function(e) {
    var tp = MAIN.get('train_payload');
    console.log(tp);
    if(tp.input.upload) {
        var tfiles = $("#train-input-file").prop('files');
        console.log(tfiles);
        console.log(lfiles);
        var tfile = tfiles[0];
        if(!tfile) {
            alert("no input file selected");
            return;
        }
        tp.input.size_KB = tfile.size/1000.0,
        tp.input.upload_name=tfile.name,
        tp.input.data = tfile
    }
    else {
        var sind  = tp.input.select_ind;
        var inputs = MAIN.get('saved_input');
        var selinp = inputs[sind];
        if(!selinp) {
            alert("Must select a valid input file name");
            return;
        }
        tp.input.select_id = selinp.id;
        tp.input.select_name = selinp.name;
        tp.input.data = {};
        tp.input.upload_name = "";
    }

    if(tp.labels.upload) {
        var lfiles = $("#train-label-file").prop('files');
        var lfile = lfiles[0];
        if(!lfile) {
            alert("no labels file selected");
            return;
        }
        tp.labels.size_KB = lfile.size/1000.0,
        tp.labels.upload_name=lfile.name,
        tp.labels.data = lfile
    }
    else {
        var sind = tp.labels.select_ind;
        var labels = MAIN.get('saved_labels');
        var selinp = labels[sind];
        if(!selinp) {
            alert("Must select a valid input file name");
            return;
        }
        tp.labels.select_id = selinp.id;
        tp.labels.select_name = selinp.name;
        tp.labels.data = {};
        tp.labels.upload_name = "";
    }

    console.log(tp);
    request_train(MAIN, MAIN.get('model_id'), tp, function(data) {
        console.log(data);
    });

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
        if(type === "eval-input-box") {
            MAIN.set('eval_payload.input.save', !MAIN.get('eval_payload.input.save')); 
        }
        if(type === "eval-labels-box") {
            MAIN.set('eval_payload.labels.save', !MAIN.get('eval_payload.labels.save')); 
        }
    });

     $("#train-input-file").change(function (){
       var fileName = $(this).val();
       var file = $(this).prop('files')[0];
       var fname = file.name;
       if(fname.slice((fname.lastIndexOf(".") - 1 >>> 0) + 2) !== "csv") {
            alert("Not a CSV File");
            $(this).val(null);
        }
     });

    MAIN.observe('train_payload', function() {
            console.log(MAIN.get('train_payload'));
    });


});
