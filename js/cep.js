    const cepInput = document.getElementById('cep');
  const enderecoInput = document.getElementById('endereco');
  const complementoInput = document.getElementById('complemento');

  cepInput.addEventListener("blur", async () => {
    let cep = cepInput.value.replace(/\D/g, "");

    if (cep.length !== 8) return; 

    try {
      let response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
      let data = await response.json();

      if (data.erro) {
        alert("CEP não encontrado!");
        return;
      }

      enderecoInput.value = `${data.logradouro}, ${data.bairro}, ${data.localidade} - ${data.uf}`;

      complementoInput.value = data.complemento || "";
    } 
    catch (error) {
      console.error("Erro ao buscar CEP:", error);
      alert("Erro ao consultar CEP.");
    }
  });
