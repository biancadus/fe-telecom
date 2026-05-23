document.querySelector('.wpp-mask').addEventListener('input', function (e) {
  let value = e.target.value.replace(/\D/g, "");

  if (value.length > 11) value = value.slice(0, 11);

  let formatted = "";

  if (value.length > 0) formatted += "(" + value.substring(0, 2);
  if (value.length >= 3) formatted += ") " + value.substring(2, 7);
  if (value.length >= 8) formatted += "-" + value.substring(7);

  e.target.value = formatted;
});