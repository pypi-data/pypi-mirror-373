{% load educommon %}
{% include "ui-js/validators.js" %}

var win = Ext.getCmp('{{ component.client_id }}');

Ext.onReady(function() {
    // Инициализация валидаторов
    initializeValidators();

    // Инициализация взаимозависимых полей
    initializeBatchSizeSplitByLogic();
});

function initializeValidators() {
    // Валидатор для institute_ids
    var instituteIdsField = Ext.getCmp('institute_ids');
    if (instituteIdsField) {
        instituteIdsField.validate = instituteIdsValidator;
        instituteIdsField.on('blur', function() {
            this.validate();
        });
    }

    // Валидатор для institute_count
    var instituteCountField = Ext.getCmp('institute_count');
    if (instituteCountField) {
        var originalValidator = instituteCountField.validate;

        instituteCountField.validate = function() {
            if (!instituteCountValidator.call(this)) {
                return false;
            }
            if (originalValidator) {
                return originalValidator.call(this);
            }
            return true;
        };

        instituteCountField.on('blur', function() {
            this.validate();
        });
    }

    // Устанавливаем текущую дату и время как максимальное значение
    // и выполняем валидацию каждую секунду
    var validationInterval = setInterval(function() {
        var now = new Date();

        logsPeriodStartField.setMaxValue(now);
        logsPeriodEndField.setMaxValue(now);

        logsPeriodStartField.validate();
        logsPeriodEndField.validate();
    }, 1000);

    win.on('destroy', function() {
        clearInterval(validationInterval);
    });

    logsPeriodStartField.validator = logsPeriodsValidator;
    logsPeriodEndField.validator = logsPeriodsValidator;
}

function initializeBatchSizeSplitByLogic() {
    var batchSizeField = Ext.getCmp('batch_size');
    var splitByField = Ext.getCmp('split_by');

    if (!batchSizeField || !splitByField) {
        return;
    }

    // Функция для обновления обязательности полей
    function updateFieldRequirements() {
        var batchSizeValue = batchSizeField.getValue();
        var splitByValue = splitByField.getValue();

        if (splitByValue && splitByValue !== '') {
            batchSizeField.allowBlank = true;
            batchSizeField.clearInvalid();
        } else {
            batchSizeField.allowBlank = false;
        }

        if (batchSizeValue && batchSizeValue !== '' && batchSizeValue !== 0) {
            splitByField.allowBlank = true;
            splitByField.clearInvalid();
        } else {
            splitByField.allowBlank = false;
        }
    }

    // Обработчики изменения полей
    batchSizeField.on('change', updateFieldRequirements);
    splitByField.on('change', updateFieldRequirements);

    // Инициализация при загрузке
    updateFieldRequirements();
}