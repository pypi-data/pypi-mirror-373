/**
 * jQuery Loading Block
 *
 * demos / documentation: https://github.com/chan15/jquery-loading-block
 *
 * @author Chan
 */
;(function ($) {
    $.loadingBlockShow = function(opts) {
        var defaults = {
            imgPath: '/app/img/shared/icon.gif',
            imgStyle: {
                width: 'auto',
                textAlign: 'center',
                marginTop: '20%'
            }, 
            text: 'loading...',
            style: {
                position: 'fixed',
                width: '100%',
                height: '100%',
                background: 'rgba(255, 255, 255, .8)',
                left: 0,
                top: 0,
                zIndex: 10000
            }
        };

		$.console.log('opts='+JSON.stringify(opts));

        $.extend(defaults, opts);
        $.loadingBlockHide();
		var show_in_target_selector = opts['target_selector'];
		
		$.console.log('show_in_target_selector='+show_in_target_selector);
		
		if(show_in_target_selector){
			var img = $('<div><img src="' + defaults.imgPath + '"><div>' + defaults.text + '</div></div>');
        	var block = $('<div id="loading_block"></div>');

        	block.css(defaults.style).appendTo($(show_in_target_selector));
        	img.css(defaults.imgStyle).appendTo(block);
		}else{
			var img = $('<div><img src="' + defaults.imgPath + '"><div>' + defaults.text + '</div></div>');
        	var block = $('<div id="loading_block"></div>');

        	block.css(defaults.style).appendTo('body');
        	img.css(defaults.imgStyle).appendTo(block);
		}
		
		
        
    };

    $.loadingBlockHide = function() {
        $('#loading_block').remove();
    };
}(jQuery));
