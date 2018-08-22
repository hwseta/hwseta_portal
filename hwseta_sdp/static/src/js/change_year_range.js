(function() {
var instance = openerp;
var _super = instance.web.DateTimeWidget.prototype.start

instance.web.DateTimeWidget.prototype.start = function(){
    var self = this;
    _super.apply(this, arguments);
    $.datepicker.setDefaults({
        clearText: _t('Clear'),
        clearStatus: _t('Erase the current date'),
        closeText: _t('Done'),
        closeStatus: _t('Close without change'),
        prevText: _t('<Prev'),
        prevStatus: _t('Show the previous month'),
        nextText: _t('Next>'),
        nextStatus: _t('Show the next month'),
        currentText: _t('Today'),
        currentStatus: _t('Show the current month'),
        monthNames: Date.CultureInfo.monthNames,
        monthNamesShort: Date.CultureInfo.abbreviatedMonthNames,
        monthStatus: _t('Show a different month'),
        yearStatus: _t('Show a different year'),
        weekHeader: _t('Wk'),
        weekStatus: _t('Week of the year'),
        dayNames: Date.CultureInfo.dayNames,
        dayNamesShort: Date.CultureInfo.abbreviatedDayNames,
        dayNamesMin: Date.CultureInfo.shortestDayNames,
        dayStatus: _t('Set DD as first week day'),
        dateStatus: _t('Select D, M d'),
        firstDay: Date.CultureInfo.firstDayOfWeek,
        initStatus: _t('Select a date'),
        isRTL: false,
        yearRange: 'c-100:c+10',
    });
}

var _super_session = instance.Session.prototype.rpc

instance.Session.prototype.rpc = function(url, params, options){
	var self = this;
    options = _.clone(options || {});
    var shadow = options.shadow || false;
    delete options.shadow;
    
    return self.check_session_id().then(function() {
        // TODO: remove
        if (! _.isString(url)) {
            _.extend(options, url);
            url = url.url;
        }
        // TODO correct handling of timeouts
        if (! shadow)
            self.trigger('request');
        var fct;
        if (self.origin_server) {
            fct = openerp.jsonRpc;
            if (self.override_session) {
                options.headers = _.extend({}, options.headers, {
                    "X-Openerp-Session-Id": self.override_session ? self.session_id || '' : ''
                });
            }
        } else if (self.use_cors) {
            fct = openerp.jsonRpc;
            url = self.url(url, null);
            options.session_id = self.session_id || '';
            if (self.override_session) {
                options.headers = _.extend({}, options.headers, {
                    "X-Openerp-Session-Id": self.override_session ? self.session_id || '' : ''
                });
            }
        } else {
            fct = openerp.jsonpRpc;
            url = self.url(url, null);
            options.session_id = self.session_id || '';
        }
        var p = fct(url, "call", params, options);
        p = p.then(function (result) {
            if (! shadow)
                self.trigger('response');
            return result;
        }, function(type, error, textStatus, errorThrown) {
            if (type === "server") {
                if (! shadow)
                    self.trigger('response');
                if (error.code === 100) {
                    self.uid = false;
                }
                return $.Deferred().reject(error, $.Event());
            } else {
                if (! shadow)
                    self.trigger('response_failed');
                var nerror = {
                    code: -32098,
                    message: "Kindly check your Network Connection " + errorThrown,
                    data: {type: "xhr"+textStatus, debug: error.responseText, objects: [error, errorThrown] }
                };
                return $.Deferred().reject(nerror, $.Event());
            }
        });
        return p.fail(function() { // Allow deferred user to disable rpc_error call in fail
            p.fail(function(error, event) {
                if (!event.isDefaultPrevented()) {
                    self.trigger('error', error, event);
                }
            });
        });
    });
    
    
}
    
})();



openerp.hwseta_sdp = function(openerp) {
	var _t = openerp.web._t,
	   _lt = openerp.web._lt;
	var instance = openerp;
	var QWeb = instance.web.qweb;
//	var dataset = instance.web.DataSet
	instance.web.list.columns = new instance.web.Registry({
		   'field': 'instance.web.list.Column',
		   'field.boolean': 'instance.web.list.Boolean',
		   'field.binary': 'instance.web.list.Binary',
		   'field.char': 'instance.web.list.Char',
		   'field.progressbar': 'instance.web.list.ProgressBar',
		   'field.handle': 'instance.web.list.Handle',
		   'button': 'instance.web.list.Button',
		   'field.many2one' : 'instance.web.list.Many2One',
		   'field.many2onebutton': 'instance.web.list.Many2OneButton',
		   'field.reference': 'instance.web.list.Reference',
		   'field.many2many': 'instance.web.list.Many2Many'
		});
	instance.web.list.columns.for_ = function (id, field, node) {
	    var description = _.extend({tag: node.tag}, field, node.attrs);
	    var tag = description.tag;
	    var Type = this.get_any([
	        tag + '.' + description.widget,
	        tag + '.'+ description.type,
	        tag
	    ]);
	    return new Type(id, node.tag, description);
	};
	instance.web.list.Many2One = instance.web.list.Column.extend({
		   _format: function (row_data, options) {
		       var text = _t(row_data[this.id].value[1]);
		       var href = '#id=' + row_data[this.id].value[0] + '&view_type=form&model='+ this.relation
		       if (this.relation == 'ir.attachment'){
			       return _.template('<a href="<%-href%>"><%-text%></a>', {
			           text: text,
			           href: href,
			       });
		       }
		       else{
		    	   return this._super(row_data, options);
		       }
		   },
		});
	var _super_mail = instance.mail.Wall.prototype.start;
	instance.mail.Wall.prototype.start = function(){
//			_super_mail.apply(this,arguments);
            this.bind_events();
            var searchview_loaded = this.load_searchview(this.defaults);
            if (! this.searchview.has_defaults) {
                this.message_render();
            }
            // render sidebar
//            var wall_sidebar = new mail.WallSidebar(this);
//            wall_sidebar.appendTo(this.$el.find('.oe_mail_wall_aside'));
        }	
	
	
/*	instance.web.views.add('list', 'instance.web.ListView.inherit');
	instance.web.ListView.inherit = instance.web.ListView.extend( *//** @lends instance.web.ListView# *//* {
	    configure_pager: function (dataset) {
	    	var self = this;
	    	self._super.apply(self, arguments);
	        this.dataset.ids = dataset.ids;
	        // Not exactly clean
	        if (dataset._length) {
	            this.dataset._length = dataset._length;
	        }

	        var total = dataset.size();
	        var limit = this.limit() || total;
	        if (total === 0)
	            this.$pager.hide();
	        else
	            this.$pager.css("display", "");
	        this.$pager.toggleClass('oe_list_pager_single_page', (total <= limit));
	        var spager = '-';
	        if (total) {
	            var range_start = this.page * limit + 1;
	            var range_stop = range_start - 1 + limit;
	            if (this.records.length) {
	                range_stop = range_start - 1 + this.records.length;
	            }
	            if (range_stop > total) {
	                range_stop = total;
	            }
	            spager = _.str.sprintf(_t("No of records %d-%d of %d"), range_start, range_stop, total);
	        }
	        this.$pager.find('.oe_list_pager_state').text(spager);
	    },
	});*/
	
//	 added for load limit data in many2one field
/*	instance.web.views.add('field', 'instance.web.form.CompletionFieldMixin.inherit');
	instance.web.form.CompletionFieldMixin.inherit = instance.web.form.CompletionFieldMixin.extend({
	    get_search_result: function(search_val) {
	        var self = this;

	        var dataset = new instance.web.DataSet(this, this.field.relation, self.build_context());
	        this.last_query = search_val;
	        var exclusion_domain = [], ids_blacklist = this.get_search_blacklist();
	        if (!_(ids_blacklist).isEmpty()) {
	            exclusion_domain.push(['id', 'not in', ids_blacklist]);
	        }

	        return this.orderer.add(dataset.name_search(
	                search_val, new instance.web.CompoundDomain(self.build_domain(), exclusion_domain),
	                'ilike', this.limit + 1, self.build_context())).then(function(data) {
	            self.last_search = data;
	            // possible selections for the m2o
	            var values = _.map(data, function(x) {
	                x[1] = x[1].split("\n")[0];
	                return {
	                    label: _.str.escapeHTML(x[1]),
	                    value: x[1],
	                    name: x[1],
	                    id: x[0],
	                };
	            });

	            // search more... if more results that max
	            if (values.length > self.limit) {
	                values = values.slice(0, self.limit);
	                values.push({
	                    label: _t("Search More..."),
	                    action: function() {
	                        dataset.name_search(search_val, self.build_domain(), 'ilike', 500).done(function(data) {
	                            self._search_create_popup("search", data);
	                        });
	                    },
	                    classname: 'oe_m2o_dropdown_option'
	                });
	            }
	            // quick create
	            var raw_result = _(data.result).map(function(x) {return x[1];});
	            if (search_val.length > 0 && !_.include(raw_result, search_val) &&
	                ! (self.options && (self.options.no_create || self.options.no_quick_create))) {
	                values.push({
	                    label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
	                        $('<span />').text(search_val).html()),
	                    action: function() {
	                        self._quick_create(search_val);
	                    },
	                    classname: 'oe_m2o_dropdown_option'
	                });
	            }
	            // create...
	            if (!(self.options && (self.options.no_create || self.options.no_create_edit))){
	                values.push({
	                    label: _t("Create and Edit..."),
	                    action: function() {
	                        self._search_create_popup("form", undefined, self._create_context(search_val));
	                    },
	                    classname: 'oe_m2o_dropdown_option'
	                });
	            }
	            else if (values.length == 0)
	            	values.push({
	            		label: _t("No results to show..."),
	            		action: function() {},
	            		classname: 'oe_m2o_dropdown_option'
	            	});

	            return values;
	        });
	    },
	 });
*/	
	
}
