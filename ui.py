import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_data_upload_section():
    """Bagian unggah data yang ditingkatkan"""
    st.markdown("### 📁 Unggah Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**📊 Pesanan Selesai**")
        pesanan_file = st.file_uploader(
            "Unggah file Excel dengan pesanan selesai",
            type=['xlsx', 'xls'],
            key="pesanan",
            help="File harus berisi data pesanan dengan kolom 'Order Status'"
        )
        
        if pesanan_file:
            try:
                df = pd.read_excel(pesanan_file, header=0, skiprows=[1])
                df.columns = df.columns.str.strip()
                st.session_state.pesanan_data = df
                st.markdown(f'<div class="status-success">✅ Pesanan dimuat: {len(df):,} baris</div>', unsafe_allow_html=True)
                
                with st.expander("📋 Pratinjau Data"):
                    st.dataframe(df.head(), use_container_width=True)
                    
            except Exception as e:
                st.markdown(f'<div class="status-error">❌ Kesalahan memuat file: {str(e)}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**💰 Data Pendapatan**")
        income_file = st.file_uploader(
            "Unggah file Excel dengan data pendapatan",
            type=['xlsx', 'xls'],
            key="income",
            help="File harus berisi kolom 'Order/adjustment ID' dan 'Total settlement amount'"
        )
        
        if income_file:
            try:
                df = pd.read_excel(income_file)
                df.columns = df.columns.str.strip()
                st.session_state.income_data = df
                st.markdown(f'<div class="status-success">✅ Pendapatan dimuat: {len(df):,} baris</div>', unsafe_allow_html=True)
                
                with st.expander("📋 Pratinjau Data"):
                    st.dataframe(df.head(), use_container_width=True)
                    
            except Exception as e:
                st.markdown(f'<div class="status-error">❌ Kesalahan memuat file: {str(e)}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_metrics_dashboard():
    """Dasbor metrik yang ditingkatkan"""
    if st.session_state.summary_data is not None:
        st.markdown("### 📊 Dasbor Kinerja")
        
        # Hitung metrik kunci
        unique_orders = st.session_state.merged_data.drop_duplicates(subset=['Order ID'])
        total_orders = unique_orders['Order ID'].nunique()
        total_revenue = unique_orders['Total settlement amount'].sum()
        total_cost = st.session_state.summary_data['Total Cost'].sum()
        total_profit = total_revenue - total_cost
        total_share_60 = total_profit * 0.6
        total_share_40 = total_profit * 0.4
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Metrik utama dengan 6 kolom
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="💼 Total Pesanan",
                value=f"{total_orders:,}",
                 delta=f"AOV: Rp {avg_order_value:,.0f}"
            )

        with col2:
            st.metric(
                label="💰 Total Pendapatan", 
                value=f"Rp {total_revenue:,.0f}"
            )

        with col3:
            st.metric(
                label="💸 Biaya",
                value=f"Rp {total_cost:,.0f}"
            )

        # Baris kedua (3 kolom)
        col4, col5, col6 = st.columns(3)

        with col4:
            st.metric(
                label="📈 Total Profit",
                value=f"Rp {total_profit:,.0f}",
                delta=f"{profit_margin:.1f}% margin"
            )

        with col5:
            st.metric(
                label="🤝 Share 60%",
                value=f"Rp {total_share_60:,.0f}"
            )

        with col6:
            st.metric(
                label="🤝 Share 40%", 
                value=f"Rp {total_share_40:,.0f}"
            )
        
        # AI Summary
        st.markdown("---")
        if st.button("📄 Tampilkan Ringkasan (Copy ke ChatGPT)", type="secondary"):
            if st.session_state.summary_data is not None:
                summary_text = generate_ai_summary(st.session_state.summary_data)
                st.markdown("### 📋 Ringkasan Teks")
                st.code(summary_text, language="text")
            else:
                st.warning("⚠️ Proses data terlebih dahulu.")
        
        # Bagian grafik
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**📊 10 Produk Teratas berdasarkan Pendapatan**")
            
            top_revenue = st.session_state.summary_data.nlargest(10, 'Revenue')
            
            fig = px.bar(
                top_revenue,
                x='Revenue',
                y='Product Name',
                orientation='h',
                title="Pendapatan per Produk",
                color='Profit Margin %',
                color_continuous_scale='RdYlGn',
                text='Revenue'
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with chart_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("**📈 Distribusi Margin Profit**")
            
            fig = px.histogram(
                st.session_state.summary_data,
                x='Profit Margin %',
                nbins=20,
                title="Distribusi Margin Profit",
                color_discrete_sequence=['#667eea']
            )
            
            fig.add_vline(
                x=st.session_state.summary_data['Profit Margin %'].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"Rata-rata: {st.session_state.summary_data['Profit Margin %'].mean():.1f}%"
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analisis terperinci
        st.markdown("---")
        st.markdown("### 🔍 Analisis Terperinci")
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.markdown("**🏆 Performa Teratas**")
            
            top_profit = st.session_state.summary_data.nlargest(5, 'Profit')[['Product Name', 'Profit', 'Profit Margin %']]
            top_profit['Profit'] = top_profit['Profit'].apply(lambda x: f"Rp {x:,.0f}")
            top_profit['Profit Margin %'] = top_profit['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(top_profit, use_container_width=True, hide_index=True)
        
        with analysis_col2:
            st.markdown("**⚠️ Produk Margin Rendah**")
            
            low_margin = st.session_state.summary_data.nsmallest(5, 'Profit Margin %')[['Product Name', 'Profit', 'Profit Margin %']]
            low_margin['Profit'] = low_margin['Profit'].apply(lambda x: f"Rp {x:,.0f}")
            low_margin['Profit Margin %'] = low_margin['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(low_margin, use_container_width=True, hide_index=True)

def show_cost_management():
    """Antarmuka manajemen biaya yang ditingkatkan"""
    st.markdown("### 💸 Manajemen Biaya")
    
    # Bilah aksi cepat
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📥 Impor Biaya", help="Impor biaya dari file JSON"):
            st.info("Unggah file JSON dengan data biaya")
    
    with action_col2:
        if st.button("📤 Ekspor Biaya", help="Unduh data biaya saat ini"):
            st.download_button(
                label="💾 Unduh JSON",
                data=json.dumps(st.session_state.cost_data, ensure_ascii=False, indent=2),
                file_name=f"product_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with action_col3:
        if st.button("🔄 Segarkan Data", help="Muat ulang data biaya dari file"):
            st.session_state.cost_data = CostManager().load_cost_data()
            st.rerun()
    
    st.markdown("---")
    
    # Form manajemen biaya
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Tambah/Edit Biaya Produk**")
        
        # Pemilihan produk dengan pencarian
        if st.session_state.pesanan_data is not None:
            products = sorted(st.session_state.pesanan_data['Product Name'].astype(str).unique())
            selected_product = st.selectbox(
                "🔍 Pilih Produk",
                options=products,
                key="product_select",
                help="Cari dan pilih produk dari data pesanan Anda"
            )
        else:
            selected_product = st.text_input(
                "📝 Nama Produk",
                key="product_input",
                help="Masukkan nama produk secara manual"
            )
        
        # Input biaya dengan nilai saat ini
        current_cost = st.session_state.cost_data.get(selected_product, 0.0)
        cost_input = st.number_input(
            "💰 Biaya per Unit",
            min_value=0.0,
            value=current_cost,
            format="%.2f",
            key="cost_input",
            help=f"Biaya saat ini: Rp {current_cost:,.2f}"
        )
        
        # Tombol aksi
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.button("💾 Simpan Biaya", type="primary"):
                if selected_product and cost_input >= 0:
                    st.session_state.cost_data[selected_product] = cost_input
                    CostManager().save_cost_data(st.session_state.cost_data)
                    st.success(f"✅ Biaya disimpan untuk {selected_product}")
                    st.rerun()
                else:
                    st.warning("⚠️ Masukkan produk dan biaya yang valid")
        
        with btn_col2:
            if st.button("🗑️ Hapus Biaya", type="secondary"):
                if selected_product in st.session_state.cost_data:
                    del st.session_state.cost_data[selected_product]
                    CostManager().save_cost_data(st.session_state.cost_data)
                    st.success(f"✅ Biaya dihapus untuk {selected_product}")
                    st.rerun()
                else:
                    st.warning("⚠️ Produk tidak ditemukan dalam data biaya")
        
        with btn_col3:
            if st.button("🔄 Bersihkan Formulir"):
                st.rerun()
    
    with col2:
        st.markdown("**📊 Statistik Biaya**")
        
        if st.session_state.cost_data:
            total_products = len(st.session_state.cost_data)
            avg_cost = sum(st.session_state.cost_data.values()) / total_products
            min_cost = min(st.session_state.cost_data.values())
            max_cost = max(st.session_state.cost_data.values())
            
            st.metric("📦 Total Produk", total_products)
            st.metric("💰 Rata-rata Biaya", f"Rp {avg_cost:,.0f}")
            st.metric("📉 Biaya Minimum", f"Rp {min_cost:,.0f}")
            st.metric("📈 Biaya Maksimum", f"Rp {max_cost:,.0f}")
        else:
            st.info("Tidak ada data biaya")
    
    # Tabel data biaya
    st.markdown("---")
    st.markdown("### 📋 Data Biaya Saat Ini")
    
    if st.session_state.cost_data:
        # Cari dan filter
        search_term = st.text_input("🔍 Cari produk", placeholder="Ketik untuk mencari...")
        
        cost_df = pd.DataFrame(
            list(st.session_state.cost_data.items()),
            columns=["Product Name", "Cost per Unit"]
        )
        
        if search_term:
            cost_df = cost_df[cost_df['Product Name'].str.contains(search_term, case=False, na=False)]
        
        cost_df = cost_df.sort_values("Product Name")
        
        # Format untuk tampilan
        cost_display = cost_df.copy()
        cost_display['Cost per Unit'] = cost_display['Cost per Unit'].apply(lambda x: f"Rp {x:,.0f}")
        
        st.dataframe(cost_display, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Tidak ada data biaya. Tambahkan beberapa biaya produk untuk memulai.")

def show_advanced_analytics():
    """Analisis lanjutan dengan grafik interaktif"""
    if st.session_state.summary_data is not None:
        st.markdown("### 📊 Analisis Lanjutan")
        
        # Pemilihan grafik
        chart_type = st.selectbox(
            "📈 Pilih Jenis Grafik",
            ["Pendapatan vs Profit (Scatter)", "Analisis Margin Profit", "Matriks Kinerja Produk", "Distribusi Penjualan"]
        )
        
        if chart_type == "Pendapatan vs Profit (Scatter)":
            fig = px.scatter(
                st.session_state.summary_data,
                x='Revenue',
                y='Profit',
                size='TotalQty',
                color='Profit Margin %',
                hover_data=['Product Name'],
                title="Analisis Pendapatan vs Profit",
                color_continuous_scale='RdYlGn',
                labels={'Revenue': 'Pendapatan (Rp)', 'Profit': 'Profit (Rp)'}
            )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Analisis Margin Profit":
            # Buat subplot
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Distribusi Margin Profit', 'Produk Teratas berdasarkan Margin', 
                              'Pendapatan vs Margin', 'Kuantitas vs Margin'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Histogram
            fig.add_trace(
                go.Histogram(x=st.session_state.summary_data['Profit Margin %'], 
                           name="Distribusi Margin", showlegend=False),
                row=1, col=1
            )
            
            # Produk teratas berdasarkan margin
            top_margin = st.session_state.summary_data.nlargest(10, 'Profit Margin %')
            fig.add_trace(
                go.Bar(x=top_margin['Product Name'], y=top_margin['Profit Margin %'],
                      name="Margin Tertinggi", showlegend=False),
                row=1, col=2
            )
            
            # Scatter pendapatan vs margin
            fig.add_trace(
                go.Scatter(x=st.session_state.summary_data['Revenue'], 
                          y=st.session_state.summary_data['Profit Margin %'],
                          mode='markers', name="Pendapatan vs Margin", showlegend=False),
                row=2, col=1
            )
            
            # Scatter kuantitas vs margin
            fig.add_trace(
                go.Scatter(x=st.session_state.summary_data['TotalQty'], 
                          y=st.session_state.summary_data['Profit Margin %'],
                          mode='markers', name="Kuantitas vs Margin", showlegend=False),
                row=2, col=2
            )
            
            fig.update_layout(height=600, title_text="Analisis Komprehensif Margin Profit")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Matriks Kinerja Produk":
            # Buat matriks kinerja dengan perbaikan untuk nilai negatif
            plot_data = st.session_state.summary_data.copy()
            
            # Pastikan nilai size selalu positif (gunakan absolut + offset kecil)
            plot_data['size_value'] = plot_data['Revenue'].abs() + 1
            
            # Buat informasi hover yang lebih informatif
            plot_data['hover_text'] = (
                plot_data['Product Name'] + '<br>' +
                'Revenue: Rp ' + plot_data['Revenue'].apply(lambda x: f"{x:,.0f}") + '<br>' +
                'Profit: Rp ' + plot_data['Profit'].apply(lambda x: f"{x:,.0f}") + '<br>' +
                'Margin: ' + plot_data['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
            )
            
            fig = px.scatter(
                plot_data,
                x='TotalQty',
                y='Profit Margin %',
                size='size_value',  # Gunakan nilai yang sudah diperbaiki
                color='Profit',
                hover_name='Product Name',
                hover_data={
                    'Revenue': ':,.0f',
                    'Profit': ':,.0f',
                    'TotalQty': ':,.0f',
                    'Profit Margin %': ':.1f',
                    'size_value': False  # Sembunyikan kolom size_value dari hover
                },
                title="Matriks Kinerja Produk",
                labels={
                    'TotalQty': 'Total Kuantitas Terjual', 
                    'Profit Margin %': 'Margin Profit (%)',
                    'Profit': 'Profit (Rp)'
                },
                color_continuous_scale='RdYlGn',
                size_max=50  # Batasi ukuran maksimum marker
            )
            
            # Tambahkan garis kuadran
            median_qty = plot_data['TotalQty'].median()
            median_margin = plot_data['Profit Margin %'].median()
            
            fig.add_hline(y=median_margin, line_dash="dash", line_color="red", 
                         annotation_text=f"Margin Median: {median_margin:.1f}%")
            fig.add_vline(x=median_qty, line_dash="dash", line_color="red", 
                         annotation_text=f"Kuantitas Median: {median_qty:.0f}")
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Analisis kuadran
            st.markdown("**📊 Analisis Kuadran:**")
            quad_col1, quad_col2, quad_col3, quad_col4 = st.columns(4)
            
            # Volume tinggi, margin tinggi (Bintang)
            stars = plot_data[
                (plot_data['TotalQty'] >= median_qty) & 
                (plot_data['Profit Margin %'] >= median_margin)
            ]
            
            # Volume tinggi, margin rendah (Kuda Pekerja)
            workhorses = plot_data[
                (plot_data['TotalQty'] >= median_qty) & 
                (plot_data['Profit Margin %'] < median_margin)
            ]
            
            # Volume rendah, margin tinggi (Ceruk)
            niche = plot_data[
                (plot_data['TotalQty'] < median_qty) & 
                (plot_data['Profit Margin %'] >= median_margin)
            ]
            
            # Volume rendah, margin rendah (Masalah)
            problem = plot_data[
                (plot_data['TotalQty'] < median_qty) & 
                (plot_data['Profit Margin %'] < median_margin)
            ]
            
            with quad_col1:
                st.metric("⭐ Bintang", len(stars), "Vol Tinggi, Margin Tinggi")
                if len(stars) > 0:
                    st.caption(f"Avg Revenue: Rp {stars['Revenue'].mean():,.0f}")
            with quad_col2:
                st.metric("🐎 Kuda Pekerja", len(workhorses), "Vol Tinggi, Margin Rendah")
                if len(workhorses) > 0:
                    st.caption(f"Avg Revenue: Rp {workhorses['Revenue'].mean():,.0f}")
            with quad_col3:
                st.metric("💎 Ceruk", len(niche), "Vol Rendah, Margin Tinggi")
                if len(niche) > 0:
                    st.caption(f"Avg Revenue: Rp {niche['Revenue'].mean():,.0f}")
            with quad_col4:
                st.metric("⚠️ Masalah", len(problem), "Vol Rendah, Margin Rendah")
                if len(problem) > 0:
                    st.caption(f"Avg Revenue: Rp {problem['Revenue'].mean():,.0f}")
            
            # Tambahkan tabel produk untuk setiap kuadran
            st.markdown("---")
            st.markdown("**🔍 Detail Produk per Kuadran:**")
            
            quad_tab1, quad_tab2, quad_tab3, quad_tab4 = st.tabs(["⭐ Bintang", "🐎 Kuda Pekerja", "💎 Ceruk", "⚠️ Masalah"])
            
            with quad_tab1:
                if len(stars) > 0:
                    display_stars = stars[['Product Name', 'TotalQty', 'Revenue', 'Profit', 'Profit Margin %']].copy()
                    display_stars['Revenue'] = display_stars['Revenue'].apply(lambda x: f"Rp {x:,.0f}")
                    display_stars['Profit'] = display_stars['Profit'].apply(lambda x: f"Rp {x:,.0f}")
                    display_stars['Profit Margin %'] = display_stars['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_stars.sort_values('TotalQty', ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada produk dalam kategori ini")
            
            with quad_tab2:
                if len(workhorses) > 0:
                    display_workhorses = workhorses[['Product Name', 'TotalQty', 'Revenue', 'Profit', 'Profit Margin %']].copy()
                    display_workhorses['Revenue'] = display_workhorses['Revenue'].apply(lambda x: f"Rp {x:,.0f}")
                    display_workhorses['Profit'] = display_workhorses['Profit'].apply(lambda x: f"Rp {x:,.0f}")
                    display_workhorses['Profit Margin %'] = display_workhorses['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_workhorses.sort_values('TotalQty', ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada produk dalam kategori ini")
            
            with quad_tab3:
                if len(niche) > 0:
                    display_niche = niche[['Product Name', 'TotalQty', 'Revenue', 'Profit', 'Profit Margin %']].copy()
                    display_niche['Revenue'] = display_niche['Revenue'].apply(lambda x: f"Rp {x:,.0f}")
                    display_niche['Profit'] = display_niche['Profit'].apply(lambda x: f"Rp {x:,.0f}")
                    display_niche['Profit Margin %'] = display_niche['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_niche.sort_values('Profit Margin %', ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada produk dalam kategori ini")
            
            with quad_tab4:
                if len(problem) > 0:
                    display_problem = problem[['Product Name', 'TotalQty', 'Revenue', 'Profit', 'Profit Margin %']].copy()
                    display_problem['Revenue'] = display_problem['Revenue'].apply(lambda x: f"Rp {x:,.0f}")
                    display_problem['Profit'] = display_problem['Profit'].apply(lambda x: f"Rp {x:,.0f}")
                    display_problem['Profit Margin %'] = display_problem['Profit Margin %'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_problem.sort_values('Profit Margin %', ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("Tidak ada produk dalam kategori ini")
        
        elif chart_type == "Distribusi Penjualan":
            # Buat analisis distribusi
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Distribusi Pendapatan', 'Distribusi Profit', 
                              'Distribusi Kuantitas', 'Pendapatan Kumulatif'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Distribusi pendapatan
            fig.add_trace(
                go.Box(y=st.session_state.summary_data['Revenue'], 
                      name="Pendapatan", showlegend=False),
                row=1, col=1
            )
            
            # Distribusi profit
            fig.add_trace(
                go.Box(y=st.session_state.summary_data['Profit'], 
                      name="Profit", showlegend=False),
                row=1, col=2
            )
            
            # Distribusi kuantitas
            fig.add_trace(
                go.Box(y=st.session_state.summary_data['TotalQty'], 
                      name="Kuantitas", showlegend=False),
                row=2, col=1
            )
            
            # Pendapatan kumulatif (Pareto)
            sorted_data = st.session_state.summary_data.sort_values('Revenue', ascending=False)
            sorted_data['Cumulative Revenue'] = sorted_data['Revenue'].cumsum()
            sorted_data['Cumulative %'] = (sorted_data['Cumulative Revenue'] / sorted_data['Revenue'].sum()) * 100
            
            fig.add_trace(
                go.Scatter(x=list(range(1, len(sorted_data) + 1)), 
                          y=sorted_data['Cumulative %'],
                          mode='lines+markers', name="Persentase Pendapatan Kumulatif", showlegend=False),
                row=2, col=2
            )
            
            fig.update_layout(height=600, title_text="Analisis Distribusi Penjualan")
            st.plotly_chart(fig, use_container_width=True)
        
        # Wawasan tambahan

                # --- 🔗 Tombol Ringkas + Lanjut ke ChatGPT ---
        st.markdown("---")
        if st.button("💬 Ringkas & Lanjut ke ChatGPT", type="primary"):
            if st.session_state.summary_data is not None:
                # --- ringkas data ---
                df = st.session_state.summary_data
                total_sku   = len(df)
                untung      = len(df[df['Profit'] > 0])
                hi_margin   = len(df[df['Profit Margin %'] > 20])
                top20_pct   = (df.nlargest(int(total_sku*0.2), 'Revenue')['Revenue'].sum() /
                               df['Revenue'].sum() * 100)
                low_margin  = len(df[df['Profit Margin %'] < 10])
                hi_vol_low  = len(df[(df['TotalQty'] >= df['TotalQty'].median()) &
                                     (df['Profit Margin %'] < 15)])

                prompt = f"""
                Kamu adalah Chief Data Scientist e-commerce. Buat laporan strategis 360° dari data berikut:
                                
                📊 Ringkasan Data:
                - Total SKU        : {total_sku}
                - Produk Untung    : {untung}
                - Margin >20 %     : {hi_margin}
                - 20 % Top SKU     : {top20_pct:.1f}% pendapatan
                - SKU margin <10 % : {low_margin}
                - SKU volume-tinggi-margin-rendah : {hi_vol_low}

                💬 Prompt ChatGPT:
                Buat:
                1. Executive summary 3 kalimat.
                2. 3 SKU prioritas optimize.
                3. 2 pricing strategy SKU margin rendah.
                4. Forecast 30 hari jika strategi 50 % rollout.
                
                """

                # encode URL-safe
                from urllib.parse import quote
                chatgpt_url = f"https://chat.openai.com/?q={quote(prompt)}"
                st.markdown(
                    f'<a href="{chatgpt_url}" target="_blank" rel="noopener noreferrer">'
                    '📲 Buka ChatGPT (tab baru)</a>',
                    unsafe_allow_html=True
                )
                st.text_area("📋 Copy prompt:", value=prompt, height=250)
            else:
                st.warning("⚠️ Proses data terlebih dahulu.")
        
        st.markdown("---")
        st.markdown("### 🔍 Wawasan Utama")
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("**📈 Wawasan Kinerja**")
            
            # Hitung wawasan
            total_products = len(st.session_state.summary_data)
            profitable_products = len(st.session_state.summary_data[st.session_state.summary_data['Profit'] > 0])
            high_margin_products = len(st.session_state.summary_data[st.session_state.summary_data['Profit Margin %'] > 20])
            
            st.write(f"• **{profitable_products}/{total_products}** produk menghasilkan profit")
            st.write(f"• **{high_margin_products}** produk memiliki margin >20%")
            st.write(f"• **Produk 20% teratas** menghasilkan **{(st.session_state.summary_data.nlargest(int(total_products*0.2), 'Revenue')['Revenue'].sum() / st.session_state.summary_data['Revenue'].sum() * 100):.1f}%** pendapatan")
        
        with insight_col2:
            st.markdown("**💡 Rekomendasi**")
            
            # Rekomendasi utama
            low_margin = st.session_state.summary_data[st.session_state.summary_data['Profit Margin %'] < 10]
            if not low_margin.empty:
                st.write(f"• Tinjau penetapan harga untuk **{len(low_margin)}** produk margin rendah")
            
            high_volume_low_margin = st.session_state.summary_data[
                (st.session_state.summary_data['TotalQty'] >= st.session_state.summary_data['TotalQty'].median()) & 
                (st.session_state.summary_data['Profit Margin %'] < 15)
            ]
            if not high_volume_low_margin.empty:
                st.write(f"• Optimalkan biaya untuk **{len(high_volume_low_margin)}** produk volume tinggi")
            
            st.write("• Fokuskan pemasaran pada produk margin tinggi")
            st.write("• Pertimbangkan menghentikan item yang secara konsisten berkinerja rendah")
    
    else:
        st.info("ℹ️ Silakan proses data Anda terlebih dahulu untuk melihat analisis lanjutan")

           

def generate_ai_summary(summary_df):
    # --- Hitung metrik BERSIH (tanpa duplikat order) ---
    if st.session_state.merged_data is None:
        return "Data belum diproses."

    unique_orders = st.session_state.merged_data.drop_duplicates(subset=['Order ID'])
    total_r = unique_orders['Total settlement amount'].sum()
    total_cost = summary_df['Total Cost'].sum()
    total_p = total_r - total_cost
    avg_m   = summary_df['Profit Margin %'].mean()

    top = summary_df.nlargest(5, 'Profit')[['Product Name', 'Profit', 'Profit Margin %']]

    prompt = f"""
    Kamu adalah Chief Data Scientist e-commerce. Buat laporan strategis 360° dari data berikut:

    📊 Total Pendapatan               : Rp {total_r:,.0f}
    📈 Total Profit                   : Rp {total_p:,.0f}
    📉 Margin Rata-rata               : {avg_m:.1f}%

    5 Produk Ter-Profit:
    {top.to_string(index=False)}

    Deliverables:
    1. Executive summary 3 kalimat
    2. 3 SKU prioritas optimize
    3. 2 pricing strategy SKU margin rendah
    4. 2 saran strategi peningkatan profit
        """

    # --- Tombol ke ChatGPT ---
    from urllib.parse import quote
    encoded = quote(prompt)
    chatgpt_url = f"https://chat.openai.com/?q={encoded}"

    st.markdown(
        f'<a href="{chatgpt_url}" target="_blank" rel="noopener noreferrer">'
        '💬 Buka ChatGPT (tab baru)</a>',
        unsafe_allow_html=True
    )

    st.text_area("📋 Copy prompt:", value=prompt, height=280)
    #return prompt  # opsional, sudah tampil di text_area