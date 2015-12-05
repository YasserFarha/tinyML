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
            murl: murl
        },
    });

  function load_models(page, page_size) {
      $.ajax(MAIN.get("murl"),
          { method: 'POST', data: {'page' : page, 'page_size' : page_size},
          success: function (data) { 
            for(var i = 0; i < data['models'].length; i++) {
              data['models'][i]['uuid_short'] = data['models'][i]['uuid'].substring(0, 8)
            }
            MAIN.set('models', data['models']);
            models = MAIN.get('models')
         }
        }
      );
    }

  function load_transactions(page, page_size, callback) {
      $.ajax(MAIN.get("turl"),
          { method: 'POST', data: {'page' : page, 'page_size' : page_size},
          success: function (data) { 
            for(var i = 0; i < data['transactions'].length; i++) {
              data['transactions'][i]['uuid_short'] = data['transactions'][i]['uuid'].substring(0, 8)
            }
			callback(data);
            console.log(data);
          }
        }
      );
    }

    setInterval(function() { load_models(1, 6); }, 2000);
    setInterval(function() { load_transactions(1, 8, function(data) {
            MAIN.set('transactions', data['transactions']);
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

   function plot_home() {
		TESTER = document.getElementById('home_plot');
		var layout = {
			margin : {l:30, r:10, t:20, b:20},
			height : 180,
			pad : 20,
            autosize: "initial",
            showlegend: false
		};
		models = MAIN.get('models');
        load_transactions(1, 50, function(data) {
            trs = data['transactions'];
            console.log(trs);
            data = [];
            times = [];
            colors = [
                'rgb(128, 0, 128)',
                'rgb(34, 34, 100)',
                'rgb(8, 89, 14)',
                'rgb(128, 12, 12)',
                'rgb(12, 128, 1)',
                'rgb(2, 0, 128)'
            ]
           for(var j = 0; j < trs.length; j++) {
                var d = new Date(trs[j].created_at);
                d.setSeconds(d.getSeconds() + 30);
                d.setSeconds(0);
                times.push(d);
            }
            for(var i = 0; i < models.length; i++) {
               pdata = {
                    x : [], y : [],
                    marker: {
                        color: colors[i%colors.length],
                        size: 8
                    },
                    line: {
                        color: colors[i%colors.length],
                        width:2 
                    },
                    name: models[i].name,
                    mode: "markers"
               }
               for(var j = 0; j < trs.length; j++) {
                    if(trs[j].model === models[i].id) {
                        var d = new Date(trs[j].created_at);
                        d.setSeconds(d.getSeconds() + 30);
                        d.setSeconds(0);
                        var found = false;
                        for(var k = 0; k < pdata.x.length; k++) {
                            console.log(d);console.log(pdata.x[k]);console.log("\n");
                            if(pdata.x[k].getTime() === d.getTime()) {
                                console.log("inner");
                                pdata.y[k] += 1;
                                found = true;	
                                break;
                             }
                        }
                        if(!found) {
                            pdata.y.push(1);
                            pdata.x.push(d);
                        }
                    }
               } 
               data.push(pdata);
            }
            console.log(data);
            Plotly.newPlot(TESTER, data,
            layout, {showLink : false});
        })
	}

  load_models(1, 6);
  load_transactions(1, 8, function(data) {  
    MAIN.set('transactions', data['transactions']);
  });

  setTimeout(plot_home, 200); 
  window.addEventListener( 'resize', resizeHandler = function () {
        plot_home();
    }, false );

});
