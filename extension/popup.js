const API_URL =
    "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev";

const contextBox =
    document.getElementById("context");

const analyzeButton =
    document.getElementById("analyze");

const status =
    document.getElementById("status");

const taskList =
    document.getElementById("taskList");


// ---------------------------------------------------------
// LOAD SELECTED TEXT + ORIGINAL SOURCE URL
// ---------------------------------------------------------

let selectedSourceURL = null;

chrome.storage.local.get(
    [
        "selectedContext",
        "selectedSourceURL"
    ],
    (result) => {

        if (result.selectedContext) {

            contextBox.value =
                result.selectedContext;

            chrome.storage.local.remove(
                "selectedContext"
            );
        }

        if (result.selectedSourceURL) {

            selectedSourceURL =
                result.selectedSourceURL;

            chrome.storage.local.remove(
                "selectedSourceURL"
            );
        }
    }
);


// ---------------------------------------------------------
// LOAD TASKS WHEN POPUP OPENS
// ---------------------------------------------------------

loadTasks();


// ---------------------------------------------------------
// ANALYZE CONTEXT
// ---------------------------------------------------------

analyzeButton.addEventListener(
    "click",
    async () => {

        const context =
            contextBox.value.trim();

        if (!context) {

            status.textContent =
                "Please enter some context.";

            return;
        }

        status.textContent =
            "Analyzing...";

        analyzeButton.disabled =
            true;

        try {

            // Find any action URL inside the selected text
            const actionLink =
                extractURL(context);


            const response =
                await fetch(
                    `${API_URL}/analyze-context-extension`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            context: context
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Server error"
                );
            }


            // -------------------------------------------------
            // NEW TASKS CREATED
            // -------------------------------------------------

            if (
                data.created_tasks &&
                data.created_tasks.length > 0
            ) {

                status.textContent =
                    `${data.created_tasks.length} task(s) created successfully.`;


                data.created_tasks.forEach(
                    (task) => {

                        /*
                         * IMPORTANT:
                         *
                         * Notification should open
                         * the ORIGINAL SOURCE PAGE.
                         *
                         * The action link is kept separately.
                         */

                        const notificationLink =
                            selectedSourceURL ||
                            actionLink ||
                            task.link ||
                            null;


                        chrome.runtime.sendMessage({

                            type:
                                "TASK_CREATED",

                            taskId:
                                task.task_id,

                            title:
                                task.title,

                            // This is the URL notification opens
                            link:
                                notificationLink,

                            // Original email/message/page
                            sourceLink:
                                selectedSourceURL ||
                                null,

                            // Actual task/action URL
                            actionLink:
                                actionLink ||
                                task.link ||
                                null

                        });

                    }
                );


                // Source URL has now been consumed
                selectedSourceURL =
                    null;
            }


            // -------------------------------------------------
            // DUPLICATE TASK
            // -------------------------------------------------

            else if (
                data.duplicate_tasks &&
                data.duplicate_tasks.length > 0
            ) {

                status.textContent =
                    "Duplicate task detected.";

            }


            // -------------------------------------------------
            // NOTHING CREATED
            // -------------------------------------------------

            else {

                status.textContent =
                    "No new task was created.";

            }


            // Refresh task list
            await loadTasks();


        } catch (error) {

            console.error(
                "ContextFlow analyze error:",
                error
            );

            status.textContent =
                "Error: " +
                error.message;


        } finally {

            analyzeButton.disabled =
                false;
        }
    }
);


// ---------------------------------------------------------
// EXTRACT URL FROM CONTEXT
// ---------------------------------------------------------

function extractURL(text) {

    const urlPattern =
        /https?:\/\/[^\s<>"']+/i;

    const match =
        text.match(urlPattern);

    if (!match) {

        return null;
    }

    return match[0].replace(
        /[.,;!?)]$/,
        ""
    );
}


// ---------------------------------------------------------
// LOAD ALL TASKS
// ---------------------------------------------------------

async function loadTasks() {

    try {

        const response =
            await fetch(
                `${API_URL}/tasks`
            );


        if (!response.ok) {

            throw new Error(
                "Could not load tasks"
            );
        }


        const tasks =
            await response.json();


        displayTasks(tasks);


    } catch (error) {

        console.error(
            "ContextFlow task loading error:",
            error
        );


        taskList.innerHTML = `
            <p>
                Unable to load tasks.
            </p>
        `;
    }
}


// ---------------------------------------------------------
// DISPLAY TASKS
// ---------------------------------------------------------

function displayTasks(tasks) {

    taskList.innerHTML = "";


    // Task count
    updateTaskCount(tasks);


    // Empty state
    if (
        !tasks ||
        tasks.length === 0
    ) {

        taskList.innerHTML = `
            <div class="empty-state">
                No tasks yet.<br>
                Capture some context to get started.
            </div>
        `;

        return;
    }


    tasks.forEach(
        (task) => {

            const taskCard =
                document.createElement(
                    "div"
                );


            taskCard.className =
                "task-card";


            // Category
            const category =
                task.category ||
                "General";


            // Priority
            const priority =
                task.priority ||
                "Medium";


            // Status
            const taskStatus =
                task.status ||
                "READY";


            // Deadline
            const deadline =
                task.deadline ||
                "None";


            // Deadline status
            const deadlineStatus =
                task.deadline_status ||
                "No deadline";


            // Reminder
            const reminder =
                task.reminder_message ||
                "";


            // -------------------------------------------------
            // COMPLETE BUTTON / COMPLETED LABEL
            // -------------------------------------------------

            let completeSection =
                "";


            if (
                taskStatus !==
                "COMPLETED"
            ) {

                completeSection = `
                    <button
                        class="complete-button"
                        data-task-id="${escapeHTML(
                            String(task.task_id)
                        )}">
                        Complete
                    </button>
                `;

            } else {

                completeSection = `
                    <div class="completed-label">
                        Completed
                    </div>
                `;
            }


            // -------------------------------------------------
            // SOURCE BUTTON
            // -------------------------------------------------

            let sourceSection =
                "";


            if (
                isValidSourceURL(
                    task.link
                )
            ) {

                sourceSection = `
                    <button
                        class="source-button"
                        data-source-url="${escapeHTML(
                            task.link
                        )}">
                        View Source
                    </button>
                `;
            }


            // -------------------------------------------------
            // TASK CARD
            // -------------------------------------------------

            taskCard.innerHTML = `

                <div class="task-title">
                    ${escapeHTML(
                        task.title
                    )}
                </div>


                <div class="task-details">

                    <span>
                        Category:
                        <strong>
                            ${escapeHTML(
                                category
                            )}
                        </strong>
                    </span>


                    <span>
                        Priority:
                        <strong>
                            ${escapeHTML(
                                priority
                            )}
                        </strong>
                    </span>


                    <span>
                        Deadline:
                        <strong>
                            ${escapeHTML(
                                deadline
                            )}
                        </strong>
                    </span>


                    <span>
                        Status:
                        <strong>
                            ${escapeHTML(
                                taskStatus
                            )}
                        </strong>
                    </span>


                    <span>
                        Deadline status:
                        <strong>
                            ${escapeHTML(
                                deadlineStatus
                            )}
                        </strong>
                    </span>


                    ${
                        reminder
                            ? `
                                <span>
                                    ${escapeHTML(
                                        reminder
                                    )}
                                </span>
                              `
                            : ""
                    }

                </div>


                ${sourceSection}


                ${completeSection}

            `;


            taskList.appendChild(
                taskCard
            );

        }
    );


    // ---------------------------------------------------------
    // COMPLETE BUTTONS
    // ---------------------------------------------------------

    document
        .querySelectorAll(
            ".complete-button"
        )
        .forEach(
            (button) => {

                button.addEventListener(
                    "click",
                    async () => {

                        const taskId =
                            button.dataset.taskId;


                        await completeTask(
                            taskId
                        );

                    }
                );

            }
        );


    // ---------------------------------------------------------
    // SOURCE BUTTONS
    // ---------------------------------------------------------

    document
        .querySelectorAll(
            ".source-button"
        )
        .forEach(
            (button) => {

                button.addEventListener(
                    "click",
                    () => {

                        const url =
                            button.dataset.sourceUrl;


                        if (
                            !isValidSourceURL(
                                url
                            )
                        ) {

                            status.textContent =
                                "Invalid source URL.";

                            return;
                        }


                        chrome.tabs.create(
                            {
                                url:
                                    url
                            },
                            () => {

                                if (
                                    chrome.runtime.lastError
                                ) {

                                    console.error(
                                        "ContextFlow source error:",
                                        chrome.runtime.lastError.message
                                    );


                                    status.textContent =
                                        "Could not open source.";

                                }

                            }
                        );

                    }
                );

            }
        );

}


// ---------------------------------------------------------
// UPDATE TASK COUNT
// ---------------------------------------------------------

function updateTaskCount(tasks) {

    const taskCount =
        document.getElementById(
            "taskCount"
        );


    if (!taskCount) {

        return;
    }


    const count =
        tasks
            ? tasks.length
            : 0;


    taskCount.textContent =
        count === 1
            ? "1 task"
            : `${count} tasks`;

}


// ---------------------------------------------------------
// COMPLETE TASK
// ---------------------------------------------------------

async function completeTask(
    taskId
) {

    try {

        status.textContent =
            "Completing task...";


        const response =
            await fetch(
                `${API_URL}/tasks/${taskId}/complete`,
                {
                    method: "PATCH"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Could not complete task"
            );
        }


        status.textContent =
            "Task completed successfully!";


        // Completion notification
        chrome.runtime.sendMessage({

            type:
                "TASK_COMPLETED",

            title:
                data.title

        });


        // Refresh tasks
        await loadTasks();


    } catch (error) {

        console.error(
            "ContextFlow completion error:",
            error
        );


        status.textContent =
            "Error: " +
            error.message;
    }
}


// ---------------------------------------------------------
// VALIDATE SOURCE URL
// ---------------------------------------------------------

function isValidSourceURL(
    url
) {

    if (!url) {

        return false;
    }


    try {

        const parsedURL =
            new URL(url);


        return (
            parsedURL.protocol ===
                "http:" ||
            parsedURL.protocol ===
                "https:"
        );


    } catch (error) {

        return false;
    }
}


// ---------------------------------------------------------
// PREVENT HTML INJECTION
// ---------------------------------------------------------

function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        String(value);


    return div.innerHTML;
}