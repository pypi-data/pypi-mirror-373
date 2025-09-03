var win = Ext.getCmp('{{ component.client_id }}');
var periodStartField = Ext.getCmp('period_started_at');
var periodEndField = Ext.getCmp('period_ended_at');

Ext.onReady(function() {
    // Инициализация валидаторов
    initializeValidators();
});

function initializeValidators() {
    // Устанавливаем текущую дату и время как максимальное значение
    // и выполняем валидацию каждую секунду
    var validationInterval = setInterval(function() {
        var now = new Date();

        periodStartField.setMaxValue(now);
        periodEndField.setMaxValue(now);

        periodStartField.validate();
        periodEndField.validate();
    }, 1000);

    win.on('destroy', function() {
        clearInterval(validationInterval);
    });

    var periodsValidator = function () {
        if (
            periodStartField.getValue() &&
            periodEndField.getValue() &&
            periodStartField.getValue() > periodEndField.getValue()
        ) {
            return 'Дата конца периода не может быть меньше даты начала периода'
        };

        return true;
    };

    periodStartField.validator = periodsValidator;
    periodEndField.validator = periodsValidator;
}