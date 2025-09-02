from peewee import Model, CharField, DateTimeField, IntegerField, SQL


class BaseModel(Model):
    class Meta:
        database = None


class Order(BaseModel):
    id = IntegerField(primary_key=True)
    account_id = CharField()
    order_id = CharField()
    item_id = CharField()
    item_name = CharField()
    charge_item_uuid = CharField()
    created = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'usage_associations'
