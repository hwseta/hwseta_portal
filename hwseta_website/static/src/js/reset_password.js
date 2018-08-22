$(document).ready(function(){
	$('.oe_login_buttons .reset_pwd').click(function() {
    	email=$('.field-login #login').val();
    	if (email){
        	$.ajax({url: "/web/login/hwseta_reset_password",
                type:"post", 
                dataType:"json",
                async:false,
                data:{'user_email_id':email},
                success: function(result){
                	if (result.length>0){
    	    			if(result[0].email==true){
    	    				$("<div title='Info'>Reset Link has been send on your register email id!!</div>").dialog();
    	    			}
    	    			else if (result[0].email==false){
    	    				$("<div title='Warning'>Enter Valid Username!!</div>").dialog();
    	    			}
    	
        			}
                },
        	});
    	}
    	else if(!email){
    		$("<div title='Warning'>Enter Username First!!</div>").dialog();
    	}
    	
    });

});

$(document).ready(function() { 
//     	$('.oe_login_buttons #login').click(function() {
//         	email=$('.field-login #login').val();
// 			$('.oe_login_form').submit(function(e){
// 			    return false;
// 			});
//         	if (email){
//             	$.ajax({url: "/web/login/get_dormant",
//                     type:"post", 
//                     dataType:"json",
//                     async:true,
//                     data:{'user_email_id':email},
//                     success: function(result){
//                     	console.log("get_dormant reuslt-----",result);
//                     	if (result.length>0){
//         	    			if(result[0].email==true){
//         	    				$.blockUI({ message: $('#question'), css: { width: '300px' } });
//         	    				$('#user_id').val(parseInt(result[0].user));
//         	    			}
//         	    			else if (result[0].email==false){
//         	    				$('.oe_login_form').unbind('submit').submit();
//         	    				$('#user_id').val(paserInt(result[0].user));
//         	    			}
//         	
//             			}
//                     },
//             	});
//         	}
//         	else if(!email){
//         		$("<div title='Warning'>Enter Username First!!</div>").dialog();
//         	}
//         	
//         });  
    	$('.oe_login_form #yes').click(function() {
    		var user_id=$('#user_id').val();
        	if (user_id){
            	$.ajax({url: "/web/login/deselect_dormant",
                    type:"post", 
                    dataType:"json",
                    async:true,
                    data:{'user_id':parseInt(user_id)},
                    success: function(result){
                    	 $.unblockUI();
                    	 $('.oe_login_form').unbind('submit').submit();
                    },
            	});
        	}
    	});
    	$('.oe_login_form #no').click(function() {
    		var user_id=$('#user_id').val();
        	if (user_id){
            	$.ajax({url: "/web/login/in_active",
                    type:"post", 
                    dataType:"json",
                    async:true,
                    data:{'user_id':parseInt(user_id)},
                    success: function(result){
                    	 $.unblockUI();
                    },
            	});
        	}
    	});    	
    }); 


