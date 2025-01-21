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
function clearFilters() {
    document.getElementById('provider-filter').value = '';
    // Optional: Logik für das Zurücksetzen der Tabelle einfügen
    alert('Filter gelöscht!');
}

function openProviderDetails() {
    alert('Signalgeber-Details öffnen (noch in Entwicklung)');
}
function openAddProviderModal() {
    document.getElementById('add-provider-modal').style.display = 'block';
}

function closeAddProviderModal() {
    document.getElementById('add-provider-modal').style.display = 'none';
}

document.getElementById('add-provider-form').onsubmit = function(event) {
    event.preventDefault();
    const name = document.getElementById('provider-name').value;
    const platform = document.getElementById('provider-platform').value;

    const tableBody = document.getElementById('provider-table-body');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>${name}</td>
        <td class="positive">0.00</td>
        <td class="positive">N/A</td>
        <td class="positive">$0.00</td>
        <td class="positive">0.00%</td>
        <td><button onclick="openProviderDetails()">Details</button></td>
    `;
    tableBody.appendChild(newRow);

    closeAddProviderModal();
};
