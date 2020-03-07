var qual_count = 0;
var skill_count = 0;
var learning_count = 0;
// var ass_count = 0;
// var mod_count = 0;
function GotoStep2Part2() {
    if (frmProviderAccreditation.txtRegName.value == "" &&
        frmProviderAccreditation.txtRegName.readOnly == false) {
        msg = "Please specify the organisation's Provider name";
        alert(msg);
        frmProviderAccreditation.txtRegName.focus();
        return false;
    } else if (frmProviderAccreditation.txtTradeName.value == "" &&
        frmProviderAccreditation.txtTradeName.readOnly == false) {
        msg = "Please specify the organisation's trading as name";
        alert(msg);
        frmProviderAccreditation.txtTradeName.focus();
        return false;
        /*
         * } else if (frmProviderAccreditation.cboOrgLegalStatus.value == "0" &&
         * frmProviderAccreditation.cboOrgLegalStatus.disabled == false) { msg =
         * "Please select a legal status"; alert(msg);
         * frmProviderAccreditation.cboOrgLegalStatus.focus(); return false;
         */
    } else if (frmProviderAccreditation.txtCompanyRegNo.value == "" &&
        frmProviderAccreditation.txtCompanyRegNo.readOnly == false) {
        msg = "Please specify a company registration number";
        alert(msg);
        frmProviderAccreditation.txtCompanyRegNo.focus();
        return false;

        /*
         * make it non mandatory } else if
         * (frmProviderAccreditation.txtSDLNo.value == "" &&
         * frmProviderAccreditation.txtSDLNo.readOnly == false) { msg = "Please
         * specify a SARS / SD levy number"; alert(msg);
         * frmProviderAccreditation.txtSDLNo.focus(); return false;
         */
    }
    /*
     * else if (frmProviderAccreditation.txtSDLNo.value == "") { msg = "Please
     * specify the SDL Number"; alert(msg);
     * frmProviderAccreditation.txtSDLNo.focus(); return false; }
     */
    /*
     * else if (frmProviderAccreditation.txtVATRegNo.value == "") { msg =
     * "Please specify the VAT registration Number"; alert(msg);
     * frmProviderAccreditation.txtVATRegNo.focus(); return false; }
     */
    else if (frmProviderAccreditation.cboOrgSICCode.value == "") {
        msg = "Please select the SIC Code";
        alert(msg);
        frmProviderAccreditation.cboOrgSICCode.focus();
        return false;
    } else if (frmProviderAccreditation.txtNumStaffMembers.value == "" &&
        frmProviderAccreditation.txtNumStaffMembers.readOnly == false) {
        msg = "Please specify the number of full time staff members";
        alert(msg);
        frmProviderAccreditation.txtNumStaffMembers.focus();
        return false;
    } else if (frmProviderAccreditation.optYesNo.value == "yes") {
        if (frmProviderAccreditation.SETA.value == "") {
            msg = "Please specify the Accreditation Number";
            alert(msg);
            frmProviderAccreditation.SETA.focus();
            return false;
        }
        if (frmProviderAccreditation.Document1.value == "") {
            msg = "Please upload Document1";
            alert(msg);
            frmProviderAccreditation.Document1.focus();
            return false;
        }
        if (frmProviderAccreditation.Document2.value == "") {
            msg = "Please upload Document2";
            alert(msg);
            frmProviderAccreditation.Document2.focus();
            return false;
        }
    }

    return true;
}

function GetSDLNo() {
    var returnValue = window
        .showModalDialog(
            "../../ETQA/Achievements/Certificates/Provider_Opening.asp?sType=Org",
            document,
            "dialogWidth:780px; status:no;  help:no; scroll:No; center:yes; resizable:Yes;")
    if (returnValue == null) {
        frmProviderAccreditation.txtSDLNo.value = "";
    } else {
        var sString = returnValue
        sString = sString.split("|||")

        frmProviderAccreditation.txtRegName.value = sString[0];
        frmProviderAccreditation.txtRegName.readOnly = true;
        frmProviderAccreditation.txtTradeName.value = sString[1];
        frmProviderAccreditation.txtTradeName.readOnly = true;
        frmProviderAccreditation.txtSDLNo.value = sString[2];
        frmProviderAccreditation.txtSDLNo.readOnly = true;

        if (sString[3] == "0") {
            frmProviderAccreditation.txtCompanyRegNo.value = "";
            frmProviderAccreditation.txtCompanyRegNo.readOnly = true;
        } else {
            frmProviderAccreditation.txtCompanyRegNo.value = sString[3];
            frmProviderAccreditation.txtCompanyRegNo.readOnly = true;
        }

        frmProviderAccreditation.cboOrgLegalStatus.selectedIndex = sString[4];
        frmProviderAccreditation.cboOrgLegalStatus.disabled = true;
        frmProviderAccreditation.OrgLegalStatus.value = sString[4];

        frmProviderAccreditation.cboOrgSICCode.selectedIndex = sString[5];
        frmProviderAccreditation.cboOrgSICCode.disabled = true;
        frmProviderAccreditation.SICCode.value = sString[5];

        if (sString[6] == "0") {
            frmProviderAccreditation.txtNumYearsCurrentBusiness.value = "";
            frmProviderAccreditation.txtNumYearsCurrentBusiness.readOnly = true;
        } else {
            frmProviderAccreditation.txtNumYearsCurrentBusiness.value = sString[6];
            frmProviderAccreditation.txtNumYearsCurrentBusiness.readOnly = true;
        }

        if (sString[7] == "0") {
            frmProviderAccreditation.txtNumStaffMembers.value = "";
            frmProviderAccreditation.txtNumStaffMembers.readOnly = true;
        } else {
            frmProviderAccreditation.txtNumStaffMembers.value = sString[7];
            frmProviderAccreditation.txtNumStaffMembers.readOnly = true;
        }

        frmProviderAccreditation.IsExistingSearch.value = 1;

    }
}

function CheckSDLNumber() {
    var xDocMenu;
    var XSLMenu;

    xDocMenu = new ActiveXObject('Microsoft.XMLDOM');
    xDocMenu.async = false;
    xDocMenu.load('../GenericXML.asp?PageType=GetNextProviderAccSDLNo');
    var SDLNumber = xDocMenu.getElementsByTagName("NUMBER/LEVYNUMBER");

    if (frmProviderAccreditation.chkSDLNo.checked == true) {
        frmProviderAccreditation.txtSDLNo.value = SDLNumber(0).text;
        frmProviderAccreditation.txtSDLNo.readOnly = true;
    } else {
        frmProviderAccreditation.txtSDLNo.value = "";
        frmProviderAccreditation.txtSDLNo.readOnly = false;
    }
    frmProviderAccreditation.txtRegName.value = "";
    frmProviderAccreditation.txtRegName.readOnly = false;
    frmProviderAccreditation.txtTradeName.value = "";
    frmProviderAccreditation.txtTradeName.readOnly = false;
    frmProviderAccreditation.cboOrgLegalStatus.selectedIndex = "";
    frmProviderAccreditation.cboOrgLegalStatus.disabled = false;
    frmProviderAccreditation.txtCompanyRegNo.value = "";
    frmProviderAccreditation.txtCompanyRegNo.readOnly = false;
    frmProviderAccreditation.cboOrgSICCode.selectedIndex = "";
    frmProviderAccreditation.cboOrgSICCode.disabled = false;
    frmProviderAccreditation.txtNumYearsCurrentBusiness.value = "";
    frmProviderAccreditation.txtNumYearsCurrentBusiness.readOnly = false;
    frmProviderAccreditation.txtNumStaffMembers.value = "";
    frmProviderAccreditation.txtNumStaffMembers.readOnly = false;
}

function AddOption() {
    if (frmProviderAccreditation.cboTHETAChamberSelect.value != "0") {

        for (var i = 0; i < frmProviderAccreditation.cboTHETAChamber.length; i++) {
            if (frmProviderAccreditation.cboTHETAChamber.options[i].value == frmProviderAccreditation.cboTHETAChamberSelect.value) {
                return false;
            }
        }
        var oOption = document.createElement("OPTION");
        oOption.text = frmProviderAccreditation.cboTHETAChamberSelect
            .item(frmProviderAccreditation.cboTHETAChamberSelect.selectedIndex).text;
        oOption.value = frmProviderAccreditation.cboTHETAChamberSelect.value;
        frmProviderAccreditation.cboTHETAChamber.add(oOption);
    }
}

function RemoveOption() {
    if (frmProviderAccreditation.cboTHETAChamber.selectedIndex != -1) {
        frmProviderAccreditation.cboTHETAChamber
            .remove(frmProviderAccreditation.cboTHETAChamber.selectedIndex);
    }
}

function keyNumerics() {
    if (event.keyCode < 48 || event.keyCode > 57)
        event.returnValue = false;
}

function CheckSDLNo(SDLNo) {
    if (SDLNo !== "") {
        var xDocMenu;
        var XSLMenu;

        xDocMenu = new ActiveXObject("Microsoft.XMLDOM");
        xDocMenu.async = false;
        xDocMenu.load('../GenericXML.asp?SDLNo=' + SDLNo);
        var Exists = xDocMenu.getElementsByTagName("NUMBER/EXISTS");

        if (Exists(0).text == "1") {
            msg = "Please note that the specified SARS/SD Levy number already exists in the system as a provider \n or as a finalized application in the provider accreditation process";
            alert(msg);
            frmProviderAccreditation.txtSDLNo.focus();
            return false;
        }
    }
}

function GotoStep3() {
    if (frmProviderAccreditation.txtContactNameSurname.value == "") {
        msg = "Please specify a name and surname";
        alert(msg);
        frmProviderAccreditation.txtContactNameSurname.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactDesignation.value == "") {
        msg = "Please specify a designation";
        alert(msg);
        frmProviderAccreditation.txtContactDesignation.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactTel.value == "") {
        msg = "Please specify a telephone / cell phone number";
        alert(msg);
        frmProviderAccreditation.txtContactTel.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactFax.value == "") {
        msg = "Please specify a fax number";
        alert(msg);
        frmProviderAccreditation.txtContactFax.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactEmail.value == "") {
        msg = "Please specify an email address";
        alert(msg);
        frmProviderAccreditation.txtContactEmail.focus();
        return false;
    } else if (frmProviderAccreditation.cboContactStatus.value == "0") {
        msg = "Please select a status in relation to the provider";
        alert(msg);
        frmProviderAccreditation.cboContactStatus.focus();
        return false;
    }
    return true;
}

function GotoStep4() {

    /*
     * else if (frmProviderAccreditation.txtContactTel.value == "") { msg =
     * "Please specify a telephone number"; alert(msg);
     * frmProviderAccreditation.txtContactTel.focus(); return false; }else if
     * (frmProviderAccreditation.txtContactCell.value == "") { msg = "Please
     * specify a Cell no"; alert(msg);
     * frmProviderAccreditation.txtContactCell.focus(); return false; } else if
     * (frmProviderAccreditation.cboQualification.value == "") { msg = "Please
     * select a Qualification"; alert(msg);
     * frmProviderAccreditation.cboQualification.focus(); return false; }else if
     * (frmProviderAccreditation.cboSkill.value == "") { msg = "Please select a
     * Skill Program"; alert(msg); frmProviderAccreditation.cboSkill.focus();
     * return false; }
     */
    // Added these validations because each Qualification should have assessor &
    // moderator
    // if (ass_count < qual_count)
    // {
    // alert('Please add assessor! Number of selected Qualifications and number
    // of selected Assessors should be same.');
    // return false;
    // }else if (ass_count > qual_count)
    // {
    // alert('Please remove assessor! Number of selected Qualifications and
    // number of selected Assessors should be same.');
    // return false;
    // }else if (mod_count < qual_count)
    // {
    // alert('Please add moderator! Number of selected Qualifications and number
    // of selected Moderators should be same.');
    // return false;
    // }else if (mod_count > qual_count)
    // {
    // alert('Please remove moderator! Number of selected Qualifications and
    // number of selected Moderators should be same.');
    // return false;
    // }
    if ($("#assessor").val() == null || $("#assessor").val() == undefined) {
        msg = "Please Add Assessor";
        $("#assessor").focus();
        alert(msg);
        return false;
    }
    //check if file has been attached to accessor
    var accessor_file_evals = $(".field_wrapper_assessor :file[required]");
    for (var i = 0; i < accessor_file_evals.length; i++) {
        if (accessor_file_evals[i].value == '' || accessor_file_evals[i].value == undefined) {
            alert("Please Upload Appoinment Letter/SLA to Assessor");
            accessor_file_evals[i].focus();
            accessor_file_evals[i].style.border = "medium solid red";
            return false;
        }
    } //end of for loop

    //check if file has been attached to accessor
    var accessor_notification_file_evals = $(".field_wrapper_assessor_notification_letter :file[required]");
    for (var i = 0; i < accessor_notification_file_evals.length; i++) {
        if (accessor_notification_file_evals[i].value == '' || accessor_notification_file_evals[i].value == undefined) {
            alert("Please Upload Notification Letter to Assessor");
            accessor_notification_file_evals[i].focus();
            accessor_notification_file_evals[i].style.border = "medium solid red";
            return false;
        }
    } //end of for loop

    if ($("#moderator").val() == null || $("#moderator").val() == undefined) {
        msg = "Please Add Moderator";
        $("#moderator").focus();
        alert(msg);
        return false;
    }

    //check if file has been attached to moderator
    var moderator_file_evals = $(".field_wrapper_moderator :file[required]");
    for (var i = 0; i < moderator_file_evals.length; i++) {
        if (moderator_file_evals[i].value == '' || moderator_file_evals[i].value == undefined) {
            alert("Please Upload Appoinment Letter/SLA to Moderator");
            moderator_file_evals[i].focus();
            moderator_file_evals[i].style.border = "medium solid red";
            return false;
        }
    } //end of for loop

    //check if file has been attached to moderator
    var moderator_notification_file_evals = $(".field_wrapper_moderator_notification_letter :file[required]");
    for (var i = 0; i < moderator_notification_file_evals.length; i++) {
        if (moderator_notification_file_evals[i].value == '' || moderator_notification_file_evals[i].value == undefined) {
            alert("Please Upload Notification Letter to Moderator");
            moderator_notification_file_evals[i].focus();
            moderator_notification_file_evals[i].style.border = "medium solid red";
            return false;
        }
    } //end of for loop

    if (frmProviderAccreditation.ciproDocument.value == "") {
        msg = "Please Upload CIPC/DSD Document";
        alert(msg);
        frmProviderAccreditation.ciproDocument.focus();
        return false;
    } else if (frmProviderAccreditation.taxDocument.value == "") {
        msg = "Please Upload Tax Clearance Document";
        alert(msg);
        frmProviderAccreditation.taxDocument.focus();
        return false;
    } else if (frmProviderAccreditation.cvDocument.value == "") {
        msg = "Please Upload Director C.V";
        alert(msg);
        frmProviderAccreditation.cvDocument.focus();
        return false;
    } else if (frmProviderAccreditation.qualificationDocument.value == "") {
        msg = "Please Upload Certified Copies Of Qualifications";
        alert(msg);
        frmProviderAccreditation.qualificationDocument.focus();
        return false;
    } else if (frmProviderAccreditation.lease_agreement.value == "") {
        msg = "Please Upload Proof of Ownership (Utility Bill) or Lease Agreement";
        alert(msg);
        frmProviderAccreditation.lease_agreement.focus();
        return false;
    } else if (frmProviderAccreditation.company_profile_and_organogram.value == "") {
        msg = "Please Upload Company Profile and organogram";
        alert(msg);
        frmProviderAccreditation.company_profile_and_organogram.focus();
        return false;
    } else if (frmProviderAccreditation.quality_management_system.value == "") {
        msg = "Please Upload Quality Management System (QMS)";
        alert(msg);
        frmProviderAccreditation.quality_management_system.focus();
        return false;
    } else if ($("#material").val() == "own_material" &&
        frmProviderAccreditation.provider_learning_material.value == "") {
        msg = "Please Upload Learning Programme Approval Report";
        alert(msg);
        frmProviderAccreditation.provider_learning_material.focus();
        return false;
    } else if ($("#skill").val() &&
        frmProviderAccreditation.skills_programme_registration_letter.value == "") {
        msg = "Please Upload Skills Programme Registration Letter";
        alert(msg);
        frmProviderAccreditation.skills_programme_registration_letter.focus();
        return false;
    } else if (frmProviderAccreditation.workplace_agreement.value == "") {
        msg = "Please Upload Workplace Agreement";
        alert(msg);
        frmProviderAccreditation.workplace_agreement.focus();
        return false;
    }
    return true;
}

function GotoStep10() {
    if (frmProviderAccreditation.txtCmpName.value == "") {
        msg = "Please specify a Campus Name";
        alert(msg);
        frmProviderAccreditation.txtCmpName.focus();
        return false;
    } else if (frmProviderAccreditation.txtCmpEmail.value == "") {
        msg = "Please specify a campus email";
        alert(msg);
        frmProviderAccreditation.txtCmpEmail.focus();
        return false;
    } else if (frmProviderAccreditation.txtCmpPhone.value == "") {
        msg = "Please specify a campus phone";
        alert(msg);
        frmProviderAccreditation.txtCmpPhone.focus();
        return false;
    } else if (frmProviderAccreditation.txtCmpStreet1.value == "") {
        msg = "Please specify a street 1 ";
        alert(msg);
        frmProviderAccreditation.txtCmpStreet1.focus();
        return false;
    } else if (frmProviderAccreditation.txtCmpStreet2.value == "") {
        msg = "Please specify a street 2 ";
        alert(msg);
        frmProviderAccreditation.txtCmpStreet2.focus();
        return false;
    }
    /*
     * else if (frmProviderAccreditation.txtCmpStreet3.value == "") { msg =
     * "Please specify a street 3 "; alert(msg);
     * frmProviderAccreditation.txtCmpStreet3.focus(); return false; }
     */
    else if (frmProviderAccreditation.txtCmpProvince.value == "") {
        msg = "Please select a Province ";
        alert(msg);
        frmProviderAccreditation.txtCmpProvince.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactNameSurname.value == "") {
        msg = "Please specify a contact person name ";
        alert(msg);
        frmProviderAccreditation.txtContactNameSurname.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactSurname.value == "") {
        msg = "Please specify a contact person surname ";
        alert(msg);
        frmProviderAccreditation.txtContactSurname.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactEmail.value == "") {
        msg = "Please specify a contact person email address";
        alert(msg);
        frmProviderAccreditation.txtContactEmail.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactNameSurname.value == "") {
        msg = "Please specify a name";
        alert(msg);
        frmProviderAccreditation.txtContactNameSurname.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactCell.value == "") {
        msg = "Please specify a contact person cell number";
        alert(msg);
        frmProviderAccreditation.txtContactCell.focus();
        return false;
    } else if (frmProviderAccreditation.txtContactTel.value == "") {
        msg = "Please specify a contact person telephone number";
        alert(msg);
        frmProviderAccreditation.txtContactTel.focus();
        return false;
    } else if (frmProviderAccreditation.txtCmpPhone.value != "" &&
        $('#txtCmpPhone').val().length < 10) {
        alert("Campus Phone should be 10 digit")
        $("#txtCmpPhone").focus();
        return false;
    } else if (frmProviderAccreditation.txtFaxNo.value != "" &&
        $('#txtFaxNo').val().length < 10) {
        alert("Campus Fax should be 10 digit")
        $("#txtFaxNo").focus();
        return false;
    } else if (frmProviderAccreditation.txtContactTel.value != "" &&
        $('#txtContactTel').val().length < 10) {
        alert("Telephone Number should be 10 digit")
        $("#txtContactTel").focus();
        return false;
    } else if (frmProviderAccreditation.txtContactCell.value != "" &&
        $('#txtContactCell').val().length < 10) {
        alert("Cell Number should be 10 digit")
        $("#txtContactCell").focus();
        return false;
    } else if (qual_count < 1 && skill_count < 1 && learning_count < 1) {
        alert('Please select atleast one [Qualification/Skills Programme/Learning Programme]');
        return false;
    } else if ((qual_count + skill_count + learning_count) > 3) {
        alert('You can select maximum three [Qualification/Skills Programme/Learning Programme]');
        return false;
    }
    return true;
}

function keyNumerics() {
    if (event.keyCode < 48 || event.keyCode > 57)
        event.returnValue = false;
}

function AddSite() {
    var returnValue = window
        .showModalDialog(
            'IFrame.asp?PageType=AddSite&ReadOnly=&Style=',
            '',
            'dialogWidth:650px; dialogHeight:370px; status:no; help:no; scroll:Yes; center:Yes; resizable:No;');
    if (returnValue != "undefined") {
        frmProviderAccreditation.action = "GeneralSiteInfo.asp?ReadOnly=";
        frmProviderAccreditation.submit();
    }
}

function EditSite(ProviderSiteID) {
    var returnValue = window
        .showModalDialog(
            'IFrame.asp?PageType=UpdateSite&ReadOnly=&Style=&ProviderSiteID=' +
            ProviderSiteID,
            '',
            'dialogWidth:650px; dialogHeight:370px; status:no; help:no; scroll:Yes; center:Yes; resizable:No;');
    if (returnValue != "undefined") {
        frmProviderAccreditation.action = "GeneralSiteInfo.asp?ReadOnly=";
        frmProviderAccreditation.submit();
    }
}

function DeleteSite(ProviderSiteID) {
    frmProviderAccreditation.action = "GeneralSiteInfo.asp?PageType=DeleteProviderSite&ProviderSiteID=" +
        ProviderSiteID;
    frmProviderAccreditation.submit()
}

function GotoStep5() {
    return true;
}

function GotoStep6() {
    /*
     * if (frmProviderAccreditation.txtPhysicalAddressLine1.value == "") { msg =
     * "Please specify a physical address"; alert(msg);
     * frmProviderAccreditation.txtPhysicalAddressLine1.focus(); return false; }
     * else if (frmProviderAccreditation.txtPhysicalAddressLine2.value == "") {
     * msg = "Please specify a physical address"; alert(msg);
     * frmProviderAccreditation.txtPhysicalAddressLine2.focus(); return false; }
     * else if (frmProviderAccreditation.txtPostalAddressLine1.value == "") {
     * msg = "Please specify a postal address"; alert(msg);
     * frmProviderAccreditation.txtPostalAddressLine1.focus(); return false; }
     * else if (frmProviderAccreditation.txtPostalAddressLine2.value == "") {
     * msg = "Please specify a fax number"; alert(msg);
     * frmProviderAccreditation.txtPostalAddressLine2.focus(); return false; }
     */
    return true;
}

function GotoStep7() {
    if (frmProviderAccreditation.campus.value == "") {
        msg = "Please specify campus";
        alert(msg);
        frmProviderAccreditation.campus.focus();
        return false;
    }
    return true;
}

function EnableControls() {
    frmProviderAccreditation.cboSETA.disabled = false;
    frmProviderAccreditation.optAccStatus[0].disabled = false;
    frmProviderAccreditation.optAccStatus[1].disabled = false;
    frmProviderAccreditation.optAccStatus[2].disabled = false;
    frmProviderAccreditation.optAccStatus[3].disabled = false;
    frmProviderAccreditation.AppliedToAnotherSETA.value = 1;
}

function DisableControls() {
    frmProviderAccreditation.cboSETA.disabled = true;
    frmProviderAccreditation.optAccStatus[0].disabled = true;
    frmProviderAccreditation.optAccStatus[1].disabled = true;
    frmProviderAccreditation.optAccStatus[2].disabled = true;
    frmProviderAccreditation.optAccStatus[3].disabled = true;
    frmProviderAccreditation.optStatusReason[0].disabled = true;
    frmProviderAccreditation.optStatusReason[1].disabled = true;
    frmProviderAccreditation.optStatusReason[2].disabled = true;
    frmProviderAccreditation.optStatusReason[3].disabled = true;
    frmProviderAccreditation.txtAccStartDate.disabled = true;
    frmProviderAccreditation.txtAccEndDate.disabled = true;
    frmProviderAccreditation.AppliedToAnotherSETA.value = 0;
}

function EnableStatusReason() {
    frmProviderAccreditation.optStatusReason[0].disabled = false;
    frmProviderAccreditation.optStatusReason[1].disabled = false;
    frmProviderAccreditation.optStatusReason[2].disabled = false;
    frmProviderAccreditation.optStatusReason[3].disabled = false;
    frmProviderAccreditation.txtAccStartDate.disabled = true;
    frmProviderAccreditation.txtAccEndDate.disabled = true;
}

function DisableStatusReason() {
    frmProviderAccreditation.optStatusReason[0].disabled = true;
    frmProviderAccreditation.optStatusReason[1].disabled = true;
    frmProviderAccreditation.optStatusReason[2].disabled = true;
    frmProviderAccreditation.optStatusReason[3].disabled = true;
    frmProviderAccreditation.txtAccStartDate.disabled = true;
    frmProviderAccreditation.txtAccEndDate.disabled = true;
}

function EnableAccDates() {
    frmProviderAccreditation.txtAccStartDate.disabled = false;
    frmProviderAccreditation.txtAccEndDate.disabled = false;
}

$(document).ready(function() {

    //Added by shoaib
    $("#cboOrgSICCode").selectize();

    $('input[type=radio][name=radio_terms]').change(function() {
        if (this.value == 'agree') {
            $("#next1").show();
        } else if (this.value == 'notagree') {
            $("#next1").hide();
        }
    });
});

$(function() {
    $("#dialog-message-accreditation").dialog({
        autoOpen: false,
        modal: true,
        closeOnEscape: false,
        hideCloseButton: false,

        buttons: {
            Ok: function() {
                $(this).dialog("close");
                // $('#frmProviderAccreditation').unbind('submit').submit();
            }
        },
        open: function(event, ui) {
            jQuery('.ui-dialog-titlebar-close').hide();
        }
    });

});

function GotoStep2Part1() {

    if ($('#already_register').prop('checked')) {
        if (document.frmProviderAccreditation.accreditation_number.value == "") {
            document.frmProviderAccreditation.accreditation_number.focus();
            alert("Please Enter the Accredidation Number");
            return false;
        }
    } else {
        var terms = $('input[name=radio_terms]:checked',
            '#frmProviderAccreditation').val()
        if (terms == 'notagree') {
            alert("Please Check Terms and Conditions");
            $("#agree").focus();
            return false;
        } else if (terms == 'agree') {
            return true;
        }
    }
    return true;
}
$(function() {
    $("#accordian").accordion({
        collapsible: true,
        heightStyle: "content"
    });

    $("#dialog-warning-assessor").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            Ok: function() {
                $(this).dialog("close");
                document.frmProviderAccreditation.assessor_number.focus();
            }
        }
    });
    $("#dialog-warning-moderator").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            Ok: function() {
                $(this).dialog("close");
                document.frmProviderAccreditation.moderator_number.focus();
            }
        }
    });
    // Added by vishwas for get assessor for main campus
    var array_assessor = [];
    $("#add_assessor")
        .on(
            'click',
            function() {
                var wrapper = $('.field_wrapper_assessor');
                var wrapper_2 = $('.field_wrapper_assessor_notification_letter');
                if (frmProviderAccreditation.assessor_number.value !== "") {
                    var assessor_no = frmProviderAccreditation.assessor_number.value
                    var count = 0
                    $
                        .when(
                            $("#assessor option:selected")
                            .each(
                                function(key, value) {
                                    array_assessor
                                        .push(value.text
                                            .split('-')[0]);
                                }))
                        .done(
                            function() {
                                if ($
                                    .inArray(
                                        frmProviderAccreditation.assessor_number.value,
                                        array_assessor) !== -1) {
                                    alert("Please Enter Unique Assessor Number!!!");
                                    frmProviderAccreditation.assessor_number.value = "";
                                    array_assessor = []
                                    return false;
                                } else {

                                    var qualification_ids = ""
                                    $(
                                            ".provider_qualification .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                qualification_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    var skill_ids = ""
                                    $(
                                            ".provider_skill .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                skill_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    var lp_ids = ""
                                    $(
                                            ".learning_skill .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                lp_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    $
                                        .ajax({
                                            url: "/page/check_assessor_number",
                                            type: "post",
                                            dataType: "json",
                                            async: true,
                                            data: {
                                                'assessor_no': assessor_no,
                                                'qualification': qualification_ids,
                                                'skill': skill_ids,
                                                'learning_programme': lp_ids
                                            },
                                            success: function(
                                                result) {
                                                if (result.length > 0) {
                                                    var oOption = document
                                                        .createElement("OPTION");
                                                    oOption.text = result[0].assessor_seq_no +
                                                        '->' +
                                                        result[0].display_name;
                                                    oOption.value = result[0].id;
                                                    oOption.selected = true;
                                                    frmProviderAccreditation.cboAssessor
                                                        .add(oOption);
                                                    // ass_count
                                                    // ++ ;
                                                    frmProviderAccreditation.assessor_number.value = "";
                                                    // agreement
                                                    // upload
                                                    // for
                                                    // assessor
                                                    var fieldHTML = '<div><input id="ID_' +
                                                        result[0].id +
                                                        '_assessor_agreement" type="file" name="ID_' +
                                                        result[0].id +
                                                        '_assessor_agreement" value="" required="required" /></div>';
                                                    var fieldHTML_2 = '<div><input id="ID_' +
                                                        result[0].id +
                                                        '_assessor_notification" type="file" name="ID_' +
                                                        result[0].id +
                                                        '_assessor_notification" value="" required="required"/></div>';
                                                    $(
                                                            wrapper)
                                                        .append(
                                                            fieldHTML);
                                                    $(
                                                            wrapper_2)
                                                        .append(
                                                            fieldHTML_2);
                                                }
                                                if (result.length == 0) {
                                                    $(
                                                            '#dialog-warning-assessor')
                                                        .empty();
                                                    $(
                                                            "#dialog-warning-assessor")
                                                        .append(
                                                            "<p>Please Enter Valid Assessor Number. This Assessor is not Linked with selected Qualifications.</p>");
                                                    $(
                                                            "#dialog-warning-assessor")
                                                        .dialog(
                                                            "open");
                                                }
                                            },
                                        });
                                }
                            })
                }
            });
    $("#remove_assessor")
        .on(
            'click',
            function() {
                $(".field_wrapper_assessor div input[type=file]")
                    .each(
                        function(index, value) {
                            var id = $(this).attr('id');
                            var key = id.split('_');
                            if (parseInt($(
                                        "#frmProviderAccreditation #assessor option:selected")
                                    .val()) == parseInt(key[1])) {
                                // ass_count -- ;
                                $(
                                        'div #ID_' +
                                        key[1] +
                                        '_assessor_agreement')
                                    .remove();
                                $(
                                        'div #ID_' +
                                        key[1] +
                                        '_assessor_notification')
                                    .remove();
                            }
                        });
                if (frmProviderAccreditation.cboAssessor.selectedIndex != -1) {
                    frmProviderAccreditation.cboAssessor
                        .remove(frmProviderAccreditation.cboAssessor.selectedIndex);
                }
            });
    // Added by vishwas for get moderator for main campus
    var array_moderator = [];
    $("#add_moderator")
        .on(
            'click',
            function() {
                var wrapper = $('.field_wrapper_moderator');
                var wrapper_2 = $('.field_wrapper_moderator_notification_letter');

                if (frmProviderAccreditation.moderator_number.value !== "") {
                    var moderator_no = frmProviderAccreditation.moderator_number.value

                    $
                        .when(
                            $("#moderator option:selected")
                            .each(
                                function(key, value) {
                                    array_moderator
                                        .push(value.text
                                            .split('-')[0]);
                                }))
                        .done(
                            function() {
                                if ($
                                    .inArray(
                                        frmProviderAccreditation.moderator_number.value,
                                        array_moderator) !== -1) {
                                    alert("Please Enter Unique Moderator Number!!!");
                                    frmProviderAccreditation.moderator_number.value = "";
                                    array_moderator = []
                                    return false;
                                } else {

                                    var qualification_ids = ""
                                    $(
                                            ".provider_qualification .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                qualification_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    var skill_ids = ""
                                    $(
                                            ".provider_skill .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                skill_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    var lp_ids = ""
                                    $(
                                            ".learning_skill .fs-options .fs-option.selected")
                                        .each(
                                            function() {
                                                lp_ids += parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) +
                                                    ' '
                                            });
                                    $
                                        .ajax({
                                            url: "/page/check_moderator_number",
                                            type: "post",
                                            dataType: "json",
                                            async: true,
                                            data: {
                                                'moderator_no': moderator_no,
                                                'qualification': qualification_ids,
                                                'skill': skill_ids,
                                                'learning_programme': lp_ids,
                                            },
                                            success: function(
                                                result) {
                                                if (result.length > 0) {
                                                    var oOption = document
                                                        .createElement("OPTION");
                                                    oOption.text = result[0].moderator_seq_no +
                                                        '->' +
                                                        result[0].display_name;
                                                    oOption.value = result[0].id;
                                                    oOption.selected = true;
                                                    frmProviderAccreditation.cboModerator
                                                        .add(oOption);
                                                    // mod_count
                                                    // ++ ;
                                                    frmProviderAccreditation.moderator_number.value = "";
                                                    // agreement
                                                    // upload
                                                    // for
                                                    // moderator
                                                    var fieldHTML = '<div><input id="ID_' +
                                                        result[0].id +
                                                        '_moderator_agreement" type="file" name="ID_' +
                                                        result[0].id +
                                                        '_moderator_agreement" value="" required="required"/></div>';
                                                    var fieldHTML_2 = '<div><input id="ID_' +
                                                        result[0].id +
                                                        '_moderator_notification" type="file" name="ID_' +
                                                        result[0].id +
                                                        '_moderator_notification" value="" required="required"/></div>';
                                                    $(
                                                            wrapper)
                                                        .append(
                                                            fieldHTML);
                                                    $(
                                                            wrapper_2)
                                                        .append(
                                                            fieldHTML_2);

                                                }
                                                if (result.length == 0) {
                                                    $(
                                                            '#dialog-warning-moderator')
                                                        .empty();
                                                    $(
                                                            "#dialog-warning-moderator")
                                                        .append(
                                                            "<p>Please Enter Valid Moderator Number. This Moderator is not Linked with selected Qualifications/Skills Programme/Learning Programme.</p>");
                                                    $(
                                                            "#dialog-warning-moderator")
                                                        .dialog(
                                                            "open");
                                                }
                                            },
                                        });
                                }
                            })
                }
            });
    $("#remove_moderator")
        .on(
            'click',
            function() {
                $(".field_wrapper_moderator div input[type=file]")
                    .each(
                        function(index, value) {
                            var id = $(this).attr('id');
                            var key = id.split('_');
                            if (parseInt($(
                                        "#frmProviderAccreditation #moderator option:selected")
                                    .val()) == parseInt(key[1])) {
                                // mod_count -- ;
                                $(
                                        'div #ID_' +
                                        key[1] +
                                        '_moderator_agreement')
                                    .remove();
                                $(
                                        'div #ID_' +
                                        key[1] +
                                        '_moderator_notification')
                                    .remove();
                            }
                        });

                if (frmProviderAccreditation.cboModerator.selectedIndex != -1) {
                    frmProviderAccreditation.cboModerator
                        .remove(frmProviderAccreditation.cboModerator.selectedIndex);
                }
            });

    $('.campus_add_assessor')
        .live(
            'click',
            function() {
                var id = $(this).attr("id");
                var key = id.split('_');
                var assessor_number = $(
                    '#' + key[0] + '_campus_assessor_number').val();
                var wrapper = $('#' + key[0] +
                    '_campus_wrapper_assessor');

                var qualification_ids = ""
                $(
                        ".campus_qualification .fs-options .fs-option.selected")
                    .each(
                        function() {
                            qualification_ids += parseInt($(
                                    this).attr('data-value')) +
                                ' '
                        });
                var skill_ids = ""
                $(".campus_skills .fs-options .fs-option.selected")
                    .each(
                        function() {
                            skill_ids += parseInt($(this).attr(
                                    'data-value')) +
                                ' '
                        });
                var lp_ids = ""
                $(".campus_learning .fs-options .fs-option.selected")
                    .each(
                        function() {
                            lp_ids += parseInt($(this).attr(
                                    'data-value')) +
                                ' '
                        });
                $
                    .ajax({
                        url: "/page/check_assessor_number",
                        type: "post",
                        dataType: "json",
                        async: true,
                        data: {
                            'assessor_no': assessor_number,
                            'qualification': qualification_ids,
                            'skill': skill_ids,
                            'learning_programme': lp_ids
                        },
                        success: function(result) {
                            if (result.length > 0) {
                                var oOption = document
                                    .createElement("OPTION");
                                oOption.text = assessor_number +
                                    '->' +
                                    result[0].display_name;
                                oOption.value = result[0].id;
                                oOption.selected = true;
                                $(
                                        '#frmProviderAccreditation #' +
                                        key[0] +
                                        '_campusassessor')
                                    .append(oOption)
                                $(
                                        '#' +
                                        key[0] +
                                        '_campus_assessor_number')
                                    .val('');
                                // agreement upload for campus
                                // assessor
                                var fieldHTML = '<div><input id="ID_' +
                                    result[0].id +
                                    '_assessor_agreement_campus_' +
                                    key[0] +
                                    '" type="file" name="ID_' +
                                    result[0].id +
                                    '_assessor_agreement_campus_' +
                                    key[0] +
                                    '" value="" /></div>';
                                $(wrapper).append(fieldHTML);

                            }
                            if (result.length == 0) {
                                $('#dialog-warning-assessor')
                                    .empty();
                                $("#dialog-warning-assessor")
                                    .append(
                                        "<p>Please Enter Valid Assessor Number. This Assessor is not Linked with selected Qualifications/Skills Programme/Learning Programme.</p>");
                                $("#dialog-warning-assessor")
                                    .dialog("open");
                            }
                        },
                    });
            });

    $(".campus_remove_assessor")
        .live(
            'click',
            function() {
                var id = $(this).attr("id");
                var key = id.split('_');
                $(
                        "#" +
                        key[0] +
                        "_campus_wrapper_assessor div input[type=file]")
                    .each(
                        function(index, value) {
                            var campus_id = $(this).attr('id');
                            var campus_key = campus_id
                                .split('_');
                            if (parseInt($(
                                        "#frmProviderAccreditation #" +
                                        key[0] +
                                        "_campusassessor option:selected")
                                    .val()) == parseInt(campus_key[1])) {
                                $(
                                        'div #ID_' +
                                        campus_key[1] +
                                        '_assessor_agreement_campus_' +
                                        key[0] + '')
                                    .remove();
                            }
                        });
                if ($('#frmProviderAccreditation #' + key[0] +
                        '_campusassessor').selectedIndex != -1) {
                    $(
                        '#frmProviderAccreditation #' +
                        key[0] +
                        '_campusassessor option[value=' +
                        $(
                            "#frmProviderAccreditation #" +
                            key[0] +
                            "_campusassessor option:selected")
                        .val() + ']').remove();
                }
            });

    $('.campus_add_moderator')
        .live(
            'click',
            function() {
                var id = $(this).attr("id");
                var key = id.split('_');
                var moderator_number = $(
                        '#' + key[0] + '_campus_moderator_number')
                    .val();
                var wrapper = $('#' + key[0] +
                    '_campus_wrapper_moderator');

                var qualification_ids = ""
                $(
                        ".campus_qualification .fs-options .fs-option.selected")
                    .each(
                        function() {
                            qualification_ids += parseInt($(
                                    this).attr('data-value')) +
                                ' '
                        });
                var skill_ids = ""
                $(".campus_skills .fs-options .fs-option.selected")
                    .each(
                        function() {
                            skill_ids += parseInt($(this).attr(
                                    'data-value')) +
                                ' '
                        });
                var lp_ids = ""
                $(".campus_learning .fs-options .fs-option.selected")
                    .each(
                        function() {
                            lp_ids += parseInt($(this).attr(
                                    'data-value')) +
                                ' '
                        });
                $
                    .ajax({
                        url: "/page/check_moderator_number",
                        type: "post",
                        dataType: "json",
                        async: true,
                        data: {
                            'moderator_no': moderator_number,
                            'qualification': qualification_ids,
                            'skill': skill_ids,
                            'learning_programme': lp_ids
                        },
                        success: function(result) {
                            if (result.length > 0) {
                                var oOption = document
                                    .createElement("OPTION");
                                oOption.text = moderator_number +
                                    '->' +
                                    result[0].display_name;
                                oOption.value = result[0].id;
                                oOption.selected = true;
                                $(
                                        '#frmProviderAccreditation #' +
                                        key[0] +
                                        '_campusmoderator')
                                    .append(oOption)
                                $(
                                        '#' +
                                        key[0] +
                                        '_campus_moderator_number')
                                    .val('');
                                // agreement upload for campus
                                // assessor
                                var fieldHTML = '<div><input id="ID_' +
                                    result[0].id +
                                    '_moderator_agreement_campus_' +
                                    key[0] +
                                    '" type="file" name="ID_' +
                                    result[0].id +
                                    '_moderator_agreement_campus_' +
                                    key[0] +
                                    '" value="" /></div>';
                                $(wrapper).append(fieldHTML);
                            }
                            if (result.length == 0) {
                                $('#dialog-warning-moderator')
                                    .empty();
                                $("#dialog-warning-moderator")
                                    .append(
                                        "<p>Please Enter Valid Moderator Number. This Moderator is not Linked with selected Qualifications/Skills Programme/Learning Programme.</p>");
                                $("#dialog-warning-moderator")
                                    .dialog("open");
                            }
                        },
                    });
            });

    $(".campus_remove_moderator")
        .live(
            'click',
            function() {
                var id = $(this).attr("id");
                var key = id.split('_');
                $(
                        "#" +
                        key[0] +
                        "_campus_wrapper_moderator div input[type=file]")
                    .each(
                        function(index, value) {
                            var campus_id = $(this).attr('id');
                            var campus_key = campus_id
                                .split('_');
                            if (parseInt($(
                                        "#frmProviderAccreditation #" +
                                        key[0] +
                                        "_campusmoderator option:selected")
                                    .val()) == parseInt(campus_key[1])) {
                                $(
                                        'div #ID_' +
                                        campus_key[1] +
                                        '_moderator_agreement_campus_' +
                                        key[0] + '')
                                    .remove();
                            }
                        });
                if ($('#frmProviderAccreditation #' + key[0] +
                        '_campusmoderator').selectedIndex != -1) {
                    $(
                        '#frmProviderAccreditation #' +
                        key[0] +
                        '_campusmoderator option[value=' +
                        $(
                            "#frmProviderAccreditation #" +
                            key[0] +
                            "_campusmoderator option:selected")
                        .val() + ']').remove();
                }
            });

});

$(document)
    .ready(
        function() {
            $("#SETA").hide();
            $("#SETA_label").hide();
            $("#doc_row").hide();

            // readonly check box
            function readOnlyCheckBox() {
                return false;
            }

            $('input:radio[name="optYesNo"]').change(
                function() {
                    if ($(this).is(':checked') &&
                        $(this).val() == 'yes') {
                        $("#SETA").show();
                        $("#SETA_label").show();
                        $("#doc_row").show();

                    } else if ($(this).is(':checked') &&
                        $(this).val() == 'no') {
                        $("#SETA").hide();
                        $("#SETA_label").hide();
                        $("#doc_row").hide();
                    }
                });

            // load province on the basis of country
            $('#txtCmpCountry')
                .on(
                    'change',
                    function() {
                        var country = $(
                                "#txtCmpCountry option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_province",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'country': country
                                },
                                success: function(result) {
                                    $('#txtCmpProvince')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Province --</option>');
                                    $(
                                            '#frmProviderAccreditation #city')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#frmProviderAccreditation #txtSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtCmpZip").val('');
                                    if (result.length > 0) {
                                        var workprovince = $("#txtCmpProvince");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    workprovince
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });

            $("#txtSDLNo")
                .change(
                    function() {
                        var sdl_number = $("#txtSDLNo").val();
                        $
                            .ajax({
                                url: "/page/check_sdlnumber",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'sdl_number': sdl_number
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        if (result[0].result == 1) {
                                            $('#txtSDLNo')
                                                .val('');
                                            alert("Provider Already Register for this SDL Number");
                                            $('#txtSDLNo')
                                                .focus();
                                        }
                                    }
                                },
                            });
                    });

            $("#txtVATRegNo")
                .change(
                    function() {
                        var vat_registration_no = $(
                            "#txtVATRegNo").val();
                        $
                            .ajax({
                                url: "/page/check_vat_registartion_no",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'vat_registration_no': vat_registration_no
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        if (result[0].result == 1) {
                                            $(
                                                    '#txtVATRegNo')
                                                .val('');
                                            alert("Provider Already Register for this VAT Registration Number");
                                            $(
                                                    '#txtVATRegNo')
                                                .focus();
                                        }
                                    }
                                },
                            });
                    });

            //					$("#cboOrgSICCode").change(function() {
            //						var cboOrgSICCode = $("#cboOrgSICCode").val();
            //						$.ajax({
            //							url : "/load_sic_code",
            //							type : "post",
            //							dataType : "json",
            //							async : false,
            //							data : {
            //								'sic_code' : cboOrgSICCode
            //							},
            //							success : function(result) {
            //								if (result.length > 0) {
            //									$("#empl_sic_code_id").val(result[0].code)
            //								}
            //							},
            //						});
            //					});
            //					$("#empl_sic_code_id").change(function() {
            //						var cboOrgSICCode = $("#empl_sic_code_id").val();
            //						$.ajax({
            //							url : "/load_sic_description",
            //							type : "post",
            //							dataType : "json",
            //							async : false,
            //							data : {
            //								'sic_code' : cboOrgSICCode
            //							},
            //							success : function(result) {
            //								if (result.length > 0) {
            //									$("#cboOrgSICCode").val(result[0].id)
            //								}
            //							},
            //						});
            //					});

            $("#txtCmpEmail")
                .change(
                    function() {

                        var email = $("#txtCmpEmail").val()
                        $
                            .ajax({
                                url: "/page/check_email_id",
                                type: "post",
                                dataType: "json",
                                async: true,
                                data: {
                                    'email': email
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        console
                                            .log(
                                                "111",
                                                result[0].result);
                                        if (result[0].result == 2) {
                                            $(
                                                    '#txtCmpEmail')
                                                .val('');
                                            alert("Please enter valid Email ID");
                                            $(
                                                    '#txtCmpEmail')
                                                .focus();
                                        } else if (result[0].result == 1) {
                                            $(
                                                    '#txtCmpEmail')
                                                .val('');
                                            alert("Provider Already Register for this Email ID ");
                                            $(
                                                    '#txtCmpEmail')
                                                .focus();
                                        }
                                    }
                                },
                            });
                    })

            // validation for provider contact email id
            $("#txtContactEmail")
                .change(
                    function() {

                        var email = $("#txtContactEmail").val()
                        $
                            .ajax({
                                url: "/page/check_email_id",
                                type: "post",
                                dataType: "json",
                                async: true,
                                data: {
                                    'email': email
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        console
                                            .log(
                                                "111",
                                                result[0].result);
                                        if (result[0].result == 2) {
                                            $(
                                                    '#txtContactEmail')
                                                .val('');
                                            alert("Please enter valid Contact Email ID");
                                            $(
                                                    '#txtContactEmail')
                                                .focus();
                                        }
                                    }
                                },
                            });
                    })

            // load city on the basis of province
            $('#txtCmpProvince')
                .on(
                    'change',
                    function() {
                        var province = $(
                                "#txtCmpProvince option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_city",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'province': province
                                },
                                success: function(result) {
                                    $(
                                            '#frmProviderAccreditation #city')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#frmProviderAccreditation #txtSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtCmpZip").val('');
                                    if (result.length > 0) {
                                        var workcity = $("#city");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    // workcity
                                                    // .append('<option
                                                    // value='
                                                    // +
                                                    // value['id']
                                                    // +
                                                    // '>'
                                                    // +
                                                    // value['name']
                                                    // +
                                                    // '('
                                                    // +
                                                    // value['region']
                                                    // +
                                                    // ')'
                                                    // +
                                                    // '</option>');
                                                    workcity
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });

                    });

            // load suburb on the basis of city
            $('#frmProviderAccreditation #city')
                .on(
                    'change',
                    function() {
                        var city = $("#city option:selected")
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_suburb",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'city': city
                                },
                                success: function(result) {
                                    $(
                                            '#frmProviderAccreditation #txtSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtCmpZip").val('');
                                    if (result.length > 0) {
                                        var worksuburb = $("#txtSuburb");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    worksuburb
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });
            $('#frmProviderAccreditation #txtSuburb').on(
                'change',
                function() {
                    var suburb = $("#txtSuburb option:selected")
                        .attr('value');

                    $.ajax({
                        url: "/page/get_locality",
                        type: "post",
                        dataType: "json",
                        async: false,
                        data: {
                            'suburb': suburb
                        },
                        success: function(result) {
                            if (result.length > 0) {
                                $('#txtCmpZip').val(
                                    result[0].postal_code);
                            }
                        },
                    });
                });

            // Physical load province on the basis of country
            $('#txtPhysicalCountry')
                .on(
                    'change',
                    function() {
                        var country = $(
                                "#txtPhysicalCountry option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_province",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'country': country
                                },
                                success: function(result) {
                                    $(
                                            '#txtPhysicalProvince')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Province --</option>');
                                    $('#txtPhysicalCity')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $('#txtPhysicalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtPhysicalZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var physicalprovince = $("#txtPhysicalProvince");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    physicalprovince
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });

            // Physical load city on the basis of province
            $('#txtPhysicalProvince')
                .on(
                    'change',
                    function() {
                        var province = $(
                                "#txtPhysicalProvince option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_city",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'province': province
                                },
                                success: function(result) {
                                    $('#txtPhysicalCity')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $('#txtPhysicalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtPhysicalZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var physicalcity = $("#txtPhysicalCity");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    // physicalcity
                                                    // .append('<option
                                                    // value='
                                                    // +
                                                    // value['id']
                                                    // +
                                                    // '>'
                                                    // +
                                                    // value['name']
                                                    // +
                                                    // '('
                                                    // +
                                                    // value['region']
                                                    // +
                                                    // ')'
                                                    // +
                                                    // '</option>');
                                                    physicalcity
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');

                                                });
                                    }
                                },
                            });

                    });

            // Physical load suburb on the basis of city
            $('#txtPhysicalCity')
                .on(
                    'change',
                    function() {
                        var city = $(
                                "#txtPhysicalCity option:selected")
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_suburb",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'city': city
                                },
                                success: function(result) {
                                    $('#txtPhysicalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $("#txtPhysicalZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var physicalsuburb = $("#txtPhysicalSuburb");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    physicalsuburb
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });
            // Physical load Zip on the basis of city
            $('#txtPhysicalSuburb').on(
                'change',
                function() {
                    var suburb = $(
                            "#txtPhysicalSuburb option:selected")
                        .attr('value');

                    $.ajax({
                        url: "/page/get_locality",
                        type: "post",
                        dataType: "json",
                        async: false,
                        data: {
                            'suburb': suburb
                        },
                        success: function(result) {
                            if (result.length > 0) {
                                $('#txtPhysicalZip').val(
                                    result[0].postal_code);
                            }
                        },
                    });
                });

            // Postal load province on the basis of country
            $('#txtPostalAddressCountry')
                .on(
                    'change',
                    function() {
                        var country = $(
                                "#txtPostalAddressCountry option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_province",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'country': country
                                },
                                success: function(result) {
                                    $(
                                            '#txtPostalAddressProvince')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Province --</option>');
                                    $(
                                            '#txtPostalAddressCity')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#frmProviderAccreditation #txtPostalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $(
                                            "#txtPostalAddressZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var postprovince = $("#txtPostalAddressProvince");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    postprovince
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });

            // Postal load city on the basis of province
            $('#txtPostalAddressProvince')
                .on(
                    'change',
                    function() {
                        var province = $(
                                "#txtPostalAddressProvince option:selected")
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_city",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'province': province
                                },
                                success: function(result) {
                                    $(
                                            '#txtPostalAddressCity')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#frmProviderAccreditation #txtPostalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $(
                                            "#txtPostalAddressZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var postcity = $("#txtPostalAddressCity");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    // postcity
                                                    // .append('<option
                                                    // value='
                                                    // +
                                                    // value['id']
                                                    // +
                                                    // '>'
                                                    // +
                                                    // value['name']
                                                    // +
                                                    // '('
                                                    // +
                                                    // value['region']
                                                    // +
                                                    // ')'
                                                    // +
                                                    // '</option>');
                                                    postcity
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });

                    });

            // Postal load suburb on the basis of city
            $('#txtPostalAddressCity')
                .on(
                    'change',
                    function() {
                        var city = $(
                                "#txtPostalAddressCity option:selected")
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_suburb",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'city': city
                                },
                                success: function(result) {
                                    $(
                                            '#frmProviderAccreditation #txtPostalSuburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $(
                                            "#txtPostalAddressZip")
                                        .val('');
                                    if (result.length > 0) {
                                        var postsuburb = $("#frmProviderAccreditation #txtPostalSuburb");
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    postsuburb
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });
            // Postal load Zip on the basis of city
            $('#frmProviderAccreditation #txtPostalSuburb')
                .on(
                    'change',
                    function() {
                        var suburb = $(
                                "#frmProviderAccreditation #txtPostalSuburb option:selected")
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_locality",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'suburb': suburb
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        $(
                                                '#txtPostalAddressZip')
                                            .val(
                                                result[0].postal_code);
                                    }
                                },
                            });
                    });

            // set default country as South Africa
            $('#txtCmpCountry option:contains("South Africa")').prop(
                'selected', true).trigger('change');
            $('#txtPhysicalCountry option:contains("South Africa")')
                .prop('selected', true).trigger('change');
            $(
                    '#txtPostalAddressCountry option:contains("South Africa")')
                .prop('selected', true).trigger('change');

            /*
             * // changes in locality $('#frmProviderAccreditation
             * #txtSuburb').on('change', function() { var
             * suburb=$("#frmProviderAccreditation #txtSuburb
             * option:selected" ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'suburb':suburb},
             * success: function(result){ if (result.length>0) {
             * $('#txtCmpCountry option[value=' + result[0].country +
             * ']').attr('selected',true); $('#txtCmpProvince
             * option[value=' + result[0].province +
             * ']').attr('selected',true); $('#frmProviderAccreditation
             * #city option[value=' + result[0].city +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#txtCmpProvince').on('change', function() { var
             * province=$("#txtCmpProvince option:selected"
             * ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false,
             * data:{'province':province}, success: function(result){ if
             * (result.length>0) { $('#txtCmpCountry option[value=' +
             * result[0].country + ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#frmProviderAccreditation #city').on('change',
             * function() { var city=$("#frmProviderAccreditation #city
             * option:selected" ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'city':city},
             * success: function(result){ if (result.length>0) {
             * $('#txtCmpCountry option[value=' + result[0].country +
             * ']').attr('selected',true); $('#txtCmpProvince
             * option[value=' + result[0].province +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * //for home address
             * 
             * $('#txtPhysicalSuburb').on('change', function() { var
             * suburb=$("#txtPhysicalSuburb option:selected"
             * ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'suburb':suburb},
             * success: function(result){ if (result.length>0) {
             * $('#txtPhysicalCountry option[value=' + result[0].country +
             * ']').attr('selected',true); $('#txtPhysicalProvince
             * option[value=' + result[0].province +
             * ']').attr('selected',true); $('#txtPhysicalCity
             * option[value=' + result[0].city +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#txtPhysicalProvince').on('change', function() { var
             * province=$("#txtPhysicalProvince option:selected"
             * ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false,
             * data:{'province':province}, success: function(result){ if
             * (result.length>0) { $('#txtPhysicalCountry option[value=' +
             * result[0].country + ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#txtPhysicalCity').on('change', function() { var
             * city=$("#txtPhysicalCity option:selected"
             * ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'city':city},
             * success: function(result){ if (result.length>0) {
             * $('#txtPhysicalCountry option[value=' + result[0].country +
             * ']').attr('selected',true); $('#txtPhysicalProvince
             * option[value=' + result[0].province +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * //for postal address
             * 
             * $('#frmProviderAccreditation
             * #txtPostalSuburb').on('change', function() { var
             * suburb=$("#frmProviderAccreditation #txtPostalSuburb
             * option:selected" ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'suburb':suburb},
             * success: function(result){ if (result.length>0) {
             * $('#txtPostalAddressCountry option[value=' +
             * result[0].country + ']').attr('selected',true);
             * $('#txtPostalAddressProvince option[value=' +
             * result[0].province + ']').attr('selected',true);
             * $('#txtPostalAddressCity option[value=' + result[0].city +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#txtPostalAddressProvince').on('change', function() {
             * var province=$("#txtPostalAddressProvince
             * option:selected" ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false,
             * data:{'province':province}, success: function(result){ if
             * (result.length>0) { $('#txtPostalAddressCountry
             * option[value=' + result[0].country +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('#txtPostalAddressCity').on('change', function() { var
             * city=$("#txtPostalAddressCity option:selected"
             * ).attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'city':city},
             * success: function(result){ if (result.length>0) {
             * $('#txtPostalAddressCountry option[value=' +
             * result[0].country + ']').attr('selected',true);
             * $('#txtPostalAddressProvince option[value=' +
             * result[0].province + ']').attr('selected',true); } }, });
             * 
             * });
             */

            // for satellite campus address
            /*
             * $('.suburb').live('change', function() { var id =
             * $(this).attr("id"); var key=id.split('_'); var
             * suburb=$('#'+ key[0]+ '_suburb
             * option:selected').attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'suburb':suburb},
             * success: function(result){ if (result.length>0) { $('#'+
             * key[0] + '_country option[value=' + result[0].country +
             * ']').attr('selected',true); $('#'+ key[0] + '_province
             * option[value=' + result[0].province +
             * ']').attr('selected',true); $('#'+ key[0] + '_city
             * option[value=' + result[0].city +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('.province').live('change', function() { var id =
             * $(this).attr("id"); var key=id.split('_'); var
             * province=$('#'+ key[0]+ '_province
             * option:selected').attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false,
             * data:{'province':province}, success: function(result){ if
             * (result.length>0) { $('#'+ key[0] + '_country
             * option[value=' + result[0].country +
             * ']').attr('selected',true); } }, });
             * 
             * });
             * 
             * $('.city').live('change', function() { var id =
             * $(this).attr("id"); var key=id.split('_'); var
             * city=$('#'+ key[0]+ '_city
             * option:selected').attr('value');
             * 
             * $.ajax({ url: "/page/get_locality", type:"post",
             * dataType:"json", async : false, data:{'city':city},
             * success: function(result){ if (result.length>0) { $('#'+
             * key[0] + '_country option[value=' + result[0].country +
             * ']').attr('selected',true); $('#'+ key[0] + '_province
             * option[value=' + result[0].province +
             * ']').attr('selected',true); } }, }); });
             */

            // Sattelite load province on the basis of country
            $('.country')
                .live(
                    'change',
                    function() {
                        var id = $(this).attr("id");
                        var key = id.split('_');
                        var country = $(
                                '#' +
                                key[0] +
                                '_country option:selected')
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_province",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'country': country
                                },
                                success: function(result) {
                                    $(
                                            '#' +
                                            key[0] +
                                            '_province')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Province --</option>');
                                    $(
                                            '#' +
                                            key[0] +
                                            '_city')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#' +
                                            key[0] +
                                            '_suburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $('#' + key[0] + '_zip')
                                        .val('');
                                    if (result.length > 0) {
                                        var satteliteprovince = $('#' +
                                            key[0] +
                                            '_province');
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    satteliteprovince
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });

            // Sattelite load city on the basis of province
            $('.province')
                .live(
                    'change',
                    function() {
                        var id = $(this).attr("id");
                        var key = id.split('_');
                        var province = $(
                                '#' +
                                key[0] +
                                '_province option:selected')
                            .attr('value');
                        $
                            .ajax({
                                url: "/page/get_city",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'province': province
                                },
                                success: function(result) {
                                    $(
                                            '#' +
                                            key[0] +
                                            '_city')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select City--</option>');
                                    $(
                                            '#' +
                                            key[0] +
                                            '_suburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $('#' + key[0] + '_zip')
                                        .val('');
                                    if (result.length > 0) {
                                        var sattelitecity = $('#' +
                                            key[0] +
                                            '_city');
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    // sattelitecity
                                                    // .append('<option
                                                    // value='
                                                    // +
                                                    // value['id']
                                                    // +
                                                    // '>'
                                                    // +
                                                    // value['name']
                                                    // +
                                                    // '('
                                                    // +
                                                    // value['region']
                                                    // +
                                                    // ')'
                                                    // +
                                                    // '</option>');
                                                    sattelitecity
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });

                    });

            // Sattelite load suburb on the basis of city
            $('.city')
                .live(
                    'change',
                    function() {
                        var id = $(this).attr("id");
                        var key = id.split('_');
                        var city = $(
                                '#' +
                                key[0] +
                                '_city option:selected')
                            .attr('value');

                        $
                            .ajax({
                                url: "/page/get_suburb",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'city': city
                                },
                                success: function(result) {
                                    $(
                                            '#' +
                                            key[0] +
                                            '_suburb')
                                        .find('option')
                                        .remove()
                                        .end()
                                        .append(
                                            '<option value="">-- Select Suburb--</option>');
                                    $('#' + key[0] + '_zip')
                                        .val('');
                                    if (result.length > 0) {
                                        var sattelitesuburb = $('#' +
                                            key[0] +
                                            '_suburb');
                                        $
                                            .each(
                                                result,
                                                function(
                                                    key,
                                                    value) {
                                                    sattelitesuburb
                                                        .append('<option value=' +
                                                            value['id'] +
                                                            '>' +
                                                            value['name'] +
                                                            '</option>');
                                                });
                                    }
                                },
                            });
                    });
            // Sattelite load Zip on the basis of city
            $('.suburb').live(
                'change',
                function() {
                    var id = $(this).attr("id");
                    var key = id.split('_');
                    var suburb = $(
                            '#' + key[0] +
                            '_suburb option:selected')
                        .attr('value');

                    $.ajax({
                        url: "/page/get_locality",
                        type: "post",
                        dataType: "json",
                        async: false,
                        data: {
                            'suburb': suburb
                        },
                        success: function(result) {
                            if (result.length > 0) {
                                $('#' + key[0] + '_zip').val(
                                    result[0].postal_code);
                            }
                        },
                    });
                });

            $('.country option:contains("South Africa")').prop(
                'selected', true).trigger('change');

            // added by vishwas for getting home address and postal
            // address same
            $('#provider_postal_address')
                .change(
                    function() {
                        if ($(this).prop("checked") == true) {
                            $('#provider_postal_address')
                                .val(1);
                            $("#txtPostalAddressLine1")
                                .val(
                                    $(
                                        "#txtPhysicalAddressLine1")
                                    .val());
                            $("#txtPostalAddressLine2")
                                .val(
                                    $(
                                        "#txtPhysicalAddressLine2")
                                    .val());
                            $("#txtPostalAddressLine3")
                                .val(
                                    $(
                                        "#txtPhysicalAddressLine3")
                                    .val());
                            $("#txtPostalAddressCity option")
                                .remove();
                            $("#txtPostalAddressCity")
                                .append(
                                    $(
                                        "#txtPhysicalCity option")
                                    .clone());
                            $("#txtPostalSuburb option")
                                .remove();
                            $("#txtPostalSuburb")
                                .append(
                                    $(
                                        "#txtPhysicalSuburb option")
                                    .clone());
                            $("#txtPostalSuburb").val(
                                $("#txtPhysicalSuburb")
                                .val());
                            $("#txtPostalAddressCity")
                                .val(
                                    $(
                                        "#txtPhysicalCity")
                                    .val());
                            $("#txtPostalAddressZip").val(
                                $("#txtPhysicalZip").val());
                            $("#txtPostalAddressProvince").val(
                                $("#txtPhysicalProvince")
                                .val());
                            $("#txtPostalAddressCountry").val(
                                $("#txtPhysicalCountry")
                                .val());
                            $("#tr_txtPostalAddressLine1")
                                .hide();
                            $("#tr_txtPostalAddressLine2")
                                .hide();
                            $("#tr_txtPostalAddressLine3")
                                .hide();
                            $("#tr_txtPostalAddressSuburb")
                                .hide();
                            $("#tr_txtPostalAddressCity")
                                .hide();
                            $("#tr_txtPostalAddressCountry")
                                .hide();
                            $("#tr_postal_label").hide();

                        } else if ($(this).prop("checked") == false) {
                            $("#txtPostalAddressCity option")
                                .remove();
                            $("#txtPostalAddressCity")
                                .append(
                                    '<option value="">-- Select City--</option>');
                            $("#txtPostalSuburb option")
                                .remove();
                            $("#txtPostalSuburb")
                                .append(
                                    '<option value="">-- Select Suburb--</option>');
                            $('#sdf_postal_address').val(0);
                            $("#txtPostalAddressLine1").val('');
                            $("#txtPostalAddressLine2").val('');
                            $("#txtPostalAddressLine3").val('');
                            $("#txtPostalSuburb").val('');
                            $("#txtPostalAddressCity").val('');
                            $("#txtPostalAddressZip").val('');
                            $("#txtPostalAddressProvince").val(
                                '');
                            $("#txtPostalAddressCountry").val(
                                '');
                            $("#tr_txtPostalAddressLine1")
                                .show();
                            $("#tr_txtPostalAddressLine2")
                                .show();
                            $("#tr_txtPostalAddressLine3")
                                .show();
                            $("#tr_txtPostalAddressSuburb")
                                .show();
                            $("#tr_txtPostalAddressCity")
                                .show();
                            $("#tr_txtPostalAddressCountry")
                                .show();
                            $("#tr_postal_label").show();
                        }
                    });

            $("#frmProviderAccreditation #next4")
                .click(
                    function() {
                        var qualification_ids = {};
                        var q_ids = [];

                        var flag = true;
                        $(
                                ".provider_qualification .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    q_ids
                                        .push(parseInt($(
                                                this)
                                            .attr(
                                                'data-value')))
                                });
                        $
                            .each(
                                q_ids,
                                function(index, value) {
                                    var line_ids = [];
                                    $(
                                            "#check_qualification_line:checked")
                                        .each(
                                            function() {
                                                if (parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) === q_ids[index]) {
                                                    line_ids
                                                        .push(parseInt(this.value));
                                                }
                                            });
                                    // if
                                    // (line_ids.length
                                    // === 0) {
                                    // var
                                    // qualification_name=''
                                    // $(".provider_qualification
                                    // .fs-options
                                    // .fs-option.selected").each(function(){
                                    // if
                                    // (parseInt($(this).attr('data-value'))==q_ids[index]){
                                    // qualification_name=$(this)
                                    // console.log("qualification_name================",qualification_name)
                                    // }
                                    // });
                                    // flag=false
                                    // alert("Please
                                    // select at least
                                    // one Unit standard
                                    // for
                                    // "+qualification_name+"");
                                    // return false;
                                    // }
                                    // else{
                                    qualification_ids[q_ids[index]] = line_ids;
                                    // }
                                });

                        var skill_ids = {};
                        var s_ids = [];
                        $(
                                ".provider_skill .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    s_ids
                                        .push(parseInt($(
                                                this)
                                            .attr(
                                                'data-value')))
                                });
                        $
                            .each(
                                s_ids,
                                function(index, value) {
                                    var line_ids = [];
                                    $(
                                            "#check_skill_line:checked")
                                        .each(
                                            function() {
                                                if (parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) === s_ids[index]) {
                                                    line_ids
                                                        .push(parseInt(this.value));
                                                }
                                            });
                                    // // if
                                    // (line_ids.length
                                    // === 0) {
                                    // // var
                                    // skill_name=''
                                    // //
                                    // $(".provider_skill
                                    // .fs-options
                                    // .fs-option.selected").each(function(){
                                    // // if
                                    // (parseInt($(this).attr('data-value'))==s_ids[index]){
                                    // //
                                    // skill_name=$(this)
                                    // //
                                    // console.log("skill================",skill_name)
                                    // // }
                                    // // });
                                    // // alert("Please
                                    // select at least
                                    // one Unit standard
                                    // for
                                    // "+skill_name+"");
                                    // // flag=false
                                    // // return false;
                                    // // }
                                    // // else{
                                    skill_ids[s_ids[index]] = line_ids;
                                    // // }
                                });
                        // Added by shoaib for populating
                        // #learning_idss hidden field
                        var learning_ids = {};
                        var l_ids = [];
                        $(
                                ".learning_skill .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    l_ids
                                        .push(parseInt($(
                                                this)
                                            .attr(
                                                'data-value')))
                                });
                        $
                            .each(
                                l_ids,
                                function(index, value) {
                                    var line_ids = [];
                                    $(
                                            "#check_learning_line:checked")
                                        .each(
                                            function() {
                                                if (parseInt($(
                                                            this)
                                                        .attr(
                                                            'data-value')) === l_ids[index]) {
                                                    line_ids
                                                        .push(parseInt(this.value));
                                                }
                                            });
                                    learning_ids[l_ids[index]] = line_ids;
                                    console
                                        .log("Hidden field population" +
                                            JSON
                                            .stringify(learning_ids));
                                });
                        $
                            .ajax({
                                url: "/hwseta/providerAccreditation/learnings",
                                type: "post",
                                async: false,
                                data: JSON
                                    .stringify(learning_ids),
                                success: function(result) {
                                    console
                                        .log(
                                            "ISNIDE SUCCESS !!",
                                            result
                                            .toString())
                                    $("#learning_idss")
                                        .val(
                                            result
                                            .toString());
                                },
                            });
                        // end of code by shoaib

                        if (flag = true) {
                            $
                                .ajax({
                                    url: "/hwseta/qualification_assessor_moderator",
                                    type: "post",
                                    async: false,
                                    data: JSON
                                        .stringify(qualification_ids),
                                    success: function(
                                        result) {
                                        $(
                                                "#qualification_idss")
                                            .val(
                                                result
                                                .toString());
                                    },
                                });
                            $
                                .ajax({
                                    url: "/hwseta/providerAccreditation/skills",
                                    type: "post",
                                    async: false,
                                    data: JSON
                                        .stringify(skill_ids),
                                    success: function(
                                        result) {
                                        $("#skill_idss")
                                            .val(
                                                result
                                                .toString());
                                    },
                                });
                            var selected_qualification_ids = [];
                            var selected_skill_ids = [];
                            var selected_learning_progs_ids = [];
                            // copied main campus Qualification
                            // into sattelite campus
                            $(
                                    ".campus_qualification .fs-options")
                                .children().remove();
                            $(
                                    ".campus_qualification .fs-options")
                                .append(
                                    $(
                                        ".provider_qualification .fs-option.selected")
                                    .clone())
                            $(
                                    ".campus_qualification .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        selected_qualification_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))

                                    });
                            $
                                .each(
                                    selected_qualification_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_qualification .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })
                            $
                                .each(
                                    selected_qualification_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_qualification .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })

                            // copied main campus skill
                            // programme into sattelite campus
                            $(".campus_skills .fs-options")
                                .children().remove();
                            $(".campus_skills .fs-options")
                                .append(
                                    $(
                                        ".provider_skill .fs-option.selected")
                                    .clone());
                            $(
                                    ".campus_skills .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        selected_skill_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))
                                    });
                            $
                                .each(
                                    selected_skill_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_skills .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })
                            $
                                .each(
                                    selected_skill_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_skills .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })

                            // copied main campus Assessor into
                            // sattelite campus
                            // $(".campus_assessor
                            // .fs-options").children().remove();
                            // $(".campus_assessor
                            // .fs-options").append($(".assessor
                            // .fs-option.selected").clone());
                            // $(".campus_assessor
                            // .fs-options").append($(".assessor
                            // .fs-option").clone());

                            // copied main campus Moderator into
                            // sattelite campus
                            // $(".campus_moderator
                            // .fs-options").children().remove();
                            // $(".campus_moderator
                            // .fs-options").append($(".moderator
                            // .fs-option.selected").clone());
                            // $(".campus_moderator
                            // .fs-options").append($(".moderator
                            // .fs-option").clone());

                            // Below Code added by shoaib
                            $(".campus_learning .fs-options")
                                .children().remove();
                            $(".campus_learning .fs-options")
                                .append(
                                    $(
                                        ".learning_skill .fs-option.selected")
                                    .clone())
                            $(
                                    ".campus_learning .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        selected_learning_progs_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))

                                    });
                            $
                                .each(
                                    selected_learning_progs_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_learning .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })
                            $
                                .each(
                                    selected_learning_progs_ids,
                                    function(i, o) {
                                        $(
                                                '.campus_learning .fs-option[data-value=' +
                                                o +
                                                ']')
                                            .trigger(
                                                'click');
                                    })

                            // end of code by shoaib
                        }
                    });

            $('input[type=radio][name=radiosattelite]').change(
                function() {
                    if (this.value == 'yes') {
                        $("#next4").show();
                        $("#submit_accreditation").hide();
                    } else if (this.value == 'no') {
                        $("#next4").hide();
                        $("#submit_accreditation").show();
                    }
                });

            /*
             * $( "#frmProviderAccreditation #next4" ).click(function() {
             * var selected_qualification_ids=[]; var
             * selected_skill_ids=[]; // copied main campus
             * Qualification into sattelite campus
             * $(".campus_qualification
             * .fs-options").children().remove();
             * $(".campus_qualification
             * .fs-options").append($(".provider_qualification
             * .fs-option.selected").clone()) $(".campus_qualification
             * .fs-options .fs-option.selected").each(function(){
             * console.log('----=---',$(this).attr('data-value'));
             * selected_qualification_ids.push(parseInt($(this).attr('data-value')))
             * 
             * }); $.each(selected_qualification_ids,function(i,o){
             * $('.campus_qualification
             * .fs-option[data-value='+o+']').trigger('click');})
             * $.each(selected_qualification_ids,function(i,o){
             * $('.campus_qualification
             * .fs-option[data-value='+o+']').trigger('click');}) //
             * copied main campus skill programme into sattelite campus
             * $(".campus_skills .fs-options").children().remove();
             * $(".campus_skills .fs-options").append($(".provider_skill
             * .fs-option.selected").clone()); $(".campus_skills
             * .fs-options .fs-option.selected").each(function(){
             * console.log('----=---',$(this).attr('data-value'));
             * selected_skill_ids.push(parseInt($(this).attr('data-value')))
             * }); $.each(selected_skill_ids,function(i,o){
             * $('.campus_skills
             * .fs-option[data-value='+o+']').trigger('click');})
             * $.each(selected_skill_ids,function(i,o){
             * $('.campus_skills
             * .fs-option[data-value='+o+']').trigger('click');}) //
             * copied main campus Assessor into sattelite campus
             * $(".campus_assessor .fs-options").children().remove(); //
             * $(".campus_assessor .fs-options").append($(".assessor
             * .fs-option.selected").clone()); $(".campus_assessor
             * .fs-options").append($(".assessor .fs-option").clone());
             * 
             * //copied main campus Moderator into sattelite campus
             * $(".campus_moderator .fs-options").children().remove(); //
             * $(".campus_moderator .fs-options").append($(".moderator
             * .fs-option.selected").clone()); $(".campus_moderator
             * .fs-options").append($(".moderator .fs-option").clone());
             * });
             */

            /*
             * $(document).on('click', '.assessor .fs-option',
             * function() { var assessor_ids="" $(".assessor .fs-options
             * .fs-option.selected").each(function(){
             * console.log('----=---',$(this).attr('data-value'));
             * assessor_ids+=parseInt($(this).attr('data-value'))+' '
             * }); $('#assesor_set').val(assessor_ids); });
             * 
             * $(document).on('click', '.moderator .fs-option',
             * function() { var moderator_ids="" $(".moderator
             * .fs-options .fs-option.selected").each(function(){
             * console.log('----=---',$(this).attr('data-value'));
             * moderator_ids+=parseInt($(this).attr('data-value'))+' '
             * }); $('#moderator_set').val(moderator_ids); });
             */

            // Added by vishwas for Provider Main qualification
            $(document)
                .on(
                    'click',
                    '.provider_qualification .fs-option',
                    function() {
                        count = 0;
                        var qualification_ids = ""
                        $(
                                ".provider_qualification .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    qualification_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                    count++
                                });
                        qual_count = count;
                        ids = JSON.stringify(qualification_ids)
                        $('#show_qualification').show();
                        $
                            .ajax({
                                url: "/page/assessorModerator/get_qualification",
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'qualification_ids': qualification_ids
                                },
                                success: function(result) {
                                    var checked_list = []
                                    var readonly_checked_list = []
                                    $(
                                            '[name=quali]:checked')
                                        .each(
                                            function() {
                                                checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    $(
                                            '[name=quali]:disabled')
                                        .each(
                                            function() {
                                                readonly_checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    if (result.length > 0) {
                                        unit_standard_line = false;
                                        $(
                                                "#show_qualification #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_qualification #qualification")
                                            .remove();
                                        var qualification = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {
                                                    //element variable is for holding dynamic HTML tag for seta_approved_lp checkbox
                                                    var element = result[index]['is_seta_approved'] == true ? (
                                                        "<input id='is_seta_approved' type='checkbox' name='is_seta_approved' checked='true' value='" + result[index]['is_seta_approved'] + "'/>") : (
                                                        "<input id='is_seta_approved' type='checkbox' name='is_seta_approved' value='" + result[index]['is_seta_approved'] + "'/>");

                                                    var element2 = result[index]['is_provider_approved'] == true ? (
                                                        "<input id='is_provider_approved' type='checkbox' name='is_provider_approved' checked='true' value='" + result[index]['is_provider_approved'] + "'/>") : (
                                                        "<input id='is_provider_approved' type='checkbox' name='is_provider_approved' value='" + result[index]['is_provider_approved'] + "'/>");
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['saqa_qual_id']),
                                                            qualification) == -1) {
                                                        qualification
                                                            .push(parseInt(result[index]['saqa_qual_id']))
                                                        $(
                                                                "#show_qualification .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='qualification'><td colspan='9'><b>" +
                                                                result[index]['qualification_name'] +
                                                                "</b> (" +
                                                                result[index]['saqa_qual_id'] +
                                                                ")</td><tr>")
                                                    }
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['line_id']),
                                                            checked_list) != -1) {
                                                        if ($
                                                            .inArray(
                                                                parseInt(result[index]['line_id']),
                                                                readonly_checked_list) != -1) {
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked disabled/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    } else {
                                                        if ((result[index]['type'] == 'Core') ||
                                                            (result[index]['type'] == 'Fundamental') ||
                                                            (result[index]['type'] == 'Core ') ||
                                                            (result[index]['type'] == 'Fundamental ')) {
                                                            unit_standard_line = true;
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' disabled='disabled' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else if ((result[index]['type'] == 'Elective') && (result[index]['is_seta_approved'] == true)) {
                                                            unit_standard_line = true;
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' disabled='disabled' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else if ((result[index]['is_provider_approved'] == true)) {
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines' style='color:blue;' ><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "'/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {
                                                            $(
                                                                    "#show_qualification .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_qualification_line' type='checkbox' name='quali' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' /><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    }
                                                });

                                        $("input[name='quali']").click(function() {
                                            if ($(this).is(":checked")) {
                                                alert("Note that the Electives chosen must have HWSETA approved report!!!");
                                            }
                                        });

                                    } else if (result.length == 0) {
                                        unit_standard_line = true;
                                        $(
                                                "#show_qualification")
                                            .hide();
                                    }
                                },
                            });
                    });
            // Commented by Ganesh because of checked & unchecked issue
            /*
             * $ .ajax({ url :
             * "/page/assessorModerator/get_qualification", type :
             * "post", dataType : "json", data : { 'qualification_ids' :
             * qualification_ids }, success : function(result) { var
             * checked_list = [] $( '[name=quali]:checked') .each(
             * function() { checked_list .push(parseInt($( this)
             * .val())) }); if (result.length > 0) { $(
             * "#show_qualification #lines") .nextUntil( '#lines')
             * .andSelf() .remove(); $( "#show_qualification
             * #qualification") .remove(); var qualification = [] $
             * .each( result, function( index, value) { if ($ .inArray(
             * parseInt(result[index]['saqa_qual_id']), qualification) ==
             * -1) { qualification
             * .push(parseInt(result[index]['saqa_qual_id'])) $(
             * "#show_qualification .heading") .parent( "tbody")
             * .append( "<tr id='qualification'><td colspan='7'><b>" +
             * result[index]['qualification_name'] + "</b> (" +
             * result[index]['saqa_qual_id'] + ")</td><tr>") } if ($
             * .inArray( parseInt(result[index]['line_id']),
             * checked_list) != -1) { $( "#show_qualification .heading")
             * .parent( "tbody") .append( "<tr id='lines' class='lines'><td>" +
             * result[index]['type'] + "</td><td>" +
             * result[index]['id_no'] + "</td><td>" +
             * result[index]['title'] + "</td><td>" +
             * result[index]['level1'] + "</td><td>" +
             * result[index]['level2'] + "</td><td>" +
             * result[index]['level3'] + "</td><td><input
             * style='height: 15px;width: 15px;'
             * id='check_qualification_line' type='checkbox'
             * name='quali' value='" + result[index]['line_id'] + "'
             * data-value='" + result[index]['id'] + "' checked/><input
             * id='check_qualification_id' type='hidden' name='quali'
             * value='" + result[index]['id'] + "'/></td></tr>") }
             * else { if ((result[index]['type'] == 'Core') ||
             * (result[index]['type'] == 'Fundamental') ||
             * (result[index]['type'] == 'Elective') ||
             * (result[index]['type'] == 'Core ') ||
             * (result[index]['type'] == 'Fundamental ') ||
             * (result[index]['type'] == 'Elective ')) { $(
             * "#show_qualification .heading") .parent( "tbody")
             * .append( "<tr id='lines' class='lines'><td>" +
             * result[index]['type'] + "</td><td>" +
             * result[index]['id_no'] + "</td><td>" +
             * result[index]['title'] + "</td><td>" +
             * result[index]['level1'] + "</td><td>" +
             * result[index]['level2'] + "</td><td>" +
             * result[index]['level3'] + "</td><td><input
             * style='height: 15px;width: 15px;'
             * id='check_qualification_line' disabled='disabled'
             * type='checkbox' name='quali' value='" +
             * result[index]['line_id'] + "' data-value='" +
             * result[index]['id'] + "'checked /><input
             * id='check_qualification_id' type='hidden' name='quali'
             * value='" + result[index]['id'] + "'/></td></tr>") }
             * else { $( "#show_qualification .heading") .parent(
             * "tbody") .append( "<tr id='lines' class='lines'><td>" +
             * result[index]['type'] + "</td><td>" +
             * result[index]['id_no'] + "</td><td>" +
             * result[index]['title'] + "</td><td>" +
             * result[index]['level1'] + "</td><td>" +
             * result[index]['level2'] + "</td><td>" +
             * result[index]['level3'] + "</td><td><input
             * style='height: 15px;width: 15px;'
             * id='check_qualification_line' type='checkbox'
             * name='quali' value='" + result[index]['line_id'] + "'
             * data-value='" + result[index]['id'] + "' /><input
             * id='check_qualification_id' type='hidden' name='quali'
             * value='" + result[index]['id'] + "'/></td></tr>") }
             *  } }); } else if (result.length == 0) { $(
             * "#show_qualification") .hide(); } }, });
             */

            // Added by vishwas for Provider Campus qualification
            $(document)
                .on(
                    'click',
                    '.campus_qualification .fs-option',
                    function() {
                        var qualification_ids = ""
                        $(
                                ".campus_qualification .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    qualification_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                });
                        ids = JSON.stringify(qualification_ids)
                        main_campus_qualification = $(
                            '#qualification_idss').val();
                        $('#show_campus_qualification').show();
                        $
                            .ajax({
                                url: "/page/providerAccreditation/get_campus_qualification",
                                type: "post",
                                dataType: "json",
                                data: {
                                    'qualification_ids': qualification_ids,
                                    'sub_ids': main_campus_qualification
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        $(
                                                "#show_campus_qualification #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_campus_qualification #campus_qualification")
                                            .remove();
                                        var campus_qualification = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {
                                                    //element variable is for holding dynamic HTML tag for seta_approved_lp checkbox
                                                    var element = result[index]['is_seta_approved'] == true ? (
                                                        "<input id='is_seta_approved' disabled='true' type='checkbox' name='is_seta_approved' checked='true' value='" + result[index]['is_seta_approved'] + "'/>") : (
                                                        "<input id='is_seta_approved' disabled='true' type='checkbox' name='is_seta_approved' value='" + result[index]['is_seta_approved'] + "'/>");

                                                    var element2 = result[index]['is_provider_approved'] == true ? (
                                                        "<input id='is_provider_approved' disabled='true' type='checkbox' name='is_provider_approved' checked='true' value='" + result[index]['is_provider_approved'] + "'/>") : (
                                                        "<input id='is_provider_approved' disabled='true' type='checkbox' name='is_provider_approved' value='" + result[index]['is_provider_approved'] + "'/>");
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['saqa_qual_id']),
                                                            campus_qualification) == -1) {
                                                        campus_qualification
                                                            .push(parseInt(result[index]['saqa_qual_id']))
                                                        $(
                                                                "#show_campus_qualification .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='campus_qualification'><td colspan='9'><b>" +
                                                                result[index]['qualification_name'] +
                                                                "</b> (" +
                                                                result[index]['saqa_qual_id'] +
                                                                ")</td><tr>")
                                                    }
                                                    $(
                                                            "#show_campus_qualification .heading")
                                                        .parent(
                                                            "tbody")
                                                        .append(
                                                            "<tr id='lines' class='lines'><td>" +
                                                            result[index]['type'] +
                                                            "</td><td>" +
                                                            result[index]['id_no'] +
                                                            "</td><td>" +
                                                            result[index]['title'] +
                                                            "</td><td>" +
                                                            result[index]['level1'] +
                                                            "</td><td>" +
                                                            result[index]['level2'] +
                                                            "</td><td>" +
                                                            result[index]['level3'] +
                                                            "</td><td>" +
                                                            element + "</td><td>" +
                                                            element2 + "</td><td>" +
                                                            "<input checked style='height: 15px;width: 15px;' id='check_qualification_line' type='checkbox' name='quali' onClick='return false;' value='" +
                                                            result[index]['line_id'] +
                                                            "' data-value='" +
                                                            result[index]['id'] +
                                                            "'/><input id='check_qualification_id' type='hidden' name='quali' value='" +
                                                            result[index]['id'] +
                                                            "'/></td></tr>")
                                                });
                                        $(
                                                "#show_campus_qualification")
                                            .show();
                                    } else if (result.length == 0) {
                                        $(
                                                "#show_campus_qualification")
                                            .hide();
                                    }
                                },
                            });

                    });

            // Added by vishwas for Skill program
            $(document)
                .on(
                    'click',
                    '.provider_skill .fs-option',
                    function() {
                        count = 0;
                        var skill_ids = ""
                        $(
                                ".provider_skill .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    skill_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                    count++
                                });
                        skill_count = count;
                        ids = JSON.stringify(skill_ids)
                        $('#show_skills').show();
                        $
                            .ajax({
                                url: "/page/providerAccreditation/get_skill",
                                type: "post",
                                dataType: "json",
                                data: {
                                    'skill_ids': skill_ids
                                },
                                success: function(result) {
                                    var checked_list = []
                                    var readonly_checked_list = []
                                    $(
                                            '[name=skill]:checked')
                                        .each(
                                            function() {
                                                checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    $(
                                            '[name=skill]:disabled')
                                        .each(
                                            function() {
                                                readonly_checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    if (result.length > 0) {
                                        unit_standard_line = false;
                                        $(
                                                "#show_skills #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_skills #skills")
                                            .remove();
                                        var skill_program = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['id']),
                                                            skill_program) == -1) {
                                                        skill_program
                                                            .push(parseInt(result[index]['id']))
                                                        $(
                                                                "#show_skills .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='skills'><td colspan='7'><b>" +
                                                                result[index]['skill_name'] +
                                                                "</b> (" +
                                                                result[index]['code'] +
                                                                ")</td><tr>")
                                                    }
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['line_id']),
                                                            checked_list) != -1) {
                                                        if ($
                                                            .inArray(
                                                                parseInt(result[index]['line_id']),
                                                                readonly_checked_list) != -1) {
                                                            $(
                                                                    "#show_skills .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td><input style='height: 15px;width: 15px;' id='check_skill_line' type='checkbox' name='skill' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked disabled/><input id='check_skill_id' type='hidden' name='skill' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {
                                                            $(
                                                                    "#show_skills .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td><input style='height: 15px;width: 15px;' id='check_skill_line' type='checkbox' name='skill' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked/><input id='check_skill_id' type='hidden' name='skill' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    } else {
                                                        if ((result[index]['type'] == 'Core') ||
                                                            (result[index]['type'] == 'Fundamental') ||
                                                            (result[index]['type'] == 'Elective') ||
                                                            (result[index]['type'] == 'Core ') ||
                                                            (result[index]['type'] == 'Fundamental ') ||
                                                            (result[index]['type'] == 'Elective ')) {
                                                            unit_standard_line = true;
                                                            $(
                                                                    "#show_skills .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td><input style='height: 15px;width: 15px;' id='check_skill_line' disabled='disabled' type='checkbox' name='skill' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked/><input id='check_skill_id' type='hidden' name='skill' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {
                                                            $(
                                                                    "#show_skills .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td><input style='height: 15px;width: 15px;' id='check_skill_line' type='checkbox' name='skill' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' /><input id='check_skill_id' type='hidden' name='skill' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    }
                                                });
                                    } else if (result.length == 0) {
                                        unit_standard_line = false;
                                        $("#show_skills")
                                            .hide();
                                    }
                                },
                            });

                    });
            // Added by Ganesh for Campus Skills Programme
            $(document)
                .on(
                    'click',
                    '.campus_skills .fs-option',
                    function() {
                        var skill_ids = ""
                        $(
                                ".campus_skills .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    skill_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                });
                        ids = JSON.stringify(skill_ids)
                        main_campus_skill = $('#skill_idss')
                            .val();
                        $('#show_campus_skill').show();
                        // alert('11_1');
                        $
                            .ajax({
                                url: "/page/providerAccreditation/get_campus_skill",
                                type: "post",
                                dataType: "json",
                                data: {
                                    'skill_ids': skill_ids,
                                    'sub_ids': main_campus_skill
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        $(
                                                "#show_campus_skill")
                                            .show();
                                        $(
                                                "#show_campus_skill #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_campus_skill #campus_skills")
                                            .remove();
                                        var campus_skills = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['saqa_qual_id']),
                                                            campus_skills) == -1) {
                                                        campus_skills
                                                            .push(parseInt(result[index]['saqa_qual_id']))
                                                        $(
                                                                "#show_campus_skill .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='campus_skills'><td colspan='7'><b>" +
                                                                result[index]['skill_name'] +
                                                                "</b> (" +
                                                                result[index]['saqa_qual_id'] +
                                                                ")</td><tr>")
                                                    }
                                                    $(
                                                            "#show_campus_skill .heading")
                                                        .parent(
                                                            "tbody")
                                                        .append(
                                                            "<tr id='lines' class='lines'><td>" +
                                                            result[index]['name'] +
                                                            "</td><td>" +
                                                            result[index]['id_no'] +
                                                            "</td><td>" +
                                                            result[index]['title'] +
                                                            "</td><td>" +
                                                            result[index]['level1'] +
                                                            "</td><td>" +
                                                            result[index]['level2'] +
                                                            "</td><td>" +
                                                            result[index]['level3'] +
                                                            "</td><td><input checked style='height: 15px;width: 15px;' id='check_skill_line' type='checkbox'  name='campus_skill' onClick='return false;' value='" +
                                                            result[index]['line_id'] +
                                                            "' data-value='" +
                                                            result[index]['id'] +
                                                            "'/><input id='check_qualification_id' type='hidden' name='skill' value='" +
                                                            result[index]['id'] +
                                                            "'/></td></tr>")
                                                    $(
                                                            "#show_campus_skill")
                                                        .show();
                                                });
                                    } else if (result.length == 0) {
                                        $(
                                                "#show_campus_skill")
                                            .hide();
                                    }
                                },
                            });

                    });

            // Added by Vishnu for Main campus Learning Programme

            $(document)
                .on(
                    'click',
                    '.learning_skill .fs-option',
                    function() {
                        count = 0;
                        var learning_ids = ""
                        $(
                                ".learning_skill .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    learning_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                    count++
                                });
                        learning_count = count;
                        ids = JSON.stringify(learning_ids)
                        $('#show_learnings').show();
                        $
                            .ajax({
                                url: "/page/providerAccreditation/get_learning_skill",
                                type: "post",
                                dataType: "json",
                                data: {
                                    'learning_ids': learning_ids
                                },
                                success: function(result) {
                                    var checked_list = []
                                    var readonly_checked_list = []
                                    $(
                                            '[name=skill]:checked')
                                        .each(
                                            function() {
                                                checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    $(
                                            '[name=skill]:disabled')
                                        .each(
                                            function() {
                                                readonly_checked_list
                                                    .push(parseInt($(
                                                            this)
                                                        .val()))
                                            });
                                    if (result.length > 0) {
                                        unit_standard_line = false;
                                        $(
                                                "#show_learnings #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_learnings #learning")
                                            .remove();
                                        var learning_program = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {
                                                    //element variable is for holding dynamic HTML tag for seta_approved_lp checkbox
                                                    var element = result[index]['seta_approved_lp'] == true ? (
                                                        "<input id='seta_approved_lp' disabled='true' type='checkbox' name='seta_approved_lp' checked='true' value='" + result[index]['seta_approved_lp'] + "'/>") : (
                                                        "<input id='seta_approved_lp' disabled='true' type='checkbox' name='seta_approved_lp' value='" + result[index]['seta_approved_lp'] + "'/>");

                                                    var element2 = result[index]['provider_approved_lp'] == true ? (
                                                        "<input id='provider_approved_lp' disabled='true' type='checkbox' name='provider_approved_lp' checked='true' value='" + result[index]['provider_approved_lp'] + "'/>") : (
                                                        "<input id='provider_approved_lp' disabled='true' type='checkbox' name='provider_approved_lp' value='" + result[index]['provider_approved_lp'] + "'/>");

                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['id']),
                                                            learning_program) == -1) {
                                                        learning_program
                                                            .push(parseInt(result[index]['id']))
                                                        $(
                                                                "#show_learnings .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='learning'><td colspan='9'><b>" +
                                                                result[index]['learning_name'] +
                                                                "</b> (" +
                                                                result[index]['code'] +
                                                                ")</td><tr>")
                                                    }
                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['line_id']),
                                                            checked_list) != -1) {
                                                        if ($
                                                            .inArray(
                                                                parseInt(result[index]['line_id']),
                                                                readonly_checked_list) != -1) {
                                                            $(
                                                                    "#show_learnings .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_learning_line' type='checkbox' name='learning' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked disabled/><input id='check_learning_id' type='hidden' name='learning' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {
                                                            $(
                                                                    "#show_learnings .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_learning_line' type='checkbox' name='learning' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked disabled/><input id='check_learning_id' type='hidden' name='learning' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    } else {
                                                        if ((result[index]['type'] == 'Core') ||
                                                            (result[index]['type'] == 'Fundamental') ||
                                                            (result[index]['type'] == 'Elective') ||
                                                            (result[index]['type'] == 'Core ') ||
                                                            (result[index]['type'] == 'Fundamental ') ||
                                                            (result[index]['type'] == 'Elective ')) {
                                                            unit_standard_line = true;
                                                            $(
                                                                    "#show_learnings .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_learning_line' type='checkbox' name='learning' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' checked disabled/><input id='check_learning_id' type='hidden' name='learning' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        } else {

                                                            $(
                                                                    "#show_learnings .heading")
                                                                .parent(
                                                                    "tbody")
                                                                .append(
                                                                    "<tr id='lines' class='lines'><td>" +
                                                                    result[index]['type'] +
                                                                    "</td><td>" +
                                                                    result[index]['id_no'] +
                                                                    "</td><td>" +
                                                                    result[index]['title'] +
                                                                    "</td><td>" +
                                                                    result[index]['level1'] +
                                                                    "</td><td>" +
                                                                    result[index]['level2'] +
                                                                    "</td><td>" +
                                                                    result[index]['level3'] +
                                                                    "</td><td>" +
                                                                    element + "</td><td>" +
                                                                    element2 + "</td><td>" +
                                                                    "<input style='height: 15px;width: 15px;' id='check_learning_line' type='checkbox' name='learning' value='" +
                                                                    result[index]['line_id'] +
                                                                    "' data-value='" +
                                                                    result[index]['id'] +
                                                                    "' /><input id='check_learning_id' type='hidden' disabled name='learning' value='" +
                                                                    result[index]['id'] +
                                                                    "'/></td></tr>")
                                                        }
                                                    }
                                                });
                                    } else if (result.length == 0) {
                                        unit_standard_line = false;
                                        $("#show_learnings")
                                            .hide();
                                    }
                                },
                            });

                    });

            // added by shoaib for satellite campus learning programme
            $(document)
                .on(
                    'click',
                    '.campus_learning .fs-option',
                    function() {
                        var learning_ids = ""
                        $(
                                ".campus_learning .fs-options .fs-option.selected")
                            .each(
                                function() {
                                    learning_ids += parseInt($(
                                                this)
                                            .attr(
                                                'data-value')) +
                                        ' '
                                });
                        ids = JSON.stringify(learning_ids)
                        main_campus_learning = $(
                            '#learning_idss').val();
                        $('#show_campus_learning').show();
                        // alert('campus learning called');
                        $
                            .ajax({
                                url: "/page/providerAccreditation/get_campus_learning",
                                type: "post",
                                dataType: "json",
                                data: {
                                    'learning_ids': learning_ids,
                                    'sub_ids': main_campus_learning
                                },
                                success: function(result) {
                                    if (result.length > 0) {

                                        $(
                                                "#show_campus_learning")
                                            .show();
                                        $(
                                                "#show_campus_learning #lines")
                                            .nextUntil(
                                                '#lines')
                                            .andSelf()
                                            .remove();
                                        $(
                                                "#show_campus_learning #camp_learning")
                                            .remove();
                                        var campus_skills = []
                                        $
                                            .each(
                                                result,
                                                function(
                                                    index,
                                                    value) {

                                                    //element variable is for holding dynamic HTML tag for seta_approved_lp checkbox
                                                    var element = result[index]['seta_approved_lp'] == true ? (
                                                        "<input id='seta_approved_campus_lp' disabled='true' type='checkbox' name='seta_approved_lp' checked='true' value='" + result[index]['seta_approved_lp'] + "'/>") : (
                                                        "<input id='seta_approved_campus_lp' disabled='true' type='checkbox' name='seta_approved_campus_lp' value='" + result[index]['seta_approved_lp'] + "'/>");

                                                    var element2 = result[index]['provider_approved_lp'] == true ? (
                                                        "<input id='provider_approved_campus_lp' disabled='true' type='checkbox' name='provider_approved_campus_lp' checked='true' value='" + result[index]['provider_approved_lp'] + "'/>") : (
                                                        "<input id='provider_approved_campus_lp' disabled='true' type='checkbox' name='provider_approved_campus_lp' value='" + result[index]['provider_approved_lp'] + "'/>");

                                                    if ($
                                                        .inArray(
                                                            parseInt(result[index]['saqa_qual_id']),
                                                            campus_skills) == -1) {
                                                        campus_skills
                                                            .push(parseInt(result[index]['saqa_qual_id']))
                                                        $(
                                                                "#show_campus_learning .heading")
                                                            .parent(
                                                                "tbody")
                                                            .append(
                                                                "<tr id='camp_learning'><td colspan='9'><b>" +
                                                                result[index]['learning_name'] +
                                                                "</b> (" +
                                                                result[index]['saqa_qual_id'] +
                                                                ")</td><tr>")
                                                    }
                                                    $(
                                                            "#show_campus_learning .heading")
                                                        .parent(
                                                            "tbody")
                                                        .append(
                                                            "<tr id='lines' class='lines'><td>" +
                                                            result[index]['type'] +
                                                            "</td><td>" +
                                                            result[index]['id_no'] +
                                                            "</td><td>" +
                                                            result[index]['title'] +
                                                            "</td><td>" +
                                                            result[index]['level1'] +
                                                            "</td><td>" +
                                                            result[index]['level2'] +
                                                            "</td><td>" +
                                                            result[index]['level3'] +
                                                            "</td><td>" +
                                                            element + "</td><td>" +
                                                            element2 + "</td><td>" +
                                                            "<input checked style='height: 15px;width: 15px;' id='check_learning_line' type='checkbox'  name='campus_learning' onClick='return false;' value='" +
                                                            result[index]['line_id'] +
                                                            "' data-value='" +
                                                            result[index]['id'] +
                                                            "'/><input id='check_qualification_id' type='hidden' name='skill' value='" +
                                                            result[index]['id'] +
                                                            "'/></td></tr>")
                                                    $(
                                                            "#show_campus_learning")
                                                        .show();
                                                });
                                    } else if (result.length == 0) {
                                        $(
                                                "#show_campus_learning")
                                            .hide();
                                    }
                                },
                            });
                    });
            // end code by shoaib
            $("#frmProviderAccreditation #submit_accreditation")
                .click(
                    function() {
                        // alert("Clicked")
                        // return false;


                        var flag = false;
                        $('#assesor_set').val('');
                        assessor_ids = ''
                        $("#assessor option:selected")
                            .each(
                                function() {
                                    assessor_ids += parseInt($(
                                            this).attr(
                                            'value')) +
                                        ' '
                                });
                        $('#assesor_set').val(assessor_ids);

                        $('#moderator_set').val('');
                        moderator_ids = ''
                        $("#moderator option:selected")
                            .each(
                                function() {
                                    moderator_ids += parseInt($(
                                            this).attr(
                                            'value')) +
                                        ' '
                                });
                        $('#moderator_set').val(moderator_ids);

                        if ($(
                                'input[type=radio][name=radiosattelite]:checked')
                            .val() == 'yes') {

                            $(
                                    "#fs8 .form-bg .tableclass .clonedInput")
                                .each(
                                    function(key, val) {
                                        if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_campusname')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_campusname')
                                                .focus();
                                            alert("Please specify campus name");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_email')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_email')
                                                .focus();
                                            alert("Please specify campus email address");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_street')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_street')
                                                .focus();
                                            alert("Please specify an street address");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_street2')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_street2')
                                                .focus();
                                            alert("Please specify an street2 address");
                                            flag = false;
                                            return false;
                                        }
                                        /*
                                         * else if
                                         * ($('#ID' +
                                         * (key+1) +
                                         * '_street3').val()
                                         * ==''){
                                         * $('#ID' +
                                         * (key+1) +
                                         * '_street3').focus();
                                         * alert("Please
                                         * specify
                                         * an
                                         * street3
                                         * address");
                                         * flag=false;
                                         * return
                                         * false; }
                                         */
                                        else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_country')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_country')
                                                .focus();
                                            alert("Please Select country");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_province')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_province')
                                                .focus();
                                            alert("Please Select Province");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_txtContactNameSurname')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_txtContactNameSurname')
                                                .focus();
                                            alert("Please specify an contact person name");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_txtContactEmail')
                                            .val() == '') {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_txtContactEmail')
                                                .focus();
                                            alert("Please specify an contact person email address");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_campusassessor')
                                            .val() == null) {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_campus_assessor_number')
                                                .focus();
                                            alert("Please Add Assessors!");
                                            flag = false;
                                            return false;
                                        } else if ($(
                                                '#ID' +
                                                (key + 1) +
                                                '_campusmoderator')
                                            .val() == null) {
                                            $(
                                                    '#ID' +
                                                    (key + 1) +
                                                    '_campus_moderator_number')
                                                .focus();
                                            alert("Please Add Moderators!");
                                            flag = false;
                                            return false;
                                        } else {
                                            flag = true;
                                        }
                                        var assessor_ids = ""
                                        $(
                                                "#fs8 .form-bg .tableclass #entry" +
                                                (key + 1) +
                                                " #ID" +
                                                (key + 1) +
                                                "_campusassessor option:selected")
                                            .each(
                                                function() {
                                                    assessor_ids += parseInt($(
                                                                this)
                                                            .attr(
                                                                'value')) +
                                                        ' '
                                                });
                                        $(
                                                "#ID" +
                                                (key + 1) +
                                                "_campusassesorset")
                                            .val(
                                                assessor_ids);
                                        var moderator_ids = ""
                                        $(
                                                "#fs8 .form-bg .tableclass #entry" +
                                                (key + 1) +
                                                " #ID" +
                                                (key + 1) +
                                                "_campusmoderator option:selected")
                                            .each(
                                                function() {
                                                    moderator_ids += parseInt($(
                                                                this)
                                                            .attr(
                                                                'value')) +
                                                        ' '
                                                });
                                        $(
                                                "#ID" +
                                                (key + 1) +
                                                "_campusmoderatorset")
                                            .val(
                                                moderator_ids);
                                        var qualification_ids = {};
                                        var q_ids = [];
                                        $(
                                                "#fs8 .form-bg .tableclass #entry" +
                                                (key + 1) +
                                                " .campus_qualification .fs-options .fs-option.selected")
                                            .each(
                                                function() {
                                                    q_ids
                                                        .push(parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')))

                                                });
                                        $
                                            .each(
                                                q_ids,
                                                function(
                                                    index,
                                                    value) {
                                                    var line_ids = [];
                                                    $(
                                                            "#fs8 .form-bg .tableclass #entry" +
                                                            (key + 1) +
                                                            " #check_qualification_line:checked")
                                                        .each(
                                                            function() {
                                                                if (parseInt($(
                                                                            this)
                                                                        .attr(
                                                                            'data-value')) === q_ids[index]) {
                                                                    line_ids
                                                                        .push(parseInt(this.value));
                                                                }
                                                            });
                                                    qualification_ids[q_ids[index]] = line_ids;
                                                });
                                        $
                                            .ajax({
                                                url: "/hwseta/qualification_assessor_moderator",
                                                type: "post",
                                                async: false,
                                                data: JSON
                                                    .stringify(qualification_ids),
                                                success: function(
                                                    result) {
                                                    $(
                                                            "#ID" +
                                                            (key + 1) +
                                                            "_campusqualificationids")
                                                        .val(
                                                            result
                                                            .toString());
                                                },
                                            });

                                        // added by
                                        // shoaib

                                        var learning_ids = {};
                                        var l_ids = [];
                                        $(
                                                "#fs8 .form-bg .tableclass #entry" +
                                                (key + 1) +
                                                " .campus_learning .fs-options .fs-option.selected")
                                            .each(
                                                function() {
                                                    l_ids
                                                        .push(parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')))

                                                });
                                        $
                                            .each(
                                                l_ids,
                                                function(
                                                    index,
                                                    value) {
                                                    var line_ids = [];
                                                    $(
                                                            "#fs8 .form-bg .tableclass #entry" +
                                                            (key + 1) +
                                                            " #check_learning_line:checked")
                                                        .each(
                                                            function() {
                                                                if (parseInt($(
                                                                            this)
                                                                        .attr(
                                                                            'data-value')) === l_ids[index]) {
                                                                    line_ids
                                                                        .push(parseInt(this.value));
                                                                }
                                                            });
                                                    learning_ids[l_ids[index]] = line_ids;
                                                    console
                                                        .log("Final learning IDS is :" +
                                                            JSON
                                                            .stringify(learning_ids));
                                                });
                                        $
                                            .ajax({
                                                url: "/hwseta/providerAccreditation/learnings",
                                                type: "post",
                                                async: false,
                                                data: JSON
                                                    .stringify(learning_ids),
                                                success: function(
                                                    result) {
                                                    console
                                                        .log('campus learning data passing.' +
                                                            result
                                                            .toString() +
                                                            typeof(result));
                                                    $(
                                                            "#ID" +
                                                            (key + 1) +
                                                            "_campuslearningsids")
                                                        .val(
                                                            result
                                                            .toString());
                                                    console
                                                        .log("AFter " +
                                                            $(
                                                                "#ID" +
                                                                (key + 1) +
                                                                "_campuslearningsids")
                                                            .val());
                                                },
                                            });
                                        // end of code
                                        // by shoaib
                                        var skill_ids = {};
                                        var s_ids = [];
                                        $(
                                                "#fs8 .form-bg .tableclass #entry" +
                                                (key + 1) +
                                                " .campus_skills .fs-options .fs-option.selected")
                                            .each(
                                                function() {
                                                    s_ids
                                                        .push(parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')))

                                                });
                                        $
                                            .each(
                                                s_ids,
                                                function(
                                                    index,
                                                    value) {
                                                    var line_ids = [];
                                                    $(
                                                            "#fs8 .form-bg .tableclass #entry" +
                                                            (key + 1) +
                                                            " #check_skill_line:checked")
                                                        .each(
                                                            function() {
                                                                if (parseInt($(
                                                                            this)
                                                                        .attr(
                                                                            'data-value')) === s_ids[index]) {
                                                                    line_ids
                                                                        .push(parseInt(this.value));
                                                                }

                                                            });
                                                    skill_ids[s_ids[index]] = line_ids;
                                                });
                                        $
                                            .ajax({
                                                url: "/hwseta/providerAccreditation/skills",
                                                type: "post",
                                                async: false,
                                                data: JSON
                                                    .stringify(skill_ids),
                                                success: function(
                                                    result) {
                                                    $(
                                                            "#ID" +
                                                            (key + 1) +
                                                            "_campusskillsids")
                                                        .val(
                                                            result
                                                            .toString());
                                                    console
                                                        .log("FOR SKILLS " +
                                                            $(
                                                                "#ID" +
                                                                (key + 1) +
                                                                "_campusskillsids")
                                                            .val() +
                                                            typeof(result));

                                                },
                                            });
                                    });
                        } else if ($(
                                'input[type=radio][name=radiosattelite]:checked')
                            .val() == 'no') {
                            // Added these validations because
                            // each Qualification should have
                            // assessor & moderator
                            // if (ass_count < qual_count)
                            // {
                            // alert('Please add assessor!
                            // Number of selected Qualifications
                            // and number of selected Assessors
                            // should be same.');
                            // return false;
                            // }else if (ass_count > qual_count)
                            // {
                            // alert('Please remove assessor!
                            // Number of selected Qualifications
                            // and number of selected Assessors
                            // should be same.');
                            // return false;
                            // }else if (mod_count < qual_count)
                            // {
                            // alert('Please add moderator!
                            // Number of selected Qualifications
                            // and number of selected Moderators
                            // should be same.');
                            // return false;
                            // }else if (mod_count > qual_count)
                            // {
                            // alert('Please remove moderator!
                            // Number of selected Qualifications
                            // and number of selected Moderators
                            // should be same.');
                            // return false;
                            // }
                            if ($("#assessor").val() == null ||
                                $("#assessor").val() == undefined) {
                                msg = "Please Add Assessor";
                                $("#assessor").focus();
                                alert(msg);
                                return false;
                            }
                            //check if file has been attached to accessor
                            var accessor_file_evals = $(".field_wrapper_assessor :file[required]");
                            for (var i = 0; i < accessor_file_evals.length; i++) {
                                if (accessor_file_evals[i].value == '' || accessor_file_evals[i].value == undefined) {
                                    alert("Please Upload Appoinment Letter/SLA to Assessor");
                                    accessor_file_evals[i].focus();
                                    accessor_file_evals[i].style.border = "medium solid red";
                                    return false;
                                }
                            } //end of for loop

                            //check if file has been attached to accessor
                            var accessor_notification_file_evals = $(".field_wrapper_assessor_notification_letter :file[required]");
                            for (var i = 0; i < accessor_notification_file_evals.length; i++) {
                                if (accessor_notification_file_evals[i].value == '' || accessor_notification_file_evals[i].value == undefined) {
                                    alert("Please Upload Notification Letter to Assessor");
                                    accessor_notification_file_evals[i].focus();
                                    accessor_notification_file_evals[i].style.border = "medium solid red";
                                    return false;
                                }
                            } //end of for loop

                            if ($("#moderator").val() == null ||
                                $("#moderator").val() == undefined) {
                                msg = "Please Add Moderator";
                                $("#moderator").focus();
                                alert(msg);
                                return false;
                            }

                            //check if file has been attached to moderator
                            var moderator_file_evals = $(".field_wrapper_moderator :file[required]");
                            for (var i = 0; i < moderator_file_evals.length; i++) {
                                if (moderator_file_evals[i].value == '' || moderator_file_evals[i].value == undefined) {
                                    alert("Please Upload Appoinment Letter/SLA to Moderator");
                                    moderator_file_evals[i].focus();
                                    moderator_file_evals[i].style.border = "medium solid red";
                                    return false;
                                }
                            } //end of for loop


                            //check if file has been attached to moderator
                            var moderator_notification_file_evals = $(".field_wrapper_moderator_notification_letter :file[required]");
                            for (var i = 0; i < moderator_notification_file_evals.length; i++) {
                                if (moderator_notification_file_evals[i].value == '' || moderator_notification_file_evals[i].value == undefined) {
                                    alert("Please Upload Notification Letter to Moderator");
                                    moderator_notification_file_evals[i].focus();
                                    moderator_notification_file_evals[i].style.border = "medium solid red";
                                    return false;
                                }
                            } //end of for loop

                            if (frmProviderAccreditation.ciproDocument.value == "") {
                                msg = "Please Upload CIPC/DSD Document";
                                alert(msg);
                                frmProviderAccreditation.ciproDocument
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.taxDocument.value == "") {
                                msg = "Please Upload Tax Clearance Document";
                                alert(msg);
                                frmProviderAccreditation.taxDocument
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.cvDocument.value == "") {
                                msg = "Please Upload Director C.V";
                                alert(msg);
                                frmProviderAccreditation.cvDocument
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.qualificationDocument.value == "") {
                                msg = "Please Upload Certified Copies Of Qualifications";
                                alert(msg);
                                frmProviderAccreditation.qualificationDocument
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.lease_agreement.value == "") {
                                msg = "Please Upload Proof of Ownership (Utility Bill) or Lease Agreement";
                                alert(msg);
                                frmProviderAccreditation.lease_agreement
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.company_profile_and_organogram.value == "") {
                                msg = "Please Upload Company Profile and organogram";
                                alert(msg);
                                frmProviderAccreditation.company_profile_and_organogram
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.quality_management_system.value == "") {
                                msg = "Please Upload Quality Management System (QMS) ";
                                alert(msg);
                                frmProviderAccreditation.quality_management_system
                                    .focus();
                                return false;

                            } else if ($("#material").val() == "own_material" &&
                                frmProviderAccreditation.provider_learning_material.value == "") {
                                msg = "Please Upload Learning Programme Approval Report";
                                alert(msg);
                                frmProviderAccreditation.provider_learning_material
                                    .focus();
                                return false;
                            } else if ($("#skill").val() &&
                                frmProviderAccreditation.skills_programme_registration_letter.value == "") {
                                msg = "Please Upload Skills Programme Registration Letter";
                                alert(msg);
                                frmProviderAccreditation.skills_programme_registration_letter
                                    .focus();
                                return false;
                            } else if (frmProviderAccreditation.workplace_agreement.value == "") {
                                msg = "Please Upload Workplace Agreement";
                                alert(msg);
                                frmProviderAccreditation.workplace_agreement
                                    .focus();
                                return false;
                            }
                            var qualification_ids = {};
                            var q_ids = [],
                                check_limit_sum = true;
                            $(
                                    ".provider_qualification .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        q_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))
                                    });
                            $
                                .each(
                                    q_ids,
                                    function(index,
                                        value) {
                                        var line_ids = [],
                                            unit_ids = '';
                                        $(
                                                "#check_qualification_line:checked")
                                            .each(
                                                function() {
                                                    if (parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')) === q_ids[index]) {
                                                        line_ids
                                                            .push(parseInt(this.value));
                                                        unit_ids += this.value
                                                        unit_ids += ','
                                                    }

                                                });
                                        qualification_ids[q_ids[index]] = line_ids;
                                        $
                                            .ajax({
                                                url: "/hwseta/validate_minimum_credit",
                                                type: "post",
                                                async: false,
                                                data: {
                                                    'qual_ids': value,
                                                    'unit_line_ids': unit_ids
                                                },
                                                success: function(
                                                    result) {

                                                    if (result.length == 24) {
                                                        check_limit_sum = false;
                                                        alert("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!")
                                                        return false;
                                                    }
                                                },
                                            });
                                    });

                            $
                                .ajax({
                                    url: "/hwseta/qualification_assessor_moderator",
                                    type: "post",
                                    async: false,
                                    data: JSON
                                        .stringify(qualification_ids),
                                    success: function(
                                        result) {
                                        $(
                                                "#qualification_idss")
                                            .val(
                                                result
                                                .toString());

                                    },
                                });

                            var skill_ids = {};
                            var s_ids = [];
                            $(
                                    ".provider_skill .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        s_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))
                                    });
                            $
                                .each(
                                    s_ids,
                                    function(index,
                                        value) {
                                        var line_ids = [];
                                        $(
                                                "#check_skill_line:checked")
                                            .each(
                                                function() {
                                                    if (parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')) === s_ids[index]) {
                                                        line_ids
                                                            .push(parseInt(this.value));
                                                    }
                                                });
                                        skill_ids[s_ids[index]] = line_ids;
                                    });
                            $
                                .ajax({
                                    url: "/hwseta/providerAccreditation/skills",
                                    type: "post",
                                    async: false,
                                    data: JSON
                                        .stringify(skill_ids),
                                    success: function(
                                        result) {
                                        $("#skill_idss")
                                            .val(
                                                result
                                                .toString());
                                    },
                                });

                            //added by shoaib for populating learning skills on direct submit (i.e Satellite campus not checked)

                            var learning_ids = {};
                            var l_ids = [];
                            $(
                                    ".learning_skill .fs-options .fs-option.selected")
                                .each(
                                    function() {
                                        l_ids
                                            .push(parseInt($(
                                                    this)
                                                .attr(
                                                    'data-value')))
                                    });
                            $
                                .each(
                                    l_ids,
                                    function(index,
                                        value) {
                                        var line_ids = [];
                                        $(
                                                "#check_learning_line:checked")
                                            .each(
                                                function() {
                                                    if (parseInt($(
                                                                this)
                                                            .attr(
                                                                'data-value')) === l_ids[index]) {
                                                        line_ids
                                                            .push(parseInt(this.value));
                                                    }
                                                });
                                        learning_ids[l_ids[index]] = line_ids;
                                    });
                            $
                                .ajax({
                                    url: "/hwseta/providerAccreditation/learnings",
                                    type: "post",
                                    async: false,
                                    data: JSON
                                        .stringify(learning_ids),
                                    success: function(
                                        result) {
                                        $("#learning_idss")
                                            .val(
                                                result
                                                .toString());
                                    },
                                });

                            flag = true;
                        }

                        $('#frmProviderAccreditation').submit(
                            function(e) {
                                return false;
                            });
                        /*
                         * if(q_ids.length == 0){ alert("Please
                         * Select Atleast One Qualification
                         * Before Submit! "); }
                         */
                        /* else */
                        if (flag == true && check_limit_sum == true) {
                            var provider_accreditation_ref = document
                                .getElementById("provider_accreditation_ref").value;
                            $("#dialog-message-accreditation").dialog("open");
                            $('#frmProviderAccreditation').unbind('submit').submit();
                            $("#dialog-message-accreditation")
                                .append(
                                    "<p> Thank you for your Provider application. Your application will be evaluated. Your Reference Number is : " +
                                    provider_accreditation_ref +
                                    "</p>");

                            // return false;

                        }

                    });
        });

// for getting already register provider details

$(document)
    .ready(
        function() {
            $('input[name=accreditation_number]')
                .change(
                    function() {
                        accreditation_number = $(
                            '#accreditation_number').val();
                        $
                            .ajax({
                                url: "/get-accreditation-details",
                                context: document.body,
                                type: "post",
                                dataType: "json",
                                async: false,
                                data: {
                                    'accreditation_number': accreditation_number
                                },
                                success: function(result) {
                                    if (result.length > 0) {
                                        $(
                                                "#accreditation_number")
                                            .prop(
                                                'readonly',
                                                true);
                                        $(
                                                "#already_register")
                                            .attr(
                                                'onClick',
                                                'return false');
                                        $("#txtRegName")
                                            .val(
                                                result[0].name);
                                        $("#txtTradeName")
                                            .val(
                                                result[0].trading_name);
                                        $(
                                                "#txtCompanyRegNo")
                                            .val(
                                                result[0].company_registration_no);
                                        $("#txtVATRegNo")
                                            .val(
                                                result[0].vat_number);
                                        if (result[0].sic_code) {
                                            $(
                                                    "#cboOrgSICCode")
                                                .val(
                                                    result[0].sic_code)
                                                .trigger(
                                                    'change');
                                        }
                                        $(
                                                "#txtNumYearsCurrentBusiness")
                                            .val(
                                                result[0].current_business_year);
                                        $(
                                                "#txtNumStaffMembers")
                                            .val(
                                                result[0].no_of_staff);
                                        $("#material")
                                            .val(
                                                result[0].material);
                                        $("#txtCmpName")
                                            .val(
                                                result[0].name);
                                        $("#txtCmpEmail")
                                            .val(
                                                result[0].email);
                                        $("#txtCmpPhone")
                                            .val(
                                                result[0].phone);
                                        $("#txtFaxNo")
                                            .val(
                                                result[0].fax);
                                        $("#txtCmpStreet1")
                                            .val(
                                                result[0].street);
                                        $("#txtCmpStreet2")
                                            .val(
                                                result[0].street2);
                                        $("#txtCmpStreet3")
                                            .val(
                                                result[0].street3);
                                        $("#txtCmpCountry")
                                            .val(
                                                result[0].country)
                                            .trigger(
                                                'change');
                                        $("#txtCmpProvince")
                                            .val(
                                                result[0].province)
                                            .trigger(
                                                'change');
                                        $("#city")
                                            .val(
                                                result[0].city)
                                            .trigger(
                                                'change');
                                        $("#txtSuburb")
                                            .val(
                                                result[0].suburb)
                                            .trigger(
                                                'change');
                                        $("#txtCmpZip")
                                            .val(
                                                result[0].zip);
                                        // contact details
                                        $(
                                                "#txtContactNameSurname")
                                            .val(
                                                result[0].contacts[0].name);
                                        $(
                                                "#txtContactSurname")
                                            .val(
                                                result[0].contacts[0].sur_name);
                                        $(
                                                "#txtContactEmail")
                                            .val(
                                                result[0].contacts[0].email);
                                        $("#txtContactTel")
                                            .val(
                                                result[0].contacts[0].phone);
                                        $("#txtContactCell")
                                            .val(
                                                result[0].contacts[0].mobile);

                                        function qualifications() {
                                            var $def = $
                                                .Deferred();
                                            // Added
                                            // Provider
                                            // Qualification
                                            var qualification_line_ids = [];
                                            $
                                                .each(
                                                    result[0].master_qualifications,
                                                    function(
                                                        key,
                                                        value) {
                                                        $
                                                            .each(
                                                                value,
                                                                function(
                                                                    k,
                                                                    v) {
                                                                    $
                                                                        .when(
                                                                            $(
                                                                                '.provider_qualification .fs-option[data-value=' +
                                                                                k +
                                                                                ']')
                                                                            .trigger(
                                                                                'click')
                                                                            .prop(
                                                                                'disabled',
                                                                                true))
                                                                        .done(
                                                                            function() {
                                                                                $
                                                                                    .each(
                                                                                        value[k][1],
                                                                                        function(
                                                                                            a,
                                                                                            qualification_line) {
                                                                                            qualification_line_ids
                                                                                                .push(qualification_line);
                                                                                        });
                                                                            });
                                                                    $def
                                                                        .resolve(qualification_line_ids)
                                                                });
                                                    });

                                            return $def;
                                        }
                                        qualifications()
                                            .then(
                                                function(
                                                    qualification_line_ids) {
                                                    setTimeout(
                                                        function() {
                                                            $(
                                                                    "#show_qualification #check_qualification_line")
                                                                .each(
                                                                    function() {
                                                                        for (i = 0; i < qualification_line_ids.length; i++) {
                                                                            if ($(
                                                                                    this)
                                                                                .val() == qualification_line_ids[i]) {
                                                                                $(
                                                                                        this)
                                                                                    .prop(
                                                                                        'checked',
                                                                                        true);
                                                                                $(
                                                                                        this)
                                                                                    .prop(
                                                                                        'disabled',
                                                                                        true);
                                                                            }
                                                                        }
                                                                    });
                                                        },
                                                        1000)
                                                })

                                        function skills() {
                                            var $def = $
                                                .Deferred();
                                            // Added
                                            // Provider
                                            // Skills
                                            var skill_line_ids = [];
                                            $
                                                .each(
                                                    result[0].master_skills,
                                                    function(
                                                        key,
                                                        value) {
                                                        $
                                                            .each(
                                                                value,
                                                                function(
                                                                    k,
                                                                    v) {
                                                                    $
                                                                        .when(
                                                                            $(
                                                                                '.provider_skill .fs-option[data-value=' +
                                                                                k +
                                                                                ']')
                                                                            .trigger(
                                                                                'click')
                                                                            .prop(
                                                                                'disabled',
                                                                                true))
                                                                        .done(
                                                                            function() {
                                                                                $
                                                                                    .each(
                                                                                        value[k][1],
                                                                                        function(
                                                                                            a,
                                                                                            skill_line) {
                                                                                            skill_line_ids
                                                                                                .push(skill_line);
                                                                                        });
                                                                            });
                                                                    $def
                                                                        .resolve(skill_line_ids)
                                                                });
                                                    });
                                            return $def;
                                        }

                                        skills()
                                            .then(
                                                function(
                                                    skill_line_ids) {
                                                    setTimeout(
                                                        function() {
                                                            $(
                                                                    "#show_skills #check_skill_line")
                                                                .each(
                                                                    function() {
                                                                        for (i = 0; i < skill_line_ids.length; i++) {
                                                                            if ($(
                                                                                    this)
                                                                                .val() == skill_line_ids[i]) {
                                                                                $(
                                                                                        this)
                                                                                    .prop(
                                                                                        'checked',
                                                                                        true);
                                                                                $(
                                                                                        this)
                                                                                    .prop(
                                                                                        'disabled',
                                                                                        true);
                                                                            }
                                                                        }
                                                                    });
                                                        },
                                                        1000)
                                                })

                                        // Added Provider
                                        // Assessors
                                        $
                                            .each(
                                                result[0].assessors,
                                                function(
                                                    key,
                                                    value) {
                                                    $
                                                        .when(
                                                            $(
                                                                '#add_assessor_number')
                                                            .val(
                                                                value['name']))
                                                        .done(
                                                            function() {
                                                                $(
                                                                        "#add_assessor")
                                                                    .trigger(
                                                                        'click');
                                                            });
                                                });

                                        // Added Provider
                                        // Moderators
                                        $
                                            .each(
                                                result[0].moderators,
                                                function(
                                                    key,
                                                    value) {
                                                    $
                                                        .when(
                                                            $(
                                                                '#add_moderator_number')
                                                            .val(
                                                                value['name']))
                                                        .done(
                                                            function() {
                                                                $(
                                                                        "#add_moderator")
                                                                    .trigger(
                                                                        'click');
                                                            });
                                                });

                                    } else if (result.length === 0) {
                                        alert('Please Enter Valid Accreditation Number!!');
                                        document.frmProviderAccreditation.accreditation_number
                                            .focus();
                                        document.frmProviderAccreditation.accreditation_number.value = ""
                                    }
                                },
                            });

                    });

            $('#accreditation_number').hide();

            $("#already_register").change(function() {
                if (this.checked) {
                    $('#accreditation_number').show();
                } else {
                    $('#accreditation_number').hide();
                }
            });

        });

$(document)
    .ready(
        function() {
            // called when key is pressed in textbox
            $(
                    "#txtCmpPhone,#txtFaxNo,#txtContactTel,#txtContactCell,#txtNumStaffMembers,#ID1_phone,#ID1_fax,#ID1_txtContactTel,#ID1_txtContactCell")
                .keypress(
                    function(e) {
                        // if the letter is not digit then
                        // display error and don't type anything
                        if (e.which != 8 &&
                            e.which != 0 &&
                            (e.which < 48 || e.which > 57)) {
                            // display error message
                            alert("Please Enter Digits Only");
                            return false;
                        }
                    });
            // To set learning material doc mandatory
            $('#material').change(
                function() {
                    if (this.value == "own_material") {
                        $('#learning_material_font').attr("color",
                            "#FF0000");
                    } else if (this.value == "hwseta_material") {
                        $('#learning_material_font').attr("color",
                            "#F7F7EF");
                    }
                });
            // To set skills programme registration letter mandatory
            $('#skill').change(
                function() {
                    if ($('#skill').val()) {
                        $('#skills_programme_registration_font')
                            .attr("color", "#FF0000");
                    } else {
                        $('#skills_programme_registration_font')
                            .attr("color", "#F7F7EF");
                    }
                });
        });