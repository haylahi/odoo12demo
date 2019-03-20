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
    
    _.each($('.input-group.date'), function(date_field){
        var minDate = $(date_field).data('mindate') || moment({ y: 1900 });
        var maxDate = $(date_field).data('maxdate') || moment().add(200, "y");
        $('#' + date_field.id).datetimepicker({
            format : time.getLangDateFormat(),
            minDate: minDate,
            maxDate: maxDate,
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
});
var loadFile = function(event) {
    var output = document.getElementById($("#"+event.target.id).attr("data-target"));
    output.src = URL.createObjectURL(event.target.files[0]);
    event.target.className="inputfile";
  };
function uploadeFile(hidden_input_image)
{
      var fileinputElement = document.getElementById(hidden_input_image);
      fileinputElement.click();
}   