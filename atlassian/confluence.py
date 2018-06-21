import logging
from requests.exceptions import HTTPError
from atlassian import AtlassianRestAPI


log = logging.getLogger('atlassian.confluence')


class Confluence(AtlassianRestAPI):

    def page_exists(self, space, title):
        try:
            self.get_page_by_title(space, title)
            log.info('Page "{title}" already exists in space "{space}"'.format(space=space, title=title))
            return True
        except (HTTPError, KeyError, IndexError):
            log.info('Page "{title}" does not exist in space "{space}"'.format(space=space, title=title))
            return False

    def get_page_title(self, page_id):
        page = self.get_page_by_id(page_id)
        return page.get('title') if page else None

    def get_page_id(self, space, title):
        page = self.get_page_by_title(space, title)
        return page.get('id') if page else None

    def get_page_space(self, page_id):
        page = self.get_page_by_id(page_id, expand='space')
        return page['space']['key'] if page else None

    def get_page_by_title(self, space, title, status='current',
                          representation='storage', expand=None):
        expand = expand + ',' if expand else ''
        expand += 'body.{representation}'.format(representation=representation)
        url = '/rest/api/content?spaceKey={space}&title={title}&' \
              'status={status}&expand={expand}'.format(space=space,
                                                       title=title,
                                                       status=status,
                                                       expand=expand)
        page = self.get(url)
        results = page['results'] if page else None
        return None if not results else results[0] if len(
                results) == 1 else results

    def get_page_by_id(self, page_id, status='current',
                       representation='storage', expand=None):
        expand = expand + ',' if expand else ''
        expand += 'body.{representation}'.format(representation=representation)
        url = '/rest/api/content/{page_id}?status={status}&expand={expand}'.\
            format(page_id=page_id, status=status, expand=expand)
        return self.get(url)

    def create_page(self, space, parent_id, title, body, type='page'):
        log.info('Creating {type} "{space}" -> "{title}"'.format(space=space, title=title, type=type))
        return self.post('/rest/api/content/', data={
            'type': type,
            'ancestors': [{'type': type, 'id': parent_id}],
            'title': title,
            'space': {'key': space},
            'body': {'storage': {
                'value': body,
                'representation': 'storage'}}})

    def history(self, page_id):
        return self.get('/rest/api/content/{0}/history'.format(page_id))

    def is_page_content_is_already_updated(self, page_id, body):
        confluence_content = self.get_page_by_id(page_id, expand='body.storage')['body']['storage']['value']
        confluence_content = confluence_content.replace('&oacute;', 'ó')

        log.debug('Old Content: """{body}"""'.format(body=confluence_content))
        log.debug('New Content: """{body}"""'.format(body=body))

        if confluence_content == body:
            log.warning('Content of {page_id} is exactly the same'.format(page_id=page_id))
            return True
        else:
            log.info('Content of {page_id} differs'.format(page_id=page_id))
            return False

    def update_page(self, parent_id, page_id, title, body, type='page',
                    is_already_updated=None):
        log.info('Updating {type} "{title}"'.format(title=title, type=type))

        if is_already_updated is None:
            def is_already_updated(self_, page_id_, body_):
                return self_.is_page_content_is_already_updated(page_id_,
                                                                body_)

        if is_already_updated(self, page_id, body):
            return self.get_page_by_id(page_id)
        else:
            version = self.history(page_id)['lastUpdated']['number'] + 1

            data = {
                'id': page_id,
                'type': type,
                'title': title,
                'body': {'storage': {
                    'value': body,
                    'representation': 'storage'}},
                'version': {'number': version}
            }

            if parent_id:
                data['ancestors'] = [{'type': 'page', 'id': parent_id}]

            return self.put('/rest/api/content/{0}'.format(page_id), data=data)

    def update_or_create(self, parent_id, title, body):
        space = self.get_page_space(parent_id)

        if self.page_exists(space, title):
            page_id = self.get_page_id(space, title)
            result = self.update_page(parent_id, page_id, title, body)
        else:
            result = self.create_page(space, parent_id, title, body)

        log.warning('You may access your page at: {host}{url}'.format(
            host=self.url,
            url=result['_links']['tinyui']))

        return result
