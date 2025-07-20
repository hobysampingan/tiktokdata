import pandas as pd
from datetime import datetime

class DataManager:
    def process_data(self, pesanan_data, income_data, cost_data):
        """Memproses dan menggabungkan data"""
        # Filter pesanan selesai
        df1 = pesanan_data[pesanan_data['Order Status'] == 'Selesai']
        
        # Hapus duplikat dari data pendapatan
        df2 = income_data.drop_duplicates(subset=['Order/adjustment ID'])
        
        # Gabungkan data
        merged = pd.merge(df1, df2, left_on='Order ID', right_on='Order/adjustment ID', how='inner')
        
        if merged.empty:
            return None, None
        
        # Buat ringkasan
        summary = merged.groupby(['Seller SKU', 'Product Name', 'Variation'], as_index=False).agg(
            TotalQty=('Quantity', 'sum'),
            Revenue=('Total settlement amount', 'sum')
        )
        
        # Tambahkan perhitungan biaya
        summary['Cost per Unit'] = summary['Product Name'].apply(
            lambda x: self.get_product_cost(x, cost_data)
        )
        summary['Total Cost'] = summary['TotalQty'] * summary['Cost per Unit']
        summary['Profit'] = summary['Revenue'] - summary['Total Cost']
        summary['Profit Margin %'] = (summary['Profit'] / summary['Revenue'] * 100).round(2)
        summary['Share 60%'] = summary['Profit'] * 0.6
        summary['Share 40%'] = summary['Profit'] * 0.4
        
        return merged, summary
    
    def get_product_cost(self, product_name, cost_data):
        """Mendapatkan biaya produk dari data biaya"""
        return float(cost_data.get(product_name, 0.0))