function al() {
   alert("works!")
}

 function log_training(text,form_number) {
    var xhr =new XMLHttpRequest()
    var fd = new FormData(document.forms[form_number])
    fd.append("log_text","completed training " + text)
    xhr.onreadystatechange = function() {
     if (this.readyState == 4) {
       if (this.status != 200) {
        console.log(this.responseText)
       }
     }
   }
   var url = "http://" + location.host + "/api/logs/"
   xhr.open("POST",url,true)
   xhr.send(fd)   
  }





