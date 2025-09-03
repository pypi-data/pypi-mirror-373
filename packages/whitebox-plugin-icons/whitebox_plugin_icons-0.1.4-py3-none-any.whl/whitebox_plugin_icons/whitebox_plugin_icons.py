import whitebox


class WhiteboxPluginIcons(whitebox.Plugin):
    name = "Icons"

    provides_capabilities = ["icons"]
    exposed_component_map = {
        "icons": {
            # Logos
            "logo": "Logo",
            "logo-white-on-black": "generated/logos/WhiteOnBlack",
            # Icons
            "eye": "generated/icons/Eye",
            "info": "generated/icons/Info",
            "link": "generated/icons/Link",
            "close": "generated/icons/Close",
            "search": "generated/icons/Search",
            "cancel": "generated/icons/Cancel",
            "eclipse": "generated/icons/Eclipse",
            "spinner": "generated/icons/Spinner",
            "arrow-back": "generated/icons/ArrowBack",
            "camera-device": "generated/icons/CameraDevice",
            "check-circle": "generated/icons/CheckCircle",
            "chevron-right": "generated/icons/ChevronRight",
            "import-export": "generated/icons/ImportExport",
            "airplane": "generated/icons/Airplane",
            "arrow-forward": "generated/icons/ArrowForward",
            "edit": "generated/icons/Edit",
            "fullscreen-exit": "generated/icons/FullscreenExit",
            "play": "generated/icons/Play",
            "restart": "generated/icons/Restart",
            "chevron-down": "generated/icons/ChevronDown",
            "camera-roll": "generated/icons/CameraRoll",
            "trash": "generated/icons/Trash",
            "chevron-up": "generated/icons/ChevronUp",
            "chat": "generated/icons/Chat",
            "arrow-circle-up": "generated/icons/ArrowCircleUp",
            "play-circle": "generated/icons/PlayCircle",
            "stop-circle": "generated/icons/StopCircle",
            "video-camera": "generated/icons/VideoCamera",
            "calendar": "generated/icons/Calendar",
            "share": "generated/icons/Share",
            "location-target": "generated/icons/LocationTarget",
        },
    }


plugin_class = WhiteboxPluginIcons
