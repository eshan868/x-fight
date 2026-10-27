/* =========================================================
   X-FIGHT DASHBOARD
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard JS loaded");


    /* =====================================================
       NAVIGATION
    ===================================================== */

    const dashboardLink =
        document.getElementById("dashboardLink");

    const tournamentLink =
        document.getElementById("tournamentLink");

    const matchesLink =
        document.getElementById("matchesLink");

    const chatsLink =
        document.getElementById("chatsLink");

    const teamsLink =
        document.getElementById("teamsLink");

    const coinTransferHistoryLink =
        document.getElementById("coinTransferHistoryLink");


    /* =====================================================
    SECTIONS
 ===================================================== */

    const dashboardContent =
        document.getElementById("dashboardContent");

    const tournamentsSection =
        document.getElementById("tournamentsSection");

    const matchesSection =
        document.getElementById("matchesSection");

    const chatsSection =
        document.getElementById("chatsSection");

    const teamsSection =
        document.getElementById("teamsSection");


    const coinTransferHistory =
        document.getElementById("coinTransferHistory");


    const navigationLinks = [

        dashboardLink,
        tournamentLink,
        matchesLink,
        chatsLink,
        teamsLink,
   
        coinTransferHistoryLink

    ];


    const dashboardSections = [

        dashboardContent,
        tournamentsSection,
        matchesSection,
        chatsSection,
        teamsSection,
        coinTransferHistory


    ];


    /* =====================================================
       MOBILE SIDEBAR
    ===================================================== */

    const mobileSidebarToggle =
        document.getElementById(
            "mobileSidebarToggle"
        );

    const mobileSidebarOverlay =
        document.getElementById(
            "mobileSidebarOverlay"
        );

    const dashboardSidebar =
        document.querySelector(
            ".dashboard-sidebar"
        );


    /* =====================================================
       OPEN SIDEBAR
    ===================================================== */

    function openMobileSidebar() {

        if (!dashboardSidebar) {
            return;
        }


        dashboardSidebar.classList.add(
            "mobile-open"
        );


        if (mobileSidebarOverlay) {

            mobileSidebarOverlay.classList.add(
                "mobile-visible"
            );

        }


        if (mobileSidebarToggle) {

            mobileSidebarToggle.classList.add(
                "menu-open"
            );

            mobileSidebarToggle.setAttribute(
                "aria-expanded",
                "true"
            );

        }

    }


    /* =====================================================
       CLOSE SIDEBAR
    ===================================================== */

    function closeMobileSidebar() {

        if (!dashboardSidebar) {
            return;
        }


        dashboardSidebar.classList.remove(
            "mobile-open"
        );


        if (mobileSidebarOverlay) {

            mobileSidebarOverlay.classList.remove(
                "mobile-visible"
            );

        }


        if (mobileSidebarToggle) {

            mobileSidebarToggle.classList.remove(
                "menu-open"
            );

            mobileSidebarToggle.setAttribute(
                "aria-expanded",
                "false"
            );

        }

    }


    /* =====================================================
       TOGGLE SIDEBAR
    ===================================================== */

    if (mobileSidebarToggle) {

        mobileSidebarToggle.addEventListener(
            "click",
            function () {

                if (
                    dashboardSidebar &&
                    dashboardSidebar.classList.contains(
                        "mobile-open"
                    )
                ) {

                    closeMobileSidebar();

                } else {

                    openMobileSidebar();

                }

            }
        );

    }


    /* =====================================================
       CLICK OVERLAY TO CLOSE
    ===================================================== */

    if (mobileSidebarOverlay) {

        mobileSidebarOverlay.addEventListener(
            "click",
            function () {

                closeMobileSidebar();

            }
        );

    }


    /* =====================================================
       ESCAPE TO CLOSE
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeMobileSidebar();

            }

        }
    );


    /* =====================================================
       SHOW DASHBOARD SECTION
    ===================================================== */

    function showSection(
        activeLink,
        activeSection
    ) {

        /* Remove active from all links */

        navigationLinks.forEach(
            function (link) {

                if (link) {

                    link.classList.remove(
                        "active"
                    );

                }

            }
        );


        /* Hide all sections */

        dashboardSections.forEach(
            function (section) {

                if (section) {

                    section.classList.remove(
                        "active-view"
                    );

                }

            }
        );


        /* Activate selected link */

        if (activeLink) {

            activeLink.classList.add(
                "active"
            );

        }


        /* Show selected section */

        if (activeSection) {

            activeSection.classList.add(
                "active-view"
            );

        }


        /* Close mobile sidebar */

        closeMobileSidebar();

    }


    /* =====================================================
       DASHBOARD
    ===================================================== */

    if (dashboardLink) {

        dashboardLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    dashboardLink,
                    dashboardContent
                );

            }
        );

    }


    /* =====================================================
       TOURNAMENTS
    ===================================================== */

    if (tournamentLink) {

        tournamentLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    tournamentLink,
                    tournamentsSection
                );

            }
        );

    }


    /* =====================================================
       MATCHES
    ===================================================== */

    if (matchesLink) {

        matchesLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    matchesLink,
                    matchesSection
                );

            }
        );

    }


    /* =====================================================
       CHATS
    ===================================================== */

    if (chatsLink) {

        chatsLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    chatsLink,
                    chatsSection
                );

            }
        );

    }


    /* =====================================================
       TEAMS
    ===================================================== */

    if (teamsLink) {

        teamsLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    teamsLink,
                    teamsSection
                );

            }
        );

    }


    /* =====================================================
       DASHBOARD → MATCHES
    ===================================================== */

    const dashboardMatchesLink =
        document.getElementById(
            "dashboardMatchesLink"
        );


    if (dashboardMatchesLink) {

        dashboardMatchesLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    matchesLink,
                    matchesSection
                );

            }
        );

    }



    /* =====================================================
       COIN TRANSFER HISTORY
    ===================================================== */

    if (coinTransferHistoryLink) {

        coinTransferHistoryLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                showSection(
                    coinTransferHistoryLink,
                    coinTransferHistory
                );

            }
        );

    }
    /* =====================================================
       INITIAL VIEW
    ===================================================== */

    showSection(
        dashboardLink,
        dashboardContent
    );

});