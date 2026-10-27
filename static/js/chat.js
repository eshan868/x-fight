/* ==========================================
   CHAT SYSTEM
========================================== */

function initializeChat() {

    console.log("Chat JS loaded");


    /* ==========================================
       GET ELEMENTS
    ========================================== */

    const messages = document.getElementById("messages");

    const inviteBtn = document.getElementById("inviteBtn");
    const inviteOverlay = document.getElementById("inviteOverlay");
    const closeInvite = document.getElementById("closeInvite");

    const searchInput = document.querySelector(".chat-search");
    const filterButtons = document.querySelectorAll(".chat-filter");
    const noResults = document.getElementById("noFilterResults");


    const messageInput = document.getElementById(
        "chat-message-input"
    );

    const messageForm = document.getElementById(
        "chat-message-form"
    );

    const fileInput = document.getElementById(
        "chat-file-input"
    );

    const fileUploadInput = document.getElementById(
        "chat-file-upload-input"
    );

    const uploadButton = document.querySelector(
        ".chat-upload-btn"
    );
    const callReceiverId = "{{ other_user.id }}";
    const currentChatroomName = "{{ chatroom_name|escapejs }}";


    /* ==========================================
     SCROLL TO BOTTOM
  ========================================== */

    function scrollToBottom(smooth = false) {

        if (!messages) {
            return;
        }

        requestAnimationFrame(function () {

            messages.scrollTo({
                top: messages.scrollHeight,
                behavior: smooth ? "smooth" : "auto"
            });

        });

    }




    function resizeMessageInput() {

        if (!messageInput) {
            return;
        }

        messageInput.style.height = "auto";

        const newHeight = Math.min(
            messageInput.scrollHeight,
            160
        );

        messageInput.style.height = newHeight + "px";
    }


    if (messageInput) {

        messageInput.addEventListener(
            "input",
            resizeMessageInput
        );

        resizeMessageInput();

    }


    /* ==========================================
       ENTER / SHIFT + ENTER
    ========================================== */

    if (messageInput) {

        messageInput.addEventListener(
            "keydown",
            function (event) {

                /*
                 Shift + Enter
                 = new line
                */

                if (
                    event.key === "Enter" &&
                    event.shiftKey
                ) {
                    return;
                }


                /*
                 Enter
                 = send message
                */

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    if (
                        messageInput.value.trim() !== ""
                    ) {

                        messageForm.requestSubmit();

                    }

                }

            }
        );

    }


    /* ==========================================
       FILE UPLOAD
    ========================================== */

    if (fileInput) {

        fileInput.addEventListener(
            "change",
            function () {

                if (!fileInput.files.length) {
                    return;
                }

                /*
                 Copy selected file into
                 the actual HTMX upload form.
                */

                const selectedFile =
                    fileInput.files[0];

                const dataTransfer =
                    new DataTransfer();

                dataTransfer.items.add(
                    selectedFile
                );

                fileUploadInput.files =
                    dataTransfer.files;


                /*
                 Visual indication
                 that a file was selected.
                */

                if (uploadButton) {

                    uploadButton.classList.add(
                        "file-selected"
                    );

                }


                /*
                 Submit the hidden
                 HTMX upload form.
                */

                htmx.trigger(
                    "#chat_form-file",
                    "submit"
                );


                /*
                 Reset after upload.
                */

                setTimeout(function () {

                    fileInput.value = "";

                    if (uploadButton) {

                        uploadButton.classList.remove(
                            "file-selected"
                        );

                    }

                }, 500);

            }
        );
    }

    /* ==========================================
       INITIAL SCROLL
    ========================================== */

    scrollToBottom();


    /* ==========================================
       AFTER HTMX SWAP
    ========================================== */

    document.body.addEventListener(
        "htmx:afterSwap",
        function (event) {

            if (
                event.target === messages ||
                messages.contains(event.target)
            ) {

                scrollToBottom(true);

            }

        }
    );


    /* ==========================================
       AFTER WEBSOCKET MESSAGE
    ========================================== */

    document.body.addEventListener(
        "htmx:wsAfterMessage",
        function () {

            scrollToBottom(true);

        }
    );


    /* ==========================================
       OBSERVE NEW CHAT MESSAGES
    ========================================== */

    if (messages) {

        const observer = new MutationObserver(function () {

            scrollToBottom(true);

        });

        observer.observe(messages, {
            childList: true,
            subtree: true
        });

    }


    /* ==========================================
       INVITE POPUP
    ========================================== */

    if (inviteBtn && inviteOverlay) {

        inviteBtn.addEventListener("click", function () {

            inviteOverlay.style.display = "flex";

        });

    }


    if (closeInvite && inviteOverlay) {

        closeInvite.addEventListener("click", function () {

            inviteOverlay.style.display = "none";

        });

    }


    if (inviteOverlay) {

        inviteOverlay.addEventListener("click", function (event) {

            if (event.target === inviteOverlay) {

                inviteOverlay.style.display = "none";

            }

        });

    }


    /* ==========================================
       CHAT FILTER STATE
    ========================================== */

    let currentFilter = "all";


    /* ==========================================
       UPDATE CHAT LIST
    ========================================== */

    function updateChatList() {

        /*
        Get all chat items every time.
        */

        const chatItems = document.querySelectorAll(".chat-item");


        /*
        Get current search text.
        */

        const searchText = searchInput
            ? searchInput.value.trim().toLowerCase()
            : "";


        let visibleCount = 0;


        /* ==========================================
           CHECK EVERY CHAT
        ========================================== */

        chatItems.forEach(function (chat) {

            /*
            Get chat name.

            Example:
            x-test-1
            7201666
            TEST GROUP
            Gaming Group
            */

            const chatName = (
                chat.dataset.name || ""
            )
                .trim()
                .toLowerCase();


            /*
            Get chat type.

            gamemate
            group
            */

            const chatType = (
                chat.dataset.type || ""
            )
                .trim()
                .toLowerCase();


            /* ==========================================
               FILTER MATCH
            ========================================== */

            let matchesFilter = false;


            if (currentFilter === "all") {

                matchesFilter = true;

            } else if (currentFilter === "gamemate") {

                matchesFilter = chatType === "gamemate";

            } else if (currentFilter === "group") {

                matchesFilter = chatType === "group";

            }


            /* ==========================================
               SEARCH MATCH

               Searches anywhere in the name.

               Example:
               GameMaster

               "g"       -> GameMaster
               "game"    -> GameMaster
               "master"  -> GameMaster
               "ster"    -> GameMaster
            ========================================== */

            const matchesSearch =

                searchText === "" ||

                chatName.includes(searchText);


            /* ==========================================
               FINAL RESULT
            ========================================== */

            const shouldShow =

                matchesFilter &&

                matchesSearch;


            /* ==========================================
               SHOW / HIDE
            ========================================== */

            if (shouldShow) {

                /*
                Remove inline display:none.

                CSS will then control the normal
                display:flex layout.
                */

                chat.style.display = "";

                visibleCount++;

            } else {

                /*
                Force hide the chat.

                IMPORTANT:
                Your CSS must NOT have:

                display: flex !important;

                for .chat-user
                */

                chat.style.setProperty(
                    "display",
                    "none",
                    "important"
                );

            }

        });


        /* ==========================================
           NO RESULTS MESSAGE
        ========================================== */

        if (noResults) {

            if (visibleCount === 0) {

                noResults.classList.remove("d-none");

                noResults.style.setProperty(
                    "display",
                    "block",
                    "important"
                );

            } else {

                noResults.classList.add("d-none");

                noResults.style.setProperty(
                    "display",
                    "none",
                    "important"
                );

            }

        }


        /* ==========================================
           DEBUG
        ========================================== */

        console.log({
            filter: currentFilter,
            search: searchText,
            visibleChats: visibleCount
        });

    }


    /* ==========================================
       FILTER BUTTONS
    ========================================== */

    filterButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            /*
            Remove active class
            from every filter button.
            */

            filterButtons.forEach(function (btn) {

                btn.classList.remove("active");

            });


            /*
            Add active class
            to clicked button.
            */

            this.classList.add("active");


            /*
            Update filter.
            */

            currentFilter = (
                this.dataset.filter || "all"
            )
                .trim()
                .toLowerCase();


            console.log(
                "Selected filter:",
                currentFilter
            );


            /*
            Apply filter immediately.
            */

            updateChatList();

        });

    });


    /* ==========================================
       LIVE SEARCH
    ========================================== */

    if (searchInput) {

        searchInput.addEventListener("input", function () {

            /*
            Search instantly after
            every letter typed.
            */

            updateChatList();

        });


        /*
        Optional:
        Press Escape to clear search.
        */

        searchInput.addEventListener("keydown", function (event) {

            if (event.key === "Escape") {

                searchInput.value = "";

                updateChatList();

            }

        });

    }


    /* ==========================================
       INITIAL LOAD
    ========================================== */

    updateChatList();

}


function getCallCsrfToken() {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();

        if (trimmedCookie.startsWith("csrftoken=")) {
            return decodeURIComponent(
                trimmedCookie.substring("csrftoken=".length)
            );
        }
    }

    return null;
}


function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();

        if (trimmedCookie.startsWith(name + "=")) {
            return decodeURIComponent(
                trimmedCookie.substring(name.length + 1)
            );
        }
    }

    return null;
}

function updateCallStatus(message) {
    console.log("[GameArena Call]", message);
}
async function startGameArenaCall(callType, chatroomName) {
    if (!chatroomName) {
        alert("Chatroom name is missing.");
        return;
    }

    console.log("[GameArena] Starting group call:", {
        callType: callType,
        chatroomName: chatroomName
    });

    try {
        const response = await fetch("/social/calls/start/", {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },

            body: JSON.stringify({
                chatroom_name: chatroomName,
                call_type: callType
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Unable to start the call.");
            return;
        }

        if (!data.success) {
            alert(data.error || "Call could not be started.");
            return;
        }

        console.log("[GameArena] Group call started:", data);

        // Keep the caller on the current chat page.
        // Show the outgoing calling popup.
        if (typeof window.showOutgoingCall === "function") {
            window.showOutgoingCall({
                room_id: data.room_id,
                call_type: data.call_type,
                chatroom_name: data.chatroom_name
            });
        }

    } catch (error) {
        console.error("[GameArena] Start call error:", error);
        alert("Something went wrong while starting the call.");
    }
}

function openGameArenaCallingRoom(
    roomId,
    callType
) {
    const url =
        "/social/calling/?room_id=" +
        encodeURIComponent(roomId) +
        "&call_type=" +
        encodeURIComponent(callType);

    window.location.href = url;
}




/* ==========================================
   START SCRIPT SAFELY
========================================== */

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeChat
    );

} else {

    initializeChat();

}