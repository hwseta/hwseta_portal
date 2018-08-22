openerp.hwseta_menu_disable = function(instance){
	instance.web.Menu.include({	
		init : function()
		{
			var self = this;
			this._super();
		},
		
		menu_click : function(id, needaction){
			if (!id) { return; }

	        // find back the menuitem in dom to get the action
	        var $item = this.$el.find('a[data-menu=' + id + ']');
	        
	        if (!$item.length) {
	            $item = this.$secondary_menus.find('a[data-menu=' + id + ']');
	        }
	        var action_id = $item.data('action-id');
	        console.log("Action ID is :"+action_id+" "+typeof(action_id));
	        // code for menu disabling by removing action id
	        var data = {'action_id':action_id};
	        var parsed_str = ''
	        var array = []
	        var flag = 0;
	        var continue_flag = false;
	        console.log("data is :"+data);
	        $.ajax({
	        	'url':'/check_expired_menus',
	        	'type':'GET',
	        	'async':false,
	        	'data':data,
	        }).done(function(resp){
	        	console.log("Inside Success :"+JSON.stringify(resp));
	        	if (resp!='' || resp!=null){
	        		parsed_str = JSON.parse(resp);
	        	}
	        	if (parsed_str!='' || parsed_str!=null)
	        	{
	        	array = parsed_str.toString().split(",");
	        	}
	        	if (array!='' || array!=null){
		        	for (var i=0; i<array.length;i++){
		        		if (parseInt(array[i])==action_id){
		        			flag = 1;
		        			alert("Provider End Date has been expired. Please re-accredate again.");
		        			break;
		        		}
		        		else{
		        			continue_flag = true;
		        			flag=2;
		        		}
		        	}
	        	}//if
	        	else{
	        		flag=2;
	        	}//else
	        	
	        });
	        
	        if (flag==2){
		        // If first level menu doesnt have action trigger first leaf
		        if (!action_id) {
		            if(this.$el.has($item).length) {
		                var $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + id + ']');
		                var $items = $sub_menu.find('a[data-action-id]').filter('[data-action-id!=""]');
		                console.log("Items : "+$items);
		                if($items.length) {
		                    action_id = $items.data('action-id');
		                    id = $items.data('menu');
		                }
		            }
		        }
		        if (action_id) {
		            this.trigger('menu_click', {
		                action_id: action_id,
		                needaction: needaction,
		                id: id,
		                previous_menu_id: this.current_menu // Here we don't know if action will fail (in which case we have to revert menu)
		            }, $item);
		        } else {
		            console.log('Menu no action found web test 04 will fail');
		        }
	        	this.open_menu(id);
	        }
	        
		},
		
	});
	
};