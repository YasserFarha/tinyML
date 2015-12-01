$(function() {
    var MAIN = new Ractive({
        el: '#target',
        template: '#template',
        delimiters: ['{%', '%}'],
        tripleDelimiters: ['{%%', '%%}'],
        data: {
            logged_in: logged_in,
            user_id: user_id,
            my_models : [],
            current_edit : {}, // index of model being edited
            current_edit_name : "", // index of model being edited
            new_model : default_model(),
            current_tab : "new",
            max_nodes: 1000,
            murl: murl,
            selected : {}
        },
    });


  function load_models() {
      $.ajax(MAIN.get("murl"),
          { method: 'POST', data: {'page' : 1},
          success: function (data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8);
            }
            MAIN.set('my_models', data['models']);
            models = MAIN.get('my_models');
            for(var i = 0; i < models.length; i++) {
              models[i].arch = (JSON.parse(models[i].arch));
            }
            MAIN.set('my_models', models);
            console.log(MAIN.get('my_models'));
            if(data['models'].length > 0) {
                var ce = MAIN.get('my_models')[0];
                MAIN.set('current_edit', ce);
            }
         }
        }
      );
    }

    MAIN.on("addLayer", function(e) {
        var layers = {};
        if(MAIN.get("current_tab") === "new")
            layers = MAIN.get('new_model');
        else
            layers = MAIN.get('current_edit');
        layers = layers.arch.layer_dicts;
        layers.push({
                     "type" : "dense",
                     "nodes" : 4,
                     "uuid" : genuuid(),
                     "init" : "uniform",
                     "activation" : "relu"});
        MAIN.set("layer_dicts", layers);
        setInterval(function() {
            componentHandler.upgradeDom();
            mdlUpgradeDom = false;
        }, 200);
                     
    });


    MAIN.on("removeLayer", function(e) {
        var layers = {};
        if(MAIN.get("current_tab") === "new")
            layers = MAIN.get('new_model');
        else
            layers = MAIN.get('current_edit');
        layers = layers.arch.layer_dicts;
        sel = MAIN.get('selected');
        for(s in sel) {
            var index = -1;
            for(var i = 0; i<layers.length; i++) {
                if(layers[i]["uuid"] === s) {
                    index = i;
                }
            }
            if(index > -1) {
                layers.splice(index, 1); 
            }
        }
        MAIN.set('selected', {});
        MAIN.set("layer_dicts", layers);
    });

    MAIN.on("selectLayer", function(e) {
        lay_num = $(e.node).data('layer-id');
        cb = $("#layer_check_"+lay_num)
        cb.toggleClass("fa-check-square");
        cb.toggleClass("fa-square-o");
        sel = MAIN.get('selected');
        if(sel[lay_num] == undefined)
            sel[lay_num] = lay_num;
        else
            delete sel[lay_num];

        console.log(sel);
                     
    });

    MAIN.on("clearAll", function(e) {
        MAIN.set('new_model', default_model());
    });

    MAIN.on("editselect", function(e) {
        uuid = $(e.node).data('model-id');
        models = MAIN.get('my_models');
        for(var i = 0; i < models.length; i++) {
            if(uuid === models[i].uuid) {
                MAIN.set("current_edit", models[i]);
            }
        }
        console.log(models);
    });

  load_models();
  $("#new-model-panel").toggleClass("is-active");
  $("#new-model-tab").toggleClass("is-active");
 
 MAIN.on("set_new_panel", function(e) { 
     MAIN.set('current_tab', 'new');
     $("#new-model-panel").addClass("active");
     $("#edit-model-panel").removeClass("active");
 });
 MAIN.on("set_edit_panel", function(e) { 
     MAIN.set('current_tab', 'edit');
     $("#edit-model-panel").addClass("active");
     $("#new-model-panel").removeClass("active");
 });


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

  function default_model() {
    return  {
        uuid : genuuid(),
        name: "my_new_model",
        arch : {
            layer_dicts: [{"uuid" : genuuid(), 
                           "type" : "dense",
                           "nodes" : 4,
                           "init" : "uniform",
                           "activation" : "relu"}],
            num_inp : 3,
            num_out: 1,
        }
    }
  }

MAIN.observe( 'current_edit_name', function () {
    models = MAIN.get('my_models');
    ce = MAIN.get('current_edit_name');
    for(var i =0; i < models.length; i++) {
        if(models[i].name === ce) {
            MAIN.set('current_edit',models[i]);
            console.log(models[i]);
        }
    }
});


});
