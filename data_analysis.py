# data_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataAnalysis:
    
    def show_data_details(self):
        st.markdown("### 📋 Detail Data")
        
        if st.session_state.summary_data is not None:
            # Tabel ringkasan dengan pencarian dan filter
            st.markdown("**📊 Tabel Ringkasan Lengkap**")
            
            # Filter
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                min_revenue = st.number_input("Pendapatan Minimum", min_value=0, value=0)
            with filter_col2:
                min_profit = st.number_input("Profit Minimum", value=0)
            with filter_col3:
                min_margin = st.number_input("Margin Minimum %", min_value=0.0, max_value=100.0, value=0.0)
            
            # Terapkan filter
            filtered_data = st.session_state.summary_data[
                (st.session_state.summary_data['Revenue'] >= min_revenue) &
                (st.session_state.summary_data['Profit'] >= min_profit) &
                (st.session_state.summary_data['Profit Margin %'] >= min_margin)
            ]
            
            # Format untuk tampilan
            display_data = filtered_data.copy()
            display_data['Revenue'] = display_data['Revenue'].apply(lambda x: f"Rp {x:,.0f}")
            display_data['Total Cost'] = display_data['Total Cost'].apply(lambda x: f"Rp {x:,.0f}")
            display_data['Profit'] = display_data['Profit'].apply(lambda x: f"Rp {x:,.0f}")
            display_data['Share 60%'] = display_data['Share 60%'].apply(lambda x: f"Rp {x:,.0f}")
            display_data['Share 40%'] = display_data['Share 40%'].apply(lambda x: f"Rp {x:,.0f}")
            display_data['Profit Margin %'] = display_data['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
            
            # Ringkasan statistik
            st.markdown("**📊 Ringkasan Data Tersaring**")
            st.info("ℹ️ **Catatan:** Metrik di bawah menunjukkan data produk tersaring saja. Untuk total bisnis akurat, lihat Dasbor Kinerja yang menangani perhitungan tingkat pesanan dengan benar.")
            
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric("Produk Tersaring", len(filtered_data))
            with summary_col2:
                st.metric("Jumlah Pendapatan Produk", f"Rp {filtered_data['Revenue'].sum():,.0f}")
            with summary_col3:
                st.metric("Jumlah Profit Produk", f"Rp {filtered_data['Profit'].sum():,.0f}")
            with summary_col4:
                avg_margin = filtered_data['Profit Margin %'].mean()
                st.metric("Margin Rata-rata", f"{avg_margin:.1f}%")
            
            # Tambahkan perbandingan dengan total bisnis aktual
            if st.session_state.merged_data is not None:
                st.markdown("---")
                st.markdown("**🔍 Perbandingan Total Bisnis**")
                
                # Hitung total bisnis aktual (sama seperti Dasbor Kinerja)
                unique_orders = st.session_state.merged_data.drop_duplicates(subset=['Order ID'])
                actual_total_revenue = unique_orders['Total settlement amount'].sum()
                actual_total_cost = st.session_state.summary_data['Total Cost'].sum()
                actual_total_profit = actual_total_revenue - actual_total_cost
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                with comp_col1:
                    st.metric(
                        "Total Pendapatan Aktual", 
                        f"Rp {actual_total_revenue:,.0f}",
                        help="Dihitung dari pesanan unik (metode Dasbor Kinerja)"
                    )
                with comp_col2:
                    st.metric(
                        "Total Profit Aktual", 
                        f"Rp {actual_total_profit:,.0f}",
                        help="Pendapatan dikurangi total biaya (metode Dasbor Kinerja)"
                    )
                with comp_col3:
                    filter_coverage = (filtered_data['Revenue'].sum() / actual_total_revenue * 100) if actual_total_revenue > 0 else 0
                    st.metric(
                        "Cakupan Filter", 
                        f"{filter_coverage:.1f}%",
                        help="Persentase total pendapatan yang dicakup oleh produk tersaring"
                    )
        
        else:
            st.info("ℹ️ Tidak ada data untuk ditampilkan. Silakan unggah dan proses data Anda terlebih dahulu.")