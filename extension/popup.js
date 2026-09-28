const API_URL = "http://localhost:8000/analyze-context";

document.getElementById("analyze").addEventListener("click", async () => {
    const context = document.getElementById("context").value.trim();
    const status = document.getElementById("status");

    if (!context) {
        status.textContent = "Please enter some context.";
        return;
    }

    status.textContent = "Analyzing...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                context: context
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed");
        }

        status.textContent =
            `Created ${data.created_tasks.length} task(s) successfully.`;
    } catch (error) {
        status.textContent = "Error: " + error.message;
    }
});
