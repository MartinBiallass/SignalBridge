document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".sidebar a");
    const activeSection = document.body.dataset.section;

    links.forEach(link => {
        const section = link.dataset.section;
        if (section === activeSection) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
});

function changeLanguage() {
    const form = document.getElementById("language-form");
    form.submit();
}
