openerp.hwseta_button_suppress = function(instance) {
	'use strict';
	instance.point_of_sale = {};

	var module = instance.button_supress;

	new instance.web.Model("res.users").call("check_user_group", []).then(function(res) {
		self.check_user = res;
		instance.web.Sidebar = instance.web.Sidebar.extend({
			
		    init: function(parent) {
		        var self = this;
		        this._super(parent);
		        var form = new instance.web.ActionManager(self);
				if (form.__parentedParent.__parentedParent.model == 'hr.employee') {
					self.check_user_group = res;
					self.form_name = 'sdf';
				}
				if (form.__parentedParent.__parentedParent.model == 'wsp.plan') {
					self.check_user_group = res;
					self.form_name = 'wsp';
				}
				if (form.__parentedParent.__parentedParent.model == 'res.partner') {
					self.check_user_group = res;
					self.form_name = 'employer';
				}
		    },			
			
		});
	});
};
