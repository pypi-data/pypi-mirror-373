from opentelemetry_distro_odoo.distro import odoo


def load_opentelemetry_odoo_distro():
    odoo.OdooDistro().configure()
