    function toggleSenha() {
      const senha = document.getElementById("senha");
      senha.type = senha.type === "password" ? "text" : "password";
    }

    function toggleConfirmarSenha() {
    const confirmar = document.getElementById("confirmarSenha");
    confirmar.type = confirmar.type === "password" ? "text" : "password";
    }