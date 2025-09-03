function startTask(){
    var grid = Ext.getCmp('{{ component.grid.client_id }}'),
        selections = grid.selModel.getSelections(),
        commands = [];

    if (Ext.isEmpty(selections)) {
        Ext.Msg.alert('Внимание', 'Не выбрана команда!');
        return false;
    } else {
        Ext.each(selections, function (obj) {
            commands.push(obj.id);
        });
    }

    Ext.Ajax.request({
        url: '{{ component.queue_select_win_url }}',
        method: 'POST',
        params: {},
        success: function (res) {
            var queue_select_win = smart_eval(res.responseText);
            queue_select_win.on('closed_ok', function() {
                 var queue_level_field = queue_select_win.items.items[0];
                 var params = queue_select_win.actionContextJson;
                 params['commands'] = commands.join();
                 params['queue_level'] = queue_level_field.getValue();
                 Ext.Ajax.request({
                     url: '{{ component.start_task_url }}',
                     method: 'POST',
                     params: params,
                     success: function (res) {
                         smart_eval(res.responseText);
                         grid.getStore().reload();
                         },
                     failure: uiAjaxFailMessage
                 });
                 queue_select_win.close();

            });
        },
        failure: uiAjaxFailMessage
    });
}
