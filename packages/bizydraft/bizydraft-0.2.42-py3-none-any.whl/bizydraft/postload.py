from loguru import logger


def lazy_hook():
    try:
        import app.database.db
        import comfy.utils

        origin_fun_post_add_routes = comfy.utils.set_progress_bar_global_hook
        origin_fun_pre_add_routes = app.database.db.init_db

        def hijack_all_pre_add_routes():
            from bizydraft.hijack_routes import hijack_routes_pre_add_routes

            hijack_routes_pre_add_routes()

        def new_fun_pre_add_routes(*args, **kwargs):
            hijack_all_pre_add_routes()
            origin_fun_pre_add_routes(*args, **kwargs)

        def hijack_all_post_add_routes():
            from bizydraft.hijack_nodes import hijack_nodes

            hijack_nodes()

            from bizydraft.hijack_routes import hijack_routes_post_add_routes

            hijack_routes_post_add_routes()

            from bizydraft.block_nodes import remove_blacklisted_nodes

            remove_blacklisted_nodes()

        def new_fun_post_add_routes(*args, **kwargs):
            hijack_all_post_add_routes()
            origin_fun_post_add_routes(*args, **kwargs)

        comfy.utils.set_progress_bar_global_hook = new_fun_post_add_routes
        app.database.db.init_db = new_fun_pre_add_routes

    except Exception as e:
        logger.error(f"failed to lazyhook: {e}")
        exit(1)
