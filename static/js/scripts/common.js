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
