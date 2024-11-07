import streamlit as st
import logging

import uuid
import pprint
import pandas as pd
from urllib.error import URLError
from datetime import datetime

import src.st_utils as st_utils
import src.utils as utils

from sdv.metadata import Metadata
from sdv.datasets.local import load_csvs
from sdv.multi_table import HMASynthesizer

st.set_page_config(page_title="Test Data Management",  layout="wide", page_icon="📈")

logger = logging.getLogger()
st.markdown("# Test Data Management")
pp = pprint.PrettyPrinter(indent=2)

multiple_files = st.file_uploader(
    "Sample Data  Uploader",
    accept_multiple_files=True
)

for file in multiple_files:
    dataframe = pd.read_csv(file)
    file.seek(0)
    st.write(f"### {file.name}")
    st.write(dataframe.head())
    
    dataframe.to_csv(f"data/{file.name}", index=False)

    data = load_csvs(folder_name='data/')
    # st.write("## Sample Data")
    # for data_name in data:
    #     st.write(data[data_name].head())

if st.button("Generate ER Diagram"):
    metadata = Metadata.detect_from_dataframes(data)
    st.session_state['metadata'] = metadata
    st.write("## ER Diagram")
    with st.container():
        st.write(metadata.visualize())

if st.button("Generate Synthetic Data"):
    metadata = st.session_state['metadata']
    synthesizer = HMASynthesizer(metadata)
    synthesizer.fit(data)
    synthetic_data = synthesizer.sample(scale=10)
    with st.container():
        st.write("### synthetic_data")
        for s_data in synthetic_data:
            st.write(synthetic_data[s_data].sample(n=5, random_state=1))
        
    from sdv.evaluation.multi_table import run_diagnostic

    diagnostic = run_diagnostic(
        real_data=data,
        synthetic_data=synthetic_data,
        metadata=metadata
    )
    
    st.write("### Diagnostic report")
    # st.write(diagnostic)

    from sdv.evaluation.multi_table import evaluate_quality

    quality_report = evaluate_quality(
        data,
        synthetic_data,
        metadata
    )

    st.write("### Quality report")
    # st.write(dir(quality_report))
    st.write(quality_report.get_info())
    st.write("### Quality Score:")
    st.write(quality_report.get_score())


    st.write(quality_report.get_visualization( property_name='Column Pair Trends',
        table_name="guests"))
    # st.write(quality_report.get_visualization( property_name='Column Pair Trends',
    #     table_name="hotels"))

    from sdv.evaluation.multi_table import get_column_pair_plot

    fig = get_column_pair_plot(
        real_data=data,
        synthetic_data=synthetic_data,
        column_names=['room_rate', 'room_type'],
        table_name='guests',
        metadata=metadata
    )
    st.write("#### Column pair plot")
    st.plotly_chart(fig, use_container_width=True)

    from sdv.evaluation.multi_table import get_column_plot

    fig = get_column_plot(
        real_data=data,
        synthetic_data=synthetic_data,
        metadata=metadata,
        table_name='guests',
        column_name='amenities_fee'
    )
    st.write("#### Column Plot")
    st.plotly_chart(fig, use_container_width=True)

    from sdv.evaluation.multi_table import get_cardinality_plot

    fig = get_cardinality_plot(
        real_data=data,
        synthetic_data=synthetic_data,
        child_table_name='guests',
        parent_table_name='hotels',
        child_foreign_key='hotel_id',
        metadata=metadata)
        
    st.write("#### Cardinality Plot")
    st.plotly_chart(fig, use_container_width=True)
    
    # fig.show()
    












