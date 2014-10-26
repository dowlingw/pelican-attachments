import os
import shutil
import six

from logging import warning, info

from pelican import signals
from pelican.contents import Static
from pelican.utils import copy, process_translations, mkdir_p

METADATA_KEY = 'attachments'


def get_generators(generators):
    return AttachmentGenerator


def register():
    signals.get_generators.connect(get_generators)


class AttachmentGenerator(object):

    def __init__(self, context, settings, path, theme, output_path, *null):
        self.staticfiles = []
        self.output_path = output_path
        self.context = context
        self.settings = settings
        self.siteurl = settings.get('SITEURL')

    def generate_context(self):
        for article in self.context['articles']:
            if METADATA_KEY in article.metadata:
                files = article.metadata[METADATA_KEY].split(', ')
                for file in files:
                    self._emitfile(article,file)

    def _emitfile(self, article, filename):
        file_path = os.path.join( os.path.dirname(article.get_relative_source_path()), filename )
        src_path = os.path.join( os.path.dirname(article.source_path), filename )
        file_relurl = os.path.join( article.url, filename )
        metadata = { 'save_as': file_relurl }
        sc = Static(
            content=None,
            metadata=metadata,
            settings=self.settings,
            source_path=src_path )
        sc.override_url = file_relurl
        self.staticfiles.append(sc)
        self.context['filenames'][file_path] = sc


    def generate_output(self, writer):
        for sc in self.staticfiles:
            output_file = os.path.join(self.output_path, sc.save_as )
            try:
                os.makedirs(os.path.dirname(output_file) )
            except:
                pass
            shutil.copy(sc.source_path, output_file)

