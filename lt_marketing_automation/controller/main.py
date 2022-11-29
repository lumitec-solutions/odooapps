##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
import werkzeug
import json
import math
from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.http import request


class WebsiteSaleSlides(WebsiteSlides):

    def _fetch_from_access_token(self, channel_id, token):
        """ Check that given token matches an attendee from the given
        channel"""
        channel_sudo = request.env['slide.channel'].sudo().search(
            [('id', '=', channel_id.id)])
        if not token:
            partner_sudo = request.env['slide.channel.partner'].sudo()
        else:
            partner_sudo = request.env['slide.channel.partner'].sudo().search([
                ('channel_id', '=', channel_sudo.id),
                ('token', '=', token)
            ], limit=1)
        return channel_sudo, partner_sudo

    def sitemap_slide(env, rule, qs):
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/slides/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/slides/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '/slides/<model("slide.channel"):channel>',
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def slide_channel(self, channel, category=None, tag=None, page=1, slide_type=None,
                uncategorized=False, sorting=None, search=None, **kw):
        partner_sudo = request.env['slide.channel.partner'].sudo().search(
            [('channel_id', '=', channel.id),
             ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        partner_token = partner_sudo['token']
        if partner_token:
            return request.redirect('/slides/%s/%s' % (slug(channel), partner_token))
        else:
            fail_page = request.env.ref(
                'lt_marketing_automation.slide_redirect_fail').sudo()
            if not fail_page or not fail_page.is_published:
                raise ValidationError(
                    _('Only Attendees can view the course'))
            return werkzeug.utils.redirect(fail_page.url or '/')
            # raise werkzeug.exceptions.NotFound()

    @http.route([
        '/slides/<model("slide.channel"):channel>/<string:token>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>/<string:token>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/<string:token>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>/<string:token>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/<string:token>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>/<string:token>'
    ], type='http', auth="public", website=True, sitemap=sitemap_slide)
    def channel(self, channel, token, category=None, tag=None, page=1,
                slide_type=None,
                uncategorized=False, sorting=None, search=None, **kw):
        channel_sudo, partner_sudo = self._fetch_from_access_token(channel,
                                                                   token)
        if not partner_sudo:
            partner_sudo = request.env['slide.channel.partner'].sudo().search(
                    [('channel_id', '=', channel_sudo.id),
                     ('partner_id', '=', request.env.user.partner_id.id)], limit=1)
            partner_token = partner_sudo['token']
        else:
            partner_token = token
        domain = self._get_channel_slides_base_domain(channel)

        pager_url = "/slides/%s" % (channel.id)
        pager_args = {}
        slide_types = dict(request.env['slide.slide']._fields[
                               'slide_type']._description_selection(
            request.env))

        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('description', 'ilike', search),
                ('html_content', 'ilike', search)]
            pager_args['search'] = search
        else:
            if category:
                domain += [('category_id', '=', category.id)]
                pager_url += "/category/%s" % category.id
            elif tag:
                domain += [('tag_ids.id', '=', tag.id)]
                pager_url += "/tag/%s" % tag.id
            if uncategorized:
                domain += [('category_id', '=', False)]
                pager_args['uncategorized'] = 1
            elif slide_type:
                domain += [('slide_type', '=', slide_type)]
                pager_url += "?slide_type=%s" % slide_type

        # sorting criterion
        if channel.channel_type == 'documentation':
            default_sorting = 'latest' if channel.promote_strategy in [
                'specific', 'none', False] else channel.promote_strategy
            actual_sorting = sorting if sorting and sorting in request.env[
                'slide.slide']._order_by_strategy else default_sorting
        else:
            actual_sorting = 'sequence'
        order = request.env['slide.slide']._order_by_strategy[actual_sorting]
        pager_args['sorting'] = actual_sorting

        slide_count = request.env['slide.slide'].sudo().search_count(domain)
        page_count = math.ceil(slide_count / self._slides_per_page)
        pager = request.website.pager(url=pager_url, total=slide_count,
                                      page=page,
                                      step=self._slides_per_page,
                                      url_args=pager_args,
                                      scope=page_count if page_count < self._pager_max_pages else self._pager_max_pages)

        query_string = None
        if category:
            query_string = "?search_category=%s" % category.id
        elif tag:
            query_string = "?search_tag=%s" % tag.id
        elif slide_type:
            query_string = "?search_slide_type=%s" % slide_type
        elif uncategorized:
            query_string = "?search_uncategorized=1"

        values = {
            'channel': channel,
            'main_object': channel,
            'partner_token': partner_token,
            'active_tab': kw.get('active_tab', 'home'),
            # search
            'search_category': category,
            'search_tag': tag,
            'search_slide_type': slide_type,
            'search_uncategorized': uncategorized,
            'query_string': query_string,
            'slide_types': slide_types,
            'sorting': actual_sorting,
            'search': search,
            # display data
            'user': request.env.user,
            'pager': pager,
            'is_public_user': request.website.is_public_user(),
            # display upload modal
            'enable_slide_upload': 'enable_slide_upload' in kw,
            **self._slide_channel_prepare_review_values(channel),
        }

        # fetch slides and handle uncategorized slides; done as sudo because we want to display all
        # of them but unreachable ones won't be clickable (+ slide controller will crash anyway)
        # documentation mode may display less slides than content by category but overhead of
        # computation is reasonable
        if channel.promote_strategy == 'specific':
            values['slide_promoted'] = channel.sudo().promoted_slide_id
        else:
            values['slide_promoted'] = request.env['slide.slide'].sudo().search(
                domain, limit=1, order=order)

        limit_category_data = False
        if channel.channel_type == 'documentation':
            if category or uncategorized:
                limit_category_data = self._slides_per_page
            else:
                limit_category_data = self._slides_per_category

        values['category_data'] = channel._get_categorized_slides(
            domain, order,
            force_void=not category,
            limit=limit_category_data,
            offset=pager['offset'])
        values['channel_progress'] = self._get_channel_progress(channel,
                                                                include_quiz=True)

        # for sys admins: prepare data to install directly modules from eLearning when
        # uploading slides. Currently supporting only survey, because why not.
        if request.env.user.has_group('base.group_system'):
            module = request.env.ref('base.module_survey')
            if module.state != 'installed':
                values['modules_to_install'] = [{
                    'id': module.id,
                    'name': module.shortdesc,
                    'motivational': _('Evaluate and certify your students.'),
                }]

        values = self._prepare_additional_channel_values(values, **kw)
        return request.render('website_slides.course_main', values)
