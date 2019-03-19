odoo.define('ifs_dental_product.streatment', function (require) {
    "use strict";

    require('web.dom_ready');
    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var context = require('web_editor.context');
    var field_utils = require('web.field_utils');
$( document ).ready(function (name) {
	
	function load_locale(){
        var url = "/web/webclient/locale/" + context.get().lang || 'en_US';
        return ajax.loadJS(url);
    }

    var ready_with_locale = $.when(base.ready(), load_locale());
    // datetimepicker use moment locale to display date format according to language
    // frontend does not load moment locale at all.
    // so wait until DOM ready with locale then init datetimepicker
    
    $('.form-control.date').datetimepicker({
            format : time.getLangDateFormat(),
            minDate: moment({ y: 1900 }),
            maxDate: moment().add(200, "y"),
            calendarWeeks: true,
            icons: {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                next: 'fa fa-chevron-right',
                previous: 'fa fa-chevron-left',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down',
            },
            locale : moment.locale(),
            allowInputToggle: true,
            keyBinds: null,
        });
   
                
                
});
});