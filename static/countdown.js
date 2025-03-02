document.addEventListener("DOMContentLoaded", function () {
    function startCountdown(durationInSeconds) {
        let timer = durationInSeconds;
        let countdownElement = document.getElementById("countdown");
        let extendContainer = document.getElementById("extend-container");

        function updateCountdown() {
            let days = Math.floor(timer / (24 * 3600));
            let hours = Math.floor((timer % (24 * 3600)) / 3600);
            let minutes = Math.floor((timer % 3600) / 60);
            let seconds = timer % 60;

            countdownElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;

            if (timer <= 0) {
                countdownElement.innerHTML = "Abo abgelaufen!";
                countdownElement.classList.add("warning");
                extendContainer.style.display = "block";
            } else if (timer < 259200) { // Weniger als 3 Tage
                countdownElement.classList.add("warning");
                extendContainer.style.display = "block";
            } else {
                countdownElement.classList.remove("warning");
            }

            if (timer > 0) {
                timer--;
                setTimeout(updateCountdown, 1000);
            }
        }

        updateCountdown();
    }

    function extendSubscription() {
        let selectedPlan = document.getElementById("plan-select").value;
        alert(`Abo wird um: ${selectedPlan} verlängert!`);
        // Hier könnte später die API-Anbindung erfolgen
    }

    // Countdown starten (Standard: 5 Tage = 432000 Sekunden)
    startCountdown(432000);

    // Event Listener für den Verlängerungs-Button
    document.getElementById("extend-button").addEventListener("click", extendSubscription);
});
