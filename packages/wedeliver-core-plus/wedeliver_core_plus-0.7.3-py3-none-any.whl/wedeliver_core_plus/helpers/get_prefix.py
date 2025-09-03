from wedeliver_core_plus import WedeliverCorePlus


def get_prefix(service_url):
    app = WedeliverCorePlus.get_app()
    final_url = ""
    service_name = app.config.get("SERVICE_NAME")
    if service_name:
        final_url += "/{}".format(service_name)

    final_url += service_url

    app.logger.debug(final_url)

    return final_url
