function stageForExport(){
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
        url: '{{ component.sub_stage_for_export_url }}',
        method: 'POST',
        params: {'commands': commands.join()},
        success: function (res) {
            smart_eval(res.responseText);
            grid.getStore().reload();
        },
        failure: uiAjaxFailMessage
    });
}
