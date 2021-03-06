
function ajax_post(form_name, operation, safe = false) {
  event.preventDefault()
  if (safe == true) {
    response = confirm("Are you sure?")
    if (response == false) {
      console.log(response)
      return
    }
  }
  var xhr = new XMLHttpRequest()
  var fd = new FormData(document.forms[form_name])
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      if (this.status != 200) {
        console.log(this.responseText)
        console.log(this.status)
      }
    }
  }
  var url = location.href
  xhr.open("POST", url, true)
  xhr.setRequestHeader("operation", operation)
  xhr.send(fd)
}

/////////////////////////////////////////////////////////////////////////
function log_training(training_name, form_number, quantity = undefined) {
  var xhr = new XMLHttpRequest()
  var fd = new FormData(document.forms[form_number])
  if (quantity == undefined) {
    var log_text = "completed training " + String(training_name)
  }
  else {
    var log_text = "completed training " + String(training_name) + " with " + String(quantity) + " words";
  }
  fd.append("log_text", log_text)
  xhr.onreadystatechange = function () {
    if (this.readyState == 4) {
      if (this.status != 200) {
        console.log(this.responseText)
      }
    }
  }
  var url = "http://" + location.host + "/api/logs/"
  xhr.open("POST", url, true)
  xhr.send(fd)
}
/////////////////////////////////////////////////////////////////////////////
function complete_training(training_name, form_number) {
  var xhr = new XMLHttpRequest()
  var fd = new FormData(document.forms[form_number])
  fd.append("training", training_name)
  xhr.onreadystatechange = function () {
    if (this.readyState == 4) {
      if (this.status != 200) {
        console.log(this.responseText)
      }
    }
  }
  var url = "http://" + location.host + "/trainings/"
  xhr.open("POST", url, true)
  xhr.send(fd)
}
//////////////////////////////////////////////////////////////////////////
function send_word_to_training(words) {
  if (words.length == 0) {
    return
  }
  var xhr = new XMLHttpRequest()
  var fd = new FormData(document.forms[0])
  id_string = build_id_array(words)
  fd.append("words_to_training", id_string)
  xhr.onreadystatechange = function () {
    if (this.readyState == 4) {
      if (this.status != 200) {
        alert("The word wasn't sent. Some error on server occured!")
        console.log(this.responseText)
      }
    }
  }
  var url = "http://" + location.host + "/dictionary/"
  xhr.open("POST", url, true)
  xhr.setRequestHeader("operation", "words_to_training")
  xhr.send(fd)
}

function build_id_array(words) {
  id_string = "["
  for (var ind in words) {
    id_string = id_string + words[Number(ind)].id.toString()
  }
  id_string = id_string + "]"
  return id_string
}




function ajax_get_sync(action, key=undefined, parameters=undefined) {
  var xhr = new XMLHttpRequest()
  var url_str = window.location.href
  url_str = url_str + get_params_string(parameters)
  xhr.open("GET", url_str, false)
  xhr.setRequestHeader("action", action)
  xhr.send(null)
  var response = xhr.responseText
  if (key == undefined) {
    var value = JSON.parse(response)
  }
  else {
    var value = JSON.parse(response)[key]
  }
  return value
}


function get_params_string(params) {
  if (params != undefined) {
    var params_str = "?"
    for (var x in params) {
      if (params_str == "?") {
        params_str = params_str + x + "=" + params[x]
      }
      else {
        params_str = params_str + "&" + x + "=" + params[x]
      }
    }
    return params_str
  }
  else {
    return ""
  }
}
