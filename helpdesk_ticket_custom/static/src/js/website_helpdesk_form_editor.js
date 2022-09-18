odoo.define('helpdesk_ticket_custom.form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website.form_editor_registry');

var _t = core._t;

FormEditorRegistry.add('create_ticket', {
    formFields: [{
        type: 'char',
        required: true,
        name: 'partner_name',
        fillWith: 'name',
        string: 'Your Name',
    }, {
        type: 'email',
        required: true,
        name: 'partner_email',
        fillWith: 'email',
        string: 'Your Email',
    }, {
        type: 'char',
        modelRequired: true,
        name: 'name',
        string: 'Subject',
    }, {
        type: 'char',
        name: 'description',
        string: 'Description',
    }, {
        type: 'binary',
        custom: true,
        name: 'Attachment',
    }],
    fields: [{
        name: 'team_id',
        type: 'many2one',
        relation: 'helpdesk.team',
        string: _t('Helpdesk Team'),
    }, {
        name: 'projects',
        type: 'many2one',
        relation: 'project.project',
        string: _t('Proyecto'),
        title: _t('Proyecto'),
    }, {
        name: 'ticket_type_id',
        type: 'many2one',
        relation: 'helpdesk.ticket.type',
        string: _t('Type'),
        title: _t('Type'),
    }, {
        name: 'helpdesk_family',
        type: 'many2one',
        relation: 'helpdesk_family',
        string: _t('Familia'),
        title: _t('Familia'),
    }, {
        name: 'partner_id',
        type: 'many2one',
        relation: 'res.partner',
        string: _t('Partner'),
        title: _t('Partner'),
    }],
    successPage: '/your-ticket-has-been-submitted',
});

});
