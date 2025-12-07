"""Celery tasks for background processing."""

import pandas as pd
from celery import shared_task

from base.models import TransactionItem, Product


def forecast_stock(product_id, days=30):
    """
    Forecast stock using Prophet time series prediction.
    
    Args:
        product_id: ID of the product to forecast
        days: Number of days to forecast ahead
        
    Returns:
        DataFrame with forecast data or None if insufficient data
    """
    # Need at least 2 data points for Prophet
    if TransactionItem.objects.filter(product_id=product_id).count() < 2:
        return None
    
    # Import Prophet here to avoid loading it unnecessarily
    from prophet import Prophet
    
    # Load transaction data
    qs = TransactionItem.objects.filter(product_id=product_id).order_by("transaction__date")
    df = pd.DataFrame(list(qs.values("transaction__date", "quantity")))
    df.rename(columns={"transaction__date": "ds", "quantity": "y"}, inplace=True)
    
    # Remove timezone as Prophet requires timezone-naive datetimes
    if not df.empty:
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
    
    # Create and fit model
    model = Prophet()
    model.fit(df)
    
    # Generate forecast
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)
    
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def estimate_stock_out(product_id=-1, forecast_df=None):
    """
    Estimate when products will run out of stock.
    
    Args:
        product_id: Specific product ID or -1 for all products
        forecast_df: Pre-computed forecast DataFrame
    """
    if product_id != -1 and forecast_df is not None:
        return None
    
    products = Product.objects.all()
    
    for product in products:
        # Skip products with insufficient transaction data
        if TransactionItem.objects.filter(product_id=product.id).count() < 2:
            continue
        
        forecast_df = forecast_stock(product.id)
        if forecast_df is None:
            continue
        
        # Calculate cumulative demand and find stock-out date
        total = 0
        for _, row in forecast_df.iterrows():
            total += max(row['yhat'], 0)
            
            if total >= product.stock:
                product.estimated_stock_out = row['ds']
                product.save()
                break


@shared_task
def estimate_stock_out_task():
    """Celery task to run stock estimation."""
    estimate_stock_out()
    return {'status': 'done', 'result': 'Process completed successfully!'}