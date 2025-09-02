function initSignUpPage(){
	loadCountryCode();
	validateSignupForm();
	
	$('#signup_button').click(function(e){
		e.preventDefault();
		$('#signup_form').submit();
	});
	
	//notify('info','Test', 'Test show notify message');
	//var next_url_button_html = createNextButtonHTML('/dashboard');
	//notify('success', 'Hurray~!', createNotifyMessageHTML("Yes~!", next_url_button_html));
	

}

function loadCountryCode(){
	var $country_option = $('#country');
	$.ajax({
		 url 		: "/system/list-country-code",
		 success 	: function(response_data) {
	  	
						$.console.log($country_option.html());
						
						$.each(response_data, function(key, value) {
							//$.console.log('country name='+value.cnty_name);    
							$country_option.append($('<option></option>').attr('value', value.cnty_code).text(value.cnty_name));     
				    	});

					}
	});
}

function validateSignupForm(){
	
	jQuery.validator.addMethod(
	  "straightPassword",
	  function(value, element) {
	    // This is your regex, I have not looked closely at it to see if it is sensible
	    return value.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/); 
	  },
	  "Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character (@$!%*#?&). E.g. P@ssW0r4"
	);
	
	$('#signup_form').validate({
						rules:{
        					fullname:{
                				required    		: true,
								minlength			: 3,
                				maxlength   		: 100
							},
							country:{
                				required    		: true
							},
							city:{
                				maxlength   		: 150
							},
							email:{
								email				: true,
								required    		: true,
                				maxlength			: 150
							},
							password	:{
								required    		: true,
                				maxlength   		: 30,
								minlength			: 6,
								straightPassword	: true && window.debug_mode==false
							},
							confirm_password	:{
								required    		: true,
                				maxlength   		: 30,
								minlength			: 6,
                				equalTo 			: "#password",
								straightPassword	: true && window.debug_mode==false
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
				            submitSignupForm(form);
				        }//end submitHandler
    });
}

function submitSignupForm(form){
	var $signup_button 				= $('#signup_button');
	var signup_data 				= $(form).serializeJSON();
	var password					= signup_data['password'];
	var confirm_password			= signup_data['confirm_password'];
	
	$.console.log('password='+password);
	$.console.log('confirm_password='+confirm_password);
	
	var hashed_password				= CryptoJS.MD5(password).toString();
	var hashed_confirm_password		= CryptoJS.MD5(confirm_password).toString();
	
	$.console.log('hashed_password='+hashed_password);
	$.console.log('hashed_confirm_password='+hashed_confirm_password);
	
	signup_data['password'] 		= hashed_password;
	signup_data['confirm_password'] = hashed_confirm_password;
	
	$.console.log('signup_data='+JSON.stringify(signup_data));
	
	showLoading();
	
	$signup_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: signup_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				var next_url_button_html = createNextButtonHTML('/dashboard');
				hideLoading();
				
				window.location = DASHBOARD_URL;
				//notify('success', 'Hurray~!', createNotifyMessageHTML(response, next_url_button_html));
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$signup_button.enabled();
				notify('error', 'Failed to register account', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
}