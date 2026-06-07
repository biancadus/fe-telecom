const faqButtons = document.querySelectorAll(".faq-question");
  const searchInput = document.querySelector(".barra-pesquisa input");
  let currentlyOpen = null;

  faqButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const answer = btn.nextElementSibling;
      const icon = btn.querySelector(".icon");

      if (currentlyOpen && currentlyOpen !== answer) {
        currentlyOpen.classList.remove("open");
        currentlyOpen.previousElementSibling.querySelector(".icon").textContent = "+";
      }

      answer.classList.toggle("open");
      icon.textContent = answer.classList.contains("open") ? "-" : "+";

      currentlyOpen = answer.classList.contains("open") ? answer : null;
    });
  });

  // ======== FILTRO DE PESQUISA ========
  searchInput.addEventListener("input", () => {
    const termo = searchInput.value.toLowerCase();

    document.querySelectorAll(".faq-item").forEach(item => {
      const pergunta = item.querySelector(".faq-question").textContent.toLowerCase();

      if (pergunta.includes(termo)) {
        item.classList.remove("hidden");
      } else {
        item.classList.add("hidden");

        const answer = item.querySelector(".faq-answer");
        if (answer.classList.contains("open")) {
          answer.classList.remove("open");
          answer.previousElementSibling.querySelector(".icon").textContent = "+";
          currentlyOpen = null;
        }
      }
    });
  });