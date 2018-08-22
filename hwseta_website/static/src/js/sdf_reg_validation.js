function sdfGotoStep2(){

	
	if (document.frmSDF.cboTHETAChamber.value == "")
    {
    document.frmSDF.txtEmployerSDL.focus();
    alert("Please complete the Employer SDL field.");
    return false;
    }
	if (document.frmSDF.cboTitle.value == "")
	{
	alert("Please select a title.");
	document.frmSDF.cboTitle.focus();
	return false;
	}	
	
	if (document.frmSDF.txtFirstName.value == "")
		{
		document.frmSDF.txtFirstName.focus();
		alert("Please complete the First Name field.");
		return false;
		}	
	if (document.frmSDF.txtSurname.value == "")
	{
	document.frmSDF.txtSurname.focus();
	alert("Please complete the Surname field.");
	return false;
	}	
		
	if (document.frmSDF.txtWorkEmail.value == "")
	{
	document.frmSDF.txtWorkEmail.focus();
	alert("Please complete the E-Mail Address field.");
	return false;
	}	
	if (document.frmSDF.txtWorkEmail.value != "")
	{
	if (checkmail(document.frmSDF.txtWorkEmail.value) == false) 
		{
			alert("Invalid E-mail Address! Please re-enter.")
			document.frmSDF.txtWorkEmail.focus();
			return false;
		}   																				
}	
	if (document.frmSDF.txtWorkPhone.value == "")
		{
		alert("Please complete cell phone.");
		document.frmSDF.txtWorkPhone.focus();
		return false;
		}
	
	if (document.frmSDF.txtWorkPhone.value == "")
	{
	document.frmSDF.txtWorkPhone.focus();
	alert("Please Enter the Cell phone");
	return false;
	}
	if (document.frmSDF.txtWorkPhone.value!= "")
	{
		if ($('#txtWorkPhone').val().length < 10) {
			alert("Phone Number should be 10 digit")
			$("#txtWorkPhone").focus();
			return false;
		}
	}
	var flag=0;
	$(".field_wrapper_sdf_appointment_letter div input[type=file]").each(function(index,value){
    	var id=$(this).attr('id');
    	var key=id.split('_');
	    if($(this).val()==''){
	    		alert("Please upload SDF Appointment letter for "+key[0]+"");
//	    		$("#"+id"").focus();
	    		flag=1
	    	}
	    });	
	if (flag==1){
		return false;
	}
	return true;

}
function sdfGotoStep3(){
	if (document.frmSDF.txtAddress1.value == "")
			{
			alert("Please Enter Work Address1.");
			document.frmSDF.txtAddress1.focus();
			return false;
			}
	return true;
}
function sdfGotoStep4(){
    var selectedValue = $('#txtCitizenResStatusCode_selection').val();
    var sdf_birth_date = $('#datepicker_sdf').val();
    try {
        birth_date = $.datepicker.parseDate('dd/mm/yy', sdf_birth_date);
    }catch(e){
        document.frmSDF.datepicker_sdf.focus();
        $('#datepicker_sdf').css("border-color","#cccccc");
        alert(sdf_birth_date + ' is not valid.  Format must be DD/MM/YYYY ' +
           'and the date value must be valid for the calendar.');
        return false;
    }
   if (document.frmSDF.txtCntNoHome.value!= "")
	{
		if ($('#txtCntNoHome').val().length < 10) {
			alert("Phone Number should be 10 digit")
			$("#txtCntNoHome").focus();
			return false;
		}
	}
    if (document.frmSDF.txtCntNoOffice.value!= "")
	{
		if ($('#txtCntNoOffice').val().length < 10) {
			alert("Phone Number should be 10 digit")
			$("#txtCntNoOffice").focus();
			return false;
		}
	}	    
    if(selectedValue.trim() == 'sa'){
        document.frmSDF.txtPassportNo.value = ""
        document.frmSDF.txtNationalId.value = "";      
        if($('#id_number').val()==''){
            document.frmSDF.txtID.focus();
            alert("Please complete the Identification field.");
            return false;
        }
        if($('#id_number').val()!=''){
        	if ($('#id_number').val().length < 10) {
            document.frmSDF.txtID.focus();
            alert("Identification Number should be 13 digit for SA cititzen.");
            return false;
        	}
        }        
        if($('#txtIdDocument').val()==''){
            document.frmSDF.txtIdDocument.focus();
            alert("Please Upload Id Document.");
            return false;
           
        }      
    }else if(selectedValue.trim() == 'dual'){
        if($('#txtIdDocument').val()==''){
            document.frmSDF.txtIdDocument.focus();
            alert("Please Upload Id Document.");
            return false;
        }  
        return true;
    }else if(selectedValue.trim() == 'other'){
        if($('#txtIdDocument').val()==''){
            document.frmSDF.txtIdDocument.focus();
            alert("Please Upload Id Document.");
            return false;
        }  
        if (document.frmSDF.txtNationalId.value == "")
        {
            document.frmSDF.txtNationalId.focus();
            alert("Please complete the National Id field.");
            return false;
        }
        if (document.frmSDF.txtPassportNo.value == "")
        {
            document.frmSDF.txtPassportNo.focus();
            alert("Please complete the Passport field.");
            return false;
        }      
    }
    else if(selectedValue.trim() == 'unknown'){
        if($('#txtIdDocument').val()==''){
            document.frmSDF.txtIdDocument.focus();
            alert("Please Upload Id Document.");
            return false;
        }  
        return true;
    }
    else if($('#txtCitizenResStatusCode_selection').val()==''){
        document.frmSDF.txtCitizenResStatusCode_selection.focus();
        alert("Please Select Citizen resident Status.");
        return false;
    }
    return true;
}
function sdfGotoStep5(){
	return true;
}

function runSubmit()
{
	document.frmSDF.submit();
	return false;
} 

//This will validate SDF Registration form for invalid input from user
function changePassword ()
	{
		document.frmSDF.txtPassword.value = ""; 
		document.frmSDF.txtRePassword.value = "";
		return false;
	}

//added this function from ETQA to check for valid email addresses - #10801
function checkmail(what)
{
 var s = what;
 var ss= /@/i;            
 var r = s.search(ss);
 if (r == -1)
 {
  return(false);
 }
 else
 {
  return(true);
 }
} 

function validatePhone()
{
	
	var stripped = document.frmSDF.txtWorkPhoneNo.value.replace(/[\(\)\.\-\ ]/g, '');
	var illegalChars= /[\(\)\&lt;\&gt;\,\;\:\\\[\-\]]/ ;
	
	if (document.frmSDF.txtWorkPhoneNo.value == "") 
	{
		alert("You didn't enter a phone number");
		return false;
	} 
	//alert(stripped);
	if (document.frmSDF.txtWorkPhoneNo.value.match(illegalChars))  
	{
		alert("The phone number contains illegal characters");
		return false;
	}
	else if (isNaN(stripped))
	{
		alert("The phone number is not numbers only.");
		return false;
	}  
	else if (!(stripped.length == 10)) 
	{
		alert("The phone number is the wrong length. Make sure you included an area code");
		return false;
	} 
	
	
}

function validatefax() 
{
	var stripped = document.frmSDF.txtFaxNo.value.replace(/[\(\)\.\-\ ]/g, '');
	var illegalChars = /[\(\)\&lt;\&gt;\,\;\:\\\[\-\]]/ ;
	
	if (document.frmSDF.txtFaxNo.value == "") 
	{
		alert("You didn't enter a fax number");
		return false;
	} 
	//alert(stripped);
	else if (document.frmSDF.txtFaxNo.value.match(illegalChars))  
	{
		alert("The fax number contains illegal characters");
		return false;
	}
	else if (isNaN(stripped))
	{
		alert("The fax number is not numbers only.");
		return false;
	}  
	else if (!(stripped.length == 10)) 
	{
		alert("The fax number is the wrong length. Make sure you included an area code");
		return false;
	} 	
}

function validateCell() 
{
	var stripped = document.frmSDF.txtCellNo.value.replace(/[\(\)\.\-\ ]/g, '');
	var illegalChars = /[\(\)\&lt;\&gt;\,\;\:\\\[\-\]]/ ;
	
	if (document.frmSDF.txtCellNo.value == "") 
	{
		alert("You didn't enter a Cellphone number");
		return false;
	} 
	//alert(stripped);
	else if (document.frmSDF.txtCellNo.value.match(illegalChars))  
	{
		alert("The Cellphone number contains illegal characters");
		return false;
	}
	else if (isNaN(stripped))
	{
		alert("The Cellphone number is not numbers only.");
		return false;
	}  
	else if (!(stripped.length == 10)) 
	{
		alert("The Cellphone number is the wrong length.");
		return false;
	} 	
}

function CheckIDNumber ()  
{
    
	var val1 = 0;
	var val2 = 0;
	var iLoop;
	var cTmp;
	var strAcc = new String(document.frmSDF.txtID.value);
	if (strAcc.length == 13) {
	  for (iLoop=0; iLoop<13; iLoop=iLoop+2) {
	     cTmp = strAcc.charAt(iLoop);
	     if (isNaN(cTmp)) {
	       //window.alert("Please, enter a thirteen digit number.");
//	       document.frmSDF.txtIDMsg.style.color = "RED"
           document.frmSDF.txtIDMsg.setAttribute('style','font-family: Arial; font-size: 8pt; color: red !important; border: 0px; background-color: rgb(247, 247, 239);');
	       document.frmSDF.txtIDMsg.value = "Invalid South African ID Number";
	       return;
	     }
	     val1 = val1 + eval(cTmp);
	  }
	  for (iLoop=1; iLoop<12; iLoop=iLoop+2) {
	     cTmp = strAcc.charAt(iLoop);
	     if (isNaN(cTmp)) {
	       //window.alert("Please, enter a thirteen digit number.");
//	       document.frmSDF.txtIDMsg.style.color = "RED"
	       document.frmSDF.txtIDMsg.setAttribute('style','font-family: Arial; font-size: 8pt; color: red !important; border: 0px; background-color: rgb(247, 247, 239);');
	       document.frmSDF.txtIDMsg.value = "Invalid South African ID Number";
	       return;
	     }
	     cTmp = eval(cTmp) * 2;
	     if (cTmp >= 10) {
	       cTmp = (cTmp - 10) + 1;
	     }
	     val2 = val2 + cTmp;
	  }
	  var iTotal = ((val1 + val2) / 10);
	  cTmp = iTotal.toString(10);
	  var sTmp = ".";
	  var iValid = cTmp.indexOf(sTmp, 0);
	  if (iValid == -1) {
		//Cool
		//alert("COOL");
//		document.frmSDF.txtIDMsg.style.color = "GREEN"
		document.frmSDF.txtIDMsg.setAttribute('style','font-family: Arial; font-size: 8pt; color: green !important; border: 0px; background-color: rgb(247, 247, 239);');
		document.frmSDF.txtIDMsg.value = "Valid South African ID Number";

     	
	 
            return true
	  } else {
		//Wrong
		//alert("WRONG");
//		document.frmSDF.txtIDMsg.style.color = "BLACK"
		document.frmSDF.txtIDMsg.setAttribute('style','font-family: Arial; font-size: 8pt; color: red !important; border: 0px; background-color: rgb(247, 247, 239);');
		document.frmSDF.txtIDMsg.value = "Invalid South African ID Number";
            return false
	  }
	} else {
	       //window.alert("Please, enter a thirteen digit number.");
//	       document.frmSDF.txtIDMsg.style.color = "RED"
		   document.frmSDF.txtIDMsg.setAttribute('style','font-family: Arial; font-size: 8pt; color: red !important; border: 0px; background-color: rgb(247, 247, 239);');
	       document.frmSDF.txtIDMsg.value = "Invalid South African ID Number";
        }
        
        
}

function IDdisable()
{
    //if (frmSDF.cbosdftype.value == 4)
    //{
    //    document.frmSDF.txtID.disabled=true;
    //}
    //else
    //{
    //    document.frmSDF.txtID.disabled=false;
    //}
}
function CheckNumeric(txtbox)
{
if (isNumNoZero(txtbox,txtbox.name))
		{
			return false;
		}
		else
		{
			txtbox.value = "0"
			txtbox.focus();
			return false;
		}	
}
function ClearSDFTraining()
{
    if (frmSDF.chkTraining.checked == false)
    {
        frmSDF.txtTrainProv.value = "";
        frmSDF.txtTrainYear.value = "";
        frmSDF.txtCert.value = "";
    }
}

function SetPhysical()
{
        if (frmSDF.chbSameasPostal.checked == true)
	    {      
	        if (document.frmSDF.txtAddressPostalLine1.value != "") document.frmSDF.txtAddressPyhsicalLine1.value = document.frmSDF.txtAddressPostalLine1.value;
	        if (document.frmSDF.txtAddressPostalLine2.value != "") document.frmSDF.txtAddressPyhsicalLine2.value = document.frmSDF.txtAddressPostalLine2.value;
	        if (document.frmSDF.txtAddressPostalPostalCode.value != "") document.frmSDF.txtAddressPyhsicalPostalCode.value = document.frmSDF.txtAddressPostalPostalCode.value;
	        if (document.frmSDF.txtAddressPostalCity.value != "") document.frmSDF.txtAddressPyhsicalCity.value = document.frmSDF.txtAddressPostalCity.value;
	        if (document.frmSDF.cboProvince.selectedIndex != "") document.frmSDF.cboProvincePyhsical.selectedIndex = document.frmSDF.cboProvince.selectedIndex;
        }
 }
 

function boxupdatePwAndUn()
{
    //Get first 6 digits of id number
    var idstr=document.frmSDF.txtID.value;
    var idpart=idstr.substring(0,6);

    //Assgin the surname + 6 digits of idnumber as password eg Botes650602
    var boxone = document.frmSDF.txtSurname.value
    var boxtwo = document.frmSDF.txtPassword.value
    document.frmSDF.txtPassword.value=boxone+idpart
    document.frmSDF.txtRePassword.value=boxone+idpart
    
    //Assign the id number as username
    var boxthree = document.frmSDF.txtID.value
    var boxfour = document.frmSDF.txtLogon.value
    document.frmSDF.txtLogon.value=boxthree
}

function passwordpreview()
{
    //show user a preview of the password
    var boxone = document.frmSDF.txtPassword.value
    alert("Your password is: " + boxone);
}

function SpecializationSearch()
{
	var returnValue = window.showModalDialog("SpecializationSearch_IFrame.asp?lYear=", "document", "center:yes; help:no; dialogWidth:600px; dialogHeight:400px; status:no; scroll:yes; resizable:yes");
 if (returnValue != undefined)
 {
  var String = returnValue.split("|||");

  frmSDF.txtofoCode.value = String[0];
  frmSDF.txtofotitle.value = String[1];
  frmSDF.cboOccupation.value = String[2];
 } 
}

function GetMunicipality(controlName) {

    var returnValue;
    var municipalityName = "";
    var municipalityId = "0";
    returnValue = window.showModalDialog('/cdas/Geographic/Municipality_Opening.asp', document, 'dialogWidth:780px; status:no;  help:no; scroll:no; center:yes; resizable:yes;');

    if ((returnValue != null) && (returnValue != undefined)) {
        var CheckValues = returnValue;
        CheckValues = CheckValues.split('|||')
        
        
        document.getElementById(controlName + "Id").value = CheckValues[0];
        document.getElementById("txt" + controlName).value = unescape(CheckValues[1]);

        
    }
   
}

function ShowRelatedQuestion()
{
    if (frmSDF.optQualifiedSDF[0].checked == true)
    {
        div1.className = "show";
    }
    else
    {
        div1.className = "hide";
    }
}
function selectAll()
{
selectBox = document.getElementById("cboTHETAChamber");

for (var i = 0; i < selectBox.options.length; i++)
{
selectBox.options[i].selected = true;
var $textbox = $('<input/>').attr({type:'text',name:'opt'+i,value:selectBox.options[i].value}).addClass('text');
$("#myselectedoptions").append($textbox);
}

var $textboxcount = $('<input/>').attr({type:'text',name:'optionCount',value:selectBox.options.length}).addClass('text');
$("#myselectedoptions").append($textboxcount);
}


$(function() {
     $( "#dialog-message" ).dialog({
     autoOpen: false,
     closeOnEscape:false,
     hideCloseButton: false,
     dialogClass:false,
     draggable:false,
     modal: true,
      buttons: {
        Ok: function() {
          $( this ).dialog( "close" );
//          $("#sdf_submit_form").submit();
        }
      },
     open: function(event, ui) { jQuery('.ui-dialog-titlebar-close').hide(); }
    });
    
    $( "#dialog-warning" ).dialog({
     autoOpen: false,
     modal: true,
      buttons: {
        Ok: function() {
          $( this ).dialog( "close" );
          document.frmSDF.txtEmployerSDL.focus();
        }
      }
    });
 
    $( "#sdfSubmit" ).click(function() {
	    var flag = false;
	    if (document.frmSDF.txtHomeAddress1.value == "")
	    {
        	    document.frmSDF.txtHomeAddress1.focus();
        	    alert("Please complete Home Address1 field.");
        	    flag = false;
        	    return false;
	    }
	    if (document.frmSDF.txtPostalAddress1.value == "" && document.frmSDF.sdf_postal_address.checked == false)
	    {
        	    document.frmSDF.txtPostalAddress1.focus();
        	    alert("Please complete Postal Address1 field.");
        	    flag = false;
        	    return false;
    	    }
	    else {
		flag = true;
	    }
	    if (flag == true) {
        	var sdf_reference_no = document.getElementById("sdf_reference_no").value;
        	selectAll();
        	$("#sdf_submit_form").submit();
    		$("#dialog-message")
    		.append(
    			"<p> Thank you for your SDF application. Your application will be evaluated. Your Reference Number is : "
    			+ sdf_reference_no
    			+ "</p>");
    		$("#dialog-message").dialog("open");
    		// return false;
    
            }
//      var sdf_reference_no = document.getElementById("sdf_reference_no").value;
//      $( "#dialog-message" ).append( "<p>Thank you for submiting your application, Your reference number is "+sdf_reference_no+"</p>" );
//       selectAll();
//      $( "#dialog-message" ).dialog( "open" );
//        return false;
    });
  });
  var array =[];
  function AddOption1() {
    if (sdf_submit_form.txtEmployerSDL.value !== "") {
        
        var sdl_no=sdf_submit_form.txtEmployerSDL.value
        var wrapper = $('.field_wrapper_sdf_appointment_letter');
         $.when($("#cboTHETAChamber option:selected").each(function(key,value){
		 	array.push(value.text.split(' -')[0]);
			})).done(function(){
				if($.inArray(sdf_submit_form.txtEmployerSDL.value, array) !== -1){
				alert("Please Enter Unique SDL Number!!!");
				sdf_submit_form.txtEmployerSDL.value="";
				array =[]
				return false;
				}
				else{
				    	$.ajax({ url: "/page/check_sdl_number",
				            type:"post", 
				            dataType:"json",
				            async : true,
				            data:{'sdl_no':sdl_no},
				            success: function(result){
				            	if (result.length>0){
				                    var oOption = document.createElement("OPTION");
				                    var employer_name=result[0].name
				                    var employer_trading_name=result[0].employer_trading_name
				                    oOption.text = sdf_submit_form.txtEmployerSDL.value+"  -> "+employer_name+" -> "+employer_trading_name;
				                    oOption.value = sdf_submit_form.txtEmployerSDL.value;
				                    oOption.selected = true;
				                	sdf_submit_form.cboTHETAChamber.add(oOption);
				                    sdf_submit_form.txtEmployerSDL.value="";
				                    //agreement upload for assessor
				        			var fieldHTML = '<div><font color="#FF0000">* </font><input id="'+sdl_no+'_sdf_appointment_letter" type="file" name="'+sdl_no+'_sdf_appointment_letter" value="" /></div>';
				        			$(wrapper).append(fieldHTML);
				        			$('#cboTHETAChamber option').prop('disabled', true);
				    			}
				            	if(result.length==0){
				                    $('#dialog-warning').empty();
				                    $( "#dialog-warning" ).append( "<p>Check your employer SDL number.</p>" );
				                    $( "#dialog-warning" ).dialog( "open" );
				            	}
				            },
				    	});  
				}
			})
    }
}

function RemoveOption1() {
    $(".field_wrapper_sdf_appointment_letter div input[type=file]").each(function(index,value){
    	var id=$(this).attr('id');
    	var key=id.split('_');
	    if($("#cboTHETAChamber option:selected").val()==key[0]){
	    		$('#'+key[0]+'_sdf_appointment_letter').parent().remove();
	    	}
	    });	
    if (sdf_submit_form.cboTHETAChamber.selectedIndex != -1) {
        sdf_submit_form.cboTHETAChamber.remove(sdf_submit_form.cboTHETAChamber.selectedIndex);
    }
}



$(function () {
	
	$("#datepicker").datepicker({ dateFormat: "mm/dd/yy" ,firstDay: 1, changeMonth: true,
	      changeYear: true});
	$("#datepicker_sdf").datepicker({ dateFormat: "dd/mm/yy" ,firstDay: 1, changeMonth: true,
	    changeYear: true});
});

//Added by vishwas for birthdate picker
$(function () {
	   $('#datepicker_sdf').datepicker( {
	        changeMonth: true,
	        changeYear: true,
	        showButtonPanel: true,
	   });

	$("#datepicker_sdf").datepicker().on("input change", function (e) {
	    $("#BirthDate").val(e.target.value);
	});
});

$("#txtCitizenResStatusCode_selection").change(function(){
	var selectedValue = $(this).val()
	if(selectedValue.trim() == 'sa'){
		if ( $("#nationality option[value='250']").length == 0 ){
			 	$("#nationality").append('<option value="250">South Africa</option>');
		}
		var nationality='South Africa';
		$("#nationality option:contains("+ nationality +")").attr('selected', 'selected');
		$("#nationality").attr("disabled", true);
		$('#identification').show();
		$('#id_document').show();
		$('#passport_no').val('');
//		$('#passport').hide();
		$('#nat_id').val('');
		$('#nat_id').attr("disabled", true);
		$('#passport_no').attr("disabled", true);
//		$('#national_id').hide();
		$('#id_number').attr('maxlength','13');
		$('#id_number').val('');
        $('#font_id_number').css("color","#FF0000");
        $('#font_id_document').css("color","#FF0000");
        $('#font_nat_id').css("color","#F7F7EF");
        $('#font_passport_no').css("color","#F7F7EF");
	}else if(selectedValue.trim() == 'dual'){
		if ( $("#nationality option[value='250']").length == 0 ){
			 	$("#nationality").append('<option value="250">South Africa</option>');
		}
		var nationality='South Africa';
		$("#nationality option:contains("+ nationality +")").attr('selected', 'selected');
		$("#nationality").attr("disabled", true);
		$('#identification').show();
		$('#passport').show();
		$('#national_id').show();
		$('#nat_id').attr("disabled", false);
		$('#passport_no').attr("disabled", false);
		$('#id_document').show();
		$('#id_number').attr('maxlength','20');
		$('#id_number').val('');
        $('#font_id_number').css("color","#F7F7EF");
        $('#font_nat_id').css("color","#F7F7EF");
        $('#font_passport_no').css("color","#F7F7EF");
//        $('#font_id_document').css("color","#F7F7EF");
        $('#font_id_document').css("color","#FF0000");
	}else if(selectedValue.trim() == 'other'){
		var nationality='-- select --';
		$("#nationality option:contains("+ nationality +")").attr('selected', 'selected');
		$("#nationality").attr("disabled", false);
		$("#nationality option[value='250']").remove();
		$('#passport').show();
		$('#national_id').show();
		$('#nat_id').attr("disabled", false);
		$('#passport_no').attr("disabled", false);
		$('#id_number').val('');
		$('#txtIdDocument').val('');
		$('#id_number').attr('maxlength','20');
		$('#id_number').val('');
        $('#font_nat_id').css("color","#FF0000");
        $('#font_passport_no').css("color","#FF0000");
        $('#font_id_number').css("color","#F7F7EF");
//        $('#font_id_document').css("color","#F7F7EF");
        $('#font_id_document').css("color","#FF0000");
	}
	else if(selectedValue.trim() == 'unknown'){
		if ( $("#nationality option[value='250']").length == 0 ){
			 	$("#nationality").append('<option value="250">South Africa</option>');
		}
		var nationality='-- select --';
		$("#nationality option:contains("+ nationality +")").attr('selected', 'selected');
		$("#nationality").attr("disabled", false);
		$('#identification').show();
		$('#passport').show();
		$('#national_id').show();
		$('#nat_id').attr("disabled", false);
		$('#passport_no').attr("disabled", false);
		$('#id_document').show();
		$('#id_number').attr('maxlength','20');
		$('#id_number').val('');
        $('#font_id_number').css("color","##F7F7EF");
//        $('#font_id_document').css("color","##F7F7EF");
        $('#font_id_document').css("color","#FF0000");
        $('#font_id_number').css("color","#F7F7EF");
        $('#font_nat_id').css("color","#F7F7EF");
        
	}
	else if(selectedValue.trim() == ''){
		var nationality='-- select --';
		$("#nationality option:contains("+ nationality +")").attr('selected', 'selected');
		$("#nationality").attr("disabled", false);
		$('#identification').show();
		$('#passport').show();
		$('#national_id').show();
		$('#nat_id').attr("disabled", false);
		$('#passport_no').attr("disabled", false);
		$('#id_document').show();
		$('#id_number').attr('maxlength','20');
		$('#id_number').val('');
        $('#font_id_number').css("color","##F7F7EF");
//        $('#font_id_document').css("color","##F7F7EF");
        $('#font_id_document').css("color","#FF0000");
        $('#font_id_number').css("color","#F7F7EF");
        $('#font_nat_id').css("color","#F7F7EF");
	}	
	
});

$(function(){
	
$("#id_number").on('change',function(){
	var identification_no=$("id_number").val();
	$.ajax({ url: "/page/check_identification_no",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'identification_no':identification_no},
        success: function(result){
        	if (result.length>0){
			}
        },
	});
})
	
//for getting postal code according to suburb
	
	$('#txtSuburb').on('change', function() {
		var suburb=$("#txtSuburb option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'suburb':suburb},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#txtZip').val(result[0].postal_code);
    			}
            },
    	});
});	
	
	$('#txtHomeSuburb').on('change', function() {
		var suburb=$("#txtHomeSuburb option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'suburb':suburb},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#txtHomeZip').val(result[0].postal_code);
    			}
            },
    	});
});	
	
	$('#txtPostalSuburb').on('change', function() {
		var suburb=$("#txtPostalSuburb option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'suburb':suburb},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#txtPostalZip').val(result[0].postal_code);
    			}
            },
    	});
});		
	
/*	
	 
	$('#cboState').on('change', function() {
		var province=$("#cboState option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'province':province},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#cboCountry option[value=' + result[0].country + ']').attr('selected',true);
    			}
            },
    	});
    	
		});	
	
	$('#txtCity').on('change', function() {
		var city=$("#txtCity option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'city':city},
            success: function(result){
            	if (result.length>0)
    			{
           		 $('#cboCountry option[value=' + result[0].country + ']').attr('selected',true);
        		 $('#cboState option[value=' + result[0].province + ']').attr('selected',true);
    			}
            },
    	});
    	
		});		

	//for home address
	
	$('#txtHomeSuburb').on('change', function() {
		var suburb=$("#txtHomeSuburb option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'suburb':suburb},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#cboHomeCountry option[value=' + result[0].country + ']').attr('selected',true);
            		 $('#cboHomeState option[value=' + result[0].province + ']').attr('selected',true);
            		 $('#txtHomeCity option[value=' + result[0].city + ']').attr('selected',true);
    			}
            },
    	});
    	
		});
	
	$('#cboHomeState').on('change', function() {
		var province=$("#cboHomeState option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'province':province},
            success: function(result){
            	if (result.length>0)
    			{
            		$('#cboHomeCountry option[value=' + result[0].country + ']').attr('selected',true);
    			}
            },
    	});
    	
		});	
	
	$('#txtHomeCity').on('change', function() {
		var city=$("#txtHomeCity option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'city':city},
            success: function(result){
            	if (result.length>0)
    			{
           		 $('#cboHomeCountry option[value=' + result[0].country + ']').attr('selected',true);
        		 $('#cboHomeState option[value=' + result[0].province + ']').attr('selected',true);
    			}
            },
    	});
    	
		});			
	
	//for postal address
	
	$('#txtPostalSuburb').on('change', function() {
		var suburb=$("#txtPostalSuburb option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'suburb':suburb},
            success: function(result){
            	if (result.length>0)
    			{
            		 $('#cboPostalCountry option[value=' + result[0].country + ']').attr('selected',true);
            		 $('#cboPostalState option[value=' + result[0].province + ']').attr('selected',true);
            		 $('#txtPostalCity option[value=' + result[0].city + ']').attr('selected',true);
    			}
            },
    	});
    	
		});
	
	$('#cboPostalState').on('change', function() {
		var province=$("#cboPostalState option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'province':province},
            success: function(result){
            	if (result.length>0)
    			{
            		$('#cboPostalCountry option[value=' + result[0].country + ']').attr('selected',true);
    			}
            },
    	});
    	
		});	
	
	$('#txtPostalCity').on('change', function() {
		var city=$("#txtPostalCity option:selected" ).attr('value');
		
    	$.ajax({ url: "/page/get_locality",
            type:"post", 
            dataType:"json",
            async : false,
            data:{'city':city},
            success: function(result){
            	if (result.length>0)
    			{
           		 $('#cboPostalCountry option[value=' + result[0].country + ']').attr('selected',true);
        		 $('#cboPostalState option[value=' + result[0].province + ']').attr('selected',true);
    			}
            },
    	});
    	
		});	*/
	
// load province on the basis of country
	$('#cboCountry').on('change', function() {
	var country=$("#cboCountry option:selected" ).attr('value');
	$.ajax({ url: "/page/get_province",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'country':country},
        success: function(result){
        	$('#cboState').find('option').remove().end().append('<option value="">-- Select Province --</option>');
        	if (result.length>0)
			{
        		var workprovince=$("#cboState");
        		$.each(result, function(key,value) {
        				workprovince.append('<option value=' + value['id'] + '>' + value['name'] + '</option>');
        		}); 
			}
        },
	});
	});
	
// load city on the basis of province
$('#cboState').on('change', function() {
	var province=$("#cboState option:selected" ).attr('value');
	$.ajax({ url: "/page/get_city",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'province':province},
        success: function(result){
        	$('#txtCity').find('option').remove().end().append('<option value="">-- Select City--</option>');
        	$('#txtSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	$("#txtZip").val('');
        	if (result.length>0)
			{
        		var workcity=$("#txtCity");
        		$.each(result, function(key,value) {
        			/*workcity.append('<option value=' + value['id'] + '>' + value['name'] +'('+value['region']+')'+'</option>');*/
        			workcity.append('<option value='+ value['id']+ '>'+ value['name']+ '</option>');
        		});         		
			}
        },
	});
	
	});	

//load suburb on the basis of city
$('#txtCity').on('change', function() {
	var city=$("#txtCity option:selected" ).attr('value');
	
	$.ajax({ url: "/page/get_suburb",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'city':city},
        success: function(result){
        	$('#txtSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	$("#txtZip").val('');
        	if (result.length>0)
			{
        		var worksuburb=$("#txtSuburb");
        		$.each(result, function(key,value) {
        			worksuburb.append('<option value=' + value['id'] + '>' + value['name'] + '</option>');
        		}); 
			}
        },
	});
	
	});		

//for home address

$('#cboHomeCountry').on('change', function() {
	var country=$("#cboHomeCountry option:selected" ).attr('value');
	$.ajax({ url: "/page/get_province",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'country':country},
        success: function(result){
        	$('#cboHomeState').find('option').remove().end().append('<option value="">-- Select Province --</option>');
        	if (result.length>0)
			{
        		var homeprovince=$("#cboHomeState");
        		$.each(result, function(key,value) {
        			homeprovince.append('<option value=' + value['id'] + '>' + value['name'] + '</option>');
        		}); 
			}
        },
	});
	});

$('#cboHomeState').on('change', function() {
	var province=$("#cboHomeState option:selected" ).attr('value');
	$.ajax({ url: "/page/get_city",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'province':province},
        success: function(result){
        	$('#txtHomeCity').find('option').remove().end().append('<option value="">-- Select City--</option>');
        	$('#txtHomeSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	$('#txtHomeZip').val('');
        	if (result.length>0)
			{
        		var homecity=$("#txtHomeCity");
        		$.each(result, function(key,value) {
        			/*homecity.append('<option value=' + value['id'] + '>' + value['name'] +'('+value['region']+')'+'</option>');*/
        		    	homecity.append('<option value='+ value['id']+ '>'+ value['name']+ '</option>');
        		});
			}
        },
	});
});	

$('#txtHomeCity').on('change', function() {
	var city=$("#txtHomeCity option:selected" ).attr('value');
	
	$.ajax({ url: "/page/get_suburb",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'city':city},
        success: function(result){
        	$('#txtHomeSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	if (result.length>0)
			{
        		var homesuburb=$("#txtHomeSuburb");
        		$.each(result, function(key,value) {
        			homesuburb.append('<option value=' + value['id'] + '>' + value['name'] + '</option>');
        		}); 
			}
        },
	});
});		

//for postal address

$('#cboPostalCountry').on('change', function() {
	var country=$("#cboPostalCountry option:selected" ).attr('value');
	$.ajax({ url: "/page/get_province",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'country':country},
        success: function(result){
        	$('#cboPostalState').find('option').remove().end().append('<option value="">-- Select Province --</option>');
        	$('#txtPostalZip').val('');
        	if (result.length>0)
			{
        		var postalprovince=$("#cboPostalState");
        		$.each(result, function(key,value) {
        			postalprovince.append('<option value=' + value['id'] + '>' + value['name'] + '</option>');
        		}); 
			}
        },
	});
	});

$('#cboPostalState').on('change', function() {
	var province=$("#cboPostalState option:selected" ).attr('value');
	$.ajax({ url: "/page/get_city",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'province':province},
        success: function(result){
        	$('#txtPostalCity').find('option').remove().end().append('<option value="">-- Select City--</option>');
        	$('#txtPostalSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	$('#txtPostalZip').val('');
        	if (result.length>0)
			{
        		var postalcity=$("#txtPostalCity");
        		$.each(result, function(key,value) {
        			postalcity.append('<option value=' + value['id'] + '>' + value['name'] +'('+value['region']+')'+'</option>');
        			postalcity.append('<option value='+ value['id']+ '>'+ value['name']+ '</option>');
        		});
			}
        },
	});
});	

$('#txtPostalCity').on('change', function() {
	var city=$("#txtPostalCity option:selected" ).attr('value');
	
	$.ajax({ url: "/page/get_suburb",
        type:"post", 
        dataType:"json",
        async : false,
        data:{'city':city},
        success: function(result){
        	$('#txtPostalSuburb').find('option').remove().end().append('<option value="">-- Select Suburb--</option>');
        	$('#txtPostalZip').val('');
        	if (result.length>0)
			{
        		var postalsuburb=$("#txtPostalSuburb");
        		$.each(result, function(key,value) {
        			postalsuburb.append('<option value=' + value['id'] + '>' + value['name'] +'</option>');
        		}); 
			}
        },
	});
});	

//set default country as South Africa 
$('#cboCountry option:contains("South Africa")').prop('selected',true).trigger('change');	
$('#cboHomeCountry option:contains("South Africa")').prop('selected',true).trigger('change');
$('#cboPostalCountry option:contains("South Africa")').prop('selected',true).trigger('change');
	
	$('#txtCitizenResStatusCode_selection').on('change', function() {
		$('#txtCitizenResStatusCode').val($( "#txtCitizenResStatusCode_selection option:selected" ).attr('value'));
		});
	
	$('#id_number').keydown(function (e) {
		if (e.shiftKey || e.ctrlKey || e.altKey) {
		e.preventDefault();
		} else {
		var key = e.keyCode;
		if (!((key == 8) || (key == 9) || (key == 46) || (key >= 35 && key <= 40) || (key >= 48 && key <= 57) || (key >= 96 && key <= 105))) {
		e.preventDefault();
		}
		}
		});
	
    $("#txtWorkPhone").keydown(function (e) {
        // Allow: backspace, delete, tab, escape, enter and .
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
             // Allow: Ctrl+A
            (e.keyCode == 65 && e.ctrlKey === true) ||
             // Allow: Ctrl+C
            (e.keyCode == 67 && e.ctrlKey === true) ||
             // Allow: Ctrl+X
            (e.keyCode == 88 && e.ctrlKey === true) ||
             // Allow: home, end, left, right
            (e.keyCode >= 35 && e.keyCode <= 39)) {
                 // let it happen, don't do anything
                 return;
        }
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
    $("#txtCntNoHome").keydown(function (e) {
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
            (e.keyCode == 65 && e.ctrlKey === true) ||
            (e.keyCode == 67 && e.ctrlKey === true) ||
            (e.keyCode == 88 && e.ctrlKey === true) ||
            (e.keyCode >= 35 && e.keyCode <= 39)) {
                 return;
        }
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
    $("#txtCntNoOffice").keydown(function (e) {
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
            (e.keyCode == 65 && e.ctrlKey === true) ||
            (e.keyCode == 67 && e.ctrlKey === true) ||
            (e.keyCode == 88 && e.ctrlKey === true) ||
            (e.keyCode >= 35 && e.keyCode <= 39)) {
                 return;
        }
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });	
	
	$("#id_number").change(function(){
		$('#id_number').css("border-color","#cccccc");
		var dateOfBirth = '';
		if(!(/\D/.test($("#id_number").val()))){
			if ($('#id_number').val().length < 13) {
				alert("S.A.Identification Number should be greater than 13 digit")
				$('#id_number').focus();
			}else{
			var southAfricanId = $("#id_number").val().toString();
			year = southAfricanId.substring(0, 2);
		        if (year == 00 || year >= 01 && year <= 20) {
		            dateOfBirth = southAfricanId.substring(4, 6) + '/' + southAfricanId.substring(2, 4) + '/20' + southAfricanId.substring(0, 2)
		        }
	                else {
	                    dateOfBirth = southAfricanId.substring(4, 6) + '/' + southAfricanId.substring(2, 4) + '/19' + southAfricanId.substring(0, 2)
	                }
		        var dt;
		        var sbm=0;
		        var months = [1,2,3,4,5,6,7,8,9,10,11,12];
		        var days = [31,28,31,30,31,30,31,31,30,31,30,31];
		        dt = dateOfBirth
		        $(document).ready(
		            function (){
		               var arr=dt.split("/");
		               var i = 0;
		               if(arr[1] > 12)
		               {
		                   sbm=1;
		                   $('#id_number').val('');
		                   alert("Enter Valid S.A Identification Number!!");
		                   $('#id_number').focus();
		               }
		               if(arr[2] % 4 == 0)
		               {
		                   days[1] = 29;
		               }
		               for(i=0;i<12;i++)
		               {
		                   if(arr[1] == months[i])  
		                   {
		                           if(arr[0] > days[i])
		                       {
		                           sbm=1;
		                           $('#id_number').val('');
		                           alert("Enter Valid S.A Identification Number!!");
		                           $('#id_number').focus();
		                       }
		                    }
		               }
		            });
		            if(sbm == 0){
		            	var identification_no=$("#id_number").val()
		            	$.ajax({ url: "/page/check_identification_no",
		                    type:"post", 
		                    dataType:"json",
		                    async : true,
		                    data:{'identification_no':identification_no},
		                    success: function(result){
		                    	if (result.length>0){
		                    		if(result[0].result==1){
				                           $('#id_number').val('');
				                           alert("SDF Already Registered for this Identification No.");
				                           $('#id_number').focus();		                    			
		                    		}
		                    		else if(result[0].result==0){
		        						$('#datepicker_sdf').val(dt);		
		        						$("#BirthDate").val(dt);
		                    		}
		            			}
		                    },
		            	});
		            }				
			}

	}
	});
	

	$("#txtWorkEmail").change(function(){
		
    	var email=$("#txtWorkEmail").val()
    	$.ajax({ url: "/page/check_email_id",
            type:"post", 
            dataType:"json",
            async : true,
            data:{'email':email},
            success: function(result){
            	if (result.length>0){
            		if(result[0].result==1){
                           $('#txtWorkEmail').val('');
                           alert("Email ID already exist in the system!");
                           $('#txtWorkEmail').focus();		                    			
            		}
    			}
            },
    	});		
	})	;	

/*	$("#id_number").change(function(){
		$('#id_number').css("border-color","#cccccc");
		var dateOfBirth = '';
		var southAfricanId = $("#id_number").val().toString();
	    dateOfBirth = southAfricanId.substring(2,4)+'/'+southAfricanId.substring(4,6)+'/19'+southAfricanId.substring(0,2)
        var dt;
        var sbm=0;
        var months = [1,2,3,4,5,6,7,8,9,10,11,12];
        var days = [31,28,31,30,31,30,31,31,30,31,30,31];
        dt = dateOfBirth
        $(document).ready(
            function (){
               var arr=dt.split("/");
               var i = 0;
               if(arr[0] > 12)
               {
                   sbm=1;
                   $('#id_number').val('');
                   $('#id_number').focus();
                   alert("Enter Valid S.A Identification Number!!");
               }
               if(arr[2] % 4 == 0)
               {
                   days[1] = 29;
               }
               for(i=0;i<12;i++)
               {
                   if(arr[0] == months[i])  
                   {
                           if(arr[1] > days[i])
                       {
                           sbm=1;
                           $('#id_number').val('');
                           $('#id_number').focus();
                           alert("Enter Valid S.A Identification Number!!");
                           
                       }
                       
                    }
               }
            });
            if(sbm == 0){
				$('#datepicker_sdf').val(dt);		
				$("#BirthDate").val(dt);
            }
                	 		
	});*/	

	
//  added by vishwas for getting home address and postal address same
    $('#sdf_postal_address').change(function() {
    	 if($(this).prop("checked") == true){
    		$('#sdf_postal_address').val(1);
            $("#txtPostalAddress1").val($("#txtHomeAddress1").val());
            $("#txtPostalAddress2").val($("#txtHomeAddress2").val());
            $("#txtPostalAddress3").val($("#txtHomeAddress3").val());
            $("#txtPostalCity option").remove();
            $("#txtPostalCity").append($("#txtHomeCity option").clone());
            $("#txtPostalSuburb option").remove();
            $("#txtPostalSuburb").append($("#txtHomeSuburb option").clone());            
            $("#txtPostalSuburb").val($("#txtHomeSuburb").val());
            $("#txtPostalCity").val($("#txtHomeCity").val());
            $("#txtPostalZip").val($("#txtHomeZip").val());
            $("#cboPostalState").val($("#cboHomeState").val());
            $("#cboPostalCountry").val($("#cboHomeCountry").val());
            $("#tr_txtPostalAddress1").hide();
            $("#tr_txtPostalAddress2").hide();
            $("#tr_txtPostalAddress3").hide();
            $("#tr_txtPostalSuburb").hide();
            $("#tr_txtPostalCity").hide();
            $("#tr_cboPostalCountry").hide();
            $("#tr_postal_label").hide();
            $("#font_txtPostalAddress1").hide();
            
        }
    	 else if($(this).prop("checked") == false){
 			$("#txtPostalCity option").remove();
			$("#txtPostalCity").append('<option value="">-- Select City--</option>');
			$("#txtPostalSuburb option").remove();
			$("#txtPostalSuburb").append('<option value="">-- Select Suburb--</option>');    		 
     		$('#sdf_postal_address').val(0);
            $("#txtPostalAddress1").val('');
            $("#txtPostalAddress2").val('');
            $("#txtPostalAddress3").val('');
            $("#txtPostalSuburb").val('');
            $("#txtPostalCity").val('');
            $("#txtPostalZip").val('');
            $("#cboPostalState").val('');
            $("#cboPostalCountry").val('');
            $("#tr_txtPostalAddress1").show();
            $("#tr_txtPostalAddress2").show();
            $("#tr_txtPostalAddress3").show();
            $("#tr_txtPostalSuburb").show();
            $("#tr_txtPostalCity").show();
            $("#tr_cboPostalCountry").show();
            $("#tr_postal_label").show();
    		$("#font_txtPostalAddress1").show();
    		}
    }); 
    
    $("#sdf_submit_form").keypress(function (evt) {
    	//Deterime where our character code is coming from within the event
    	var charCode = evt.charCode || evt.keyCode;
    	if (charCode  == 13) { //Enter key's keycode
    	return false;
    	}
    	}); 
    
    $("input[name=radioIC]:radio").change(function () {
    	if (this.value=='Internal'){
    		$("#primary_secondary").show();
    	}else if (this.value=='Consultant'){
    		$("#primary_secondary").hide();
    	}
    });
    
});
