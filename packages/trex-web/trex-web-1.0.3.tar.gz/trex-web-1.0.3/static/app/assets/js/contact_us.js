var is_contact_us_from_dashboard=false;

function initContactUs(){
	$.console.log('---initContactUs---');
	validateContactUsForm();
	
	$('#contact_us_button').click(function(e){
		e.preventDefault();
		$('#contact_us_form').submit();
		
	});	
	
}

function initContactUsFromDashboard(){
	$.console.log('---initContactUsFromDashboard---');
	validateContactUsForm();
	is_contact_us_from_dashboard = true;
	$('#contact_us_button').click(function(e){
		e.preventDefault();
		$('#contact_us_form').submit();
		
	});	
	
}

function validateContactUsForm(){
	
	$('#contact_us_form').validate({
						rules:{
        					name:{
                				required    		: true,
								minlength			: 3,
                				maxlength   		: 200
							},
							email:{
								email				: true,
								required    		: true,
                				maxlength			: 150
							},
							subject:{
                				required    		: true,
								maxlength			: 300
							},
                            message:{
                                required            : true,
                                maxlength           : 3000
                            }
						},
						errorClass	: "help-block error",
				        validClass 	: "success",
				        errorElement: "div",
				        highlight:function(element, errorClass, validClass) {
				            $(element).parents('.control-group').addClass('error').removeClass(validClass);
				        },
				        unhighlight: function(element, errorClass, validClass) {
				            $(element).parents('.error').removeClass('error').addClass(validClass);
				        },
				        submitHandler : function(form) {
				            submitContactUsForm(form);
				        }//end submitHandler
    });
}

function submitContactUsForm(form){
	var $contact_us_button 				= $('#contact_us_button');
	var contact_us_data 				= $(form).serializeJSON();
	
	$.console.log('contact_us_data='+JSON.stringify(contact_us_data));
	
	showLoading();
	
	$contact_us_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: contact_us_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$contact_us_button.enabled();
				
				notify('success', 'Hurray~!', createNotifyMessageHTML(response));
				
				$.console.log('is_contact_us_from_dashboard='+is_contact_us_from_dashboard);
				
				if(is_contact_us_from_dashboard){
					var $clicked_side_menu	= $('.main-sidebar a.nav-menu.active');
					
					$('#content').load('/thank-you-for-contact-us', function(){
						$clicked_side_menu.removeClass('active');
						
					}).hide().fadeIn();
				}else{
					window.location = '/thank-you-for-contact-us';
					
				}

            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$contact_us_button.enabled();
				notify('error', 'Failed to contact', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
}