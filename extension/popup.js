const API_URL = "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev/analyze-context-extension";

const contextBox = document.getElementById("context");
const analyzeButton = document.getElementById("analyze");
const status = document.getElementById("status");

chrome.storage.local.get(["selectedContext"], (result) => {
    if (result.selectedContext) {
        contextBox.value = result.selectedContext;
        chrome.storage.local.remove("selectedContext");
    }
});

analyzeButton.addEventListener("click", async () => {
    const context = contextBox.value.trim();

    if (!context) {
        status.textContent = "Please enter some context.";
        return;
    }

    status.textContent = "Analyzing...";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "text/plain"
            },
            body: JSON.stringify({
                context: context
            })
        });

        const responseText = await response.text();

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}: ${responseText || "empty response"}`
            );
        }

        if (!responseText) {
            throw new Error("Server returned an empty response.");
        }

        const data = JSON.parse(responseText);

        if (data.created_tasks && data.created_tasks.length > 0) {
            const task = data.created_tasks[0];

            status.textContent =
                `Created: ${task.title} | Category: ${task.category} | Priority: ${task.priority} | Deadline: ${task.deadline || "None"}`;
        } else if (data.duplicate_tasks && data.duplicate_tasks.length > 0) {
            status.textContent =
                `Duplicate task detected: ${data.duplicate_tasks[0].title}`;
        } else {
            status.textContent = "No new task was created.";
        }

    } catch (error) {
        status.textContent = "Error: " + error.message;
    }
});
