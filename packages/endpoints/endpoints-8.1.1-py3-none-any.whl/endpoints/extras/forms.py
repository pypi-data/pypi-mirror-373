# -*- coding: utf-8 -*-

from datatypes import Enum


"""

Links and searches I had open while writing this:

    * https://github.com/Jaymon/Montage/blob/master/src/Montage/Form/Field/Input.php
    * https://github.com/Jaymon/Montage/blob/master/src/Montage/Form/Field/Textarea.php
    * https://proper-forms.scaletti.dev/introduction/#diving-into-it
    * https://github.com/jpsca/proper-forms
    * https://deformdemo.pylonsproject.org/sequence_of_fileuploads_with_initial_item/
    * python html forms library
    * https://www.w3schools.com/tags/tag_input.asp
"""


class Element(object):
    attributes = None

    @property
    def TAG_NAME(self):
        raise NotImplementedError()

    def render_attributes(self, **attributes):
        if not self.attributes and not attributes:
            return ""

        attrs = dict(self.attributes)
        attrs.update(attributes)

        ret = []
        for name, value in attrs.items():
            ret.append(f"{name}=\"{value}\"")

        return " ".join(ret)

    def render_start(self, **attributes):
        s = f"<{self.TAG_NAME}"

        attr_str = self.render_attributes(**attributes)
        if attr_str:
            s += f" {attr_str}"

        s += ">"
        return s

    def render_body(self):
        return ""

    def render_stop(self):
        return f"</{self.TAG_NAME}>"

    def render(self):
        return "".join([
            self.render_start(),
            self.render_body(),
            self.render_stop()
        ])


class Form(Element):

    TAG_NAME = "form"

    METHOD_POST = "POST"
    METHOD_GET = "GET"

    ENCODING_FILE = "multipart/form-data"

    ENCODING_POST = "application/x-www-form-urlencoded"

    field_names = []
    field_instances = []

    @property
    def fields(self):
        d = {}
        for field_name in self.field_names:
            d[field_name] = getattr(self, field_name)

        return d

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.attributes["encoding"] = self.ENCODING_POST
        self.attributes["method"] = self.METHOD_POST

    def render(self):
        s = [self.render_start()]

        for field in self.field_instances:
            s.append(
                field.render(getattr(self, field.name))
            )

    def __str__(self):
        return self.render()


class Field(Element):
    def __init__(self, field_required=True, **kwargs):
        self.required = field_required
        self.attributes = kwargs

    def __set_name__(self, field_class, name):
        self.name = name
        self.field_class = field_class
        self.field_class.field_names.append([name])
        self.field_class.field_instances.append(self)

    def __get__(self, field, field_class=None):
        if field is None:
            return self

        try:
            return field.__dict__[self.name]

        except KeyError as e:
            raise AttributeError(self.name) from e

    def __set__(self, field, value):
        field.__dict__[self.name] = value

    def __init__(self, field):

        try:
            del field.__dict__[self.name]

        except KeyError as e:
            raise AttributeError(self.name) from e


class Input(Field):
    TAG_NAME = "input"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_input_type()

    def set_input_type(self):
        input_type = self.__class__.__name__.lower()
        if input_type == "input":
            input_type = "text"

        self.atributes["type"] = input_type

    def render(self, value=None):
        attrs = {}
        if value:
            attrs["value"] = value # TODO get safe method to html encode

        s = [self.render_start(**attrs)]
        s.append(self.render_stop())

        return "".join(s)


class Hidden(Input):
    pass


class Password(Input):
    pass


class Textarea(Field):
    TAG_NAME = "textarea"

    def render(self, value=None):
        s = [self.render_start()]

        if value:
            s.append(value) # TODO get safe method to html encode

        s.append(self.render_stop())

        return "".join(s)

