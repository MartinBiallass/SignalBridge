document.addEventListener("DOMContentLoaded", function () {
    // Sidebar Navigation
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

    // Change Language Form Submission
    function changeLanguage() {
        const form = document.getElementById("language-form");
        form.submit();
    }

    // Take Profit Levels Logic
    const tpLevelsContainer = document.getElementById("tp-levels-container");
    const addTpLevelButton = document.getElementById("add-tp-level");
    const distributeEquallyButton = document.getElementById("distribute-equally");

    let tpLevels = [
        { id: 1, percentage: 20 },
        { id: 2, percentage: 20 },
        { id: 3, percentage: 20 },
        { id: 4, percentage: 20 },
        { id: 5, percentage: 20 }
    ];

    function renderTpLevels() {
        tpLevelsContainer.innerHTML = ""; // Clear existing levels
        tpLevels.forEach((level, index) => {
            const tpRow = document.createElement("div");
            tpRow.classList.add("tp-row");
            tpRow.innerHTML = `
                <span>TP ${index + 1}</span>
                <input type="number" value="${level.percentage}" class="tp-percentage" /> %
                <button class="btn-green" onclick="openTpDetails(${index})">Details</button>
                <button class="btn-red" onclick="removeTpLevel(${index})">Remove</button>
            `;
            tpLevelsContainer.appendChild(tpRow);
        });
    }

    function addTpLevel() {
        tpLevels.push({ id: tpLevels.length + 1, percentage: 20 });
        renderTpLevels();
    }

    function removeTpLevel(index) {
        tpLevels.splice(index, 1); // Remove the TP level
        renderTpLevels();
    }

    function distributeEqually() {
        const equalPercentage = (100 / tpLevels.length).toFixed(2);
        tpLevels.forEach(level => level.percentage = equalPercentage);
        renderTpLevels();
    }

    // Open Details Modal for a Specific TP Level
    window.openTpDetails = function (index) {
        const modal = document.getElementById("tp-details-modal");
        const modalContent = document.getElementById("tp-details-content");
        modal.style.display = "block";

        const level = tpLevels[index];
        modalContent.innerHTML = `
            <h3>Details for TP ${index + 1}</h3>
            <label>Percentage:</label>
            <input type="number" value="${level.percentage}" class="tp-details-percentage" />
            <button class="btn-green" onclick="saveTpDetails(${index})">Save</button>
            <button class="btn-red" onclick="closeTpModal()">Close</button>
        `;
    };

    // Save Changes from the Modal
    window.saveTpDetails = function (index) {
        const modalPercentage = document.querySelector(".tp-details-percentage").value;
        tpLevels[index].percentage = parseFloat(modalPercentage);
        closeTpModal();
        renderTpLevels();
    };

    // Close the Modal
    function closeTpModal() {
        const modal = document.getElementById("tp-details-modal");
        modal.style.display = "none";
    }

    // Event Listeners
    addTpLevelButton.addEventListener("click", addTpLevel);
    distributeEquallyButton.addEventListener("click", distributeEqually);

    renderTpLevels(); // Initial render
});
// Event-Listener für Klick auf "Aktion"
document.querySelector('.horizontal-menu-item:first-child').addEventListener('click', function () {
    const aktionSection = document.getElementById('aktion-section');
    // Blendet den Bereich ein/aus
    if (aktionSection.style.display === 'none' || !aktionSection.style.display) {
        aktionSection.style.display = 'block';
        window.scrollTo({
            top: aktionSection.offsetTop - 50, // Scrollt zum Bereich mit einem kleinen Offset
            behavior: 'smooth'
        });
    } else {
        aktionSection.style.display = 'none';
    }
});
// Modal öffnen
document.getElementById('info-update-sl').addEventListener('click', function () {
    document.getElementById('modal-update-sl').style.display = 'block';
});

// Modal schließen
document.getElementById('close-modal-update-sl').addEventListener('click', function () {
    document.getElementById('modal-update-sl').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-update-sl');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für TP
document.getElementById('info-update-tp').addEventListener('click', function () {
    document.getElementById('modal-update-tp').style.display = 'block';
});

// Modal schließen für TP
document.getElementById('close-modal-update-tp').addEventListener('click', function () {
    document.getElementById('modal-update-tp').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-update-tp');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für ENTRYPOINT
document.getElementById('info-update-entrypoint').addEventListener('click', function () {
    document.getElementById('modal-update-entrypoint').style.display = 'block';
});

// Modal schließen für ENTRYPOINT
document.getElementById('close-modal-update-entrypoint').addEventListener('click', function () {
    document.getElementById('modal-update-entrypoint').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-update-entrypoint');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Schließen des Signals
document.getElementById('info-close-signal').addEventListener('click', function () {
    document.getElementById('modal-close-signal').style.display = 'block';
});

// Modal schließen für Schließen des Signals
document.getElementById('close-modal-close-signal').addEventListener('click', function () {
    document.getElementById('modal-close-signal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-close-signal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// SCHLIESSE Modal Logik
const closeSignalInfo = document.getElementById("close-signal-info");
const closeSignalModal = document.getElementById("close-signal-modal");
const closeSignalModalClose = document.getElementById("close-signal-modal-close");

closeSignalInfo.addEventListener("click", () => {
    closeSignalModal.style.display = "block";
});

closeSignalModalClose.addEventListener("click", () => {
    closeSignalModal.style.display = "none";
});

// Klick außerhalb des Modals schließt es
window.addEventListener("click", (event) => {
    if (event.target === closeSignalModal) {
        closeSignalModal.style.display = "none";
    }
});
document.addEventListener("DOMContentLoaded", function () {
    // Bestehende Logik bleibt hier unverändert

    // Event-Listener für Klick auf "SCHLIESSE"
    const closeSignalInfo = document.getElementById("close-signal-info");
    const closeSignalModal = document.getElementById("close-signal-modal");
    const closeSignalModalClose = document.getElementById("close-signal-modal-close");

    closeSignalInfo.addEventListener("click", () => {
        closeSignalModal.style.display = "block";
    });

    closeSignalModalClose.addEventListener("click", () => {
        closeSignalModal.style.display = "none";
    });

    // Klick außerhalb des Modals schließt es
    window.addEventListener("click", (event) => {
        if (event.target === closeSignalModal) {
            closeSignalModal.style.display = "none";
        }
    });

    // Sicherstellen, dass andere Modal-Elemente unabhängig bleiben
    const modals = document.querySelectorAll(".modal");
    window.addEventListener("click", (event) => {
        modals.forEach((modal) => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
});
// Modal öffnen für SCHLIESSE HALBE
document.getElementById('close-half-lot-info').addEventListener('click', function () {
    document.getElementById('close-half-lot-modal').style.display = 'block';
});

// Modal schließen für SCHLIESSE HALBE
document.getElementById('close-half-lot-modal-close').addEventListener('click', function () {
    document.getElementById('close-half-lot-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('close-half-lot-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Debugging für Modal-Anzeige
const modals = document.querySelectorAll('.modal');
modals.forEach(modal => {
    console.log('Modal gefunden:', modal.id);
});

// Funktion für Öffnen und Schließen
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    } else {
        console.error('Modal nicht gefunden:', modalId);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    } else {
        console.error('Modal nicht gefunden:', modalId);
    }
}
// Modal öffnen für "SCHLIESSE HALBE (Nur im Gewinn)"
document.getElementById('close-half-lot-profit-only-info').addEventListener('click', function () {
    document.getElementById('close-half-lot-profit-only-modal').style.display = 'block';
});

// Modal schließen für "SCHLIESSE HALBE (Nur im Gewinn)"
document.getElementById('close-half-lot-profit-only-modal-close').addEventListener('click', function () {
    document.getElementById('close-half-lot-profit-only-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('close-half-lot-profit-only-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für "SL zum Einstieg"
document.getElementById('move-sl-entry-info').addEventListener('click', function () {
    document.getElementById('move-sl-entry-modal').style.display = 'block';
});

// Modal schließen für "SL zum Einstieg"
document.getElementById('move-sl-entry-modal-close').addEventListener('click', function () {
    document.getElementById('move-sl-entry-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('move-sl-entry-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Entferne SL
document.getElementById('remove-sl-info').addEventListener('click', function () {
    document.getElementById('remove-sl-modal').style.display = 'block';
});

// Modal schließen für Entferne SL
document.getElementById('remove-sl-modal-close').addEventListener('click', function () {
    document.getElementById('remove-sl-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('remove-sl-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Schließe ausstehende Order
document.getElementById('close-pending-order-info').addEventListener('click', function () {
    document.getElementById('close-pending-order-modal').style.display = 'block';
});

// Modal schließen für Schließe ausstehende Order
document.getElementById('close-pending-order-modal-close').addEventListener('click', function () {
    document.getElementById('close-pending-order-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('close-pending-order-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Schließe ausstehende Order
document.getElementById('close-pending-order-info').addEventListener('click', function () {
    document.getElementById('close-pending-order-modal').style.display = 'block';
});
// Modal öffnen für Eine schwebende Order auslösen
document.getElementById('trigger-pending-order-info').addEventListener('click', function () {
    document.getElementById('trigger-pending-order-modal').style.display = 'block';
});

// Modal schließen für Eine schwebende Order auslösen
document.getElementById('trigger-pending-order-modal-close').addEventListener('click', function () {
    document.getElementById('trigger-pending-order-modal').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('trigger-pending-order-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Ändere SL
document.getElementById('info-change-sl-exist').addEventListener('click', function () {
    document.getElementById('modal-change-sl-exist').style.display = 'block';
});

// Modal schließen für Ändere SL
document.getElementById('close-modal-change-sl-exist').addEventListener('click', function () {
    document.getElementById('modal-change-sl-exist').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-change-sl-exist');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
/// Modal öffnen für Ändere TP
document.getElementById('info-change-tp-exist').addEventListener('click', function () {
    document.getElementById('modal-change-tp-exist').style.display = 'block';
});

// Modal schließen für Ändere TP
document.getElementById('close-modal-change-tp-exist').addEventListener('click', function () {
    document.getElementById('modal-change-tp-exist').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-change-tp-exist');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Ändere Eintrittspunkt
document.getElementById('info-change-entry-exist').addEventListener('click', function () {
    document.getElementById('modal-change-entry-exist').style.display = 'block';
});

// Modal schließen für Ändere Eintrittspunkt
document.getElementById('close-modal-change-entry-exist').addEventListener('click', function () {
    document.getElementById('modal-change-entry-exist').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-change-entry-exist');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Wieder Eintritt
document.getElementById('info-retry-entry').addEventListener('click', function () {
    document.getElementById('modal-retry-entry').style.display = 'block';
});

// Modal schließen für Wieder Eintritt
document.getElementById('close-modal-retry-entry').addEventListener('click', function () {
    document.getElementById('modal-retry-entry').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-retry-entry');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Schliesse
document.getElementById('info-close-entry').addEventListener('click', function () {
    document.getElementById('modal-close-entry').style.display = 'block';
});

// Modal schließen für Schliesse
document.getElementById('close-modal-close-entry').addEventListener('click', function () {
    document.getElementById('modal-close-entry').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-close-entry');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Ändere SL zum Eintrittspunkt
document.getElementById('info-change-sl-entrypoint').addEventListener('click', function () {
    document.getElementById('modal-change-sl-entrypoint').style.display = 'block';
});

// Modal schließen für Ändere SL zum Eintrittspunkt
document.getElementById('close-modal-change-sl-entrypoint').addEventListener('click', function () {
    document.getElementById('modal-change-sl-entrypoint').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-change-sl-entrypoint');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});
// Modal öffnen für Ändere SL
document.getElementById('info-change-sl').addEventListener('click', function () {
    document.getElementById('modal-change-sl').style.display = 'block';
});

// Modal schließen für Ändere SL
document.getElementById('close-modal-change-sl').addEventListener('click', function () {
    document.getElementById('modal-change-sl').style.display = 'none';
});

// Modal schließen, wenn außerhalb geklickt wird
window.addEventListener('click', function (event) {
    const modal = document.getElementById('modal-change-sl');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});