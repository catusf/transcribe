from transcribe import *

from gooey import Gooey, GooeyParser


@Gooey(program_name="Media Transcriber")
def main():
    global MEDIA_DIR, SUBTITLE_DIR, TRANSLATOR_SERVICE, LANGUAGE, DEST_LANGUAGE_1, DEST_LANGUAGE_2

    initial_checks()

    parser = GooeyParser(description="Transcriber Media & Translate Subtitles")

    parser.add_argument(
        "media_dir",
        metavar="Media Directory",
        action="store",
        default=MEDIA_DIR,
        help="Directory containing media files",
    )

    parser.add_argument(
        "subtitle_dir",
        metavar="Subtitle Directory",
        action="store",
        default=SUBTITLE_DIR,
        help="Directory to store subtitle files",
    )

    parser.add_argument(
        "translator_service",
        metavar="Translator Service",
        action="store",
        default=TRANSLATOR_SERVICE,
        help="Translation service to use (e.g., baidu, google, etc.)",
    )

    parser.add_argument(
        "language",
        metavar="Audio language",
        action="store",
        default=LANGUAGE,
        help="Audio language in English, such as chinese, vietnamese, english, etc.",
    )

    parser.add_argument(
        "dest_language_1",
        metavar="Destination language #1",
        action="store",
        default=DEST_LANGUAGE_1,
        help="Translated languaged #1 for instance vietnamese",
    )

    parser.add_argument(
        "dest_language_2",
        metavar="Destination language #2",
        action="store",
        default=DEST_LANGUAGE_2,
        help="Translated languaged #2 for instance english",
    )

    args = parser.parse_args()

    MEDIA_DIR = args.media_dir
    SUBTITLE_DIR = args.subtitle_dir
    TRANSLATOR_SERVICE = args.translator_service
    LANGUAGE = args.language
    DEST_LANGUAGE_1 = args.dest_language_1
    DEST_LANGUAGE_2 = args.dest_language_2

    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    if not os.path.exists(URL_FILE):
        with open(URL_FILE, "w", encoding="utf-8") as file:
            file.write(
                "# URLs to download. If needed, add a tab character and the filename.\n"
            )

    # iteration_count = 0
    # max_iterations = 10  # or some appropriate number based on your requirements

    print("Waiting for new media files...", flush=True)
    while True:
        process_urls(URL_FILE)
        transcribe_media(5)
        translate_subs(
            TRANSLATOR_SERVICE, LANGUAGE, DEST_LANGUAGE_1, DEST_LANGUAGE_2, 0
        )


if __name__ == "__main__":
    main()
