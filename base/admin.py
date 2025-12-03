from django.contrib import admin
from .models import(
          User,
          Product,
          Category,
          Transaction,
          TransactionItem)
# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(TransactionItem)
