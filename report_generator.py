import io
import pandas as pd
import xlsxwriter

class ReportGenerator:
    def create_excel_report(self, merged_data, summary_data, cost_data):
        """Membuat laporan Excel"""
        output = io.BytesIO()
        
        # Hitung total
        unique_orders = merged_data.drop_duplicates(subset=['Order ID'])
        total_orders = unique_orders['Order ID'].nunique()
        total_revenue = unique_orders['Total settlement amount'].sum()
        total_qty = merged_data['Quantity'].sum()
        
        # Ringkasan berdasarkan SKU
        summary_by_sku = (
            merged_data.groupby('Seller SKU', as_index=False)
            .agg({
                'Quantity': 'sum',
                'Order ID': 'nunique',
                'Total settlement amount': 'sum'
            })
            .rename(columns={
                'Quantity': 'Total Quantity',
                'Order ID': 'Total Orders',
                'Total settlement amount': 'Total Revenue'
            })
        )
        
        # Dapatkan nama produk pertama untuk setiap SKU
        sku_products = merged_data.groupby('Seller SKU')['Product Name'].first().to_dict()
        summary_by_sku['Cost per Unit'] = summary_by_sku['Seller SKU'].map(
            lambda sku: self.get_product_cost(sku_products.get(sku, ''), cost_data)
        )
        summary_by_sku['Total Cost'] = summary_by_sku['Total Quantity'] * summary_by_sku['Cost per Unit']
        summary_by_sku['Profit'] = summary_by_sku['Total Revenue'] - summary_by_sku['Total Cost']
        summary_by_sku['Profit Margin %'] = (summary_by_sku['Profit'] / summary_by_sku['Total Revenue'] * 100).round(2)
        summary_by_sku['Share 60%'] = summary_by_sku['Profit'] * 0.6
        summary_by_sku['Share 40%'] = summary_by_sku['Profit'] * 0.4
        
        # Hitung total biaya dan profit
        total_cost = summary_by_sku['Total Cost'].sum()
        total_profit = total_revenue - total_cost
        total_share_60 = total_profit * 0.6
        total_share_40 = total_profit * 0.4
        
        # Analisis penjualan harian
        date_column = None
        possible_date_columns = [
            'Order created time(UTC)', 'Order creation time', 'Order Creation Time', 
            'Creation Time', 'Date', 'Order Date', 'Order created time', 'Created time'
        ]
        
        for col in possible_date_columns:
            if col in merged_data.columns:
                date_column = col
                break
        
        if date_column:
            try:
                merged_data_copy = merged_data.copy()
                merged_data_copy['Order Date'] = pd.to_datetime(merged_data_copy[date_column]).dt.date
                daily_sales = (
                    merged_data_copy.groupby('Order Date', as_index=False)
                    .agg({
                        'Quantity': 'sum',
                        'Order ID': 'nunique',
                        'Total settlement amount': 'sum'
                    })
                    .rename(columns={
                        'Quantity': 'Daily Quantity',
                        'Order ID': 'Daily Orders',
                        'Total settlement amount': 'Daily Revenue'
                    })
                )
            except:
                daily_sales = pd.DataFrame({
                    'Order Date': ['Data tidak tersedia'],
                    'Daily Quantity': [0],
                    'Daily Orders': [0],
                    'Daily Revenue': [0]
                })
        else:
            daily_sales = pd.DataFrame({
                'Order Date': ['Kolom tanggal tidak ditemukan'],
                'Daily Quantity': [0],
                'Daily Orders': [0],
                'Daily Revenue': [0]
            })
        
        # Produk terbaik berdasarkan profit
        top_products = summary_data.nlargest(10, 'Profit')
        
        # Buat penulis Excel
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Tentukan format
            title_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'align': 'center',
                'bg_color': '#4472C4', 'font_color': 'white'
            })
            
            header_format = workbook.add_format({
                'bold': True, 'font_size': 12,
                'bg_color': '#D9E2F3', 'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '#,##0', 'border': 1
            })
            
            number_format = workbook.add_format({
                'num_format': '#,##0', 'border': 1
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%', 'border': 1
            })
            
            # Lembar ringkasan
            overview_sheet = workbook.add_worksheet('Ringkasan')
            overview_sheet.set_column('A:B', 25)
            overview_sheet.set_column('C:C', 20)
            
            row = 0
            overview_sheet.merge_range(f'A{row+1}:C{row+1}', 'LAPORAN PENJUALAN & ANALISIS PROFIT', title_format)
            row += 2
            
            # Rentang tanggal
            if date_column and date_column in merged_data.columns:
                try:
                    date_range_start = pd.to_datetime(merged_data[date_column]).min()
                    date_range_end = pd.to_datetime(merged_data[date_column]).max()
                except:
                    date_range_start = datetime.now()
                    date_range_end = datetime.now()
            else:
                date_range_start = datetime.now()
                date_range_end = datetime.now()
            
            overview_sheet.write(row, 0, f'Periode:', header_format)
            overview_sheet.write(row, 1, f'{date_range_start.strftime("%d/%m/%Y")} - {date_range_end.strftime("%d/%m/%Y")}')
            row += 1
            
            overview_sheet.write(row, 0, f'Dibuat:', header_format)
            overview_sheet.write(row, 1, f'{datetime.now().strftime("%d %B %Y %H:%M")}')
            row += 3
            
            # Metrik kunci
            overview_sheet.write(row, 0, 'RINGKASAN PENJUALAN & PROFIT', header_format)
            row += 1
            overview_sheet.write(row, 0, 'Total Pesanan:')
            overview_sheet.write(row, 1, total_orders, number_format)
            row += 1
            overview_sheet.write(row, 0, 'Total Kuantitas:')
            overview_sheet.write(row, 1, total_qty, number_format)
            row += 1
            overview_sheet.write(row, 0, 'Total Pendapatan:')
            overview_sheet.write(row, 1, total_revenue, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Total Biaya:')
            overview_sheet.write(row, 1, total_cost, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Total Profit:')
            overview_sheet.write(row, 1, total_profit, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Bagian 60%:')
            overview_sheet.write(row, 1, total_share_60, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Bagian 40%:')
            overview_sheet.write(row, 1, total_share_40, currency_format)
            row += 2
            
            # Hitung metrik tambahan
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            avg_profit_per_order = total_profit / total_orders if total_orders > 0 else 0
            overall_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            overview_sheet.write(row, 0, 'Nilai Rata-rata Pesanan:')
            overview_sheet.write(row, 1, avg_order_value, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Rata-rata Profit per Pesanan:')
            overview_sheet.write(row, 1, avg_profit_per_order, currency_format)
            row += 1
            overview_sheet.write(row, 0, 'Margin Profit Keseluruhan:')
            overview_sheet.write(row, 1, overall_profit_margin / 100, percent_format)
            
            # Tulis lembar lainnya
            summary_data.to_excel(writer, index=False, sheet_name='Ringkasan per Produk')
            summary_by_sku.to_excel(writer, index=False, sheet_name='Ringkasan per SKU')
            daily_sales.to_excel(writer, index=False, sheet_name='Penjualan Harian')
            top_products.to_excel(writer, index=False, sheet_name='Produk Teratas')
            
            # Daftar biaya produk
            if cost_data:
                cost_df = pd.DataFrame(list(cost_data.items()), columns=["Product Name", "Cost per Unit"])
                cost_df = cost_df.sort_values(by="Product Name")
                cost_df.to_excel(writer, index=False, sheet_name='Daftar Biaya Produk')
        
        output.seek(0)
        return output