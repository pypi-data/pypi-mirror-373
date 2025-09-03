var grid = Ext.getCmp('{{component.grid.client_id}}');

function changeExport(bool_value){
    var selections = grid.selModel.getSelections();
    var selections_len = selections.length;

    if (selections_len){
        var selected_ids = [];
        for (var i = 0; i < selections_len; i += 1) {
            selected_ids.push(selections[i].id);
        }
        var params =  {'export_enabled': bool_value};
        params['ids'] = selected_ids.join(',');
        Ext.Ajax.request({
            url: '{{component.export_change_action_url}}',
            method: 'POST',
            params: params,
            success: function(res, opt){
                if (Ext.util.JSON.decode(res.responseText).success) {
                   grid.refreshStore();
                }
                smart_eval(res.responseText);
        },
            failure: Ext.emptyFn
        });
    } else {
         Ext.Msg.alert('Внимание!', 'Выберите Сущность для выключения экспорта!');
    }
}

function offExport(){
    changeExport(false)
}

function onExport(){
    changeExport(true)
}
