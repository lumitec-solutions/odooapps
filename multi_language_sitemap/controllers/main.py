import base64
import datetime
from odoo import models, fields, http, api
from odoo.http import request
from odoo.addons.portal.controllers.web import Home
from itertools import islice

SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)
LOC_PER_SITEMAP = 45000


class Website(Home):

    @http.route('/sitemap.xml', type='http', auth="public", website=True,
                multilang=False, sitemap=False)
    def sitemap_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None
        dom = [('url', '=', '/sitemap-%d.xml' % current_website.id),
               ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)
        if sitemap:
            content = base64.b64decode(sitemap.datas)
        return request.make_response(content, [('Content-Type', mimetype)])
