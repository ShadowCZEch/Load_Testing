if __name__ == "__main__":
    if cfg is None:
        try:
            cfg=config_load()
        except Exception as e:
            print("Error when loading configuration from file:",e,file=sys.stderr)
            sys.exit(1)

    try:
        users = cfg_int(cfg["unique_users_count"])
        spawn_rate = 10
        run_time = cfg_str(cfg["time_total"])
        html_out = "report.html"
    except Exception as e:
        print("Error when loading configuration from file:",e,file=sys.stderr)
        sys.exit(2)

    try:
        run_locust_headless_and_make_report(
            locustfile=__file__,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            html_out=html_out,
        )
    except subprocess.CalledProcessError as e:
        print("Error when running Locust process:",e,file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print("Error generating report:",e,file=sys.stderr)
        sys.exit(4)
