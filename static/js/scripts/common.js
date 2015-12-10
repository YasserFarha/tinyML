// John Allard
// @liscence MIT
// December 2015

// This file contains functions that are common to all dashboard routes, like model querying,
// transaction querying, etc. The primary purpose of this file it to reduce code-duplication

function load_models(MAIN, page, page_size, callback) {
  $.ajax(MAIN.get("murl"),
      { 
        method: 'POST', 
        data: {'page' : page, 'page_size' : page_size},
        success: function (data) { 
            callback(data);
        },
         error: function(xhr, textStatus, errorThrown){
            console.error("load models request errored");
            console.log(xhr);
            console.log(textStatus);
            console.log(errorThrown);
        }
    }
  );
}

function load_model(MAIN, id, callback) {                                                                                                       
  $.ajax(MAIN.get("mdurl"),
      { method: 'GET', data : {"id" : id},
      success: function (data) { 
          callback(data);
     }
    }
  );
}


function load_transactions(MAIN, page, page_size, callback) {
  $.ajax(MAIN.get("turl"),
      { method: 'POST', data: {'page' : page, 'page_size' : page_size},
      success: function (data) { 
        for(var i = 0; i < data['transactions'].length; i++) {
          data['transactions'][i]['uuid_short'] = data['transactions'][i]['uuid'].substring(0, 8);
          data['transactions'][i]['output_payload'] = JSON.parse(data['transactions'][i]['output_payload']);
          data['transactions'][i]['input_payload'] = JSON.parse(data['transactions'][i]['input_payload']);
        }
        callback(data);
      }
    }
  );
}

function load_transaction(MAIN, tid, callback) {
  $.ajax(MAIN.get("tdurl"),
      { method: 'POST', data: {'tid' : tid},
      success: function (data) { 
        if(data['transaction']) {
          data['transaction']['uuid_short'] = data['transaction']['uuid'].substring(0, 8)
          data['transaction']['output_payload'] = JSON.parse(data['transaction']['output_payload'])
          data['transaction']['input_payload'] = JSON.parse(data['transaction']['input_payload'])
        }
        callback(data);
      }
    }
  );
}

function load_transactions_id(MAIN, id,  page, page_size, callback) {
  $.ajax(MAIN.get("turl"),
      { method: 'POST', data: {'page' : page, 'page_size' : page_size, 'mid' : id},
      success: function (data) { 
        for(var i = 0; i < data['transactions'].length; i++) {
          data['transactions'][i]['uuid_short'] = data['transactions'][i]['uuid'].substring(0, 8)
          data['transactions'][i]['output_payload'] = JSON.parse(data['transactions'][i]['output_payload']);
          data['transactions'][i]['input_payload'] = JSON.parse(data['transactions'][i]['input_payload']);
        }
        callback(data);
      }
    }
  );
}

function get_all_user_data(MAIN, callback) {
  $.ajax(MAIN.get("user_data_url"),
      { method: 'POST', data: {},
      success: function (data) { 
        new_data = {};
        new_data['inputs'] = [];
        new_data['labels'] = [];
        for(var i = 0; i < data['user_data'].length; i++) {
            if(data['user_data'][i].dclass === "inputs") {
                new_data['inputs'].push(data['user_data'][i]);
            }
            else {
                new_data['labels'].push(data['user_data'][i]);
            }
        }
        callback(new_data);
      }
    }
  );
}

function request_train(MAIN, model_id, td, callback) {
  var train_data = new FormData();
  train_data.append("batch_size", td.batch_size);
  train_data.append("nb_epoch", td.nb_epoch);
  train_data.append("valid_split", td.valid_split);
  train_data.append("input", JSON.stringify(td.input));
  train_data.append("input_fh", td.input.data);
  train_data.append("labels", JSON.stringify(td.labels));
  train_data.append("labels_fh", td.labels.data);
  train_data.append("model_id", model_id);
  console.log(train_data);
  var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function (){
        if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
        } 
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback("");
        } else {
        }
    };
  xhr.open("POST", MAIN.get("train_url"), true);
  xhr.send(train_data);
}


function request_eval(MAIN, model_id, td, callback) {
  var eval_data = new FormData();
  eval_data.append("batch_size", td.batch_size);
  eval_data.append("input", JSON.stringify(td.input));
  eval_data.append("input_fh", td.input.data);
  eval_data.append("labels", JSON.stringify(td.labels));
  eval_data.append("labels_fh", td.labels.data);
  eval_data.append("model_id", model_id);
  console.log(eval_data);
  var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function (){
        if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
        } 
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback("");
        } else {
        }
    };
  xhr.open("POST", MAIN.get("eval_url"), true);
  xhr.send(eval_data);
}

function request_predict(MAIN, model_id, td, callback) {
  var predict_data = new FormData();
  predict_data.append("batch_size", td.batch_size);
  predict_data.append("input", JSON.stringify(td.input));
  predict_data.append("input_fh", td.input.data);
  predict_data.append("model_id", model_id);
  console.log(predict_data);
  var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function (){
        if(xhr.readyState==4 && xhr.status==200){
            callback(xhr.responseText);
        } 
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback("");
        } else {
        }
    };
  xhr.open("POST", MAIN.get("predict_url"), true);
  xhr.send(predict_data);
}

function isEmpty(object) { for(var i in object) { return false; } return true; } 

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,    
    function(m,key,value) {
      vars[key] = value;
    });
    return vars;
  }


  function genuuid(){
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now();; //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
  }

  function get_date(d) {
    var date1 = new Date(d.substr(0, 4), d.substr(5, 2) - 1, d.substr(8, 2), d.substr(11, 2), d.substr(14, 2), d.substr(17, 2));
    return date1;
   }
