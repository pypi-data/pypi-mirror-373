function onObjGridAction(grid, actionUrl) {
    assert(grid, 'grid is not define');
    assert(actionUrl, 'actionUrl is not define');
    var mask = new Ext.LoadMask(grid.body),
        params = grid.getMainContext();
    params[grid.rowIdName] = '';
    params = Ext.apply(params, getGridParams(grid));

    grid.getStore()

    var req = {
        url: actionUrl,
        params: params,
        success: function(res, opt){
            if (scope.fireEvent('afternewrequest', scope, res, opt)) {
                try {
                    var child_win = scope.onNewRecordWindowOpenHandler(res, opt);
                } finally {
                    mask.hide();
                }
                return child_win;
            }
            mask.hide();
        }
       ,failure: function(){
           uiAjaxFailMessage.apply(this, arguments);
           mask.hide();

       }
    };

    if (grid.fireEvent('beforenewrequest', grid, req)) {
        var scope = grid;

        mask.show();
        Ext.Ajax.request(req);
    }
}

function onObjGridOneRecordAction(grid, actionName, actionUrl) {
    assert(grid, 'grid is not define');
    assert(actionName, 'actionName is not define');
    assert(actionUrl, 'actionUrl is not define');
    assert(grid.rowIdName, 'rowIdName is not define');

    if (grid.getSelectionModel().hasSelection()) {
        // при локальном редактировании запросим также текущую строку
        var baseConf = grid.getSelectionContext(grid.localEdit);
        // грязный хак
        if (String(baseConf[grid.rowIdName]).indexOf(",") != -1) {
            Ext.Msg.show({
                title: actionName,
                msg: 'Для выполнения действия должен быть выбран только один элемент.',
                buttons: Ext.Msg.OK,
                icon: Ext.MessageBox.INFO
                });
        } else {
            var mask = new Ext.LoadMask(grid.body);
            var req = {
                url: actionUrl,
                params: baseConf,
                success: function(res, opt){
                    if (scope.fireEvent('aftereditrequest', scope, res, opt)) {
                        try {
                            var child_win = scope.onEditRecordWindowOpenHandler(res, opt);
                        } finally {
                            mask.hide();
                        }
                        return child_win;
                    }
                    mask.hide();
                }
               ,failure: function(){
                   uiAjaxFailMessage.apply(this, arguments);
                   mask.hide();
               }
            };

            if (grid.fireEvent('beforeeditrequest', grid, req)) {
                var scope = grid;

                mask.show();
                Ext.Ajax.request(req);
            }
        }
    } else {
    Ext.Msg.show({
        title: actionName,
        msg: 'Элемент не выбран',
        buttons: Ext.Msg.OK,
        icon: Ext.MessageBox.INFO
        });
    }
}

function onObjGridMultiRecordAction(
    grid, actionName, actionUrl, isConfirmRequired
) {
    assert(grid, 'grid is not define');
    assert(actionName, 'actionName is not define');
    assert(actionUrl, 'actionUrl is not define');
    assert(grid.rowIdName, 'rowIdName is not define');

    var scope = grid;
    if (scope.getSelectionModel().hasSelection()) {
        var request = function(btn, text, opt){
            if (btn === 'yes') {
                var baseConf = scope.getSelectionContext(scope.localEdit);
                var mask = new Ext.LoadMask(scope.body);
                var req = {
                   url: actionUrl,
                   params: baseConf,
                   success: function(res, opt){
                       if (scope.fireEvent('afterdeleterequest', scope, res, opt)) {
                           try {
                               var child_win =  scope.deleteOkHandler(res, opt);
                           } finally {
                               mask.hide();
                           }
                           return child_win;
                       }
                       mask.hide();
                   }
                   ,failure: function(){
                       uiAjaxFailMessage.apply(this, arguments);
                       mask.hide();
                   }
                };
                if (scope.fireEvent('beforedeleterequest', scope, req)) {

                    mask.show();
                    Ext.Ajax.request(req);
                }
            }
        }
        if (isConfirmRequired) {
            Ext.Msg.show({
                title: actionName,
                msg: 'Вы действительно хотите выполнить '
                    + actionName + 'для выбранной записи?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                fn: request
            });
        }
        else {
            request('yes');
        }
    } else {
        Ext.Msg.show({
            title: actionName,
            msg: 'Элемент не выбран',
            buttons: Ext.Msg.OK,
            icon: Ext.MessageBox.INFO
        });
    }
}

function getGridParams(grid) {
    var options = {};
    if (grid.allowPaging) {
        var pagingBar = grid.getBottomToolbar();
        if(pagingBar &&  pagingBar instanceof Ext.PagingToolbar){
            var o = {}, pp = pagingBar.getParams();
            o[pp.start] = (
                (Math.ceil((
                    pagingBar.cursor + pagingBar.pageSize
                ) / pagingBar.pageSize) - 1) * pagingBar.pageSize
            ).constrain(0, pagingBar.store.getTotalCount());
            o[pp.limit] = pagingBar.pageSize;
            options = Ext.apply(options, o);
        }
    }

    var store = grid.getStore();
    options = Ext.apply(options, store.baseParams);

    if (store.sortInfo && store.remoteSort) {
        var sp = store.paramNames;
        options[sp.sort] = store.sortInfo.field;
        options[sp.dir] = store.sortInfo.direction;
    }

    return options;
}
