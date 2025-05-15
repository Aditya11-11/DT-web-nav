function ajaxFunction() {
    var e = "",
        n = !0;
    if ("" == document.getElementById("name").value && (e += "* Please Enter Name\n"), "" == document.getElementById("company").value && (e += "* Please Enter Company Name\n"), "" == document.getElementById("emailid").value && (e += "* Please Enter Email Address\n"), "" == document.getElementById("phone").value && (e += "* Please Enter Phone No\n"), "" == document.getElementById("message").value && (e += "* Please Enter Message\n"), "" == document.getElementById("txtAns").value && (e += "* Please Enter Security Answer\n"), e.length > 0 && (n = !1), n) {
        var t;
        if (validateEmail().length > 0) return !1;
        if (ToCellValidate().length > 0) return !1;
        if (checkAnswer().length > 0) return !1;
        document.getElementById("lblMessage").innerHTML = "<b>Under Process ..........</b>";
        try {
            t = new XMLHttpRequest
        } catch (e) {
            try {
                t = new ActiveXObject("Msxml2.XMLHTTP")
            } catch (e) {
                try {
                    t = new ActiveXObject("Microsoft.XMLHTTP")
                } catch (e) {
                    return !1
                }
            }
        }
        t.onreadystatechange = function() {
            4 == t.readyState && (document.getElementById("ajaxDiv").innerHTML = t.responseText)
        };
        var a = "?name=" + document.getElementById("name").value + "&company=" + document.getElementById("company").value + "&emailid=" + document.getElementById("emailid").value + "&phone=" + document.getElementById("phone").value + "&message=" + document.getElementById("message").value;
        t.open("GET", "sendmail_cdo.asp" + a, !0), t.send(null), document.getElementById("lblMessage").innerHTML = "", window.location.href = "thankyou.html"
    } else alert(e)
}

function validateEmail() {
    var e, n = "",
        t = (e = document.getElementById("emailid").value).indexOf("@"),
        a = e.lastIndexOf(".");
    return t < 1 || a < t + 2 || a + 2 >= e.length ? (alert("Not a valid e-mail address"), n = "Not a valid e-mail address") : n = "", n
}
var d, lblRadomValue, lblRadomValue1, my_num, val = "";

function setLabelValue() {
    return my_num = Math.random(), val = Math.floor(11 * my_num), lblRadomValue = d.getElementById("lblRadom"), lblRadomValue1 = d.getElementById("lblRadom1"), lblRadomValue.innerHTML = val, lblRadomValue1.innerHTML = val, val
}
//function checkAnswer(){var e="";return val+val!=d.getElementById("txtAns").value?(alert("please enter correct answer for security question"),e="please enter correct answer for security question"):e="",e}
function ToCellValidate() {
    var e, n, t = "";
    "" != (e = document.getElementById("phone").value) && (trimSpace(n = e).length < 8 || trimSpace(n).length > 15 || -1 != n.search(/[^0-9\-()+]/g) ? (alert("Please enter valid phone number (8-15 numbers)"), t = "Please enter valid phone number (8-15 numbers)") : t = "");
    return t
}

function trimSpace(e) {
    return e.replace(/^\s+|\s+$/g, "")
}

function blockSpecilchar(e) {
    return !0
}
d = document;