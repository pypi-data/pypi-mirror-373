from collections import OrderedDict, defaultdict
from datetime import datetime
import re
from decimal import Decimal

from typing import Optional, TypeVar

from dmutils.formats import DATE_FORMAT, DISPLAY_DATE_FORMAT

from .converters import convert_to_boolean, convert_to_number, convert_to_pence
from .errors import ContentNotFoundError
from .formats import format_price
from .govuk_frontend import get_href
from .utils import TemplateField, drop_followups, drop_dependent_follow_ups, get_option_value, is_option_divider

TQuestion = TypeVar("TQuestion", bound="Question")
TMultiquestion = TypeVar("TMultiquestion", bound="Multiquestion")
TListMultiquestion = TypeVar("TListMultiquestion", bound="ListMultiquestion")


class Question(object):
    MARKDOWN_FIELDS = ['question_advice']
    TEMPLATE_FIELDS = ['name', 'question', 'hint']
    TEMPLATE_OPTIONS_FIELDS = [('options', 'description'), ('validations', 'message')]
    MULTIQUESTION_TYPES = ('multiquestion', 'formula',)

    def __init__(self, data, number=None, _context=None):
        self.number = number
        self._data = data.copy()
        self._context = _context

    def summary(self, service_data, inplace_allowed: bool = False) -> "QuestionSummary":
        return QuestionSummary(self, service_data)

    def filter(
        self: TQuestion,
        context,
        dynamic=True,
        inplace_allowed: bool = False,
        ignore_depends_on_follow_up: bool = False
    ) -> Optional[TQuestion]:
        if not self._should_be_shown(context, ignore_depends_on_follow_up):
            return None

        if inplace_allowed:
            self._context = context
            return self

        return self.__class__(self._data, number=self.number, _context=context)

    def _should_be_shown(self, context, ignore_depends_on_follow_up):
        return all(
            depends["on"] in context and (context[depends["on"]] in depends["being"])
            for depends in self.get("depends", [])
        ) and (
            ignore_depends_on_follow_up
            or all(
                question_id in context and (set(context[question_id]).intersection(set(question_values)))
                for question_id, question_values in self.get("depends_on_follow_up", {}).items()
            )
        )

    def get_question(self, field_name):
        if self.id == field_name:
            return self

    def get_data(self, form_data):
        data = self._get_data(form_data)

        if not self.get('assuranceApproach'):
            return data

        value = {}

        if data.get(self.id) is not None:
            value = {"value": data[self.id]}

        if f'{self.id}--assurance' in form_data:
            value['assurance'] = form_data.get(f'{self.id}--assurance')

        return {self.id: value}

    def _get_data(self, form_data):  # noqa: C901
        if self.id not in form_data and self.type not in ['boolean_list', 'upload']:
            return {}

        if self.type == 'boolean_list':

            # if self.id is 'q5', form keys will come back as ('q5-0', 'true'), ('q5-1', 'false'), ('q5-3', 'true'), ...
            # here, we build a dict with keys as indices and values converted to boolean, eg {0: True, 1: False, 3: True, ...}  # noqa
            boolean_indices_and_values = {
                int(k.split('-')[-1]): convert_to_boolean(v) for k, v in form_data.items()
                if k.startswith(f"{self.id}-") and k.split('-')[-1].isdigit()
            }

            if not boolean_indices_and_values:
                return {}

            value = [None] * (max(boolean_indices_and_values.keys()) + 1)
            for k, v in boolean_indices_and_values.items():
                value[k] = v

        elif self.type == 'boolean':
            value = convert_to_boolean(form_data[self.id])
        elif self.type == 'number':
            kwargs = {}
            if self.get("unit"):
                if self.unit_position == "after":
                    kwargs["suffix"] = self.unit
                elif self.unit_position == "before":
                    kwargs["prefix"] = self.unit

            value = convert_to_number(form_data[self.id], **kwargs)
        elif self.type == 'money':
            value = convert_to_pence(form_data[self.id])
        elif self.type == 'upload':
            upload_id = f"{self.id}-upload"

            if upload_id in form_data:
                value = form_data[upload_id]
            else:
                return {}
        else:
            value = form_data[self.id]

        if self.type not in ['boolean', 'number', 'money']:
            value = value if value else None

        return {self.id: value}

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        error_fields = set(errors.keys()) & set(self.form_fields)
        if not error_fields:
            return OrderedDict()

        question_errors = OrderedDict()
        for field_name in sorted(error_fields):
            question = self.get_question(field_name)
            message_key = errors[field_name]
            validation_message = question.get_error_message(message_key, field_name)

            error_key = question.id
            if message_key == 'assurance_required':
                error_key = f'{error_key}--assurance'

            question_errors[error_key] = {
                'input_name': error_key,
                'href': question.href,
                'question': getattr(question, question_descriptor_from),
                'message': validation_message,
            }

        return question_errors

    def unformat_data(self, data):
        return {self.id: data.get(self.id, None)}

    def get_error_message(self, message_key, field_name=None):
        """Return a single error message.

        :param message_key: error message key as returned by the data API
        :param field_name:
        """
        if field_name is None:
            field_name = self.id
        for validation in self.get_question(field_name).get('validations', []):
            if validation['name'] == message_key:
                if validation.get('field', field_name) == field_name:
                    return validation['message']

        defaults = {
            'answer_required': 'You need to answer this question.'
        }

        return defaults.get(message_key, 'There was a problem with the answer to this question.')

    @property
    def href(self):
        """Return the URL fragment for the first input element for this question"""
        return get_href(self)

    @property
    def label(self):
        return self.get('name') or self.question

    @property
    def form_fields(self):
        return [self.id]

    @property
    def is_optional(self):
        return self.get('optional')

    @property
    def values_followup(self):
        """Return a reversed (value->followups) followup mapping

        Form templates need a reversed followup structure: a list of question
        ids that follow a certain question value.

        """

        if not self.get('followup'):
            return {}

        followups = defaultdict(list)
        for q, values in self.followup.items():
            for value in values:
                followups[value].append(q)

        return dict(followups)

    @property
    def required_form_fields(self):
        return [field for field in self.form_fields if field not in self._optional_form_fields]

    @property
    def _optional_form_fields(self):
        if self.get('optional'):
            return self.form_fields

        return []

    @property
    def type_is_multiquestion(self):
        return self.type in self.MULTIQUESTION_TYPES

    def inject_brief_questions_into_boolean_list_question(self, brief):
        if self.type == 'boolean_list':
            if self.id not in brief.keys() and not self.get('optional'):
                raise ContentNotFoundError(f"No {self.id} found for brief {brief['id']}")

            # briefs might not have optional boolean_list questions
            self.boolean_list_questions = brief.get(self.id, [])

    def has_assurance(self):
        return bool(self.get('assuranceApproach'))

    def get_question_ids(self, type=None):
        return [self.id] if type in [self.type, None] else []

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getattr__(self, key):
        if key not in self._data:
            raise AttributeError(key)

        field = self._data[key]

        if isinstance(field, TemplateField):
            return field.render(self._context)

        if key in [_field for _field, _ in self.TEMPLATE_OPTIONS_FIELDS]:
            return [
                {
                    k: (v.render(self._context) if isinstance(v, TemplateField) else v)
                    for k, v in i.items()
                }
                for i in field
            ]

        return field

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        return key in self._data

    def get_source(self, key, default=None):
        try:
            field = self._data[key]
        except KeyError:
            return default

        if isinstance(field, TemplateField):
            return field.source
        else:
            return field

    def __repr__(self):
        return f'<{self.__class__.__name__}: number={self.number}, data={self._data}>'


class Multiquestion(Question):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        self.questions = [
            ContentQuestion(question)
            for question in data['questions']
        ]

    def summary(self, service_data, inplace_allowed: bool = False) -> "MultiquestionSummary":
        return MultiquestionSummary(self, service_data)

    def filter(
        self: TMultiquestion,
        context,
        dynamic=True,
        inplace_allowed: bool = False,
        ignore_depends_on_follow_up: bool = False
    ) -> Optional[TMultiquestion]:
        multi_question = super().filter(
            context,
            dynamic=dynamic,
            inplace_allowed=inplace_allowed,
            ignore_depends_on_follow_up=ignore_depends_on_follow_up
        )
        if not multi_question:
            return None

        multi_question.questions = list(filter(None, [
            question.filter(
                context,
                dynamic,
                inplace_allowed=inplace_allowed,
                ignore_depends_on_follow_up=ignore_depends_on_follow_up
            )
            for question in multi_question.questions
        ]))

        return multi_question

    def get_question(self, field_name):
        if self.id == field_name:
            return self

        return next(
            (question for question in self.get_questions_flat() if question.id == field_name),
            None
        )

    def get_questions_flat(self, ignore_multiquestion=False):
        questions = []

        for question in self.questions:
            if question.type_is_multiquestion:
                if not ignore_multiquestion:
                    questions.append(question)

                for multiquestion in question.get_questions_flat(ignore_multiquestion=ignore_multiquestion):
                    questions.append(multiquestion)
            else:
                questions.append(question)

        return questions

    def get_data(self, form_data):
        questions_data = {}
        for question in self.get_questions_flat():
            for key, value in question.get_data(form_data).items():
                if key not in questions_data:
                    questions_data[key] = value

        list_multi_question_index = self.get('index', None)

        questions_data = drop_followups(
            self,
            questions_data,
            nested=list_multi_question_index is not None,
            list_multi_question_index=list_multi_question_index
        )
        questions_data = drop_dependent_follow_ups(self, questions_data)

        return questions_data

    @property
    def form_fields(self):
        return [form_field for question in self.questions for form_field in question.form_fields]

    @property
    def _optional_form_fields(self):
        if self.get('optional'):
            return self.form_fields

        return [form_field for question in self.questions for form_field in question._optional_form_fields]

    def get_question_ids(self, type=None):
        return [
            question.id for question in self.get_questions_flat(
                ignore_multiquestion=True
            ) if type in [question.type, None]
        ]

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        # Multi-question errors should have the same ordering as the questions
        errors = super().get_error_messages(
            errors, question_descriptor_from=question_descriptor_from
        )
        return OrderedDict(
            (q.id, errors[q.id]) for q in self.get_questions_flat(ignore_multiquestion=True) if q.id in errors.keys()
        )


class DynamicList(Multiquestion):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.type = 'multiquestion'  # same UI components as Multiquestion

    def filter(
        self,
        context,
        dynamic=True,
        inplace_allowed: bool = False,
        ignore_depends_on_follow_up: bool = False
    ) -> Optional["DynamicList"]:
        if not dynamic:
            return super().filter(
                context,
                dynamic=dynamic,
                inplace_allowed=inplace_allowed,
                ignore_depends_on_follow_up=ignore_depends_on_follow_up
            )

        dynamic_list = super(Multiquestion, self).filter(
            context,
            dynamic=dynamic,
            inplace_allowed=inplace_allowed,
            ignore_depends_on_follow_up=ignore_depends_on_follow_up
        )
        if not dynamic_list:
            return None

        # dynamic_field: 'brief.essentialRequirements'
        dynamic_questions = self.get_dynamic_questions(context)

        dynamic_list.questions = list(filter(None, [
            self._make_dynamic_question(question, item, index)
            for index, item in enumerate(dynamic_questions)
            for question in dynamic_list.questions
        ]))

        return dynamic_list

    def get_dynamic_questions(self, context):
        """ Returns the value of the dynamic.field from the context """
        dynamic_questions = context
        for key in self.dynamic_field.split('.'):
            dynamic_questions = dynamic_questions[key]
        return dynamic_questions

    def get_data(self, form_data):
        """
        # IN
        {
            "respondToEmailAddress": "paul@paul.paul",
            "yesno-0": "true",
            "yesno-1": "false",
            "yesno-2": "false",
            "evidence-0": "Yes, I did.",
            "evidence-1": ""
            "evidence-2": "to be removed"
        }

        # OUT
        {
            "dynamicListKey":
            [{
                "yesno": True,
                "evidence": "Yes, I did."
            },
            {
                "yesno": False
            },
            {
                "yesno": False
            }]
        }
        """

        q_data = {}
        for question in self.questions:
            q_data.update(question.get_data(form_data))

        if not q_data:
            return {self.id: []}

        if self._context is None:
            raise ValueError("DynamicList question requires correct .filter context to parse form data")

        q_data = drop_followups(self, q_data, nested=True)

        answers = sorted([(int(k.split('-')[1]), k.split('-')[0], v) for k, v in q_data.items()])

        questions_data = [{} for i in range(len(self.get_dynamic_questions(self._context)))]
        for index, question, value in answers:
            if value is not None:
                questions_data[index][question] = value

        return {self.id: questions_data}

    def unformat_data(self, data):
        """ Unpack service data to be used in a form

        :param data: the service data as returned from the data API
        :type data: dict
        :return: service data with unpacked dynamic list question

        # IN
        {
            "dynamicListKey": [
                {
                    "yesno": True,
                    "evidence": "Yes, I did."
                },
                {
                    "yesno": False
                }
            ],
            "nonDynamicListKey": 'other data'
        }

        # OUT
        {
            "yesno-0": True,
            "yesno-1": False,
            "evidence-0": "Yes, I did."
        }
        """
        result = {}
        dynamic_list_data = data.get(self.id, None)
        if not dynamic_list_data:
            return result
        for question in self.questions:
            # For each question e.g. evidence-0, find if data exists for it and insert it into our result
            root, index = question.id.split('-')
            question_data = dynamic_list_data[int(index)]
            if root in question_data:
                result.update({question.id: question_data.get(root)})

        return result

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        if self.id not in errors:
            return OrderedDict()

        # Assumes errors being passed in are ordered by 'index' key e.g.
        # {'example': [
        #     {'index': 0, 'error': 'answer_required'}
        #     {'index': 1, 'error': 'answer_required'}
        # ]}
        question_errors = OrderedDict()
        for error in errors[self.id]:
            if 'field' in error:
                input_name = f"{error['field']}-{error['index']}"
            else:
                input_name = self.id

            question = self.get_question(input_name)
            question_errors[input_name] = {
                'input_name': input_name,
                'question': getattr(question, question_descriptor_from),
                'message': question.get_error_message(error['error']),
            }

        return question_errors

    @property
    def form_fields(self):
        return [self.id]

    def summary(self, service_data, inplace_allowed: bool = False) -> "DynamicListSummary":
        return DynamicListSummary(self, service_data)

    def _make_dynamic_question(self, question, item, index):
        question = question.filter({'item': item})
        question._data['id'] = f'{question.id}-{index}'

        followups = {}
        for followup, values in question.get('followup', {}).items():
            followups[f'{followup}-{index}'] = values

        question._data['followup'] = followups

        return question


class ListMultiquestion(Multiquestion):
    _multi_questions_made = False

    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        self.number_of_items = data['number_of_items']
        self.item_question = data['item_question']
        self.column_width = data.get('column_width')

    def summary(self, service_data, inplace_allowed: bool = False):
        return ListMultiquestionSummary(self, service_data)

    def filter(
        self: TListMultiquestion,
        context,
        dynamic=True,
        inplace_allowed: bool = False,
        ignore_depends_on_follow_up: bool = False
    ) -> Optional[TListMultiquestion]:
        if not dynamic:
            return super().filter(
                context,
                dynamic=dynamic,
                inplace_allowed=inplace_allowed,
                ignore_depends_on_follow_up=ignore_depends_on_follow_up
            )

        list_multiquestion = super().filter(
            context,
            dynamic=dynamic,
            inplace_allowed=inplace_allowed,
            ignore_depends_on_follow_up=ignore_depends_on_follow_up
        )
        if not list_multiquestion:
            return None

        list_multiquestion.questions = list(filter(None, [
            self._make_multi_question(list_multiquestion.questions, index).filter(
                context,
                dynamic,
                inplace_allowed=inplace_allowed,
                ignore_depends_on_follow_up=ignore_depends_on_follow_up
            )
            for index in range(self.number_of_items)
        ]))
        list_multiquestion._multi_questions_made = True

        return list_multiquestion

    def get_data(self, form_data):
        q_data = {}

        for question in self.questions:
            q_data.update(question.get_data(form_data))

        q_data = drop_followups(self, q_data)
        q_data = drop_dependent_follow_ups(self, q_data)

        questions_data = [{} for _ in range(self.number_of_items)]

        for key, string_index, value in sorted(k.split('-') + [v] for k, v in q_data.items()):
            index = int(string_index)

            questions_data[index][key] = value

        last_present_row = 0

        for index, row in enumerate(questions_data):
            if any(bool(value) or value is False for value in row.values()):
                last_present_row = index + 1

        return {self.id: questions_data[0:last_present_row]}

    def unformat_data(self, data):
        result = {}

        items = data.get(self.id) or []

        for index, item in enumerate(items):
            for key, value in item.items():
                result[f"{key}-{index}"] = value

        return result

    @property
    def form_fields(self):
        return [self.id]

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        if self.id not in errors:
            return OrderedDict()

        question_errors = OrderedDict()

        errors = errors[self.id]

        if isinstance(errors, str):
            question_errors[self.id] = {
                'input_name': self.id,
                'question': getattr(self, question_descriptor_from),
                'message': self.get_error_message(errors),
            }
        else:
            for error in errors:
                if 'field' in error:
                    input_name = f"{error['field']}-{error['index']}"
                else:
                    input_name = self.id

                question = self.get_question(input_name)
                question_errors[input_name] = {
                    'input_name': input_name,
                    'question': getattr(question, question_descriptor_from),
                    'message': question.get_error_message(error['error']),
                }

        return question_errors

    def _make_multi_question(self, questions, index):
        if isinstance(self._data["item_question"], TemplateField):
            question_and_name = TemplateField(
                self._data["item_question"].source.format(index=index + 1),
                self._data["item_question"].markdown
            )
        else:
            question_and_name = self._data["item_question"].format(index=index + 1)

        return Multiquestion(
            self._data | {
                "index": index,
                "id": f'{self.id}-{index}',
                "type": "multiquestion",
                "question": question_and_name,
                "name": question_and_name,
                "questions": [
                    question._data | {"id": f"{question.id}-{index}"}
                    for question in questions
                ]
            }
        )

    def get_question_ids_for_item(self, item_number):
        return self.questions[item_number].get_question_ids()


class Formula(Multiquestion):
    def summary(self, service_data, inplace_allowed: bool = False):
        return FormulaSummary(self, service_data)


class Pricing(Question):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.fields = data['fields']

        # True if we are restricting to an integer or a 2dp value (representing pounds and optionally pence)
        self.decimal_place_restriction = data.get('decimal_place_restriction', False)

    def summary(self, service_data, inplace_allowed: bool = False) -> "PricingSummary":
        return PricingSummary(self, service_data)

    def get_question(self, field_name):
        if self.id == field_name or field_name in self.fields.values():
            return self

    def unformat_data(self, data):
        """Get values from api data whose keys are in self.fields; this indicates they are related to this question."""
        return {key: data[key] for key in data if key in self.fields.values()}

    def get_data(self, form_data):
        """
        Return a subset of form_data containing only those key: value pairs whose key appears in the self.fields of
        this question (therefore only those pairs relevant to this question).
        Filter 0/ False values here and replace with None as they are handled with the optional flag.
        """
        question_data = {key: form_data[key] or None for key in self.fields.values() if key in form_data}

        if self.decimal_place_restriction:
            # Permissive validation to transform incomplete pennies to 2dp
            pattern_0dp = re.compile(r"\d+(\.)$")  # integer followed by '.' but no decimal values
            pattern_1dp = re.compile(r"\d+(\.)(?:\d)$")  # integer with 1 decimal place
            for key, value in question_data.items():
                if value:
                    if pattern_0dp.search(value):
                        question_data[key] = value + "00"

                    if pattern_1dp.search(value):
                        question_data[key] = value + "0"

        return question_data

    @property
    def form_fields(self):
        return sorted(self.fields.values())

    @property
    def _optional_form_fields(self):
        if self.get('optional'):
            return self.form_fields
        if self.get('optional_fields'):
            return [self.fields[key] for key in self['optional_fields']]

        return []


class List(Question):
    def _get_data(self, form_data):
        if self.id not in form_data:
            return {self.id: None}

        value = form_data.getlist(self.id)

        return {self.id: value or None}

    def summary(self, service_data, inplace_allowed: bool = False) -> 'QuestionSummary':
        return ListSummary(self, service_data)


class Hierarchy(List):
    """
    For our purposes, a Hierarchy is like a List, except the entries
    are potentially related to each other in a "subsumptive
    containment hierarchy". We don't store the parent categories
    (that denormalization will have to be added for the search engine),
    so the only real difference is that we gracefully handle
    the same value being submitted several times. This can happen
    because some leaf nodes (e.g. subcategories) can appear in multiple
    places in the tree (i.e. in multiple categories).
    """

    def _get_data(self, form_data):
        if self.id not in form_data:
            return {self.id: None}

        values = set(form_data.getlist(self.id))

        return {self.id: sorted(values) or None}

    def summary(self, service_data, inplace_allowed: bool = False) -> 'QuestionSummary':
        return HierarchySummary(self, service_data)

    def get_missing_values(self, selected_values_set):
        """
        Recursively retrieves un-selected parent categories of the
        passed-in selection, as a set of 'value' strings.
        :param selected_values_set: initially-selected categories (e.g. by the user)
        :return: additional values that should also be considered as selected
        """

        def update_expected_values(options, parents, expected_set):
            for option in options:
                if is_option_divider(option):
                    continue
                value = get_option_value(option)
                if value in selected_values_set:
                    expected_set.update(parents)
                children = option.get('options')
                if children:
                    update_expected_values(children, parents + [value], expected_set)

        expected_values = set()
        update_expected_values(self._data.get('options', []), list(), expected_values)

        return expected_values - selected_values_set


class Date(Question):
    """Class used as an interface for date data between forms, backend and summary pages."""

    FIELDS = ('year', 'month', 'day')

    def summary(self, service_data, inplace_allowed: bool = False) -> "DateSummary":
        return DateSummary(self, service_data)

    @staticmethod
    def process_value(value):
        """If there are any hyphens in the value then it does not validate."""
        value = value.strip() if value else ''
        if not value or '-' in value:
            return ''
        return value

    def get_data(self, form_data):
        r"""Retreive the fields from the POST data (form_data).

        The d, m, y should be in the post as 'questionName-day', questionName-month ...
        Extract them and format as '\d\d\d\d-\d{1,2}-\d{1,2}'.
        https://code.tutsplus.com/tutorials/validating-data-with-json-schema-part-1--cms-25343
        """
        parts = []
        for key in self.FIELDS:
            identifier = '-'.join([self.id, key])
            value = form_data.get(identifier, '')
            parts.append(self.process_value(value))

        return {self.id: '-'.join(parts) if any(parts) else None}

    def unformat_data(self, data):
        result = {}
        value = data.get(self.id, None)
        if value:
            for partial_value, field in zip(value.split('-'), self.FIELDS):
                result['-'.join([self.id, field])] = partial_value
        return result


class Money(Question):
    def summary(self, service_data, inplace_allowed: bool = False) -> 'QuestionSummary':
        return MoneySummary(self, service_data)

    def unformat_data(self, data):
        value = data.get(self.id, None)

        if isinstance(value, int):
            value = f'{(Decimal(value) / 100):.2f}'

        return {self.id: value}


class Display(Question):
    def summary(self, service_data, inplace_allowed: bool = False) -> 'QuestionSummary':
        return DisplaySummary(self, service_data)

    @property
    def required_form_fields(self):
        return []

    @property
    def _optional_form_fields(self):
        return [self.id]


class QuestionSummary(Question):
    def __init__(self, question, service_data):
        self.number = question.number
        self._data = question._data
        self._service_data = service_data
        self._context = question._context

        if question.get('boolean_list_questions'):
            self.boolean_list_questions = question.boolean_list_questions

    def _default_for_field(self, field_key):
        return self.get('field_defaults', {}).get(field_key)

    def get_error_messages(self, errors: dict, question_descriptor_from: str = "label") -> OrderedDict:
        question_errors = super().get_error_messages(
            errors,
            question_descriptor_from=question_descriptor_from,
        )

        boolean_list_questions = self.get('boolean_list_questions')
        boolean_list_values = self.get('value') or []

        if self.id in question_errors and self.type == 'boolean_list' and boolean_list_questions:
            # pad list of values to same length as boolean_list_questions
            boolean_list_values.extend([None] * (len(boolean_list_questions) - len(boolean_list_values)))

            for index, boolean_list_question in enumerate(boolean_list_questions):
                if not isinstance(boolean_list_values[index], bool):
                    # Each non-boolean value is an error
                    boolean_question_id = f"{self.id}-{index}"
                    question_errors[boolean_question_id] = {
                        'input_name': boolean_question_id,
                        'message': question_errors[self.id]['message'],
                        'question': boolean_list_question
                    }

            question_errors[self.id] = True
            question_errors = OrderedDict([
                (k, question_errors[k]) for k in sorted(question_errors.keys())
            ])

        return question_errors

    @property
    def is_empty(self):
        return self.value in ('', [], None,)

    @property
    def value(self):
        # Look up display values for options that have different labels from values
        options = self.get('options')
        if self.has_assurance():
            value = self._service_data.get(self.id, {}).get('value', '')
        else:
            value = self._service_data.get(self.id, '')
        if value != '' and self.type == "number" and self.get('unit'):
            if self.unit_position == "after":
                value = f"{value}{self.unit}"
            else:
                return f"{self.unit}{value}"
        if options and value:
            for option in options:
                if 'label' in option and 'value' in option and option['value'] == value:
                    return option['label']

        return value

    @property
    def filter_value(self):
        # For options where we want to show different text on the service page than when the question was asked
        options = self.get('options')
        value = self._service_data.get(self.id, '')
        if options and value:
            for opt in options:
                if 'filter_label' in opt and 'value' in opt and any(value == opt.get(i) for i in ['value', 'label']):
                    return opt['filter_label']
        return self.value

    @property
    def assurance(self):
        if self.has_assurance():
            return self._service_data.get(self.id, {}).get('assurance', '')
        return ''

    @property
    def answer_required(self):
        if self.get('optional'):
            return False

        return self.is_empty


class DateSummary(QuestionSummary):
    def __init__(self, question, service_data):
        super().__init__(question, service_data)
        self._value = self._service_data.get(self.id, '')

    @property
    def value(self):
        try:
            return datetime.strptime(self._value, DATE_FORMAT).strftime(DISPLAY_DATE_FORMAT)
        except ValueError:
            # We may need to fall back to displaying a plain string value in the case of briefs in draft before
            # the date field was introduced.
            return self._value


class MoneySummary(QuestionSummary):
    @property
    def value(self):
        value = self._service_data.get(self.id, '')

        if value != '':
            return f'{self.unit}{(Decimal(value) / 100):,.2f}'

        return value


class DisplaySummary(QuestionSummary):
    def __init__(self, question, service_data):
        super().__init__(question, service_data)
        self._value = self._data.get('value')

    @property
    def value(self):
        if self._value is None:
            return super().value

        return self._value

    @property
    def answer_required(self):
        return False


class MultiquestionSummary(QuestionSummary, Multiquestion):
    def __init__(self, question, service_data):
        super().__init__(question, service_data)
        self.questions = [q.summary(service_data) for q in question.questions]

    @property
    def value(self):
        return [question for question in self.questions if not question.is_empty]

    @property
    def answer_required(self):
        """
            Checks all sub-questions and returns true if any questions which are required, still require answers.
            Appropriately checks/ignores followup questions based on current answers.

            NOTE this is a "hot path" so be careful making changes to it.
        """
        if self.get('optional'):
            return False

        lookup_question_by_id = {q.id: q for q in self.questions}
        ignorable_ids = set()

        # note iteration order is important here: followups coming "before" their referring question will cause trouble
        for question in self.questions:
            if not question.get('followup'):
                continue

            if question.id not in ignorable_ids:
                if question.answer_required:
                    return True
                else:
                    # ignorable because it's not `.answer_required`
                    ignorable_ids.add(question.id)

            question_value = question.value
            answers_provided_set = frozenset(question_value if isinstance(question_value, list) else (question_value,))

            for followup_id, answers_triggering_followup in question.get('followup', {}).items():
                if answers_provided_set.intersection(answers_triggering_followup) and \
                        lookup_question_by_id[followup_id].answer_required:
                    return True

                # ignorable because it's listed as a followup to a question that hasn't been triggered or is not
                # `.answer_required`
                ignorable_ids.add(followup_id)

        return any(q.answer_required for q in self.questions if q.id not in ignorable_ids)


class DynamicListSummary(MultiquestionSummary, DynamicList):
    pass


class FormulaSummary(MultiquestionSummary, Formula):
    @property
    def value(self):
        all_empty = True
        values = []

        for question in self.questions:
            # print(question.type)
            # print(question.value)
            if question.type != 'display' and not question.is_empty:
                all_empty = False

            values.append(question)

        if all_empty:
            return []

        return values


class ListMultiquestionSummary(QuestionSummary, ListMultiquestion):
    def __init__(self, question, service_data):
        super().__init__(question, service_data)
        unformated_data = self.unformat_data(service_data)
        if question._multi_questions_made:
            self.questions = [q.summary(unformated_data) for q in question.questions]
        else:
            self.questions = [
                self._make_multi_question(question.questions, index).summary(unformated_data)
                for index in range(self.number_of_items)
            ]

    @property
    def value(self):
        return [
            multiquestion
            for multiquestion in self.questions
            if not all(question.is_empty for question in multiquestion.questions)
        ]


class PricingSummary(QuestionSummary, Pricing):
    def __init__(self, question, service_data):
        super().__init__(question, service_data)
        self.fields = question.fields

    @property
    def value(self):
        price = self._service_data.get(self.fields.get('price'))
        minimum_price = self._service_data.get(self.fields.get('minimum_price'))
        maximum_price = self._service_data.get(self.fields.get('maximum_price'))
        price_unit = self._service_data.get(self.fields.get('price_unit'),
                                            self._default_for_field('price_unit'))
        price_interval = self._service_data.get(self.fields.get('price_interval'),
                                                self._default_for_field('price_interval'))
        hours_for_price = self._service_data.get(self.fields.get('hours_for_price'),
                                                 self._default_for_field('hours_for_price'))

        if price or minimum_price or maximum_price:
            return format_price(price or minimum_price, maximum_price, price_unit, price_interval, hours_for_price)
        else:
            return ''


class ListSummary(QuestionSummary, List):
    @property
    def value(self):
        if self.has_assurance():
            value = self._service_data.get(self.id, {}).get('value', '')
        else:
            value = self._service_data.get(self.id, '')

        # Look up display values for options that have different labels from values
        options = self.get('options')
        if options and value:
            value = list(value)  # Make a copy of the list to avoid mutating the underlying list data
            for i, v in enumerate(value):
                for option in options:
                    if 'label' in option and 'value' in option and v == option['value']:
                        value[i] = option['label']
                        break

        if self.get('before_summary_value'):
            value = self.before_summary_value + (value or [])

        return value

    @property
    def filter_value(self):
        # Display values for options where we want to show different text ('filter_label') than the usual 'label'
        options = self.get('options')
        value = self._service_data.get(self.id, '')
        if options and value:
            new_list = list()
            for v in value:
                for opt in options:
                    if (opt.get('value') or opt.get('label')) == v:
                        new_list.append(opt.get('filter_label') or opt.get('label') or v)
            value = new_list

        if self.get('before_summary_value'):
            value = self.before_summary_value + (value or [])

        return value


class HierarchySummary(QuestionSummary):
    def __init__(self, question, service_data):
        self._hierarchy_question = question
        QuestionSummary.__init__(self, question, service_data)

    @property
    def value(self):
        selection = set(self._service_data.get(self.id, []))
        parent_values_not_persisted = self._hierarchy_question.get_missing_values(selection)

        def _get_options_recursive(options):
            """
            Filter the supplied options (and their child options) by the current selection
            as stored in service_data. Parent options - that we didn't store but can
            be considered 'selected' because one of their children have been selected -
            are also included.
            :return: filtered options
            """
            filtered_options = []
            for option in options:
                value = option.get('value', option.get('label'))
                # note: test below causes confusion if a non-selected child option has
                # the same name as a parent option - that child will _appear_ selected
                # if any of its siblings are selected.  Could refactor this
                # if we wanted to have (e.g.) sub-cats named that way - right now
                # we don't, and it's hard to see that making much sense. We've
                # found more clear ways of expressing those kinds of special 'other'
                # or 'general' sub-cats than naming them identically to their parents,
                # anyway.
                if value in selection or value in parent_values_not_persisted:
                    option = option.copy()
                    filtered_options.append(option)
                    option['options'] = _get_options_recursive(option.get('options', []))
            return filtered_options

        return _get_options_recursive(self._data.get('options', []))


QUESTION_TYPES = {
    'dynamic_list': DynamicList,
    'multiquestion': Multiquestion,
    'list_multiquestion': ListMultiquestion,
    'formula': Formula,
    'pricing': Pricing,
    'list': List,
    'checkboxes': List,
    'checkbox_tree': Hierarchy,
    'checkbox_tree_large': Hierarchy,
    'date': Date,
    'money': Money,
    'display': Display
}


class ContentQuestion(Question):
    def __new__(cls, data, *args, **kwargs):
        if data.get('type') in QUESTION_TYPES:
            return QUESTION_TYPES[data['type']](data, *args, **kwargs)

        return Question(data, *args, **kwargs)
