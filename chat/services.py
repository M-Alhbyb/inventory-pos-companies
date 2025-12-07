"""Gemini AI chat service with function calling."""

from google import genai
from google.genai import types
from django.conf import settings

from chat.tools import (
    # Basic data getters
    get_categories, 
    get_products, 
    get_users,
    get_merchants,
    get_representatives,
    get_transactions, 
    get_transaction_items, 
    get_transaction_types,
    # Statistics & Analytics
    get_inventory_stats,
    get_daily_transactions_summary,
    get_top_products_by_sales,
    get_top_merchants_by_debt,
    get_top_merchants_by_transactions,
    get_low_stock_alert,
    get_stock_predictions,
    get_products_by_category,
    get_monthly_revenue,
    get_monthly_payments,
    get_user_transactions,
    get_product_transactions,
    get_today_summary,
    search_products,
    search_users
)


GEMINI_MODEL = "gemini-2.5-flash"
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Define all available tools for function calling
available_tools = [
    # Basic data
    get_categories, 
    get_products, 
    get_users,
    get_merchants,
    get_representatives,
    get_transactions, 
    get_transaction_items, 
    get_transaction_types,
    # Statistics & Analytics
    get_inventory_stats,
    get_daily_transactions_summary,
    get_top_products_by_sales,
    get_top_merchants_by_debt,
    get_top_merchants_by_transactions,
    get_low_stock_alert,
    get_stock_predictions,
    get_products_by_category,
    get_monthly_revenue,
    get_monthly_payments,
    get_user_transactions,
    get_product_transactions,
    get_today_summary,
    search_products,
    search_users
]

# Tools that require parameters
TOOLS_WITH_PARAMS = {
    'get_user_transactions': {
        'user_id': types.Schema(type=types.Type.INTEGER, description='معرف المستخدم للحصول على معاملاته')
    },
    'get_product_transactions': {
        'product_id': types.Schema(type=types.Type.INTEGER, description='معرف المنتج للحصول على معاملاته')
    },
    'search_products': {
        'query': types.Schema(type=types.Type.STRING, description='نص البحث في المنتجات')
    },
    'search_users': {
        'query': types.Schema(type=types.Type.STRING, description='نص البحث في المستخدمين')
    }
}

SYSTEM_INSTRUCTIONS = """
أنت مساعد ذكي لنظام إدارة المخزون 'Inventory Pro'.
النظام يدير المنتجات، الفئات، التجار، المندوبين، والمعاملات المالية.

## البيانات الأساسية:
- get_categories: للحصول على قائمة الفئات مع عدد المنتجات
- get_products: للحصول على جميع المنتجات مع تفاصيلها (السعر، المخزون، الفئة، توقع النفاذ)
- get_users: للحصول على جميع المستخدمين (تجار ومندوبين)
- get_merchants: للحصول على التجار فقط مع ديونهم
- get_representatives: للحصول على المندوبين فقط
- get_transactions: للحصول على آخر 100 معاملة
- get_transaction_items: للحصول على تفاصيل عناصر المعاملات
- get_transaction_types: لمعرفة أنواع المعاملات (أخذ، دفع، إرجاع، منصرف)

## الإحصائيات والتحليلات:
- get_inventory_stats: إحصائيات شاملة (إجمالي المنتجات، الفئات، الديون، المخزون المنخفض، إلخ)
- get_daily_transactions_summary: ملخص المعاملات اليومية لآخر 30 يوم
- get_top_products_by_sales: أكثر المنتجات مبيعاً
- get_top_merchants_by_debt: التجار الأكثر ديوناً
- get_top_merchants_by_transactions: التجار الأكثر نشاطاً
- get_low_stock_alert: تنبيهات المخزون المنخفض
- get_stock_predictions: توقعات نفاذ المخزون
- get_products_by_category: المنتجات مصنفة حسب الفئة
- get_monthly_revenue: الإيرادات الشهرية
- get_monthly_payments: المدفوعات الشهرية
- get_today_summary: ملخص اليوم

## البحث والتصفية:
- search_products(query): البحث في المنتجات
- search_users(query): البحث في المستخدمين
- get_user_transactions(user_id): معاملات مستخدم محدد
- get_product_transactions(product_id): معاملات منتج محدد

## أنواع المعاملات:
- أخذ (take): عندما يأخذ التاجر/المندوب منتجات من المخزون
- دفع (payment): عندما يسدد التاجر جزء من ديونه
- إرجاع (restore): عندما يُرجع المندوب منتجات للمخزون
- منصرف (fees): مصاريف متنوعة

## إرشادات:
1. استخدم الأداة المناسبة للسؤال
2. يمكنك استخدام أكثر من أداة للإجابة على سؤال معقد
3. قدم تحليلات ونصائح مفيدة بناءً على البيانات
4. نبه على المشاكل مثل المخزون المنخفض أو الديون الكبيرة
5. أجب بشكل مختصر ومهني
6. استخدم اللغة العربية في جميع الردود
7. استخدم التنسيق المناسب (قوائم، جداول بسيطة) لعرض البيانات
"""


def generate_chat_response(prompt: str, history: list = None):
    """
    Generate a response from Gemini AI with function calling support.
    
    Args:
        prompt: The user's message
        history: List of previous messages in the conversation
        
    Returns:
        The AI response text
    """
    # Build conversation history
    contents = []
    
    if history:
        for message in history[:-1]:  # Exclude the last message (current prompt)
            role = message.get("role", "user")
            text = message.get("text", "")
            if text:
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    )
                )
    
    # Add the current user prompt
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    )
    
    # Build function declarations
    function_declarations = []
    for func in available_tools:
        func_name = func.__name__
        
        # Check if this tool requires parameters
        if func_name in TOOLS_WITH_PARAMS:
            properties = TOOLS_WITH_PARAMS[func_name]
            required = list(properties.keys())
        else:
            properties = {}
            required = []
        
        function_declarations.append(
            types.FunctionDeclaration(
                name=func_name,
                description=func.__doc__ or f"Function {func_name}",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties=properties,
                    required=required
                )
            )
        )
    
    tools = [types.Tool(function_declarations=function_declarations)]
    
    # Generate config
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        tools=tools,
    )
    
    # Generate response
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config
    )
    
    # Handle function calls if present
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                func_name = part.function_call.name
                func_args = dict(part.function_call.args) if part.function_call.args else {}
                
                # Find and execute the function
                func_map = {f.__name__: f for f in available_tools}
                if func_name in func_map:
                    # Call with or without arguments
                    if func_args:
                        func_result = func_map[func_name](**func_args)
                    else:
                        func_result = func_map[func_name]()
                    
                    # Send the function result back to get final response
                    contents.append(response.candidates[0].content)
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_function_response(
                                name=func_name,
                                response={"result": func_result}
                            )]
                        )
                    )
                    
                    # Get final response
                    final_response = client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=contents,
                        config=config
                    )
                    return final_response.text
    
    return response.text
