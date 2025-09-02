/*

    Global JS application module for Hawat - The web interface for Mentat system.

*/
var Hawat = (function () {

    /*
        Get given icon as HTML snippet.

        @param {string} name - Name of the icon.
    */
    function _get_icon(name) {
        try {
            return _icons[name];
        }
        catch(err) {
            return _icons['missing-icon'];
        }
    }

    /*
        Append given flash message element to appropriate flash message container
        element.

        @param {element} message_element - Element containing new flash message.
    */
    function _append_flash_message(message_element) {
        $(".container-flashed-messages").append(message_element);
    }

    /*
        Generate and append new flash message.
    */
    function _flash_message(category, message) {
        var msg_elem = document.createElement('div');
        $(msg_elem).addClass("alert alert-" + category + " alert-dismissible");
        $(msg_elem).append('<button type="button" class="btn-close" data-bs-dismiss="alert"></button>');
        $(msg_elem).append(document.createTextNode(message));
        _append_flash_message(message_element);
    }

    function _append_result_flash_messages(result_data) {
        if (!result_data.snippets || !result_data.snippets.flash_messages) {
            return;
        }
        for (const category in result_data.snippets.flash_messages) {
            if (result_data.snippets.flash_messages.hasOwnProperty(category)) {
                result_data.snippets.flash_messages[category].forEach(function(snippet) {
                    _append_flash_message(snippet);
                });
            }
        }
    }

    /*
        Internal function for building URL parameters.
    */
    function _build_param_builder(skeleton, rules, kwrules) {
        //var _skeleton = Object.assign({}, skeleton);
        var _skeleton = skeleton;
        var _rules    = rules;
        var _kwrules  = kwrules;
        return function(args, kwargs = null) {
            //var _result = Object.assign({}, _skeleton);
            var _result = _skeleton;
            if (!Array.isArray(args)) {
                args = [args];
            }
            _rules.forEach(function(r, i) {
                try {
                    _result[r[0]] = args[i];
                }
                catch(err) {
                    if (!r[3]) {
                        throw "Missing mandatory URL builder argument '" + i + "'";
                    }
                }
            });
            _kwrules.forEach(function(r) {
                value = kwargs[r[0]];
                if (value != null) {
                    _result[r[0]] = value;
                } else if (!r[3]) {
                    throw "Missing mandatory URL builder argument '" + r[0] + "'";
                }
            });
            return _result;
        }
    }

    function _oads_setup_placeholder(parent_elem, oads_item) {
        // Append placeholder element for OADS query result and populate it with
        // AJAX spinner.
        $(parent_elem).append(
            '<div class="query-result '
            + oads_item.ident
            + '"><i class="fas fa-fw fa-cog fa-spin" data-bs-toggle="tooltip" title="{{ _("Fetching additional object data from service") }}: '
            + oads_item.ident.toUpperCase()
            + '"></i></div>'
        );
        // Return reference for recently created element for OADS query result.
        return $(parent_elem).children('.query-result.' + oads_item.ident);
    }

    function _oads_result_success(result_data, result_elem, oads_item, cfg) {
        console.debug("OADS result for " + oads_item.ident + " query for: " + cfg.objectName);
        console.debug(result_data);
        // There might be some tooltips displayed, so first get rid of them
        // and of all temporary content.
        $(result_elem).children().tooltip('dispose');
        $(result_elem).empty();
        // Populate the element with result snippets.
        oads_item.snippets.forEach(function(snippet) {
            $(result_elem).append(result_data.snippets[snippet['name']]);
        });
        // Display all flash messages, if any.
        if (cfg.renderFlash) {
            _append_result_flash_messages(result_data);
        }
    }

    function _oads_result_empty(result_data, result_elem, oads_item, cfg) {
        console.debug("OADS empty result for " + oads_item.ident + " query for: " + cfg.objectName);
        console.debug(result_data);
        // Either insert information about empty query result.
        if (cfg.renderEmpty) {
            $(result_elem).html(
                '<i class="fas fa-fw fa-minus" data-bs-toggle="tooltip" title="{{ _("Empty result for") }} '
                + oads_item.ident.toUpperCase()
                + '{{ _(" query for ") }}&quot;'
                + cfg.objectName
                + '&quot;"></i>'
            );
        }
        // Or remove the result element to reduce display clutter.
        else {
            $(result_elem).children().tooltip('dispose');
            $(result_elem).remove();
        }
        // Display all flash messages, if any.
        if (cfg.renderFlash) {
            _append_result_flash_messages(result_data);
        }
    }

    function _oads_result_error(result_data, result_elem, oads_item, cfg) {
        console.log("OADS failure " + oads_item.ident + " query for: " + cfg.objectName);
        console.debug(result_data);
        // Either insert information about error query result.
        if (cfg.renderError) {
            $(result_elem).html(
                '<i class="fas fa-fw fa-times" data-bs-toggle="tooltip" title="{{ _("Error result for") }} '
                + oads_item.ident.toUpperCase()
                + '{{ _(" query for ") }}&quot;'
                + cfg.objectName
                + '&quot;"></i>'
            );
        }
        // Or remove the result element to reduce display clutter.
        else {
            $(result_elem).children().tooltip('dispose');
            $(result_elem).remove();
        }
        // Display all flash messages, if any.
        if (cfg.renderFlash) {
            _append_result_flash_messages(result_data);
        }
    }

    function _get_oad(oads_item, elem) {
        var cfg = $(elem).data();
        var url = Flask.url_for(
            oads_item.endpoint,
            oads_item.params([cfg.objectName], {render: cfg.renderType})
        )

        // Setup placeholder element for OADS query result.
        elem = _oads_setup_placeholder(elem, oads_item);

        // Perform asynchronous request.
        console.debug(
            "OADS request URL" + url + ", snippets: [" + oads_item.snippets.join(', ') + "]"
        );
        var jqxhr = $.get(url)
        .done(function(data) {
            if (data.search_result && ((Array.isArray(data.search_result) && data.search_result.length > 0) || !Array.isArray(data.search_result))) {
                _oads_result_success(data, elem, oads_item, cfg);
            }
            else {
                _oads_result_empty(data, elem, oads_item, cfg);
            }
        })
        .fail(function(data) {
            _oads_result_error(data, elem, oads_item, cfg);
        })
        .always(function() {
            //console.log("Finished " + oads_item.ident + " query for: " + cfg.objectName);
        });
    }

    /**
        Hawat application configurations.
    */
    var _configs = {
        'APPLICATION_ROOT': '{{ hawat_current_app.config['APPLICATION_ROOT'] }}'
    };

    /**
        Hawat application icon set.
    */
    var _icons = {{ hawat_current_app.icons | tojson | safe }};

    /**
        Data structure containing registrations of object additional data services
        for particular object types.
    */
    var _oads = {
{%- for oads_name in hawat_current_app.oads.keys() | sort %}
        '{{ oads_name }}': [
    {%- for oads in hawat_current_app.oads[oads_name] %}
        {%- if 'view' in oads %}
            {
                'endpoint': '{{ oads.view.get_view_endpoint() }}',
                'ident':    '{{ oads.view.module_name | upper }}',
                'snippets': {{ oads.view.snippets | tojson | safe }},
                'params':   _build_param_builder(
                    {{ oads.params.skeleton | tojson | safe }},
                    {{ oads.params.rules | tojson | safe }},
                    {{ oads.params.kwrules | tojson | safe }}
                )
            }{%- if not loop.last %},{%- endif %}
        {%- endif %}
    {%- endfor %}
        ]{%- if not loop.last %},{%- endif %}
{%- endfor %}
    };

    return {
        /*
            Generate and append new flash message to main flash message container.
        */
        flash_message: function(category, message) {
            _flash_message(category, message);
        },

        get_icon: function(name) {
            return _get_icon(name);
        },

        /**
            Get data structure containing lists of all registered additional object
            data services (OADS) for all types of objects.
        */
        get_all_oadss: function() {
            return _oads;
        },

        /**
            Get list of all registered object additional data services (OADS) for
            given object type.

            @param {string} name - Name of the object type and OADS category
        */
        get_oads: function(name) {
            try {
                return _oads[name];
            }
            catch (err) {
                console.error("Invalid OADS type: " + name);
                return [];
            }
        },

        /**
            Connect to and fetch data from all object additional data services
            registered for given object. First function argument is unused and
            ignored. The 'elem' argument must be a HTML element with CSS class
            'object-additional-data' and following HTML data attributes:

            string object-type: Type of the object in question ('ip4', 'ip6', ...)
            string object-name: Object in question (address, hostname, ...)
            string render-type: Requested result rendering ('label', 'full')
        */
        fetch_oads: function(index, elem) {
            var obj_type = $(elem).data('object-type');  // Type of the object ('ip4', 'ip6', 'hostname', ...)
            var obj_name = $(elem).data('object-name');  // Name of the object (IP address, hostname, ...)
            var oads     = Hawat.get_oads(obj_type);     // List of OADS registered for given object type.

            console.debug(
                "Retrieving OADS for '"
                + obj_type
                + " -- "
                + obj_name
                + "': "
                + oads.reduce(function(sum, item) {
                    return sum + ', ' + item.endpoint
                }, '')
            );
            console.debug(oads);
            oads.forEach(function(oads_item) {
                _get_oad(oads_item, elem);
            });
        }
    };
})();

$(function() {
    $(".object-additional-data.onload").each(Hawat.fetch_oads);
    $(".object-additional-data-block.onload").each(Hawat.fetch_oads);
    $('.object-additional-data.ondemand').on("click", function() {
        var ref = $(this);
        ref.children().tooltip('dispose');
        ref.removeClass('ondemand');
        ref.empty();
        ref.off('click');
        Hawat.fetch_oads(0, ref);
    });
});

$(function(){
  var hash = window.location.hash;
  if (hash) {
      var innerTab = $('ul.nav a[href="' + hash + '"]');
      if (innerTab.length) {
          // Show the parent tab pane if needed
          var parentTabPane = innerTab.closest('.tab-pane');
          if (parentTabPane.length) {
              var parentTabId = parentTabPane.attr('id');
              $('ul.nav a[href="#' + parentTabId + '"]').tab('show');
          }
          // Show the inner tab
          innerTab.tab('show');
      }
  }
});

// Push tab links to URL.
$(function(){
    $('a[data-bs-toggle="tab"]').on('show.bs.tab', function (e) {
        const hash = e.target.getAttribute('href');
        if (hash) {
            window.history.replaceState(null, null, hash);
        }
    });
});
