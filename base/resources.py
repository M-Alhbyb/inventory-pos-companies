"""Django Import/Export resources for data import and export."""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Transaction, TransactionItem, User, Product


# Arabic translation mappings for transaction types
TRANSACTION_TYPE_TO_ARABIC = {
    'take': 'سحب',
    'payment': 'دفع',
    'restore': 'إرجاع',
}

TRANSACTION_TYPE_FROM_ARABIC = {v: k for k, v in TRANSACTION_TYPE_TO_ARABIC.items()}


class TransactionResource(resources.ModelResource):
    """Resource for importing/exporting Transaction data."""
    
    user = fields.Field(
        column_name='المستخدم',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )
    
    type = fields.Field(
        column_name='نوع المعاملة',
        attribute='type'
    )
    
    amount = fields.Field(
        column_name='المجموع',
        attribute='amount'
    )
    
    date = fields.Field(
        column_name='التاريخ',
        attribute='date'
    )
    
    class Meta:
        model = Transaction
        fields = ('id', 'user', 'type', 'amount', 'date')
        export_order = ('id', 'user', 'type', 'date', 'amount')
        import_id_fields = ['id']
        skip_unchanged = True
        report_skipped = False
    
    def dehydrate_type(self, transaction):
        """Convert type to Arabic for export."""
        return TRANSACTION_TYPE_TO_ARABIC.get(transaction.type, transaction.type)
    
    def before_import_row(self, row, **kwargs):
        """Convert Arabic type back to English before import."""
        if 'نوع المعاملة' in row:
            row['نوع المعاملة'] = TRANSACTION_TYPE_FROM_ARABIC.get(
                row['نوع المعاملة'], 
                row['نوع المعاملة']
            )
    
    def get_export_headers(self, selected_fields=None):
        """Return Arabic headers for export."""
        return ['رقم المعاملة', 'المستخدم', 'نوع المعاملة', 'التاريخ', 'المجموع']
    
    def export(self, queryset=None, *args, **kwargs):
        """Custom export with items column."""
        dataset = super().export(queryset, *args, **kwargs)
        
        # Add items column
        items_column = []
        if queryset:
            for transaction in queryset:
                items = transaction.items.all()
                items_str = ", ".join([
                    f"{item.product.name} (x{item.quantity})" 
                    for item in items if item.product
                ])
                items_column.append(items_str or '-')
        
        # Insert items column before amount
        dataset.insert_col(4, items_column, header='العناصر')
        
        return dataset


class TransactionItemResource(resources.ModelResource):
    """Resource for importing/exporting TransactionItem data."""
    
    transaction_id = fields.Field(
        column_name='رقم المعاملة',
        attribute='transaction',
        widget=ForeignKeyWidget(Transaction, 'id')
    )
    
    product = fields.Field(
        column_name='المنتج',
        attribute='product',
        widget=ForeignKeyWidget(Product, 'name')
    )
    
    quantity = fields.Field(
        column_name='الكمية',
        attribute='quantity'
    )
    
    price = fields.Field(
        column_name='السعر',
        attribute='price'
    )
    
    class Meta:
        model = TransactionItem
        fields = ('id', 'transaction_id', 'product', 'quantity', 'price')
        import_id_fields = ['id']
        skip_unchanged = True
