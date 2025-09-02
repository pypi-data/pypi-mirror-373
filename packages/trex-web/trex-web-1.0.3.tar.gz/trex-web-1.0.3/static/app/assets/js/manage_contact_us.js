function initManageContactUs(){
    $.console.log('---initManageContactUs---');
    
    //$('.view-contact-us-message').click(function(event){
    $(document).on('click', '.view-contact-us-message', function(){          
        event.preventDefault();
        $.console.log('Clicked view_contact_us_message');
        
        var subject = $(this).data('subject');
        var read_contact_us_url = $(this).data('read-contact-us-url');
        $.console.log('subject='+subject);
        $.console.log('read_contact_us_url='+read_contact_us_url);
        
        
        
        openFullWidthModal({
            open_modal_element    : $(this),
            title                 : subject,
            content_url           : read_contact_us_url,
        });
        
    });
}