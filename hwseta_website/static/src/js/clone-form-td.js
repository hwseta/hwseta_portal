/*
Author: Tristan Denyer (based on Charlie Griefer's original clone code, and some great help from Dan - see his comments in blog post)
Plugin repo: https://github.com/tristandenyer/Clone-section-of-form-using-jQuery
Demo at http://tristandenyer.com/using-jquery-to-duplicate-a-section-of-a-form-maintaining-accessibility/
Ver: 0.9.5.0
Last updated: Oct 23, 2015

The MIT License (MIT)

Copyright (c) 2011 Tristan Denyer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
$(function () {
    $('#btnAdd').click(function () {
//        $('#accordian').accordion({
//    		collapsible: true
//    		}); 
        var num     = $('.clonedInput').length, // Checks to see how many "duplicatable" input fields we currently have
            newNum  = new Number(num+1),      // The numeric ID of the new input field being added, increasing by 1 each time
            new_heading=$('#accordian h2:last').clone();
//        	new_heading=$('#ID'+num+'_reference').clone();
            newElem = $('#entry' + num).clone().attr('id', 'entry' + newNum).fadeIn('slow');// create the new element via clone(), and manipulate it's ID using newNum value
    /*  This is where we manipulate the name/id values of the input inside the new, cloned element
        Below are examples of what forms elements you can clone, but not the only ones.
        There are 2 basic structures below: one for an H2, and one for form elements.
        To make more, you can copy the one for form elements and simply update the classes for its label and input.
        Keep in mind that the .val() method is what clears the element when it gets cloned. Radio and checkboxes need .val([]) instead of .val('').
    */
        // H2 - section
        
        
        if ($('#ID' + (num) + '_campusname').val() ==''){
        	$('#ID' + (num) + '_campusname').focus();
        	alert("Please enter campus name");
        	return false;
        }else if ($('#ID' + (num) + '_email').val() ==''){
        	$('#ID' + (num) + '_email').focus();
        	alert("Please enter campus email id");
        	return false;
        }else if ($('#ID' + (num) + '_street').val() ==''){
        	$('#ID' + (num) + '_street').focus();
        	alert("Please specify an street address");
        	flag=false;
        	return false;
        }else if ($('#ID' + (num) + '_street2').val() ==''){
        	$('#ID' + (num) + '_street2').focus();
        	alert("Please specify an street2 address");
        	flag=false;
        	return false;
        }
       /* else if ($('#ID' + (num) + '_street3').val() ==''){
        	$('#ID' + (num) + '_street3').focus();
        	alert("Please specify an street3 address");
        	flag=false;
        	return false;
        }*/
        else if ($('#ID' + (num) + '_country').val() ==''){
        	$('#ID' + (key+1) + '_country').focus();
        	alert("Please Select country");
        	flag=false;
        	return false;
        }else if ($('#ID' + (num) + '_province').val() ==''){
        	$('#ID' + (num) + '_province').focus();
        	alert("Please Select Province");
        	flag=false;
        	return false;
        } else if ($('#ID' + (num) + '_txtContactNameSurname').val() ==''){
        	$('#ID' + (num) + '_txtContactNameSurname').focus();
        	alert("Please specify a contact person name");
        	return false;
        }else if ($('#ID' + (num) + '_txtContactEmail').val() ==''){
        	$('#ID' + (num) + '_txtContactEmail').focus();
        	alert("Please specify an contact person email address");
        	return false;
        } 
     /*   else if ($('#ID' + (num) + '_campusassessor').val() == null){
        	$('#ID' + (num) + '_campus_assessor_number').focus();
        	alert("Please add Assessors!");
        	return false;
        }else if ($('#ID' + (num) + '_campusmoderator').val() == null){
        	$('#ID' + (num) + '_campus_moderator_number').focus();
        	alert("Please add Moderators!");
        	return false;
        }*/
        console.log("assessor----",$('#ID' + (num) + '_campusassessor'));
        console.log("moderator----",$('#ID' + (num) + '_campusmoderator'));

        newElem.find('.heading-reference').attr('id', 'ID' + newNum + '_reference').attr('name', 'ID' + newNum + '_reference').html('<label>Campus #' + newNum+'</label');
        
        //name 
        newElem.find('.campusname').attr('id', 'ID' + newNum + '_campusname').attr('name', 'ID' + newNum + '_campusname').val('');
        
        newElem.find('.street').attr('id', 'ID' + newNum + '_street').attr('name', 'ID' + newNum + '_street').val('');        
        newElem.find('.street2').attr('id', 'ID' + newNum + '_street2').attr('name', 'ID' + newNum + '_street2').val('');
        newElem.find('.street3').attr('id', 'ID' + newNum + '_street3').attr('name', 'ID' + newNum + '_street3').val('');
        newElem.find('.city').attr('id', 'ID' + newNum + '_city').attr('name', 'ID' + newNum + '_city').val('');
        newElem.find('.suburb').attr('id', 'ID' + newNum + '_suburb').attr('name', 'ID' + newNum + '_suburb').val('');
        newElem.find('.province').attr('id', 'ID' + newNum + '_province').attr('name', 'ID' + newNum + '_province').val(0); 
        newElem.find('.country').attr('id', 'ID' + newNum + '_country').attr('name', 'ID' + newNum + '_country').val(0);
        newElem.find('.email').attr('id', 'ID' + newNum + '_email').attr('name', 'ID' + newNum + '_email').val('');
        newElem.find('.phone').attr('id', 'ID' + newNum + '_phone').attr('name', 'ID' + newNum + '_phone').val('');
        newElem.find('.mobile').attr('id', 'ID' + newNum + '_mobile').attr('name', 'ID' + newNum + '_mobile').val('');
        newElem.find('.fax').attr('id', 'ID' + newNum + '_fax').attr('name', 'ID' + newNum + '_fax').val('');
        newElem.find('.zip').attr('id', 'ID' + newNum + '_zip').attr('name', 'ID' + newNum + '_zip').val('');
        newElem.find('.designation').attr('id', 'ID' + newNum + '_designation').attr('name', 'ID' + newNum + '_designation').val('');
        newElem.find('.status').attr('id', 'ID' + newNum + '_status').attr('name', 'ID' + newNum + '_status').val('');
        
        // satellite contact
        newElem.find('.txtContactNameSurname').attr('id', 'ID' + newNum + '_txtContactNameSurname').attr('name', 'ID' + newNum + '_txtContactNameSurname').val('');
        newElem.find('.txtContactEmail').attr('id', 'ID' + newNum + '_txtContactEmail').attr('name', 'ID' + newNum + '_txtContactEmail').val('');
        newElem.find('.txtContactTel').attr('id', 'ID' + newNum + '_txtContactTel').attr('name', 'ID' + newNum + '_txtContactTel').val('');
        newElem.find('.txtContactCell').attr('id', 'ID' + newNum + '_txtContactCell').attr('name', 'ID' + newNum + '_txtContactCell').val('');
        newElem.find('.txtJobTitle').attr('id', 'ID' + newNum + '_txtJobTitle').attr('name', 'ID' + newNum + '_txtJobTitle').val('');
        newElem.find('.txtContactSurname').attr('id', 'ID' + newNum + '_txtContactSurname').attr('name', 'ID' + newNum + '_txtContactSurname').val('');
           
        //satellite assessor
        newElem.find('.campusassessor').attr('id', 'ID' + newNum + '_campusassessor').attr('name', 'ID' + newNum + '_campusassessor').val('');            
        newElem.find('.campusassesorset').attr('id', 'ID' + newNum + '_campusassesorset').attr('name', 'ID' + newNum + '_campusassesorset').val('');
        newElem.find('.campus_assessor_number').attr('id', 'ID' + newNum + '_campus_assessor_number').attr('name', 'ID' + newNum + '_campus_assessor_number').val('');
        newElem.find('.campus_add_assessor').attr('id', 'ID' + newNum + '_campus_add_assessor').attr('name', 'ID' + newNum + '_campus_add_assessor');
        newElem.find('.campus_remove_assessor').attr('id', 'ID' + newNum + '_campus_remove_assessor').attr('name', 'ID' + newNum + '_campus_remove_assessor');
        $("#entry"+newNum+" .campus_assessor .fs-options .fs-option").removeClass( "selected" );
//        newElem.find('.campus_remove_assessor').attr('#ID'+newNum+'_campusassessor').find('option').remove()
        newElem.find('#ID'+newNum+'_campusassessor option').remove()
        
        //satellite moderator
        newElem.find('.campusmoderator').attr('id', 'ID' + newNum + '_campusmoderator').attr('name', 'ID' + newNum + '_campusmoderator').val('');
        newElem.find('.campusmoderatorset').attr('id', 'ID' + newNum + '_campusmoderatorset').attr('name', 'ID' + newNum + '_campusmoderatorset').val('');        
        newElem.find('.campus_moderator_number').attr('id', 'ID' + newNum + '_campus_moderator_number').attr('name', 'ID' + newNum + '_campus_moderator_number').val('');
        newElem.find('.campus_add_moderator').attr('id', 'ID' + newNum + '_campus_add_moderator').attr('name', 'ID' + newNum + '_campus_add_moderator');
        newElem.find('.campus_remove_moderator').attr('id', 'ID' + newNum + '_campus_remove_moderator').attr('name', 'ID' + newNum + '_campus_remove_moderator');        
        $("#entry"+newNum+" .campus_moderator .fs-options .fs-option").removeClass( "selected" );
        newElem.find('#ID'+newNum+'_campusmoderator option').remove()
        
        //satellite Qualification
        newElem.find('.campusualification').attr('id', 'ID' + newNum + '_campusualification').attr('name', 'ID' + newNum + '_campusualification').val('');
        newElem.find('.campusqualificationids').attr('id', 'ID' + newNum + '_campusqualificationids').attr('name', 'ID' + newNum + '_campusqualificationids').val('');
        
        //satellite Campus Skills
        newElem.find('.campusskill').attr('id', 'ID' + newNum + '_campusskill').attr('name', 'ID' + newNum + '_campusskill').val('');
        newElem.find('.campusskillsids').attr('id', 'ID' + newNum + '_campusskillsids').attr('name', 'ID' + newNum + '_campusskillsids').val('');

        //satellite Campus Learning
        newElem.find('.campuslearning').attr('id', 'ID' + newNum + '_campuslearning').attr('name', 'ID' + newNum + '_campuslearning').val('');
        newElem.find('.campuslearningsids').attr('id', 'ID' + newNum + '_campuslearningsids').attr('name', 'ID' + newNum + '_campuslearningsids').val('');

        
        //satellite Campus Assessor SLA 
        newElem.find('.campus_wrapper_assessor').attr('id', 'ID' + newNum + '_campus_wrapper_assessor').attr('name', 'ID' + newNum + '_campus_wrapper_assessor')
        newElem.find('#ID' + newNum + '_campus_wrapper_assessor div').remove()
        
        //satellite Campus Moderator SLA 
        newElem.find('.campus_wrapper_moderator').attr('id', 'ID' + newNum + '_campus_wrapper_moderator').attr('name', 'ID' + newNum + '_campus_wrapper_moderator')
        newElem.find('#ID' + newNum + '_campus_wrapper_moderator div').remove()
//        $('#ID'+newNum+'campus_wrapper_moderator').find('div').remove()
        
        $('#ID'+newNum+'_country option:contains("South Africa")').prop('selected',true).trigger('change');

    // Insert the new element after the last "duplicatable" input field
//        $('#accordian' + num).after(newElem).accordion("refresh").accordion({ active: num });
//        $('#accordian').accordion({
//    		collapsible: true
//    		});  
//        newheading.appendTo("#accordion");
//        newElem.appendTo("#accordion");
        
//        $('#accordian h2:last').clone().appendTo('#accordian');
        $('#accordian').append('<h2 class="heading-reference"><label>Sattelite Campus #'+(num+1)+'</label></h2>');
        $('#accordian').append(newElem);
//        $('#accordian').accordion("refresh").accordion({ active: num });
        $('#accordian').accordion('destroy').accordion({collapsible: true,active:num});
        $('#ID' + newNum + '_title').focus();

    // Enable the "remove" button. This only shows once you have a duplicated section.
        $('#btnDel').attr('disabled', false);

    // Right now you can only add 4 sections, for a total of 5. Change '5' below to the max number of sections you want to allow.
//        $('.clonedInput').accordion("refresh").accordion({ active: newNum }); 
        if (newNum == 100)
        $('#btnAdd').attr('disabled', true).prop('value', "You've reached the limit"); // value here updates the text in the 'add' button when the limit is reached 
    });

    $('#btnDel').click(function () {
    // Confirmation dialog box. Works on all desktop browsers and iPhone.
        if (confirm("Are you sure you wish to remove this section? This cannot be undone."))
            {
                var num = $('.clonedInput').length;
                // how many "duplicatable" input fields we currently have
                $("h2:last").remove();

                $('#entry' + num).slideUp('slow', function () {
	                $(this).remove();
	                $('#entry' + num).accordion("refresh").accordion({ active: (num - 1),heightStyle:"content" });
	                // if only one element remains, disable the "remove" button
	                    if (num -1 === 1)
	                $('#btnDel').attr('disabled', true);
	                // enable the "add" button
	                $('#btnAdd').attr('disabled', false).prop('value', "Add");
                });
            }
        return false; // Removes the last section you added
    });
    // Enable the "add" button
    $('#btnAdd').attr('disabled', false);
    // Disable the "remove" button
    $('#btnDel').attr('disabled', true);
});