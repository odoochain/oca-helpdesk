// odoo.define nos agrega en un objeto permite compilar el codigo en odoo va el nombre_modulo/nombre_archivo
odoo.define('helpdesk_ticket_custom.javascript', function(require) {
    "use strict";
    // web.dom_ready nos ejecutar despues de esta linea
    require('web.dom_ready');
    // Nos permite llamar objetos desde el controller
    var ajax = require('web.ajax');
    // usamos jquery y llamamos el id #
    var button = $('#boton');
    // Agregamos una función el parametro 'call' nos permite hacer llamados
    // El controller siempre esta esperando recibir algo en este caso enviamos un parametro vacio
    // El then nos permite llamar la variable del controller retornada y el log, en pocas palabras cargar la variable sg
    var _onButton = function(e) {
        ajax.jsonRpc('/ticket', 'call', {}).then(function(data)) {
            console.log(data)
        }
    }
    // al dar click al boton ejecuta la función
    button.click(_onButton);
});