import streamlit as st
from data_manager import DataManager
from data_analysis import DataAnalysis
from cost_manager import CostManager
from report_generator import ReportGenerator
from ui import show_data_upload_section, show_metrics_dashboard, show_cost_management, show_advanced_analytics

# Konfigurasi halaman
st.set_page_config(
    page_title="📊 Analisis Pendapatan & Pesanan",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analisis Pendapatan & Pesanan</h1>
        <p>Intelijen bisnis komprehensif untuk operasi e-commerce Anda</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inisialisasi manajer data
    data_manager = DataManager()
    cost_manager = CostManager()
    report_generator = ReportGenerator()
    data_analysis = DataAnalysis()
    
    # Inisialisasi state sesi
    if 'cost_data' not in st.session_state:
        st.session_state.cost_data = cost_manager.load_cost_data()
    if 'pesanan_data' not in st.session_state:
        st.session_state.pesanan_data = None
    if 'income_data' not in st.session_state:
        st.session_state.income_data = None
    if 'merged_data' not in st.session_state:
        st.session_state.merged_data = None
    if 'summary_data' not in st.session_state:
        st.session_state.summary_data = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Panel Kontrol")
        
        # Status data
        st.markdown("**📊 Status Data:**")
        pesanan_status = "✅ Dimuat" if st.session_state.pesanan_data is not None else "❌ Tidak dimuat"
        income_status = "✅ Dimuat" if st.session_state.income_data is not None else "❌ Tidak dimuat"
        processed_status = "✅ Diproses" if st.session_state.summary_data is not None else "❌ Tidak diproses"
        
        st.write(f"Pesanan: {pesanan_status}")
        st.write(f"Pendapatan: {income_status}")
        st.write(f"Analisis: {processed_status}")
        
        st.markdown("---")
        
        # Aksi cepat
        st.markdown("**⚡ Aksi Cepat:**")
        
        if st.button("🔄 Proses Data", type="primary", use_container_width=True):
            if st.session_state.pesanan_data is not None and st.session_state.income_data is not None:
                with st.spinner("Memproses data..."):
                    merged, summary = data_manager.process_data(
                        st.session_state.pesanan_data, 
                        st.session_state.income_data, 
                        st.session_state.cost_data
                    )
                    
                    if merged is not None:
                        st.session_state.merged_data = merged
                        st.session_state.summary_data = summary
                        st.success("✅ Data diproses!")
                        st.rerun()
                    else:
                        st.error("❌ Tidak ditemukan data yang cocok")
            else:
                st.warning("⚠️ Unggah kedua file terlebih dahulu")
        
        if st.session_state.summary_data is not None:
            if st.button("📥 Ekspor Laporan", use_container_width=True):
                try:
                    excel_data = report_generator.create_excel_report(
                        st.session_state.merged_data,
                        st.session_state.summary_data,
                        st.session_state.cost_data
                    )
                    
                    st.download_button(
                        label="💾 Unduh Excel",
                        data=excel_data,
                        file_name=f"income_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Kesalahan: {str(e)}")
        
        st.markdown("---")
        
        # Statistik cepat biaya
        if st.session_state.cost_data:
            st.markdown("**💰 Data Biaya:**")
            st.write(f"Produk: {len(st.session_state.cost_data)}")
            avg_cost = sum(st.session_state.cost_data.values()) / len(st.session_state.cost_data)
            st.write(f"Biaya Rata-rata: Rp {avg_cost:,.0f}")
    
    # Tab konten utama
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dasbor", 
        "💸 Manajemen Biaya", 
        "📈 Analisis", 
        "📋 Detail Data"
    ])
    
    with tab1:
        show_data_upload_section()
        
        st.markdown("---")
        
        show_metrics_dashboard()
    
    with tab2:
        show_cost_management()
    
    with tab3:
        show_advanced_analytics()
    
    with tab4:
        data_analysis.show_data_details()

if __name__ == "__main__":
    main()