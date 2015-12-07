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
            ce : 0, // index of model being edited
            current_edit_name : "", // index of model being edited
            new_model : default_model(),
            added_models : [],
            added_transactions : [],
            current_tab : "new",
            max_nodes: 1000,
            murl: murl, mdurl: mdurl, tdurl: tdurl,
            new_url: new_url,
            edit_url: edit_url,
            selected : {}
        },
    });

	// defines what to do when load_models() function finishes
	function on_model_load(data) { 
		for(var i = 0; i < data['models'].length; i++) {
		  data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8);
		  data['models'][i]['updated'] = false;
		}
		MAIN.set('my_models', data['models']);
		models = MAIN.get('my_models');
		for(i = 0; i < models.length; i++) {
		  models[i].arch = JSON.parse(models[i]["arch"]);
		}
		MAIN.set('my_models', models);
		if(data['models'].length > 0) {
			var ce = MAIN.get('my_models')[0];
			ce.updated = false;
			MAIN.set('ce', 0);
			// MAIN.set('current_edit.updated', false);
		}
	 }


    MAIN.on("create_new", function(e) {
        model = MAIN.get('new_model');
        mdls = MAIN.get('my_models');
        if(model.name === "") {
            alert("Model must be named.");
            return false;
        }

        for(var i = 0; i < mdls.length; i++) {
            if(mdls[i].name === model.name) {
                alert("You already have a model with this name, try another one.");
                return false;
            }
        }
        if(model.arch.layer_dicts.length <= 0) {
            alert("not enough layers!");
        }
        $.ajax(MAIN.get("new_url"),
          { 
              method: 'POST', data: {
                "name" : model.name,
                "mclass" : "deep-nnet",
                "uuid" : model.uuid,
                "arch" : JSON.stringify(model.arch)
              },
                success: function (data) { 
                    var models = mdls; //MAIN.get('my_models');
                    var new_model = data['model'];
                    var new_trans = data['transaction'];
                    new_model.arch = JSON.parse(new_model.arch);
                    md = [new_model];
                    for(var i = 0; i < models.length; i++) {
                      md.unshift(models[i]);
                    }
                    models = md;
                    var added = MAIN.get('added_models');
                    added_trs = MAIN.get('added_transactions');
                    added.push(new_model);
                    added_trs.push(new_trans);
                    MAIN.set('added_models', added);
                    MAIN.set('added_transactions', added_trs);
                    MAIN.set('my_models', models);
                    clear_all();
            },
             error: function(xhr, textStatus, errorThrown){
                alert("A model with that name exists already, try another one.");
            }
           }
        );
    });

    MAIN.on("update_model", function(e) {
        model = get_current_edit();
        if(model.arch.layer_dicts.length <= 0) {
            alert("not enough layers!");
        }
        $.ajax(MAIN.get("edit_url"),
          { 
              method: 'POST', data: {
                "name" : model.name,
                "mclass" : "deep-nnet",
                "uuid" : model.uuid,
                "arch" : JSON.stringify(model.arch)
              },
                success: function (data) { 
                var models = MAIN.get('my_models');
                var ce = MAIN.get('ce');
                models[ce] = data['model'];
                models[ce].arch = JSON.parse(data['model'].arch);
                MAIN.set('my_models', models);
                added = MAIN.get('added_models');
                added.push(models[ce]);
                MAIN.set('added_models', added);
				new_trans = data['transaction'];
				added_trs = MAIN.get('added_transactions');
				added_trs.push(new_trans);
				MAIN.set('added_transactions', added_trs);
            }
           }
        );
    });

    MAIN.on("addLayer", function(e) {
        var layers = {};
        var model = {};
        if(MAIN.get("current_tab") === "new")
            model = MAIN.get('new_model');
        else
            model = get_current_edit();
		model.updated = true;
        model.arch.layer_dicts.push({
                     "type" : "dense",
                     "nodes" : 4,
                     "uuid" : genuuid(),
                     "init" : "uniform",
                     "activation" : "relu"});
        if(MAIN.get("current_tab") === "new") {
            MAIN.set("new_model", model);
        }
        else {
            set_current_edit(model);
        }

        MAIN.updateModel();
                     
    });


    MAIN.on("removeLayer", function(e) {
        var layers = {};
        sel = MAIN.get('selected');
        if(isEmpty(sel)) {
          return false;
        }
        if(MAIN.get("current_tab") === "new")
            model = MAIN.get('new_model');
        else
            model = get_current_edit(); //MAIN.get('current_edit');
		model.updated = true;
        layers = model.arch.layer_dicts;
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
        MAIN.set('selected', sel );
        if(MAIN.get("current_tab") === "new")
            MAIN.set("new_model.arch.layer_dicts", layers);
        else
            // MAIN.set("current_edit.arch.layer_dicts", layers);
            set_current_edit(model);
    });

    MAIN.on("selectLayer", function(e) {
        var mdl = {};
        lay_num = $(e.node).data('layer-id');
        cb = $("#layer_check_"+lay_num)
        sel = MAIN.get('selected');
        if(!sel[lay_num] ) {
            sel[lay_num] = true;
        }
        else {
            delete sel[lay_num];
        }
        MAIN.set('selected', sel);
                     
    });


	function clear_all(e) {
       MAIN.set('new_model', default_model());
       MAIN.set('new_model.arch.layer_dicts', default_model().arch.layer_dicts);
    };

    MAIN.on("clearAll", function(e) { clear_all(); });

    MAIN.on("resetModel", function(e) {
        mdl = get_current_edit(); 
        load_model(MAIN, mdl.id, function(data) {
            md = data['model'];
            md.arch = JSON.parse(md.arch);
            md.updated = true;
            md.arch.layer_dicts = md.arch.layer_dicts;
            set_current_edit(md);
            MAIN.set('my_models['+MAIN.get('ce')+']', md);
            MAIN.set('my_models['+MAIN.get('ce')+'].arch.layer_dicts', md.arch.layer_dicts);
        });
    
    });

    MAIN.on("editselect", function(e) {
        uuid = $(e.node).data('model-id');
        models = MAIN.get('my_models');
        for(var i = 0; i < models.length; i++) {
            if(uuid === models[i].uuid) {
                // MAIN.set("current_edit", models[i]);
                set_current_edit(models[i]);
            }
        }
    });

  var vars = getUrlVars();
  if(vars['tab'] && vars['tab'] === 'new' || vars['tab'] === 'edit') {
	MAIN.set('current_tab', vars['tab']);
  }

    if(MAIN.get('current_tab') === 'new') {
      $("#new-model-panel").toggleClass("is-active");
      $("#new-model-tab").toggleClass("is-active");
    }
    else {
      $("#edit-model-panel").toggleClass("is-active");
      $("#edit-model-tab").toggleClass("is-active");
    }
     
     MAIN.on("set_new_panel", function(e) { 
         MAIN.set('current_tab', "new");
     });
     MAIN.on("set_edit_panel", function(e) { 
         MAIN.set('current_tab', "edit");
     });


  function default_model() {
    return  {
        uuid : genuuid(),
        name: "",
        name_short: "",
		updated: false,
        compiled: false,
        trained: false,
        mclass: "deep-nnet",
        arch_json: "",
        arch : {
            layer_dicts: [{"uuid" : genuuid(), 
                           "type" : "dense",
                           "nodes" : 4,
                           "init" : "uniform",
                           "activation" : "relu"}],
            num_inp : 3,
            num_out: 1,
            optimizer : "sgd",
            lossfn : "mse"
        }
    }
  }

  function push_update(data) {
    mdls = MAIN.get('my_models');
    active = MAIN.get('added_models');
    for(var i = 0; i < mdls.length; i++) {
      if(mdls[i].uuid === data['uuid']) {
         mdls[i] = data;
         mdls[i].arch = data['arch'];
         MAIN.set('current_edit_name', MAIN.get('current_edit_name'));
      }
        for(var j = 0; j < active.length; j++) {
          var cur = active[j];
          if(mdls[i].uuid === cur.uuid) {
              active[j] = mdls[i];
          }
        }
    }
    MAIN.set('my_models', mdls);
    MAIN.set('added_models', active);
  }


  function watch_added() {
    /*added = MAIN.get('added_models')
    for(var i = 0; i < added.length; i++) {
        if(added[i].status === "compiling") {
            var k = i;
            load_model(MAIN, added[k].id, function(data) {
                dl = data['model'];
                added[k] = dl;
                added[k].arch = JSON.parse(dl.arch); 
                push_update(added[k]);
            });
        }
    }
    MAIN.set('added_models', added);
    */

    added_trs = MAIN.get('added_transactions')
    for(var j = 0; j < added_trs.length; j++) {
        // if(added_trs[j].status === "active") {
            load_transaction(MAIN, added_trs[j].id, function(data) {
                added_trs = MAIN.get('added_transactions')
                tr = data['transaction'];
                for(var i = 0; i < added_trs.length; i++) {
                    if(added_trs[i].uuid === tr.uuid) {
                        added_trs[i] = tr;
                        break;
                    }
                }
                load_model(MAIN, tr.model, function(data) { 
                    data = data['model'];
                    data.arch = JSON.parse(data.arch);
                    mdls = MAIN.get('my_models');
                    active = MAIN.get('added_models');
                    for(var i = 0; i < mdls.length; i++) {
                      if(mdls[i].uuid === data['uuid']) {
                         mdls[i].status = data['status'];
                         // mdls[i].arch = data['arch'];
                         MAIN.set('current_edit_name', MAIN.get('current_edit_name'));
                      }
                        for(var j = 0; j < active.length; j++) {
                          var cur = active[j];
                          if(mdls[i].uuid === cur.uuid) {
                              active[j] = mdls[i];
                          }
                        }
                    }
                    MAIN.set('my_models', mdls);
                    MAIN.set('added_models', active);
                });
            });
            MAIN.set('added_transactions', added_trs);
      // }
    }
  }

    setInterval(watch_added, 2000);

    function get_current_edit() {
        models = MAIN.get('my_models');
        return models[MAIN.get('ce')];
    }

    function set_current_edit(data) {
        models = MAIN.get('my_models');
        models[MAIN.get('ce')] = data;
        models[MAIN.get('ce')].arch = data.arch;
    }

	MAIN.observe( 'current_edit_name', function () {
		models = MAIN.get('my_models');
        // MAIN.set('selected', {});
		ce = MAIN.get('current_edit_name');
        if(MAIN.get('ce') === undefined) 
            return;
		for(var i =0; i < models.length; i++) {
			if(models[i].name === ce) {
				MAIN.set('ce', i);
				// MAIN.set('current_edit.arch.layer_dicts', models[i].arch.layer_dicts);
			}
		}
        MAIN.set('my_models', MAIN.get('my_models'));
	});

	MAIN.observe( 'my_models['+MAIN.get('ce')+']', function () {
		models = MAIN.get('my_models');
        if(models.length <= 0) {
            return;
        }
        ce = MAIN.get('ce');
        if(ce !== undefined) {
            models[ce].updated = true;
            MAIN.set('my_models', models);
        }
	});

	MAIN.observe( 'new_model.name', function () {
		model = MAIN.get('new_model');
		model.updated = true;
		MAIN.set('new_model', model);
	});
	MAIN.observe( 'new_model.arch', function () {
		model = MAIN.get('new_model');
		model.updated = true;
		MAIN.set('new_model', model);
	});

    MAIN.on("clickrow", function(e) {
        id = $(e.node).data('href');
        window.document.location = id
    });

    load_models(MAIN, 1, 100, on_model_load);
    MAIN.set('new_model.updated', false);
	
	setTimeout( function() {
		if(vars['model_id']) {
		  mdls = MAIN.get('my_models');
		  for(var i = 0; i < mdls.length; i++) {
			if(mdls[i].id === parseInt(vars['model_id'])) {
				MAIN.set('ce', i);
				MAIN.set('current_edit_name', mdls[i].name);
			}
		  }
		}
	}, 100);


});
