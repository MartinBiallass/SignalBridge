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
