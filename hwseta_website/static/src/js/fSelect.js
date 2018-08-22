(function($) {

	
	function tset(){
		alert("in select js")
	}
	
    $.fn.fSelect = function(options) {

        if (typeof options == 'string' ) {
            var settings = options;
        }
        else {
            var settings = $.extend({
                placeholder: 'Select some option(s)',
                numDisplayed: 3,
                overflowText: '{n} selected',
                searchText: 'Search',
                showSearch: true
            }, options);
        }


        /**
         * Constructor
         */
        function fSelect(select, settings) {
            this.$select = $(select);
            this.settings = settings;
            this.create();
        }


        /**
         * Prototype class
         */
        fSelect.prototype = {
            create: function() {
                var multiple = this.$select.is('[multiple]') ? ' multiple' : '';
                this.$select.wrap('<div class="fs-wrap' + multiple + '"></div>');
                this.$select.before('<div class="fs-label-wrap"><div class="fs-label">' + this.settings.placeholder + '</div><span class="fs-arrow"></span></div>');
                this.$select.before('<div class="fs-dropdown hidden"><div class="fs-options"></div><a id="load_more" class="load_more">Load more... </a></div>');
                this.$select.addClass('hidden');
                this.$wrap = this.$select.closest('.fs-wrap');
                this.reload();
            },

            reload: function() {
                if (this.settings.showSearch) {
                    var search = '<div class="fs-search"><input type="search" placeholder="' + this.settings.searchText + '" /></div>';
                    this.$wrap.find('.fs-dropdown').prepend(search);
                }
                var choices = this.buildOptions(this.$select);
                this.$wrap.find('.fs-options').html(choices);
                this.reloadDropdownLabel();
            },

            destroy: function() {
                this.$wrap.find('.fs-label-wrap').remove();
                this.$wrap.find('.fs-dropdown').remove();
                this.$select.unwrap().removeClass('hidden');
            },

            buildOptions: function($element) {
                var $this = this;

                var choices = '';
                $element.children().each(function(i, el) {
                    var $el = $(el);

                    if ('optgroup' == $el.prop('nodeName').toLowerCase()) {
                        choices += '<div class="fs-optgroup">';
                        choices += '<div class="fs-optgroup-label">' + $el.prop('label') + '</div>';
                        choices += $this.buildOptions($el);
                        choices += '</div>';
                    }
                    else {
                        var selected = $el.is('[selected]') ? ' selected' : '';
                        choices += '<div class="fs-option' + selected + '" data-value="' + $el.prop('value') + '"><span class="fs-checkbox"><i></i></span><div class="fs-option-label">' + $el.html().split(',')[0] + '<p class="hidden">'+$el.html().split(',')[1]+'</p></div></div>';
                    }
                });
                $(".fs-wrap .multiple").remove();
                return choices;
            },

            reloadDropdownLabel: function() {
                var labelText = '';
                var counter=0
                this.$wrap.find('.fs-option.selected').each(function(i, el) {
                	counter++
                    labelText='You have Selected '+counter+' Option(s)'
                });

                if (counter < 1) {
                    labelText = settings.placeholder;
                }
                else if (counter > settings.numDisplayed) {
                    labelText = settings.overflowText.replace('{n}', counter);
                }
                else {
                    labelText = 'You have Selected '+counter+' Option(s)'
                }

                this.$wrap.find('.fs-label').html(labelText);
                this.$select.change();
            }
        }


        /**
         * Loop through each matching element
         */
        return this.each(function() {
            var data = $(this).data('fSelect');

            if (!data) {
                data = new fSelect(this, settings);
                $(this).data('fSelect', data);
            }

            if (typeof settings == 'string') {
                data[settings]();
            }
        });
    }


    /**
     * Events
     */
    window.fSelect = {
        'active': null,
        'idx': -1
    };

    function setIndexes($wrap) {
        $wrap.find('.fs-option:not(.hidden)').each(function(i, el) {
            $(el).attr('data-index', i);
            $wrap.find('.fs-option').removeClass('hl');
        });
        $wrap.find('.fs-search input').focus();
        window.fSelect.idx = -1;
    }

    function setScroll($wrap) {
        var $container = $wrap.find('.fs-options');
        var $selected = $wrap.find('.fs-option.hl');

        var itemMin = $selected.offset().top + $container.scrollTop();
        var itemMax = itemMin + $selected.outerHeight();
        var containerMin = $container.offset().top + $container.scrollTop();
        var containerMax = containerMin + $container.outerHeight();

        if (itemMax > containerMax) { // scroll down
            var to = $container.scrollTop() + itemMax - containerMax;
            $container.scrollTop(to);
        }
        else if (itemMin < containerMin) { // scroll up
            var to = $container.scrollTop() - containerMin - itemMin;
            $container.scrollTop(to);
        }
    }

    $(document).on('click', '.fs-option', function() {
        var $wrap = $(this).closest('.fs-wrap');

        if ($wrap.hasClass('multiple')) {
            var selected = [];

            $(this).toggleClass('selected');
            $wrap.find('.fs-option.selected').each(function(i, el) {
                selected.push($(el).attr('data-value'));
            });
        }
        else {
            var selected = $(this).attr('data-value');
            $wrap.find('.fs-option').removeClass('selected');
            $(this).addClass('selected');
            $wrap.find('.fs-dropdown').hide();
        }

        $wrap.find('select').val(selected);
        $wrap.find('select').fSelect('reloadDropdownLabel');
    });
   
 // Qualifications for Assessor-Moderator Registration   
    $(document).on('click', '.assessor_qualification .load_more', function() {
	    var limit = 8;
	    var qualification_id=parseInt($('.assessor_qualification .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_qualification",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'last_qualification_id':qualification_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".assessor_qualification .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>(&#160;"+value['saqa_qual_id']+"&#160;) &#160;"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });
    
 // Unit Standards for Assessor-Moderator Registration   
    $(document).on('click', '.assessor_unit_qualification .load_more', function() {
	    var limit = 8;
	    var qualification_id=parseInt($('.assessor_unit_qualification .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_unit_qualification",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'last_qualification_id':qualification_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".assessor_unit_qualification .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>(&#160;"+value['saqa_qual_id']+"&#160;) &#160;"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });
    
    //Main Qualifications for Provider Accreditation Registration   
    $(document).on('click', '.provider_qualification .load_more', function() {
	    var limit = 8;
	    var qualification_id=parseInt($('.provider_qualification .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_qualification",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'last_qualification_id':qualification_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".provider_qualification .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>(&#160;"+value['saqa_qual_id']+"&#160;)&#160;"+value['name']+"&#160;(&#160;Minimum Credits- "+value['m_credits']+"&#160;)&#160;"+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });
    
    // Main Skills for Provider Accreditation Registration   
    $(document).on('click', '.provider_skill .load_more', function() {
	    var limit = 8;
	    var skill_id=parseInt($('.provider_skill .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_skill",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'last_skill_id':skill_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".provider_skill .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>(&#160;"+value['code']+"&#160;)&#160;"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });
    // Main Learning Programme for Provider Accreditation Registration   
    $(document).on('click', '.learning_skill .load_more', function() {
	    var limit = 8;
	    var lp_id=parseInt($('.learning_skill .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_lp",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'last_lp_id':lp_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".learning_skill .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>(&#160;"+value['code']+"&#160;)&#160;"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });   

    // Assessor for Provider Accreditation Registration   
    $(document).on('click', '.assessor .load_more', function() {
	    var limit = 8;
	    var assessor_id=parseInt($('.assessor .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_assessor",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'assessor_id':assessor_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".assessor .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });       
    
    // Moderator for Provider Accreditation Registration   
    $(document).on('click', '.moderator .load_more', function() {
	    var limit = 8;
	    var moderator_id=parseInt($('.assessor .fs-options').children().last().attr('data-value'))
		$.ajax({ url: "/load_more_moderator",
	        type:"post", 
	        dataType:"json",
	        async : false,
	        data:{'moderator_id':moderator_id},
	        success: function(result){
	        	if (result.length>0){
	        		$.each(result,function(key,value){
	        			$(".moderator .fs-options").append("<div class='fs-option' data-value='"+value['id']+"'><span class='fs-checkbox'><i></i></span><div class='fs-option-label'>"+value['name']+"<p class='hidden'> </p></div></div>")
	        		})
	        		
	        	}
	        },
		});   
    });       
    $(document).on('keyup', '.fs-search input', function(e) {
        if (40 == e.which) {
            $(this).blur();
            return;
        }

        var $wrap = $(this).closest('.fs-wrap');
        var keywords = $(this).val();

        $wrap.find('.fs-option, .fs-optgroup-label').removeClass('hidden');

        if ('' != keywords) {
            $wrap.find('.fs-option').each(function() {
                var regex = new RegExp(keywords, 'gi');
                if (null === $(this).find('.fs-option-label').text().match(regex)) {
                    $(this).addClass('hidden');
                }
            });

            $wrap.find('.fs-optgroup-label').each(function() {
                var num_visible = $(this).closest('.fs-optgroup').find('.fs-option:not(.hidden)').length;
                if (num_visible < 1) {
                    $(this).addClass('hidden');
                }
            });
        }

        setIndexes($wrap);
    });

    $(document).on('click', function(e) {
        var $el = $(e.target);
        var $wrap = $el.closest('.fs-wrap');

        if (0 < $wrap.length) {
            if ($el.hasClass('fs-label') || $el.hasClass('fs-arrow')) {
                window.fSelect.active = $wrap;
                var is_hidden = $wrap.find('.fs-dropdown').hasClass('hidden');
                $('.fs-dropdown').addClass('hidden');

                if (is_hidden) {
                    $wrap.find('.fs-dropdown').removeClass('hidden');
                }
                else {
                    $wrap.find('.fs-dropdown').addClass('hidden');
                }

                setIndexes($wrap);
            }
        }
        else {
            $('.fs-dropdown').addClass('hidden');
            window.fSelect.active = null;
        }
    });

    $(document).on('keydown', function(e) {
        var $wrap = window.fSelect.active;

        if (null === $wrap) {
            return;
        }
        else if (38 == e.which) { // up
            e.preventDefault();

            $wrap.find('.fs-option').removeClass('hl');

            if (window.fSelect.idx > 0) {
                window.fSelect.idx--;
                $wrap.find('.fs-option[data-index=' + window.fSelect.idx + ']').addClass('hl');
                setScroll($wrap);
            }
            else {
                window.fSelect.idx = -1;
                $wrap.find('.fs-search input').focus();
            }
        }
        else if (40 == e.which) { // down
            e.preventDefault();

            var last_index = $wrap.find('.fs-option:last').attr('data-index');
            if (window.fSelect.idx < parseInt(last_index)) {
                window.fSelect.idx++;
                $wrap.find('.fs-option').removeClass('hl');
                $wrap.find('.fs-option[data-index=' + window.fSelect.idx + ']').addClass('hl');
                setScroll($wrap);
            }
        }
        else if (32 == e.which || 13 == e.which) { // space, enter
            $wrap.find('.fs-option.hl').click();
        }
        else if (27 == e.which) { // esc
            $('.fs-dropdown').addClass('hidden');
            window.fSelect.active = null;
        }
    });

})(jQuery);