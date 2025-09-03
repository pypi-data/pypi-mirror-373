// Валидатор для поля institute_ids
var instituteIdsValidator = function () {
    var value = this.getValue();
    
    // Если поле пустое - это допустимо
    if (!value || value.trim() === '') {
        this.clearInvalid();
        return true;
    }

    value = value.trim();

    if (!/^[0-9,]+$/.test(value)) {
        this.markInvalid('Разрешены только цифры и запятые');
        return false;
    }

    var numbers = value.split(',');

    for (var i = 0; i < numbers.length; i++) {
        if (numbers[i].trim() === '') {
            this.markInvalid('Между запятыми не должно быть пустых значений');
            return false;
        }
    }

    var uniqueNumbers = [];
    for (var j = 0; j < numbers.length; j++) {
        var num = parseInt(numbers[j].trim());
        if (uniqueNumbers.indexOf(num) !== -1) {
            this.markInvalid('ID организаций не должны повторяться');
            return false;
        }
        uniqueNumbers.push(num);
    }
    
    this.clearInvalid();
    return true;
};

// Валидатор для поля institute_count - запрещаем 0
var instituteCountValidator = function() {
    var value = this.getValue();
    if (value === 0) {
        this.markInvalid('Количество организаций не может быть равно 0');
        return false;
    }
    
    this.clearInvalid();
    return true;
};

var logsPeriodStartField = Ext.getCmp('logs_period_started_at');
var logsPeriodEndField = Ext.getCmp('logs_period_ended_at');

var logsPeriodsValidator = function () {
    if (
        logsPeriodStartField.getValue() &&
        logsPeriodEndField.getValue() &&
        logsPeriodStartField.getValue() > logsPeriodEndField.getValue()
    ) {
        return 'Дата конца периода не может быть меньше даты начала периода'
    };

    return true;
};