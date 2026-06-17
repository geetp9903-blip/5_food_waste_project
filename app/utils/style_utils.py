import streamlit as st

def inject_premium_styles():
    """Injects custom CSS to achieve modern, high-quality, and visual design aesthetics in Streamlit."""
    css = """
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Fonts and General Reset */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        }

        /* App Background and Primary Accent */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
            color: #f1f5f9;
        }
        
        /* Hide default Streamlit sidebar and top header */
        [data-testid="stSidebar"] {
            display: none;
        }
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Top Header Styling */
        h1 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            background: linear-gradient(to right, #38bdf8, #818cf8, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            color: #e2e8f0;
        }

        /* Custom Cards (Glassmorphism) */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            margin-bottom: 20px;
            transition: all 0.3s ease;
            animation: fadeIn 0.5s ease-in-out;
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 8px 40px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        /* Custom Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
            transform: translateY(-1px);
        }

        /* Form Inputs */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
            background-color: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Navbar styling */
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 15px;
            padding: 15px 0;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
            border-radius: 12px;
        }

        /* Metrics styling */
        [data-testid="stMetricValue"] {
            font-size: 2.2rem;
            font-weight: 700;
            color: #38bdf8;
        }

        [data-testid="stMetricLabel"] {
            color: #94a3b8;
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        /* Status Badges */
        .badge-pending { background-color: rgba(250, 204, 21, 0.2); color: #facc15; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
        .badge-completed { background-color: rgba(74, 222, 128, 0.2); color: #4ade80; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
        .badge-cancelled { background-color: rgba(248, 113, 113, 0.2); color: #f87171; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Scrollbar customizing */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
