console.log("script.js loaded");

const scanBtn = document.querySelector(".scan-btn");
const resultText = document.getElementById("stressText");
const emojis = document.querySelectorAll(".emoji");

const avoidEl = document.getElementById("avoid");
const alterEl = document.getElementById("alter");
const adaptEl = document.getElementById("adapt");

let scanning = false;
let timer = null;

// emoji glow
function glow(level) {
    emojis.forEach(e => e.classList.remove("active"));

    if (level === "HIGH")
        document.getElementById("emoji-high").classList.add("active");

    if (level === "MODERATE")
        document.getElementById("emoji-moderate").classList.add("active");

    if (level === "LOW")
        document.getElementById("emoji-low").classList.add("active");
}

// analyze call
async function analyze() {
    console.log("Calling /analyze");

    const res = await fetch("/analyze");
    const data = await res.json();
    console.log(data);

    if (data.status === "scanning") {
        resultText.innerText =
            `${data.stress_level} Stress: ${data.stress_percent}% (scanning...)`;

        document.getElementById("progressBar").style.width =
            data.stress_percent + "%";

        if (data.stress_level === "HIGH")
            document.getElementById("progressBar").style.background = "red";
        else if (data.stress_level === "MODERATE")
            document.getElementById("progressBar").style.background = "orange";
        else
            document.getElementById("progressBar").style.background = "lime";

        glow(data.stress_level);
        showSolutions(data.stress_level);
        return;
    }

    if (data.status === "locked") {
        clearInterval(timer);
        scanning = false;

        resultText.innerText =
            `${data.stress_level} Stress: ${data.stress_percent}%`;

        document.getElementById("progressBar").style.width =
            data.stress_percent + "%";

        if (data.stress_level === "HIGH")
            document.getElementById("progressBar").style.background = "red";
        else if (data.stress_level === "MODERATE")
            document.getElementById("progressBar").style.background = "orange";
        else
            document.getElementById("progressBar").style.background = "lime";

        document.getElementById("solutionBtn").style.display = "inline-block";

        // store suggestions globally
        window.latestSuggestions = data.suggestions || {
            avoid: "No suggestion",
            alter: "No suggestion",
            adapt: "No suggestion"
        };
        glow(data.stress_level);

        // STEP 3 - Card color
        const card = document.querySelector(".right");

        if (data.stress_level === "HIGH") {
            card.style.border = "1px solid #ef4444";
        }
        else if (data.stress_level === "MODERATE") {
            card.style.border = "1px solid #f59e0b";
        }
        else {
            card.style.border = "1px solid #4ade80";
        }

        // STEP 4 - Delayed reveal
        avoidEl.innerText = "...";
        alterEl.innerText = "...";
        adaptEl.innerText = "...";

        setTimeout(() => {
            avoidEl.innerText = window.latestSuggestions.avoid;
        }, 300);

        setTimeout(() => {
            alterEl.innerText = window.latestSuggestions.alter;
        }, 600);

        setTimeout(() => {
            adaptEl.innerText = window.latestSuggestions.adapt;
        }, 900);
    }
}

// START SCAN — ONLY HERE
scanBtn.addEventListener("click", async () => {
    if (scanning) return;

    scanning = true;

    resultText.innerText = "Scanning...";
    emojis.forEach(e => e.classList.remove("active"));

    document.getElementById("progressBar").style.width = "0%";
    document.querySelector(".right").style.border = "none";
    document.getElementById("solutionBtn").style.display = "none";

    await fetch("/reset");
    timer = setInterval(analyze, 1000);
});

const solutionBtn = document.getElementById("solutionBtn");

const modal = document.querySelector(".modal-overlay");
const closeBtn = document.querySelector(".modal-close");

// Open modal
solutionBtn.addEventListener("click", () => {
    modal.classList.add("active");
});

// Close modal
closeBtn.addEventListener("click", () => {
    modal.classList.remove("active");
});

// Close when clicking outside card
modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("active");
    }
});

closeModal.onclick = function () {
    modal.style.display = "none";
};

window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
};

function showSolutions(level){

    const solutionContent = document.getElementById("solutionContent");

    let content = "";

    if(level === "HIGH"){

        content = `
        <div class="section">
        <h4>🚫 Avoid</h4>
        <p>Avoid stressful environments or situations that increase pressure.</p>
        </div>

        <div class="section">
        <h4>⚖ Alter</h4>
        <p>Reorganize tasks or take a break from heavy workload.</p>
        </div>

        <div class="section">
        <h4>🌿 Adapt</h4>
        <p>Practice meditation, breathing exercises, or relaxation.</p>
        </div>

        <div class="section">
        <h4>🤝 Accept</h4>
        <p>Accept things beyond control and seek support if needed.</p>
        </div>
        `;
    }

    else if(level === "MODERATE"){

        content = `
        <div class="section">
        <h4>🚫 Avoid</h4>
        <p>Avoid distractions like excessive phone usage.</p>
        </div>

        <div class="section">
        <h4>⚖ Alter</h4>
        <p>Adjust workload and prioritize important tasks.</p>
        </div>

        <div class="section">
        <h4>🌿 Adapt</h4>
        <p>Take short breaks or practice deep breathing.</p>
        </div>

        <div class="section">
        <h4>🤝 Accept</h4>
        <p>Accept temporary challenges calmly.</p>
        </div>
        `;
    }

    else{

        content = `
        <div class="section">
        <h4>🚫 Avoid</h4>
        <p>Avoid overcommitting or unnecessary pressure.</p>
        </div>

        <div class="section">
        <h4>⚖ Alter</h4>
        <p>Maintain a balanced routine.</p>
        </div>

        <div class="section">
        <h4>🌿 Adapt</h4>
        <p>Continue healthy habits like exercise and good sleep.</p>
        </div>

        <div class="section">
        <h4>🤝 Accept</h4>
        <p>Accept daily challenges positively.</p>
        </div>
        `;
    }

    solutionContent.innerHTML = content;
}