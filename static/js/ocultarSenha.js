document.addEventListener("DOMContentLoaded", () => {
    const checkbox = document.getElementById("mostrarSenha");
    const camposSenha = document.querySelectorAll(".senha");

    checkbox.addEventListener("change", () => {
        camposSenha.forEach((campo) => {
            campo.type = checkbox.checked ? "text" : "password";
        });
    });
});