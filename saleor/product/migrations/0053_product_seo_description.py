# Generated by Django 2.0.2 on 2018-03-11 18:54
import html

import bleach
from django.core.validators import MaxLengthValidator
from django.db import migrations, models
from django.template.defaultfilters import truncatechars
from html5lib.serializer import HTMLSerializer


def get_cleaner(**serializer_kwargs: bool):
    """Build a bleach cleaner from the passed parameters.

    :param serializer_kwargs:
        options:
            - alphabetical_attributes
            - escape_lt_in_attrs
            - escape_rcdata
            - inject_meta_charset
            - minimize_boolean_attributes
            - omit_optional_tags
            - quote_attr_values
            - quote_char
            - resolve_entities
            - sanitize
            - space_before_trailing_solidus
            - strip_whitespace
            - use_best_quote_char
            - use_trailing_solidus
    :type serializer_kwargs: Dict[str, bool]

    :rtype: bleach.Cleaner
    """
    cleaner = bleach.Cleaner([], strip=True)
    for k, v in serializer_kwargs.items():
        if k not in HTMLSerializer.options:
            raise ValueError(
                "Parameter %s is not a valid option for HTMLSerializer" % k
            )
        setattr(cleaner.serializer, k, v)
    return cleaner


def strip_html(text: str, **serializer_kwargs: bool):
    """Remove (strip) HTML tags from text.

    Can also take additional parameters
    to be passed to the serializer (see `get_cleaner`).

    :param text:
     :type text: str
    :param serializer_kwargs:
     :type serializer_kwargs: Dict[str, bool]
    :rtype: str
    """
    cleaner = get_cleaner(**serializer_kwargs)
    text = cleaner.clean(text)
    return text


def strip_html_and_truncate(html_text: str, max_length: int):
    """Strip HTML tags and whitespaces from the text, then trim the description."""
    text = strip_html(html_text, strip_whitespace=True)
    text = truncatechars(text, max_length)
    return text


def to_seo_friendly(text):
    # saleor descriptions are stored as escaped HTML,
    # we need to decode them before processing them
    text = html.unescape(text)

    # cleanup the description and make it seo friendly
    return strip_html_and_truncate(text, 300)


def assign_seo_descriptions(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    for product in Product.objects.all():
        if product.seo_description is None:
            product.seo_description = to_seo_friendly(product.description)
            product.save()


class Migration(migrations.Migration):

    dependencies = [("product", "0052_slug_field_length")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="seo_description",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=300,
                validators=[MaxLengthValidator(300)],
            ),
            preserve_default=False,
        ),
        migrations.RunPython(assign_seo_descriptions),
    ]