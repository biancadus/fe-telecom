
window.sendEmail = function(subject="test", body, mail="test@gmail.com") {
  var link = 'mailto:${mail}'
   + "?cc=fetelecomservices@gmail.com"
           + "&subject=" + encodeURIComponent(`${subject}`)
           + "&body=" + encodeURIComponent(`${body}`)
  ;
  window.location.href = link;
 console.log(link);

}