import logging
from odoo import api, models
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

from odoo.addons.website.models.ir_http import ModelConverter, \
    _guess_mimetype

logger = logging.getLogger(__name__)


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_converters(cls):
        """ Get the converters list for custom url pattern werkzeug need to
            match Rule. This override adds the website ones.
        """
        return dict(
            super(Http, cls)._get_converters(),
            model=ModelConverter,
        )


class ModelConverter(ModelConverter):

    def generate_record(self, uid, dom=None, args=None):
        Model = request.env[self.model].with_user(uid)
        # Allow to current_website_id directly in route domain
        args.update(
            current_website_id=request.env['website'].get_current_website().id)
        website_id = request.env['website'].get_current_website()
        domain = safe_eval(self.domain, (args or {}).copy())
        if dom:
            domain += dom
        for record in Model.search_read(domain, ['display_name']):
            yield {'loc': (record['id'], record['display_name']), 'model': self.model}
