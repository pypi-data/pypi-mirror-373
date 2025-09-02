function initManageAdmin(){
	$.console.log('---initManageAdmin---');
	
	
	$('#add_admin_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked add_admin_button');
		/*
		var add_admin_url = $(this).data('add-admin-url');
		$('#content').overlay();
		
		$('#content').load(add_admin_url, function(){
			$('#content').overlay('hide');
		}).hide().fadeIn();
		*/
		var add_admin_url 	= $(this).data('add-admin-url');
		var title 			= $(this).data('title');
		
		
		openFullWidthModal({
		    open_modal_element    : $(this),
		    title                 : title,
		    content_url           : add_admin_url,
		});
		
		
		
	});
	
	$('#search_admin_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked search_admin_button');
		$.console.log('Going to submit form search~!');
		
		$('#manage_admin_form').submit();
		
	});
	
	$('#list_all_admin_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked list_all_admin_button');
		var list_all_admin_url = $(this).data('list-all-admin-url');
		$('#admin_search_list_div').overlay();
		
		$('#admin_search_list_div').load(list_all_admin_url, function(response, status, xhr){
			
			handleRequestForLoadContent(response, status, xhr, 
							function(){
								$('#admin_search_list_div').overlay('hide');
							},
							function(){
								$('#admin_search_list_div').overlay('hide');
							}
							)
		}).hide().fadeIn();
		
		
		
	});
	
	$('#reset_search_admin_button').click(function(event){
		$('#search_admin_form').trigger("reset");
		$.console.log('Clicked reset_admin_button');
	});
	
	//initAdminListing();
	validateSearchAdminAcctForm();
	
	
}

function validateSearchAdminAcctForm(){
	$.console.log('---validateSearchAdminAcctForm---');
	$('#manage_admin_form').validate({
						rules:{
        					email:{
								required    		: true,
								maxlength   		: 300
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
							submitSearchAdminAcctForm(form);
				        }//end submitHandler
    });
}

function submitSearchAdminAcctForm(form){
	$.console.log('---submitSearchAdminAcctForm---');
	
	var $search_admin_button 			= $('#search_admin_button');
	var search_admin_data 				= $(form).serializeJSON();
	
	$.console.log('search_admin_data='+JSON.stringify(search_admin_data));
	$.console.log('form.action='+form.action);
	
	
	$search_admin_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: search_admin_data,
            success 	: function(response) {
				try{
					$.console.log('after submitted with success ='+ JSON.stringify(response));
					var result_url = response.result_url;
					$.console.log(response);
					$.console.log('result_url='+result_url);
					$('#admin_search_list_div').overlay();
					
					if(result_url){
						$('#admin_search_list_div').load(result_url, function(response, status, xhr){
			
							handleRequestForLoadContent(response, status, xhr, 
											function(){
												$('#admin_search_list_div').overlay('hide');
											},
											function(){
												$('#admin_search_list_div').overlay('hide');
											}
											)
						}).hide().fadeIn();
						
					}
					
					 	
				}catch(error){
					$.console.log(error);	
				}
				
				hideLoading();
				$search_admin_button.enabled();
				
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	/*
				$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				$.console.log('textStatus ='+ JSON.stringify(textStatus));
				$.console.log('errorThrown ='+ JSON.stringify(errorThrown));
				var response 	= jqXHR.responseText;
				var status		= textStatus;
				var status_code = jqXHR.status;
				
				$.console.log('error response='+JSON.stringify(response));
				$.console.log('error status='+JSON.stringify(status));
				$.console.log('error status_code='+JSON.stringify(status_code));
				*/
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(){
								hideLoading();
								$search_admin_button.enabled();
								notify('error', 'Failed to search admin account', createNotifyMessageHTML(error_message_in_json.msg));
							}
							)



				
				
				//hideLoading();
				//$search_admin_button.enabled();
				//notify('error', 'Failed to search admin account', createNotifyMessageHTML(error_message_in_json.msg));
	        },
	        beforeSend : function(xhr) {
	        	//showLoading();
	        }            
    });
	
}

function initAddAdmin(){
	$.console.log('---initAddAdmin---');
	
	validateAdminDetailsForm();
	initAdminDetailsButtons();
}

function initAdminDetailsButtons(){
	$('#save_admin_button').click(function(event){
		event.preventDefault();
		$('#admin_details_form').submit();
	});
	
	$('#reset_manage_admin_button').click(function(event){
		event.preventDefault();
		$('#admin_details_form').trigger("reset");
		
	});
	/*
	$('#back_to_manage_admin_button').click(function(event){
		event.preventDefault();
		var back_url = $(this).data('back-url');
		
		$.console.log('back_url='+back_url);
		
		$('#content').overlay();
		
		$('#content').load(back_url, function(){
			$('#content').overlay('hide');
		}).hide().fadeIn();
	});	
	*/
}

function validateAdminDetailsForm(){
	
	
	$('#admin_details_form').validate({
						rules:{
        					name:{
                				required    		: true,
								minlength			: 3,
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
				            submitAdminDetailsForm(form);
				        }//end submitHandler
    });
}


function submitAdminDetailsForm(form){
	$.console.log('---submitAdminDetailsForm---');
	
	var is_admin_key_available = $('input[name=key]').val();
	is_update_admin_details = is_admin_key_available!='';
	
	$.console.log('submitAdminDetailsForm: is_update_admin_details='+is_update_admin_details);
	
	var $add_admin_button 				= $('#save_admin_button');
	var admin_details_data 				= $(form).serializeJSON();
	
	$.console.log('admin_details_data='+JSON.stringify(admin_details_data));
	if(is_update_admin_details==false){
		var password						= admin_details_data['password'];
		var confirm_password				= admin_details_data['confirm_password'];
		
		$.console.log('password='+password);
		$.console.log('confirm_password='+confirm_password);
		
		var hashed_password				= CryptoJS.MD5(password).toString();
		var hashed_confirm_password		= CryptoJS.MD5(confirm_password).toString();
		
		$.console.log('hashed_password='+hashed_password);
		$.console.log('hashed_confirm_password='+hashed_confirm_password);
		
		admin_details_data['password'] 			= hashed_password;
		admin_details_data['confirm_password'] = hashed_confirm_password;
	}
	$.console.log('admin_details_data='+JSON.stringify(admin_details_data));
	
	showLoading();
	
	$add_admin_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: admin_details_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$add_admin_button.enabled();
				if(is_update_admin_details==false){
					var created_admin_key = response.created_admin_key;
					$.console.log('created_admin_key='+created_admin_key);
					$('input[name=key]').val(created_admin_key);
					form.action = response.post_url
					$('#password_input_div').remove();
				}
				notify('success', HURRAY, createNotifyMessageHTML(response.msg));
            },
	        error : function(jqXHR, textStatus, errorThrown) {
		
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(){
								hideLoading();
								$add_admin_button.enabled();
								var error_message_title = FAILED_TO_ADD_ADMIN;
								if(is_update_admin_details){
									error_message_title = FAILED_TO_UPDATE_ADMIN;
								}
								
								notify('error', error_message_title, createNotifyMessageHTML(error_message_in_json.msg));
							}
							)
							
	           	/*
				$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$add_admin_button.enabled();
				var error_message_title = FAILED_TO_ADD_ADMIN;
				if(is_update_admin_details){
					error_message_title = FAILED_TO_UPDATE_ADMIN;
				}
				
				notify('error', error_message_title, createNotifyMessageHTML(error_message_in_json.msg));
				*/
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
}

function initAdminListing(){
	$.console.log('---initAdminListing---');
	//$(document).on('click','.edit-admin',function(event){
	$('.edit-admin').click(function(event){		
		event.preventDefault();
		$.console.log('Clicked edit_admin_button');
		$.console.log('going to read admin url');
		
		var read_admin_url 	= $(this).data('read-admin-url');
		var modal_title 	= $(this).data('title');
		
		openFullWidthModal({
            open_modal_element    : $(this),
            title                 : modal_title,
            content_url           : read_admin_url,
        });
		
		/*
		
		$.console.log('read_admin_url='+read_admin_url);
		$.console.log('modal_title='+modal_title);
		
		var $input_modal_body 	= $('#input_modal .modal-body');
		var $input_modal_title 	= $('#input_modal .modal-title');
		
		$input_modal_title.text(modal_title);
		$input_modal_body.overlay();
		
		$input_modal_body.load(read_admin_url, function(){
			$(this).overlay('hide');
			$('#input_modal').modal('show')
		});
		*/
	});
	
	//$(document).on('click','.delete-admin',function(event){
	$('.delete-admin').click(function(event){		
		event.preventDefault();
		$.console.log('Clicked delete_admin_button');
		var delete_admin_url 	= $(this).data('delete-admin-url');
		var $deleting_row 		= $(this).closest('tr'); 
		$.confirm({
		    title: CONFIRM_TO_DELETE,
		    content: ARE_YOU_CONFIRM_TO_DELETE_ADMIN_ACCOUNT,
		    type: 'green',
		    buttons: {   
		        ok: {
		            text: OKAY,
		            btnClass: 'btn-primary',
		            keys: ['enter'],
		            action: function(){
		                 	$.console.log('the user clicked confirm');
						 	
							$.console.log('delete_admin_url='+delete_admin_url);
							deleteAdminAccount(delete_admin_url, function(response){
								hideLoading();
								notify('success', 'Hurray~!', createNotifyMessageHTML(response.msg));
								$deleting_row.fadeOut('fast', function(){
									$deleting_row.remove();	
									
								});
								
								
							});
							
							showLoading();
		            }
		        },
		        cancel: function(){
		                $.console.log('the user clicked cancel');
		        }
		    }
		});
		
		
		
		
	});
}

function deleteAdminAccount(delete_admin_url, callback){
	$.ajax({
            url 		: delete_admin_url,
            type 		: 'DELETE',
			dataType 	: 'json', 
            success 	: function(response) {
				if(callback){
					callback(response);
				}
				
				
            },
	        error : function(jqXHR, textStatus, errorThrown) {
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(){
								hideLoading();
								notify('error', FAILED_TO_DELETE_ADMIN, createNotifyMessageHTML(error_message_in_json.msg));
							}
							)
		
				/*
	           	$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				notify('error', FAILED_TO_DELETE_ADMIN, createNotifyMessageHTML(error_message_in_json.msg));
				*/
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    	});
}


function initUpdateAdmin(){
	$.console.log('----initUpdateAdmin----');
	
	validateAdminDetailsForm();
	
	initAdminDetailsButtons();
}

