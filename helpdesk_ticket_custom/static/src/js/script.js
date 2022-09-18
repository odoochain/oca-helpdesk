odoo.define('helpdesk_ticket_custom.script', function (require) {
    "use strict";
    require('web.dom_ready');
    const tour = require('web_tour.tour');



    $(function () {

        $("#helpdesk_family").change(function() {
            let family_id = $("#helpdesk_family").val();
            console.log(family_id);
            $.ajax({
                    type: "GET",
                    url: "/familty/sub_grupo/" + family_id,
                    dataType: "json",
                    success: function (response) {
                        //var data = JSON.parse(response);
                        console.log(response);
                        if(response){
                            var t = '<option value="">-- Seleccione --</option>';
                            $(response).each(function (i, v) {
                                t += '<option value="' + v.id + '">' + v.name + '</option>';
                            })
                            $('#helpdesk_sub_grupo').empty();
                            $('#helpdesk_sub_grupo').html(t);
                        }
                        else{
                            $('#helpdesk_sub_grupo').empty();
                        }

                    }
                });


        });


     });

})
