if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "web":
        # e.g. `python -m clipit.main web https://my.site/to/inspect`
        url_to_load = sys.argv[2] if len(sys.argv) > 2 else None
        gui_web(target_url=url_to_load)
    else:
        gui_main()
