def includeme(config):
    config.include(".routes")
    config.include(".lists")
    config.include(".userdatas")
    config.include(".filelist")
    config.include(".career_path")
    config.include(".py3o")
    config.include("caerp.views.admin.userdatas")
