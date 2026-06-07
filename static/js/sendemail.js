function abrirModal() {
  document.getElementById("modalEnvio").style.display = "flex";
}

function fecharModal() {
  document.getElementById("modalEnvio").style.display = "none";
}

function gerarIdPedido() {
  return "#" + Math.floor(10000 + Math.random() * 90000);
}

function enviarPedido() {
  const form = document.getElementById("formContato");

  const nome = form[0].value;
  const email = form[1].value;
  const telefone = form[2].value;
  const servico = form[3].value;
  const data = form[4].value;
  const horario = form[5].value;
  const detalhes = form[6].value;

  const idPedido = gerarIdPedido();

  abrirModal();
  document.getElementById("modalLoading").style.display = "block";
  document.getElementById("modalLoading").className = "loading";
  document.getElementById("modalMensagem").textContent = "Enviando seu pedido...";

  emailjs.send("service_m9l5auo", "template_o2p4im9", {
    id_pedido: idPedido,
    nome: nome,
    email: email,
    telefone: telefone,
    servico: servico,
    data: data,
    horario: horario,
    detalhes: detalhes
  })
  .then(() => {
      setTimeout(() => {
        document.getElementById("modalLoading").style.display = "none";
        document.getElementById("modalLoading").className = "";

        document.getElementById("modalLoading").innerHTML = "";
        document.getElementById("modalLoading").outerHTML = '<div id="modalLoading" class="ok">✔</div>';

        document.getElementById("modalMensagem").innerHTML = 
          "Pedido enviado com sucesso!<br>ID: <strong>" + idPedido + "</strong>";

        document.getElementById("btnFecharModal").style.display = "inline-block";
      }, 800);
  })
  .catch(() => {
      document.getElementById("modalMensagem").textContent =
        "Erro ao enviar o pedido. Tente novamente mais tarde.";

      document.getElementById("modalLoading").style.display = "none";
      document.getElementById("btnFecharModal").style.display = "inline-block";
  });
}
