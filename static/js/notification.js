document.addEventListener("DOMContentLoaded", function () {

    const notificationBtn =
        document.getElementById("notificationBtn");

    const notificationModal =
        document.getElementById("notificationModal");

    const notificationClose =
        document.getElementById("notificationClose");

    const notificationBackdrop =
        document.getElementById("notificationBackdrop");

    const notificationFooterClose =
        document.getElementById("notificationFooterClose");


    /* =====================================================
       OPEN
    ===================================================== */

    function openNotifications() {

        if (!notificationModal) {
            return;
        }

        notificationModal.classList.add("show");

        notificationModal.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.style.overflow = "hidden";
    }


    /* =====================================================
       CLOSE
    ===================================================== */

    function closeNotifications() {

        if (!notificationModal) {
            return;
        }

        notificationModal.classList.remove("show");

        notificationModal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.style.overflow = "";
    }


    /* =====================================================
       BUTTON
    ===================================================== */

    if (notificationBtn) {

        notificationBtn.addEventListener(
            "click",
            openNotifications
        );

    }


    /* =====================================================
       CLOSE BUTTON
    ===================================================== */

    if (notificationClose) {

        notificationClose.addEventListener(
            "click",
            closeNotifications
        );

    }


    /* =====================================================
       FOOTER CLOSE
    ===================================================== */

    if (notificationFooterClose) {

        notificationFooterClose.addEventListener(
            "click",
            closeNotifications
        );

    }


    /* =====================================================
       CLICK BACKDROP
    ===================================================== */

    if (notificationBackdrop) {

        notificationBackdrop.addEventListener(
            "click",
            closeNotifications
        );

    }


    /* =====================================================
       ESC KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                notificationModal &&
                notificationModal.classList.contains("show")
            ) {

                closeNotifications();

            }

        }
    );

});