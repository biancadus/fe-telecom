document.addEventListener("DOMContentLoaded", () => {
    const checkbox = document.getElementById("mostrarSenha");
    // Ele vai buscar todos os elementos que têm a classe 'senha'
    const camposSenha = document.querySelectorAll(".senha");

    if (checkbox) {
        checkbox.addEventListener("change", () => {
            camposSenha.forEach((campo) => {
                if (checkbox.checked) {
                    campo.type = "text";
                } else {
                    campo.type = "password";
                }
            });
        });
    }
});