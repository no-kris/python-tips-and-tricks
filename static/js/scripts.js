const toggler = document.querySelector(".navbar-toggler");
const navbarCollapse = document.querySelector(".navbar-collapse");
const body = document.body;

toggler.addEventListener("click", function () {
  const isOpen = navbarCollapse.classList.toggle("show");
  toggler.classList.toggle("active");
  body.style.overflow = isOpen ? "hidden" : "visible";
});

// Close menu when a link is clicked
document.querySelectorAll(".navbar-link, .navbar-btn").forEach((link) => {
  link.addEventListener("click", () => {
    navbarCollapse.classList.remove("show");
    toggler.classList.remove("active");
    body.style.overflow = "visible";
  });
});
