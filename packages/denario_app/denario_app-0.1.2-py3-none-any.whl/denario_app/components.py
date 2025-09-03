from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from denario import Denario, Journal
from denario import models

from utils import show_markdown_file, create_zip_in_memory, stream_to_streamlit

#--- 
# Components
#---

def description_comp(den: Denario) -> None:

    st.header("Data description")

    data_descr = st.text_area(
        "Describe the data and tools to be used in the project. You may also include information about the computing resources required.",
        placeholder="E.g. Analyze the experimental data stored in /path/to/data.csv using sklearn and pandas. This data includes time-series measurements from a particle detector.",
        key="data_descr",
        height=100
    )

    uploaded_file = st.file_uploader("Alternatively, upload a file with the data description in markdown format.", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        den.set_data_description(content)   

    if data_descr:

        den.set_data_description(data_descr)

    st.markdown("### Current data description")

    try:
        show_markdown_file(den.project_dir+"/input_files/data_description.md",label="data description")
    except FileNotFoundError:
        st.write("Data description not set.")

def idea_comp(den: Denario) -> None:

    st.header("Research idea")
    st.write("Generate a research idea provided the data description.")

    st.write("Choose between a fast generation process or a more involved one using planning and control through [cmbagent](https://github.com/CMBAgents/cmbagent).")

    fast = st.toggle("Fast generation",value=True,key="fast_toggle_idea")

    model_keys = list(models.keys())

    if fast:

        default_fast_idea_index = model_keys.index("gemini-2.0-flash")

        st.caption("Choose a LLM model for the fast generation")
        llm_model = st.selectbox(
            "LLM Model",
            model_keys,
            index=default_fast_idea_index,
            key="llm_model_idea"
        )

    else:

        # Get index of desired default models
        default_idea_maker_index = model_keys.index("gpt-4o")
        default_idea_hater_index = model_keys.index("claude-3.7-sonnet")

        # Add model selection dropdowns
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Idea Maker: Generates and selects the best research ideas based on the data description")
            idea_maker_model = st.selectbox(
                "Idea Maker Model",
                model_keys,
                index=default_idea_maker_index,
                key="idea_maker_model"
            )
        with col2:
            st.caption("Idea Hater: Critiques ideas and proposes recommendations for improvement")
            idea_hater_model = st.selectbox(
                "Idea Hater Model",
                model_keys,
                index=default_idea_hater_index,
                key="idea_hater_model"
            )
    
    press_button = st.button("Generate", type="primary",key="get_idea")
    if press_button:

        with st.spinner("Generating research idea...", show_time=True):

            log_box = st.empty()

            # Redirect console output to app
            with stream_to_streamlit(log_box):

                if fast:
                    den.get_idea_fast(llm=llm_model, verbose=True)
                else:
                    den.get_idea(idea_maker_model=models[idea_maker_model], idea_hater_model=models[idea_hater_model])

        st.success("Done!")

    uploaded_file = st.file_uploader("Choose a file with the research idea", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        den.set_idea(content)

    try:
        show_markdown_file(den.project_dir+"/input_files/idea.md", extra_format=True, label="idea")
    except FileNotFoundError:
        st.write("Idea not generated or uploaded.")

def method_comp(den: Denario) -> None:

    st.header("Methods")
    st.write("Generate the methods to be employed in the computation of the results, provided the idea and data description.")

    st.write("Choose between a fast generation process or a more involved one using planning and control through [cmbagent](https://github.com/CMBAgents/cmbagent).")

    fast = st.toggle("Fast generation",value=True,key="fast_toggle_method")

    model_keys = list(models.keys())

    default_fast_method_index = model_keys.index("gemini-2.0-flash")

    if fast:

        st.caption("Choose a LLM model for the fast generation")
        llm_model = st.selectbox(
            "LLM Model",
            model_keys,
            index=default_fast_method_index,
            key="llm_model_method"
        )

    press_button = st.button("Generate", type="primary",key="get_method")
    if press_button:

        with st.spinner("Generating methods...", show_time=True):

            log_box = st.empty()

            # Redirect console output to app
            with stream_to_streamlit(log_box):

                if fast:
                    den.get_method_fast(llm=llm_model, verbose=True)
                else:
                    den.get_method()

        st.success("Done!")

    uploaded_file = st.file_uploader("Choose a file with the research methods", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        den.set_method(content)

    try:
        show_markdown_file(den.project_dir+"/input_files/methods.md",label="methods")
    except FileNotFoundError:
        st.write("Methods not generated or uploaded.")
        
def results_comp(den: Denario) -> None:

    st.header("Results")
    st.write("Compute the results, given the methods, idea and data description.")

    model_keys = list(models.keys())

    # Get index of desired default models
    default_researcher_index = model_keys.index("gemini-2.5-pro")
    default_engineer_index = model_keys.index("gemini-2.5-pro")

    # Add model selection dropdowns
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Engineer: Generates the code to compute the results")
        engineer_model = st.selectbox(
            "Engineer Model",
            model_keys,
            index=default_engineer_index,
            key="engineer_model"
        )
    with col2:
        st.caption("Researcher: processes the results and writes the results report")
        researcher_model = st.selectbox(
            "Researcher Model",
            model_keys,
            index=default_researcher_index,
            key="researcher_model"
        )

    ## add option dropdown for restart at step
    with st.expander("Options for the results generation"):
        restart_at_step = st.number_input("Restart at step", min_value=0, max_value=100, value=0)

    press_button = st.button("Generate", type="primary",key="get_results")
    if press_button:

        with st.spinner("Computing results...", show_time=True):

            log_box = st.empty()

            # Redirect console output to app
            with stream_to_streamlit(log_box):

                den.get_results(engineer_model=models[engineer_model], 
                                researcher_model=models[researcher_model],
                                restart_at_step=restart_at_step)

        st.success("Done!")

    uploaded_files = st.file_uploader("Upload markdown file and/or plots from the results of the research", accept_multiple_files=True)

    if uploaded_files:
        plots = []
        for file in uploaded_files:
            if file.name.endswith(".md"):
                content = file.read().decode("utf-8")
                den.set_results(content)
            else:
                plots.append(Image.open(file))
        den.set_plots(plots)

    plots = list(Path(den.project_dir+"/input_files/plots").glob("*"))

    num_plots = len(list(plots))

    if num_plots>0:
        plots_cols = st.columns(num_plots)

        for i, plot in enumerate(plots):
            with plots_cols[i]:
                st.image(plot, caption=plot.name)

        plots_zip = create_zip_in_memory(den.project_dir+"/input_files/plots")

        st.download_button(
            label="Download plots",
            data=plots_zip,
            file_name="plots.zip",
            mime="application/zip",
            icon=":material/download:",
        )

    else:
        st.write("Plots not generated or uploaded.")

    try:

        codes_zip = create_zip_in_memory(den.project_dir+"/experiment_generation_output")

        st.download_button(
            label="Download codes",
            data=codes_zip,
            file_name="codes.zip",
            mime="application/zip",
            icon=":material/download:",
        )

        show_markdown_file(den.project_dir+"/input_files/results.md",label="results summary")

    except FileNotFoundError:
        st.write("Results not generated or uploaded.")

def paper_comp(den: Denario) -> None:

    st.header("Article")
    st.write("Write the article using the computed results of the research.")

    with st.expander("Options for the paper writing agents"):

        st.caption("Choose a LLM model for the paper generation")
        llm_model = st.selectbox(
            "LLM Model",
            models.keys(),
            index=0,
            key="llm_model_paper"
        )

        selected_journal = st.selectbox(
            "Choose the journal for the latex style:",
            [j.value for j in Journal],
            index=0, key="journal_select")
        
        citations = st.toggle("Add citations",value=True,key="toggle_citations")

        writer = st.text_input(
            "Describe the type of researcher e.g. cosmologist, biologist... Default is 'scientist'.",
            placeholder="scientist",
            key="writer_type",
            value="scientist",
        )

    press_button = st.button("Generate", type="primary",key="get_paper")
    if press_button:

        with st.spinner("Writing the paper...", show_time=True):

            # log_box = st.empty()

            # Redirect console output to app
            # with stream_to_streamlit(log_box):

            den.get_paper(journal=selected_journal,
                        llm=llm_model,
                        writer=writer,
                        add_citations=citations)

        st.success("Done!")
        st.balloons()

    try:

        texfile = den.project_dir+"/paper/paper_v4.tex"

        # Ensure that the .tex has been created and we can read it
        with open(texfile, "r") as f:
            f.read()

        paper_zip = create_zip_in_memory(den.project_dir+"/paper")

        st.download_button(
            label="Download latex files",
            data=paper_zip,
            file_name="paper.zip",
            mime="application/zip",
            icon=":material/download:",
        )

    except FileNotFoundError:
        st.write("Latex not generated yet.")

    try:

        pdffile = den.project_dir+"/paper/paper_v4.pdf"

        with open(pdffile, "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(label="Download pdf",
                    data=PDFbyte,
                    file_name="paper.pdf",
                    mime='application/octet-stream',
                    icon=":material/download:")

        pdf_viewer(pdffile)

    except FileNotFoundError:
        st.write("Pdf not generated yet.")

def check_idea_comp(den: Denario) -> None:
    
    st.header("Check idea")
    st.write("Check if the research idea has been investigated in previous literature.")

    fast = st.toggle("Fast generation",value=True,key="fast_toggle_check_idea")

    try:
        den.set_idea()
        idea = den.research.idea

        # show current idea
        st.markdown("### Current idea")
        st.write(idea)

        press_button = st.button("Literature search", type="primary", key="get_literature")
        
        if press_button:
            with st.spinner("Searching for previous literature...", show_time=True):

                log_box = st.empty()

                # Redirect console output to app
                with stream_to_streamlit(log_box):

                    if fast:
                        result = den.check_idea_fast(verbose=True)
                    else:
                        result = den.check_idea()
                        st.write(result)

            st.success("Literature search completed!")

    except FileNotFoundError:
        st.write("Need to generate an idea first.")

    

def keywords_comp(den: Denario) -> None:

    st.header("Keywords")
    st.write("Generate keywords from your research text.")
    
    input_text = st.text_area(
        "Enter your research text to extract keywords:",
        placeholder="Multi-agent systems (MAS) utilizing multiple Large Language Model agents with Retrieval Augmented Generation and that can execute code locally may become beneficial in cosmological data analysis. Here, we illustrate a first small step towards AI-assisted analyses and a glimpse of the potential of MAS to automate and optimize scientific workflows in Cosmology. The system architecture of our example package, that builds upon the autogen/ag2 framework, can be applied to MAS in any area of quantitative scientific research. The particular task we apply our methods to is the cosmological parameter analysis of the Atacama Cosmology Telescope lensing power spectrum likelihood using Monte Carlo Markov Chains. Our work-in-progress code is open source and available at this https URL.",
        height=200
    )
    
    n_keywords = st.slider("Number of keywords to generate:", min_value=1, max_value=10, value=5)
    
    press_button = st.button("Generate Keywords", type="primary", key="get_keywords")
    
    if press_button and input_text:
        with st.spinner("Generating keywords..."):
            den.get_keywords(input_text, n_keywords=n_keywords)
            
            if hasattr(den.research, 'keywords') and den.research.keywords:
                st.success("Keywords generated!")
                st.write("### Generated Keywords")
                for keyword, url in den.research.keywords.items():
                    st.markdown(f"- [{keyword}]({url})")
            else:
                st.error("No keywords were generated. Please try again with different text.")
    elif press_button and not input_text:
        st.warning("Please enter some text to generate keywords.")