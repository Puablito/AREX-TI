
//Rango de fechas
$(function() {
            $('#fechaa').daterangepicker({
            showDropdowns: true,
            ranges: {
               'Hoy': [moment(), moment()],
               'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
               'Última Semana': [moment().subtract(6, 'days'), moment()],
               'Últimos 30 días': [moment().subtract(29, 'days'), moment()],
               'Este mes': [moment().startOf('month'), moment().endOf('month')],
               'Mes anterior': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            },
            autoUpdateInput: false,
            opens: 'left',
            applyClass: 'btn-sm btn-primary',
//            autoApply: true,
            cancelClass: 'btn-sm btn-default',
            locale: {
                format: 'DD/MM/YYYY',
                applyLabel: 'Aplicar',
                cancelLabel: 'Limpiar',
                fromLabel: 'Desde',
                toLabel: 'Hasta',
                customRangeLabel: 'Seleccionar rango',
                daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre',
                    'Diciembre'],
                firstDay: 1
            }
        });
        $('#fechaa').on('apply.daterangepicker', function(ev, picker) {
      $(this).val(picker.startDate.format('DD/MM/YYYY') + ' - ' + picker.endDate.format('DD/MM/YYYY'));
          });

          $('#fechaa').on('cancel.daterangepicker', function(ev, picker) {
              $(this).val('');
          });

        });

// Fecha simple
$(function() {
            $('#id_fecha').daterangepicker({
            showDropdowns: true,
            locale: {
                format: 'YYYY-MM-DD',
                daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
                monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre',
                    'Diciembre'],
                firstDay: 1
                },
            singleDatePicker: true,
            autoUpdateInput: true,
            applyClass: 'btn-sm btn-primary',
            autoApply: true,
            cancelClass: 'btn-sm btn-default',

        });
        });

