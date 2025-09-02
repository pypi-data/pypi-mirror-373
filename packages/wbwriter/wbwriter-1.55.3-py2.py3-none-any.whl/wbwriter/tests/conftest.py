from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.directory.factories import PersonFactory
from wbcore.contrib.geography.tests.signals import app_pre_migration
from wbwriter.factories import (
    ArticleFactory,
    ArticleTypeFactory,
    BlockFactory,
    InEditorTemplateFactory,
    MetaInformationFactory,
    MetaInformationInstanceFactory,
    PublicationParserFactory,
    TemplateFactory,
)

register(UserFactory)
register(ArticleFactory)
register(ArticleTypeFactory)
register(BlockFactory)
register(InEditorTemplateFactory)
register(PersonFactory)
register(PublicationParserFactory)
register(TemplateFactory)
register(MetaInformationFactory)
register(MetaInformationInstanceFactory)

from .signals import *

pre_migrate.connect(app_pre_migration, sender=apps.get_app_config("wbwriter"))
