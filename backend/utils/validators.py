"""Input validation helpers using marshmallow."""
import re
from marshmallow import Schema, fields, validate, ValidationError


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class RegisterSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))
    phone = fields.String(required=False, allow_none=True,
                          validate=validate.Length(max=20))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class ProductSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    description = fields.String(required=False, allow_none=True)
    price = fields.Decimal(required=True, as_string=True)
    category = fields.String(required=True, validate=validate.Length(min=1, max=80))
    material = fields.String(required=False, allow_none=True,
                             validate=validate.Length(max=80))
    stock = fields.Integer(required=False, missing=0,
                           validate=validate.Range(min=0))
    image_url = fields.String(required=False, allow_none=True)


class CartItemSchema(Schema):
    product_id = fields.Integer(required=True, validate=validate.Range(min=1))
    quantity = fields.Integer(required=True, validate=validate.Range(min=1, max=100))


class CheckoutSchema(Schema):
    address = fields.String(required=True, validate=validate.Length(min=5, max=500))
    phone = fields.String(required=True, validate=validate.Length(min=5, max=20))
    payment_method = fields.String(required=True,
                                   validate=validate.OneOf(["cod", "card", "upi"]))


class ReviewSchema(Schema):
    product_id = fields.Integer(required=True)
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(required=False, allow_none=True,
                            validate=validate.Length(max=1000))


class ExpenseSchema(Schema):
    expense_type = fields.String(required=True, validate=validate.Length(min=1, max=80))
    amount = fields.Decimal(required=True, as_string=True)
    expense_date = fields.Date(required=True)
    note = fields.String(required=False, allow_none=True,
                         validate=validate.Length(max=500))


def validate_payload(schema_cls, payload):
    schema = schema_cls()
    try:
        return schema.load(payload), None
    except ValidationError as err:
        return None, err.messages
