const checkbox = document.getElementById("mostrarSenha");

const camposSenha = document.querySelectorAll(".senha");

checkbox.addEventListener("change", () => {

    camposSenha.forEach((campo) => {

        if (checkbox.checked) {
            campo.type = "text";
        } else {
            campo.type = "password";
        }

    });

});