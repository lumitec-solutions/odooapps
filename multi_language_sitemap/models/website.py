import base64
import logging

import datetime
from odoo import models, fields, http, api
from odoo.http import request
from itertools import islice
from odoo.addons.http_routing.models.ir_http import slug,slugify
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.osv.expression import FALSE_DOMAIN

SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)
LOC_PER_SITEMAP = 45000

logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    def create_website_sitemap(self):
        website_ids = self.env['website'].search([])
        for rec in website_ids:
            current_website = rec
            Attachment = self.env['ir.attachment'].sudo()
            View = self.env['ir.ui.view'].sudo()
            mimetype = 'application/xml;charset=utf-8'
            content = None

            def create_sitemap(url, content):
                return Attachment.create({
                    'raw': content.encode(),
                    'mimetype': mimetype,
                    'type': 'binary',
                    'name': url,
                    'url': url,
                })

            if not content:
                # Remove all sitemaps in ir.attachments as we're going to regenerated them
                dom = [('type', '=', 'binary'), '|',
                       ('url', '=like', '/sitemap-%d-%%.xml' % current_website.id),
                       ('url', '=', '/sitemap-%d.xml' % current_website.id)]
                sitemaps = Attachment.search(dom)
                sitemaps.unlink()

                pages = 0
                locs = rec.with_user(
                    rec.user_id).sudo().enumerate_pages_lang()
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                while True:
                    values = {
                        'locs': islice(locs, 0, LOC_PER_SITEMAP),
                        'url_root': base_url,
                    }
                    urls = View._render_template('website.sitemap_locs', values)
                    if urls.strip():
                        content = View._render_template('website.sitemap_xml',
                                                       {'content': urls})
                        pages += 1
                        last_sitemap = create_sitemap(
                            '/sitemap-%d-%d.xml' % (current_website.id, pages),
                            content)
                    else:
                        break

                if not pages:
                    return request.not_found()
                elif pages == 1:
                    # rename the -id-page.xml => -id.xml
                    last_sitemap.write({
                        'url': "/sitemap-%d.xml" % current_website.id,
                        'name': "/sitemap-%d.xml" % current_website.id,
                    })
                else:
                    # TODO: in master/saas-15, move current_website_id in template directly
                    pages_with_website = ["%d-%d" % (current_website.id, p) for p in
                                          range(1, pages + 1)]

                    # Sitemaps must be split in several smaller files with a sitemap index
                    content = View._render_template('website.sitemap_index_xml', {
                        'pages': pages_with_website,
                        'url_root': base_url + '/',
                    })
                    create_sitemap('/sitemap-%d.xml' % current_website.id, content)

    def enumerate_pages_lang(self, query_string=None, force=False):
        router = http.root.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()

        sitemap_endpoint_done = set()

        for rule in router.iter_rules():
            if 'sitemap' in rule.endpoint.routing and rule.endpoint.routing[
                'sitemap'] is not True:
                if rule.endpoint in sitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func = rule.endpoint.routing['sitemap']
                if func is False:
                    continue
                for loc in func(self.env, rule, query_string):
                    yield loc
                    for lang in self.language_ids:
                        if lang.url_code != self.default_lang_id.url_code:
                            url_lang = '/'+lang.url_code+loc['loc']
                            new_loc = {'loc': url_lang}
                            yield new_loc
                continue

            if not self.rule_is_enumerable(rule):
                continue

            if 'sitemap' not in rule.endpoint.routing:
                logger.warning(
                    'No Sitemap value provided for controller %s (%s)' %
                    (rule.endpoint.method,
                     ','.join(rule.endpoint.routing['routes'])))

            converters = rule._converters or {}
            if query_string and not converters and (
                    query_string not in rule.build({}, append_unknown=False)[
                1]):
                continue

            values = [{}]
            # converters with a domain are processed after the other ones
            convitems = sorted(
                converters.items(),
                key=lambda x: (
                    hasattr(x[1], 'domain') and (x[1].domain != '[]'),
                    rule._trace.index((True, x[0]))))

            for (i, (name, converter)) in enumerate(convitems):
                if 'website_id' in self.env[converter.model]._fields and (
                        not converter.domain or converter.domain == '[]'):
                    converter.domain = "[('website_id', 'in', (False, current_website_id))]"

                newval = []
                for val in values:
                    query = i == len(convitems) - 1 and query_string
                    if query:
                        r = "".join([x[1] for x in rule._trace[1:] if not x[
                            0]])  # remove model converter from route
                        query = sitemap_qs2dom(query, r, self.env[
                            converter.model]._rec_name)
                        if query == FALSE_DOMAIN:
                            continue

                    for rec in converter.generate(uid=self.env.uid, dom=query,
                                                  args=val):
                        newval.append(val.copy())
                        newval[-1].update({name: rec})
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                if not query_string or query_string.lower() in url.lower():
                    page = {'loc': url}
                    if url in url_set:
                        continue
                    url_set.add(url)
                    yield page
                    for lang in self.language_ids:
                        if lang.url_code != self.default_lang_id.url_code:
                            lang_urls = ''
                            if len(value) > 1:
                                for val in value:
                                    if val != 'current_website_id':
                                        model, mode_id = str(value.get(val)).split('(')
                                        trans_val = self.env[
                                            'ir.translation'].sudo().search(
                                            [('name', '=', model+',name'),
                                                ('res_id', '=', value.get(val).id),
                                                ('lang', '=', lang.code)])
                                        if trans_val.value:
                                            lang_urls += '/'+slugify(trans_val.value)+'-'+str(value.get(val).id)
                                        else:
                                            lang_urls += '/' + slugify(
                                                value.get(val).name) + '-' + str(
                                                value.get(val).id)
                                if url[-5:] == '/feed':
                                    set_url = '/' + lang.url_code + '/' + \
                                              list(value)[1] + lang_urls + '/feed'
                                else:
                                    set_url = '/' + lang.url_code + '/' + list(value)[1]  +  lang_urls
                                if set_url:
                                    lang_page = {'loc': set_url}
                                    yield lang_page
                            if value == {} and url:
                                val_url = '/'+lang.url_code + url
                                yield {'loc': val_url}

        # '/' already has a http.route & is in the routing_map so it will already have an entry in the xml
        domain = [('url', '!=', '/')]
        if not force:
            domain += [('website_indexed', '=', True),
                       ('visibility', '=', False)]
            # is_visible
            domain += [
                ('website_published', '=', True), ('visibility', '=', False),
                '|', ('date_publish', '=', False),
                ('date_publish', '<=', fields.Datetime.now())
            ]

        if query_string:
            domain += [('url', 'like', query_string)]

        pages = self._get_website_pages(domain)

        for page in pages:
            record = {'loc': page['url'], 'id': page['id'],
                      'name': page['name']}
            if page.view_id and page.view_id.priority != 16:
                record['priority'] = min(round(page.view_id.priority / 32.0, 1),
                                         1)
            if page['write_date']:
                record['lastmod'] = page['write_date'].date()
            yield record
            for lang in self.language_ids:
                if lang.url_code != self.default_lang_id.url_code:
                    lang_record = {'loc': '/' + lang.url_code + page['url']}
                    if page.view_id and page.view_id.priority != 16:
                        lang_record['priority'] = min(
                            round(page.view_id.priority / 32.0, 1), 1)
                    if page['write_date']:
                        lang_record['lastmod'] = page['write_date'].date()
                    yield lang_record
