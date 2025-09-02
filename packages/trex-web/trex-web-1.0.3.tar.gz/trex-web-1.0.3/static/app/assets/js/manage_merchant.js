function initManageMerchant(){
	$.console.log('---initManageMerchant---');
	
	
	$('#add_merchant_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked add_merchant_button');
		var add_merchant_url = $(this).data('add-merchant-url');
		$('#content').overlay();
		
		/*
		$('#content').load(add_merchant_url, function(){
			$('#content').overlay('hide');
		}).hide().fadeIn();
		*/
		
		openFullWidthModal({
            open_modal_element  : $(this),
            content_url         : add_merchant_url,
            callback            : function(){
                                        $('#content').overlay('hide');              
                                    }
        });
		
	});
	
	$('#search_merchant_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked search_merchant_button');
		$('#search_merchant_form').submit();
		
		
	});
	
	$('#list_all_merchant_button').click(function(event){
		event.preventDefault();
		$.console.log('Clicked list_all_merchant_button');
		var list_all_merchant_url = $(this).data('list-all-merchant-url');
		$('#merchant_list_div').overlay();
		
		$('#merchant_list_div').load(list_all_merchant_url, function(){
			$('#merchant_list_div').overlay('hide');
		}).hide().fadeIn();
		
	});
	
	$('#reset_search_merchant_button').click(function(event){
		event.preventDefault();
		$('#search_merchant_form').trigger("reset");
		$.console.log('Clicked reset_merchant_button');
	});
	
	//initMerchantListing();
	validateSearchMerchantAcctForm();
	
}


function initAddMerchant(){
	$.console.log('---initAddMerchant---');
	
	validateMerchantDetailsForm();
	initMerchantDetailsButtons();
}

function initMerchantDetailsButtons(){
	$('#save_merchant_button').click(function(event){
		event.preventDefault();
		$('#merchant_details_form').submit();
	});
	
	$('#reset_manage_merchant_button').click(function(event){
		event.preventDefault();
		$('#merchant_details_form').trigger("reset");
		
	});
	
	$('#back_to_manage_merchant_button').click(function(event){
		event.preventDefault();
		var back_url = $(this).data('back-url');
		
		$.console.log('back_url='+back_url);
		
		$('#content').overlay();
		
		$('#content').load(back_url, function(){
			$('#content').overlay('hide');
		}).hide().fadeIn();
	});	
}

function validateSearchMerchantAcctForm(){
	$('#search_merchant_form').validate({
						rules:{
        					company_name:{
                				require_from_group	:[1, ".search-input"],
								maxlength   		: 150
							},
							account_code:{
                				require_from_group	:[1, ".search-input"],
								maxlength   		: 16
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
							//submitSearchMerchantForm(form);
							loadSearchMerchantForm(form);
				        }//end submitHandler
    });
}

function validateMerchantDetailsForm(){
	$('#merchant_details_form').validate({
						rules:{
        					company_name:{
                				required    		: true,
								minlength			: 3,
                				maxlength   		: 150
							},
							brand_name:{
								required    		: true,
                				minlength			: 3,
								maxlength   		: 100
							},
							
							contact_name:{
                				required    		: true,
								minlength			: 3,
                				maxlength   		: 250
							},
							email:{
								email				: true,
								required    		: true,
                				maxlength			: 150
							},
							plan_start_date:{
                				required    		: true
							},
							plan_end_date:{
                				required    		: true
							},
							outlet_limit:{
                				required    		: true

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
				            submitMerchantDetailsForm(form);
				        }//end submitHandler
    });
}

function submitMerchantDetailsForm(form){
	var is_merchant_key_available  = $('input[name=key]').val();
	var is_update_merchant_details = is_merchant_key_available !=='';
	
	$.console.log('submitMerchantDetailsForm: is_update_merchant_details='+is_update_merchant_details);
	
	var $save_merchant_button 				= $('#save_merchant_button');
	var merchant_details_data 				= $(form).serializeJSON();
	
	$.console.log('merchant_details_data='+JSON.stringify(merchant_details_data));
	
	showLoading();
	
	$save_merchant_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: merchant_details_data,
            success 	: function(response) {
				$.console.log('after submitted with success ='+ JSON.stringify(response));
				
				hideLoading();
				$save_merchant_button.enabled();
				if(is_update_merchant_details==false){
					var created_merchant_key = response.created_merchant_key;
					$.console.log('created_merchant_key='+created_merchant_key);
					$('input[name=key]').val(created_merchant_key);
					form.action = response.post_url
					$('#merchant_details_nav_tabs').show();	
				}
				
				notify('success', HURRAY, createNotifyMessageHTML(response.msg));
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	/*
				$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				try{
					var error_message = jqXHR.responseText;
					var error_message_in_json = JSON.parse(error_message);
					$.console.log('error error_message_in_json='+error_message_in_json);
					hideLoading();
					$save_merchant_button.enabled();
					var error_message_title = FAILED_TO_ADD_MERCHANT;
					if(is_update_merchant_details){
						error_message_title = FAILED_TO_UPDATE_MERCHANT;
					}
					notify('error', error_message_title, createNotifyMessageHTML(error_message_in_json.msg));
				}catch(error){
					$save_merchant_button.enabled();
					notify('error', error_message_title, FAILED_TO_PROCESS);
				}
				*/
				
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(error_message){
								var error_message_title = FAILED_TO_ADD_MERCHANT;
								if(is_update_merchant_details){
									error_message_title = FAILED_TO_UPDATE_MERCHANT;
								}
								
								
								hideLoading();
								$save_merchant_button.enabled();
								notify('error', error_message_title, createNotifyMessageHTML(error_message));
							}
							)
				
				
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    });
}

function initMerchantListing(){
	$.console.log('---initMerchantListing---');
	
	//$(document).on('click', '.edit-merchant', function(event){
	$('.edit-merchant').click(function(event){			
		event.preventDefault();
		$.console.log('Clicked edit_merchant_button');
		$.console.log('going to read merchant url');
		var read_merchant_url = $(this).data('read-merchant-url');
		$.console.log('read_merchant_url='+read_merchant_url);
		
		//$('#content').overlay();
		$('#content').html(SHOW_LOAD_OVERLAY_TEMPLATE);
		/*
		$('#content').load(read_merchant_url, function(){
			$('#content').overlay('hide');
		}).hide().fadeIn();
		*/
		
		$('#content').load(read_merchant_url, function(response, status, xhr){
			
			handleRequestForLoadContent(response, status, xhr, 
							function(){
								$('#content').overlay('hide');
							},
							function(){
								$('#content').overlay('hide');
							}
							)
		}).hide().fadeIn();
		
	});
	
	//$(document).on('click', '.delete-merchant', function(event){
	$('.delete-merchant').click(function(event){		
		event.preventDefault();
		$.console.log('Clicked delete_merchant_button');
		var delete_merchant_url 	= $(this).data('delete-merchant-url');
		var $deleting_row 			= $(this).closest('tr'); 
		$.confirm({
		    title	: CONFIRM_TO_DELETE,
		    content	: ARE_YOU_CONFIRM_TO_DELETE_MERCHANT_ACCOUNT,
		    type: 'green',
		    buttons: {   
		        ok: {
		            text: OKAY,
		            btnClass: 'btn-primary',
		            keys: ['enter'],
		            action: function(){
		                 	$.console.log('the user clicked confirm');
						 	
							$.console.log('delete_merchant_url='+delete_merchant_url);
							deleteMerchantAccount(delete_merchant_url, function(response){
								hideLoading();
								notify('success', HURRAY, createNotifyMessageHTML(response.msg));
								$deleting_row.fadeOut('fast', function(){
									$deleting_row.remove();	
									
								});
								
								
							});
							
							showLoading();
		            }
		        },
		        cancel: function(){
						text: CANCEL,
		                $.console.log('the user clicked cancel');
		        }
		    }
		});
		
		
		
		
	});
}

function deleteMerchantAccount(delete_merchant_url, callback){
	$.ajax({
            url 		: delete_merchant_url,
            type 		: 'DELETE',
			dataType 	: 'json', 
            success 	: function(response) {
				if(callback){
					callback(response);
				}
				
				
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	/*
				$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				notify('error', 'Failed to delete merchant account', createNotifyMessageHTML(error_message_in_json.msg));
				*/
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(error_message){
								hideLoading();
								notify('error', FAILED_TO_DELETE_MERCHANT, createNotifyMessageHTML(error_message));
							}
							)
				
	        },
	        beforeSend : function(xhr) {
	        	
	        }            
    	});
}


function loadSearchMerchantForm(form){
	
	$.console.log('---loadSearchMerchantForm---')
	
	var $search_merchant_button 		= $('#search_merchant_button');
	var search_merchant_data 			= $(form).serializeJSON();
	var $search_result_div				= $('#merchant_list_div');
	
	$.console.log('form.action='+form.action);
	
	$.console.log('search_merchant_data='+JSON.stringify(search_merchant_data));
	
	$search_customer_button.disabled();
	
	$search_result_div.html('');
	
	createCRSFHeader();
	
	$search_result_div.load(form.action, search_merchant_data, function(response, status, xhr){
							
							$search_merchant_button.enabled();
							
							handleRequestForLoadContent(response, status, xhr, 
											function(error_message){
												$search_result_div.overlay('hide');
												notify_error(FAILED_TO_SEARCH_MERCHANT, createNotifyMessageHTML(error_message));
											},
											function(){
												$search_result_div.overlay('hide');
												
												
											}
											)
						}).hide().fadeIn('slow', function(){
							var scrool_to = $search_result_div.offset().top;
												
							$.console.log('scrool_to='+scrool_to);
							
							$('html, body').animate({
						         scrollTop: scrool_to
						     }, 1500);
						});
}

function submitSearchMerchantForm(form){
	$.console.log('---submitSearchMerchantForm---');
	
	var $search_merchant_button 			= $('#search_merchant_button');
	var search_merchant_data 				= $(form).serializeJSON();
	
	$.console.log('search_merchant_data='+JSON.stringify(search_merchant_data));
	
	
	//$search_merchant_button.disabled();
	
	$.ajax({
            url 		: form.action,
            type 		: form.method,
			dataType 	: 'json', 
            data 		: search_merchant_data,
            success 	: function(response) {
				try{
					$.console.log('after submitted with success ='+ JSON.stringify(response));
					var result_url = response.result_url;
					$.console.log(response);
					$.console.log('result_url='+result_url);
					$('#merchant_list_div').overlay();
					
					if(result_url){
						$('#merchant_list_div').load(result_url, function(){
							$('#merchant_list_div').overlay('hide');
						}).hide().fadeIn();
					}
					
					 	
				}catch(error){
					$.console.log(error);	
				}
				
				hideLoading();
				$search_merchant_button.enabled();
				
            },
	        error : function(jqXHR, textStatus, errorThrown) {
	           	/*
				$.console.log('after submitted with error ='+ JSON.stringify(jqXHR));
				var error_message = jqXHR.responseText;
				var error_message_in_json = JSON.parse(error_message);
				$.console.log('error error_message_in_json='+error_message_in_json);
				hideLoading();
				$search_merchant_button.enabled();
				notify('error', 'Failed to search merchant', createNotifyMessageHTML(error_message_in_json.msg));
				*/
				handleErrorRequestForAjaxCall(jqXHR, textStatus, errorThrown, 
							function(error_message){
								hideLoading();
								$search_merchant_button.enabled();
								notify('error', FAILED_TO_SEARCH_MERCHANT, createNotifyMessageHTML(error_message));
							}
							)
				
	        },
	        beforeSend : function(xhr) {
	        	//showLoading();
	        }            
    });
}

function initUpdateMerchant(){
	$.console.log('----initUpdateMerchant----');
	
	validateMerchantDetailsForm();
	
	initMerchantDetailsButtons();
}

