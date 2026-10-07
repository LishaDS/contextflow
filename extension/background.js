const API_URL =
    "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev";


// =========================================================
// INSTALLATION
// =========================================================

chrome.runtime.onInstalled.addListener(() => {

    chrome.contextMenus.create({
        id: "send-to-contextflow",
        title: "Send to ContextFlow",
        contexts: ["selection"]
    });

    chrome.alarms.create("deadline-check", {
        periodInMinutes: 1
    });

    console.log(
        "ContextFlow: Extension installed and alarm created."
    );
});


// =========================================================
// STARTUP
// =========================================================

chrome.runtime.onStartup.addListener(() => {

    chrome.alarms.create("deadline-check", {
        periodInMinutes: 1
    });

    console.log(
        "ContextFlow: Extension startup alarm created."
    );
});


// Create alarm whenever service worker starts.
chrome.alarms.create("deadline-check", {
    periodInMinutes: 1
});


// =========================================================
// CONTEXT MENU / MANUAL CAPTURE
// =========================================================

chrome.contextMenus.onClicked.addListener(
    (info, tab) => {

        if (
            info.menuItemId !==
            "send-to-contextflow"
        ) {
            return;
        }

        if (!info.selectionText) {
            return;
        }

        const sourceURL =
            tab && tab.url
                ? tab.url
                : null;

        chrome.storage.local.set({

            selectedContext:
                info.selectionText,

            selectedSourceURL:
                sourceURL

        });

        chrome.notifications.create({

            type: "basic",

            iconUrl: "icon.png",

            title: "ContextFlow",

            message:
                "Selected context captured.",

            priority: 1

        });

    }
);


// =========================================================
// MESSAGES FROM POPUP
// =========================================================

chrome.runtime.onMessage.addListener(
    async (message) => {

        // -------------------------------------------------
        // TASK CREATED MANUALLY
        // -------------------------------------------------

        if (
            message.type ===
            "TASK_CREATED"
        ) {

            console.log(
                "ContextFlow: Task created notification received.",
                message
            );

            const sourceLink =
                message.sourceLink ||
                message.link ||
                null;

            const actionLink =
                message.actionLink ||
                null;


            // Mark task as known so the automatic
            // detector does not notify twice.

            if (message.taskId) {

                const stored =
                    await chrome.storage.local.get(
                        "contextflow_known_task_ids"
                    );

                const knownTaskIds =
                    Array.isArray(
                        stored.contextflow_known_task_ids
                    )
                        ? stored.contextflow_known_task_ids
                        : [];

                if (
                    !knownTaskIds.includes(
                        message.taskId
                    )
                ) {

                    knownTaskIds.push(
                        message.taskId
                    );

                    await chrome.storage.local.set({

                        contextflow_known_task_ids:
                            knownTaskIds

                    });

                }

            }


            chrome.notifications.create({

                type: "basic",

                iconUrl: "icon.png",

                title: "ContextFlow",

                message:
                    `Task created: ${message.title}`,

                priority: 2

            })
            .then(
                async (notificationId) => {

                    console.log(
                        "ContextFlow notification created:",
                        notificationId
                    );

                    await chrome.storage.local.set({

                        [`notification_${notificationId}`]:
                        {
                            link:
                                sourceLink,

                            taskId:
                                message.taskId,

                            actionLink:
                                actionLink
                        }

                    });

                    if (
                        message.taskId &&
                        sourceLink
                    ) {

                        await chrome.storage.local.set({

                            [`task_source_${message.taskId}`]:
                                sourceLink

                        });

                    }

                }
            )
            .catch(
                (error) => {

                    console.error(
                        "ContextFlow notification error:",
                        error
                    );

                }
            );

        }


        // -------------------------------------------------
        // TASK COMPLETED
        // -------------------------------------------------

        if (
            message.type ===
            "TASK_COMPLETED"
        ) {

            chrome.notifications.create({

                type: "basic",

                iconUrl: "icon.png",

                title: "🎉 ContextFlow",

                message:
                    `Task completed successfully: ${message.title}`,

                priority: 2

            });

        }

    }
);


// =========================================================
// AUTOMATIC NEW TASK DETECTOR
// =========================================================

async function checkForNewTasks(tasks) {

    try {

        console.log(
            "ContextFlow: Checking for new tasks..."
        );

        const stored =
            await chrome.storage.local.get(
                "contextflow_known_task_ids"
            );

        let knownTaskIds =
            stored.contextflow_known_task_ids;


        // -------------------------------------------------
        // FIRST RUN
        // -------------------------------------------------

        if (!Array.isArray(knownTaskIds)) {

            knownTaskIds =
                tasks
                    .map(
                        task =>
                            task.task_id
                    )
                    .filter(
                        taskId =>
                            Boolean(taskId)
                    );

            await chrome.storage.local.set({

                contextflow_known_task_ids:
                    knownTaskIds

            });

            console.log(
                "ContextFlow: Existing tasks registered:",
                knownTaskIds.length
            );

            return;
        }


        console.log(
            "ContextFlow: Known tasks:",
            knownTaskIds.length
        );


        let newTasksFound = 0;


        // -------------------------------------------------
        // FIND NEW TASKS
        // -------------------------------------------------

        for (
            const task
            of tasks
        ) {

            if (
                !task ||
                !task.task_id
            ) {
                continue;
            }


            if (
                knownTaskIds.includes(
                    task.task_id
                )
            ) {
                continue;
            }


            console.log(
                "ContextFlow: NEW AUTOMATIC TASK:",
                task.task_id,
                task.title
            );


            const notificationLink =
                task.link ||
                null;


            try {

                const notificationId =
                    await chrome.notifications.create({

                        type: "basic",

                        iconUrl: "icon.png",

                        title:
                            "ContextFlow",

                        message:
                            `New task detected: ${task.title}`,

                        priority: 2

                    });


                console.log(
                    "ContextFlow automatic notification created:",
                    notificationId
                );


                await chrome.storage.local.set({

                    [`notification_${notificationId}`]:
                    {
                        link:
                            notificationLink,

                        taskId:
                            task.task_id
                    }

                });


                if (
                    task.task_id &&
                    notificationLink
                ) {

                    await chrome.storage.local.set({

                        [`task_source_${task.task_id}`]:
                            notificationLink

                    });

                }


                // Immediately mark as known.
                // This prevents duplicate notifications.

                knownTaskIds.push(
                    task.task_id
                );

                newTasksFound++;

            } catch (notificationError) {

                console.error(
                    "ContextFlow automatic notification error:",
                    notificationError
                );

            }

        }


        // -------------------------------------------------
        // SAVE KNOWN TASKS
        // -------------------------------------------------

        await chrome.storage.local.set({

            contextflow_known_task_ids:
                knownTaskIds

        });


        console.log(
            "ContextFlow: New task notifications sent:",
            newTasksFound
        );

    } catch (error) {

        console.error(
            "ContextFlow new task detector error:",
            error
        );

    }

}


// =========================================================
// NOTIFICATION CLICK
// =========================================================

chrome.notifications.onClicked.addListener(
    async (notificationId) => {

        console.log(
            "ContextFlow notification clicked:",
            notificationId
        );

        const key =
            `notification_${notificationId}`;

        try {

            const result =
                await chrome.storage.local.get(
                    key
                );

            const notificationData =
                result[key];


            if (
                notificationData &&
                notificationData.link
            ) {

                console.log(
                    "ContextFlow opening source:",
                    notificationData.link
                );

                await chrome.tabs.create({

                    url:
                        notificationData.link

                });

                await chrome.storage.local.remove(
                    key
                );

            } else {

                console.error(
                    "ContextFlow: No source URL found:",
                    notificationId
                );

            }

        } catch (error) {

            console.error(
                "ContextFlow notification click error:",
                error
            );

        }

    }
);


// =========================================================
// ALARM
// =========================================================

chrome.alarms.onAlarm.addListener(
    async (alarm) => {

        if (
            alarm.name !==
            "deadline-check"
        ) {

            return;
        }


        console.log(
            "🔥 ContextFlow: deadline-check alarm fired."
        );


        try {

            // -------------------------------------------------
            // FETCH TASKS
            // -------------------------------------------------

            const response =
                await fetch(
                    `${API_URL}/tasks`
                );


            if (!response.ok) {

                console.error(
                    "ContextFlow: Failed to fetch tasks:",
                    response.status
                );

                return;
            }


            const tasks =
                await response.json();


            console.log(
                "ContextFlow: Tasks fetched:",
                tasks.length
            );


            // -------------------------------------------------
            // AUTOMATIC NEW TASK DETECTION
            // -------------------------------------------------

            await checkForNewTasks(
                tasks
            );


            // -------------------------------------------------
            // DEADLINE REMINDERS
            // -------------------------------------------------

            for (
                const task
                of tasks
            ) {

                if (
                    task.status ===
                    "COMPLETED"
                ) {
                    continue;
                }


                if (
                    !task.deadline
                ) {
                    continue;
                }


                if (
                    !task.reminder_message
                ) {
                    continue;
                }


                const storageKey =
                    `deadline_reminder_${task.task_id}_${task.reminder_message}`;


                const stored =
                    await chrome.storage.local.get(
                        storageKey
                    );


                if (
                    stored[storageKey]
                ) {
                    continue;
                }


                const sourceData =
                    await chrome.storage.local.get(
                        `task_source_${task.task_id}`
                    );


                const notificationLink =
                    sourceData[
                        `task_source_${task.task_id}`
                    ] ||
                    task.link ||
                    null;


                const notificationId =
                    await chrome.notifications.create({

                        type: "basic",

                        iconUrl: "icon.png",

                        title:
                            getNotificationTitle(
                                task.deadline_status
                            ),

                        message:
                            `${task.title}\n${task.reminder_message}`,

                        priority: 2

                    });


                console.log(
                    "ContextFlow reminder notification created:",
                    notificationId
                );


                if (
                    notificationLink
                ) {

                    await chrome.storage.local.set({

                        [`notification_${notificationId}`]:
                        {
                            link:
                                notificationLink,

                            taskId:
                                task.task_id
                        }

                    });

                }


                await chrome.storage.local.set({

                    [storageKey]:
                        true

                });

            }

        } catch (error) {

            console.error(
                "ContextFlow deadline checker error:",
                error
            );

        }

    }
);


// =========================================================
// NOTIFICATION TITLE
// =========================================================

function getNotificationTitle(
    deadlineStatus
) {

    switch (
        deadlineStatus
    ) {

        case "Overdue":

            return "🚨 ContextFlow - Overdue";


        case "Due Today":

            return "🔴 ContextFlow - Due Today";


        case "Due Soon":

            return "🟡 ContextFlow - Due Soon";


        case "On Track":

            return "🔵 ContextFlow Reminder";


        default:

            return "ContextFlow Reminder";

    }

}