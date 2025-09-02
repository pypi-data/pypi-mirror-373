/*******************************************************************************

    jQuery and Bootstrap related functions.

*******************************************************************************/

$(function() {

    const createTempusDominusInstance = (elementId, options) => {
        const element = document.getElementById(elementId);
        return new tempusDominus.TempusDominus(element, options);
    };
    const createCommonOptions = (_format, _useSeconds) => {
        return {
            localization: {
                locale: GLOBAL_LOCALE,
                format: _format,
                startOfTheWeek: 1,
                hourCycle: 'h23'
            },
            display: {
                icons: {
                    time: "fas fa-fw fa-clock",
                    date: "fas fa-fw fa-calendar-alt",
                    up: "fas fa-fw fa-arrow-up",
                    down: "fas fa-fw fa-arrow-down",
                    previous: 'fas fa-chevron-left',
                    next: 'fas fa-chevron-right'
                },
                components: {
                    seconds: _useSeconds
                },
                theme: 'light'
            }
        }
    };

    // Initialize date and datetime picker components.
    const commonOptionsSeconds = createCommonOptions('yyyy-MM-dd HH:mm:ss', true);
    if (document.getElementById('datetimepicker-from') && document.getElementById('datetimepicker-to')) {
        const linked_from_1 = createTempusDominusInstance('datetimepicker-from', commonOptionsSeconds);
        const linked_to_1 = createTempusDominusInstance('datetimepicker-to', {
            useCurrent: false,
            ...commonOptionsSeconds
        });
        document.getElementById('datetimepicker-from').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_to_1.updateOptions({
                restrictions: {
                    minDate: e.detail.date,
                },
            });
        });
        document.getElementById('datetimepicker-to').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_from_1.updateOptions({
                restrictions: {
                    maxDate: e.detail.date,
                },
            });
        });
    }
    if (document.getElementById('datetimepicker-from-2') && document.getElementById('datetimepicker-to-2')) {
        const linked_from_2 = createTempusDominusInstance('datetimepicker-from-2', commonOptionsSeconds);
        const linked_to_2 = createTempusDominusInstance('datetimepicker-to-2', {
            useCurrent: false,
            ...commonOptionsSeconds
        });
        document.getElementById('datetimepicker-from-2').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_to_2.updateOptions({
                restrictions: {
                    minDate: e.detail.date,
                },
            });
        });
        document.getElementById('datetimepicker-to-2').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_from_2.updateOptions({
                restrictions: {
                    maxDate: e.detail.date,
                },
            });
        });
    }
    const commonOptions = createCommonOptions('yyyy-MM-dd HH:mm', false);
    if (document.getElementById('datetimepicker-hm-from') && document.getElementById('datetimepicker-hm-to')) {
        const linked_from = createTempusDominusInstance('datetimepicker-hm-from', commonOptions);
        const linked_to = createTempusDominusInstance('datetimepicker-hm-to', {
            useCurrent: false,
            ...commonOptions
        });
        document.getElementById('datetimepicker-hm-from').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_to.updateOptions({
                restrictions: {
                    minDate: e.detail.date,
                },
            });
        });
        document.getElementById('datetimepicker-hm-to').addEventListener(tempusDominus.Namespace.events.change, (e) => {
            linked_from.updateOptions({
                restrictions: {
                    maxDate: e.detail.date,
                },
            });
        });
    }

    // Initialize select pickers.
    [...document.getElementsByClassName('selectpicker')].forEach(sp => {
        const plugins = ['dropdown_input'];
        if (sp.multiple || !sp.required) {
            plugins.push('remove_button');
        }

        const empty_option_value = sp.querySelector('option[value="__None"]') ? '__None' : '';

        const select = new TomSelect(sp, {
            plugins: plugins,
            maxOptions: null,
            onDelete: () => sp.multiple || !sp.required, // Disable removing options on backspace if the required value is set
            emptyOptionValue: empty_option_value,
            placeholder: sp.getAttribute('data-none-selected-text'),
            hidePlaceholder: true,
        });
        sp.selectpicker = select;
    });

    // Initialize tooltips.
    new bootstrap.Tooltip('#inner-body-1', {
        selector: '[data-bs-toggle=tooltip]',
        container: 'body'
    });

    // Tooltips for navbar tabs require special handling.
    // (I don't think tooltips on tabs have ever worked, and they cause errors in
    // Bootstrap v5, but I'm leaving it here just in case it gets resolved later)
    // [...document.querySelectorAll('.nav-tabs-tooltipped')].forEach(e => new bootstrap.Tooltip(e, {
    //     selector: '[data-bs-toggle=tab]',
    //     trigger: 'hover',
    //     placement: 'top',
    //     animation: true,
    //     container: 'body'
    // }));


    // Initialize popovers.
    new bootstrap.Popover('#inner-body-2', {
        selector: "[data-bs-toggle=popover]"
    })

    // Custom popovers implemented using @popperjs/core library. The Bootstrap variant
    // does not support some advanced features.
    $('.popover-hover-container').on("mouseenter", ".popover-hover", function() {
        var ref = $(this);
        var popup = $($(this).attr("data-popover-content"));
        popup.addClass("static-popover");
        popup.removeClass("d-none");
        var popper = Popper.createPopper(ref[0], popup[0], {
            placement: 'top',
            onFirstUpdate: function(data) {
                popup.find('.popover').removeClass('top');
                popup.find('.popover').removeClass('bottom');
                popup.find('.popover').addClass(data.placement);
                popper.update();
            },
            modifiers: [
                {
                    name: 'flip',
                    options: {
                        fallbackPlacements: ['top', 'bottom']
                    }
                },
                {
                    name: 'offset',
                    options: {
                      offset: [0, 8],
                    },
                }
            ]
        });
        ref.data('popper-instance', popper);
    });
    $('.popover-hover-container').on("mouseleave", ".popover-hover", function() {
        var ref = $(this);
        var popup = $($(this).attr("data-popover-content"));
        popup.addClass("d-none");
        popup.removeClass("static-popover")
        var popper = ref.data('popper-instance');
        if (popper) {
            popper.destroy();
            ref.data('popper-instance', null);
        }
    });

    // Initialize Monaco Editor (only if container is present)
    const monacoFormItems = [...document.getElementsByClassName('expression-input-block')];
    monacoFormItems.forEach(formItem => {
        window.require.config({ paths: { 'vs': `${window.STATIC_BASE_URL}vendor/monaco-editor/vs` } });

        window.require(['vs/editor/editor.main'], function () {
            window.registerRansack(monaco);
            const monacoContainer = formItem.querySelector('.monaco-container');
            const monacoHiddenInput = formItem.querySelector('.monaco-hidden-input');
            const editor = monaco.editor.create(monacoContainer, {
                value: monacoHiddenInput.value || '',
                language: 'ransack',
                automaticLayout: true,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
            });

            // Update hidden textarea on form submit
            const form = formItem.closest('form');
            if (form) {
                form.addEventListener('click', function () {
                    if (monacoHiddenInput) {
                        monacoHiddenInput.value = editor.getValue();
                    }
                }, true); // useCapture = true
            }

            const errorMeta = formItem.querySelector('.monaco-error-meta .monaco-error-marker');
            if (errorMeta) {
                const startLineNumber = parseInt(errorMeta.dataset.line);
                const startColumn = parseInt(errorMeta.dataset.column);
                const endLineNumber = parseInt(errorMeta.dataset.endLine);
                const endColumn = parseInt(errorMeta.dataset.endColumn);
                const message = errorMeta.dataset.message || 'Parse error';

                // Add marker to Monaco
                monaco.editor.setModelMarkers(editor.getModel(), 'filter-validator', [
                    {
                        severity: monaco.MarkerSeverity.Error,
                        message: message,
                        startLineNumber,
                        startColumn,
                        endLineNumber,
                        endColumn
                    }
                ]);
            }

            // Clear error markers on any change
            editor.onDidChangeModelContent(() => {
                monaco.editor.setModelMarkers(editor.getModel(), 'filter-validator', []);
            });

            // Autocompletion
            monaco.languages.registerCompletionItemProvider('ransack', {
                provideCompletionItems: () => {
                  const fields = [
                    'Format',
                    'ID',
                    'AltNames',
                    'CorrelID',
                    'AggrID',
                    'PredID',
                    'RelID',
                    'CreateTime',
                    'DetectTime',
                    'EventTime',
                    'CeaseTime',
                    'WinStartTime',
                    'WinEndTime',
                    'ConnCount',
                    'FlowCount',
                    'PacketCount',
                    'ByteCount',
                    'Category',
                    'Ref',
                    'Confidence',
                    'Description',
                    'Note',
                    'Source.Type',
                    'Source.Hostname',
                    'Source.IP4',
                    'Source.MAC',
                    'Source.IP6',
                    'Source.Port',
                    'Source.Proto',
                    'Source.URL',
                    'Source.Email',
                    'Source.AttachHand',
                    'Source.Note',
                    'Source.Spoofed',
                    'Source.Imprecise',
                    'Source.Anonymised',
                    'Source.ASN',
                    'Source.Router',
                    'Source.Netname',
                    'Source.Ref',
                    'Target.Type',
                    'Target.Hostname',
                    'Target.IP4',
                    'Target.MAC',
                    'Target.IP6',
                    'Target.Port',
                    'Target.Proto',
                    'Target.URL',
                    'Target.Email',
                    'Target.AttachHand',
                    'Target.Note',
                    'Target.Spoofed',
                    'Target.Imprecise',
                    'Target.Anonymised',
                    'Target.ASN',
                    'Target.Router',
                    'Target.Netname',
                    'Target.Ref',
                    'Attach.Handle',
                    'Attach.FileName',
                    'Attach.Type',
                    'Attach.Hash',
                    'Attach.Size',
                    'Attach.Ref',
                    'Attach.Note',
                    'Attach.ContentType',
                    'Attach.ContentCharset',
                    'Attach.ContentEncoding',
                    'Attach.Content',
                    'Attach.ContentID',
                    'Attach.ExternalURI',
                    'Node.Name',
                    'Node.Type',
                    'Node.SW',
                    'Node.AggrWin',
                    'Node.Note',
                    '_Mentat.EventClass',
                    '_Mentat.EventSeverity',
                    '_Mentat.ResolvedAbuses',
                    '_Mentat.TargetClass',
                    '_Mentat.TargetSeverity',
                    '_Mentat.TargetAbuses',
                    '_Mentat.StorageTime',
                  ];

                  const suggestions = [];

                  fields.forEach(field => {
                    suggestions.push({
                      label: field,
                      kind: monaco.languages.CompletionItemKind.Field,
                      insertText: field
                    });
                  });

                  return { suggestions };
                }
            });
        });
    });


    // Special handling of '__EMPTY__' and '__ANY__' options in event search form
    // selects. This method stil can be improved, so that 'any' is capable of disabling
    // 'empty'.
    //$(".esf-any-empty").on("changed.bs.select", function(e, clickedIndex, newValue, oldValue) {
    //    var selected = $(e.currentTarget).val();
    //    // The empty option is mutually exclusive with everything else and has
    //    // top priority.
    //    if (selected.indexOf('__EMPTY__') != -1) {
    //        console.log('Empty selected');
    //        $(e.currentTarget).selectpicker('deselectAll');
    //        $(e.currentTarget).selectpicker('refresh');
    //        $(e.currentTarget).val('__EMPTY__');
    //        $(e.currentTarget).selectpicker('refresh');
    //    }
    //    // The any option is mutually exclusive with everything else.
    //    else if (selected.indexOf('__ANY__') != -1) {
    //        console.log('Any selected');
    //        $(e.currentTarget).selectpicker('deselectAll');
    //        $(e.currentTarget).selectpicker('refresh');
    //        $(e.currentTarget).val('__ANY__');
    //        $(e.currentTarget).selectpicker('refresh');
    //    }
    //    console.log(e, this, 'VAL', this.value, 'SEL', selected, 'CI', clickedIndex, 'NV', newValue, 'OV', oldValue);
    //});
});
