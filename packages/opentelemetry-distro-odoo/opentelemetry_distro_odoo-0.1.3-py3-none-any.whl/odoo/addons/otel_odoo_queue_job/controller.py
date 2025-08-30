from odoo.addons.queue_job.controllers.main import RunJobController

from opentelemetry_distro_odoo.instrumentation.odoo import OdooInstrumentor


class OTelRunJobController(RunJobController):
    def _try_perform_job(self, env, job):
        span_attrs = {
            "odoo.queue.job.uuid": job.uuid,
            "odoo.queue.job.model_name": job.model_name,
            "odoo.queue.job.method_name": job.method_name,
            "odoo.queue.job.func_string": job.func_string,
        }

        def _post_callback(span):
            span.set_attribute("odoo.queue.job.state", job.state)

        with OdooInstrumentor().odoo_call_wrapper(
            "queue.job",
            "perform",
            span_attrs=span_attrs,
            post_span_callback=_post_callback,
            common_attrs={"odoo.queue.job.channel": job.channel},
        ):
            return super()._try_perform_job(env, job)
