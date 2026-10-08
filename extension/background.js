const API_URL =
    "https://bookish-barnacle-jjr55rjwv4v2pv9-8000.app.github.dev";


// =========================================================
// NOTIFICATION METRICS
// =========================================================

async function recordNotificationMetric() {

    try {

        await fetch(
            API_URL + "/metrics/notification",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error(
            "ContextFlow notification metrics error:",
            error
        );

    }

}


async function recordCompletionMetric() {

    try {

        await fetch(
            API_URL + "/metrics/completion",
            {
                method: "POST"
            }
        );

        console.log(
            "ContextFlow: Completion metric recorded."
        );

    } catch (error) {

        console.error(
            "ContextFlow completion metrics error:",
            error
        );

    }

}


// =========================================================
// INSTALLATION
// =========================================================

chrome.runtime.onInstalled.addListener(() => {

    chrome.contextMenus.create({

        id: "send-to-contextflow",

        title: "Send to ContextFlow",

        contexts: ["selection"]

    });


    chrome.alarms.create(
        "deadline-check",
        {
            periodInMinutes: 1
        }
    );


    console.log(
        "ContextFlow: Extension installed and alarm created."
    );

});


// =========================================================
// STARTUP
// =========================================================

chrome.runtime.onStartup.addListener(() => {

    chrome.alarms.create(
        "deadline-check",
        {
            periodInMinutes: 1
        }
    );


    console.log(
        "ContextFlow: Extension startup alarm created."
    );

});


// Create alarm whenever service worker starts.

chrome.alarms.create(
    "deadline-check",
    {
        periodInMinutes: 1
    }
);


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

        }).then(() => {

            recordNotificationMetric();

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


                    await recordNotificationMetric();


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

            try {

                await chrome.notifications.create({

                    type: "basic",

                    iconUrl: "icon.png",

                    title: "🎉 ContextFlow",

                    message:
                        `Task completed successfully: ${message.title}`,

                    priority: 2

                });


                await recordNotificationMetric();


                await recordCompletionMetric();


                console.log(
                    "ContextFlow: Completion notification and metric recorded."
                );

            } catch (error) {

                console.error(
                    "ContextFlow completion notification/metrics error:",
                    error
                );

            }

        }

    }
);


// =========================================================
// AUTOMATIC NEW TASK DETECTOR
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
            "ContextFlow: Deadline alarm triggered."
        );


        try {

            const response =
                await fetch(
                    API_URL + "/tasks"
                );


            if (!response.ok) {

                throw new Error(
                    `Tasks request failed: ${response.status}`
                );

            }


            const tasks =
                await response.json();


            console.log(
                "ContextFlow: Tasks fetched:",
                tasks.length
            );


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


            for (
                const task of tasks
            ) {

                if (
                    task.status ===
                    "COMPLETED"
                ) {

                    continue;

                }


                if (
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


                const sourceLink =
                    task.link ||
                    null;


                const actionLink =
                    task.action_link ||
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


                    await recordNotificationMetric();


                    await chrome.storage.local.set({

                        [`notification_${notificationId}`]:
                        {

                            link:
                                sourceLink,

                            taskId:
                                task.task_id,

                            actionLink:
                                actionLink

                        }

                    });


                    knownTaskIds.push(
                        task.task_id
                    );


                    if (
                        sourceLink
                    ) {

                        await chrome.storage.local.set({

                            [`task_source_${task.task_id}`]:
                                sourceLink

                        });

                    }

                } catch (error) {

                    console.error(
                        "ContextFlow automatic notification error:",
                        error
                    );

                }

            }


            await chrome.storage.local.set({

                contextflow_known_task_ids:
                    knownTaskIds

            });


        } catch (error) {

            console.error(
                "ContextFlow automatic task detection error:",
                error
            );

        }

    }
);


// =========================================================
// DEADLINE REMINDERS
// =========================================================

async function checkDeadlineReminders() {

    try {

        const response =
            await fetch(
                API_URL + "/tasks"
            );


        if (!response.ok) {

            throw new Error(
                `Tasks request failed: ${response.status}`
            );

        }


        const tasks =
            await response.json();


        for (
            const task of tasks
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


            const deadline =
                new Date(
                    task.deadline +
                    "T23:59:59"
                );


            const now =
                new Date();


            const difference =
                deadline.getTime() -
                now.getTime();


            const hoursRemaining =
                difference /
                (
                    1000 *
                    60 *
                    60
                );


            let reminderMessage =
                null;


            if (
                hoursRemaining <= 0
            ) {

                reminderMessage =
                    `Deadline passed: ${task.title}`;

            } else if (
                hoursRemaining <= 5
            ) {

                reminderMessage =
                    `⚠️ ${Math.ceil(hoursRemaining)} hour(s) remaining: ${task.title}`;

            } else if (
                hoursRemaining <= 24
            ) {

                reminderMessage =
                    `⏰ Less than 1 day remaining: ${task.title}`;

            } else if (
                hoursRemaining <= 48
            ) {

                reminderMessage =
                    `⏰ 2 days remaining: ${task.title}`;

            }


            if (
                !reminderMessage
            ) {

                continue;

            }


            const reminderKey =
                `reminder_${task.task_id}_${task.deadline}`;


            const stored =
                await chrome.storage.local.get(
                    reminderKey
                );


            if (
                stored[reminderKey]
            ) {

                continue;

            }


            try {

                const notificationId =
                    await chrome.notifications.create({

                        type: "basic",

                        iconUrl: "icon.png",

                        title:
                            "ContextFlow Deadline Reminder",

                        message:
                            reminderMessage,

                        priority: 2

                    });


                await recordNotificationMetric();


                await chrome.storage.local.set({

                    [reminderKey]:
                    true

                });


                await chrome.storage.local.set({

                    [`notification_${notificationId}`]:
                    {

                        link:
                            task.link ||
                            null,

                        taskId:
                            task.task_id,

                        actionLink:
                            task.action_link ||
                            null

                    }

                });


                console.log(
                    "ContextFlow deadline reminder sent:",
                    task.task_id
                );

            } catch (error) {

                console.error(
                    "ContextFlow deadline notification error:",
                    error
                );

            }

        }

    } catch (error) {

        console.error(
            "ContextFlow deadline check error:",
            error
        );

    }

}


// =========================================================
// ALARM HANDLER FOR DEADLINE REMINDERS
// =========================================================

chrome.alarms.onAlarm.addListener(
    async (alarm) => {

        if (
            alarm.name !==
            "deadline-check"
        ) {

            return;

        }


        await checkDeadlineReminders();

    }
);


// =========================================================
// NOTIFICATION CLICK
// =========================================================

chrome.notifications.onClicked.addListener(
    async (notificationId) => {

        try {

            const stored =
                await chrome.storage.local.get(
                    `notification_${notificationId}`
                );


            const notification =
                stored[
                    `notification_${notificationId}`
                ];


            if (
                !notification
            ) {

                console.log(
                    "ContextFlow: No notification data found."
                );

                return;

            }


            const targetURL =
                notification.actionLink ||
                notification.link;


            if (
                targetURL
            ) {

                await chrome.tabs.create({

                    url:
                        targetURL

                });

            }


            await chrome.storage.local.remove(
                `notification_${notificationId}`
            );


        } catch (error) {

            console.error(
                "ContextFlow notification click error:",
                error
            );

        }

    }
);


// =========================================================
// NOTIFICATION CLOSED
// =========================================================

chrome.notifications.onClosed.addListener(
    async (notificationId) => {

        try {

            await chrome.storage.local.remove(
                `notification_${notificationId}`
            );

        } catch (error) {

            console.error(
                "ContextFlow notification cleanup error:",
                error
            );

        }

    }
);


// =========================================================
// PERIODIC DEADLINE CHECK
// =========================================================

setInterval(
    () => {

        checkDeadlineReminders();

    },
    60 * 1000
);


// =========================================================
// SERVICE WORKER STARTUP LOG
// =========================================================

console.log(
    "ContextFlow background service worker loaded."
);